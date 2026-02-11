Features
- Real-time collaboration - Add WebSocket support (Django Channels) so collaborators see updates instantly without refreshing
- List categories/tags - Allow users to organize lists into categories
- Item reordering - Drag-and-drop to reorder list items
- Due dates/reminders - Useful for shopping or task lists
- Import/export - CSV or JSON export for list backup

User Experience
- Dark mode - Add a theme toggle in the profile settings
- Keyboard shortcuts - Quick add items, navigate lists
- Mobile PWA - Add a manifest.json for installable mobile experience
- Offline support - Service worker to cache lists for offline viewing
- Search - Search across all your lists and items

Performance & Reliability
- Batch translations - Queue multiple items for translation instead of one-by-one
- Translation fallback - Add a backup translation service if LibreTranslate is down
- Pagination - For lists with many items
- ~~Database indexes - Add indexes on frequently queried fields~~ ✓
- ~~N+1 query in get_items_for_user - Batch prefetch translation cache~~ ✓
- ~~N+1 query in item_reorder - Use bulk update instead of separate UPDATEs~~ ✓
- ~~lst.items.count in templates - Annotate queryset with item_count~~ ✓
- https://uptimekuma.org/

Security & Production Readiness
- Rate limiting - Prevent abuse of translation API
- Email verification required - Change from "optional" to "mandatory"
- HTTPS enforcement - Add SECURE_SSL_REDIRECT for production
- Audit logging - Track who changed what and when

Testing & Quality
- Unit tests - Add pytest tests for models, views, translation service
- E2E tests - Playwright tests for critical user flows
- CI/CD pipeline - GitHub Actions for automated testing and deployment