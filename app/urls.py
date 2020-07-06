from django.urls import path
from rest_framework.routers import DefaultRouter

from app import views

urlpatterns = [
    path('user/account/<str:account>', views.AppViewSet.as_view({'get': 'get_by_account'})),
    path('shares/<int:share_num>', views.UserViewSet.as_view({'get': 'get_shares'})),
    path('favorites/<str:user_id>', views.UserViewSet.as_view({'get': 'get_favorites'})),
    path('share_info/<str:user_id>/<str:photo_id>', views.UserViewSet.as_view({'get': 'get_share_info'})),
    path('star', views.UserViewSet.as_view({'post': 'star'})),
    path('comment', views.UserViewSet.as_view({'post': 'comment'})),
]
