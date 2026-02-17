from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db.models import Avg, Count
from datetime import timedelta

from .models import (
    Category, Advertisement, AdvertisementImage,
    RentRequest, Favorite, Review
)
from .serializers import (
    CategorySerializer,
    AdvertisementListSerializer,
    AdvertisementDetailSerializer,
    AdvertisementCreateSerializer,
    AdvertisementApprovalSerializer,
    RentRequestSerializer,
    RentRequestActionSerializer,
    FavoriteSerializer,
    ReviewSerializer,
    AdminStatisticsSerializer,
)
from .filters import AdvertisementFilter
from .permissions import IsAdmin, IsAdvertisementOwner, IsAdvertisementOwnerOrAdmin
from accounts.models import User


#  CATEGORY VIEWS

class CategoryListCreateView(generics.ListCreateAPIView):
    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdmin()]
        return [AllowAny()]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdmin()]


#  ADVERTISEMENT VIEWS

class AdvertisementListView(generics.ListAPIView):
    
    serializer_class = AdvertisementListSerializer
    permission_classes = [AllowAny]
    filterset_class = AdvertisementFilter
    search_fields = ['title', 'description', 'city', 'address']
    ordering_fields = ['rent_amount', 'created_at', 'bedrooms']

    def get_queryset(self):
        return Advertisement.objects.filter(status='approved')


class AdvertisementCreateView(generics.CreateAPIView):
    
    serializer_class = AdvertisementCreateSerializer
    permission_classes = [IsAuthenticated]


class AdvertisementDetailView(generics.RetrieveAPIView):
    
    serializer_class = AdvertisementDetailSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and (
            user.role == 'admin' or user.is_superuser
        ):
            return Advertisement.objects.all()
        if user.is_authenticated:
            return (
                Advertisement.objects.filter(status='approved') |
                Advertisement.objects.filter(owner=user)
            )
        return Advertisement.objects.filter(status='approved')


class AdvertisementUpdateView(generics.UpdateAPIView):
    
    serializer_class = AdvertisementCreateSerializer
    permission_classes = [IsAuthenticated, IsAdvertisementOwner]

    def get_queryset(self):
        return Advertisement.objects.filter(owner=self.request.user)


class AdvertisementDeleteView(generics.DestroyAPIView):
    
    serializer_class = AdvertisementListSerializer
    permission_classes = [IsAuthenticated, IsAdvertisementOwnerOrAdmin]
    queryset = Advertisement.objects.all()


class MyAdvertisementsView(generics.ListAPIView):
    
    serializer_class = AdvertisementListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Advertisement.objects.filter(owner=self.request.user)


#  ADMIN ADVERTISEMENT VIEWS 

class AdminPendingAdvertisementsView(generics.ListAPIView):
    
    serializer_class = AdvertisementListSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return Advertisement.objects.filter(status='pending')


class AdminAllAdvertisementsView(generics.ListAPIView):
    
    serializer_class = AdvertisementListSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filterset_class = AdvertisementFilter

    def get_queryset(self):
        return Advertisement.objects.all()


