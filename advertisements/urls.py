from django.urls import path
from . import views

app_name = 'advertisements'

urlpatterns = [
    # Categories
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),

    # Advertisements - Public
    path('', views.AdvertisementListView.as_view(), name='advertisement-list'),
    path('<int:pk>/', views.AdvertisementDetailView.as_view(), name='advertisement-detail'),

    # Advertisements - Authenticated Users
    path('create/', views.AdvertisementCreateView.as_view(), name='advertisement-create'),
    path('<int:pk>/update/', views.AdvertisementUpdateView.as_view(), name='advertisement-update'),
    path('<int:pk>/delete/', views.AdvertisementDeleteView.as_view(), name='advertisement-delete'),
    path('my-advertisements/', views.MyAdvertisementsView.as_view(), name='my-advertisements'),

    # Admin - Advertisements
    path('admin/pending/', views.AdminPendingAdvertisementsView.as_view(), name='admin-pending'),
    path('admin/all/', views.AdminAllAdvertisementsView.as_view(), name='admin-all'),
    path('admin/<int:pk>/approve/', views.admin_approve_advertisement, name='admin-approve'),
    path('admin/<int:pk>/delete/', views.admin_delete_advertisement, name='admin-delete'),
    path('admin/statistics/', views.admin_statistics, name='admin-statistics'),

    # Rent Requests
    path('<int:advertisement_id>/rent-request/', views.send_rent_request, name='send-rent-request'),
    path('<int:advertisement_id>/rent-requests/', views.AdvertisementRentRequestsView.as_view(), name='advertisement-rent-requests'),
    path('my-rent-requests/', views.MyRentRequestsView.as_view(), name='my-rent-requests'),
    path('received-rent-requests/', views.ReceivedRentRequestsView.as_view(), name='received-rent-requests'),
    path('rent-request/<int:rent_request_id>/action/', views.handle_rent_request, name='handle-rent-request'),

    # Favorites
    path('favorites/', views.FavoriteListView.as_view(), name='favorite-list'),
    path('<int:advertisement_id>/favorite/', views.add_favorite, name='add-favorite'),
    path('<int:advertisement_id>/unfavorite/', views.remove_favorite, name='remove-favorite'),

    # Reviews
    path('<int:advertisement_id>/review/', views.create_review, name='create-review'),
    path('<int:advertisement_id>/reviews/', views.AdvertisementReviewsView.as_view(), name='advertisement-reviews'),
    path('review/<int:review_id>/update/', views.update_review, name='update-review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete-review'),
]