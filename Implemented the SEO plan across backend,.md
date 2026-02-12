Implemented the SEO plan across backend, routing, templates, content pages, and assets.

**What I changed**
- Added SEO config + sitemap support in Django:
  - `lingolist/settings.py:18`
  - `lingolist/settings.py:92`
  - `lingolist/settings.py:106`
  - `lingolist/settings.py:134`
- Added SEO context processor:
  - `lingolist/context_processors.py:4`
- Added optional canonical-host redirect middleware:
  - `lingolist/middleware.py:5`
- Added sitemap definitions:
  - `lingolist/sitemaps.py:5`
  - `lingolist/sitemaps.py:36`
- Added SEO endpoints/routes + use-case routes:
  - `lingolist/urls.py:18`
  - `lingolist/urls.py:19`
  - `lingolist/urls.py:23`
  - `lingolist/urls.py:28`
  - `lingolist/urls.py:33`
- Added `robots.txt` view and use-case page views:
  - `lingolist/views.py:16`

**Metadata system + page directives**
- Refactored base metadata system (robots/canonical/OG/Twitter/JSON-LD block support) and removed duplicate Swetrix include:
  - `templates/base.html:10`
  - `templates/base.html:11`
  - `templates/base.html:43`
  - `templates/base.html:46`
- Landing SEO metadata + Organization/WebSite JSON-LD + internal links to use-case pages:
  - `templates/landing.html:6`
  - `templates/landing.html:13`
  - `templates/landing.html:102`
- Privacy page canonical/meta:
  - `templates/privacy_notice.html:5`
- Auth pages set to indexable + canonical:
  - `templates/account/login.html:6`
  - `templates/account/signup.html:6`
  - `templates/account/password_reset.html:6`
- Private/error pages set to `noindex,nofollow`:
  - `templates/lists/index.html:5`
  - `templates/lists/detail.html:5`
  - `templates/lists/create.html:5`
  - `templates/lists/archived.html:5`
  - `templates/accounts/profile.html:5`
  - `templates/403.html:5`
  - `templates/404.html:5`
  - `templates/500.html:5`

**Use-case content cluster**
- Added 3 public SEO pages with canonical + FAQ JSON-LD:
  - `templates/use_cases/multilingual_shopping_lists.html:5`
  - `templates/use_cases/travel_planning_shared_lists.html:5`
  - `templates/use_cases/roommate_household_task_lists.html:5`

**Social preview asset**
- Added default OG image:
  - `static/og/lingolist-default.png`

**Env/docs**
- Added new SEO env vars:
  - `.env.example:5`
- Documented SEO/indexing behavior and canonical settings:
  - `README.md:229`
  - `README.md:237`

**Validation**
- `python -m compileall lingolist` passed.
- `python manage.py check` could not run in this environment because Django is not installed locally.

**Still required in Coolify (manual)**
1. Configure proxy redirects: `http://* -> https://lingolist.io` and `https://www.lingolist.io/* -> https://lingolist.io/*`.
2. Set env vars (`SITE_URL`, `SEO_CANONICAL_HOST`, optional `DJANGO_ENFORCE_CANONICAL_HOST`).
3. After deploy, verify `https://lingolist.io/robots.txt` and `https://lingolist.io/sitemap.xml`.