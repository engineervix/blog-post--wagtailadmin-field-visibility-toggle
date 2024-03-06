from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ToysConfig(AppConfig):
    name = "project.toys"
    label = "toys"
    verbose_name = _("Toys")
