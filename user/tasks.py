from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_email_user(email, token):
    send_mail('Activate your BOHDANBLOG account',
              "Go to link:  {}".format(token),
              settings.EMAIL_HOST_USER,
              [email])
    return None
