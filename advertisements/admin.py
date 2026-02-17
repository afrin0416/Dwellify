from django.contrib import admin
from .models import (
    Category, Advertisement, AdvertisementImage,
    RentRequest, Favorite, Review
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'owner', 'category', 'rent_amount',
        'status', 'is_rented', 'created_at'
    ]
    list_filter = ['status', 'is_rented', 'category', 'city']
    search_fields = ['title', 'description', 'city', 'address']
    list_editable = ['status']


@admin.register(AdvertisementImage)
class AdvertisementImageAdmin(admin.ModelAdmin):
    list_display = ['advertisement', 'created_at']


@admin.register(RentRequest)
class RentRequestAdmin(admin.ModelAdmin):
    list_display = ['requester', 'advertisement', 'status', 'created_at']
    list_filter = ['status']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'advertisement', 'created_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'advertisement', 'rating', 'created_at']
    list_filter = ['rating']