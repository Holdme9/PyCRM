from typing import Any, Dict
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import generic
from .models import Lead
from users.models import User
from .forms import LeadCreateUpdateForm
from organizations.models import Organization, Membership
from django.core.exceptions import PermissionDenied


class GetQuerysetAndLeadContextObjectNameMixin():
    queryset = Lead.objects.all()
    context_object_name = 'lead'


class VerifyMembershipMixin(PermissionRequiredMixin):

    def has_permission(self) -> bool:
        user = self.request.user
        organization = Organization.objects.get(id=self.kwargs['org_id'])
        try:
            membership = Membership.objects.get(user=user, organization=organization)
            return True
        except Membership.DoesNotExist:
            raise PermissionDenied


class LeadCreateView(VerifyMembershipMixin, generic.CreateView):
    model = Lead
    form_class = LeadCreateUpdateForm
    template_name = 'leads/lead_create.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['org_id'] = self.kwargs['org_id']
        return context

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        organization = Organization.objects.get(id=self.kwargs['org_id'])
        user_ids = Membership.objects.filter(organization=organization).values('user')
        kwargs['managers'] = User.objects.filter(id__in=user_ids)
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        org_id = self.kwargs['org_id']
        organization = Organization.objects.get(id=org_id)
        form.instance.organization = organization
        return super().form_valid(form)

    def get_success_url(self) -> str:
        org_id = self.kwargs['org_id']
        return reverse_lazy('organizations:leads:lead_list', kwargs={'org_id': org_id})


class LeadListView(VerifyMembershipMixin, generic.ListView):
    template_name = 'leads/lead_list.html'
    queryset = Lead.objects.all()

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        org_id = self.kwargs['org_id']
        organization = Organization.objects.get(id=org_id)
        leads = Lead.objects.filter(organization=organization)
        context['leads'] = leads
        context['org_id'] = org_id
        return context


class LeadDetailView(
    VerifyMembershipMixin,
    GetQuerysetAndLeadContextObjectNameMixin,
    generic.DetailView
):
    template_name = 'leads/lead_detail.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['org_id'] = self.kwargs['org_id']
        return context


class LeadUpdateView(
    VerifyMembershipMixin,
    GetQuerysetAndLeadContextObjectNameMixin,
    generic.UpdateView
):
    model = Lead
    form_class = LeadCreateUpdateForm
    template_name = 'leads/lead_update.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['org_id'] = self.kwargs['org_id']
        return context

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        organization = Organization.objects.get(id=self.kwargs['org_id'])
        user_ids = Membership.objects.filter(organization=organization).values('user')
        kwargs['managers'] = User.objects.filter(id__in=user_ids)
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        org_id = self.kwargs['org_id']
        pk = self.kwargs['pk']
        return reverse_lazy('organizations:leads:lead_detail',
                            kwargs={'org_id': org_id, 'pk': pk})


class LeadDeleteView(
    VerifyMembershipMixin,
    GetQuerysetAndLeadContextObjectNameMixin,
    generic.DeleteView
):
    template_name = 'leads/lead_delete.html'

    def get_success_url(self) -> str:
        org_id = self.kwargs['org_id']
        return reverse_lazy('organizations:leads:lead_list', kwargs={'org_id': org_id})

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['org_id'] = self.kwargs['org_id']
        return context
