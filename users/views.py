from typing import Any, Dict

from django.forms.models import BaseModelForm
from django.http import HttpResponse, HttpResponseForbidden
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404

from .forms import SignupForm, UserUpdateForm

User = get_user_model()


class VerifyUserMixin(PermissionRequiredMixin):
    """Verifies that user has the necessary membership to access a resource."""

    def has_permission(self) -> bool:
        """
        Checks if requesting user is operating with their own profile.

        Returns:
            bool: True if user has necessary membership, False otherwise.
        """
        user = get_object_or_404(User, id=self.kwargs['pk'])
        requesting_user = self.request.user
        return user == requesting_user

    def handle_no_permission(self) -> HttpResponseForbidden:
        """
        Handles the case when the user doesn't have the permission.

        Returns:
            HttpResponseForbidden: 403 response when access is denied.
        """
        return HttpResponseForbidden()


class GetQuerysetAndContextObjectNameMixin:
    """Provides queryset and context object name for User model."""

    context_object_name = 'user'
    queryset = User.objects.all()


class UserSignupView(generic.CreateView):
    """A view for creating a new user."""

    template_name = 'users/signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        """
        Returns form invalid if user with provided email already exists,
        returns form valid otherwise.
        """
        email = form.cleaned_data['email']
        user = User.objects.filter(email=email).first()

        if user:
            form.add_error('email', 'Пользователь с таким email уже существует.')
            return self.form_invalid(form)

        return super().form_valid(form)


class UserProfileView(GetQuerysetAndContextObjectNameMixin, generic.DetailView):
    """A view for displaying details of user."""

    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, id=self.kwargs['pk'])
        context['own_profile'] = self.request.user == user
        return context


class UserUpdateView(VerifyUserMixin, GetQuerysetAndContextObjectNameMixin, generic.UpdateView):
    """A view for for updating details of user."""

    form_class = UserUpdateForm
    template_name = 'users/user_update.html'

    def get_success_url(self) -> str:
        """
        Get the URL to redirect to after a successful form submission.
        Returns:
            str: The success URL.
        """
        pk = self.kwargs['pk']
        return reverse_lazy('users:user_profile', kwargs={'pk': pk})


class UserDeleteView(VerifyUserMixin, GetQuerysetAndContextObjectNameMixin, generic.DeleteView):
    """A view for deleting a user"""

    template_name = 'users/user_delete.html'
    success_url = reverse_lazy('users:login')
