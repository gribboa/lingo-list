# LingoList — Improvement Ideas

## UX / User Interface

- **Redirect authenticated users from landing page** — `landing_page` view has a commented-out redirect for authenticated users. Visiting `/` while logged in still shows the marketing page, which is a dead end requiring manual nav to "My Lists".
- **Copy-link feedback** — The "Copy" button for the share URL uses `navigator.clipboard.writeText()` but gives no visual confirmation (e.g. "Copied!" tooltip or button text change) that the copy succeeded.
- **Delete confirmation UX** — List deletion uses a `confirm()` JS dialog, which is jarring. A styled in-page confirmation modal (consistent with the rename modal) would be more polished.
- **Item add input auto-focus** — After adding an item via HTMX, the text input is cleared (`this.reset()`) but focus is not returned to it, requiring the user to click back into the field.
- **Empty list detail description** — When a list has no description, the space feels abrupt. A subtle placeholder or "Add a description" link (for owners) would improve discoverability.
- **Keyboard shortcuts** — No keyboard shortcuts exist. `Enter` to add item works (form submit), but there's no shortcut for common actions like toggling items, navigating between lists, or creating a new list.
- **Toast/notification system** — Django messages appear only on full page loads. HTMX partial responses (item add, toggle, delete) don't display messages, so errors during these operations are silently swallowed.
- **Undo support for destructive actions** — Deleting an item or removing a collaborator is immediate and irreversible. A brief "Undo" toast would prevent accidental data loss.
- **List card item preview** — The list index shows item count but not a preview of the actual items. Showing the first 2-3 item names on the card would help users identify lists faster.
- **Collaborator can leave a list** — There's no way for a collaborator to voluntarily leave a shared list; only the owner can remove them. A "Leave list" action would be useful.
- **Sortable drag handle on mobile** — The `⋮⋮` text drag handle is small and hard to grab on touch devices. A larger touch target or a dedicated grip icon would improve mobile reordering.
- **Checked items visual separation** — Checked items are moved to the end by sort order, but there's no visual divider or grouping between unchecked and checked items. A "Completed" separator would clarify the list state.
- **Accessible color contrast for messages** — The dark-mode versions of success/error/info/warning messages don't have explicit dark overrides (only `archived-banner` does). Light-on-light or dark-on-dark readability issues may occur.
- **Loading states for HTMX actions** — The HTMX indicator (`...`) is minimal. A spinner or subtle skeleton animation on the item list during add/toggle/delete would provide clearer feedback.

## Functionality

- **Real-time collaboration via WebSockets** — Currently, collaborators must refresh to see each other's changes. Django Channels with WebSocket push would make the app feel truly real-time.
- **Offline PWA support (service worker)** — The manifest.json is present but there's no service worker. Lists can't be viewed or edited offline. A service worker that caches list data and syncs on reconnect would significantly improve mobile UX.
- **Search across lists and items** — No search functionality exists. Users with many lists have no way to find a specific item without scrolling through each list.
- **Item editing** — Once an item is added, its text cannot be changed — only deleted and re-added. Inline editing (click-to-edit or an edit button) is a common expectation.
- **List description editing** — Descriptions can be set at creation but cannot be edited afterward. The rename modal only covers the title.
- **Bulk item actions** — No way to check/uncheck all items, delete all checked items, or move checked items to another list. These are common list management patterns.
- **Due dates and reminders** — Useful for task-oriented lists. Optional per-item date field with sorting by due date.
- **List categories/tags** — No organizational structure beyond pinning. Tags or folders would help users with many lists.
- **Import/export** — No way to export a list to CSV/JSON/plain text or import items from another source.
- **Item notes/details** — Items are limited to a single text field. An optional expandable notes area per item would support use cases like recipes, links, or quantities.
- **Translation language override per item** — `source_language` is auto-set to the adding user's `preferred_language`. If a user types an item in a different language, the translation will be based on the wrong source language.
- **TranslationCache invalidation** — If an item's text could be edited (see above), cached translations would become stale. There is no cache invalidation mechanism. Even without editing, the cache has no TTL — translations are stored forever.
- **Collaborator roles/permissions** — All collaborators have identical permissions (add, check, delete any item). Role-based access (e.g. view-only, can-add, full-edit) would be useful for larger groups.
- **Regenerate share token** — There's no way to rotate the share link if it's been shared too widely. A "regenerate link" button would improve security.
- **Account deletion** — No account deletion flow exists. Users cannot delete their own account or data, which may also be a GDPR concern.

