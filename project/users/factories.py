import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from faker import Faker

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating Django User objects"""

    email = factory.Faker("email")
    password = factory.LazyFunction(lambda: make_password("password"))
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    class Meta:
        model = get_user_model()
