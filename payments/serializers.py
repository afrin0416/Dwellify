from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_username = serializers.CharField(
        source='user.username', read_only=True)
    advertisement_title = serializers.CharField(
        source='advertisement.title', read_only=True
    )

    class Meta:
        model = Payment
        fields = [
            'id', 'transaction_id', 'user', 'user_email', 'user_username',
            'rent_request', 'advertisement', 'advertisement_title',
            'amount', 'payment_type', 'status', 'currency',
            'payment_method', 'card_type', 'bank_tran_id',
            'paid_at', 'created_at', 'updated_at',
        ]
        read_only_fields = fields


class PaymentInitiateSerializer(serializers.Serializer):
    rent_request_id = serializers.IntegerField()
    payment_type = serializers.ChoiceField(
        choices=['rent', 'security_deposit'], default='rent'
    )
