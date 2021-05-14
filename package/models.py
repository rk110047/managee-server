from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.core.serializers.json import DjangoJSONEncoder
from utils.models import BaseAbstractModel
from utils.managers import CustomQuerySet, ChannelsQuery
# from authentication.models import User
from liveTv.models import Channels


class Package(BaseAbstractModel):
    """This class defines the Package model"""

    name = models.CharField(max_length=255)
    channel = models.ManyToManyField(Channels)
    backgroundImage_url = models.URLField(max_length=255, blank=True, null=True)
    thumbnailImage_url = models.URLField(max_length=255, blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)
    validity = models.DurationField(blank=True, null=True)
    discount = models.IntegerField(blank=True, null=True)
    is_default = models.BooleanField(default=False)
    objects = models.Manager()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Saves all the changes of the Archive model"""
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Packages"
        app_label = "package"
