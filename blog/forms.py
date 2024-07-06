from typing import Any
from django import forms
from .models import *

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit



class CreateBlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'topic', 'content']

class SearchForm(forms.Form):
    CHOICE_LIST = Topic.objects.all()
    search_string = forms.CharField(label="Cerca",max_length=100, min_length=3, required=True)
    search_where = forms.ModelChoiceField(label="Topic", required=False, queryset=CHOICE_LIST)


