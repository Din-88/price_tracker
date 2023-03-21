from django import urls
from django.urls import include, path, re_path
from dj_rest_auth.registration.views import (
    SocialAccountListView, SocialAccountDisconnectView
)
from . import views

from rest_framework.routers import DefaultRouter
from django.views.generic import (
    RedirectView, 
    TemplateView,
)

from .views import (
    AccountBasics,
)

urlpatterns = [
    path('basics/', AccountBasics.as_view()),
]