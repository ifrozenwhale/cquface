from django.urls import path
from rest_framework.routers import DefaultRouter

from account import views

router = DefaultRouter()
router.register('user', views.UserViewSet)

urlpatterns = [
    # path('', include(router.urls)),
    path('user/account/<str:account>', views.UserViewSet.as_view({'get': 'get_by_account'})),
    path('user/', views.UserViewSet.as_view({'get': 'get_all'})),
    path('user', views.UserViewSet.as_view({'post': 'add_one'})),
    path('login', views.UserViewSet.as_view({'post': 'login'})),
    path('logout/', views.UserViewSet.as_view({'get': 'logout'})),
    path('login/status', views.UserViewSet.as_view({'get': 'check_login_status'})),
]
