from accounts.views import RegisterView
from django.urls import path,include

urlpatterns = [
    path('api/auth/register/', RegisterView.as_view(), name='register'),
]