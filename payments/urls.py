from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Initiate
    path('initiate/', views.initiate_payment, name='initiate'),

    # SSLCommerz callbacks (plain Django views)
    path('success/', views.payment_success_callback, name='success'),
    path('fail/', views.payment_fail_callback, name='fail'),
    path('cancel/', views.payment_cancel_callback, name='cancel'),
    path('ipn/', views.payment_ipn_callback, name='ipn'),

    # User endpoints
    path('history/', views.payment_history, name='history'),
    path('<int:pk>/', views.payment_detail, name='detail'),
    path('tran/<str:tran_id>/', views.payment_by_tran_id, name='by-tran-id'),

    # Admin
    path('admin/all/', views.AdminPaymentListView.as_view(), name='admin-all'),
    path('admin/<int:pk>/refund/', views.admin_refund, name='admin-refund'),
]