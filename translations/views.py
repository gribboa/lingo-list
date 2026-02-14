from django.shortcuts import render

from .models import LanguagePair


def language_pairs(request):
    """Display available LibreTranslate language pairs with source-language filtering."""
    source_filter = request.GET.get("source", "")

    pairs = LanguagePair.objects.filter(enabled=True)
    if source_filter:
        pairs = pairs.filter(source_code=source_filter)

    # Distinct source languages for the filter dropdown (enabled only)
    source_languages = (
        LanguagePair.objects.filter(enabled=True)
        .values_list("source_code", "source_name")
        .distinct()
        .order_by("source_name")
    )

    return render(
        request,
        "translations/language_pairs.html",
        {
            "pairs": pairs,
            "source_languages": source_languages,
            "selected_source": source_filter,
        },
    )
