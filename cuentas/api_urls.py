from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api_views import (
    CuentaBancariaViewSet,
    api_login,
    api_logout,
)


router = DefaultRouter()

router.register(
    'cuentas',
    CuentaBancariaViewSet,
    basename='api-cuentas'
)


urlpatterns = [

    path(
        'login/',
        api_login,
        name='api-login'
    ),

    path(
        'logout/',
        api_logout,
        name='api-logout'
    ),

    path(
        '',
        include(router.urls)
    ),
]