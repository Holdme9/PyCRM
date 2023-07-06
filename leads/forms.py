from django import forms
from .models import Lead
from organizations.models import Organization


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

    # def __init__(self, org_id, *args, **kwargs) -> None:
    #     super().__init__(*args, **kwargs)
    #     self.org_id = kwargs['org_id']

    # def save(self, commit=True):
    #     lead = super().save(commit=False)
    #     lead.organization = Organization.objects.get(pk=self.org_id)
    #     if commit:
    #         lead.save()
    #     return lead
