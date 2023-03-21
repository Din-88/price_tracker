import copy
import re
from rest_framework import serializers
# from rest_framework.validators import RegexValidator
from django.core.validators import RegexValidator
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount

from .models import (
    NotifyType,
    NotifyCase,
    Tracker,
    Price,
    TrackersUserSettings,
    UserTracker,
)
from django.db.models import Model

User = get_user_model()


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = ['date_time', 'price']


class TrackerSerializer(serializers.ModelSerializer):
    prices = PriceSerializer(many=True, required=False)

    class Meta:
        model = Tracker
        # fields = ['last_datetime', 'prices']
        # fields = ['__all__']
        # exclude = ['users']
        fields = [
            'pk',
            'prices',
            'url',
            'host',
            'title',
            'price',
            'date_time',
            'img_url',
            'currency',
            'in_stock',
            'archive',
        ]
        depth = 1

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # representation['prices'] = representation['prices']#[-100:]
        rep_copy = copy.deepcopy(representation)
        representation = {}

        request = self.context.get('request')
        if request and \
            isinstance(request.user, Model) and \
                instance.users.contains(request.user):
            rep_copy['is_user'] = True
            ut = instance.user_tracker.get(user=request.user)
            rep_copy['notify'] = ut.notify

        representation['info'] = rep_copy

        return representation


class TrackerUpdateSerializer(serializers.ModelSerializer):
    prices = PriceSerializer(many=False, read_only=True)
 
    class Meta:
        model = Tracker
        fields = '__all__'
        depth = 1

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        price = Price.objects.create(price=validated_data.get('price'))
        instance.prices.add(price)
        return instance
    

class NewTrackerSerializer(serializers.Serializer):
    url = serializers.URLField(read_only=True)

    def update(self, instance, validated_data):
        pass
        return instance


class PasswordValidator(object):
    message = 'Invalid current password.'

    def __call__(self, value):
        passwords = {p: value.get(p) for p in ['curr_pass', 'new_pass1', 'new_pass2']}

        if any(passwords.values()):
            if not all(passwords.values()):
                errors = {k: 'Все 3 поля паролей обязательны к заполнению.' for k, v in passwords.items() if not v}
                raise serializers.ValidationError(errors)

            request = self.context.get('request')
            is_check = request.user.check_password(raw_password=passwords['curr_pass'])
            if not is_check:
                raise serializers.ValidationError(
                    {'curr_pass': ['Неверный текущий пароль']})

            if passwords['new_pass1'] != passwords['new_pass2']:
                raise serializers.ValidationError(
                    {'new_pass2': ['Новые пароли не совпадают.']})


class TrackerNotifySerializer(serializers.Serializer):
    notify = serializers.BooleanField()

    def update(self, instance, validated_data):
        instance.notify = validated_data.get('notify', instance.notify)
        instance.save()
        return instance


class NotifyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotifyType
        fields = ['id', 'type']


class NotifyCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotifyCase
        fields = ['id', 'case']


class NotifyTypeCaseSerializer(serializers.Serializer):
    notify_types = NotifyTypeSerializer(instance=NotifyType.objects.all())
    notify_cases = NotifyCaseSerializer(instance=NotifyCase.objects.all())


class TrackersUserSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrackersUserSettings
        fields = ['notify_types', 'notify_case']

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        if ret['notify_types']:
            ret['notify_types'] = NotifyTypeSerializer(instance=NotifyType.objects.filter(pk__in=ret['notify_types']), many=True).data
        if ret['notify_case']:
            ret['notify_case']  = NotifyCaseSerializer(instance=NotifyCase.objects.get(pk=ret['notify_case']), many=False).data
        return ret
