# from django.urls import path
# from .views import RegisterView, VerifyEmailView, LoginView, LogoutView, ProfileView

# urlpatterns = [
#     path('register/', RegisterView.as_view(), name='register'),
#     path('verify-email/<str:code>/', VerifyEmailView.as_view(), name='verify-email'),
#     path('login/', LoginView.as_view(), name='login'),
#     path('logout/', LogoutView.as_view(), name='logout'),
#     path('profile/', ProfileView.as_view(), name='profile'),
# ]


from django.urls import path
from .views import RegisterView, VerifyEmailView, LoginView, LogoutView, ProfileView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('verify-email/<str:code>/', VerifyEmailView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('profile/', ProfileView.as_view()),
]
