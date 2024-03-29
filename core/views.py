from django.shortcuts import render
from rest_framework import permissions
from rest_framework.views import APIView, Response, status
from rest_framework.generics import GenericAPIView
from django.contrib.auth import authenticate

# Create your views here.
from .models import User
from helper.helper import CLIENT_URL
from core.utils import Util
from .serializers import RegisterSerializer, LoginSerializer, ResetPasswordSerializer
from rest_framework_simplejwt.tokens import RefreshToken


from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

import jwt
from django.conf import settings

class VerifyEmail(GenericAPIView):
    def get(self, request):
        token = request.GET.get('token')
        try:
            response = jwt.decode(token,settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=response['user_id'])
            
            if not user.email_verified:
                user.email_verified = True
                user.is_active = True
                user.save()
            return Response({"success": "account verified"}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as invalidToken:
            return Response({"error": "Activation time out"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            print(e)
            return Response({"error": e}, status=status.HTTP_403_FORBIDDEN)

class Utils: 
    def get_user_by_email(email):
        user = User.objects.filter(email=email).first()  
        return user  

class RegisterAPIView(GenericAPIView):

    serializer_class = RegisterSerializer

    def sendRegisterEmail(self, user, request, token):

        current_site = get_current_site(
            request = request
            ).domain
                

        relativeLink = reverse('verify-email')
        absurl = 'http://'+current_site+relativeLink + "?token=" + str(token)
        email_body = f'Hi there,\n Welcome to SACRETE HEART COLLEGE management system {user.username} click the link below to activate your account\n\n {absurl}'
        data = {
            'email_body': email_body,
            'to_email': user.email,
            'email_subject': 'Confirm account',
        }

        Util.send_email(data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save()

            user_data = serializer.data
            user = User.objects.get(email=user_data['email'])

            token = RefreshToken.for_user(user).access_token
            self.sendRegisterEmail(user, request, token)

            return Response( serializer.data, status=status.HTTP_201_CREATED )
        return Response( serializer.errors, status=status.HTTP_400_BAD_REQUEST )
    

class LoginAPIView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        email = request.data.get('email', None)
        password = request.data.get('password', None)

        pre_user = Utils.get_user_by_email(email)
        
        if not pre_user:
            return Response({"message": "No such user"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not pre_user.is_active:
            return Response({"message": "Account not active"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=email, password = password)
        
        if not user:
            return Response({"message": "Invalid credentials, try again"}, status=status.HTTP_401_UNAUTHORIZED)
        
        
        serializer = self.serializer_class(user)

        server = str(request.tenant)
        server_url = f"https://{server}.{CLIENT_URL}"

        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': serializer.data,
            'server': server,
            'server_url': server_url,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)

        
class UserView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = RegisterSerializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)
    



class RequestPasswordReset(GenericAPIView):

    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=data)

        try:
            email = request.data.get('email')
            
            if User.objects.filter(email=email).exists():

                user = User.objects.get(email=email)
                uidb64 = urlsafe_base64_encode(user.id)
                token = PasswordResetTokenGenerator().make_token(user)

                # Send reset email
                current_site = get_current_site(
                    request = request
                    ).domain
                
                relativeLink = reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token':token})
                absurl = 'http://'+current_site+relativeLink
                email_body = f'To Reset password for {user.username} user the link below \n {absurl}'
                data = {
                    'email_body': email_body,
                    'to_email': user.email,
                    'email_subject': 'Reset password',
                    
                }
                Util.send_email(data=data)
        
        except Exception as indentifier:
            print(indentifier)
        return Response({"success": "we have sent you a link to reset your password"}, status=status.HTTP_200_OK)


class PasswordTokenCheck(GenericAPIView):
    def get(self, request, uidb64, token):
        data = request.data
        print(data)