from typing import Any, Dict
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from .models import Lead
from .forms import LeadCreateUpdateForm


class LeadMixin(LoginRequiredMixin):
    queryset = Lead.objects.all()
    context_object_name = 'lead'


class LeadListView(LeadMixin, generic.ListView):
    # Later I need to add leads filter functionality to show only leads who belong
    # to a asking organisation and managers attached to it.
    template_name = 'leads/lead_list.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        leads = Lead.objects.all()
        context['leads'] = leads
        context['org_id'] = self.kwargs['org_id']
        return context


class LeadCreateView(LoginRequiredMixin, generic.CreateView):
    model = Lead
    form_class = LeadCreateUpdateForm
    template_name = 'leads/lead_create.html'

    def get_success_url(self) -> str:
        org_id = self.kwargs['org_id']
        return reverse_lazy('organizations:leads:lead_list', kwargs={'org_id': org_id})

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['org_id'] = self.kwargs['org_id']
        return context

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class LeadDetailView(LeadMixin, generic.DetailView):
    template_name = 'leads/lead_detail.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['org_id'] = self.kwargs['org_id']
        return context


class LeadUpdateView(LeadMixin, generic.UpdateView):
    model = Lead
    form_class = LeadCreateUpdateForm
    template_name = 'leads/lead_update.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['org_id'] = self.kwargs['org_id']
        return context

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        org_id = self.kwargs['org_id']
        pk = self.kwargs['pk']
        return reverse_lazy('organizations:leads:lead_detail',
                            kwargs={'org_id': org_id, 'pk': pk})


class LeadDeleteView(LeadMixin, generic.DeleteView):
    template_name = 'leads/lead_delete.html'

    def get_success_url(self) -> str:
        org_id = self.kwargs['org_id']
        return reverse_lazy('organizations:leads:lead_list', kwargs={'org_id': org_id})

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['org_id'] = self.kwargs['org_id']
        return context
