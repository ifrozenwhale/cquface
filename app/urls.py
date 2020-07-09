from django.urls import path

from app import views

urlpatterns = [
    path('add_user', views.AppViewSet.as_view({'post': 'add_one'})),
    path('login', views.AppViewSet.as_view({'post': 'login'})),
    path('logout', views.AppViewSet.as_view({'post': 'logout'})),
    path('get_my_info', views.AppViewSet.as_view({'post': 'get_my_info'})),
    path('update_my_info', views.AppViewSet.as_view({'post': 'update_my_info'})),
    path('get_my_portrait/<str:account>', views.AppViewSet.as_view({'get': 'get_my_portrait'})),  #
    path('update_my_portrait', views.AppViewSet.as_view({'post': 'update_my_portrait'})),  #

    path('shares_random/<str:user_id>/<int:share_num>', views.AppViewSet.as_view({'get': 'get_shares'})),
    path('favorites/<str:user_id>', views.AppViewSet.as_view({'get': 'get_favorites'})),
    path('share_info/<str:user_id>/<str:photo_id>/<str:user_now>', views.AppViewSet.as_view({'get': 'get_share_info'})),
    path('star', views.AppViewSet.as_view({'post': 'star'})),
    path('comment', views.AppViewSet.as_view({'post': 'comment'})),
    path('shares/account/<str:account>', views.AppViewSet.as_view({'get': 'get_shared_by_account'})),
    path('share/photo/<str:photo_id>', views.AppViewSet.as_view({'delete': 'delete_photo'})),#

    path('recognition', views.AppViewSet.as_view({'post': 'recognition'})),
    path('share', views.AppViewSet.as_view({'post': 'share'})),
    path('showFollows/<str:account>', views.AppViewSet.as_view({'get': 'showFollows'})),
    path('showFans/<str:account>', views.AppViewSet.as_view({'get': 'showFans'})),
    path('showOthersShared/<str:account>', views.AppViewSet.as_view({'get': 'showOthersShared'})),
    path('followAndUnfollow', views.AppViewSet.as_view({'post': 'followAndUnfollow'})),

    path('fanFollowCollect/<str:account>', views.AppViewSet.as_view({'get': 'get_fan_follow_collect'})), #
]
