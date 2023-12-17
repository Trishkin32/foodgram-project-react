from django.urls import include, path

from api.views import SubscribeList, APISubscribe

urlpatterns = [
    path(
        'users/subscriptions/',
        SubscribeList.as_view(),
        name='subscriptions',
    ),
    path(
        'users/<int:pk>/subscribe/',
        APISubscribe.as_view(),
        name='subscribe',
    ),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
