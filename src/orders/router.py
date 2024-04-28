from datetime import date

from fastapi import APIRouter, Body, Depends, File, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response, StreamingResponse

from src.action_history.schemas import SetOrderItemWarehouseStatus
from src.common.models import SortOrder
from src.database import get_db
from src.directions.models import TransportationType
from src.orders.schemas import (CancelledOrder, CourierDeliverySchema,
                                NotDeliveredOrder, OrderItemsCreateSchemas,
                                OrderItemsPaginated, OrderItemsViewSchemas,
                                OrderPaginated, OrdersCreateSchemas,
                                OrderStatus, OrderUpdateSchemas,
                                OrderViewSchemas, PaymentUpdateSchemas,
                                SignOrderOTP, TotalAmount, TotalAmountOrder)
from src.orders.service import order_item_service, order_service
from src.orders.utils import generate_excel_file
from src.users.auth import JWTBearer
from src.users.perms import PermsRequired
from src.users.schemas import Permission

router = APIRouter(
    tags=["Orders"]
)


@router.post("/orders", status_code=status.HTTP_201_CREATED)
async def create_order(payload: OrdersCreateSchemas, db: AsyncSession = Depends(get_db)):
    return await order_service.create_order(payload, db)


@router.get("/orders/paginated",
            dependencies=[PermsRequired([Permission.VIEW_ORDER])],
            response_model=OrderPaginated,
            status_code=status.HTTP_200_OK)
async def get_orders_paginated(user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db), status: list[OrderStatus] = Query(None), warehouse_id: list[int] = Query(None), direction_id: list[int] = Query(None), transportation_type: list[TransportationType] = Query(None), start_date: date = Query(None), end_date: date = Query(None), page: int = 1, limit: int = 10, sort_by: str = Query(None), sort_order: SortOrder = Query(None), today: bool = Query(None), all_time: bool = Query(None), search: str = Query(None), shipping_id: int = Query(None)) -> OrderPaginated:
    return await order_service.get_orders_paginated(user, db, status, warehouse_id, direction_id, transportation_type, start_date, end_date, page, limit, sort_by, sort_order, today, all_time, search, shipping_id)


@router.get("/orders/excel",
            dependencies=[Depends(JWTBearer())],
            status_code=status.HTTP_200_OK)
