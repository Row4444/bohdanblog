from django.core.mail import send_mail
from django.conf import settings


def email(w):
    send_mail('hello', w, settings.EMAIL_HOST_USER, ['nikitabelik205@gmail.com'])
