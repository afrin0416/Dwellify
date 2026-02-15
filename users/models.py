# from django.contrib.auth.models import AbstractUser
# from django.db import models
# from django.utils.crypto import get_random_string

# class CustomUser(AbstractUser):
#     ROLE_CHOICES = (
#         ('admin', 'Admin'),
#         ('user', 'User'),
#     )
#     email = models.EmailField(unique=True)
#     is_verified = models.BooleanField(default=False)
#     role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
#     verification_code = models.CharField(max_length=50, blank=True, null=True)

#     def generate_verification_code(self):
#         code = get_random_string(length=32)
#         self.verification_code = code
#         self.save()
#         return code


from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # 🔥 hashes password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)  # inactive until verified
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=100, blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if not self.verification_code:
            self.verification_code = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
