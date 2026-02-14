from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom user with language preferences."""

    preferred_language = models.CharField(
        max_length=10,
        default="en",
        help_text=_(
            "Items on shared lists will be translated into this language for you."
        ),
    )

    ui_language = models.CharField(
        max_length=10,
        choices=settings.LANGUAGES,
        default="en",
        help_text=_("The language used for the website interface."),
    )

    def __str__(self):
        return self.email or self.username
