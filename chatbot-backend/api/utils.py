import requests

GEMINI_API_KEY = "AIzaSyDUnO0E42RWNptjaN0jI402mUdjCbGxSJw"
GEMINI_API_URL = "https://api.gemini.com/v1"

def get_stock_info(symbol):
    try:
        response = requests.get(
            f"{GEMINI_API_URL}/ticker/{symbol}",
            headers={"Authorization": f"Bearer {GEMINI_API_KEY}"}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
