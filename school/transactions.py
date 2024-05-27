# views.py
import requests
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.views import APIView, status, Response

@api_view(['POST'])
def verify_payment(request):
    transaction_id = request.data.get('transaction_id')
    url = f'https://api.flutterwave.com/v3/transactions/{transaction_id}/verify'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {settings.FLUTTERWAVE_SECRET_KEY}',
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    print(data)

    if data['status'] == 'success':
        return Response({'status': 'success', 'data': data}, status=status.HTTP_200_OK)
    else:
        return Response({'status': 'error', 'message': data['message']}, status=status.HTTP_400_BAD_REQUEST)
