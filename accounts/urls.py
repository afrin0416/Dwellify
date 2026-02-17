from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Registration & Verification
    path('register/', views.register, name='register'),
    path('verify-email/<str:uidb64>/<str:token>/', views.verify_email, name='verify-email'),
    path('resend-verification/', views.resend_verification_email, name='resend-verification'),

    # JWT Authentication
    path('login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', views.CustomTokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', views.logout_view, name='logout'),
    path('logout-all/', views.logout_all, name='logout-all'),

    # Profile Management
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('change-password/', views.change_password, name='change-password'),

    # Admin
    path('users/', views.UserListView.as_view(), name='user-list'),
]