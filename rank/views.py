
from django.shortcuts import render
from rest_framework.views import Response, status
from rest_framework.views import APIView
import pyrebase
from rest_framework.decorators import api_view
from tenant.models import Client, Domain

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



@api_view(['POST'])
def create_tenant_view(request):
    if request.method == 'POST':
        tenant_name = request.data.get('tenant_name')
        school_name = request.data.get('school_name')

        new_tenant = Client(schema_name=tenant_name, name=school_name)
        new_tenant.save()

        new_domain = Domain(tenant=new_tenant, name=tenant_name)
        new_domain.save()

        print(new_tenant)
        print(new_domain)

        return Response({"message": "creating tenant"}, status=status.HTTP_200_OK)
    
    return Response({"message": "method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)




class FireConnect(APIView):
    def get(self, request):
        day = database.child('Data').child('Day').get().val()
        print(day)
        # id = database.child('Data').child('Id').get().val()
        # projectname = database.child('Data').child('Projectname').get().val()
        # return render(request,"Home.html",{"day":day,"id":id,"projectname":projectname })
        return Response( "hello world", status=status.HTTP_200_OK )
    
