from django.contrib import admin
from django.urls import include, path

from web import urls as web_urls
from api_profile import urls as api_profile_urls
from api_tracker import urls as api_tracker_urls



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(web_urls.urlpatterns)),
    path('api/', include(api_profile_urls.urlpatterns)),
    path('api/', include(api_tracker_urls.urlpatterns)),
]

handler404 = 'web.views.error_404_view'