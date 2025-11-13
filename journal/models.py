import uuid as uuid_lib
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Template(TimeStampedModel):
    uuid = models.UUIDField(default=uuid_lib.uuid4, editable=False, primary_key=True)
    title = models.CharField(max_length=240)
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    categories = models.ManyToManyField(
        "journal.Category", related_name="templates", blank=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="templates"
    )

    def __str__(self):
        return self.title
    

class Category(TimeStampedModel):
    uuid = models.UUIDField(default=uuid_lib.uuid4, editable=False, primary_key=True)
    name = models.CharField(max_length=120)
    description = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="categories"
    )

    def __str__(self):
        return self.name
    

class JournalEntry(TimeStampedModel):
    uuid = models.UUIDField(default=uuid_lib.uuid4, editable=False, primary_key=True)
    title = models.CharField(max_length=240, null=True, blank=True)
    template = models.ForeignKey(
        "Template", on_delete=models.SET_NULL, null=True, related_name="entries"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="entries"
    )
    quote_of_the_day = models.CharField(max_length=500, null=True, blank=True)
    rate_your_day = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        # Fallback to the template title if the user didn't provide a title
        if self.title:
            return self.title
        return f"Entry from {self.created_at.date()}"
    

class TemplateField(models.Model):
    template = models.ForeignKey(
        Template, on_delete=models.CASCADE, related_name="fields"
    )
    name = models.CharField(max_length=120)
    field_type = models.CharField(
        max_length=50,
        choices=[
            ("text", "Text"),
            ("number", "Number"),
            ("date", "Date"),
            ("boolean", "Boolean"),
        ],
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="template_fields"
    )
    order = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.field_type})"
    

class EntryFieldAnswer(TimeStampedModel):
    uuid = models.UUIDField(default=uuid_lib.uuid4, editable=False, primary_key=True)
    entry = models.ForeignKey(
        "JournalEntry", 
        on_delete=models.CASCADE, 
        related_name="field_answers"
    )
    field = models.ForeignKey(
        "TemplateField", 
        on_delete=models.CASCADE, 
        related_name="answers"
    )
    value = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ("entry", "field")

    def __str__(self):
        return f"Answer for {self.field.name} in {self.entry.title}"
    
