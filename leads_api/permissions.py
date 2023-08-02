from rest_framework import permissions

from organizations.models import Organization, Membership


class MembershipPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        org_id = view.kwargs.get('org_id')
        organization = Organization.objects.get(id=org_id)

        try:
            membership = Membership.objects.get(user=user, organization=organization)
            return True
        except Membership.DoesNotExist:
            return False