## Performance & Scalability

- ~~**N+1 query in `get_items_for_user`** — The function iterates over items and performs a separate `TranslationCache.objects.filter()` query for each item that needs translation. This should be batch-prefetched or done with a single query/annotation.~~
- ~~**N+1 query in `item_reorder`** — The reorder view does a separate `UPDATE` for each item ID. A bulk update or `CASE`/`WHEN` SQL expression would reduce database round-trips.~~
- ~~**Missing database indexes** — `ListItem.list` + `ListItem.order` is a common query pattern but has no composite index. `TranslationCache.(item, source_language, target_language)` has a unique constraint (which creates an index), which is good, but `ListItem` ordering queries could benefit from explicit indexing.~~
- **Batch translations** — Each pending item triggers a separate HTMX request to `item_translate`. For a list with many new items from a different language, this creates a burst of sequential HTTP requests. A batch translation endpoint would reduce overhead.
- **Pagination** — Lists with hundreds of items load all items at once. Paginated or infinite-scroll loading would improve performance for large lists.
- **CDN scripts lack Subresource Integrity (SRI)** — HTMX and Sortable.js are loaded from CDN without `integrity` hashes, allowing tampered scripts if the CDN is compromised.
- **Translation timeout** — The LibreTranslate client has a 10-second timeout. If LibreTranslate is slow, each `item_translate` HTMX call will block for up to 10 seconds with no client-side timeout or abort mechanism.
- ~~**`lst.items.count` in template** — The list index template calls `lst.items.count` for every list card, which is a query per list. This should be annotated in the queryset (`annotate(item_count=Count('items'))`)~~.
- **Translation fallback** — If LibreTranslate is down, translations silently fail and fall back to the original text. A secondary translation service or user notification would improve reliability.

## Security & Production Hardness

