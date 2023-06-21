from django.urls import reverse_lazy
from .forms import SignupForm
from django.views.generic import CreateView


class SignupView(CreateView):
    template_name = 'users/signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('users:login')
    success_message = 'Вы успешно зарегистрировались!'
