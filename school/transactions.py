# views.py
import requests
from django.conf import settings
from .serializer import *
from helper.workers import *
from rest_framework.decorators import api_view
from rest_framework.views import APIView, status, Response

@api_view(['POST'])
def verify_payment(request):
    transaction_id = request.data.get('transaction_id')
    tx_ref = request.data.get('tx_ref')
    school_id = request.data.get('school_id')
    url = f'https://api.flutterwave.com/v3/transactions/{transaction_id}/verify'

    metadata = {
        'payment_type': 'fee_payment',
        'school_id': school_id,
        'tenant': request.tenant.schema_name,
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {settings.FLUTTERWAVE_SECRET_KEY}',
        'metadata': metadata
    }
    response = requests.get(url, headers=headers)
    data = response.json()

    print(data)

    if data['status'] == 'success':
        update_registration(request, data, school_id, tx_ref)
        return Response({'status': 'success', 'data': data}, status=status.HTTP_200_OK)
    else:
        return Response({'status': 'error', 'message': data['message']}, status=status.HTTP_400_BAD_REQUEST)


def update_registration(request, transaction_history, school_id, tx_ref):
    feeInstallments = ["none", "first", "second", "complete"]
    transaction_id = request.data.get('transaction_id')
    payment = Payment.objects.filter(transaction_id=tx_ref).first()

    if payment.amount != transaction_history['data']['amount']:
        return Response({"message": "Fraud detected in transcation"}, status=status.HTTP_409_CONFLICT)
    
    registration = payment.registration

    # UPDATE PAYMENT OBJECT
    payment.is_complete = True
    payment.payment_status = "success"
    payment.payment_confirmation_date = timezone.now()
    payment.reference_number = transaction_history['data']['id']
    payment.notes = transaction_history['message']
    payment.currency = transaction_history['data']['currency']
    payment.installment_number = registration.payments.count()
    payment.payment_method = transaction_history['data']['payment_type']
    payment.payment_gateway = transaction_history['data']['meta']['MOMO_NETWORK']
    payment.save()

    # UPDATE REGISTRATION OBJECT
    registration.payments.aadd(payment)
    registration.payed_ammount += transaction_history['data']['amount']
    if registration.expected_ammount >= registration.payed_ammount:
        registration.is_complete = True
        registration.registration_status = "complete"
    
    current_status = registration.registration_status
    if current_status != "complete":
        registration.registration_status = feeInstallments[feeInstallments.index(current_status) + 1]

    registration.save()
    
    # Serializer student and send email to school admins
    student = StudentSerializer(registration.student).data

    admins_transaction_report_emails.delay(transaction_history, school_id, student)



@api_view(['POST'])
def verify_service_charge(request):
    transaction_id = request.data.get('transaction_id')
    tx_ref = request.data.get('tx_ref')
    school_id = request.data.get('school_id')
    registration_id = request.data.get('registration_id')
    url = f'https://api.flutterwave.com/v3/transactions/{transaction_id}/verify'

    metadata = {
        'payment_type': 'service_charge',
        'school_id': school_id,
        'tenant': request.tenant.schema_name,
        'registration_id': registration_id
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {settings.FLUTTERWAVE_SECRET_KEY}',
        'metadata': metadata
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    if data['status'] == 'success':
        update_service_charge(request, data, school_id, tx_ref)
        return Response({'status': 'success', 'data': data}, status=status.HTTP_200_OK)
    else:
        return Response({'status': 'error', 'message': data['message']}, status=status.HTTP_400_BAD_REQUEST)

def update_service_charge(request, transaction_history, school_id, tx_ref):
    service_charge = ServiceCharge.objects.filter(transaction_id=tx_ref).first()

    if not service_charge:
        return Response({"message": "Service charge not found"}, status=status.HTTP_404_NOT_FOUND)

    if service_charge.amount != transaction_history['data']['amount']:
        return Response({"message": "Fraud detected in transaction"}, status=status.HTTP_409_CONFLICT)
    
    service_charge.is_complete = True
    service_charge.payment_status = "success"
    service_charge.payment_confirmation_date = timezone.now()
    service_charge.reference_number = transaction_history['data']['id']
    service_charge.notes = transaction_history['message']
    service_charge.currency = transaction_history['data']['currency']
    service_charge.payment_method = transaction_history['data']['payment_type']
    service_charge.payment_gateway = transaction_history['data']['meta'].get('MOMO_NETWORK')
    service_charge.save()

    # Update the related registration
    registration = service_charge.registration
    registration.paid_charges = True
    registration.save()

    # Send email notification
    admins_service_charge_report_emails.delay(transaction_history, school_id)


@api_view(['POST'])
def verify_subscription(request):
    transaction_id = request.data.get('transaction_id')
    url = f'https://api.flutterwave.com/v3/transactions/{transaction_id}/verify'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {settings.FLUTTERWAVE_SECRET_KEY}',
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    if data['status'] == 'success':
        grant_school_permissions(request, data)
        return Response({'status': 'success', 'data': data}, status=status.HTTP_200_OK)
    else:
        return Response({'status': 'error', 'message': data['message']}, status=status.HTTP_400_BAD_REQUEST)

def grant_school_permissions(request, transaction_history):
    subscription_plans = {
        "base": 50000,
        "standard": 70000,
        "premium": 120000
    }
    active_program = Program.get_active_program()

    subscription = active_program.subscription
    subscription.is_complete = True
    subscription_plans.get( transaction_history.data.amount )

    subscription.save()

    

@app.task
def admins_transaction_report_emails(transaction_history, school_id, student):
   
    school = School.objects.filter(id=school_id).first()

    principal_email = school.principal_email
    director_email = school.director_email
    director_phone = school.director_phone

    template = f'emails/received_payment.html'
    
    context ={transaction_history, student}
    try:
        email_body = render_to_string(template, context)
        
        email = EmailMessage(
            subject="[IMPORTANT] Fee payment by a student",
            body=email_body,
            from_email='rank.tiidel@gmail.com',
            to=[principal_email, director_email]
        )
        email.content_subtype = "html" 
        email.send()

    except Exception as e:
        print(e)



@app.task
def admins_service_charge_report_emails(transaction_history, school_id, student):
    pass




