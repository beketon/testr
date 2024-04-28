from fastapi import Depends, HTTPException, Query, status
from sqlalchemy import select, update, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.dao.base import BaseDao
from src.database import get_db
from src.tarifs.exceptions import TarifNotFound
from src.tarifs.models import Tarifs
from src.tarifs.schemas import (CalculationType, TarifCreateSchemas,
                                TarifUpdateSchemas, TarifViewSchemas, TarifLimitSchemas, DeliveryTarifSchemas)


DELIVERY_WEIGHT_LIMIT = 500
DELIVERY_VOLUME_LIMIT = 15
TARIF_LIMIT = 100


class TarifService(BaseDao):
    class_name = Tarifs

    async def get_tarifs(self, calculation_type: CalculationType, db: AsyncSession = Depends(get_db), amount: int | None = None, direction_id: int | None = None) -> list[TarifViewSchemas]:
        query = select(Tarifs).filter_by(
            calculation_type=calculation_type).order_by(
            Tarifs.amount)
        if amount is not None:
            query = query.filter_by(amount=amount)
        if direction_id is not None:
            query = query.filter_by(direction_id=direction_id)
        return (await db.execute(query)).scalars().all()

    async def get_delivery_tarifs(self, calculation_type: CalculationType, db: AsyncSession = Depends(get_db),
                                  amount: int | None = None, direction_id: int | None = None) -> list[
        DeliveryTarifSchemas]:
        if calculation_type != CalculationType.DELIVERY_VOLUME.value and calculation_type != CalculationType.DELIVERY_WEIGHT.value and calculation_type != CalculationType.SENDER_CARGO_PICKUP_WEIGHT.value and calculation_type != CalculationType.SENDER_CARGO_PICKUP_VOLUME.value:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f'calculation_type should be {CalculationType.DELIVERY_VOLUME.value} or {CalculationType.DELIVERY_WEIGHT.value}')
        query = select(
            Tarifs.price,
            func.min(Tarifs.amount).label("starting_amount"),
            func.max(Tarifs.amount).label("ending_amount"),
            Tarifs.calculation_type,
            Tarifs.direction_id
        ).where(
            Tarifs.calculation_type == calculation_type
        ).group_by(
            Tarifs.price,
            Tarifs.calculation_type,
            Tarifs.direction_id
        ).order_by(
            func.min(Tarifs.amount)
        )

        if amount is not None:
            query = query.having(
                (func.min(Tarifs.amount) <= amount) & (func.max(Tarifs.amount) >= amount)
            )
        if direction_id is not None:
            query = query.where(Tarifs.direction_id == direction_id)

        result = await db.execute(query)
        tarifs = result.all()

        return [DeliveryTarifSchemas(
            calculation_type=calculation_type,
            starting_amount=tarif.starting_amount,
            ending_amount=tarif.ending_amount,
            price=tarif.price,
            direction_id=tarif.direction_id
        ) for tarif in tarifs]


    async def get_tarifs_limit(self, direction_id: int, calculation_type: CalculationType, db: AsyncSession = Depends(get_db)) -> list[TarifLimitSchemas]:
        query = select(Tarifs).filter_by(
            direction_id=direction_id,
            calculation_type=calculation_type,
            is_limit=True)
        return (await db.execute(query)).scalars().all()

    async def create_update_tarifs_limit(self, payload: TarifLimitSchemas, db: AsyncSession = Depends(get_db)) -> list[TarifLimitSchemas]:
        try:
            existing_tarif = await db.execute(select(Tarifs).filter_by(calculation_type=payload.calculation_type,
                                                                       direction_id=payload.direction_id, is_limit=True))
            existing_tarif = existing_tarif.scalars().first()
            if existing_tarif:
                await db.execute(update(Tarifs).where(Tarifs.id == existing_tarif.id).values(price=payload.price))
            else:
                new_tarif = Tarifs(calculation_type=payload.calculation_type,
                                   direction_id=payload.direction_id, amount=0, price=payload.price, is_limit=True)
                db.add(new_tarif)
            await db.commit()
        except IntegrityError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e._message))
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)

    async def create_tarifs(self, payload: TarifCreateSchemas, db: AsyncSession = Depends(get_db)) -> list[TarifViewSchemas]:
        if payload.ending_amount > DELIVERY_WEIGHT_LIMIT:
            raise HTTPException(status_code=400, detail="ending amount should be less than 500")
        try:
            tarifs = []
            price = payload.starting_price
            for amount in range(payload.starting_amount, payload.ending_amount + 1):
                tarif_data = {'calculation_type': payload.calculation_type,
                              'direction_id': payload.direction_id, 'amount': amount, 'price': price}
                price += payload.increment
                if payload.calculation_type == CalculationType.VOLUME or payload.calculation_type == CalculationType.WEIGHT or payload.calculation_type == CalculationType.HANDLING:
                    existing_tarif = await db.execute(select(Tarifs).filter_by(calculation_type=payload.calculation_type,
                                                                               direction_id=payload.direction_id,
                                                                               amount=amount))
                    existing_tarif = existing_tarif.scalars().first()
                else:
                    existing_tarif = await db.execute(
                        select(Tarifs).filter_by(calculation_type=payload.calculation_type, amount=amount))
                    existing_tarif = existing_tarif.scalars().first()
                if existing_tarif:
                    await db.execute(update(Tarifs).where(Tarifs.id == existing_tarif.id).values(price=tarif_data['price']))
                else:
                    tarifs.append(tarif_data)
            if tarifs:
                await db.run_sync(lambda session: session.bulk_insert_mappings(Tarifs, tarifs))
            await db.commit()
        except IntegrityError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e._message))

        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)

    async def set_delivery_tarifs(self, payloads: list[DeliveryTarifSchemas], db: AsyncSession = Depends(get_db)) -> None:
        for payload in payloads:
            if payload.calculation_type != CalculationType.DELIVERY_VOLUME.value and payload.calculation_type != CalculationType.DELIVERY_WEIGHT.value and payload.calculation_type != CalculationType.SENDER_CARGO_PICKUP_VOLUME.value and payload.calculation_type != CalculationType.SENDER_CARGO_PICKUP_WEIGHT.value:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f'calculation_type should be {CalculationType.DELIVERY_VOLUME.value} or {CalculationType.DELIVERY_WEIGHT.value}')
            if (payload.calculation_type == CalculationType.DELIVERY_WEIGHT.value or payload.calculation_type == CalculationType.SENDER_CARGO_PICKUP_WEIGHT.value) and payload.ending_amount > DELIVERY_WEIGHT_LIMIT:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ending amount should be less than 500")
            if (payload.calculation_type == CalculationType.DELIVERY_VOLUME.value or payload.calculation_type == CalculationType.SENDER_CARGO_PICKUP_VOLUME.value) and payload.ending_amount > DELIVERY_VOLUME_LIMIT:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ending amount should be less than 15")
        try:
            for payload in payloads:
                tarifs = []
                price = payload.price
                for amount in range(payload.starting_amount, payload.ending_amount + 1):
                    tarif_data = {'calculation_type': payload.calculation_type,
                                  'direction_id': payload.direction_id, 'amount': amount, 'price': price}

                    existing_tarif = await db.execute(select(Tarifs).filter_by(calculation_type=payload.calculation_type,
                                                                               direction_id=payload.direction_id,
                                                                               amount=amount))
                    existing_tarif = existing_tarif.scalars().first()
                    if existing_tarif:
                        await db.execute(update(Tarifs).where(Tarifs.id == existing_tarif.id).values(price=tarif_data['price']))
                    else:
                        tarifs.append(tarif_data)
                if tarifs:
                    await db.run_sync(lambda session: session.bulk_insert_mappings(Tarifs, tarifs))
                await db.commit()
        except IntegrityError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e._message))

        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)

    async def update_tarifs(self, payload: list[TarifUpdateSchemas], db: AsyncSession = Depends(get_db)) -> list[TarifViewSchemas]:
        try:
            tarifs = [{'id': tarif.id, 'price': tarif.price} for tarif in payload]
            await db.run_sync(lambda session: session.bulk_update_mappings(Tarifs, tarifs))
            await db.commit()
        except IntegrityError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e._message))

        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)


tarif_service = TarifService()
