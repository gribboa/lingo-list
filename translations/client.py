"""Client for the LibreTranslate API."""

import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def translate_text(text: str, source: str, target: str) -> str | None:
    """Translate *text* from *source* language to *target* language.

    Returns the translated string, or ``None`` if the request fails.
    """
    if source == target:
        return text

    url = f"{settings.LIBRETRANSLATE_URL}/translate"
    payload = {
        "q": text,
        "source": source,
        "target": target,
        "format": "text",
    }

    logger.info("Translation request: %r (%s -> %s)", text, source, target)

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        translated = data.get("translatedText")
        logger.info("Translation response: %r -> %r", text, translated)
        return translated
    except requests.RequestException:
        logger.exception(
            "LibreTranslate request failed for %r (%s->%s)", text, source, target
        )
        return None
