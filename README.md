# b-express

## Landscape
sd
http://api-test.b-express-platform.kz/

http://api.b-express-platform.kz/

## installation

needs libreoffice in ubuntu

- Update lead

```json
{
  "address": "Almaty",
  "courier": 1,
  "delivery_type": "DELIVERY",
  "cargo_pickup_type": "PICKUP", // PICKUP, DELIVERY
  "description": "Some description",
  "direction_id": 1,
  "insurance": 10,
  "payment": {
    "amount": 100,
    "bin": "123456789012",
    "currency": "KZT",
    "payer_type": "SENDER",
    "payment_type": "CASH"
  },
  "receiver_fio": "John Doe",
  "receiver_phone": "+77785547554",
  "sender_fio": "John Doe",
  "sender_phone": "+77785547554",
  "total_volume": 10,
  "total_weight": 10,
  "warehouse_id": 1
}
```

- Добавить на склад товар

POST /warehouses/id/add

Request

```json
{
    "order_item_ids": [
        1,2,3,4,5
    ]
}
```

Товар должен добавиться в склад.

Получение товаров по id перевозки

GET /order_items/?shipping_id=1213

OrderOutScheme

```json
[{
  "id": 1,
  "address": "Almaty",
  "courier": 1,
  "description": "Some description",
  "sender_fio": "John Doe",
  "sender_phone": "+77785547554",
  "receiver_fio": "John Doe",
  "receiver_phone": "+77785547554",
  "total_weight": 10.0,
  "total_volume": 10.0,
  "insurance": 10.0,
  "order_items_number": 1,
  "created_at": "2021-06-29T16:00:00",
  "is_public_offer_accepted": true,
  "is_active": true,
  "order_status": "NEW",
  "delivery_type": "DELIVERY",
  "public_offer_url": "https://example.com",
  "direction": {
      "id": 1,
      "name": "Almaty - Nur-Sultan"
  },
  "payment": {
      "amount": 100.0,
      "currency": "KZT",
      "payment_type": "CASH",
      "payer_type": "SENDER",
      "bin": "123456789012",
      "payment_status": "PAID"
  },
  "warehouse": {
      "id": 1,
      "name": "Almaty"
  }
}]
```

Данные в этом респонсе должны выводиться без expenses, order_items, action_histories

- Когда начинается погрузка, то через девайс направления создается новая перевозка из данных направления

POST /shippings

```json
{
  "shipping_type": "AIR",
  "direction_id": 2
}
```

- Добавить историю трэкинга в заказ

GET "/orders/{order_id}

```json
{
  ... //extend OrderOutScheme
  "order_items": [{
    "created_at": "2021-09-16T10:54:13.000Z",
    "action_description": "Заказ создан",
    "action_code": "ORDER_CREATED"
  }]
}
```

- Добавить причину отмены заказа
PATCH /orders/id/cancelled

```
{
  cancellation_reason: "Груз не подходил по параметрам, не упакован"
}
```

- Добавить причину недоставленного товара

PATCH /orders/id/not_delivered

```
{
  not_delivered_reason: "Не дозвонились до клиента"
}
```

## Statistics

### Big numbers

1. Сложить веса всех товаров и показать на странице

GET /statistics/total_weight

```json
{
  total_weight: 213123.213
}
```

2. GET /statistics/total_volume

```json
{
  total_volume: 213123.213
}
```

3. GET /statistics/total_order_items_count

```json 
{
  total_order_items_count: 213123
}
```

Orders

GET /statistics/orders?start_date=2024-02-31&end_date=2024-02-31&directions=1&directions=2

{
    {
        "status": "CANCELLED",
        "count": 213,
    },
    {
        "status": "DELIVERED",
        "count": 213,
    },
    {
        "status": "PENDING",
        "count": 213
    }
}

Barplot

GET /statisics/shippings?start_date=2024-02-31&end_date=2024-02-31&directions=1&directions=2

[
    {
        "shipping_type": "AIR",
        "count": 213,
    },
    {
        "shipping_type": "ROAD",
        "count": 213,
    },
    {
        "shipping_type": "RAIL",
        "count": 213
    }
]

Payment type

GET /statisics/payments?start_date=2024-02-31&end_date=2024-02-31&directions=1&directions=2

[
    {
        "payment_type": "CASH",
        "count": 213,
    },
    {
        "payment_type": "ONLINE",
        "count": 213,
    }
]

Table of couriers

GET /statisics/couriers

| Courier Name | Number of Selected Orders | Total Profit from Orders | Number of Accepted Items in Warehouse |
|--------------|---------------------------|--------------------------|--------------------------------------|
| Courier 1    | 100                       | $5000                    | 200                                  |
| Courier 2    | 150                       | $7500                    | 300                                  |
| Courier 3    | 120                       | $6000                    | 250                                  |

