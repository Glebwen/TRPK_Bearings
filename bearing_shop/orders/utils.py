from django.core.mail import send_mail
from django.conf import settings
from .models import EmailNotification

def send_order_notification(order):
    subject = f'Ваша заявка №{order.order_number} принята'
    
    items_list = ''
    for item in order.items.all():
        items_list += f'- {item.bearing.name} x {item.quantity} = {item.price_at_order * item.quantity} руб.\n'
    
    message = f'''
Здравствуйте, {order.customer.name}!

Ваша заявка №{order.order_number} успешно создана.

Состав заказа:
{items_list}

Итого к оплате: {order.total_amount} руб.

Статус заявки: {order.status.name}

Спасибо за покупку!
'''
    
    try:
        send_mail(
            subject=subject,
            message=message.strip(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer.email],
            fail_silently=False,
        )
        
        EmailNotification.objects.create(
            order=order,
            recipient_email=order.customer.email,
            subject=subject,
            body=message
        )
        print(f"Уведомление отправлено на {order.customer.email}")
        
    except Exception as e:
        print(f"Ошибка отправки email: {e}")

def send_status_notification(order, old_status, new_status):
    """Отправка уведомления клиенту при изменении статуса заявки"""
    
    subject = f'Статус заявки №{order.order_number} изменён'
    
    message = f'''
Здравствуйте, {order.customer.name}!

Статус вашей заявки №{order.order_number} был изменён.

Старый статус: {old_status.name}
Новый статус: {new_status.name}
Сумма заказа: {order.total_amount} руб.

С уважением,
Магазин подшипников
'''
    
    try:
        send_mail(
            subject=subject,
            message=message.strip(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer.email],
            fail_silently=False,
        )
        
        # Сохраняем уведомление в БД
        EmailNotification.objects.create(
            order=order,
            recipient_email=order.customer.email,
            subject=subject,
            body=message
        )
        print(f"✓ Уведомление отправлено на {order.customer.email}")
        
    except Exception as e:
        print(f"✗ Ошибка отправки email: {e}")
