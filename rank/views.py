
from django.shortcuts import render
from rest_framework.views import Response, status
from rest_framework.views import APIView
import pyrebase


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


class FireConnect(APIView):
    def get(self, request):
        day = database.child('Data').child('Day').get().val()
        print(day)
        # id = database.child('Data').child('Id').get().val()
        # projectname = database.child('Data').child('Projectname').get().val()
        # return render(request,"Home.html",{"day":day,"id":id,"projectname":projectname })
        return Response( "hello world", status=status.HTTP_200_OK )
    
