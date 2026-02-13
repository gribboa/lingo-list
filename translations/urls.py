from django.urls import path

from . import views

app_name = "translations"

urlpatterns = [
    path("languages/", views.language_pairs, name="language_pairs"),
]
