from notification.models import UpcomingNotification, Notification, ReadReciepts, processNotification
from datetime import datetime, timedelta, time
from dateutil.relativedelta import *
from apscheduler.schedulers.background import BackgroundScheduler
from authentication.models import User, UserProfile

def setupNotificationManager():
    scheduler = BackgroundScheduler()
    scheduler.add_job(processTodayNotifications, 'cron', hour=10, minute=16)
    scheduler.start()    

def processTodayNotifications():
    print("scheduler processing started") 
    today = datetime.now().date()
    tomorrow = today + timedelta(1)
    today_start = datetime.combine(today, time())
    today_end = datetime.combine(tomorrow, time())
    upcomingNotifications = list(UpcomingNotification.objects.filter(next_notify_time__gte=today_start, next_notify_time__lte=today_end))
    print(*upcomingNotifications, sep=",")
    for notif in upcomingNotifications:
        processNotification(notif)
