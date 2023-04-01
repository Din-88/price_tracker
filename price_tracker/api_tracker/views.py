
import json
from dataclasses import asdict
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from django.conf import settings
from django.utils import timezone
from django.db.models import Prefetch, Max, Count
from django.shortcuts import get_object_or_404, redirect, render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status, viewsets
from rest_framework.generics import (
    RetrieveAPIView,
    GenericAPIView,
    UpdateAPIView, CreateAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.viewsets import ViewSet, GenericViewSet
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.decorators import action
from rest_framework import mixins
from rest_framework import serializers
# from rest_framework.serializers import APIException, ValidationError

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from urllib.parse import urlparse

from .serializers import (
    TrackerSerializer,
    TrackerUpdateSerializer,
    TrackersUserSettingsSerializer,
    NotifyTypeSerializer,
    TrackerNotifySerializer,
    NotifyCaseSerializer,
    NotifyTypeCaseSerializer,
    NewTrackerSerializer,
)

from .models import *
from .models import Tracker, Price
from .workers.tasks import task_send_mail_admins
from .workers.parsers.parsers import Parsers


class TrackerViewSet(GenericViewSet):
    days_ago = timezone.now() - timezone.timedelta(days=90)
    queryset = Tracker.objects \
        .prefetch_related(
            Prefetch(
                'prices',
                Price.objects.filter(date_time__gt=days_ago).order_by('id')
            )
        )
    
    serializer_class = TrackerSerializer
    allowed_methods = ['get', 'put' 'post', 'patch']

    def get_permissions(self):
        if self.action in ['get_detail', 'get_list']:
            permission_classes = [AllowAny,]
        elif self.action == 'update':
            permission_classes = [IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]

        return [permission() for permission in permission_classes] 
    
    @action(detail=True, methods=['get'], url_path='get',
            permission_classes=[AllowAny])
    def get_detail(self, request, pk=None):
        instance = self.get_object()
        # days_ago = timezone.now() - timezone.timedelta(days=90)
        # instance.prices \
        #     .filter(date_time__gt=days_ago) \
        #     .order_by('-date_time')
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='get',
            permission_classes=[AllowAny])
    def get_list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='update',
            permission_classes=[AllowAny])
    def get_update(self, request, *args, **kwargs):
        instance = self.get_object()

        url = instance.url
        host = instance.host
        prev_price = instance.price

        parser = Parsers().get_parser(host=urlparse(url).hostname)
        
        raw_data = parser(url=url).get_info()
        raw_data = asdict(raw_data)

        serializer = self.get_serializer(instance, data=raw_data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()
        instance.prices.add(Price.objects.create(price=instance.price))
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='new',
            permission_classes=[AllowAny])
    def new(self, request, url=None, *args, **kwargs):
        url = request.data.get('url')
        if not url:
            raise serializers.ValidationError(
                {'error': 'url required'}, code=status.HTTP_400_BAD_REQUEST)

        tracker = Tracker.objects.filter(url=url).first()
        if tracker:
            serializer = TrackerSerializer(tracker)
            return Response(serializer.data, status=status.HTTP_302_FOUND)

        parser = Parsers().get_parser(host=urlparse(url).hostname)
        if not parser:
            msg = f'url: {url} \r\nuser: {request.user.username}'
            task_send_mail_admins('new_url', msg)
            
            raise serializers.ValidationError(
                {'error': 'url unknown'},
                code=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        raw_data = parser(url=url).get_info()

        serializer = TrackerSerializer(data=asdict(raw_data))
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        instance.prices.add(Price.objects.create(price=instance.price))

        return Response(serializer.data, status=status.HTTP_201_CREATED)        

        # serializer = self.get_serializer(data={'url': url})
        # serializer.is_valid(raise_exception=True)
        # serializer.save()


# class TrackerPreview(viewsets.ReadOnlyModelViewSet):
#     serializer_class = TrackerSerializer
#     permission_classes = [permissions.AllowAny,]

#     # !!! need optimization here !!!

#     user = get_user_model().objects.get(username='admin')
#     # queryset = Tracker.objects.filter(users=user).all()
#     days_ago = timezone.now() - timezone.timedelta(days=90)
#     queryset = Tracker.objects.prefetch_related(Prefetch('prices', Price.objects.filter(date_time__gt=days_ago).order_by('id')))


class TrackerAddForUser(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        tracker = Tracker.objects.get(pk=pk)
        if tracker:
            tracker.users.add(request.user)
            return Response(data={'add_for_user': 'ok'},
                            status=status.HTTP_200_OK)
        return Response(data={'add_for_user': 'error'},
                        status=status.HTTP_400_BAD_REQUEST)


class TrackerDelForUser(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        tracker = Tracker.objects.get(pk=pk)
        if tracker:
            tracker.users.remove(request.user)
            return Response(data={'del_for_user': 'ok'},
                            status=status.HTTP_200_OK)
        return Response(data={'del_for_user': 'error'},
                        status=status.HTTP_400_BAD_REQUEST)


class TrackerNotify(RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TrackerNotifySerializer
    http_method_names = ['patch', 'post']

    def get_object(self):
        pk = self.kwargs.get('pk')
        tracker = get_object_or_404(Tracker, pk=pk)
        user_tracker = get_object_or_404(tracker.user_tracker,
                                         user=self.request.user)

        return user_tracker


class UserNotify(APIView):
    def get(self, request):
        notify_types = NotifyTypeSerializer(
            instance=NotifyType.objects.all(), many=True).data
        notify_cases = NotifyCaseSerializer(
            instance=NotifyCase.objects.all(), many=True).data
        data = {
            "notify_types": notify_types,
            "notify_cases": notify_cases
        }
        return Response(data)
