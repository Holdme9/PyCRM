from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from leads.models import Lead
from .serializers import LeadSerializer
from organizations.models import Organization
from .permissions import MembershipPermission


class LeadListCreateAPIView(ListCreateAPIView):
    serializer_class = LeadSerializer
    permission_classes = [MembershipPermission]

    def get_queryset(self):
        org_id = self.kwargs['org_id']
        organization = Organization.objects.get(id=org_id)
        queryset = Lead.objects.filter(organization=organization)
        return queryset


class LeadRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = LeadSerializer
    permission_classes = [MembershipPermission]

    def get_queryset(self):
        org_id = self.kwargs.get('org_id')
        organization = Organization.objects.get(id=org_id)
        queryset = Lead.objects.filter(organization=organization)
        return queryset
