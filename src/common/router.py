from fastapi import APIRouter

from src.clients.firebase import firebase_client
from src.clients.whatsapp import whatsapp_client
from src.common.service import file_service
from src.directions.models import TransportationType
from src.notification.models import SendPushNotification, SendSMS
from src.orders.models import (STATUS_GROUPS, DeliveryType, OrderStatus,
                               PaymentStatus)
from src.orders.schemas import OrderStatus, PayerType, PaymentType
from src.shipping.models import ShippingRespondStatus
from src.tarifs.models import CalculationType

router = APIRouter(
    tags=["root"]
)


@router.get("/api/v1/calculation_types", tags=["root"])
async def get_calculation_types():
    return [calculation_type.value for calculation_type in CalculationType]


@router.get("/api/v1/statuses", tags=["root"])
async def get_statuses():
    return [status.value for status in OrderStatus]


@router.get("/api/v1/transportation_types", tags=["root"])
async def get_transportation_types():
    return [transportation_type.value for transportation_type in TransportationType]


@router.get("/api/v1/status_groups", tags=["root"])
async def get_status_groups():
    return STATUS_GROUPS


@router.get("/download/{filename}", tags=["root"])
async def download(filename: str):
    return await file_service.download_file(filename)


@router.get("/api/v1/delivery_types", tags=["root"])
async def get_delivery_types():
    return [delivery_type.value for delivery_type in DeliveryType]


@router.get("/api/v1/payment_types", tags=["root"])
async def get_payment_types():
    return [payment_type.value for payment_type in PaymentType]


@router.get("/api/v1/payer_types", tags=["root"])
async def get_payer_types():
    return [payer_type.value for payer_type in PayerType]


@router.get("/api/v1/payment_statuses", tags=["root"])
async def get_payment_statuses():
    return [payment_status.value for payment_status in PaymentStatus]


@router.get("/api/v1/shipping_respond_statuses", tags=["root"])
async def get_shipping_responds_statuses():
    return [item.value for item in ShippingRespondStatus]


@router.post("/api/v1/send-push-notification", tags=["root"])
def send_push_notification(payload: SendPushNotification):
    return firebase_client.send_notification(payload.device_token, payload.title, payload.body)


@router.post("/api/v1/send-sms", tags=["root"])
def send_sms(payload: SendSMS):
    return whatsapp_client.send_sms(payload.phone, payload.message)


@router.get("/", tags=["root"])
def main():
    return {"detail": "This is the main page of the API. Please use the /docs endpoint to see the documentation."}
