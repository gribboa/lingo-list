from allauth.account.adapter import DefaultAccountAdapter


class AccountAdapter(DefaultAccountAdapter):
    """Save the preferred_language field from the signup form."""

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        user.preferred_language = form.cleaned_data.get("preferred_language", "en")
        if commit:
            user.save()
        return user
