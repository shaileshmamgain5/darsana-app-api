from django.urls import path
from .views import HomeView

urlpatterns = [
    path('<str:date>/', HomeView.as_view(), name='home'),
    path('', HomeView.as_view(), name='home-today'),
]
