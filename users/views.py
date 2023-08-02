from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import get_user_model

from .forms import SignupForm, UserUpdateForm

User = get_user_model()


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


class UserUpdateView(GetQuerysetAndContextObjectNameMixin, generic.UpdateView):
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


class UserDeleteView(GetQuerysetAndContextObjectNameMixin, generic.DeleteView):
    """A view for deleting a user"""

    template_name = 'users/user_delete.html'
    success_url = reverse_lazy('users:login')
