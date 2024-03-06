from django.test import TestCase
from faker import Faker

from ..forms import UserCreationForm

fake = Faker(["en_GB", "en_US", "en_IN"])


class TestUserCreationForms(TestCase):
    def test_valid_user_creation_form(self):
        password = fake.password()
        email_address = fake.email()
        form = UserCreationForm(
            {
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "email": email_address,
                "password1": password,
                "password2": password,
            }
        )

        self.assertTrue(form.is_valid())

    def test_invalid_user_creation_form(self):
        password = fake.password()
        email_address = fake.email()
        form = UserCreationForm(
            {
                "first_name": fake.first_name(),
                "email": email_address,
                "password1": password,
                "password2": password,
            }
        )

        self.assertFalse(form.is_valid())
