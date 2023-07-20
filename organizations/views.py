from typing import Any, Dict
from django.db.models import QuerySet, Model
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views import generic
from .forms import OrganizationCreateForm, InvitationForm
from .models import Organization, Membership, MembershipInvitation
from users.models import User


class OrganizationListView(LoginRequiredMixin, generic.ListView):
    model = Organization
    template_name = 'organizations/organization_list.html'
    context_object_name = 'organizations'

    def get_queryset(self) -> QuerySet[Any]:
        user = self.request.user
        memberships = Membership.objects.filter(user=user)
        organizations = Organization.objects.filter(pk__in=memberships.values('organization'))
        return organizations


def MainPage(request):
    return render(request, 'main_page.html')


class OrganizationCreateView(LoginRequiredMixin, generic.CreateView):
    model = Organization
    form_class = OrganizationCreateForm
    template_name = 'organizations/organization_create.html'
    success_url = reverse_lazy('organizations:organization_list')

    def form_valid(self, form):
        user = self.request.user
        organization = form.save(commit=False)
        organization.save()
        membership = Membership.objects.create(user=user, organization=organization, role='owner')
        membership.save()
        return super().form_valid(form)


class OrganizationDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'organizations/organization_detail.html'
    context_object_name = 'organization'
    queryset = Organization.objects.all()

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        org_id = self.kwargs['org_id']
        return self.get_queryset().get(id=org_id)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        org_id = self.kwargs['org_id']
        memberships = Membership.objects.filter(organization=org_id)
        user = self.request.user
        user_is_owner = memberships.get(user=user).role == 'owner'
        user_ids = memberships.values_list('user', flat=True)
        members = User.objects.filter(id__in=user_ids)
        context['members'] = members
        context['user_is_owner'] = user_is_owner
        return context


class OrganizationInviteView(PermissionRequiredMixin, generic.FormView):
    form_class = InvitationForm
    template_name = 'organizations/organization_invite.html'
    success_url = reverse_lazy('organizations:organization_list')

    def has_permission(self) -> bool:
        user = self.request.user
        org_id = self.kwargs['org_id']
        organization = Organization.objects.get(id=org_id)
        user_role = Membership.objects.get(user=user, organization=organization).role
        if user_role == 'owner':
            return True
        raise PermissionDenied

    def form_valid(self, form):
        email = form.cleaned_data['email']
        organization = Organization.objects.get(id=self.kwargs['org_id'])
        
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
            invitation = MembershipInvitation.objects.create(organization=organization, email=email)
            send_mail(
                f'Organization {organization} invites you to join it',
                'To accept the invitation click link below:\n\n'
                + self.request.build_absolute_uri(reverse_lazy(
                        "organizations:organization_join",
                        kwargs={'token': invitation.token})),
                'noreply@example.com',
                [email],
                fail_silently=False,
                )
            return super().form_valid(form)


class OrganizationJoinView(generic.TemplateView):
    template_name = 'organizations/organization_join.html'
    success_url = reverse_lazy('organizations:organization_list')

    def get(self, request, *args, **kwargs):
        token = kwargs.get('token')
        try:
            invitation = MembershipInvitation.objects.get(token=token)
        except MembershipInvitation.DoesNotExist:
            return redirect(reverse_lazy('organizations:organization_list'))
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        token = kwargs.get('token')
        try:
            invitation = MembershipInvitation.objects.get(token=token)
        except MembershipInvitation.DoesNotExist:
            return redirect(reverse_lazy('organizations:organization_list'))
        membership = Membership.objects.create(
            user=request.user,
            organization=invitation.organization,
            role='sales manager'
        )
        membership.save()
        invitation.delete()
        return redirect(reverse_lazy('organizations:organisation_list'))
