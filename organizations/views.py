from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import CreateView, FormView, TemplateView
from .forms import OrganizationCreateForm, InvitationForm
from .models import Organization, Membership, MembershipInvitation


def OrganizationList(request):
    context = {'organizations': Membership.objects.get(user=request.user)}
    return render(request, 'organizations/organization_list.html', context=context)


class OrganizationCreateView(LoginRequiredMixin, CreateView):
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


# Позже нужно сделать так, чтобы только у владельца была возможность приглашать менеджеров
# А также скрыть эту опцию в шаблоне, чтобы она вообще у менеджеров не отображалась.
# И еще чтобы нельзя было приглашать юзеров, которые уже состоят в организации,
# Либо, чтобы запись не создавалась, когда приглашение принималось.

class OrganizationInviteView(LoginRequiredMixin, FormView):
    form_class = InvitationForm
    template_name = 'organizations/organization_invite.html'
    success_url = reverse_lazy('organizations:organization_list')

    def get_queryset(self):
        user = self.request.user
        role = 'owner'
        queryset = Membership.objects.filter(user=user).filter(role=role)

    def form_valid(self, form):
        email = form.cleaned_data['email']
        organization = form.cleaned_data['organization']
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


class OrganizationJoinView(TemplateView):
    template_name = 'organizations/organization_join.html'
    success_url = reverse_lazy('organizations:organization_list')

    def get(self, request, *args, **kwargs):
        token = kwargs.get('token')
        try:
            invitation = MembershipInvitation.objects.get(token=token)
        except MembershipInvitation.DoesNotExist:
            return redirect(reverse_lazy('organizations:organisation_list'))
        return super().get(request, *args, **kwargs)

    # нужно также сделать логику, чтобы пользователю нельзя было отправить приглашение
    # если он уже является членом организации

    def post(self, request, *args, **kwargs):
        token = kwargs.get('token')
        try:
            invitation = MembershipInvitation.objects.get(token=token)
        except MembershipInvitation.DoesNotExist:
            return redirect(reverse_lazy('organizations:organisation_list'))
        membership = Membership.objects.create(
            user=request.user,
            organization=invitation.organization,
            role='sales manager'
        )
        membership.save()
        invitation.delete()
        return redirect(reverse_lazy('organizations:organisation_list'))
