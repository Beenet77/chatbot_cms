import requests
from django.conf import settings
from api.models import Copyright,Logo


def get_stock_info(symbol):
    try:
        # Get API key from settings which loads from .env
        api_key = settings.GEMINI_API_KEY
        
        response = requests.get(
            f"https://api.gemini.com/v1/ticker/{symbol}",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    

def get_copyright():
    try:
        copyright = Copyright.objects.first()
        return copyright.content if copyright else "NEPSE Chatbot"
    except Copyright.DoesNotExist:
        return "NEPSE Chatbot"
def get_logo():
    try:
        logo = Logo.objects.filter(logo_type="main").first()
        return logo.logo if copyright else "NEPSE Chatbot"
    except Logo.DoesNotExist:
        return "NEPSE Chatbot"
