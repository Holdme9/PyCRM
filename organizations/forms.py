from django import forms
from .models import Organization, MembershipInvitation


class OrganizationCreateForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', ]


class InvitationForm(forms.ModelForm):
    class Meta:
        model = MembershipInvitation
        fields = ['email', ]
