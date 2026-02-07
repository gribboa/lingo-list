from allauth.account.forms import SignupForm
from django import forms
from django.conf import settings

from .models import User


class LanguagePreferenceForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("preferred_language",)
        widgets = {
            "preferred_language": forms.Select(
                attrs={"class": "form-select"},
            ),
        }


class CustomSignupForm(SignupForm):
    """Extend the allauth signup form with a preferred language field."""

    preferred_language = forms.ChoiceField(
        choices=[(code, name) for code, name in settings.LANGUAGES_SUPPORTED.items()],
        initial="en",
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Preferred language",
    )

    def save(self, request):
        user = super().save(request)
        user.preferred_language = self.cleaned_data["preferred_language"]
        user.save(update_fields=["preferred_language"])
        return user
