from django.urls import path
from notification.views import UserNotificationAPIView, UserStarredNotificationAPIView

urlpatterns = [
    path('', UserNotificationAPIView.as_view(),
         name='user_notification'),
    path('starred/', UserStarredNotificationAPIView.as_view(),
         name='starred_notification')
]
