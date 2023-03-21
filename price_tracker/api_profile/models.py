from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    birth_date = models.DateField(
        null=False, blank=True,
        default=timezone.datetime(1970, 1, 1).date())