@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_approve_advertisement(request, pk):
    
    try:
        advertisement = Advertisement.objects.get(pk=pk)
    except Advertisement.DoesNotExist:
        return Response(
            {'error': 'Advertisement not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = AdvertisementApprovalSerializer(
        advertisement, data=request.data, partial=True
    )
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                'message': (
                    f'Advertisement has been '
                    f'{serializer.validated_data["status"]}.'
                ),
                'advertisement': AdvertisementListSerializer(
                    advertisement
                ).data
            },
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_delete_advertisement(request, pk):
    
    try:
        advertisement = Advertisement.objects.get(pk=pk)
    except Advertisement.DoesNotExist:
        return Response(
            {'error': 'Advertisement not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    advertisement.delete()
    return Response(
        {'message': 'Advertisement deleted successfully.'},
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_statistics(request):
    
    now = timezone.now()
    current_month_start = now.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    last_month_start = (
        current_month_start - timedelta(days=1)
    ).replace(day=1)

    stats = {
        'total_advertisements': Advertisement.objects.count(),
        'total_approved': Advertisement.objects.filter(
            status='approved'
        ).count(),
        'total_pending': Advertisement.objects.filter(
            status='pending'
        ).count(),
        'total_rejected': Advertisement.objects.filter(
            status='rejected'
        ).count(),
        'total_rented': Advertisement.objects.filter(
            is_rented=True
        ).count(),
        'total_users': User.objects.count(),
        'advertisements_this_month': Advertisement.objects.filter(
            created_at__gte=current_month_start
        ).count(),
        'advertisements_last_month': Advertisement.objects.filter(
            created_at__gte=last_month_start,
            created_at__lt=current_month_start
        ).count(),
        'rent_requests_this_month': RentRequest.objects.filter(
            created_at__gte=current_month_start
        ).count(),
        'total_rent_requests': RentRequest.objects.count(),
        'total_reviews': Review.objects.count(),
    }

    serializer = AdminStatisticsSerializer(stats)
    return Response(serializer.data, status=status.HTTP_200_OK)


#  RENT REQUEST VIEWS 

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_rent_request(request, advertisement_id):
    
    try:
        advertisement = Advertisement.objects.get(pk=advertisement_id)
    except Advertisement.DoesNotExist:
        return Response(
            {'error': 'Advertisement not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if advertisement.status != 'approved':
        return Response(
            {'error': 'This advertisement is not available.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if advertisement.is_rented:
        return Response(
            {
                'error': (
                    'This property has already been rented. '
                    'No more requests can be sent.'
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if advertisement.owner == request.user:
        return Response(
            {
                'error': (
                    'You cannot send a rent request '
                    'to your own advertisement.'
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if RentRequest.objects.filter(
        advertisement=advertisement, requester=request.user
    ).exists():
        return Response(
            {
                'error': (
                    'You have already sent a rent request '
                    'for this advertisement.'
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    rent_request = RentRequest.objects.create(
        advertisement=advertisement,
        requester=request.user,
        message=request.data.get('message', '')
    )

    serializer = RentRequestSerializer(rent_request)
    return Response(
        {
            'message': 'Rent request sent successfully.',
            'rent_request': serializer.data
        },
        status=status.HTTP_201_CREATED
    )


class MyRentRequestsView(generics.ListAPIView):
    
    serializer_class = RentRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RentRequest.objects.filter(requester=self.request.user)


class ReceivedRentRequestsView(generics.ListAPIView):
    
    serializer_class = RentRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RentRequest.objects.filter(
            advertisement__owner=self.request.user
        )


class AdvertisementRentRequestsView(generics.ListAPIView):
    
    serializer_class = RentRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        advertisement_id = self.kwargs['advertisement_id']
        return RentRequest.objects.filter(
            advertisement_id=advertisement_id,
            advertisement__owner=self.request.user
        )


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def handle_rent_request(request, rent_request_id):
    
    try:
        rent_request = RentRequest.objects.get(pk=rent_request_id)
    except RentRequest.DoesNotExist:
        return Response(
            {'error': 'Rent request not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if rent_request.advertisement.owner != request.user:
        return Response(
            {'error': 'You are not authorized to handle this rent request.'},
            status=status.HTTP_403_FORBIDDEN
        )

    if rent_request.advertisement.is_rented:
        return Response(
            {
                'error': (
                    'This advertisement has already been rented. '
                    'No more actions allowed.'
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = RentRequestActionSerializer(data=request.data)
    if serializer.is_valid():
        action_type = serializer.validated_data['action']

        if action_type == 'accept':
            rent_request.status = 'accepted'
            rent_request.save()

            advertisement = rent_request.advertisement
            advertisement.is_rented = True
            advertisement.save()

            RentRequest.objects.filter(
                advertisement=advertisement,
                status='pending'
            ).exclude(pk=rent_request.pk).update(status='rejected')

            return Response(
                {
                    'message': (
                        'Rent request accepted. '
                        'The property is now marked as rented.'
                    ),
                    'rent_request': RentRequestSerializer(
                        rent_request
                    ).data
                },
                status=status.HTTP_200_OK
            )

        elif action_type == 'reject':
            rent_request.status = 'rejected'
            rent_request.save()

            return Response(
                {
                    'message': 'Rent request rejected.',
                    'rent_request': RentRequestSerializer(
                        rent_request
                    ).data
                },
                status=status.HTTP_200_OK
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# FAVORITES VIEWS

class FavoriteListView(generics.ListAPIView):
    
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_favorite(request, advertisement_id):
    
    try:
        advertisement = Advertisement.objects.get(pk=advertisement_id)
    except Advertisement.DoesNotExist:
        return Response(
            {'error': 'Advertisement not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if advertisement.status != 'approved':
        return Response(
            {'error': 'This advertisement is not available.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        advertisement=advertisement
    )

    if not created:
        return Response(
            {'message': 'Advertisement is already in your favorites.'},
            status=status.HTTP_200_OK
        )

    serializer = FavoriteSerializer(favorite)
    return Response(
        {
            'message': 'Advertisement added to favorites.',
            'favorite': serializer.data
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_favorite(request, advertisement_id):
    
    try:
        favorite = Favorite.objects.get(
            user=request.user,
            advertisement_id=advertisement_id
        )
    except Favorite.DoesNotExist:
        return Response(
            {'error': 'This advertisement is not in your favorites.'},
            status=status.HTTP_404_NOT_FOUND
        )

    favorite.delete()
    return Response(
        {'message': 'Advertisement removed from favorites.'},
        status=status.HTTP_200_OK
    )


#  REVIEW VIEWS 

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request, advertisement_id):
    
    try:
        advertisement = Advertisement.objects.get(pk=advertisement_id)
    except Advertisement.DoesNotExist:
        return Response(
            {'error': 'Advertisement not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if advertisement.status != 'approved':
        return Response(
            {'error': 'This advertisement is not available for review.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if Review.objects.filter(
        advertisement=advertisement, user=request.user
    ).exists():
        return Response(
            {'error': 'You have already reviewed this advertisement.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = ReviewSerializer(data={
        **request.data,
        'advertisement': advertisement.id
    })
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(
            {
                'message': 'Review submitted successfully.',
                'review': serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_review(request, review_id):
    
    try:
        review = Review.objects.get(pk=review_id, user=request.user)
    except Review.DoesNotExist:
        return Response(
            {'error': 'Review not found or you are not the author.'},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = ReviewSerializer(review, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                'message': 'Review updated successfully.',
                'review': serializer.data
            },
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review(request, review_id):
    
    try:
        if request.user.role == 'admin' or request.user.is_superuser:
            review = Review.objects.get(pk=review_id)
        else:
            review = Review.objects.get(pk=review_id, user=request.user)
    except Review.DoesNotExist:
        return Response(
            {'error': 'Review not found or you are not the author.'},
            status=status.HTTP_404_NOT_FOUND
        )

    review.delete()
    return Response(
        {'message': 'Review deleted successfully.'},
        status=status.HTTP_200_OK
    )


class AdvertisementReviewsView(generics.ListAPIView):
    
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Review.objects.filter(
            advertisement_id=self.kwargs['advertisement_id']
        )