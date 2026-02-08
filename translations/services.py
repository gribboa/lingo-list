"""High-level translation helpers that use the cache."""

from lists.models import ListItem, TranslationCache

from .client import translate_text
from .redis_cache import get_cached_translation, set_cached_translation


def get_translated_text(item: ListItem, target_language: str) -> str:
    """Return the item text translated into *target_language*.

    Uses a three-tier caching strategy:
    1. Check Redis hot cache
    2. Check database (TranslationCache) and populate Redis if found
    3. Call LibreTranslate API and populate both caches
    
    Falls back to the original text if translation fails.
    """
    if item.source_language == target_language:
        return item.text

    # 1. Check Redis hot cache first
    cached_text = get_cached_translation(item.id, target_language)
    if cached_text:
        return cached_text

    # 2. Check database cache
    cached = TranslationCache.objects.filter(
        item=item,
        target_language=target_language,
    ).first()
    if cached:
        # Found in DB, add to Redis for faster access next time
        set_cached_translation(item.id, target_language, cached.translated_text)
        return cached.translated_text

    # 3. Call LibreTranslate API
    translated = translate_text(item.text, item.source_language, target_language)
    if translated is None:
        return item.text

    # Store in both caches (database for persistence, Redis for speed)
    TranslationCache.objects.create(
        item=item,
        target_language=target_language,
        translated_text=translated,
    )
    set_cached_translation(item.id, target_language, translated)
    return translated


def get_items_for_user(lst, user) -> list[dict]:
    """Return list items annotated with translated text for *user*.

    Each dict contains: item, display_text, is_translated.
    """
    target = user.preferred_language
    result = []
    for item in lst.items.select_related("added_by").all():
        if item.source_language == target:
            display_text = item.text
            is_translated = False
        else:
            display_text = get_translated_text(item, target)
            is_translated = display_text != item.text
        result.append({
            "item": item,
            "display_text": display_text,
            "is_translated": is_translated,
        })
    return result
