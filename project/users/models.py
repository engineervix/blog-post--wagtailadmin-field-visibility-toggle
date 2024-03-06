from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    """Default user for mysite"""

    username = None
    email = models.EmailField(_("email address"), unique=True)

    first_name = models.CharField(_("first name"), max_length=255)
    last_name = models.CharField(_("last name"), max_length=255)

    objects = UserManager()

    USERNAME_FIELD = "email"
    # the email field and password will be required,
    # so they don’t need to go into the REQUIRED FIELDS list
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
    ]

    def __str__(self):
        return self.get_full_name()
