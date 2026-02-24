import time
import uuid
from decimal import Decimal

from django.conf import settings as django_settings
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.decorators import method_decorator

from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from sslcommerz_lib import SSLCOMMERZ

from .models import Payment
from .serializers import PaymentSerializer, PaymentInitiateSerializer
from advertisements.models import RentRequest
from advertisements.permissions import IsAdmin


# ─── helpers ───────────────────────────────────────────────

def _sslcz():
    return SSLCOMMERZ({
        'store_id': django_settings.SSLCOMMERZ_STORE_ID,
        'store_pass': django_settings.SSLCOMMERZ_STORE_PASSWORD,
        'issandbox': django_settings.SSLCOMMERZ_IS_SANDBOX,
    })


def _tran_id(user_id):
    return f"RENT_{user_id}_{int(time.time())}_{uuid.uuid4().hex[:8]}"


# ─── Initiate Payment ─────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    ser = PaymentInitiateSerializer(data=request.data)
    ser.is_valid(raise_exception=True)

    try:
        rr = RentRequest.objects.select_related('advertisement').get(
            id=ser.validated_data['rent_request_id']
        )
    except RentRequest.DoesNotExist:
        return Response({'error': 'Rent request not found.'},
                        status=status.HTTP_404_NOT_FOUND)

    if rr.status != 'accepted':
        return Response({'error': 'Rent request must be accepted first.'},
                        status=status.HTTP_400_BAD_REQUEST)
    if rr.requester != request.user:
        return Response({'error': 'Not your rent request.'},
                        status=status.HTTP_403_FORBIDDEN)

    ptype = ser.validated_data['payment_type']
    ad = rr.advertisement
    amount = ad.rent_amount * Decimal('2') if ptype == 'security_deposit' else ad.rent_amount

    if Payment.objects.filter(rent_request=rr, payment_type=ptype, status='completed').exists():
        return Response({'error': f'{ptype} already paid.'}, status=status.HTTP_400_BAD_REQUEST)

    tran = _tran_id(request.user.id)
    payment = Payment.objects.create(
        transaction_id=tran, user=request.user,
        rent_request=rr, advertisement=ad,
        amount=amount, payment_type=ptype,
    )

    backend = django_settings.BACKEND_URL
    post_body = {
        'total_amount': float(amount),
        'currency': 'BDT',
        'tran_id': tran,
        'success_url': f'{backend}/api/payments/success/',
        'fail_url': f'{backend}/api/payments/fail/',
        'cancel_url': f'{backend}/api/payments/cancel/',
        'ipn_url': f'{backend}/api/payments/ipn/',
        'cus_name': request.user.get_full_name() or request.user.username,
        'cus_email': request.user.email,
        'cus_phone': request.user.phone_number or '01700000000',
        'cus_add1': request.user.address or 'N/A',
        'cus_city': ad.city or 'Dhaka',
        'cus_country': 'Bangladesh',
        'shipping_method': 'NO',
        'product_name': ad.title,
        'product_category': ptype,
        'product_profile': 'general',
        'num_of_item': 1,
        'emi_option': 0,
        'multi_card_name': '',
    }

    resp = _sslcz().createSession(post_body)

    if resp.get('status') == 'SUCCESS':
        payment.sessionkey = resp.get('sessionkey', '')
        payment.status = 'pending'
        payment.save()
        return Response({
            'payment_id': payment.id,
            'transaction_id': tran,
            'amount': str(amount),
            'gateway_url': resp['GatewayPageURL'],
        })

    payment.status = 'failed'
    payment.gateway_response = resp
    payment.save()
    return Response({'error': 'Payment session failed.',
                     'details': resp.get('failedreason', '')},
                    status=status.HTTP_502_BAD_GATEWAY)


# ─── SSLCommerz Callbacks (plain Django views) ────────────

def _extract(post):
    """Safely convert QueryDict / dict to a regular dict for JSON storage."""
    try:
        return dict(post)
    except Exception:
        return {}


@csrf_exempt
def payment_success_callback(request):
    data = request.POST
    tran_id = data.get('tran_id', '')
    val_id = data.get('val_id', '')
    fe = django_settings.FRONTEND_URL

    if not tran_id:
        return HttpResponseRedirect(f'{fe}/payment/fail?error=missing_tran_id')

    try:
        payment = Payment.objects.get(transaction_id=tran_id)
    except Payment.DoesNotExist:
        return HttpResponseRedirect(f'{fe}/payment/fail?error=not_found')

    if payment.status == 'completed':
        return HttpResponseRedirect(f'{fe}/payment/success?tran_id={tran_id}')

    if val_id:
        try:
            validation = _sslcz().validationTransaction(val_id)
        except Exception:
            validation = {}

        valid_status = validation.get('status', '')
        if valid_status in ('VALID', 'VALIDATED'):
            validated_amount = Decimal(str(validation.get('amount', '0')))
            if validated_amount >= payment.amount:
                payment.status = 'completed'
                payment.val_id = val_id
                payment.bank_tran_id = data.get('bank_tran_id', '')
                payment.card_type = data.get('card_type', '')
                payment.payment_method = data.get('card_issuer', '')
                payment.gateway_response = _extract(data)
                payment.paid_at = timezone.now()
                payment.save()
                return HttpResponseRedirect(f'{fe}/payment/success?tran_id={tran_id}')

    payment.status = 'failed'
    payment.gateway_response = _extract(data)
    payment.save()
    return HttpResponseRedirect(f'{fe}/payment/fail?tran_id={tran_id}&error=validation')


