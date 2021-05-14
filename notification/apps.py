from django.apps import AppConfig


class NotificationConfig(AppConfig):
    name = 'notification'

    def ready(self):
        print("invoked")
        from notification.notificationmanager import setupNotificationManager
        setupNotificationManager()

