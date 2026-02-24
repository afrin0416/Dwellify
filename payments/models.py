from django.db import models
from django.conf import settings


class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = (
        ('rent', 'Monthly Rent'),
        ('security_deposit', 'Security Deposit'),
    )

    STATUS_CHOICES = (
        ('initiated', 'Initiated'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )

    transaction_id = models.CharField(max_length=120, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
    )
    rent_request = models.ForeignKey(
        'advertisements.RentRequest',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='payments',
    )
    advertisement = models.ForeignKey(
        'advertisements.Advertisement',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='payments',
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_type = models.CharField(
        max_length=20, choices=PAYMENT_TYPE_CHOICES)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='initiated')
    currency = models.CharField(max_length=10, default='BDT')

    # SSLCommerz fields
    sessionkey = models.CharField(max_length=300, blank=True, null=True)
    val_id = models.CharField(max_length=300, blank=True, null=True)
    bank_tran_id = models.CharField(max_length=300, blank=True, null=True)
    card_type = models.CharField(max_length=150, blank=True, null=True)
    payment_method = models.CharField(max_length=150, blank=True, null=True)
    gateway_response = models.JSONField(null=True, blank=True)

    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_id} — {self.status}"
