from django.db import models


class LanguagePair(models.Model):
    """A supported translation pair from LibreTranslate."""

    source_code = models.CharField(max_length=10)
    source_name = models.CharField(max_length=100)
    target_code = models.CharField(max_length=10)
    target_name = models.CharField(max_length=100)
    enabled = models.BooleanField(default=False)

    class Meta:
        unique_together = ("source_code", "target_code")
        ordering = ["source_name", "target_name"]

    def __str__(self):
        return f"{self.source_name} ({self.source_code}) -> {self.target_name} ({self.target_code})"


def get_enabled_language_choices():
    """Return a list of (code, name) tuples for all languages in enabled pairs.

    Collects every distinct language that appears as either source or target
    in an enabled ``LanguagePair``.  The result is sorted by name and always
    includes English as a fallback when no pairs are enabled yet.
    """
    enabled_pairs = LanguagePair.objects.filter(enabled=True)

    languages = {}
    for code, name in enabled_pairs.values_list("source_code", "source_name"):
        languages.setdefault(code, name)
    for code, name in enabled_pairs.values_list("target_code", "target_name"):
        languages.setdefault(code, name)

    if not languages:
        languages["en"] = "English"

    return sorted(languages.items(), key=lambda item: item[1])
