import uuid as uuid_lib
import json
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
    uuid = models.UUIDField(default=uuid_lib.uuid4, editable=False)
    title = models.CharField(max_length=240)
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="templates"
    )

    def __str__(self):
        return self.title
    
