from django.urls import path

from . import views

app_name = "lists"

urlpatterns = [
    path("", views.list_index, name="list_index"),
    path("archived/", views.list_archived, name="list_archived"),
    path("new/", views.list_create, name="list_create"),
    path("<int:pk>/", views.list_detail, name="list_detail"),
    path("<int:pk>/pin/", views.list_pin_toggle, name="list_pin_toggle"),
    path("<int:pk>/archive/", views.list_archive_toggle, name="list_archive_toggle"),
    path("<int:pk>/delete/", views.list_delete, name="list_delete"),
    path("<int:pk>/items/add/", views.item_add, name="item_add"),
    path("<int:pk>/items/reorder/", views.item_reorder, name="item_reorder"),
    path("<int:pk>/items/<int:item_pk>/toggle/", views.item_toggle, name="item_toggle"),
    path("<int:pk>/items/<int:item_pk>/delete/", views.item_delete, name="item_delete"),
    path(
        "<int:pk>/collaborators/<int:collab_pk>/remove/",
        views.collaborator_remove,
        name="collaborator_remove",
    ),
    path("join/<str:token>/", views.list_join, name="list_join"),
]
