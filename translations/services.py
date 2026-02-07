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
        target_language=target_language,
        translated_text=translated,
    )
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
