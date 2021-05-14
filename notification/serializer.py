import json
from rest_framework import serializers
from notification.models import Notification, ReadReciepts, StarredNotification

class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        exclude = ('parent',)

    def create(self, validated_data):
        return Notification.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.save()
        return super().update(instance, validated_data)


class ReadRecieptsSerializer(serializers.ModelSerializer):
    
    notification = NotificationSerializer()

    class Meta:
        model = ReadReciepts
        fields = ('notification','read_status',)

class StarredNotificationSerializer(serializers.ModelSerializer):

    notification = NotificationSerializer()

    class Meta:
        model = StarredNotification
        fields = ('notification',)

class StarredNotifSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = StarredNotification
        fields = ('__all__')
