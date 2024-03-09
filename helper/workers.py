from celery import shared_task
from django.db import connection
from rank.celery import app
from tenant_schemas_celery.task import TenantTask


from django.template.loader import render_to_string
from django.core.mail import EmailMessage

@app.task
def connection_test(arg1, arg2):
    # Do something asynchronously
    result = arg1 + arg2
    return result


    
@shared_task(base=TenantTask, bind=True)
def my_shared_task():
    print("foo")

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