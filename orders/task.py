from .models import Order
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def order_created(order_id):
    order = Order.objects.get(id=order_id)
    subject = f'order nr.{order.id}'
    message = f'Dear {order.first_name}', \
              f'you have successfully created and order with {order.id}'
    mail_sent = send_mail(subject, message, 'admin@myshop.com', [order.email])

    return mail_sent


