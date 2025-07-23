# utils/emails.py
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from spuerr import settings

def send_html_welcome_email(user):
    subject = "Bienvenue chez nous !"
    text_content = "Merci pour votre inscription..."
    html_content = render_to_string('emails/welcome.html', {'user': user})
    
    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email]
    )
    email.attach_alternative(html_content, "text/html")
    email.send()