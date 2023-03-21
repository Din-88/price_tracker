from allauth.account.models import EmailAddress
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account import app_settings
from allauth.account.app_settings import EmailVerificationMethod
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a
        social provider, but before the login is actually processed
        (and before the pre_social_login signal is emitted).

        We're trying to solve different use cases:
        - social account already exists, just go on
        - social account has no email or email is unknown, just go on
        - social account's email exists, link social account to existing user
        """        

        # some social logins don't have an email address, e.g. facebook accounts
        # with mobile numbers only, but allauth takes care of this case so just
        # ignore it
        if 'email' not in sociallogin.account.extra_data:
            return
        
        # Ignore existing social accounts, just do this stuff for new ones
        if sociallogin.is_existing:
            process = sociallogin.state.get('process')
            if process == 'login':
                return
            elif process == 'connect':
                raise serializers.ValidationError({f'provider_{sociallogin.account.provider}':'Действие отменено.'})            
            return

        # check if given email address already exists.
        # Note: __iexact is used to ignore cases
        try:
            email = sociallogin.account.extra_data['email'].lower()
            email_address = EmailAddress.objects.get(email__iexact=email)

        # if it does not, let allauth take care of this new social account
        except EmailAddress.DoesNotExist:
            return

        # if it does, connect this new social login to the existing user
        user = email_address.user
        sociallogin.connect(request, user)

    def validate_disconnect(self, account, accounts):
        """
        Validate whether or not the socialaccount account can be
        safely disconnected.
        """
        if len(accounts) == 1:
            # No usable password would render the local account unusable
            if not account.user.has_usable_password():
                raise serializers.ValidationError({'socialaccounts':_('Your account has no password set up.')})
            # No email address, no password reset
            if app_settings.EMAIL_VERIFICATION == EmailVerificationMethod.MANDATORY:
                if not EmailAddress.objects.filter(
                    user=account.user, verified=True
                ).exists():
                    raise serializers.ValidationError(
                        _("Your account has no verified e-mail address.")
                    )