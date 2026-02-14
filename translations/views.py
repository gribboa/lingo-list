from django.shortcuts import render

from .models import LanguagePair


def language_pairs(request):
    """Display available LibreTranslate language pairs with source-language filtering."""
    source_filter = request.GET.get("source", "")
    enabled_filter = request.GET.get("enabled", "")

    pairs = LanguagePair.objects.all()
    if source_filter:
        pairs = pairs.filter(source_code=source_filter)
    if enabled_filter == "1":
        pairs = pairs.filter(enabled=True)
    elif enabled_filter == "0":
        pairs = pairs.filter(enabled=False)

    # Distinct source languages for the filter dropdown
    source_languages = (
        LanguagePair.objects.values_list("source_code", "source_name")
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
            "selected_enabled": enabled_filter,
        },
    )
