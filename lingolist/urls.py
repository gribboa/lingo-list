from django.contrib import admin
from django.urls import include, path

from .views import healthz, landing_page, privacy_notice_page

urlpatterns = [
    path("", landing_page, name="landing"),
    path("healthz/", healthz, name="healthz"),
    path("privacy/", privacy_notice_page, name="privacy_notice"),
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("allauth.urls")),
    path("lists/", include("lists.urls")),
    path("translations/", include("translations.urls")),
]
