import django_filters
from .models import Advertisement


class AdvertisementFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name='category__id')
    category_name = django_filters.CharFilter(
        field_name='category__name', lookup_expr='icontains'
    )
    city = django_filters.CharFilter(
        field_name='city', lookup_expr='icontains'
    )
    min_rent = django_filters.NumberFilter(
        field_name='rent_amount', lookup_expr='gte'
    )
    max_rent = django_filters.NumberFilter(
        field_name='rent_amount', lookup_expr='lte'
    )
    bedrooms = django_filters.NumberFilter(field_name='bedrooms')
    min_bedrooms = django_filters.NumberFilter(
        field_name='bedrooms', lookup_expr='gte'
    )
    bathrooms = django_filters.NumberFilter(field_name='bathrooms')
    is_rented = django_filters.BooleanFilter(field_name='is_rented')

    class Meta:
        model = Advertisement
        fields = [
            'category', 'category_name', 'city',
            'min_rent', 'max_rent', 'bedrooms',
            'min_bedrooms', 'bathrooms', 'is_rented'
        ]