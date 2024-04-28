
from datetime import date
from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse, Response

from src.database import get_db
from src.directions.models import TransportationType
from src.orders.schemas import SignOrderOTP
from src.shipping.models import ShippingRespondStatus, ShippingStatus
from src.shipping.schemas import (PaginationShipping, ShippingCoordinate,
                                  ShippingCreateSchema, ShippingLoadsSchema,
                                  ShippingPathSchema,
                                  ShippingRespondViewSchema,
                                  ShippingViewSchema, CourierShippingsSchema, CourierShippingsDetailSchema,
                                  PaginationCourierShippings)
from src.shipping.service import shipping_service
from src.users.auth import JWTBearer
from src.users.models import Users
from src.users.perms import PermsRequired
from src.users.schemas import Permission

router = APIRouter(
    tags=["Shipping"]
)

"""
    CRUD endpoints for shippings and attachements.
"""


@router.post("/shippings",
             dependencies=[PermsRequired([Permission.CREATE_SHIPPING])],
             status_code=status.HTTP_201_CREATED)
async def create(payload: ShippingCreateSchema, db: AsyncSession = Depends(get_db)):
    return await shipping_service.create(payload=payload, db=db)


@router.get("/shippings",
            dependencies=[PermsRequired([Permission.VIEW_SHIPPING])],
            response_model=PaginationShipping,
            status_code=status.HTTP_200_OK)
async def list_shippings(is_driver_contract_accepted: bool = Query(None), is_loaded: bool = Query(None),
                         direction_id: int = Query(None), transportation_type: TransportationType = Query(None),
                         statuses: List[ShippingStatus] = Query(None), db: AsyncSession = Depends(get_db),
                         user: Users = Depends(JWTBearer()), start_date: date = Query(None),
                         end_date: date = Query(None), page: int = 1, limit: int = 10, search: str = Query(None)):
    return await shipping_service.list_shippings(is_driver_contract_accepted, direction_id=direction_id,
                                                 transportation_type=transportation_type, statuses=statuses, db=db,
                                                 user=user, page=page, limit=limit, start_date=start_date,
                                                 end_date=end_date, search=search, is_loaded=is_loaded)


@router.get("/shippings/couriers",
            dependencies=[Depends(JWTBearer()),
                          Depends(get_db)],
            response_model=PaginationCourierShippings,
            status_code=status.HTTP_200_OK)
async def get_courier_shippings(db: AsyncSession = Depends(get_db), page: int = 1, limit: int = 10, search: str = Query(None)) -> PaginationCourierShippings:
    return await shipping_service.get_courier(db=db, page=page, limit=limit, search=search)


@router.get("/shippings/couriers/{id}",
            dependencies=[Depends(JWTBearer()),
                          Depends(get_db)],
            response_model=CourierShippingsDetailSchema,
            status_code=status.HTTP_200_OK)
async def get_courier_shippings(id: int, db: AsyncSession = Depends(get_db)) -> CourierShippingsDetailSchema:
    return await shipping_service.get_courier_detail(id=id, db=db)


@router.get("/shippings/excel/{id}",
            dependencies=[Depends(JWTBearer())],
            status_code=status.HTTP_200_OK)
