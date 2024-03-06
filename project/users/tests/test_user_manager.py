from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.translation import gettext_lazy as _
from faker import Faker

from ..factories import UserFactory

fake = Faker(["en_GB", "en_US", "en_IN"])


class TestUserManager(TestCase):
    def test_create_user(self):
        firstname = fake.first_name()
        surname = fake.last_name()
        user = UserFactory(
            email="normal@user.com",
            first_name=firstname,
            last_name=surname,
        )
        self.assertEqual(str(user), f"{firstname} {surname}")
        self.assertEqual(user.email, "normal@user.com")
        self.assertEqual(user.first_name, firstname)
        self.assertEqual(user.last_name, surname)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        try:
            # username is None for the AbstractUser option
            # username does not exist for the AbstractBaseUser option
            self.assertIsNone(user.username)
        except AttributeError:
            pass

        User = get_user_model()
        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(TypeError):
            User.objects.create_user(email="")
        with self.assertRaises(TypeError):
            User.objects.create_user(first_name="")
        with self.assertRaises(TypeError):
            User.objects.create_user(last_name="")
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email="", first_name="", last_name="", password="foo"
            )

        with self.assertRaises(ValueError) as exf:
            User.objects.create_user(
                email=fake.email(),
                first_name="",
                last_name=fake.last_name(),
                password="foo",
            )
        firstname_exception = exf.exception
        self.assertEqual(str(firstname_exception), _("The First name must be set"))

        with self.assertRaises(ValueError) as exl:
            User.objects.create_user(
                email=fake.email(),
                first_name=fake.last_name(),
                last_name="",
                password="foo",
            )
        lastname_exception = exl.exception
        self.assertEqual(str(lastname_exception), _("The Last name must be set"))

    def test_create_superuser(self):
        firstname = fake.first_name()
        surname = fake.last_name()
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            "super@user.com", firstname, surname, "foo"
        )
        self.assertEqual(admin_user.email, "super@user.com")
        self.assertEqual(admin_user.first_name, firstname)
        self.assertEqual(admin_user.last_name, surname)
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        try:
            # username is None for the AbstractUser option
            # username does not exist for the AbstractBaseUser option
            self.assertIsNone(admin_user.username)
        except AttributeError:
            pass
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="super@user.com",
                first_name=firstname,
                last_name=surname,
                password="foo",
                is_superuser=False,
            )
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="super@user.com",
                first_name=firstname,
                last_name=surname,
                password="foo",
                is_staff=False,
            )
