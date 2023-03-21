from django.contrib import admin
from django.urls import include, path, re_path

from django.conf import settings
from django.conf.urls.static import static

from web import urls as web_urls
from api_profile import urls as api_profile_urls
from api_tracker import urls as api_tracker_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(web_urls.urlpatterns)),
    path('api/', include(api_profile_urls.urlpatterns)),
    path('api/', include(api_tracker_urls.urlpatterns)),
] 
# + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)