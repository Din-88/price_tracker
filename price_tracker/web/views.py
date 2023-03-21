from django.conf import settings

from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.registration.views import SocialConnectView

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

from api_tracker.models import Tracker


class IndexView(generic.ListView):
    template_name = 'web/index.html'

    def get_queryset(self):
        return Tracker.objects.only('pk').all()[:24]


class ProfileView(LoginRequiredMixin, generic.ListView):
    template_name = 'web/profile.html'
    raise_exception = True

    def get_queryset(self):
        user = self.request.user
        return Tracker.objects.filter(users=user).only('pk').all()


class GoogleLogin(SocialLoginView): 
    # raise_exception = True
    client_class = OAuth2Client
    adapter_class = GoogleOAuth2Adapter
    # callback_url = 'http://127.0.0.1:8000/accounts/google/login/callback'
    callback_url = settings.SOCIALACCOUNT_GOOGLE_CALLBACK


class GoogleConnect(SocialConnectView):
    # raise_exception = True
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.SOCIALACCOUNT_GOOGLE_CALLBACK
    client_class = OAuth2Client


class Callback(generic.TemplateView):
    template_name = 'account/callback.html'
