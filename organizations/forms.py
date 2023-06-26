from django import forms
from .models import Organization, MembershipInvitation


class OrganizationCreateForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', ]


class InvitationForm(forms.ModelForm):
    organization = forms.ModelChoiceField(queryset=Organization.objects.all())

    class Meta:
        model = MembershipInvitation
        fields = ['organization', 'email', ]
