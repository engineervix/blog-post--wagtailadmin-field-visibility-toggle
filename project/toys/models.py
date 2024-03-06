from collections import defaultdict

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.images import get_image_model_string
from wagtail.models import Orderable, Page
from wagtail.search import index

from project.users.models import User


class ToyCampaign(Orderable):
    """
    NOTE: Any changes to the field names here will need to be reflected in
    `project/static/js/page-editor.js`, which consists of custom
    logic to show the `end_date` field's container when `end_date_is_known` is `True`.
    """

    page = ParentalKey("ToyPage", related_name="campaigns")

    title = models.CharField(max_length=255)

    start_date = models.DateTimeField()
    end_date_is_known = models.BooleanField(default=False)
    end_date = models.DateTimeField(blank=True, null=True)

    panels = [
        FieldPanel("title"),
        MultiFieldPanel(
            [
                FieldPanel("start_date"),
                FieldPanel("end_date_is_known"),
                FieldPanel("end_date"),
            ],
            heading="Dates",
        ),
    ]

    def clean(self):
        errors = defaultdict(list)
        super().clean()

        end_date = self.end_date

        if self.end_date_is_known and not self.end_date:
            errors["end_date"].append(
                _("Please specify the end date, since it is known!")
            )

        if end_date and end_date <= self.start_date:
            errors["end_date"].append(_("End date must be after start date"))

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return "Toy Campaign ‘{}’ on Page “{}”".format(self.title, self.page.title)


class ToyImage(Orderable):
    page = ParentalKey("ToyPage", related_name="images")
    image = models.ForeignKey(
        get_image_model_string(),
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="+",
    )

    panels = [
        FieldPanel("image"),
    ]


class ToyPage(Page):
    description = RichTextField(features=["bold", "italic", "link"])
    designer = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="toys"
    )

    # -------------------------- contact email address --------------------------
    # NOTE: Any changes to the two field names here will need to be reflected in
    # `project/static/js/page-editor.js`, which consists of custom logic to hide
    # the `contact_email` field's container when `use_designer_email` is True.
    use_designer_email = models.BooleanField(
        default=False,
        verbose_name="Use designer's email",
        help_text="Use the designer's email address as the contact email",
    )
    contact_email = models.EmailField(blank=True)
    # ---------------------------------------------------------------------------

    content_panels = Page.content_panels + [
        FieldPanel("description"),
        MultiFieldPanel(
            [
                FieldPanel("designer"),
                FieldPanel("use_designer_email"),
                FieldPanel("contact_email"),
            ],
            heading="Designer",
        ),
        InlinePanel("images", heading="Images", label="Image"),
        InlinePanel("campaigns", heading="Campaigns", label="Campaign"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("description"),
        index.FilterField("designer"),
        index.FilterField("use_designer_email"),
    ]

    @cached_property
    def email(self):
        if (designer := self.designer) and self.use_designer_email:
            return designer.email
        return self.contact_email

    @cached_property
    def visuals(self):
        return [item.image for item in self.images.all()]
