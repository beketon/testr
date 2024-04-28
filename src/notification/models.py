from enum import Enum

from pydantic import BaseModel


class NotificationCode(str, Enum):
    COURIER_NEW_ORDER = "COURIER_NEW_ORDER"


class SmsCode(str, Enum):
    PUBLIC_OFFER = "PUBLIC_OFFER"
    WAIVER_AGREEMENT = "WAIVER_AGREEMENT"
    DRIVER_CONTRACT = "DRIVER_CONTRACT"
    TRACKING_TEMPLATE = "TRACKING_TEMPLATE"


class NotificationTemplate(BaseModel):
    title: str
    message: str


class SMSTemplate(BaseModel):
    message: str


NOTIFICATION_TEMPLATES = {
    NotificationCode.COURIER_NEW_ORDER: NotificationTemplate(
        title="Поступил новый заказ.",
        message="Поступил новый заказ, зайдите в приложение и примите его."
    ),
    SmsCode.PUBLIC_OFFER: SMSTemplate(
        message="Согласен с договором оферты. Код подтверждения: {code}"
    ),
    SmsCode.WAIVER_AGREEMENT: SMSTemplate(
        message="Согласен с актом приема и передачи. Код подтверждения: {code}"
    ),
    SmsCode.DRIVER_CONTRACT: SMSTemplate(
        message="Cогласен с договором ГПХ. Код подтверждения: {code}"
    ),
    SmsCode.TRACKING_TEMPLATE: SMSTemplate(
        message="Ссылка для трекинга заказа: {url}"
    )
}


class SendSMS(BaseModel):
    phone: str
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "phone": "+77785547554",
                "message": "Hello world"
            }
        }


class SendPushNotification(BaseModel):
    device_token: str
    title: str
    body: str

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "device_token": "device_token",
                "title": "Hello",
                "body": "Hello world"
            }
        }
    }
