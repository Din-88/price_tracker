from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .views import (
    TrackerViewSet,
    TrackerAddForUser,
    TrackerDelForUser,
    TrackerNotify,
    UserNotify,
)


schema_view = get_schema_view(
    openapi.Info(
        title='API Docs',
        default_version='v1',
    )
)

router = DefaultRouter()
router.register(r'tracker', TrackerViewSet, basename='tracker')

urlpatterns = [
    path('', include(router.urls)),
    path('add/<int:pk>', TrackerAddForUser.as_view()),
    path('del/<int:pk>', TrackerDelForUser.as_view()),
    path('notify/<int:pk>', TrackerNotify.as_view()),
    path('user_notify/', UserNotify.as_view()),

    re_path(
        r'^docs/$',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='api_docs'),
]
