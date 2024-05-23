from celery import shared_task
from django.db import connection
from rank.celery import app
from tenant_schemas_celery.task import TenantTask


from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from fcm_django.models import FCMDevice
from school.models import Grade

@app.task
def connection_test(arg1, arg2):
    # Do something asynchronously
    result = arg1 + arg2
    return result


    

@app.task
def send_email_with_template(data: dict, template_name: str, context: dict, recipient_list: list):
    template = f'emails/{template_name}'
    
    try:
        email_body = render_to_string(template, context)
        
        email = EmailMessage(
            subject=data['email_subject'],
            body=email_body,
            from_email='rank.tiidel@gmail.com',
            to=recipient_list
        )
        email.content_subtype = "html" 
        email.send()

    except Exception as e:
        print(e)



@app.task
def send_whatsapp_message_with_api(message: str, phone: str):
    
    try:
        # Send whatsapp message to the that number
        pass

    except Exception as e:
        print(e)






# @app.task
# def send_push_notification(registration_id, message):
#     push_service = FCMNotification(api_key=settings.FCM_SERVER_KEY)
#     registration_ids = [registration_id]
#     result = push_service.notify_multiple_devices(registration_ids=registration_ids, message_title='Your App Name', message_body=message)
#     return result
