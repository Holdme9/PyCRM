from django.forms import ValidationError
from django.test import TestCase
from django.contrib.auth import get_user_model

from datetime import date

from ..models import Lead, Status

User = get_user_model()


class LeadModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        status = Status.objects.create(name='TestStatus')
        user = User.objects.create(username='TestUser')
        Lead.objects.create(
            first_name='TestFirstname',
            last_name='TestLastname',
            order='Test Order',
            price=100,
            email='TestEmail@test.test',
            phone='+7(999)888-77-66',
            comment='Test comment',
            manager=user,
            status=status,
            organization='Test Organization',
        )

    def test_email_field_validation(self):
        lead = Lead.objects.get(pk=1)
        self.assertEqual(lead.email, 'TestEmail@test.test')
        lead.email = 'invalid_email'
        with self.assertRaises(ValidationError):
            lead.full_clean()

    def test_default_values(self):
        lead = Lead.objects.get(pk=1)
        default = lead._meta.get_field('comment').default
        self.assertIsNone(default)

        default = lead._meta.get_field('manager').default
        self.assertIsNone(default)

    def test_phone_field_validation(self):
        lead = Lead.objects.get(pk=1)
        lead.phone = ''
        with self.assertRaises(ValidationError):
            lead.full_clean()

    def test_values(self):
        lead = Lead.objects.get(pk=1)
        self.assertEqual(lead.first_name, 'TestFirstname')
        self.assertEqual(lead.last_name, 'TestLastname')
        self.assertEqual(lead.order, 'Test Order')
        self.assertEqual(lead.price, 100)
        self.assertEqual(lead.email, 'TestEmail@test.test')
        self.assertEqual(lead.phone, '+7(999)888-77-66')
        self.assertEqual(lead.comment, 'Test comment')
        self.assertEqual(lead.organization, 'Test Organization')

    def test_integer_fields(self):
        lead = Lead.objects.get(pk=1)
        self.assertIsInstance(lead.price, int)

    def test_related_fields_value_types(self):
        lead = Lead.objects.get(pk=1)
        self.assertIsInstance(lead.manager, User)
        self.assertIsInstance(lead.status, Status)

    def test_date_fields_auto_add(self):
        lead = Lead.objects.get(pk=1)
        self.assertIsNotNone(lead.date_created)
        self.assertIsNotNone(lead.date_updated)

    def test_date_fields_type(self):
        lead = Lead.objects.get(pk=1)
        self.assertIsInstance(lead.date_created, date)
        self.assertIsInstance(lead.date_updated, date)

    def test_null_fields(self):
        lead = Lead.objects.get(pk=1)
        is_null = lead._meta.get_field('manager').null
        self.assertTrue(is_null)

        is_null = lead._meta.get_field('status').null
        self.assertTrue(is_null)


class StatusModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        status = Status.objects.create(name='TestStatus', group=Status.GROUP_CHOICES[2][1])

    def test_values(self):
        status = Status.objects.get(pk=2)
        self.assertEqual(status.name, 'TestStatus')
        self.assertEqual(status.group, Status.GROUP_CHOICES[2][1])
