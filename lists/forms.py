from django import forms

from .models import List, ListItem


class ListForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ("title", "description")
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "e.g. Weekly Groceries",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-input",
                "placeholder": "Optional description...",
                "rows": 2,
            }),
        }


class ListItemForm(forms.ModelForm):
    class Meta:
        model = ListItem
        fields = ("text",)
        widgets = {
            "text": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Add an item...",
                "autocomplete": "off",
            }),
        }
