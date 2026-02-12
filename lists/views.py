import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from translations.services import get_items_for_user, get_translated_text

from .forms import ListForm, ListItemForm, ListTitleForm
from .models import Collaborator, List, ListItem


@login_required
def list_index(request):
    """Show all non-archived lists the user owns or collaborates on."""
    owned = List.objects.filter(owner=request.user)
    collaborated = List.objects.filter(collaborators__user=request.user)
    all_lists = (owned | collaborated).distinct().filter(is_archived=False)

    # Annotate with is_pinned and order pinned first, then by updated_at
    all_lists = all_lists.annotate(
        is_pinned=models.Exists(
            List.pinned_by.through.objects.filter(
                list_id=models.OuterRef("pk"), user_id=request.user.id
            )
        )
    ).order_by("-is_pinned", "-updated_at")

    has_archived = List.objects.filter(owner=request.user, is_archived=True).exists()

    return render(request, "lists/index.html", {"lists": all_lists, "has_archived": has_archived})


@login_required
def list_archived(request):
    """Show all archived lists owned by the current user."""
    archived_lists = List.objects.filter(
        owner=request.user, is_archived=True
    ).order_by("-updated_at")

    return render(request, "lists/archived.html", {"lists": archived_lists})


@login_required
@require_POST
def list_archive_toggle(request, pk):
    """Toggle archived status of a list (owner only)."""
    lst = get_object_or_404(List, pk=pk, owner=request.user)
    lst.is_archived = not lst.is_archived
    lst.save(update_fields=["is_archived"])

    if lst.is_archived:
        messages.success(
            request,
            _('"%(title)s" has been archived.') % {"title": lst.title},
        )
        return redirect("lists:list_index")
    else:
        messages.success(
            request,
            _('"%(title)s" has been unarchived.') % {"title": lst.title},
        )
        return redirect("lists:list_archived")


@login_required
@require_POST
def list_pin_toggle(request, pk):
    """Toggle pinned status of a list for the current user."""
    lst = get_object_or_404(List, pk=pk)
    if not lst.is_member(request.user):
        return HttpResponse(status=403)

    if lst.pinned_by.filter(pk=request.user.pk).exists():
        lst.pinned_by.remove(request.user)
    else:
        lst.pinned_by.add(request.user)

    return redirect("lists:list_index")


@login_required
def list_create(request):
    """Create a new list."""
    if request.method == "POST":
        form = ListForm(request.POST)
        if form.is_valid():
            lst = form.save(commit=False)
            lst.owner = request.user
            lst.save()
            return redirect("lists:list_detail", pk=lst.pk)
    else:
        form = ListForm()
    return render(request, "lists/create.html", {"form": form})


@login_required
def list_detail(request, pk):
    """View a single list with its items (translated for the current user)."""
    lst = get_object_or_404(List, pk=pk)
    if not lst.is_member(request.user):
        messages.error(request, _("You don't have access to this list."))
        return redirect("lists:list_index")

    is_owner = lst.owner == request.user

    # Collaborators cannot access archived lists
    if lst.is_archived and not is_owner:
        messages.error(request, _("This list has been archived."))
        return redirect("lists:list_index")

    item_form = ListItemForm()
    title_form = ListTitleForm(instance=lst) if is_owner and not lst.is_archived else None
    items = get_items_for_user(lst, request.user)
    collaborators = lst.collaborators.select_related("user").all()

    return render(
        request,
        "lists/detail.html",
        {
            "list": lst,
            "items": items,
            "item_form": item_form,
            "title_form": title_form,
            "collaborators": collaborators,
            "is_owner": is_owner,
        },
    )


@login_required
@require_POST
def list_rename(request, pk):
    """Rename a list and update description (owner only)."""
    lst = get_object_or_404(List, pk=pk, owner=request.user)
    if lst.is_archived:
        messages.error(request, _("Archived lists cannot be edited."))
        return redirect("lists:list_detail", pk=lst.pk)

    form = ListTitleForm(request.POST, instance=lst)
    if form.is_valid():
        if form.has_changed():
            form.save()
            messages.success(request, _("List updated."))
        else:
            messages.info(request, _("No changes made."))
    else:
        title_errors = form.errors.get("title")
        messages.error(
            request,
            title_errors[0] if title_errors else _("Unable to update list."),
        )

    return redirect("lists:list_detail", pk=lst.pk)


