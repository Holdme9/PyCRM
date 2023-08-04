from typing import Any, Dict

from django.db.models import QuerySet, Model
from django.forms import Form
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, render, redirect
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import generic
from django.contrib.auth import get_user_model

from .forms import OrganizationCreateForm, InvitationForm
from .models import Organization, Membership, MembershipInvitation
from leads.views import VerifyMembershipMixin

User = get_user_model()


class VerifyOwnershipMixin(PermissionRequiredMixin):
    """Verifies that user has the necessary membership to access a resource."""

    def has_permission(self) -> bool:
        """
        Checks if user has the necessary membership.

        Returns:
            bool: True if user has necessary membership, False otherwise.
        """
        user = self.request.user
        organization = get_object_or_404(Organization, id=self.kwargs['org_id'])
        membership = Membership.objects.filter(user=user, organization=organization).first()

        if membership.role == 'owner':
            return True

        return False

    def handle_no_permission(self) -> HttpResponseForbidden:
        """
        Handles the case when the user doesn't have the permission.

        Returns:
            HttpResponseForbidden: 403 response when access is denied.
        """
        return HttpResponseForbidden()


def MainPage(request):
    """A view to display a main page"""

    return render(request, 'main_page.html')


class OrganizationListView(LoginRequiredMixin, generic.ListView):
    """A view for displaying a list of organizations"""

    template_name = 'organizations/organization_list.html'
    context_object_name = 'organizations'

    def get_queryset(self) -> QuerySet[Any]:
        """Returns a queryset of organizations which user has a membership in."""
        user = self.request.user
        memberships = Membership.objects.filter(user=user)
        organizations = Organization.objects.filter(pk__in=memberships.values('organization'))
        return organizations


class OrganizationCreateView(LoginRequiredMixin, generic.CreateView):
    """A view for creating a new organization"""

    model = Organization
    form_class = OrganizationCreateForm
    template_name = 'organizations/organization_create.html'
    success_url = reverse_lazy('organizations:organization_list')

    def form_valid(self, form: Form) -> HttpResponseRedirect:
        """
        Creates a membership model instance after a valid form is submitted.

        Args:
            form: The validated form.

        Returns:
            HttpResponseRedirect: The HTTP response after processing the form.
        """

        user = self.request.user
        organization = form.save(commit=False)
        organization.save()
        Membership.objects.create(user=user, organization=organization, role='owner')
        return super().form_valid(form)


class OrganizationDetailView(VerifyMembershipMixin, generic.DetailView):
    """A view for displaying details of an organization."""

    template_name = 'organizations/organization_detail.html'
    context_object_name = 'organization'
    queryset = Organization.objects.all()

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        """Returns the object the view is displaying."""

        org_id = self.kwargs['org_id']
        return get_object_or_404(self.get_queryset(), id=org_id)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Provides data for the context dictionary."""

        context = super().get_context_data(**kwargs)
        org_id = self.kwargs['org_id']
        user = self.request.user
        memberships = Membership.objects.filter(organization=org_id)
        user_is_owner = get_object_or_404(memberships, user=user).role == 'owner'
        user_ids = memberships.values_list('user', flat=True)
        members = User.objects.filter(id__in=user_ids)
        context['members'] = members
        context['user_is_owner'] = user_is_owner
        return context


class OrganizationInviteView(VerifyOwnershipMixin, generic.FormView):
    """A view for inviting users to the organization."""

    form_class = InvitationForm
    template_name = 'organizations/organization_invite.html'
    success_url = reverse_lazy('organizations:organization_list')

    def form_valid(self, form):
        """
        Creates and sends the invitation to user if submitted form is valid
        and all conditions are met.
        """
        email = form.cleaned_data['email']
        organization = get_object_or_404(Organization, id=self.kwargs['org_id'])

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            form.add_error('email', 'Пользователя с таким email не существует')
            return self.form_invalid(form)

        try:
            membership = Membership.objects.get(user=user, organization=organization)
            form.add_error('email', 'Этот пользователь уже состоит в вашей организации')
            return self.form_invalid(form)
        except Membership.DoesNotExist:
            # Deleting old invitation if exists
            old_invitation = MembershipInvitation.objects.filter(
                organization=organization,
                email=email
                ).first()
            if old_invitation:
                old_invitation.delete()

            # Creating and sending new invitation
            invitation = MembershipInvitation.objects.create(organization=organization, email=email)
            link = self.request.build_absolute_uri(reverse_lazy(
                "organizations:organization_join",
                kwargs={"token": invitation.token}
                ))
            send_mail(
                f'Organization {organization} invites you to join it',
                f'To accept the invitation click the link below:\n\n{link}',
                'noreply@example.com',
                [email],
                fail_silently=False,
                )
            return super().form_valid(form)


class OrganizationJoinView(LoginRequiredMixin, generic.TemplateView):
    """A view for joining the organization."""

    template_name = 'organizations/organization_join.html'
    success_url = reverse_lazy('organizations:organization_list')

    def get(self, request, *args, **kwargs):
        token = self.kwargs['token']
        try:
            invitation = MembershipInvitation.objects.get(token=token)
        except MembershipInvitation.DoesNotExist:
            return redirect(reverse_lazy('organizations:organization_list'))
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        token = self.kwargs['token']
        invitation = get_object_or_404(MembershipInvitation, token=token)
        Membership.objects.create(
            user=request.user,
            organization=invitation.organization,
        )
        invitation.delete()
        return redirect(reverse_lazy('organizations:organization_list'))
