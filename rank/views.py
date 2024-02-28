
from django.shortcuts import render
from rest_framework.views import Response, status
from rest_framework.views import APIView
import pyrebase
from rest_framework.decorators import api_view, permission_classes
from tenant.models import Client, Domain
from rest_framework.permissions import IsAuthenticated

from django.core.exceptions import ObjectDoesNotExist
import random
import string


from core.serializers import LoginSerializer
from core.user_groups import create_groups


def index(request):
    return render(request, 'index.html')

def not_found(request, exception):
    return render(request, 'not_found.html')


config={
    "apiKey": "AIzaSyAXhQ7QEcb6PctU4FPCe34jzYIf-TtkGTw",
    "authDomain": "ranksecondary.firebaseapp.com",
    "databaseURL": "https://ranksecondary-default-rtdb.firebaseio.com",
    "projectId": "ranksecondary",
    "storageBucket": "ranksecondary.appspot.com",
    "messagingSenderId": "15848541862",
    "appId": "1:15848541862:web:553d46ae739e01884fae67",
    "measurementId": "G-2PRC9RLYBL"
}

firebase=pyrebase.initialize_app(config)
authe = firebase.auth()
database=firebase.database()


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
            
            # Create new tenant and domain with given school name and abbreviation
            new_tenant = Client(schema_name=tenant_name, name=school_name)
            new_tenant.save()

            new_domain = Domain(tenant=new_tenant, domain=f'{tenant_name}.localhost' )
            new_domain.save()

            # Create groups for this user
            create_groups()

            # Append schools list for that user in the shared user module
            user_school = {
                "tenant": tenant_name,
                "school": school_name
            }
            user.schools.append(user_school)
            user.save()

            user_serializer = LoginSerializer(user)
            serialized_user = user_serializer.data

            response = {
                "domain": str(new_domain),
                "tenant": str(new_tenant),
                "school_name": school_name,
                "owner": serialized_user
            }

            return Response({"data": response}, status=status.HTTP_201_CREATED)
    
    return Response({"message": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


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



def generate_unique_string(length):
    letters = string.ascii_lowercase
    unique_string = ''.join(random.choice(letters) for _ in range(length))
    return unique_string

def generate_unique_tenant_names(original_name):
    unique_names = []

    for _ in range(3):

        while True:

            unique_string = generate_unique_string(3)
            tenant_name = f"{original_name}_{unique_string}"

            try:
                Client.objects.get(name=tenant_name)

            except Client.DoesNotExist:
                unique_names.append(tenant_name)
                break

    return unique_names
        

class FireConnect(APIView):
    def get(self, request):
        day = database.child('Data').child('Day').get().val()
        print(day)
        # id = database.child('Data').child('Id').get().val()
        # projectname = database.child('Data').child('Projectname').get().val()
        # return render(request,"Home.html",{"day":day,"id":id,"projectname":projectname })
        return Response( "hello world", status=status.HTTP_200_OK )
    