- **Rate limiting** — No rate limiting on any endpoint. The translation API, login, signup, and item-add endpoints are all vulnerable to abuse. `django-ratelimit` or middleware-level limiting would help.
- **Email verification is optional** — `ACCOUNT_EMAIL_VERIFICATION = "optional"` means users can sign up with unverified emails. Setting this to `"mandatory"` would prevent fake accounts and improve trust.
- **HTTPS enforcement** — No `SECURE_SSL_REDIRECT` setting for production. The `SECURE_PROXY_SSL_HEADER` is set but doesn't enforce HTTPS.
- **Session/cookie security** — `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, and `SESSION_COOKIE_HTTPONLY` are not explicitly set. They should be `True` in production.
- **Content Security Policy (CSP)** — No CSP header is set. The app loads scripts from `unpkg.com`, `cdn.jsdelivr.net`, and `swetrix.org`, which should be explicitly allowed via CSP while blocking everything else.
- **Duplicate analytics script** — `base.html` includes `<script src="https://swetrix.org/swetrix.js" defer></script>` twice (lines 29-30), loading the analytics script two times.
- **Share token brute-force** — The 24-character alphanumeric share token provides ~143 bits of entropy, which is sufficient, but there's no rate-limiting or brute-force protection on the `list_join` endpoint.
- **`list_delete` has no server-side confirmation** — The only protection against accidental deletion is a JS `confirm()` dialog. If JS is disabled or the request is crafted directly, the list is deleted immediately.
- **Admin panel exposure** — The `/admin/` URL is the Django default and easily discoverable. Consider renaming the admin path or restricting access by IP.
- **ALLOWED_HOSTS includes `.sslip.io`** — This wildcard allows any subdomain of `sslip.io`, which is a public DNS service. This should be removed in production.
- **JSON body parsing in `item_reorder`** — The view parses `request.body` as JSON and validates that `item_ids` exists, but doesn't validate that the IDs are integers or that they all belong to the list. Invalid IDs are silently ignored.
- **Audit logging** — No record of who changed what and when. An audit trail (django-auditlog or similar) would help with debugging and accountability.

## Testing & Quality

- **No automated tests** — The project has zero tests. Unit tests for models, views, translation service, and forms are the highest priority improvement.
- **No CI/CD pipeline** — No GitHub Actions, no linting, no pre-commit hooks. A basic pipeline with `ruff` for linting, `pytest` for tests, and Docker build verification would catch regressions.
- **No type checking** — No `mypy` or `pyright` configuration. Type annotations exist in the translation service but aren't enforced.
- **No factory/fixture setup** — No test data factories (e.g. `factory_boy`) or fixtures for development seeding.
- **No E2E tests** — Playwright tests for critical user flows (signup, create list, add items, share, collaborate) would catch integration regressions.

## Code Quality & Architecture

- **`get_share_url()` returns a hardcoded path** — `List.get_share_url()` returns `f"/lists/join/{self.share_token}/"` instead of using Django's `reverse()`. This will break if the URL pattern changes.
- **View access control is inconsistent** — Some views use `get_object_or_404(List, pk=pk, owner=request.user)` to restrict to owners, while others do a separate `lst.is_member(request.user)` check. A mixin or decorator would standardize this.
- **`list_index` queryset performs two separate filters then unions** — `(owned | collaborated).distinct()` works but is less efficient than a single `Q` filter: `List.objects.filter(Q(owner=user) | Q(collaborators__user=user))`.
- **`lst.save()` in `item_add` to bump `updated_at`** — This saves the entire List model just to update the `auto_now` timestamp. An explicit `lst.save(update_fields=["updated_at"])` or a signal-based approach would be cleaner, but note `auto_now` fields need careful handling with `update_fields`.
- **Forms use inline error styling** — Error messages use `style="color:var(--color-danger)"` inline in multiple templates instead of a CSS class. A `.form-error` class would be more maintainable.
- **`unique_together` is deprecated** — The `Collaborator` and `TranslationCache` models use `unique_together` in Meta, which Django recommends replacing with `UniqueConstraint` in `Meta.constraints`.

## DevOps & Deployment

- **No `.dockerignore`** — The Docker build copies everything (including `.git`, `db.sqlite3`, `__pycache__`, `.env`) into the image. A `.dockerignore` would reduce image size and prevent leaking secrets.
- **No multi-stage Docker build** — The Dockerfile installs build dependencies in the final image. A multi-stage build would produce a smaller production image.
- **No database migration in Docker** — The Dockerfile runs `collectstatic` but not `migrate`. Migrations must be run manually or via a separate entrypoint script.
- **No health check dependency ordering** — `docker-compose.yml` uses `depends_on` but doesn't use `condition: service_healthy`, so the web container may start before LibreTranslate is ready to accept translation requests.
- **LibreTranslate uses `latest` tag** — The docker-compose uses `libretranslate/libretranslate:latest` which is non-deterministic. Pinning to a specific version would improve reproducibility.
- **Gunicorn worker configuration** — The default gunicorn config uses a single worker. For production, `--workers` should be set based on CPU count (e.g. `2 * CPU + 1`), and `--timeout` should be configured.
- **No backup strategy** — No database backup mechanism is documented or automated. For SQLite, the volume is the only persistence. For PostgreSQL, `pg_dump` scheduling would be prudent.
- **No logging to file/service** — All logging goes to console. In production, structured logging to a file or external service (e.g. Sentry) would aid debugging.
- **No environment-specific settings** — A single `settings.py` handles both development and production via env vars. A split settings pattern or django-environ validation would prevent accidentally running with insecure dev defaults in production.
- **Uptime monitoring** — No uptime monitoring configured. Uptime Kuma (https://uptimekuma.org/) or similar would provide visibility into downtime.

## Internationalization (i18n)

- **Only 2 languages enabled** — The app supports en and ru. The 13 other language definitions are commented out. Enabling more languages (especially common ones like es, fr, de, zh) would dramatically expand the user base.
- **LibreTranslate `LT_LOAD_ONLY=en,ru`** — The Docker config only loads English and Russian models. This must be updated in sync with `LANGUAGE_DEFINITIONS` whenever new languages are added.
- **No locale files for Russian** — The `locale/` directory exists but may not contain compiled `.mo` files for Russian. The UI i18n strings need `django-admin makemessages` and `compilemessages` to be run.
- **PWA manifest is English-only** — `manifest.json` has `"lang": "en"` and English-only name/description. Ideally, the manifest would be served dynamically based on user language, or multiple manifests would be provided.
- **Landing page is not locale-aware for anonymous users** — Anonymous users see the landing page in whatever language their browser negotiates via `LocaleMiddleware`, but there's no language selector available before signup.
