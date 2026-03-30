from django.urls import path
from users import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('me/', views.my_profile, name='my-profile'),
]