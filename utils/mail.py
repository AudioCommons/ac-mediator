from django.core.mail import send_mail as django_send_email
from django.conf import settings


def send_mail(subject, message, to_emails, from_email=settings.DEFAULT_FROM_EMAIL, fail_silently=True):
    """Send email using Django's send_email function but setting a number of defaults and adding a
    prefix in the subject."""
    if not subject.startswith(settings.EMAIL_SUBJECT_PREFIX):
        subject = settings.EMAIL_SUBJECT_PREFIX + subject
    django_send_email(subject, message, from_email, to_emails, fail_silently)
