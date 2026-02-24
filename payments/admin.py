from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id', 'user', 'amount', 'payment_type',
        'status', 'payment_method', 'paid_at', 'created_at',
    ]
    list_filter = ['status', 'payment_type', 'currency']
    search_fields = ['transaction_id', 'user__email', 'user__username']
    readonly_fields = [
        'transaction_id', 'sessionkey', 'val_id',
        'bank_tran_id', 'gateway_response',
    ]