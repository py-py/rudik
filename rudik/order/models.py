from django.db import models
from model_utils.models import TimeStampedModel


class Order(TimeStampedModel, models.Model):
    first_name = models.CharField(max_length=256)
    second_name = models.CharField(max_length=256)
    phone = models.CharField(max_length=256)