async def download_orders_excel(user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db),
                                status: list[OrderStatus] = Query(None), warehouse_id: list[int] = Query(None),
                                direction_id: list[int] = Query(None),
                                transportation_type: list[TransportationType] = Query(
                                    None),
                                start_date: date = Query(None), end_date: date = Query(None), sort_by: str = Query(None), sort_order: SortOrder = Query(None),
                                today: bool = Query(None), all_time: bool = Query(None),
                                search: str = Query(None)
                                ):
    excel_file = await generate_excel_file(db, user, status, warehouse_id, direction_id, transportation_type,
                                           start_date, end_date, sort_by, sort_order, today,
                                           all_time, search)
    return Response(content=excel_file.read(),
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": "attachment; filename=orders.xlsx"})


@router.get("/orders/{id}",
            dependencies=[PermsRequired([Permission.VIEW_ORDER])],
            response_model=OrderViewSchemas,
            status_code=status.HTTP_200_OK)
async def get_order(id: int, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await order_service.get_order(id, user, db)


@router.get("/client/orders/{id}",
            response_model=OrderViewSchemas,
            status_code=status.HTTP_200_OK)
async def get_client_order(id: int, db: AsyncSession = Depends(get_db)):
    return await order_service.get_client_order(id, db)


@router.patch("/orders/{id}/restore",
              dependencies=[Depends(JWTBearer())],
              response_model=OrderViewSchemas,
              status_code=status.HTTP_200_OK)
async def resume_order(id: int, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await order_service.resume_order(id, user, db)


@router.get("/orders/qr-code/{qr_code:str}",
            response_model=OrderViewSchemas,
            status_code=status.HTTP_200_OK)
async def get_order_by_qr_code(qr_code: str, db: AsyncSession = Depends(get_db)):
    return await order_service.get_order_by_qr_code(qr_code, db)


@router.delete("/orders/{id}",
               dependencies=[PermsRequired([Permission.DELETE_ORDER])],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(id: int, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await order_service.delete_orders(id, user, db)


@router.put("/orders/{id}",
            dependencies=[PermsRequired([Permission.UPDATE_ORDER])],
            response_model=OrderViewSchemas,
            status_code=status.HTTP_200_OK)
async def update_order(id: int, payload: OrderUpdateSchemas, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await order_service.update_order(id, payload, user, db)


@router.put("/orders/{id}/payment",
            dependencies=[PermsRequired([Permission.UPDATE_ORDER])],
            response_model=PaymentUpdateSchemas,
            status_code=status.HTTP_200_OK)
async def update_order_payment(id: int, payload: PaymentUpdateSchemas, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await order_service.update_payment_order(id, payload, user, db)


@router.put("/orders/{id}/payment/paid",
            dependencies=[PermsRequired([Permission.UPDATE_ORDER])],
            response_model=OrderViewSchemas,
            status_code=status.HTTP_200_OK)
async def update_order_payment(id: int, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await order_service.set_as_paid(id, user, db)


@router.put("/orders/{id}/payment/not_paid",
            dependencies=[PermsRequired([Permission.UPDATE_ORDER])],
            response_model=OrderViewSchemas,
            status_code=status.HTTP_200_OK)
async def update_order_payment(id: int, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await order_service.set_as_not_paid(id, user, db)


@router.patch("/orders/{id:int}/delivered",
              dependencies=[PermsRequired([Permission.UPDATE_ORDER_STATUS])],
              response_model=OrderViewSchemas,
              status_code=status.HTTP_200_OK)
async def set_as_delivered_order(id: int, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await order_service.set_as_delivered(id, user, db)


@router.patch("/orders/{id:int}/cancelled",
              dependencies=[PermsRequired([Permission.UPDATE_ORDER_STATUS])],
              response_model=OrderViewSchemas,
              status_code=status.HTTP_200_OK)
async def set_as_canceled(id: int, payload: CancelledOrder, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await order_service.set_as_cancelled(id, payload, user, db)


@router.patch("/orders/{id:int}/courier_delivering_to_warehouse",
              dependencies=[PermsRequired([Permission.UPDATE_ORDER_STATUS])],
              response_model=OrderViewSchemas,
              status_code=status.HTTP_200_OK)
async def set_as_courier_delivering_to_warehouse(id: int, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await order_service.set_as_courier_delivering_to_warehouse(id, user, db)


@router.patch("/orders/{id:int}/in_transit",
              dependencies=[PermsRequired([Permission.UPDATE_ORDER_STATUS])],
              response_model=OrderViewSchemas,
              status_code=status.HTTP_200_OK)
async def set_as_in_transit(id: int, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await order_service.set_as_in_transit(id, user, db)


@router.patch("/orders/{id:int}/delivering_to_recipient",
              dependencies=[PermsRequired([Permission.UPDATE_ORDER_STATUS])],
              response_model=OrderViewSchemas,
              status_code=status.HTTP_200_OK)
async def set_as_delivering_to_recipient(id: int, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await order_service.set_as_delivering_to_recipient(id, user, db)


@router.patch("/orders/{id:int}/not_delivered",
              dependencies=[PermsRequired([Permission.UPDATE_ORDER_STATUS])],
              response_model=OrderViewSchemas,
              status_code=status.HTTP_200_OK)
async def set_as_not_delivered(id: int, payload: NotDeliveredOrder, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await order_service.set_as_not_delivered(id, payload, user, db)


@router.post("/orders/{id:int}/public_offer/otp/send",
             dependencies=[Depends(JWTBearer())],
             status_code=status.HTTP_201_CREATED)
async def send_otp_code(id: int, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await order_service.send_otp_code_for_signing(id, user, db)


@router.post("/orders/{id:int}/public_offer/otp/accept",
             dependencies=[Depends(JWTBearer())],
             status_code=status.HTTP_200_OK)
async def accept_public_offer(id: int, payload: SignOrderOTP, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await order_service.accept_public_offer(id, payload, user, db)


@router.get("/orders/{id:int}/waiver_agreement", status_code=status.HTTP_200_OK)
async def get_waiver_agreement(id: int, db: AsyncSession = Depends(get_db)) -> StreamingResponse:
    return await order_service.get_waiver_agreement(id, db)


@router.post("/orders/{id:int}/waiver_agreement/otp/send",
             dependencies=[Depends(JWTBearer())],
             status_code=status.HTTP_201_CREATED)
async def send_waiver_agreement_otp_code(id: int, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await order_service.send_otp_code_for_waiver_agreement(id, user, db)


@router.post("/orders/{id:int}/waiver_agreement/otp/accept",
             dependencies=[Depends(JWTBearer())],
             status_code=status.HTTP_200_OK)
async def accept_waiver_agreement(id: int, payload: SignOrderOTP, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await order_service.accept_waiver_agreement(id, payload, user, db)


@router.post("/orders/items",
             dependencies=[PermsRequired([Permission.UPDATE_ORDER])],
             status_code=status.HTTP_201_CREATED,
             response_model=OrderItemsViewSchemas)
async def create_order_item(payload: OrderItemsCreateSchemas = Body(...), user: str = Depends(JWTBearer()), file: UploadFile = File(None), db: AsyncSession = Depends(get_db)):
    return await order_item_service.add(payload, user, file, db)


@router.delete("/orders/items/{id}",
               dependencies=[PermsRequired([Permission.UPDATE_ORDER])],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_order_item(id: int, db: AsyncSession = Depends(get_db)):
    return await order_item_service.delete(id, db)


# TODO: delete this endpoint
@router.patch("/orders/items/{id}/courier_delivering_to_warehouse",
              dependencies=[PermsRequired([Permission.UPDATE_ORDER_STATUS])],
              response_model=OrderItemsViewSchemas,
              status_code=status.HTTP_200_OK)
async def set_as_courier_delivering_to_warehouse(id: int, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await order_item_service.set_as_courier_delivering_to_warehouse(id, user, db)


@router.patch("/orders/{id:int}/accepted_to_warehouse",
              dependencies=[PermsRequired([Permission.UPDATE_ORDER_STATUS])],
              response_model=OrderViewSchemas,
              status_code=status.HTTP_200_OK)
async def set_as_accepted_to_warehouse(id: int, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await order_service.set_as_accepted_to_warehouse(id, user, db)


@router.patch("/orders/items/accepted_to_warehouse",
              dependencies=[PermsRequired([Permission.UPDATE_ORDER_STATUS])],
              response_model=OrderItemsViewSchemas,
              status_code=status.HTTP_200_OK)
async def set_as_accepted_to_warehouse(status: SetOrderItemWarehouseStatus, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await order_item_service.set_as_accepted_to_warehouse(status, user, db)


@router.patch("/orders/items/arrived_to_destination",
              dependencies=[PermsRequired([Permission.UPDATE_ORDER_STATUS])],
              status_code=status.HTTP_200_OK)
async def set_as_arrived_to_destination(status: SetOrderItemWarehouseStatus, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await order_item_service.set_as_arrived_to_destination(status, user, db)


@router.patch("/orders/items/{id}/in_transit",
              dependencies=[PermsRequired([Permission.UPDATE_ORDER_STATUS])],
              response_model=OrderItemsViewSchemas,
              status_code=status.HTTP_200_OK)
async def set_as_delivering_to_recipient(id: int, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await order_item_service.set_as_in_transit(id, user, db)


@router.post("/orders/calculate_expenses",
             status_code=status.HTTP_200_OK)
async def get_calculate_expenses(ids: list[int], db: AsyncSession = Depends(get_db)):
    return await order_service.calculate_expenses(ids, db)


@router.post("/orders/calculate_total_sum",
             status_code=status.HTTP_200_OK)
async def get_total_sum(payload: TotalAmountOrder, db: AsyncSession = Depends(get_db)) -> TotalAmount:
    return await order_service.total_amount(payload, db)


@router.post("/orders_items/take_for_delivery",
             dependencies=[Depends(JWTBearer())],
             status_code=status.HTTP_200_OK)
async def take_for_delivery(payload: CourierDeliverySchema, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await order_service.add_order_items_for_delivery(payload, user, db)


@router.post("/orders/{id:int}/upload_photos",
             dependencies=[Depends(JWTBearer())],
             status_code=status.HTTP_201_CREATED)
async def set_photos_to_order(id: int, files: list[UploadFile], user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await order_service.upload_photos_to_order(id, files, db)


@router.get("/orders-item/paginated",
            dependencies=[PermsRequired([Permission.VIEW_ORDER])],
            response_model=OrderItemsPaginated,
            status_code=status.HTTP_200_OK)
async def get_orders_paginated(order_id: int, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db), page: int = 1, limit: int = 10) -> OrderPaginated:
    return await order_item_service.get_paginated_order_items_by_order_id(order_id, db, page, limit)
