from django.core.mail import send_mail
from django.conf import settings
from .models import EmailNotification

def send_order_notification(order):
    subject = f"Заявка №{order.order_number} создана"
    body = f"Здравствуйте, {order.customer.name}!\n\nВаша заявка №{order.order_number} на сумму {order.total_amount} руб. принята.\nСтатус: {order.status.name}."
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [order.customer.email])
    EmailNotification.objects.create(
        order=order,
        recipient_email=order.customer.email,
        subject=subject,
        body=body
    )