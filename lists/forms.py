from django import forms
from django.utils.translation import gettext_lazy as _

from .models import List, ListItem


class ListForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ("title", "description")
        labels = {
            "title": _("List name"),
            "description": _("Description"),
        }
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": _("e.g. Weekly groceries"),
            }),
            "description": forms.Textarea(attrs={
                "class": "form-input",
                "placeholder": _("Optional description..."),
                "rows": 2,
            }),
        }


class ListTitleForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ("title",)
        labels = {
            "title": _("List name"),
        }
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": _("List name"),
            }),
        }


class ListItemForm(forms.ModelForm):
    class Meta:
        model = ListItem
        fields = ("text",)
        labels = {
            "text": _("Item"),
        }
        widgets = {
            "text": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": _("Add an item..."),
                "autocomplete": "off",
            }),
        }
