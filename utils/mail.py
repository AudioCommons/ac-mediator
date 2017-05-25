from django.core.mail import send_mail as django_send_email
from django.conf import settings
from django.template.loader import render_to_string


def send_mail(to_emails, from_email=settings.DEFAULT_FROM_EMAIL, subject='No subject',
              message=None, template=None, context=None, fail_silently=True):
    """Send email using Django's send_email function but setting a number of defaults and adding a
    prefix in the subject. It also renders a template with a context if provided."""
    if not subject.startswith(settings.EMAIL_SUBJECT_PREFIX):
        subject = settings.EMAIL_SUBJECT_PREFIX + subject
    if template is not None and context is not None:
        message = render_to_string(template, context)
    if type(to_emails) is not list and type(to_emails) is not tuple:
        to_emails = (to_emails, )
    django_send_email(subject, message, from_email, to_emails, fail_silently)
