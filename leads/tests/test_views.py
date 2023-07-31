from django.test import TestCase, RequestFactory
from .. import views
from ..models import Lead, Status
from django.contrib.auth import get_user_model
from organizations.models import Organization, Membership
from django.urls import reverse

User = get_user_model()


class LeadViewsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='vs_dev2023')
        cls.organization = Organization.objects.create(name='vs_org')
        Organization.objects.create(name='SomeOrg')

        Membership.objects.create(user=cls.user, organization=cls.organization, role='owner')
        cls.lead = Lead.objects.create(
            first_name='VS',
            last_name='DEV',
            order='Test my Views',
            price='1000',
            email='test@test.test',
            phone='+70987654321',
            comment='',
            organization=cls.organization.name,
            )
        cls.lead2 = Lead.objects.create(
            first_name='VS2',
            last_name='DEV2',
            order='Test my Views2',
            price='1000',
            email='test@test.test',
            phone='+70987555321',
            comment='',
            organization=cls.organization.name,
            )
        cls.lead3 = Lead.objects.create(
            first_name='VS3',
            last_name='DEV3',
            order='Test my Views3',
            price='1000',
            email='test@test.test',
            phone='+70987654321',
            comment='',
            organization='SomeOrg'
            )

    def setUp(self):
        self.client.force_login(self.user)
        self.factory = RequestFactory()

    def test_form_invalid(self):
        kwargs = {'org_id': self.organization.id}
        url = reverse(f'organizations:leads:lead_create', kwargs=kwargs)
        request = self.factory.post(url, data={
            'first_name': '',
            'last_name': '',
            'order': '',
            'price': 100,
            'email': '',
            'phone': '',
            'comment': '',
            })
        request.user = self.user
        response = views.LeadCreateView.as_view()(request, **kwargs)
        self.assertEqual(response.status_code, 200)
        lead_expected_id = self.lead3.id + 1
        lead = Lead.objects.filter(id=lead_expected_id).first()
        self.assertIsNone(lead)

    def test_form_valid_and_get_success_url(self):
        create_update_views = {
            'create': 'LeadCreateView',
            'update': 'LeadUpdateView',
        }

        for view_type, view_name in create_update_views.items():
            kwargs = {'org_id': self.organization.id}
            if view_type == 'update':
                kwargs['pk'] = Lead.objects.get(first_name='vs_test').id
            url = reverse(f'organizations:leads:lead_{view_type}',
                          kwargs=kwargs)
            request = self.factory.post(url, data={
                'first_name': 'vs_test',
                'last_name': 'test_vs',
                'order': 'Test my form create view',
                'price': 100,
                'email': 'test@test.test',
                'phone': '+79553000794',
                'comment': 'Test comment',
            })
            request.user = self.user
            view = views.__dict__[view_name]
            response = view.as_view()(request, **kwargs)
            self.assertEqual(response.status_code, 302)
            view.kwargs = kwargs
            success_url = view().get_success_url()

            if view_type == 'create':
                expected_url = reverse('organizations:leads:lead_list', kwargs=kwargs)
            else:
                expected_url = reverse('organizations:leads:lead_detail', kwargs=kwargs)

            self.assertEqual(success_url, expected_url)
        
    def test_views(self):
        views_to_test = {
            'create': 'LeadCreateView',
            'list': 'LeadListView',
            'detail': 'LeadDetailView',
            'update': 'LeadUpdateView',
            'delete': 'LeadDeleteView',
        }
        kwargs = {'org_id': self.organization.id}
        i = 0

        for view_type, view_name in views_to_test.items():
            url_name = f'organizations:leads:lead_{view_type}'

            if i > 1:
                kwargs['pk'] = self.lead.id

            url = reverse(url_name, kwargs=kwargs)
            request = self.factory.get(url)
            request.user = self.user
            response = views.__dict__[view_name].as_view()(request, **kwargs)

            self.assertIn('org_id', response.context_data)

            if view_type == 'list':
                self.assertIn('leads', response.context_data)
            i += 1
