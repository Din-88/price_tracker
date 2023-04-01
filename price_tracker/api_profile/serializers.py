import re
from rest_framework import serializers
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model

from api_tracker.serializers import TrackersUserSettingsSerializer


User = get_user_model()


class PasswordValidator(object):
    message = 'Invalid current password.'

    def __call__(self, value):
        passwords = {p: value.get(p) for p
                     in ['curr_pass', 'new_pass1', 'new_pass2']}

        if any(passwords.values()):
            if not all(passwords.values()):
                errors = {k: 'Все 3 поля паролей обязательны к заполнению.'
                          for k, v in passwords.items() if not v}
                raise serializers.ValidationError(errors)

            request = self.context.get('request')
            is_check = request.user.check_password(
                raw_password=passwords['curr_pass'])
            if not is_check:
                raise serializers.ValidationError(
                    {'curr_pass': ['Неверный текущий пароль']})

            if passwords['new_pass1'] != passwords['new_pass2']:
                raise serializers.ValidationError(
                    {'new_pass2': ['Новые пароли не совпадают.']})


class UserSerializer(serializers.ModelSerializer):
    trackers_settings = TrackersUserSettingsSerializer(
                            many=False, required=False)

    pass_regex_validator = RegexValidator(
        regex=re.compile(
            r'(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[!@#$%^&*-_=]).{8,32}',
            re.UNICODE),
        message='''Пароль должен содержать от 8 до 32 символов,
         включая заглавные и строчные буквы,
         цифры и специальные символы (!@#$%%^&*-_=)'''
    )

    curr_pass = serializers.CharField(
        required=False,
        write_only=True,
    )
    new_pass1 = serializers.CharField(
        required=False,
        write_only=True,
        validators=[pass_regex_validator]
    )
    new_pass2 = serializers.CharField(
        required=False,
        write_only=True,
        validators=[pass_regex_validator]
    )

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'birth_date',
            'email',
            'curr_pass',
            'new_pass1',
            'new_pass2',
            'trackers_settings',
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        socialaccounts = map(
            lambda s: {'id': s.id, 'provider': s.provider,
                       'email': s.extra_data['email']},
            list(instance.socialaccount_set.all()))

        socialaccounts = list(socialaccounts)
        ret['socialaccounts'] = socialaccounts

        return ret

    def validate(self, data):
        password_validator = PasswordValidator()
        password_validator.context = self.context
        password_validator(data)
        return data

    def update(self, instance, validated_data):
        trackers_settings_data = validated_data.pop('trackers_settings')
        instance = super().update(instance, validated_data)
        TrackersUserSettingsSerializer().update(
            instance.trackers_settings,
            TrackersUserSettingsSerializer().validate(trackers_settings_data))
        instance.save()
        return instance
