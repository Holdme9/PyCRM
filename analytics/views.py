from typing import Any, Dict
from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet

from leads.models import Lead, Status
from organizations.models import Organization, Membership
from leads.views import VerifyMembershipMixin
from .forms import DateRangeForm

User = get_user_model()

now = timezone.now()
yesterday = now - timedelta(days=1)
year = now.year
month = now.month
status_groups = Status.GROUP_CHOICES


class OrganizationMixin:
    """Provides various methods to retrieve data from Organization model."""

    def get_organization_id(self) -> int:
        """Returns the id of Organization model object."""
        return self.kwargs.get('org_id')

    def get_organization(self, org_id: int) -> Organization:
        """Returns the Organization model object if exists, else raises a 404 eror."""
        organization = get_object_or_404(Organization, id=org_id)
        return organization

    def get_organization_memberships(self, organization: Organization) -> QuerySet[Membership]:
        """Returns Membership model objects related to the specific organization."""
        memberships = organization.membership_set.all()
        return memberships

    def get_organization_members(self, memberships: QuerySet[Membership]) -> QuerySet[User]:
        "Returns User model objects, related to the specific organization."
        members = User.objects.filter(membership__in=memberships)
        return members


class StatusMixin:
    """Provides methods to retrieve data from Status model."""

    def get_done_statuses(self) -> QuerySet[Status]:
        """Returns queryset of Status model objects related to 'Done' status group."""
        # 1st slice corresponds to status group
        # and 2nd slice to group names where 0 is private name and 1 is public name.
        done_statuses = Status.objects.filter(group=status_groups[3][0])
        return done_statuses

    def get_reject_statuses(self) -> QuerySet[Status]:
        """Returns queryset of Status model objects related to 'Reject' status group."""
        reject_status_group = status_groups[4][0]
        reject_statuses = Status.objects.filter(group=reject_status_group)
        return reject_statuses

    def get_status_group_names(self) -> list[str]:
        """
        Returns a List of private status group names for Status Model objects
        except 'Rejected' status group.
        """
        # Slice 0 corresponds to private status group name and 1 for public one.
        status_group_names = [status_group_name[0] for status_group_name in status_groups[:4]]
        return status_group_names


class LeadMixin:
    """Provides various methods to retrieve data from Status model."""

    def get_leads_created_today(self, organization: Organization) -> QuerySet[Lead]:
        """
        Return queryset of Lead model objects which were created today
        and belong to specific organization.
        """
        leads_created_today = Lead.objects.filter(
            organization=organization,
            date_created__gt=yesterday
        )
        return leads_created_today

    def get_leads_created_this_month(self, organization: Organization) -> QuerySet[Lead]:
        """
        Returns queryset of Lead model objects which were created in this month
        and belong to specific organization.
        """
        leads_created_this_month = Lead.objects.filter(
            organization=organization,
            date_created__year=year,
            date_created__month=month
        )
        return leads_created_this_month

    def get_all_leads(self, organization: Organization) -> QuerySet[Lead]:
        """Returns queryset of Lead model objects that belong to specific organization."""
        leads = Lead.objects.filter(organization=organization)
        return leads

    def get_leads_price(self, leads: QuerySet[Lead]) -> int:
        """Returns the sum of prices of Lead model objects in given queryset."""
        leads_price = sum(lead.price for lead in leads)
        return leads_price

    def get_leads_by_statuses(self, status_group_names: list[str]) -> QuerySet[Lead]:
        """
        Returns dict with Public status group names as keys and queryset
        of Lead model objects that belongs to specific organization and
        specific status group as values.
        """
        leads_by_statuses = dict()

        for i, status_group_name in enumerate(status_group_names):
            statuses = Status.objects.filter(group=status_group_name)
            leads = Lead.objects.filter(status__in=statuses)
            leads_by_statuses[f'{status_groups[i][1]}'] = leads

        return leads_by_statuses

    def get_manager_stats(self, managers, done_statuses, reject_statuses, leads) -> dict[str: any]:
        """
        Returns dictionary with User model objects string representations as keys
        and data related to manager performance as values.
        """
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

        return managers_stats


class GeneralReport(
    OrganizationMixin,
    StatusMixin,
    LeadMixin,
    VerifyMembershipMixin,
    TemplateView,
):
    """A view for displaying general data."""
    template_name = 'analytics/general_report.html'

    def get_context_data(self, **kwargs) -> dict[str: any]:
        """Adds data to the context dictionary."""
        context = super().get_context_data(**kwargs)
        org_id = self.get_organization_id()
        organization = self.get_organization(org_id)
        context['org_id'] = org_id
        context['organization'] = organization

        leads_created_today = self.get_leads_created_today(organization)
        leads_created_today_count = len(leads_created_today)
        context['leads_created_today_count'] = leads_created_today_count

        leads_created_this_month = self.get_leads_created_this_month(organization)
        leads_created_this_month_count = len(leads_created_this_month)
        context['leads_created_this_month_count'] = leads_created_this_month_count
        leads_created_this_month_price = self.get_leads_price(leads_created_this_month)
        context['leads_created_this_month_price'] = leads_created_this_month_price

        done_statuses = self.get_done_statuses()
        leads_created_this_month_and_done = leads_created_this_month.filter(
            status__in=done_statuses
            )
        leads_created_this_month_and_done_price = self.get_leads_price(
            leads_created_this_month_and_done
            )
        context['leads_created_this_month_and_done_price'] = leads_created_this_month_and_done_price

        status_group_names = self.get_status_group_names()
        leads_by_statuses = self.get_leads_by_statuses(status_group_names)
        context['leads_by_statuses'] = leads_by_statuses
        return context


class ManagerReport(
    OrganizationMixin,
    StatusMixin,
    LeadMixin,
    VerifyMembershipMixin,
    TemplateView
):
    """A view for displaying data by manager."""
    template_name = 'analytics/manager_report.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Adds data to the context dictionary."""

        context = super().get_context_data(**kwargs)
        org_id = self.get_organization_id()
        organization = self.get_organization(org_id=org_id)
        context['org_id'] = org_id
        context['organization'] = organization

        memberships = self.get_organization_memberships(organization)
        managers = self.get_organization_members(memberships)

        done_statuses = self.get_done_statuses()
        reject_statuses = self.get_reject_statuses()
        leads = self.get_all_leads(organization)
        managers_stats = self.get_manager_stats(
            managers,
            done_statuses,
            reject_statuses,
            leads
        )
        context['managers_stats'] = managers_stats

        return context


class PeriodReport(OrganizationMixin, VerifyMembershipMixin, TemplateView):
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

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Provides data to the context dictionary."""
        context = super().get_context_data(**kwargs)
        org_id = self.get_organization_id()
        organization = self.get_organization(org_id)
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
