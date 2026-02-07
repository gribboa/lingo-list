from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user with a preferred language for translations."""

    preferred_language = models.CharField(
        max_length=10,
        choices=[(code, name) for code, name in settings.LANGUAGES_SUPPORTED.items()],
        default="en",
        help_text="Items on shared lists will be translated into this language for you.",
    )

    def __str__(self):
        return self.email or self.username
