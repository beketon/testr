import requests

from src.config import settings


class WhatsappClient:
    def __init__(self) -> None:
        self.url = settings.WHATSAPP_SERVICE_URL
        self._headers = {
            "Content-Type": "application/json"
        }

    def send_sms(self, phone: str, body: str):
        data = {"phone": phone, "text": body}
        resp = requests.post(f"{self.url}/send", json=data, headers=self._headers)
        return resp.text


whatsapp_client = WhatsappClient()
