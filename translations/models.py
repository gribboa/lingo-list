from django.db import models


class LanguagePair(models.Model):
    """A supported translation pair from LibreTranslate."""

    source_code = models.CharField(max_length=10)
    source_name = models.CharField(max_length=100)
    target_code = models.CharField(max_length=10)
    target_name = models.CharField(max_length=100)

    class Meta:
        unique_together = ("source_code", "target_code")
        ordering = ["source_name", "target_name"]

    def __str__(self):
        return f"{self.source_name} ({self.source_code}) -> {self.target_name} ({self.target_code})"
