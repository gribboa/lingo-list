from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .forms import LanguagePreferenceForm


@login_required
def profile(request):
    if request.method == "POST":
        form = LanguagePreferenceForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
    else:
        form = LanguagePreferenceForm(instance=request.user)
    return render(request, "accounts/profile.html", {"form": form})
