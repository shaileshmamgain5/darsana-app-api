from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from core.models import AppConfiguration
from .serializers import AppConfigurationSerializer
from core.permissions import IsStaffOrSuperuser

class AppConfigurationListCreateView(generics.ListCreateAPIView):
    queryset = AppConfiguration.objects.all()
    serializer_class = AppConfigurationSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsStaffOrSuperuser()]
        return [IsAuthenticated()]

class ActiveAppConfigurationView(generics.RetrieveAPIView):
    serializer_class = AppConfigurationSerializer

    def get_object(self):
        return AppConfiguration.objects.filter(is_active=True).first()
