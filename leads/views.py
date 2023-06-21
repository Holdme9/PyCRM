from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from .models import Lead
from .forms import LeadCreateUpdateForm


class LeadMixin(LoginRequiredMixin):
    queryset = Lead.objects.all()
    context_object_name = 'lead'


class LeadListView(LeadMixin, generic.ListView):
    queryset = Lead.objects.all()
    # Later I need to add leads filter functionality to show only leads who belong
    # to a asking organisation and managers attached to it.
    context_object_name = 'leads'
    template_name = 'leads/lead_list.html'


class LeadCreateView(LoginRequiredMixin, generic.CreateView):
    model = Lead
    form_class = LeadCreateUpdateForm
    template_name = 'leads/lead_create.html'
    success_url = reverse_lazy('leads:lead_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class LeadDetailView(LeadMixin, generic.DetailView):
    template_name = 'leads/lead_detail.html'


class LeadUpdateView(LeadMixin, generic.UpdateView):
    model = Lead
    form_class = LeadCreateUpdateForm
    template_name = 'leads/lead_update.html'
    success_url = reverse_lazy('leads:lead_detail')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class LeadDeleteView(LeadMixin, generic.DeleteView):
    template_name = 'leads/lead_delete.html'
    success_url = reverse_lazy('leads:lead_list')
