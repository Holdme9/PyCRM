from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import generic
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model

from .models import Lead
from .forms import LeadCreateUpdateForm
from organizations.models import Organization, Membership

User = get_user_model()


class GetQuerysetAndLeadContextObjectNameMixin:
    """Provides queryset and context object name for Lead model."""

    queryset = Lead.objects.all()
    context_object_name = 'lead'


class VerifyMembershipMixin(PermissionRequiredMixin):
    """Verifies that user has the necessary membership to access a resource."""

    def has_permission(self) -> bool:
        """
        Checks if user has the necessary membership.

        Returns:
            bool: True if user has necessary membership, False otherwise.
        """
        user = self.request.user
        organization = get_object_or_404(Organization, id=self.kwargs['org_id'])
        try:
            membership = Membership.objects.get(user=user, organization=organization)
            return True
        except Membership.DoesNotExist:
            return False

    def handle_no_permission(self) -> HttpResponseForbidden:
        """
        Handles the case when the user doesn't have the permission.

        Returns:
            HttpResponseForbidden: 403 response when access is denied.
        """
        return HttpResponseForbidden()


class GetContextDataMixin:
    """Provides additional context data for views."""

    def get_context_data(self, **kwargs) -> dict:
        """
        Gets id and queryset of leads related to certain organization.

        Returns:
            dict: The context data.
        """
        context = super().get_context_data(**kwargs)
        org_id = self.kwargs['org_id']
        organization = Organization.objects.get(id=org_id)
        leads = Lead.objects.filter(organization=organization)
        context['org_id'] = org_id
        context['leads'] = leads
        return context


class GetFormKwargsMixin:
    """Provides additional kwargs to forms."""

    def get_form_kwargs(self) -> dict:
        """
        Provides a queryset of users that have a certain membership.

        Returns:
            dict: The form kwargs.
        """
        kwargs = super().get_form_kwargs()
        organization = Organization.objects.get(id=self.kwargs['org_id'])
        users = Membership.objects.filter(organization=organization).values('user')
        kwargs['managers'] = User.objects.filter(id__in=users)
        return kwargs


class LeadCreateView(
    GetContextDataMixin,
    GetFormKwargsMixin,
    VerifyMembershipMixin,
    generic.CreateView
        ):
    """A view for creating a new lead."""
    model = Lead
    form_class = LeadCreateUpdateForm
    template_name = 'leads/lead_create.html'

    def form_valid(self, form):
        """
        Gets the organization and sets it as a value of a valid form's organization attribute.

        Args:
            form: The validated form.

        Returns:
            HttpResponseRedirect: The HTTP response after processing the form.
        """
        organization = Organization.objects.get(id=self.kwargs['org_id'])
        form.instance.organization = organization
        return super().form_valid(form)

    def get_success_url(self) -> str:
        """
        Get the URL to redirect to after a successful form submission.
        Returns:
            str: The success URL.
        """
        return reverse_lazy('organizations:leads:lead_list', kwargs={
            'org_id': self.kwargs['org_id'],
            })


class LeadListView(GetContextDataMixin, VerifyMembershipMixin, generic.ListView):
    """A view for displaying a list of leads."""

    template_name = 'leads/lead_list.html'
    queryset = Lead.objects.all()


class LeadDetailView(
    GetContextDataMixin,
    VerifyMembershipMixin,
    GetQuerysetAndLeadContextObjectNameMixin,
    generic.DetailView
):
    """A view for displaying details of lead."""

    template_name = 'leads/lead_detail.html'


class LeadUpdateView(
    GetFormKwargsMixin,
    GetContextDataMixin,
    VerifyMembershipMixin,
    GetQuerysetAndLeadContextObjectNameMixin,
    generic.UpdateView
):
    """A view for updating a lead."""

    form_class = LeadCreateUpdateForm
    template_name = 'leads/lead_update.html'

    def get_success_url(self) -> str:
        """
        Get the URL to redirect to after a successful form submission.

        Returns:
            str: The success URL.
        """
        return reverse_lazy('organizations:leads:lead_detail', kwargs={
            'org_id': self.kwargs['org_id'],
            'pk': self.kwargs['pk'],
            })


class LeadDeleteView(
    GetContextDataMixin,
    VerifyMembershipMixin,
    GetQuerysetAndLeadContextObjectNameMixin,
    generic.DeleteView
):
    """A view for deleting a lead."""

    template_name = 'leads/lead_delete.html'
