from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from translations.services import get_items_for_user

from .forms import ListForm, ListItemForm
from .models import Collaborator, List, ListItem


@login_required
def list_index(request):
    """Show all lists the user owns or collaborates on."""
    owned = List.objects.filter(owner=request.user)
    collaborated = List.objects.filter(collaborators__user=request.user)
    all_lists = (owned | collaborated).distinct().order_by("-updated_at")
    return render(request, "lists/index.html", {"lists": all_lists})


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
        messages.error(request, "You don't have access to this list.")
        return redirect("lists:list_index")

    item_form = ListItemForm()
    items = get_items_for_user(lst, request.user)
    collaborators = lst.collaborators.select_related("user").all()
    is_owner = lst.owner == request.user

    return render(request, "lists/detail.html", {
        "list": lst,
        "items": items,
        "item_form": item_form,
        "collaborators": collaborators,
        "is_owner": is_owner,
    })


@login_required
@require_POST
def item_add(request, pk):
    """Add an item to a list (HTMX endpoint)."""
    lst = get_object_or_404(List, pk=pk)
    if not lst.is_member(request.user):
        return HttpResponse(status=403)

    form = ListItemForm(request.POST)
    if form.is_valid():
        item = form.save(commit=False)
        item.list = lst
        item.added_by = request.user
        item.source_language = request.user.preferred_language
        item.save()
        lst.save()  # bump updated_at

    # Return the full updated item list for this user
    items = get_items_for_user(lst, request.user)
    return render(request, "partials/item_list.html", {
        "items": items,
        "list": lst,
    })


@login_required
@require_POST
def item_toggle(request, pk, item_pk):
    """Toggle an item's checked status (HTMX endpoint)."""
    lst = get_object_or_404(List, pk=pk)
    if not lst.is_member(request.user):
        return HttpResponse(status=403)

    item = get_object_or_404(ListItem, pk=item_pk, list=lst)
    item.is_checked = not item.is_checked
    item.save(update_fields=["is_checked"])

    items = get_items_for_user(lst, request.user)
    return render(request, "partials/item_list.html", {
        "items": items,
        "list": lst,
    })


@login_required
@require_POST
def item_delete(request, pk, item_pk):
    """Delete an item from a list (HTMX endpoint)."""
    lst = get_object_or_404(List, pk=pk)
    if not lst.is_member(request.user):
        return HttpResponse(status=403)

    item = get_object_or_404(ListItem, pk=item_pk, list=lst)
    item.delete()

    items = get_items_for_user(lst, request.user)
    return render(request, "partials/item_list.html", {
        "items": items,
        "list": lst,
    })


@login_required
def list_join(request, token):
    """Join a list via a share link."""
    lst = get_object_or_404(List, share_token=token)

    if lst.owner == request.user:
        messages.info(request, "You already own this list.")
        return redirect("lists:list_detail", pk=lst.pk)

    _, created = Collaborator.objects.get_or_create(list=lst, user=request.user)
    if created:
        messages.success(request, f'You joined "{lst.title}"!')
    else:
        messages.info(request, "You are already a collaborator on this list.")

    return redirect("lists:list_detail", pk=lst.pk)


@login_required
@require_POST
def collaborator_remove(request, pk, collab_pk):
    """Remove a collaborator from a list (owner only)."""
    lst = get_object_or_404(List, pk=pk, owner=request.user)
    collab = get_object_or_404(Collaborator, pk=collab_pk, list=lst)
    collab.delete()

    collaborators = lst.collaborators.select_related("user").all()
    return render(request, "partials/collaborator_list.html", {
        "collaborators": collaborators,
        "list": lst,
        "is_owner": True,
    })


@login_required
@require_POST
def list_delete(request, pk):
    """Delete a list (owner only)."""
    lst = get_object_or_404(List, pk=pk, owner=request.user)
    lst.delete()
    return redirect("lists:list_index")
