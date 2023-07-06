from typing import Any, Dict
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.utils import timezone
from datetime import timedelta
from leads.models import Lead, Status
from django.db.models import Sum
from organizations.models import Organization, Membership
from users.models import User

now = timezone.now()
yesterday = now - timedelta(days=1)
year = now.year
month = now.month


status_groups = Status.GROUP_CHOICES


class GeneralReport(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/general_report.html'

    def get_context_data(self, **kwargs):
        leads_created_today = Lead.objects.filter(date_created__gt=yesterday)
        leads_created_today_count = leads_created_today.count()
        leads_created_today_price = leads_created_today.aggregate(Sum('price'))['price__sum']
        leads_created_this_month = Lead.objects.filter(date_created__year=year,
                                                       date_created__month=month)
        statuses = Status.objects.filter(group='done')
        leads_created_this_month_price_done = 0

        for status in statuses:
            leads = leads_created_this_month.filter(status=status)
            leads_created_this_month_price_done += leads.aggregate(Sum('price'))['price__sum']

        leads_created_this_month_count = leads_created_this_month.count()
        leads_created_this_month_price = leads_created_this_month.aggregate(
            Sum('price'))['price__sum']
        context = super().get_context_data(**kwargs)
        context['leads_created_today_count'] = leads_created_today_count
        context['leads_created_today_price'] = leads_created_today_price
        context['leads_created_this_month_count'] = leads_created_this_month_count
        context['leads_created_this_month_price'] = leads_created_this_month_price
        context['leads_created_this_month_price_done'] = leads_created_this_month_price_done
        context['org_id'] = self.kwargs['org_id']

        status_group_names = [group_name[0] for group_name in status_groups]
        leads_by_statuses = dict()

        for i, status_group in enumerate(status_group_names):
            leads = []
            statuses = Status.objects.filter(group=status_group)
            for status in statuses:
                leads.append(Lead.objects.filter(status=status))
            # Assign statuses to status_group public name
            # TO FIX: I have to check what is gonna happen if there is >1 statuses in a group
            leads_by_statuses[f'{status_groups[i][1]}'] = leads

        context['status_group_names'] = status_group_names
        context['leads_by_statuses'] = leads_by_statuses

        return context


class ManagerReport(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/manager_report.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        org_id = self.kwargs['org_id']
        context['org_id'] = org_id
        organization = Organization.objects.get(id=org_id)
        memberships = Membership.objects.filter(organization=organization)
        user_ids = memberships.values_list('user', flat=True)
        managers = User.objects.filter(id__in=user_ids)
        context['managers'] = managers
        leads_by_manager = dict()
        excluded_statuses_group = status_groups[4][0]
        excluded_statuses = Status.objects.filter(group=excluded_statuses_group)
        done_statuses_group = status_groups[3][0]
        done_statuses = Status.objects.filter(group=done_statuses_group)
        for manager in managers:
            # TO FIX: We also need to filter leads by current organization
            # leads = Lead.objects.filter(organization=org_id, manager=manager)
            leads = Lead.objects.filter(manager=manager)
            leads_by_manager[f'{manager.id}_leads_count'] = leads.count()
            # TO FIX: I also need to exclude leads assigned to all statuses in status group
            leads_by_manager[f'{manager.id}_leads_approved'] = leads.exclude(
                status__in=excluded_statuses).count()
            leads_by_manager[f'{manager.id}_leads_price'] = leads.aggregate(
                Sum('price'))['price__sum']
            leads_by_manager[f'{manager.id}_leads_done_price'] = leads.filter(
                status__in=done_statuses).aggregate(Sum('price'))['price__sum']
        context['leads_by_manager'] = leads_by_manager
        return context


class PeriodReport(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/period_report.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # TO FIX: code should be rewritten in order to be more dynamic and flexible
        # User should be able to chose date range and point size like a day or a month etc...
        last_30_days = now - timedelta(days=30)
        leads = Lead.objects.filter(date_created__gte=last_30_days)
        leads_by_date = dict()
        for i in range(30):
            day = now - timedelta(days=i)
            date_leads = leads.filter(date_created=day)
            date_leads_data = {
                'count': date_leads.count(),
                'price': date_leads.aggregate(Sum('price'))['price__sum']
                }
            leads_by_date[str(day).split()[0]] = date_leads_data
        context['leads_by_date'] = leads_by_date
        return context
