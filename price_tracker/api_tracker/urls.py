from django import urls
from django.urls import include, path, re_path
from dj_rest_auth.registration.views import (
    SocialAccountListView, SocialAccountDisconnectView
)
from . import views

from rest_framework.routers import DefaultRouter, SimpleRouter
from django.views.generic import (
    RedirectView, 
    TemplateView,
)

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title='API Docs',
        default_version='v1',
    )
)

from .views import (
    TrackerViewSet,
    # TrackerPreview, 
    TrackerAddForUser,
    TrackerDelForUser,
    TrackerNotify,
    # TrackerUpdate,
    UserNotify,
    # TrackerNew,
)

router = DefaultRouter()
# router.register(r'trackers', TrackerPreview, basename='tracker')

# router = SimpleRouter()
router.register(r'tracker', TrackerViewSet, basename='tracker')

urlpatterns = [
    # path('trackers/', TrackerPreview.as_view({'get': 'list'})),
    path('', include(router.urls)),
    # path('', TrackerViewSet.as_view()),
    path('add/<int:pk>', TrackerAddForUser.as_view()),
    path('del/<int:pk>', TrackerDelForUser.as_view()),
    path('notify/<int:pk>', TrackerNotify.as_view()),
    # path('update/<int:pk>', TrackerUpdate.as_view()),
    path('user_notify/', UserNotify.as_view()),
    # path('new/', TrackerNew.as_view()),

    re_path(r'^docs/$', schema_view.with_ui('swagger', cache_timeout=0), name='api_docs'),
]