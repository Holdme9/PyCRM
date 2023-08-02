from django.contrib import admin
from .models import Organization, Membership, MembershipInvitation


admin.site.register(Organization)
admin.site.register(Membership)
admin.site.register(MembershipInvitation)
