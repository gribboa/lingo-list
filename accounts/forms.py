from allauth.account.forms import SignupForm
from django import forms
from django.conf import settings
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from .models import User


class LanguagePreferenceForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "ui_language", "preferred_language")
        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-input", "autocomplete": "given-name"},
            ),
            "ui_language": forms.Select(
                attrs={"class": "form-select"},
            ),
            "preferred_language": forms.Select(
                attrs={"class": "form-select"},
            ),
        }
        labels = {
            "username": _("Display name"),
            "ui_language": _("Interface language"),
            "preferred_language": _("Translation language"),
        }
        help_texts = {
            "username": _(
                "This name is shown to collaborators on shared lists."
            ),
            "ui_language": _("The language used for the website interface."),
            "preferred_language": _(
                "Items on shared lists will be translated into this language for you."
            ),
        }


class CustomSignupForm(SignupForm):
    """Extend the allauth signup form with language preference fields."""

    ui_language = forms.ChoiceField(
        choices=settings.LANGUAGES,
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Interface language"),
        help_text=_("The language used for the website interface."),
    )

    preferred_language = forms.ChoiceField(
        choices=settings.LANGUAGES_SUPPORTED_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Translation language"),
        help_text=_(
            "Items on shared lists will be translated into this language for you."
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-fill the language selectors based on the user's browser language
        current_lang = (get_language() or "").split("-")[0]
        if current_lang in settings.LANGUAGES_SUPPORTED:
            self.fields["ui_language"].initial = current_lang
        else:
            self.fields["ui_language"].initial = "en"

        if current_lang in settings.LANGUAGES_SUPPORTED:
            self.fields["preferred_language"].initial = current_lang
        else:
            self.fields["preferred_language"].initial = "en"

    def save(self, request):
        user = super().save(request)
        user.ui_language = self.cleaned_data["ui_language"]
        user.preferred_language = self.cleaned_data["preferred_language"]
        user.save(update_fields=["ui_language", "preferred_language"])
        return user
