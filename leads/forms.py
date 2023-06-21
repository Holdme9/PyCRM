from django import forms
from .models import Lead


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
            'status',
        ]
