from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom user with language preferences."""

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    email = models.EmailField(_("email address"), unique=True)

    username = models.CharField(
        _("username"),
        max_length=150,
        blank=True,
        default="",
        validators=[UnicodeUsernameValidator()],
        help_text=_(
            "Display name shown to collaborators on shared lists."
        ),
    )

    preferred_language = models.CharField(
        max_length=10,
        choices=settings.LANGUAGES_SUPPORTED_CHOICES,
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
