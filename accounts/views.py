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
            form.save()
            # Activate the new UI language immediately
            translation.activate(request.user.ui_language)
            messages.success(request, _("Your preferences have been saved."))
            return redirect("accounts:profile")
    else:
        form = LanguagePreferenceForm(instance=request.user)
    return render(request, "accounts/profile.html", {"form": form})
