from dataclasses import asdict

from django.utils import timezone
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.decorators import action
from rest_framework import serializers

from urllib.parse import urlparse

from .serializers import (
    TrackerSerializer,
    NotifyTypeSerializer,
    TrackerNotifySerializer,
    NotifyCaseSerializer,
)

from .models import Tracker, Price, NotifyType, NotifyCase
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
