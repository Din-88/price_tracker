from django import urls
from django.urls import include, path, re_path
from dj_rest_auth.registration.views import (
    SocialAccountListView,
    SocialAccountDisconnectView,
)

from . import views


urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('profile/', views.ProfileView.as_view(), name='profile'),

    path('accounts/', include('allauth.urls')),
    path('api/google/', views.GoogleLogin.as_view(), name='api_google_login'),
    path('api/google/connect/', views.GoogleConnect.as_view(), name='api_google_connect'),
    path('google/callback/', views.Callback.as_view(), name='callback'),
    
    path(
        'socialaccounts/',
        SocialAccountListView.as_view(),
        name='social_account_list'
    ),
    path(
        'socialaccounts/<int:pk>/disconnect/',
        SocialAccountDisconnectView.as_view(),
        name='social_account_disconnect'
    ),

    re_path(r'^webpush/', include('webpush.urls')),
]