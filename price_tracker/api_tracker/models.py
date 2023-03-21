from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model


class NotifyType(models.Model):
    type = models.CharField(max_length=32, unique=True)
    text = models.CharField(max_length=64, null=True, blank=True)

    class Meta:
        ordering = ['type']
        verbose_name = 'notify_type'
        verbose_name_plural = 'notify_types'

    def __str__(self):
        return self.type


class NotifyCase(models.Model):
    case = models.CharField(max_length=8, null=False, unique=True)
    text = models.CharField(max_length=64, null=True, blank=True)

    class Meta:
        ordering = ['case']
        verbose_name = 'notify_case'
        verbose_name_plural = 'notify_cases'

    def __str__(self):
        return self.case


class TrackersUserSettings(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='trackers_settings',
        on_delete=models.CASCADE
    )

    notify_types = models.ManyToManyField(
        NotifyType,
        blank=True,
        # choices=tuple(NotifyType.objects.values_list('id', 'type').all()),
    )

    notify_case = models.ForeignKey(
        NotifyCase,
        null=True,
        blank=True,
        # choices=tuple(NotifyCase.objects.values_list('id', 'case').all()),
        on_delete=models.SET_NULL,
    )

    notify_task_ids = models.TextField(
        null=True, blank=True, default='')

    def __str__(self):
        return self.user.username

    @receiver(post_save, sender=get_user_model())
    def create_trackers_user_settings(sender, instance, created, **kwargs):
        if created:
            notify_case, notify_types = None, None
            if NotifyCase.objects.exists():
                notify_case, _ = NotifyCase.objects.get_or_create(case='<>')
            if NotifyType.objects.exists():
                notify_types, _ = NotifyType.objects.get_or_create(type='push')
            
            TrackersUserSettings.objects.create(
                user=instance,
                notify_case=notify_case,
            ).notify_types.set([notify_types])
        # instance.trackers_settings.save()
    
    class Meta:
        verbose_name = 'Trackers User Settings'
        verbose_name_plural = 'Trackers Users Settings'


class Tracker(models.Model):

    url = models.CharField(max_length=255, unique=False)
    host = models.CharField(
        max_length=255, unique=False,
        null=True, blank=True)

    title = models.CharField(max_length=128, null=True, blank=True)

    price = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True)
    date_time = models.DateTimeField(null=True, blank=True)

    img_url = models.CharField(max_length=254, null=True, blank=True)
    currency = models.CharField(max_length=8,   null=True, blank=True)

    in_stock = models.BooleanField(null=True, blank=True)
    archive = models.BooleanField(null=True, blank=True, default=False)

    users = models.ManyToManyField(
        to=get_user_model(),
        through='UserTracker',
        related_name='trackers',
        blank=True,
    )

    def __str__(self) -> str:
        return self.url[0:64]

    def as_dict(self, prices_len: int = 30) -> dict:
        data = {
            'errors': {},
            'is_user': False,
            'info': {
                'pk':    self.pk,
                'url':   self.url,
                'img_url': self.img_url,
                'host':  self.host,
                'price': self.price,
                'currency': self.currency,
                'date_time': self.date_time,
                'title': self.title,
                'in_stock': self.in_stock,
                'archive': self.archive
            }
        }

        if prices_len != 0:
            data['prices'] = list(
                self.prices.order_by('-id')
                .values('price', 'date_time')[:prices_len]
            )
        return data

    def is_simple_editable_field(self, field):
        from django.db.models.fields.reverse_related import ForeignObjectRel
        return (
                field.editable
                and not field.primary_key
                and not isinstance(
                    field,
                    (ForeignObjectRel, models.ManyToManyField)
                )
        )

    def update_from_dict(self, dict: dict, save: bool = True):
        allowed_field_names = {
            f.name for f in self._meta.get_fields()
            if self.is_simple_editable_field(f)
        }

        for attr, val in dict.items():
            if attr in allowed_field_names:
                if attr == 'price' or val:
                    setattr(self, attr, val)

        if save:
            self.save()

        return self

    class Meta:
        verbose_name = 'tracker'
        verbose_name_plural = 'trackers'


class UserTracker(models.Model):
    user = models.ForeignKey(
        to=get_user_model(),
        related_name='user_tracker',
        on_delete=models.CASCADE
    )
    tracker = models.ForeignKey(
        to=Tracker,
        related_name='user_tracker',
        on_delete=models.CASCADE
    )
    notify = models.BooleanField(
        null=True, blank=True, default=True
    )
    need_notify_types = models.ManyToManyField(
        to=NotifyType, blank=True
    )
    need_notify_case = models.CharField(
        max_length=64,
        null=True, blank=True, default=''
    )

    def __str__(self) -> str:
        return f'{self.user.username} {self.tracker}'

    class Meta:
        verbose_name = 'user_tracker'
        verbose_name_plural = 'users_trackers'


class Price(models.Model):
    price = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True)
    date_time = models.DateTimeField(editable=False, auto_now_add=True)

    tracker = models.ForeignKey(
        Tracker, on_delete=models.CASCADE,
        related_name="prices",
        null=True, blank=True
    )

    def __str__(self) -> str:
        return f'{self.date_time}  {self.price}'
