from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import translation
from django.utils.translation import gettext as _

from .forms import LanguagePreferenceForm


@login_required
def profile(request):
    if request.method == "POST":
        form = LanguagePreferenceForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            # Activate the new UI language immediately
            translation.activate(user.ui_language)
            messages.success(request, _("Your profile has been saved."))
            response = redirect("accounts:profile")
            response.set_cookie(
                settings.LANGUAGE_COOKIE_NAME,
                user.ui_language,
                max_age=settings.LANGUAGE_COOKIE_AGE,
                path=settings.LANGUAGE_COOKIE_PATH,
                domain=settings.LANGUAGE_COOKIE_DOMAIN,
                secure=settings.LANGUAGE_COOKIE_SECURE,
                httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
                samesite=settings.LANGUAGE_COOKIE_SAMESITE,
            )
            return response
        messages.error(request, _("Please correct the errors below."))
    else:
        form = LanguagePreferenceForm(instance=request.user)
    return render(request, "accounts/profile.html", {"form": form})
