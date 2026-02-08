"""Views for subscription management."""
import json
import logging

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .limits import get_list_limit_status

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def pricing(request):
    """Display pricing page with monthly and annual options."""
    return render(
        request,
        "subscriptions/pricing.html",
        {
            "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
            "monthly_price": "4.99",
            "annual_price": "49.00",
            "stripe_price_id_monthly": settings.STRIPE_PRICE_ID_MONTHLY,
            "stripe_price_id_annual": settings.STRIPE_PRICE_ID_ANNUAL,
        },
    )


@login_required
def subscription_manage(request):
    """Subscription management page."""
    list_status = get_list_limit_status(request.user)

    return render(
        request,
        "subscriptions/manage.html",
        {
            "user": request.user,
            "list_status": list_status,
            "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
        },
    )


@login_required
@require_POST
def create_checkout_session(request):
    """Create a Stripe Checkout session for subscription."""
    try:
        price_id = request.POST.get("price_id")
        allowed_price_ids = {
            settings.STRIPE_PRICE_ID_MONTHLY,
            settings.STRIPE_PRICE_ID_ANNUAL,
        }
        if not price_id or price_id not in allowed_price_ids:
            messages.error(request, "Invalid pricing option selected.")
            return redirect("subscriptions:pricing")

        # Create or retrieve Stripe customer
        if request.user.stripe_customer_id:
            customer_id = request.user.stripe_customer_id
        else:
            customer = stripe.Customer.create(
                email=request.user.email,
                metadata={
                    "user_id": request.user.id,
                },
            )
            request.user.stripe_customer_id = customer.id
            request.user.save(update_fields=["stripe_customer_id"])
            customer_id = customer.id

        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=request.build_absolute_uri(
                reverse("subscriptions:subscription_success")
            )
            + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri(reverse("subscriptions:pricing")),
            metadata={
                "user_id": request.user.id,
            },
        )

        return redirect(checkout_session.url, code=303)

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating checkout session: {str(e)}")
        messages.error(
            request, "An error occurred while processing your request. Please try again."
        )
        return redirect("subscriptions:pricing")


@login_required
def subscription_success(request):
    """Handle successful subscription."""
    messages.success(
        request,
        "Your premium subscription is now active! Enjoy unlimited lists, items, and collaborators.",
    )
    return redirect("lists:list_index")


@login_required
@require_POST
def create_portal_session(request):
    """Create a Stripe Customer Portal session for managing subscription."""
    try:
        if not request.user.stripe_customer_id:
            messages.error(request, "No subscription found.")
            return redirect("subscriptions:manage")

        portal_session = stripe.billing_portal.Session.create(
            customer=request.user.stripe_customer_id,
            return_url=request.build_absolute_uri(reverse("subscriptions:manage")),
        )

        return redirect(portal_session.url, code=303)

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating portal session: {str(e)}")
        messages.error(
            request, "An error occurred while processing your request. Please try again."
        )
        return redirect("subscriptions:manage")


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhook events."""
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        logger.error("Invalid webhook payload")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid webhook signature")
        return HttpResponse(status=400)

    # Handle the event
    if event["type"] == "checkout.session.completed":
        handle_checkout_session_completed(event["data"]["object"])
    elif event["type"] == "customer.subscription.updated":
        handle_subscription_updated(event["data"]["object"])
    elif event["type"] == "customer.subscription.deleted":
        handle_subscription_deleted(event["data"]["object"])
    elif event["type"] == "invoice.payment_failed":
        handle_payment_failed(event["data"]["object"])

    return HttpResponse(status=200)


def handle_checkout_session_completed(session):
    """Handle completed checkout session."""
    try:
        from accounts.models import User

        user_id = session.get("metadata", {}).get("user_id")
        if not user_id:
            logger.error("No user_id in checkout session metadata")
            return

        user = User.objects.get(id=user_id)

        # Retrieve the subscription
        subscription_id = session.get("subscription")
        if subscription_id:
            subscription = stripe.Subscription.retrieve(subscription_id)

            user.is_premium = True
            user.stripe_subscription_id = subscription_id
            user.subscription_status = subscription.status
            user.subscription_end_date = stripe.utils.convert_to_datetime(
                subscription.current_period_end
            )
            user.save(
                update_fields=[
                    "is_premium",
                    "stripe_subscription_id",
                    "subscription_status",
                    "subscription_end_date",
                ]
            )

            logger.info(f"User {user.id} subscribed successfully")

    except Exception as e:
        logger.error(f"Error handling checkout session completed: {str(e)}")


def handle_subscription_updated(subscription):
    """Handle subscription updated event."""
    try:
        from accounts.models import User

        customer_id = subscription.get("customer")
        user = User.objects.filter(stripe_customer_id=customer_id).first()

        if user:
            user.subscription_status = subscription.status
            user.subscription_end_date = stripe.utils.convert_to_datetime(
                subscription.current_period_end
            )
            user.is_premium = subscription.status in ("active", "trialing")
            user.save(
                update_fields=[
                    "subscription_status",
                    "subscription_end_date",
                    "is_premium",
                ]
            )

            logger.info(
                f"User {user.id} subscription updated to status: {subscription.status}"
            )

    except Exception as e:
        logger.error(f"Error handling subscription updated: {str(e)}")


def handle_subscription_deleted(subscription):
    """Handle subscription deleted event."""
    try:
        from accounts.models import User

        customer_id = subscription.get("customer")
        user = User.objects.filter(stripe_customer_id=customer_id).first()

        if user:
            user.is_premium = False
            user.subscription_status = "canceled"
            user.save(update_fields=["is_premium", "subscription_status"])

            logger.info(f"User {user.id} subscription canceled")

    except Exception as e:
        logger.error(f"Error handling subscription deleted: {str(e)}")


def handle_payment_failed(invoice):
    """Handle payment failed event."""
    try:
        from accounts.models import User

        customer_id = invoice.get("customer")
        user = User.objects.filter(stripe_customer_id=customer_id).first()

        if user:
            user.subscription_status = "past_due"
            user.save(update_fields=["subscription_status"])

            logger.warning(f"Payment failed for user {user.id}")

    except Exception as e:
        logger.error(f"Error handling payment failed: {str(e)}")
