
from django.shortcuts import render
from rest_framework.views import Response, status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from tenant.models import Client, Domain
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken

from django.core.exceptions import ObjectDoesNotExist
import random
import string
import requests
import json
from fcm_django.models import FCMDevice

from core.serializers import LoginSerializer
from core.models import User, UserManager
from core.user_groups import create_groups
from tenant.serializers import DomainSerializer
from django.contrib.auth.models import Group
from django_tenants.utils import tenant_context
from helper.workers import send_email_with_template
from helper.helper import CLIENT_URL

# from firebase_admin.messaging import Message
# from firebase_admin import messaging



def index(request):
    return render(request, 'index.html')

def not_found(request, exception):
    return render(request, 'not_found.html')


def generate_random_password():
    return User.objects.make_random_password()

def assign_user_to_group( user, role):
    group = Group.objects.get(name__iexact=role)
    if group:
        return group.user_set.add(user)
    
# CREATE TENANT VIEW
@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def create_tenant_view(request):
    if request.method == 'POST':
        tenant_name = request.data.get('tenant_name')
        school_name = request.data.get('school_name')

        try:
            existing_tenant = Client.objects.get(schema_name=tenant_name)
            return Response({"message": "Tenant already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Client.DoesNotExist:
            user = request.user
            
            new_tenant = Client(schema_name=tenant_name, name=school_name)
            new_tenant.save()

            new_domain = Domain(tenant=new_tenant, domain=f'{tenant_name}.localhost' )
            new_domain.save()


            user_school = {
                "tenant": tenant_name,
                "school": school_name
            }
            user.schools.append(user_school)
            user.save()

            admin_created = False
            tenant_user = None
            with tenant_context(new_tenant):
                create_groups()
                generated_password = generate_random_password()


                create_admin = {
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "password": generated_password,
                    "is_staff": True,
                    "is_active": True,
                    "is_superuser": True,
                    "email_verified": True,
                    "schools": user.schools,
                    "school_code": tenant_name
                }

                
                tenant_user = User.objects.create_superuser(**create_admin)
                admin_created = True if tenant_user else False
                user = authenticate(request, username=tenant_user.email, password=generated_password)

                if user is not None:
                    login(request, user)
                    ctx = {
                        "user": user,
                        "password": generated_password
                    }
                    data = { 'email_subject': 'Congratulations. your school has been registered'}
                    send_email_with_template(data, context=ctx, template_name='school_created.html', recipient_list=[user.email])

            user_serializer = LoginSerializer(user)
            serialized_user = user_serializer.data
            
            refresh = RefreshToken.for_user(tenant_user)
            server_url = f"https://{tenant_name}.{CLIENT_URL}"
            response = {
                "domain": str(new_domain),
                "tenant": str(new_tenant),
                "school_name": school_name,
                "owner": serialized_user,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                "admin_created": admin_created,
                "server": tenant_name,
                "server_url": server_url
            }

            return Response({"data": response}, status=status.HTTP_201_CREATED)
    
    return Response({"message": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# TENANT EXIST VIEW
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tenant_exist_view(request):
    if request.method == 'POST':

        name = request.data.get('school_abr')

        try:
            client = Client.objects.get(schema_name=name)
            if client: 
                recommendations = generate_unique_tenant_names(name)
                return Response({"recommendations": recommendations}, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({"message": "school is valid", "unique": True}, status=status.HTTP_200_OK)


        return Response({"message": "client"}, status=status.HTTP_200_OK)
    
    return Response({"message": "method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# GET TENANTS
@api_view(['GET'])
def fetch_tenants(request):
    if request.method == 'GET':

        name = request.data.get('school_abr')

        client = Domain.objects.all()
        serializer = DomainSerializer(client, many=True)
        print(serializer.data)
       
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    return Response({"message": "method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



def generate_unique_string(length):
    letters = string.ascii_lowercase
    unique_string = ''.join(random.choice(letters) for _ in range(length))
    return unique_string

def generate_unique_tenant_names(original_name):
    unique_names = []

    for _ in range(3):

        while True:

            unique_string = generate_unique_string(3)
            tenant_name = f"{original_name}{unique_string}"

            try:
                Client.objects.get(name=tenant_name)

            except Client.DoesNotExist:
                unique_names.append(tenant_name)
                break

    return unique_names
        




# @api_view(['POST'])
# def send_notification(request):
#     data = request.data
    
#     if 'message' not in data:
#         return Response({'error': 'Message is required'}, status=400)
    
#     # Retrieve all registered devices
#     devices = FCMDevice.objects.all()
    
 
#     for device in devices:
#         msg = device.send_message(Message(data['message'], topic="SOME TOPIC"))
#         print(device, msg)
    

#     return Response({'success': 'Notification sent successfully'})


# @api_view(['POST'])
# def send_notification(request):
#     data = request.data
    
#     # Retrieve all registered devices
#     devices = FCMDevice.objects.all()
    
#     # Send message without specifying a topic
#     response = devices.send_message(
#         Message(
#             data={
#                 "Nick" : "Mario",
#                 "body" : "great match!",
#                 "Room" : "PortugalVSDenmark"
#             }
#         )
#     )

#     print("Notifying all my people, wuna gather...", response)
    
#     return Response({'success': 'Notification sent successfully'})


# @api_view(['POST'])
# def send_notification(request):
#     token = request.data.get('token')
#     title = request.data.get('title')
#     body = request.data.get('body')


#     if not (token and title and body):
#         return Response({'error': 'Missing parameters'}, status=400)

#     try:
#         message = messaging.Message(
#             notification=messaging.Notification(
#                 title=title,
#                 body=body,
#             ),
#             token=token,
#         )
#         response = messaging.send(message)
#         print('Successfully sent message:', response)
#         return Response({'success': 'Notification sent successfully'})
#     except Exception as e:
#         print('Error sending message:', e)
#         return Response({'error': 'Failed to send notification'}, status=500)
