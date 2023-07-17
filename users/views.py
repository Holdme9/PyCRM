from django.urls import reverse_lazy
from .forms import SignupForm, UserUpdateForm
from django.views import generic
from .models import User


class UserSignupView(generic.CreateView):
    template_name = 'users/signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('users:login')
    success_message = 'Вы успешно зарегистрировались!'


class UserProfileView(generic.DetailView):
    template_name = 'users/profile.html'
    context_object_name = 'user'
    queryset = User.objects.all()


class UserUpdateView(generic.UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'users/user_update.html'
    context_object_name = 'user'
    queryset = User.objects.all()

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        pk = self.kwargs['pk']
        return reverse_lazy('users:user_profile', kwargs={'pk': pk})


class UserDeleteView(generic.DeleteView):
    template_name = 'users/user_delete.html'
    success_url = reverse_lazy('users:login')
    context_object_name = 'user'
    queryset = User.objects.all()
