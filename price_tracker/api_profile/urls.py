from django.urls import path

from .views import AccountBasics


urlpatterns = [
    path('basics/', AccountBasics.as_view()),
]
