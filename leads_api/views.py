from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from django.shortcuts import get_object_or_404

from leads.models import Lead
from .serializers import LeadSerializer
from organizations.models import Organization
from .permissions import MembershipPermission


class GetQuerysetMixin:

    def get_queryset(self):
        org_id = self.kwargs['org_id']
        organization = get_object_or_404(Organization, id=org_id)
        queryset = Lead.objects.filter(organization=organization)
        return queryset


class LeadListCreateAPIView(GetQuerysetMixin, ListCreateAPIView):
    serializer_class = LeadSerializer
    permission_classes = [MembershipPermission]


class LeadRetrieveUpdateDestroyAPIView(GetQuerysetMixin, RetrieveUpdateDestroyAPIView):
    serializer_class = LeadSerializer
    permission_classes = [MembershipPermission]
