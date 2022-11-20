from typing import List

import requests
from requests import Response
from django.urls import reverse
from django.db import transaction

from payment.models import PaymentInfo, ErrorMessage


class PaymentService:
    """Класс для работы с оплатой заказов"""

    @staticmethod
    def get_wait_list() -> List[PaymentInfo]:
        """Функция возвращает список заказов, поставленных на оплату"""
        return PaymentInfo.objects.filter(status="w").select_related("order").prefetch_related("order__order_goods")

    @staticmethod
    def try_to_pay(payment_info: PaymentInfo) -> Response:
        """Функция делает запрос к сервису оплаты, возвращает ответ от сервиса"""
        total_cost = str(payment_info.order.all_goods_price + payment_info.order.cost_delivery)

        url = "http://0.0.0.0:8000" + reverse(
            viewname="payment:pay",
            kwargs={"card_number": payment_info.cart_number, "cost": total_cost},
        )

        return requests.get(url)

    @staticmethod
    @transaction.atomic
    def update_payment_info(response: Response, payment_info: PaymentInfo) -> None:
        """Функция обрабатывает ответ от сервиса оплаты"""
        response_data = response.json()

        if response.status_code == 201:
            PaymentService.update_after_success_pay(payment_info)
        else:
            PaymentService.update_after_fail_pay(payment_info, response_data["error"])

    @staticmethod
    def update_after_success_pay(payment_info: PaymentInfo) -> None:
        """Функция выставляет заказу статус оплачен и убирает заказ из таблицы неоплаченных заказов"""
        order = payment_info.order
        order.paid = True
        order.save(update_fields=["paid"])

        payment_info.delete()

    @staticmethod
    def update_after_fail_pay(payment_info: PaymentInfo, error_message: str) -> None:
        """Функция выставляет заказу статус не оплачен и добавляет сообщение с текстом ошибки"""
        payment_info.status = "f"
        payment_info.save()
        ErrorMessage.objects.update_or_create(payment_info=payment_info, defaults={"message": error_message})

    @staticmethod
    def add_order_to_payment_queue(order_id: int, cart_number: int):
        """Функция добавляет заказ в очередь на оплату"""
        PaymentInfo.objects.create(order_id=order_id, cart_number=cart_number)
