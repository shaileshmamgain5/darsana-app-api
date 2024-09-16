import requests
from django.conf import settings

class LangServeClient:
    def __init__(self):
        self.base_url = settings.LANGSERVE_BASE_URL
        self.api_key = settings.LANGSERVE_API_KEY

    def get_response(self, message, thread_messages=[]):
        """
        Get AI response for a given message and optional thread messages.
        """
        endpoint = f"{self.base_url}/chat"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "message": message,
            "thread_messages": thread_messages
        }

        try:
            response = requests.post(endpoint, json=data, headers=headers)
            response.raise_for_status()
            return response.json()["response"]
        except requests.RequestException as e:
            print(f"Error getting AI response: {e}")
            return "I'm sorry, I'm having trouble processing your request right now."

    def cancel_response(self, message_id):
        """
        Cancel an ongoing AI response generation.
        """
        endpoint = f"{self.base_url}/cancel/{message_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            response = requests.post(endpoint, headers=headers)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Error cancelling AI response: {e}")
            return False

    def create_summary(self, messages):
        """
        Create a summary for a list of messages.
        """
        endpoint = f"{self.base_url}/create_summary"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "messages": messages
        }

        try:
            response = requests.post(endpoint, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error creating summary: {e}")
            return {"summary": "Failed to generate summary", "thread_title": "New Conversation"}
