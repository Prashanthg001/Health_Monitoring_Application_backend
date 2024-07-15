from django.urls import path
from .views import HealthInfoView
from .views import RegisterView, LoginView, LogoutView
from rest_framework_simplejwt.views import TokenVerifyView

urlpatterns = [
    path('health_info/', HealthInfoView.as_view(), name='health_info'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]