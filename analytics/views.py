from typing import Any, Dict
from datetime import timedelta

from django.views.generic import TemplateView
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator

from leads.models import Lead, Status
from organizations.models import Organization
from leads.views import VerifyMembershipMixin
from .forms import DateRangeForm

User = get_user_model()

now = timezone.now()
yesterday = now - timedelta(days=1)
year = now.year
month = now.month

status_groups = Status.GROUP_CHOICES


class GeneralReport(VerifyMembershipMixin, TemplateView):
    """A view for displaying general data."""

    template_name = 'analytics/general_report.html'

    def get_context_data(self, **kwargs) -> dict:
        """Provides data for the context dictionary."""

        context = super().get_context_data(**kwargs)
        org_id = self.kwargs['org_id']
        organization = Organization.objects.get(id=org_id)
        context['org_id'] = org_id
        context['organization'] = organization
        leads_created_today = Lead.objects.filter(
            organization=organization,
            date_created__gt=yesterday,
            )
        leads_created_today_count = len(leads_created_today)
        leads_created_this_month = Lead.objects.filter(
            organization=organization,
            date_created__year=year,
            date_created__month=month
            )
        leads_created_this_month_count = len(leads_created_this_month)
        leads_created_this_month_price = sum(lead.price for lead in leads_created_this_month)
        done_statuses = Status.objects.filter(group=status_groups[3][0])
        leads_created_this_month_price_done = sum(
            lead.price for lead in leads_created_this_month.filter(status__in=done_statuses))
        context['leads_created_today_count'] = leads_created_today_count
        context['leads_created_this_month_count'] = leads_created_this_month_count
        context['leads_created_this_month_price'] = leads_created_this_month_price
        context['leads_created_this_month_price_done'] = leads_created_this_month_price_done

        # Status group slices 0 and 1 are related to private and public status group names
        status_group_names = [status_group_name[0] for status_group_name in status_groups[:4]]
        leads_by_statuses = dict()

        for i, status_group_name in enumerate(status_group_names):
            statuses = Status.objects.filter(group=status_group_name)
            leads = Lead.objects.filter(status__in=statuses)
            leads_by_statuses[f'{status_groups[i][1]}'] = leads

        context['leads_by_statuses'] = leads_by_statuses
        return context


class ManagerReport(VerifyMembershipMixin, TemplateView):
    """A view for displaying data by manager."""

    template_name = 'analytics/manager_report.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Provides data to the context dictionary."""

        context = super().get_context_data(**kwargs)
        org_id = self.kwargs['org_id']
        organization = Organization.objects.get(id=org_id)
        memberships = organization.membership_set.all()
        managers = User.objects.filter(membership__in=memberships)
        reject_status_group = status_groups[4][0]
        reject_statuses = Status.objects.filter(group=reject_status_group)
        done_status_group = status_groups[3][0]
        done_statuses = Status.objects.filter(group=done_status_group)
        leads = Lead.objects.filter(organization=organization)
        managers_stats = dict()

        for manager in managers:
            manager_name = f'{manager.first_name} {manager.last_name} ({manager.email})'
            manager_leads = leads.filter(manager=manager)
            manager_sales_sum = sum(
                lead.price for lead in manager_leads.filter(status__in=done_statuses)
                )
            manager_leads_count = len(manager_leads)
            manager_leads_rejected_count = len(manager_leads.filter(status__in=reject_statuses))
            manager_leads_rejected_percentage = round(
                manager_leads_rejected_count / manager_leads_count,
                2
                ) * 100 if manager_leads_count else 0

            managers_stats[f'{manager}'] = {
                'name': manager_name,
                'sales_sum': manager_sales_sum,
                'leads_count': manager_leads_count,
                'leads_rejected_count': manager_leads_rejected_percentage
            }

        context['org_id'] = org_id
        context['organization'] = organization
        context['managers_stats'] = managers_stats
        return context


class PeriodReport(VerifyMembershipMixin, TemplateView):
    """A view for displaying data by period."""
    template_name = 'analytics/period_report.html'

    def parse_date_parameters(self) -> tuple:
        """
        Parses the start_date and end_date parameters from the request if present,
        sets them as the last 30 days otherwise.
        """

        try:
            start_date = parse_date(self.request.GET.get('start_date'))
            end_date = parse_date(self.request.GET.get('end_date'))
        except TypeError:
            end_date = now.date()
            start_date = end_date - timedelta(days=30)

        return start_date, end_date

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Provides data to the context dictionary."""

        context = super().get_context_data(**kwargs)
        org_id = self.kwargs['org_id']
        organization = Organization.objects.get(id=org_id)
        context['org_id'] = org_id
        context['organization'] = organization
        start_date, end_date = self.parse_date_parameters()
        leads = Lead.objects.filter(date_created__range=(start_date, end_date))
        leads_by_date = dict()

        for i in range((end_date - start_date).days + 1):
            day = end_date - timedelta(days=i)
            date_leads = leads.filter(date_created=day)
            date_leads_data = {
                'count': len(date_leads),
                'price': sum(lead.price for lead in date_leads)
                }
            leads_by_date[str(day)] = date_leads_data

        context['leads_by_date'] = leads_by_date
        context['form'] = DateRangeForm

        return context
