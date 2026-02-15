# from rest_framework import generics, status
# from rest_framework.response import Response
# from rest_framework.permissions import AllowAny, IsAuthenticated
# from django.contrib.auth import authenticate
# from django.core.mail import send_mail
# from django.conf import settings
# from rest_framework.views import APIView
# from rest_framework_simplejwt.tokens import RefreshToken
# from .models import CustomUser
# from .serializers import RegisterSerializer, UserSerializer, LoginSerializer

# # Registration
# class RegisterView(generics.CreateAPIView):
#     queryset = CustomUser.objects.all()
#     serializer_class = RegisterSerializer
#     permission_classes = [AllowAny]

#     def perform_create(self, serializer):
#         user = serializer.save()
#         verification_link = f"http://localhost:8000/api/users/verify-email/{user.verification_code}/"
#         print(f"Verification link: {verification_link}")  # For testing purposes
#         send_mail(
#             'Verify your account',
#             f'Click the link to verify your account: {verification_link}',
#             settings.DEFAULT_FROM_EMAIL,
#             [user.email],
#             fail_silently=False,
#         )

# # Email verification
# class VerifyEmailView(APIView):
#     permission_classes = [AllowAny]

#     def get(self, request, code):
#         try:
#             user = CustomUser.objects.get(verification_code=code)
#             user.is_active = True
#             user.is_verified = True
#             user.verification_code = ''
#             user.save()
#             return Response({"message": "Email verified successfully!"}, status=200)
#         except CustomUser.DoesNotExist:
#             return Response({"error": "Invalid verification code"}, status=400)

# # JWT Login
# class LoginView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         email = serializer.validated_data['email']
#         password = serializer.validated_data['password']
#         user = authenticate(request, username=email, password=password)
#         if user is not None and user.is_verified:
#             refresh = RefreshToken.for_user(user)
#             return Response({
#                 "refresh": str(refresh),
#                 "access": str(refresh.access_token),
#                 "user": UserSerializer(user).data
#             })
#         return Response({"error": "Invalid credentials or email not verified"}, status=401)

# # JWT Logout
# class LogoutView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         try:
#             token = RefreshToken(request.data.get("refresh"))
#             token.blacklist()
#             return Response({"message": "Logout successful"}, status=205)
#         except Exception as e:
#             return Response({"error": str(e)}, status=400)

# # Profile management
# class ProfileView(generics.RetrieveUpdateAPIView):
#     queryset = CustomUser.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [IsAuthenticated]

#     def get_object(self):
#         return self.request.user


from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import RegisterSerializer, UserSerializer, LoginSerializer


# 🔹 Register
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()

        verification_link = f"http://localhost:8000/api/users/verify-email/{user.verification_code}/"

        print(f"Verification link: {verification_link}")

        send_mail(
            'Verify your account',
            f'Click the link to verify your account: {verification_link}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


# 🔹 Email Verification
class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, code):
        try:
            user = CustomUser.objects.get(verification_code=code)
            user.is_active = True
            user.is_verified = True
            user.verification_code = ''
            user.save()

            return Response({"message": "Email verified successfully!"})
        except CustomUser.DoesNotExist:
            return Response({"error": "Invalid verification code"}, status=400)


# 🔹 Login
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = CustomUser.objects.filter(email=email).first()

        if user and user.check_password(password) and user.is_verified:
            refresh = RefreshToken.for_user(user)

            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserSerializer(user).data
            })

        return Response(
            {"error": "Invalid credentials or email not verified"},
            status=status.HTTP_401_UNAUTHORIZED
        )


# 🔹 Logout
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Logout successful"}, status=205)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


# 🔹 Profile
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
