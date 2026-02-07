import secrets
import string

from django.conf import settings
from django.db import models


def generate_share_token():
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(24))


class List(models.Model):
    """A collaborative list owned by a user."""

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_lists",
    )
    share_token = models.CharField(
        max_length=24,
        unique=True,
        default=generate_share_token,
        editable=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title

    def get_share_url(self):
        return f"/lists/join/{self.share_token}/"

    def is_member(self, user):
        if self.owner == user:
            return True
        return self.collaborators.filter(user=user).exists()


class Collaborator(models.Model):
    """A user who has been invited to collaborate on a list."""

    list = models.ForeignKey(
        List,
        on_delete=models.CASCADE,
        related_name="collaborators",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="collaborations",
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("list", "user")

    def __str__(self):
        return f"{self.user} on {self.list}"


class ListItem(models.Model):
    """A single item on a list, stored in the language it was entered in."""

    list = models.ForeignKey(
        List,
        on_delete=models.CASCADE,
        related_name="items",
    )
    text = models.CharField(max_length=500)
    source_language = models.CharField(
        max_length=10,
        choices=[(code, name) for code, name in settings.LANGUAGES_SUPPORTED.items()],
    )
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="list_items",
    )
    is_checked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.text


class TranslationCache(models.Model):
    """Caches translations of list items to avoid repeated API calls."""

    item = models.ForeignKey(
        ListItem,
        on_delete=models.CASCADE,
        related_name="translations",
    )
    target_language = models.CharField(max_length=10)
    translated_text = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("item", "target_language")

    def __str__(self):
        return f"{self.item.text} -> {self.translated_text} ({self.target_language})"
