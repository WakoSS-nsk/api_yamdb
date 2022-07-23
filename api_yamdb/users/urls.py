from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import (
    CustomTokenView,
    SignUpViewSet,
    UsersView
)


router = DefaultRouter()
router.register(r'users', UsersView, basename='users')

urlpatterns = [
    path('v1/auth/signup/', SignUpViewSet.as_view()),
    path('v1/auth/token/', CustomTokenView.as_view()),
    path('v1/', include(router.urls))
]
