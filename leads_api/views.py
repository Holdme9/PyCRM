from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from leads.models import Lead
from .serializers import LeadSerializer
from organizations.models import Organization


class LeadListCreateAPIView(ListCreateAPIView):
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        org_id = self.kwargs['org_id']
        organization = Organization.objects.get(id=org_id)
        queryset = Lead.objects.filter(organization=organization)
        return queryset


class LeadRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]
