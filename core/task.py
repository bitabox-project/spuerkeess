from celery import shared_task
from django.core.mail import send_mail
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


@shared_task
def send_welcome_email(user):
    subject = "Confirmation de réception de votre demande d’ouverture de compte"
    
    # Chargez votre template HTML
    html_message = render_to_string('manager/email.html', {
        'user': user,
        'login_url': 'www.spuerkeess.co/login',
        'support_email': 'support@spuerkeess.co',
    })
    
    # Version texte brut
    plain_message = strip_tags(html_message)
    
    # Envoi de l'email
    send_mail(
        subject,
        plain_message,
        'support@spuerkeess.co',  # Email expéditeur
        [user.email],  # Liste des destinataires
        html_message=html_message,
        fail_silently=False,
    )


