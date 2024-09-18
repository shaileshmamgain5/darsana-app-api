import requests
from django.conf import settings

class LangServeClient:
    def __init__(self):
        self.base_url = settings.LANGSERVE_BASE_URL

    def get_response(self, message, thread_messages=[]):
        """
        Get AI response for a given message and optional thread messages.
        """
        endpoint = f"{self.base_url}/chain/invoke"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "input": {
                "question": message,
                "chat_history": thread_messages
            }
        }

        response = requests.post(endpoint, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()["output"]

    def cancel_response(self, message_id):
        """
        Cancel an ongoing AI response generation.
        """
        # The ai-assistant service doesn't support cancellation, so we'll just return True
        return True

    def create_summary(self, messages):
        """
        Create a summary of the chat session.
        """
        # This method would need to be implemented in the ai-assistant service
        # For now, we'll just return a placeholder
        return {
            "summary": "Chat session summary not implemented yet.",
            "thread_title": "New Conversation"
        }
