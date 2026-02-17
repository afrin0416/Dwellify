from rest_framework import serializers
from .models import (
    Category, Advertisement, AdvertisementImage,
    RentRequest, Favorite, Review
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']


class AdvertisementImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvertisementImage
        fields = ['id', 'image', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(
        source='user.username', read_only=True
    )
    user_email = serializers.CharField(
        source='user.email', read_only=True
    )

    class Meta:
        model = Review
        fields = [
            'id', 'advertisement', 'user', 'user_username',
            'user_email', 'rating', 'comment',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class AdvertisementListSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(
        source='owner.username', read_only=True
    )
    owner_email = serializers.CharField(
        source='owner.email', read_only=True
    )
    category_name = serializers.CharField(
        source='category.name', read_only=True
    )
    average_rating = serializers.FloatField(read_only=True)
    total_reviews = serializers.IntegerField(read_only=True)

    class Meta:
        model = Advertisement
        fields = [
            'id', 'owner', 'owner_username', 'owner_email',
            'title', 'description', 'category', 'category_name',
            'address', 'city', 'state', 'zip_code',
            'rent_amount', 'bedrooms', 'bathrooms', 'area_sqft',
            'image', 'status', 'is_rented',
            'average_rating', 'total_reviews',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'owner', 'status', 'is_rented',
            'created_at', 'updated_at'
        ]


class AdvertisementDetailSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(
        source='owner.username', read_only=True
    )
    owner_email = serializers.CharField(
        source='owner.email', read_only=True
    )
    category_name = serializers.CharField(
        source='category.name', read_only=True
    )
    average_rating = serializers.FloatField(read_only=True)
    total_reviews = serializers.IntegerField(read_only=True)
    images = AdvertisementImageSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Advertisement
        fields = [
            'id', 'owner', 'owner_username', 'owner_email',
            'title', 'description', 'category', 'category_name',
            'address', 'city', 'state', 'zip_code',
            'rent_amount', 'bedrooms', 'bathrooms', 'area_sqft',
            'image', 'images', 'status', 'is_rented',
            'average_rating', 'total_reviews', 'reviews',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'owner', 'status', 'is_rented',
            'created_at', 'updated_at'
        ]


class AdvertisementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = [
            'id', 'title', 'description', 'category',
            'address', 'city', 'state', 'zip_code',
            'rent_amount', 'bedrooms', 'bathrooms',
            'area_sqft', 'image'
        ]

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        validated_data['status'] = 'pending'
        return super().create(validated_data)


class AdvertisementApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = ['id', 'status']

    def validate_status(self, value):
        if value not in ['approved', 'rejected']:
            raise serializers.ValidationError(
                "Status must be 'approved' or 'rejected'."
            )
        return value


class RentRequestSerializer(serializers.ModelSerializer):
    requester_username = serializers.CharField(
        source='requester.username', read_only=True
    )
    requester_email = serializers.CharField(
        source='requester.email', read_only=True
    )
    advertisement_title = serializers.CharField(
        source='advertisement.title', read_only=True
    )

    class Meta:
        model = RentRequest
        fields = [
            'id', 'advertisement', 'advertisement_title',
            'requester', 'requester_username', 'requester_email',
            'message', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'requester', 'status',
            'created_at', 'updated_at'
        ]


class RentRequestActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['accept', 'reject'])


class FavoriteSerializer(serializers.ModelSerializer):
    advertisement_detail = AdvertisementListSerializer(
        source='advertisement', read_only=True
    )

    class Meta:
        model = Favorite
        fields = [
            'id', 'user', 'advertisement',
            'advertisement_detail', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class AdminStatisticsSerializer(serializers.Serializer):
    total_advertisements = serializers.IntegerField()
    total_approved = serializers.IntegerField()
    total_pending = serializers.IntegerField()
    total_rejected = serializers.IntegerField()
    total_rented = serializers.IntegerField()
    total_users = serializers.IntegerField()
    advertisements_this_month = serializers.IntegerField()
    advertisements_last_month = serializers.IntegerField()
    rent_requests_this_month = serializers.IntegerField()
    total_rent_requests = serializers.IntegerField()
    total_reviews = serializers.IntegerField()