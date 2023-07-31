from django.test import TestCase
from users.models import User
from django.urls import reverse
from organizations.models import Organization, Membership
from ..models import Lead


class LeadsURLTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_org_member = User.objects.create(username='OrgMember')
        cls.user_not_org_member = User.objects.create(username='NotOrgMember')
        cls.organization = Organization.objects.create(name='TestOrg')
        Membership.objects.create(
            user=cls.user_org_member,
            organization=cls.organization,
            role='manager',
            )
        cls.lead = Lead.objects.create(
            first_name='Vit',
            last_name='Step',
            order='Test my App',
            price='1000',
            email='test@test.test',
            phone='+70987654321',
            comment='',
            manager=cls.user_org_member,
            organization=cls.organization.name,
            )

    def setUp(self):
        self.client.force_login(self.user_org_member)

    def test_lead_list_url_returns_200(self):
        url = reverse('organizations:leads:lead_list', kwargs={'org_id': self.organization.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_lead_list_uses_correct_template(self):
        url = reverse('organizations:leads:lead_list', kwargs={'org_id': self.organization.id})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'leads/lead_list.html')

    def test_lead_list_url_returns_403_to_non_organization_members(self):
        self.client.force_login(self.user_not_org_member)
        url = reverse('organizations:leads:lead_list', kwargs={'org_id': self.organization.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_lead_create_url_returns_200(self):
        url = reverse('organizations:leads:lead_create', kwargs={'org_id': self.organization.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_lead_create_uses_correct_template(self):
        url = reverse('organizations:leads:lead_create', kwargs={'org_id': self.organization.id})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'leads/lead_create.html')

    def test_lead_detail_url_returns_200(self):
        self.client.force_login(self.user_org_member)
        url = reverse('organizations:leads:lead_detail', kwargs={
            'org_id': self.organization.id,
            'pk': self.lead.pk
            })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_lead_detail_uses_correct_template(self):
        url = reverse('organizations:leads:lead_detail', kwargs={
            'org_id': self.organization.id,
            'pk': self.lead.pk,
            })
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'leads/lead_detail.html')

    def test_lead_update_url_return_200(self):
        self.client.force_login(self.user_org_member)
        url = reverse('organizations:leads:lead_update', kwargs={
            'org_id': self.organization.id,
            'pk': self.lead.pk
            })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_lead_update_uses_correct_template(self):
        url = reverse('organizations:leads:lead_update', kwargs={
            'org_id': self.organization.id,
            'pk': self.lead.pk,
            })
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'leads/lead_update.html')

    def test_lead_delete_url_return_200(self):
        self.client.force_login(self.user_org_member)
        url = reverse('organizations:leads:lead_delete', kwargs={
            'org_id': self.organization.id,
            'pk': self.lead.pk
            })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_lead_delete_uses_correct_template(self):
        url = reverse('organizations:leads:lead_delete', kwargs={
            'org_id': self.organization.id,
            'pk': self.lead.pk,
            })
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'leads/lead_delete.html')
