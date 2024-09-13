from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from core.models import AppConfiguration
from .serializers import AppConfigurationSerializer

class AppConfigurationListCreateView(generics.ListCreateAPIView):
    queryset = AppConfiguration.objects.all()
    serializer_class = AppConfigurationSerializer
    permission_classes = [IsAdminUser]


class ActiveAppConfigurationView(generics.RetrieveAPIView):
    serializer_class = AppConfigurationSerializer

    def get_object(self):
        return AppConfiguration.objects.filter(is_active=True).first()