@csrf_exempt
def payment_fail_callback(request):
    tran_id = request.POST.get('tran_id', '')
    if tran_id:
        Payment.objects.filter(transaction_id=tran_id).exclude(
            status='completed'
        ).update(status='failed', gateway_response=_extract(request.POST))
    return HttpResponseRedirect(
        f'{django_settings.FRONTEND_URL}/payment/fail?tran_id={tran_id}'
    )


@csrf_exempt
def payment_cancel_callback(request):
    tran_id = request.POST.get('tran_id', '')
    if tran_id:
        Payment.objects.filter(transaction_id=tran_id).exclude(
            status='completed'
        ).update(status='cancelled', gateway_response=_extract(request.POST))
    return HttpResponseRedirect(
        f'{django_settings.FRONTEND_URL}/payment/cancel?tran_id={tran_id}'
    )


@csrf_exempt
def payment_ipn_callback(request):
    """Server-to-server IPN — most reliable."""
    data = request.POST
    tran_id = data.get('tran_id', '')
    val_id = data.get('val_id', '')

    if not tran_id:
        from django.http import JsonResponse
        return JsonResponse({'error': 'no tran_id'}, status=400)

    try:
        payment = Payment.objects.get(transaction_id=tran_id)
    except Payment.DoesNotExist:
        from django.http import JsonResponse
        return JsonResponse({'error': 'not found'}, status=404)

    if payment.status == 'completed':
        from django.http import JsonResponse
        return JsonResponse({'msg': 'already completed'})

    ssl_status = data.get('status', '')
    if ssl_status in ('VALID', 'VALIDATED') and val_id:
        try:
            v = _sslcz().validationTransaction(val_id)
        except Exception:
            v = {}
        if v.get('status') in ('VALID', 'VALIDATED'):
            validated_amount = Decimal(str(v.get('amount', '0')))
            if validated_amount >= payment.amount:
                payment.status = 'completed'
                payment.val_id = val_id
                payment.bank_tran_id = data.get('bank_tran_id', '')
                payment.card_type = data.get('card_type', '')
                payment.payment_method = data.get('card_issuer', '')
                payment.gateway_response = _extract(data)
                payment.paid_at = timezone.now()
                payment.save()
    elif ssl_status == 'FAILED':
        payment.status = 'failed'
        payment.gateway_response = _extract(data)
        payment.save()
    elif ssl_status == 'CANCELLED':
        payment.status = 'cancelled'
        payment.gateway_response = _extract(data)
        payment.save()

    from django.http import JsonResponse
    return JsonResponse({'msg': 'processed'})


# ─── DRF API Views ────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_history(request):
    qs = Payment.objects.filter(user=request.user)
    return Response(PaymentSerializer(qs, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_detail(request, pk):
    try:
        p = Payment.objects.get(pk=pk)
    except Payment.DoesNotExist:
        return Response({'error': 'Not found.'}, status=404)
    if p.user != request.user and not (
        request.user.role == 'admin' or request.user.is_superuser
    ):
        return Response({'error': 'Forbidden.'}, status=403)
    return Response(PaymentSerializer(p).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_by_tran_id(request, tran_id):
    try:
        p = Payment.objects.get(transaction_id=tran_id)
    except Payment.DoesNotExist:
        return Response({'error': 'Not found.'}, status=404)
    if p.user != request.user and not (
        request.user.role == 'admin' or request.user.is_superuser
    ):
        return Response({'error': 'Forbidden.'}, status=403)
    return Response(PaymentSerializer(p).data)


class AdminPaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        qs = Payment.objects.all()
        s = self.request.query_params.get('status')
        if s:
            qs = qs.filter(status=s)
        return qs


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_refund(request, pk):
    try:
        p = Payment.objects.get(pk=pk)
    except Payment.DoesNotExist:
        return Response({'error': 'Not found.'}, status=404)
    if p.status != 'completed':
        return Response({'error': 'Only completed payments can be refunded.'},
                        status=400)
    p.status = 'refunded'
    p.save()
    return Response({'message': 'Refunded.', 'payment': PaymentSerializer(p).data})