@login_required
@require_POST
def item_add(request, pk):
    """Add an item to a list (HTMX endpoint)."""
    lst = get_object_or_404(List, pk=pk)
    if not lst.is_member(request.user):
        return HttpResponse(status=403)
    if lst.is_archived:
        return HttpResponse(status=403)

    form = ListItemForm(request.POST)
    if form.is_valid():
        item = form.save(commit=False)
        item.list = lst
        item.added_by = request.user
        item.source_language = request.user.preferred_language
        # Set order to be at the end
        max_order = lst.items.aggregate(models.Max("order"))["order__max"] or 0
        item.order = max_order + 1
        item.save()
        lst.save()  # bump updated_at

    # Return the full updated item list for this user
    items = get_items_for_user(lst, request.user)
    return render(
        request,
        "partials/item_list.html",
        {
            "items": items,
            "list": lst,
        },
    )


@login_required
@require_POST
def item_toggle(request, pk, item_pk):
    """Toggle an item's checked status (HTMX endpoint)."""
    lst = get_object_or_404(List, pk=pk)
    if not lst.is_member(request.user):
        return HttpResponse(status=403)
    if lst.is_archived:
        return HttpResponse(status=403)

    item = get_object_or_404(ListItem, pk=item_pk, list=lst)
    item.is_checked = not item.is_checked

    # When checking an item, move it to the end of the manual sort order.
    if item.is_checked:
        max_order = (
            ListItem.objects.filter(list=lst).exclude(pk=item.pk).aggregate(models.Max("order"))["order__max"] or 0
        )
        item.order = max_order + 1
        item.save(update_fields=["is_checked", "order"])
    else:
        item.save(update_fields=["is_checked"])

    items = get_items_for_user(lst, request.user)
    return render(
        request,
        "partials/item_list.html",
        {
            "items": items,
            "list": lst,
        },
    )


@login_required
@require_POST
def item_delete(request, pk, item_pk):
    """Delete an item from a list (HTMX endpoint)."""
    lst = get_object_or_404(List, pk=pk)
    if not lst.is_member(request.user):
        return HttpResponse(status=403)
    if lst.is_archived:
        return HttpResponse(status=403)

    item = get_object_or_404(ListItem, pk=item_pk, list=lst)
    item.delete()

    items = get_items_for_user(lst, request.user)
    return render(
        request,
        "partials/item_list.html",
        {
            "items": items,
            "list": lst,
        },
    )


@login_required
@require_POST
def item_reorder(request, pk):
    """Reorder items in a list (HTMX/AJAX endpoint)."""
    lst = get_object_or_404(List, pk=pk)
    if not lst.is_member(request.user):
        return HttpResponse(status=403)
    if lst.is_archived:
        return HttpResponse(status=403)

    try:
        data = json.loads(request.body)
        item_ids = data.get("item_ids", [])
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    # Update order for each item
    for index, item_id in enumerate(item_ids):
        ListItem.objects.filter(pk=item_id, list=lst).update(order=index)

    return HttpResponse(status=204)


@login_required
@require_POST
def item_translate(request, pk, item_pk):
    """Translate a single item and return its rendered row (HTMX endpoint)."""
    lst = get_object_or_404(List, pk=pk)
    if not lst.is_member(request.user):
        return HttpResponse(status=403)

    item = get_object_or_404(ListItem, pk=item_pk, list=lst)
    target = request.user.preferred_language

    display_text = get_translated_text(item, target)
    is_translated = item.source_language != target and display_text != item.text

    return render(
        request,
        "partials/item_row.html",
        {
            "entry": {
                "item": item,
                "display_text": display_text,
                "is_translated": is_translated,
                "translation_pending": False,
            },
            "list": lst,
        },
    )


@login_required
def list_join(request, token):
    """Join a list via a share link."""
    lst = get_object_or_404(List, share_token=token)

    if lst.is_archived:
        messages.error(
            request,
            _("This list has been archived and is not accepting new collaborators."),
        )
        return redirect("lists:list_index")

    if lst.owner == request.user:
        messages.info(request, _("You already own this list."))
        return redirect("lists:list_detail", pk=lst.pk)

    _, created = Collaborator.objects.get_or_create(list=lst, user=request.user)
    if created:
        messages.success(
            request,
            _('You joined "%(title)s"!') % {"title": lst.title},
        )
    else:
        messages.info(request, _("You are already a collaborator on this list."))

    return redirect("lists:list_detail", pk=lst.pk)


@login_required
@require_POST
def collaborator_remove(request, pk, collab_pk):
    """Remove a collaborator from a list (owner only)."""
    lst = get_object_or_404(List, pk=pk, owner=request.user)
    collab = get_object_or_404(Collaborator, pk=collab_pk, list=lst)
    collab.delete()

    collaborators = lst.collaborators.select_related("user").all()
    return render(
        request,
        "partials/collaborator_list.html",
        {
            "collaborators": collaborators,
            "list": lst,
            "is_owner": True,
        },
    )


@login_required
@require_POST
def list_delete(request, pk):
    """Delete a list (owner only)."""
    lst = get_object_or_404(List, pk=pk, owner=request.user)
    lst.delete()
    return redirect("lists:list_index")
