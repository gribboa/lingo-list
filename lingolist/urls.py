from django.contrib import admin
from django.urls import include, path

from .views import landing_page

urlpatterns = [
    path("", landing_page, name="landing"),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("allauth.urls")),
    path("lists/", include("lists.urls")),
    path("subscriptions/", include("subscriptions.urls")),
]
