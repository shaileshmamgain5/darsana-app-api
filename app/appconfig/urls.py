from django.urls import path
from .views import AppConfigurationListCreateView, ActiveAppConfigurationView

urlpatterns = [
    path('app-configurations/', AppConfigurationListCreateView.as_view(), name='app-configuration-list-create'),
    path('app-configurations/active/', ActiveAppConfigurationView.as_view(), name='active-app-configuration'),
]
