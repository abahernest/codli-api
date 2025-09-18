from django.db import models

from events.models import CURRENCY_CHOICES
from users.models import User
from events.models import Event

CHOICES_FOR_STATUS = [
    ("PENDING", "Pending Payment"),
    ("SUCCESS", "Successful Payment"),
    ("FAILED", "Failed Payment")
]

CHOICES_FOR_PAYMENT_METHOD = [
    ("PAYSTACK", "Paystack Payment Service")
]

class TransactionLog(models.Model):

    event_name   = models.CharField(max_length=256, blank=True, null=True)
    reference       = models.CharField(max_length=256)
    event        = models.ForeignKey(Event, on_delete=models.CASCADE)
    user           = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transaction_logs_creator_id")
    payed_by          = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transaction_logs_consumer_id")
    amount          = models.PositiveBigIntegerField()
    currency        = models.CharField(max_length=10, default="NGN", choices=CURRENCY_CHOICES)
    fee             = models.PositiveBigIntegerField()
    quantity = models.IntegerField()
    status = models.CharField(
        max_length=256,
        choices=CHOICES_FOR_STATUS,
        default=CHOICES_FOR_STATUS[0][0])
    payment_method      = models.CharField(
        max_length=256, 
        choices= CHOICES_FOR_PAYMENT_METHOD,
        default = CHOICES_FOR_PAYMENT_METHOD[0][0])
    error_message_from_payment_service = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transaction_logs"

        

