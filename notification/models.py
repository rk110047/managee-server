from django.db import models
from utils.models import BaseAbstractModel
from dateutil.relativedelta import *
from subscription.models import SubscriptionPackage, UserSubscriptionPackage
from package.models import Package
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime, timedelta, time
from authentication.models import User, UserProfile

class UpcomingNotification(BaseAbstractModel):

    REOCCURANCE_CHOICES = [('N',"none"),('D',"daily"),('W',"weekly"),('M',"monthly"),('Y',"yearly")]
    
    users = models.ManyToManyField(User, related_name='user', blank=True)
    isGlobal = models.BooleanField(default=True)
    subscription = models.ManyToManyField(SubscriptionPackage, blank=True)
    package = models.ManyToManyField(Package, blank=True)
    title = models.CharField(max_length=1000)
    image_content = models.FileField(blank=True, null=True)
    text_content = models.TextField(blank=True, null=True)
    notify_time = models.DateTimeField()
    reoccurance = models.CharField(default='N', max_length=1, choices=REOCCURANCE_CHOICES)
    next_notify_time = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        if self.next_notify_time is None:
            self.next_notify_time = self.notify_time
        super(UpcomingNotification, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name_plural = "Notifications"        

@receiver(post_save, sender=UpcomingNotification, dispatch_uid="upcoming_notification_dispatch")
def update_notification(sender, instance, **kwargs):
    if instance.next_notify_time.date() == datetime.today().date():
        is_disconnected = post_save.disconnect(update_notification, sender=UpcomingNotification, dispatch_uid="upcoming_notification_dispatch")
        if is_disconnected:
            processNotification(instance)
            is_reconnected = post_save.connect(update_notification, sender=UpcomingNotification, dispatch_uid="upcoming_notification_dispatch")

def processNotification(notif):
    checkIfNotificationAlreadyPresent(notif)
    current = Notification(title=notif.title, image_content=notif.image_content, text_content=notif.text_content, notify_time=notif.next_notify_time, parent=notif)
    current.save()
    addUserReadRecieptRecords(notif, current)
    if notif.reoccurance == 'D':
        notif.next_notify_time = notif.next_notify_time + relativedelta(days=1)
    elif notif.reoccurance == 'W':
        notif.next_notify_time = notif.next_notify_time + relativedelta(weeks=1)
    elif notif.reoccurance == 'M':
        notif.next_notify_time = notif.next_notify_time + relativedelta(months=1)
    elif notif.reoccurance == 'Y':
        notif.next_notify_time = notif.next_notify_time + relativedelta(years=1)
    is_disconnected = post_save.disconnect(update_notification, sender=UpcomingNotification, dispatch_uid="upcoming_notification_dispatch")
    if is_disconnected:
        print(notif.next_notify_time)
        notif.save()
        is_reconnected = post_save.connect(update_notification, sender=UpcomingNotification, dispatch_uid="upcoming_notification_dispatch")

def checkIfNotificationAlreadyPresent(notif):
    today = datetime.now().date()
    tomorrow = today + timedelta(1)
    today_start = datetime.combine(today, time())
    today_end = datetime.combine(tomorrow, time())
    nstatus=Notification.objects.filter(parent=notif, notify_time__gte=today_start, notify_time__lte=today_end).first()
    if nstatus != None:
        nstatus.delete()

def addUserReadRecieptRecords(notification, newnotif):
    print(newnotif)
    reciepts = []
    users = set()
    if notification.isGlobal:
        for user in User.objects.all():
            users.add(user)
            #reciepts.append(ReadReciepts(notification=newnotif, user=user))
        #ReadReciepts.objects.bulk_create(reciepts)
        #return True
    for user in notification.users.all():
        users.add(user)
        #reciepts.append(ReadReciepts(notification=newnotif, user=user))
    for package in notification.package.all():
        for userprofile in UserProfile.objects.filter(package=package.id).select_related('user'):
            #reciepts.append(ReadReciepts(notification=newnotif, user=userprofile.user))
            users.add(userprofile.user)
    for sub in notification.subscription.all():
        for usersub in UserSubscriptionPackage.objects.filter(package=sub.id).select_related('user'):
            #reciepts.append(ReadReciepts(notification=newnotif, user=usersub.user))
            users.add(usersub.user)
    for u in users:
        reciepts.append(ReadReciepts(notification=newnotif, user=u))
    ReadReciepts.objects.bulk_create(reciepts)


class Notification(BaseAbstractModel):
    parent = models.ForeignKey(UpcomingNotification, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=1000)
    image_content = models.FileField(blank=True, null=True)
    text_content = models.TextField(blank=True, null=True)
    notify_time = models.DateTimeField()

    objects = models.Manager()

    def __str__(self):
        return f'{self.title}'

class ReadReciepts(BaseAbstractModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    read_status = models.BooleanField(default=False)

    objects = models.Manager()

    def __str__(self):
        return f'{self.user}_{self.notification}'

    class Meta:
        unique_together = ('user','notification',)

class StarredNotification(BaseAbstractModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)

    objects = models.Manager()

    def __str__(self):
        return f'{self.user}_{self.notification}'

    class Meta:
        unique_together = ('user','notification',)



