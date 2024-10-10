from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from core.models import JournalEntry, JournalTemplate
from core.models import GoalCompletion, Goal
from core.models import StandalonePrompt
from core.models import Quote
from .serializers import HomeSerializer

class HomeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, date=None):
        if not date:
            date = timezone.now().date()

        user = request.user
        profile = user.profile

        # Get or create journal entries
        morning_intention = self.get_or_create_journal_entry(user, date, profile.morning_intention)
        evening_reflection = self.get_or_create_journal_entry(user, date, profile.evening_reflection)

        # Get goal completions for today
        goal_completions = self.get_goal_completions(user, date)

        # Get prompt of the day
        prompt_of_the_day = self.get_prompt_of_the_day()

        # Get quote of the day
        quote_of_the_day = self.get_quote_of_the_day()

        data = {
            'date': date,
            'morning_intention': morning_intention,
            'evening_reflection': evening_reflection,
            'goal_completions': goal_completions,
            'prompt_of_the_day': prompt_of_the_day,
            'quote_of_the_day': quote_of_the_day,
        }

        serializer = HomeSerializer(data)
        return Response(serializer.data)

    def get_or_create_journal_entry(self, user, date, template):
        if not template:
            return None
        
        entry, created = JournalEntry.objects.get_or_create(
            user=user,
            journal_template=template,
            for_date=date,
            defaults={'is_completed': False, 'is_started': False}
        )
        return entry

    def get_goal_completions(self, user, date):
        goals = Goal.objects.filter(user=user, is_active=True)
        completions = []
        for goal in goals:
            if goal.is_due_today():
                completion = goal.completions.filter(date=date).first()
                completions.append({
                    'id': goal.id,
                    'title': goal.title,
                    'is_completed': completion.is_completed if completion else False,
                    'date': date  # Add this line
                })
        return completions

    def get_prompt_of_the_day(self):
        return StandalonePrompt.objects.filter(visibility='public').order_by('?').first()

    def get_quote_of_the_day(self):
        return Quote.objects.order_by('?').first()
