from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import Goal, GoalCompletion
from .serializers import GoalSerializer, GoalCompletionSerializer
from core.utils import IsOwnerOrReadOnly

class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        goal = self.get_object()
        goal.is_active = not goal.is_active
        goal.save()
        return Response({'status': 'goal activity toggled'})

    @action(detail=True, methods=['post'])
    def mark_complete(self, request, pk=None):
        goal = self.get_object()
        date = request.data.get('date')
        
        if not date:
            return Response({'error': 'Date is required'}, status=status.HTTP_400_BAD_REQUEST)

        completion, created = GoalCompletion.objects.get_or_create(
            goal=goal,
            date=date,
            defaults={'is_completed': True}
        )

        if not created:
            completion.is_completed = True
            completion.save()

        serializer = GoalCompletionSerializer(completion)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_incomplete(self, request, pk=None):
        goal = self.get_object()
        date = request.data.get('date')
        
        if not date:
            return Response({'error': 'Date is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            completion = GoalCompletion.objects.get(goal=goal, date=date)
            completion.is_completed = False
            completion.save()
            serializer = GoalCompletionSerializer(completion)
            return Response(serializer.data)
        except GoalCompletion.DoesNotExist:
            return Response({'error': 'Completion record not found'}, status=status.HTTP_404_NOT_FOUND)
