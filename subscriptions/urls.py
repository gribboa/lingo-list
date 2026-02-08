"""URLs for subscriptions app."""
from django.urls import path

from . import views

app_name = "subscriptions"

urlpatterns = [
    path("pricing/", views.pricing, name="pricing"),
    path("manage/", views.subscription_manage, name="manage"),
    path(
        "checkout/create/", views.create_checkout_session, name="create_checkout_session"
    ),
    path("success/", views.subscription_success, name="subscription_success"),
    path("portal/create/", views.create_portal_session, name="create_portal_session"),
    path("webhook/", views.stripe_webhook, name="stripe_webhook"),
]
