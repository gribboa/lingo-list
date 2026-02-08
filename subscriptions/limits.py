"""Utility functions for checking free tier limits."""
from django.conf import settings
from lists.models import Collaborator, List, ListItem


def can_create_list(user):
    """Check if user can create a new list."""
    if user.has_active_subscription():
        return True, None

    owned_count = List.objects.filter(owner=user).count()
    if owned_count >= settings.FREE_TIER_MAX_LISTS:
        return False, f"Free tier limited to {settings.FREE_TIER_MAX_LISTS} lists. Upgrade to premium for unlimited lists."

    return True, None


def can_add_item(list_obj):
    """Check if an item can be added to a list."""
    if list_obj.owner.has_active_subscription():
        return True, None

    item_count = ListItem.objects.filter(list=list_obj).count()
    if item_count >= settings.FREE_TIER_MAX_ITEMS_PER_LIST:
        return False, f"Free tier limited to {settings.FREE_TIER_MAX_ITEMS_PER_LIST} items per list. Upgrade to premium for unlimited items."

    return True, None


def can_add_collaborator(list_obj):
    """Check if a collaborator can be added to a list."""
    if list_obj.owner.has_active_subscription():
        return True, None

    collab_count = Collaborator.objects.filter(list=list_obj).count()
    if collab_count >= settings.FREE_TIER_MAX_COLLABORATORS_PER_LIST:
        max_count = settings.FREE_TIER_MAX_COLLABORATORS_PER_LIST
        collaborator_word = "collaborator" if max_count == 1 else "collaborators"
        return False, f"Free tier limited to {max_count} {collaborator_word} per list. Upgrade to premium for unlimited collaborators."

    return True, None


def get_list_limit_status(user):
    """Get current usage and limits for lists."""
    owned_count = List.objects.filter(owner=user).count()
    return {
        "current": owned_count,
        "max": settings.FREE_TIER_MAX_LISTS if not user.has_active_subscription() else None,
        "is_premium": user.has_active_subscription(),
    }


def get_item_limit_status(list_obj):
    """Get current usage and limits for items in a list."""
    item_count = ListItem.objects.filter(list=list_obj).count()
    is_premium = list_obj.owner.has_active_subscription()
    return {
        "current": item_count,
        "max": settings.FREE_TIER_MAX_ITEMS_PER_LIST if not is_premium else None,
        "is_premium": is_premium,
    }


def get_collaborator_limit_status(list_obj):
    """Get current usage and limits for collaborators on a list."""
    collab_count = Collaborator.objects.filter(list=list_obj).count()
    is_premium = list_obj.owner.has_active_subscription()
    return {
        "current": collab_count,
        "max": settings.FREE_TIER_MAX_COLLABORATORS_PER_LIST if not is_premium else None,
        "is_premium": is_premium,
    }
