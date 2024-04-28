from src.clients.firebase import firebase_client
from src.clients.whatsapp import whatsapp_client
from src.notification.models import (NOTIFICATION_TEMPLATES, NotificationCode,
                                     SmsCode)
from src.users.models import Users
from src.users.service import user_service


class NotificationService:
    async def send_notification(self, user_id: int, notification_code: NotificationCode, **kwargs):
        user: Users = await user_service.find_one_or_none({"id": user_id})
        if not user:
            return {"detail": "User not found"}
        message = NOTIFICATION_TEMPLATES[notification_code]
        firebase_client.send_notification(
            user.device_registration_id, message.title, message.message.format(**kwargs))
        return {"detail": "Notification sent"}

    def send_sms(self, phone: str, sms_code: SmsCode, **kwargs):
        message = NOTIFICATION_TEMPLATES[sms_code]
        whatsapp_client.send_sms(phone, message.message.format(**kwargs))
        return {"detail": "SMS sent"}


notification_service = NotificationService()
