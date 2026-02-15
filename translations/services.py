"""High-level translation helpers that use the cache."""

from lists.models import ListItem, TranslationCache

from .client import translate_text


def get_translated_text(item: ListItem, target_language: str) -> str:
    """Return the item text translated into *target_language*.

    Uses the TranslationCache to avoid repeated LibreTranslate calls.
    Falls back to the original text if translation fails.
    """
    if item.source_language == target_language:
        return item.text

    # Check cache first
    cached = TranslationCache.objects.filter(
        item=item,
        source_language=item.source_language,
        target_language=target_language,
    ).first()
    if cached:
        return cached.translated_text

    # Call LibreTranslate
    translated = translate_text(item.text, item.source_language, target_language)
    if translated is None:
        return item.text

    # Store in cache
    TranslationCache.objects.create(
        item=item,
        source_language=item.source_language,
        target_language=target_language,
        translated_text=translated,
    )
    return translated


def get_items_for_user(lst, user) -> list[dict]:
    """Return list items annotated with translated text for *user*.

    Non-blocking: uses cached translations where available. Items that
    need translation but have no cache entry are marked as pending so
    the page can load immediately and fetch translations asynchronously.

    Each dict contains: item, display_text, is_translated, translation_pending.
    """
    target = user.preferred_language
    
    # Prefetch translations to avoid N+1 queries
    items = lst.items.select_related("added_by").prefetch_related("translations").all()
    
    # Build a cache lookup dictionary for efficient access
    translation_cache = {}
    for item in items:
        for translation in item.translations.all():
            key = (item.id, translation.source_language, translation.target_language)
            translation_cache[key] = translation
    
    result = []
    for item in items:
        if item.source_language == target:
            result.append({
                "item": item,
                "display_text": item.text,
                "is_translated": False,
                "translation_pending": False,
            })
        else:
            cache_key = (item.id, item.source_language, target)
            cached = translation_cache.get(cache_key)
            if cached:
                result.append({
                    "item": item,
                    "display_text": cached.translated_text,
                    "is_translated": cached.translated_text != item.text,
                    "translation_pending": False,
                })
            else:
                result.append({
                    "item": item,
                    "display_text": item.text,
                    "is_translated": False,
                    "translation_pending": True,
                })
    return result
