from allauth.account.forms import SignupForm
from django import forms
from django.conf import settings
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from translations.models import get_enabled_language_choices

from .models import User


class LanguagePreferenceForm(forms.ModelForm):
    ui_language = forms.ChoiceField(
        choices=[("en", "English")],
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Interface language"),
        help_text=_("The language used for the website interface."),
    )

    preferred_language = forms.ChoiceField(
        choices=[("en", "English")],
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Translation language"),
        help_text=_(
            "Items on shared lists will be translated into this language for you."
        ),
    )

    class Meta:
        model = User
        fields = ("username", "ui_language", "preferred_language")
        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-input", "autocomplete": "given-name"},
            ),
        }
        labels = {
            "username": _("Username"),
        }
        help_texts = {
            "username": _(
                "Tip: use your first name so collaborators can recognize you."
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["ui_language"].choices = settings.LANGUAGES
        self.fields["preferred_language"].choices = get_enabled_language_choices()


class CustomSignupForm(SignupForm):
    """Extend the allauth signup form with language preference fields."""

    ui_language = forms.ChoiceField(
        choices=[("en", "English")],
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Interface language"),
        help_text=_("The language used for the website interface."),
    )

    preferred_language = forms.ChoiceField(
        choices=[("en", "English")],
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Translation language"),
        help_text=_(
            "Items on shared lists will be translated into this language for you."
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["ui_language"].choices = settings.LANGUAGES
        self.fields["preferred_language"].choices = get_enabled_language_choices()

        # Pre-fill the language selectors based on the user's browser language
        current_lang = (get_language() or "").split("-")[0]
        ui_codes = {code for code, _ in settings.LANGUAGES}
        enabled_codes = {code for code, _ in self.fields["preferred_language"].choices}
        self.fields["ui_language"].initial = current_lang if current_lang in ui_codes else "en"
        self.fields["preferred_language"].initial = current_lang if current_lang in enabled_codes else "en"

    def save(self, request):
        user = super().save(request)
        user.ui_language = self.cleaned_data["ui_language"]
        user.preferred_language = self.cleaned_data["preferred_language"]
        user.save(update_fields=["ui_language", "preferred_language"])
        return user
