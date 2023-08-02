from django.test import TestCase

from ..forms import LeadCreateUpdateForm


class LeadCreateUpdateFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.form_data = {
            'first_name': 'Oswald',
            'last_name': 'Tester',
            'order': 'Test my form',
            'price': 100,
            'email': 'test@test.test',
            'phone': '+79223000794',
            'comment': 'Test comment',
        }

    def assert_form_invalid(self, invalid_fields):
        form_data = self.form_data.copy()
        form_data.update(invalid_fields)
        form = LeadCreateUpdateForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_valid_form_data(self):
        form = LeadCreateUpdateForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_empty_first__name(self):
        self.assert_form_invalid({'first_name': ''})

    def test_empty_last_name(self):
        self.assert_form_invalid({'last_name': ''})

    def test_empty_order(self):
        self.assert_form_invalid({'order': ''})

    def test_empty_phone(self):
        self.assert_form_invalid({'phone': ''})
