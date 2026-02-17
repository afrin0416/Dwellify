from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Advertisement(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='advertisements'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='advertisements'
    )
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    bedrooms = models.PositiveIntegerField(default=1)
    bathrooms = models.PositiveIntegerField(default=1)
    area_sqft = models.PositiveIntegerField(blank=True, null=True)
    image = models.ImageField(
        upload_to='advertisement_images/', blank=True, null=True
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='pending'
    )
    is_rented = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.owner.username}"

    @property
    def average_rating(self):
        ratings = self.reviews.all()
        if ratings.exists():
            return round(
                ratings.aggregate(models.Avg('rating'))['rating__avg'], 2
            )
        return 0

    @property
    def total_reviews(self):
        return self.reviews.count()


class AdvertisementImage(models.Model):
    advertisement = models.ForeignKey(
        Advertisement,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='advertisement_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.advertisement.title}"


class RentRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )

    advertisement = models.ForeignKey(
        Advertisement,
        on_delete=models.CASCADE,
        related_name='rent_requests'
    )
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rent_requests'
    )
    message = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['advertisement', 'requester']

    def __str__(self):
        return (
            f"{self.requester.username} -> "
            f"{self.advertisement.title} ({self.status})"
        )


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    advertisement = models.ForeignKey(
        Advertisement,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'advertisement']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.advertisement.title}"


class Review(models.Model):
    advertisement = models.ForeignKey(
        Advertisement,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['advertisement', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.advertisement.title} ({self.rating}/5)"
        )