async def download_shippings_excel(id: int, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    excel_file = await shipping_service.generate_excel_file(id, db, user)
    return Response(content=excel_file.read(),
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": "attachment; filename=shipping_orders.xlsx"})


@router.get("/shippings/courier_excel/{id}",
            dependencies=[Depends(JWTBearer())],
            status_code=status.HTTP_200_OK)
async def download_courier_excel(id: int, user: str = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    excel_file = await shipping_service.generate_courier_excel(id, db, user)
    return Response(content=excel_file.read(),
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": "attachment; filename=courier_orders.xlsx"})


@router.get("/shippings/my",
            dependencies=[PermsRequired([Permission.VIEW_SHIPPING])],
            response_model=PaginationShipping,
            status_code=status.HTTP_200_OK)
async def my_shippings(respond_status: list[ShippingRespondStatus] = Query(None), is_driver_contract_accepted: bool = Query(None), direction_id: int = Query(None), transportation_type: TransportationType = Query(None), statuses: List[ShippingStatus] = Query(None), db: AsyncSession = Depends(get_db), user: Users = Depends(JWTBearer()), start_date: date = Query(None), end_date: date = Query(None), page: int = 1, limit: int = 10, search: str = Query(None)):
    return await shipping_service.my_shippings(is_driver_contract_accepted, direction_id=direction_id, transportation_type=transportation_type, statuses=statuses, db=db, user=user, page=page, limit=limit, start_date=start_date, end_date=end_date, search=search, respond_status=respond_status)


@router.get("/shippings/{id}",
            dependencies=[PermsRequired([Permission.VIEW_SHIPPING])],
            response_model=ShippingViewSchema,
            status_code=status.HTTP_200_OK)
async def get_by_id(id: int, db: AsyncSession = Depends(get_db), user: Users = Depends(JWTBearer())):
    return await shipping_service.get_by_id(id=id, db=db, user=user)


@router.patch("/shippings/{id}",
              dependencies=[PermsRequired([Permission.UPDATE_SHIPPING])],
              response_model=ShippingViewSchema,
              status_code=status.HTTP_200_OK)
async def path(id: int, payload: ShippingPathSchema, db: AsyncSession = Depends(get_db)):
    return await shipping_service.path(id=id, payload=payload, db=db)


@router.delete("/shippings/{id}",
               dependencies=[PermsRequired([Permission.DELETE_SHIPPING])],
               response_model=None,
               status_code=status.HTTP_204_NO_CONTENT)
async def delete(id: int, db: AsyncSession = Depends(get_db)):
    return await shipping_service.delete(id=id, db=db)

"""
    CRUD endpoints for shippings and attachements.
"""


@router.post("/shippings/{shipping_id}/responds",
             dependencies=[Depends(JWTBearer()),
                           Depends(get_db)],
             response_model=ShippingRespondViewSchema,
             status_code=status.HTTP_201_CREATED)
async def create_shipping_responds(shipping_id: int, user: Users = Depends(JWTBearer()), db: AsyncSession = Depends(get_db)):
    return await shipping_service.create_shipping_responds(shipping_id=shipping_id, user=user, db=db)


@router.get("/shippings/{shipping_id}/responds",
            dependencies=[Depends(JWTBearer()),
                          Depends(get_db)],
            response_model=List[ShippingRespondViewSchema],
            status_code=status.HTTP_200_OK)
async def get_shipping_responds_by_shipping(shipping_id: int, status: ShippingRespondStatus = Query(None), db: AsyncSession = Depends(get_db)):
    return await shipping_service.get_shipping_responds_by_shipping(status=status, db=db, shipping_id=shipping_id)


@router.post("/shipping_responds/{respond_id}/accept",
             dependencies=[PermsRequired([Permission.ACCEPT_SHIPPING_RESPOND])],
             status_code=status.HTTP_200_OK)
async def accept(respond_id: int, db: AsyncSession = Depends(get_db), user: Users = Depends(JWTBearer())):
    return await shipping_service.accept(respond_id=respond_id, user=user, db=db)


@router.post("/shipping_responds/{respond_id}/cancel",
             dependencies=[PermsRequired([Permission.ACCEPT_SHIPPING_RESPOND])],
             status_code=status.HTTP_200_OK)
async def cancel(respond_id: int, db: AsyncSession = Depends(get_db), user: Users = Depends(JWTBearer())):
    return await shipping_service.cancel(respond_id=respond_id, user=user, db=db)


@router.get("/shippings/{id}/driver_contract",
            tags=["root"], status_code=status.HTTP_200_OK)
async def get_driver_contract(id: int, db: AsyncSession = Depends(get_db), user: Users = Depends(JWTBearer())) -> StreamingResponse:
    return await shipping_service.get_driver_contract(id=id, db=db, user=user)


@router.post("/shippings/{id}/driver_contract/otp/send",
             dependencies=[Depends(JWTBearer()),
                           Depends(get_db)],
             status_code=status.HTTP_200_OK)
async def send_otp_signing(id: int, db: AsyncSession = Depends(get_db), user: Users = Depends(JWTBearer())):
    return await shipping_service.send_otp_code_for_signing(id=id, user=user, db=db)


@router.post("/shippings/{id}/driver_contract/otp/accept",
             dependencies=[Depends(JWTBearer()),
                           Depends(get_db)],
             status_code=status.HTTP_200_OK)
async def accept_otp_signing(id: int, otp: SignOrderOTP, db: AsyncSession = Depends(get_db), user: Users = Depends(JWTBearer())):
    return await shipping_service.accept_driver_contract(id=id, payload=otp, user=user, db=db)


@router.post("/shippings/{shipping_id}/loads",
             dependencies=[Depends(JWTBearer()),
                           Depends(get_db)],
             status_code=status.HTTP_201_CREATED)
async def shipping_loads(payload: ShippingLoadsSchema, shipping_id: int, db: AsyncSession = Depends(get_db), user: Users = Depends(JWTBearer())):
    return await shipping_service.shipping_loads(payload=payload, shipping_id=shipping_id, user=user, db=db)


@router.post("/shippings/{shipping_id}/in_transit",
             dependencies=[Depends(JWTBearer()),
                           Depends(get_db)],
             status_code=status.HTTP_200_OK, response_model=ShippingViewSchema)
async def status_in_transit(shipping_id: int, db: AsyncSession = Depends(get_db)):
    return await shipping_service.status_in_transit(shipping_id=shipping_id, db=db)


@router.post("/shippings/{shipping_id}/loads/finished",
             dependencies=[Depends(JWTBearer()),
                           Depends(get_db)],
             response_model=None,
             status_code=status.HTTP_200_OK)
async def status_in_finished(shipping_id: int, db: AsyncSession = Depends(get_db)):
    return await shipping_service.status_finished(shipping_id=shipping_id, db=db)


@router.post("/shippings/{shipping_id}/coordinates",
             dependencies=[Depends(JWTBearer()),
                           Depends(get_db)],
             response_model=ShippingViewSchema,
             status_code=status.HTTP_200_OK)
async def coordinates(payload: ShippingCoordinate, shipping_id: int, db: AsyncSession = Depends(get_db)):
    return await shipping_service.coordinates(payload=payload, shipping_id=shipping_id, db=db)
