from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

from .models import User
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    UserListSerializer,
)
from .tokens import email_verification_token
from .permissions import IsAdmin


# REGISTRATION

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):

    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_verification_token.make_token(user)
        verification_url = (
            f"{settings.BACKEND_URL}/api/accounts/verify-email/{uid}/{token}/"
        )

        subject = 'Verify Your Email - House Rent Site'
        message = (
            f"Hi {user.username},\n\n"
            f"Welcome to House Rent Site!\n\n"
            f"Please click the following link to verify your email address:\n"
            f"{verification_url}\n\n"
            f"This link will activate your account so you can start using our platform.\n\n"
            f"If you didn't create an account, please ignore this email.\n\n"
            f"Thank you!\n"
            f"House Rent Site Team"
        )

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            email_sent = True
        except Exception as e:
            email_sent = False
            email_error = str(e)

        response_data = {
            'message': 'Registration successful. Please check your email to verify your account.',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            },
            'email_sent': email_sent,
        }

        if not email_sent:
            response_data['email_error'] = email_error
            response_data['verification_url'] = verification_url

        return Response(response_data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# EMAIL VERIFICATION

@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email(request, uidb64, token):

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response(
            {'error': 'Invalid verification link.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if email_verification_token.check_token(user, token):
        user.is_email_verified = True
        user.is_active = True
        user.save()
        return Response(
            {'message': 'Email verified successfully. You can now login.'},
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {'error': 'Invalid or expired verification link.'},
            status=status.HTTP_400_BAD_REQUEST
        )


#  RESEND VERIFICATION EMAIL

@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification_email(request):

    email = request.data.get('email')
    if not email:
        return Response(
            {'error': 'Email is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {'error': 'No account found with this email.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if user.is_email_verified:
        return Response(
            {'message': 'Email is already verified.'},
            status=status.HTTP_200_OK
        )

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)

    verification_url = (
        f"{settings.BACKEND_URL}/api/accounts/verify-email/{uid}/{token}/"
    )

    subject = 'Verify Your Email - House Rent Site (Resent)'
    message = (
        f"Hi {user.username},\n\n"
        f"Here is your new verification link:\n"
        f"{verification_url}\n\n"
        f"Thank you!\n"
        f"House Rent Site Team"
    )

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return Response(
            {'message': 'Verification email sent successfully.'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to send email: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


#  JWT LOGIN

class CustomTokenObtainPairView(TokenObtainPairView):

    serializer_class = CustomTokenObtainPairSerializer


#  JWT TOKEN REFRESH

class CustomTokenRefreshView(TokenRefreshView):
    pass


#  JWT LOGOUT
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):

    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response(
            {'message': 'Logged out successfully.'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': f'Logout failed: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )


#  LOGOUT ALL DEVICES

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_all(request):

    try:
        tokens = OutstandingToken.objects.filter(user=request.user)
        for token in tokens:
            try:
                BlacklistedToken.objects.get_or_create(token=token)
            except Exception:
                pass

        return Response(
            {'message': 'Logged out from all devices successfully.'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': f'Logout failed: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )


#  USER PROFILE

class UserProfileView(generics.RetrieveUpdateAPIView):

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


#  CHANGE PASSWORD

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):

    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'error': 'Old password is incorrect.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data['new_password'])
        user.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                'message': 'Password changed successfully.',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#  ADMIN - LIST USERS

class UserListView(generics.ListAPIView):
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return User.objects.all().order_by('-created_at')
