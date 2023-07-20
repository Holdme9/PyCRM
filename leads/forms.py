from typing import Any, Dict, Mapping, Optional, Type, Union
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from .models import Lead
from organizations.models import Organization, Membership


class LeadCreateUpdateForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = [
            'first_name',
            'last_name',
            'order',
            'price',
            'email',
            'phone',
            'comment',
            'manager',
            'status',
        ]

    def __init__(self, *args, **kwargs):
        managers = kwargs.pop('managers', None)
        super().__init__(*args, **kwargs)
        self.empty_permitted = True
        self.use_required_attribute = False
        self.fields['manager'].queryset = managers

