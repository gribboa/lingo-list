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
    
    # Prefetch all translations for the target language to avoid N+1 queries
    items = lst.items.select_related("added_by").prefetch_related(
        "translations"
    ).all()
    
    # Build a mapping of item_id -> cached translation for this target language
    translation_map = {}
    for item in items:
        for translation in item.translations.all():
            if translation.target_language == target:
                translation_map[item.id] = translation.translated_text
                break
    
    result = []
    for item in items:
        if item.source_language == target:
            display_text = item.text
            is_translated = False
        else:
            # Check if we have a cached translation
            cached_translation = translation_map.get(item.id)
            if cached_translation:
                display_text = cached_translation
                is_translated = True
            else:
                # Call LibreTranslate for missing translations
                translated = translate_text(item.text, item.source_language, target)
                if translated is None:
                    display_text = item.text
                    is_translated = False
                else:
                    # Store in cache
                    TranslationCache.objects.create(
                        item=item,
                        target_language=target,
                        translated_text=translated,
                    )
                    display_text = translated
                    is_translated = True
        result.append({
            "item": item,
            "display_text": display_text,
            "is_translated": is_translated,
        })
    return result
