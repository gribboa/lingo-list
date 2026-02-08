from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom user with language preferences."""

    preferred_language = models.CharField(
        max_length=10,
        choices=[(code, name) for code, name in settings.LANGUAGES_SUPPORTED.items()],
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

    # Subscription fields
    is_premium = models.BooleanField(
        default=False,
        help_text=_("Whether the user has an active premium subscription."),
    )
    stripe_customer_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Stripe customer ID for this user."),
    )
    stripe_subscription_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Stripe subscription ID for the active subscription."),
    )
    subscription_status = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text=_("Current subscription status (active, canceled, past_due, etc.)."),
    )
    subscription_end_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_("When the current subscription period ends."),
    )

    def __str__(self):
        return self.email or self.username

    def has_active_subscription(self):
        """Check if user has an active premium subscription."""
        if not self.is_premium:
            return False
        if self.subscription_status not in ("active", "trialing"):
            return False
        if self.subscription_end_date and self.subscription_end_date < timezone.now():
            return False
        return True
