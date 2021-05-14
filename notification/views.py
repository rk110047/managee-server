from django.shortcuts import render
import datetime
from datetime import datetime as dt
from django.utils.timezone import now

from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import (
    generics,
    status,
)
from rest_framework.parsers import (
    FormParser,
    MultiPartParser,
)
from rest_framework.permissions import (
    IsAuthenticated
)
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from authentication.renderer import UserJSONRenderer
from notification.models import ReadReciepts, StarredNotification, Notification
from notification.serializer import ReadRecieptsSerializer, StarredNotificationSerializer, StarredNotifSerializer

class UserNotificationAPIView(generics.ListAPIView, generics.GenericAPIView):

    serializer_class = ReadRecieptsSerializer
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
	
    def get_queryset(self): 
        read_status = self.request.query_params.get('read_status',False)
        print(read_status)
        user = self.request.user
        try:
            fav = ReadReciepts.objects.filter(user_id=user.id).filter(is_deleted=False).filter(read_status=read_status).all().prefetch_related('notification').order_by('-notification__notify_time')
            return fav
        except:
            response = {
                'message': 'error occurred'
            }
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        user = request.user
        read_status = request.data["read_status"]
        for notif in request.data["notifications"]:
            current_notif = ReadReciepts.objects.filter(notification_id=notif, user_id=user.id).first()
            current_notif.read_status = read_status
            current_notif.save()
        response = {
            'message': 'read status updated successfully'
        }
        return Response(response, status=status.HTTP_200_OK)


    def delete(self, request):
        user = request.user
        for notif in request.data["notifications"]:
            current_notif = ReadReciepts.objects.filter(notification_id=notif, user_id=user.id).first()
            current_notif.is_deleted = True
            current_notif.save()
        response = {
            'message': 'notification deleted successfully'
        }
        return Response(response, status=status.HTTP_200_OK)

class UserStarredNotificationAPIView(generics.ListCreateAPIView):
    
    serializer_class = StarredNotificationSerializer
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class_add = StarredNotifSerializer

    def get_queryset(self):
        user = self.request.user
        try:
            fav = StarredNotification.objects.filter(user_id=user.id).all().prefetch_related('notification').order_by('-notification__notify_time')
            return fav
        except:
            response = {
                'message': 'error occurred'
            }
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        user = self.request.user
        payload = request.data
        payload['user'] = user.id
        serializer = self.serializer_class_add(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            'data': { 'notification': serializer.data }
        }
        return Response(response, status=status.HTTP_201_CREATED)
