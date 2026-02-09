# LingoList

Collaborative multilingual lists. Create shared shopping lists, wish lists, or any kind of list — each collaborator sees items translated into their own language automatically.

## The idea

Couples, families, and flatmates who speak different languages can collaborate on lists without friction. You add items in **your** language; your partner sees them in **theirs**. Translations are handled by a self-hosted [LibreTranslate](https://github.com/LibreTranslate/LibreTranslate) instance — no third-party API keys required.

## Architecture overview

```
┌──────────────┐      HTML + HTMX       ┌────────────────────┐
│   Browser    │ ◄─────────────────────► │  Django (web app)  │
└──────────────┘                         │                    │
                                         │  accounts app      │
                                         │  lists app         │
                                         │  translations app  │
                                         └────────┬───────────┘
                                                  │  HTTP / JSON
                                                  ▼
                                         ┌────────────────────┐
                                         │  LibreTranslate    │
                                         │  (self-hosted)     │
                                         └────────────────────┘
```

### Components

| Component | Role |
|---|---|
| **Django** | Web framework. Serves HTML pages, handles auth (via django-allauth), manages lists/items/collaborators. |
| **HTMX** | Adds interactivity (adding items, toggling checkboxes, removing items) without writing JavaScript or using a SPA framework. |
| **django-allauth** | Handles signup, login, logout, password reset. Configured for email-based auth. Ready for social login providers later. |
| **LibreTranslate** | Open-source machine translation API. Runs as a Docker container alongside the app. |
| **WhiteNoise** | Serves static files efficiently in production without needing nginx for static assets. |
| **SQLite + PostgreSQL** | SQLite is the default for local development. Production uses PostgreSQL via `DATABASE_URL` (for example in Coolify). |

### Django apps

| App | Purpose |
|---|---|
| `accounts` | Custom user model with a `preferred_language` field. Profile page to change language preference. Custom signup form that collects language during registration. |
| `lists` | Core domain: `List`, `ListItem`, `Collaborator`, `TranslationCache` models. Views for creating, viewing, sharing, and managing lists. HTMX endpoints for real-time item operations. |
| `translations` | LibreTranslate API client and caching layer. Translates items on-the-fly and stores results in `TranslationCache` to avoid redundant API calls. |

## Features

- **Email-based authentication** — signup, login, logout, password reset (social logins ready to add)
- **Language selection at signup** — each user picks their preferred language
- **Create and manage lists** — title, description, items with checkbox support
- **Share via link** — each list has a unique invite URL; logged-in users who visit it are added as collaborators
- **Owner controls** — list owners can remove collaborators at any time
- **Automatic translation** — items entered in one language are shown translated for users who speak another
- **Translation caching** — each translation is stored so LibreTranslate is called only once per item/language pair
- **Original text shown** — translated items show the original text alongside, so nothing is hidden
- **HTMX-powered** — add, check, and delete items without full page reloads

## Development setup

### Option A: Docker Compose (recommended)

This starts both the Django dev server and LibreTranslate in containers.

```bash
# Clone the repo
git clone <repo-url> lingo-list
cd lingo-list

# Start services
docker compose up --build

# In another terminal, run migrations and create a superuser
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

The app is at **http://localhost:8000** and LibreTranslate at **http://localhost:5000**.

> **Note:** LibreTranslate downloads language models on first start. This can take a few minutes depending on which languages are loaded.

### Option B: Local Python + external LibreTranslate

```bash
# Clone and enter the repo
git clone <repo-url> lingo-list
cd lingo-list

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and edit environment variables
cp .env.example .env
# Edit .env — set LIBRETRANSLATE_URL to your LibreTranslate instance

# Run migrations
python manage.py migrate

# Create the default Site object for django-allauth
python manage.py shell -c "
from django.contrib.sites.models import Site
Site.objects.update_or_create(id=1, defaults={'domain': 'localhost:8000', 'name': 'LingoList'})
"

# Create a superuser
python manage.py createsuperuser

# Start the dev server
python manage.py runserver
```

For LibreTranslate, either:
- Run it via Docker: `docker run -p 5000:5000 libretranslate/libretranslate`
- Or install it natively: see [LibreTranslate docs](https://github.com/LibreTranslate/LibreTranslate)

## Production setup (Coolify + PostgreSQL)

1. Create a PostgreSQL service in Coolify with persistent storage.
2. In your Django app service, set `DATABASE_URL` to your Postgres connection string:
   - `postgresql://<user>:<password>@<host>:5432/<database>`
3. Set production Django env vars (`DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`).
4. Deploy, then run bootstrap commands in the app container:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py shell -c "
from django.contrib.sites.models import Site
Site.objects.update_or_create(id=1, defaults={'domain': 'your-domain.com', 'name': 'LingoList'})
"
```

## How it works

### User flow

1. **Landing page** — unauthenticated users see the marketing page; authenticated users redirect to their lists
2. **Signup** — user provides email, password, and preferred language
3. **My Lists** — shows all lists the user owns or has been invited to
4. **Create a list** — give it a title and optional description
5. **List detail** — add items (stored in the user's preferred language), check them off, delete them. Items from other users appear translated.
6. **Sharing** — copy the share link; when another logged-in user visits it, they auto-join as a collaborator
7. **Profile** — change your preferred language at any time; translations update on next page load

### Translation flow

```
User adds "Milk" (source_language=en)
  │
  ▼
Collaborator views list (preferred_language=es)
  │
  ├─ Check TranslationCache for (item, "es")
  │   ├─ Cache hit → return cached "Leche"
  │   └─ Cache miss → call LibreTranslate API
  │       ├─ Success → store in cache, return "Leche"
  │       └─ Failure → fall back to original "Milk"
  │
  ▼
Display: "Leche" (translated) with original "Milk" shown
```

## Project structure

```
lingo-list/
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── lingolist/              # Django project config
│   ├── settings.py
│   ├── urls.py
│   ├── views.py            # Landing page view
│   └── wsgi.py
├── accounts/               # User model & auth customization
│   ├── models.py           # Custom User with preferred_language
│   ├── forms.py            # Signup form, language preference form
│   ├── views.py            # Profile view
│   ├── adapters.py         # allauth adapter for custom signup
│   ├── admin.py
│   └── urls.py
├── lists/                  # Core list functionality
│   ├── models.py           # List, ListItem, Collaborator, TranslationCache
│   ├── forms.py            # List and item forms
│   ├── views.py            # All list/item/collaborator views
│   ├── admin.py
│   └── urls.py
├── translations/           # LibreTranslate integration
│   ├── client.py           # Low-level API client
│   └── services.py         # High-level helpers with caching
├── templates/
│   ├── base.html           # Shared layout with nav/footer
│   ├── landing.html        # Marketing landing page
│   ├── account/            # Allauth template overrides
│   │   ├── login.html
│   │   ├── signup.html
│   │   ├── logout.html
│   │   └── password_reset.html
│   ├── accounts/
│   │   └── profile.html
│   ├── lists/
│   │   ├── index.html      # My Lists page
│   │   ├── create.html     # New list form
│   │   └── detail.html     # List detail with items
│   └── partials/           # HTMX partial templates
│       ├── item_list.html
│       └── collaborator_list.html
└── static/
    └── css/
        └── style.css
```

## Configuration

Key settings in `.env` (or environment variables):

| Variable | Default | Description |
|---|---|---|
| `DJANGO_SECRET_KEY` | insecure dev key | Set a real secret in production |
| `DJANGO_DEBUG` | `True` | Set to `False` in production |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated hostnames |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `http://localhost,http://127.0.0.1` | Comma-separated origins (scheme + host) used for CSRF origin checks |
| `SQLITE_PATH` | `db.sqlite3` | Local SQLite file path used when `DATABASE_URL` is not set. |
| `DATABASE_URL` | empty | Production database URL (PostgreSQL in Coolify). If unset, app falls back to SQLite. |
| `LIBRETRANSLATE_URL` | `http://localhost:5000` | URL of your LibreTranslate instance |

## Supported languages

The app ships with 16 languages enabled (matching common LibreTranslate language packs). Edit `LANGUAGES_SUPPORTED` in `lingolist/settings.py` and the `LT_LOAD_ONLY` env var in `docker-compose.yml` to add or remove languages.

## Future plans

- Social logins (Google, GitHub) via allauth social providers
- Paid tier with premium features
- WebSocket support for real-time multi-user updates
- List categories and templates
- Mobile-optimized PWA
- PostgreSQL for production deployments

## License

This project is not yet licensed. All rights reserved.
