from typing import Any, Mapping
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from .models import Chat, Message


class ChatForm(forms.ModelForm):

    class Meta:
        model = Message
        fields = ('message', )
        widgets = {
            'message': forms.widgets.TextInput()
        }
