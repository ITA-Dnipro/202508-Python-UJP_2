from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from users.models import UserProfile 

@shared_task
def send_welcome_email(user_id):
    """Send a welcome email asynchronously via Celery using user ID."""
    try:
        
        user = UserProfile.objects.get(pk=user_id)
    except UserProfile.DoesNotExist:
       
        return

    subject = "Welcome to Our Platform!"
    context = {'user_name': user.get_full_name() or user.username}
    message = render_to_string('emails/welcome_email.txt', context)
    html_message = render_to_string('emails/welcome_email.html', context)
    
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email], 
        html_message=html_message,
        fail_silently=False,
    ) 