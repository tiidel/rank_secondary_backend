from firebase_admin import credentials, initialize_app, firestore

from rest_framework import status
from rest_framework.response import Response

from fcm_django.models import FCMDevice
from fcm_django.fcm import fcm_send_bulk_message, fcm_send_message

from django.db.models import Q
from django.conf import settings

from firebase_admin.messaging import Message, Notification



def welcome(request):
    FCMDevice.objects.send_message(Message(data=dict()))
    
    FCMDevice.objects.send_message(
        Message(notification=Notification(title="title", body="body", image="image_url"))
    )
    device = FCMDevice.objects.first()
    device.send_message(Message(...))