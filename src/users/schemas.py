from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr

from src.directions.schemas import DirectionViewSchemas
from src.geography.schemas import CityOut, DistrictShortViewSchemas


class UserSchemas(BaseModel):
    email: EmailStr
    password: str
    device_registration_id: str | None = None

    model_config = {
        "json_schema_extra": {
            "example":
            {
                "email": "zshanabek@gmail.com",
                "password": "132312qQ",
                "device_registration_id": "random_device_registration_id"
            }
        }
    }


class GroupEnum(Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    DRIVER = "DRIVER"
    COURIER = "COURIER"
    WAREHOUSE_MANAGER = "WAREHOUSE_MANAGER"
    ACCOUNTANT = "ACCOUNTANT"
    DIRECTION_USER = "DIRECTION_USER"


GROUP_LOCALISATION = {
    GroupEnum.ADMIN: {
        "ru": "Администратор",
        "en": "Administrator"
    },
    GroupEnum.MANAGER: {
        "ru": "Менеджер",
        "en": "Manager"
    },
    GroupEnum.DRIVER: {
        "ru": "Водитель",
        "en": "Driver"
    },
    GroupEnum.COURIER: {
        "ru": "Курьер",
        "en": "Courier"
    },
    GroupEnum.WAREHOUSE_MANAGER: {
        "ru": "Приемосдатчик",
        "en": "Warehouse manager"
    },
    GroupEnum.ACCOUNTANT: {
        "ru": "Бухгалтер",
        "en": "Accountant"
    },
    GroupEnum.DIRECTION_USER: {
        "ru": "Пользователь направления",
        "en": "Direction user"
    }
}


class UserUpdateSchemas(BaseModel):
    first_name: str
    last_name: str
    middle_name: str
    phone: str
    longitude: float | None = None
    latitude: float | None = None
    group_id: int
    email: EmailStr
    city_id: int
    district_id: int | None = None
    car_mark: str | None = None
    car_plate_number: str | None = None
    car_engine_volume: float | None = None
    warehouse_id: int | None = None
    direction_id: int | None = None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example":
            {
                "first_name": "Zhanabek",
                "last_name": "Zhumagulov",
                "middle_name": "Zhanabekovich",
                "email": "user@mail.com",
                "phone": "+77072222222",
                "longitude": 1.0,
                "latitude": 1.0,
                "group_id": 1,
                "city_id": 1,
                "district_id": 1,
                "car_mark": "Toyota",
                "car_plate_number": "123ABC",
                "car_engine_volume": 1.6,
                "warehouse_id": 1,
                "direction_id": 1
            }
        }
    }


class UserSetPasswordSchemas(BaseModel):
    password: str
    confirm_password: str

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example":
            {
                "password": "132312qQ",
                "confirm_password": "132312qQ"
            }
        }
    }


class UserCreateSchemas(UserUpdateSchemas):
    email: EmailStr
    ...

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example":
            {
                "first_name": "Zhanabek",
                "last_name": "Zhumagulov",
                "middle_name": "Zhanabekovich",
                "email": "zshanabek@gmail.com",
                "phone": "+77072222222",
                "longitude": 1.0,
                "latitude": 1.0,
                "group_id": 1,
                "city_id": 1,
                "district_id": 1,
                "car_mark": "Toyota",
                "car_plate_number": "123ABC",
                "car_engine_volume": 1.6,
                "warehouse_id": 1,
                "direction_id": 1
            }
        }
    }


class UserConfirmationEmailSchemas(BaseModel):
    code: str
    user_id: int
    password: str
    confirm_password: str


class PermissionViewSchemas(BaseModel):
    name: str
    codename: str

    class Config:
        from_attributes = True


class GroupViewSchemasList(BaseModel):
    id: int
    name: str
    name_ru: str
    user_count: int = 0,
    permissions: list[PermissionViewSchemas]

    class Config:
        from_attributes = True


class GroupShortOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class GroupViewSchemas(GroupShortOut):
    permissions: list[str]

    class Config:
        from_attributes = True


class UserViewSchemas(BaseModel):
    id: int
    email: EmailStr
    is_superuser: bool
    is_active: bool
    is_delete: bool
    password: str | None = None
    group: GroupViewSchemas | None = None
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    phone: str | None = None
    city: CityOut | None = None
    creator: int | None = None
    district: DistrictShortViewSchemas | None = None
    longitude: float | None = None
    latitude: float | None = None
    car_mark: str | None = None
    car_plate_number: str | None = None
    car_engine_volume: float | None = None
    direction_id: int | None = None
    direction: DirectionViewSchemas | None = None
    warehouse_id: int | None = None
    rating: float | None = None

    class Config:
        from_attributes = True


class UserShippingViewSchemas(BaseModel):
    id: int
    email: EmailStr
    is_superuser: bool
    is_active: bool
    is_delete: bool
    password: str | None = None
    group: GroupShortOut | None = None
    first_name: str
    last_name: str
    middle_name: str | None = None
    phone: str
    city: int | None = None
    creator: int | None = None
    district: int | None = None
    longitude: float | None = None
    latitude: float | None = None
    car_mark: str | None = None
    car_plate_number: str | None = None
    car_engine_volume: float | None = None
    rating: float | None = None
    reviews_number: int | None = None

    class Config:
        from_attributes = True


class UserPaginated(BaseModel):
    page: int
    limit: int
    total: int
    pages_number: int
    data: list[UserViewSchemas]


class UserShortViewSchemas(BaseModel):
    id: int
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    rating: float | None = None
    group_id: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class DataToken(BaseModel):
    id: str | None = None


class GroupCreateSchemas(BaseModel):
    name: str
    name_ru: str | None = None
    permissions: list[str]

    model_config = {
        "json_schema_extra": {
            "example":
            {
                "name": "MANAGER",
                "name_ru": "Менеджер",
                "permissions": ["CREATE_USER", "UPDATE_USER", "VIEW_USERS", "DELETE_USER"]
            }
        }
    }


class AuthGroupPermissionCreateSchemas(BaseModel):
    group_id: int
    codename: str


class AuthGroupPermissionViewSchemas(BaseModel):
    id: int
    group_id: int
    codename: str

    class Config:
        from_attributes = True


class Permission(str, Enum):
    CREATE_ROLE = 'CREATE_ROLE'

    UPDATE_USER = 'UPDATE_USER'
    VIEW_USERS = 'VIEW_USERS'
    CREATE_USER = 'CREATE_USER'
    DELETE_USER = 'DELETE_USER'

    CREATE_ORDER = 'CREATE_ORDER'
    UPDATE_ORDER = 'UPDATE_ORDER'
    DELETE_ORDER = 'DELETE_ORDER'
    VIEW_ORDER = 'VIEW_ORDER'
    CANCEL_ORDER = 'CANCEL_ORDER'
    SIGN_ORDER = 'SIGN_ORDER'
    DELIVER_ORDER = 'DELIVER_ORDER'
    ACCEPT_ORDER_TO_WAREHOUSE = 'ACCEPT_ORDER_TO_WAREHOUSE'
    UPDATE_ORDER_STATUS = 'UPDATE_ORDER_STATUS'
    UPDATE_PAYMENT_STATUS_FL = 'UPDATE_PAYMENT_STATUS_FL'
    UPDATE_PAYMENT_STATUS_UL = 'UPDATE_PAYMENT_STATUS_UL'
    CANCEL_ORDER_LEAD = 'CANCEL_ORDER_LEAD'
    ACCEPT_ORDER_LEAD = 'ACCEPT_ORDER_LEAD'

    VIEW_STATISTICS = 'VIEW_STATISTICS'

    GENERATE_REPORT = 'GENERATE_REPORT'

    CREATE_WAREHOUSE = 'CREATE_WAREHOUSE'
    UPDATE_WAREHOUSE = 'UPDATE_WAREHOUSE'
    DELETE_WAREHOUSE = 'DELETE_WAREHOUSE'
    VIEW_WAREHOUSE = 'VIEW_WAREHOUSE'
    VIEW_WAREHOUSE_ORDER = 'VIEW_WAREHOUSE_ORDER'

    CREATE_SHIPPING = 'CREATE_SHIPPING'
    UPDATE_SHIPPING = 'UPDATE_SHIPPING'
    DELETE_SHIPPING = 'DELETE_SHIPPING'
    VIEW_SHIPPING = 'VIEW_SHIPPING'
    ACCEPT_SHIPPING_RESPOND = 'ACCEPT_SHIPPING_RESPOND'

    CREATE_DRIVER_RATING = 'CREATE_DRIVER_RATING'
    VIEW_DRIVER = 'VIEW_DRIVER'

    CREATE_EXPENSE = 'CREATE_EXPENSE'
    UPDATE_EXPENSE = 'UPDATE_EXPENSE'
    DELETE_EXPENSE = 'DELETE_EXPENSE'
    VIEW_EXPENSE = 'VIEW_EXPENSE'

    CREATE_DIRECTION = 'CREATE_DIRECTION'
    UPDATE_DIRECTION = 'UPDATE_DIRECTION'
    DELETE_DIRECTION = 'DELETE_DIRECTION'
    UPDATE_DIRECTION_STATUS = 'UPDATE_DIRECTION_STATUS'
    VIEW_DIRECTION = 'VIEW_DIRECTION'

    CREATE_CITY = 'CREATE_CITY'
    UPDATE_CITY = 'UPDATE_CITY'
    DELETE_CITY = 'DELETE_CITY'
    VIEW_CITY = 'VIEW_CITY'

    CREATE_DISTRICT = 'CREATE_DISTRICT'
    UPDATE_DISTRICT = 'UPDATE_DISTRICT'
    DELETE_DISTRICT = 'DELETE_DISTRICT'
    VIEW_DISTRICT = 'VIEW_DISTRICT'

    VIEW_TARIF = 'VIEW_TARIF'
    EDIT_TARIF = 'EDIT_TARIF'

    VIEW_ROLE = 'VIEW_ROLE'


RUSSIAN_PERMISSIONS_MAP = {
    Permission.CREATE_ROLE: "Создание роли",
    Permission.UPDATE_USER: "Обновление пользователя",
    Permission.VIEW_USERS: "Просмотр пользователей",
    Permission.CREATE_USER: "Создание пользователя",
    Permission.DELETE_USER: "Удаление пользователя",
    Permission.CREATE_ORDER: "Создание заказа",
    Permission.UPDATE_ORDER: "Обновление заказа",
    Permission.UPDATE_PAYMENT_STATUS_FL: "Обновление статуса оплаты физ. лица",
    Permission.UPDATE_PAYMENT_STATUS_UL: "Обновление статуса оплаты юр. лица",
    Permission.DELETE_ORDER: "Удаление заказа",
    Permission.VIEW_ORDER: "Просмотр заказа",
    Permission.CANCEL_ORDER: "Отмена заказа",
    Permission.SIGN_ORDER: "Подписание заказа",
    Permission.DELIVER_ORDER: "Доставка заказа",
    Permission.UPDATE_ORDER_STATUS: "Обновление статуса заказа",
    Permission.CANCEL_ORDER_LEAD: "Отмена лида",
    Permission.ACCEPT_ORDER_LEAD: "Принятие лида",
    Permission.VIEW_STATISTICS: "Просмотр отчета и статистики",
    Permission.GENERATE_REPORT: "Генерация файла отчетов",
    Permission.CREATE_WAREHOUSE: "Создание склада",
    Permission.UPDATE_WAREHOUSE: "Обновление склада",
    Permission.DELETE_WAREHOUSE: "Удаление склада",
    Permission.VIEW_WAREHOUSE: "Просмотр склада",
    Permission.VIEW_WAREHOUSE_ORDER: "Просмотр заказов склада",
    Permission.CREATE_SHIPPING: "Создание перевозки",
    Permission.UPDATE_SHIPPING: "Обновление перевозки",
    Permission.DELETE_SHIPPING: "Удаление перевозки",
    Permission.VIEW_SHIPPING: "Просмотр перевозки",
    Permission.ACCEPT_SHIPPING_RESPOND: "Принятие отклика перевозки",
    Permission.CREATE_DRIVER_RATING: "Добавление рейтинга водителя",
    Permission.VIEW_DRIVER: "Просмотр водителя",
    Permission.CREATE_EXPENSE: "Создание расхода",
    Permission.UPDATE_EXPENSE: "Обновление расхода",
    Permission.DELETE_EXPENSE: "Удаление расхода",
    Permission.VIEW_EXPENSE: "Просмотр расхода",
    Permission.CREATE_DIRECTION: "Создание направления",
    Permission.UPDATE_DIRECTION: "Обновление направления",
    Permission.DELETE_DIRECTION: "Удаление направления",
    Permission.UPDATE_DIRECTION_STATUS: "Обновление статуса направления",
    Permission.CREATE_CITY: "Создание города",
    Permission.UPDATE_CITY: "Обновление города",
    Permission.DELETE_CITY: "Удаление города",
    Permission.CREATE_DISTRICT: "Создание района",
    Permission.UPDATE_DISTRICT: "Обновление района",
    Permission.DELETE_DISTRICT: "Удаление района",
    Permission.ACCEPT_ORDER_TO_WAREHOUSE: "Принятие заказа на склад",
    Permission.VIEW_CITY: "Просмотр города",
    Permission.VIEW_DISTRICT: "Просмотр района",
    Permission.VIEW_DIRECTION: "Просмотр направления",
    Permission.VIEW_TARIF: "Просмотр тарифа",
    Permission.EDIT_TARIF: "Редактирование тарифа",
    Permission.VIEW_ROLE: "Просмотр роли",
}


PERMISSIONS_MAP = {
    GroupEnum.ADMIN: [
        Permission.CREATE_ROLE.value,
        Permission.CREATE_USER.value,
        Permission.DELETE_USER.value,
        Permission.CREATE_ORDER.value,
        Permission.VIEW_USERS.value,
        Permission.UPDATE_ORDER.value,
        Permission.DELETE_ORDER.value,
        Permission.VIEW_ORDER.value,
        Permission.CANCEL_ORDER.value,
        Permission.SIGN_ORDER.value,
        Permission.DELIVER_ORDER.value,
        Permission.UPDATE_ORDER_STATUS.value,
        Permission.CANCEL_ORDER_LEAD.value,
        Permission.ACCEPT_ORDER_LEAD.value,
        Permission.VIEW_STATISTICS.value,
        Permission.GENERATE_REPORT.value,
        Permission.CREATE_WAREHOUSE.value,
        Permission.UPDATE_WAREHOUSE.value,
        Permission.DELETE_WAREHOUSE.value,
        Permission.VIEW_WAREHOUSE.value,
        Permission.VIEW_WAREHOUSE_ORDER.value,
        Permission.CREATE_SHIPPING.value,
        Permission.UPDATE_SHIPPING.value,
        Permission.DELETE_SHIPPING.value,
        Permission.VIEW_SHIPPING.value,
        Permission.ACCEPT_SHIPPING_RESPOND.value,
        Permission.CREATE_DRIVER_RATING.value,
        Permission.VIEW_DRIVER.value,
        Permission.CREATE_EXPENSE.value,
        Permission.UPDATE_EXPENSE.value,
        Permission.DELETE_EXPENSE.value,
        Permission.VIEW_EXPENSE.value,
        Permission.CREATE_DIRECTION.value,
        Permission.UPDATE_DIRECTION.value,
        Permission.DELETE_DIRECTION.value,
        Permission.UPDATE_DIRECTION_STATUS.value,
        Permission.CREATE_CITY.value,
        Permission.UPDATE_CITY.value,
        Permission.DELETE_CITY.value,
        Permission.CREATE_DISTRICT.value,
        Permission.UPDATE_DISTRICT.value,
        Permission.DELETE_DISTRICT.value,
        Permission.VIEW_TARIF.value,
        Permission.EDIT_TARIF.value,
        Permission.VIEW_ROLE.value,
    ],
    GroupEnum.MANAGER: [
        Permission.CREATE_ROLE.value,
        Permission.CREATE_USER.value,
        Permission.DELETE_USER.value,
        Permission.VIEW_USERS.value,
        Permission.CREATE_ORDER.value,
        Permission.UPDATE_ORDER.value,
        Permission.DELETE_ORDER.value,
        Permission.VIEW_ORDER.value,
        Permission.CANCEL_ORDER.value,
        Permission.SIGN_ORDER.value,
        Permission.DELIVER_ORDER.value,
        Permission.UPDATE_ORDER_STATUS.value,
        Permission.CANCEL_ORDER_LEAD.value,
        Permission.ACCEPT_ORDER_LEAD.value,
        Permission.VIEW_STATISTICS.value,
        Permission.GENERATE_REPORT.value,
        Permission.CREATE_WAREHOUSE.value,
        Permission.UPDATE_WAREHOUSE.value,
        Permission.DELETE_WAREHOUSE.value,
        Permission.VIEW_WAREHOUSE.value,
        Permission.VIEW_WAREHOUSE_ORDER.value,
        Permission.CREATE_SHIPPING.value,
        Permission.UPDATE_SHIPPING.value,
        Permission.DELETE_SHIPPING.value,
        Permission.VIEW_SHIPPING.value,
        Permission.ACCEPT_SHIPPING_RESPOND.value,
        Permission.CREATE_DRIVER_RATING.value,
        Permission.VIEW_DRIVER.value,
        Permission.CREATE_EXPENSE.value,
        Permission.UPDATE_EXPENSE.value,
        Permission.DELETE_EXPENSE.value,
        Permission.VIEW_EXPENSE.value,
        Permission.CREATE_DIRECTION.value,
        Permission.UPDATE_DIRECTION.value,
        Permission.DELETE_DIRECTION.value,
        Permission.UPDATE_DIRECTION_STATUS.value,
        Permission.CREATE_CITY.value,
        Permission.UPDATE_CITY.value,
        Permission.DELETE_CITY.value,
        Permission.CREATE_DISTRICT.value,
        Permission.UPDATE_DISTRICT.value,
        Permission.DELETE_DISTRICT.value,
    ],
    GroupEnum.DRIVER: [
        Permission.VIEW_ORDER.value,
        Permission.SIGN_ORDER.value,
        Permission.VIEW_STATISTICS.value,
        Permission.CREATE_SHIPPING.value,
        Permission.UPDATE_SHIPPING.value,
        Permission.VIEW_SHIPPING.value,
        Permission.ACCEPT_SHIPPING_RESPOND.value,
        Permission.VIEW_DRIVER.value,
        Permission.VIEW_EXPENSE.value,
        Permission.CREATE_DIRECTION.value,
        Permission.UPDATE_DIRECTION.value,
        Permission.DELETE_DIRECTION.value,
        Permission.UPDATE_DIRECTION_STATUS.value,
    ],
    GroupEnum.COURIER: [
        Permission.CREATE_ORDER.value,
        Permission.UPDATE_ORDER.value,
        Permission.DELETE_ORDER.value,
        Permission.VIEW_ORDER.value,
        Permission.CANCEL_ORDER.value,
        Permission.SIGN_ORDER.value,
        Permission.DELIVER_ORDER.value,
        Permission.VIEW_STATISTICS.value,
        Permission.VIEW_WAREHOUSE.value,
        Permission.VIEW_WAREHOUSE_ORDER.value,
        Permission.VIEW_SHIPPING.value,
        Permission.VIEW_DRIVER.value,
        Permission.CREATE_EXPENSE.value,
        Permission.UPDATE_EXPENSE.value,
        Permission.DELETE_EXPENSE.value,
        Permission.VIEW_EXPENSE.value,
        Permission.CREATE_DIRECTION.value,
        Permission.UPDATE_DIRECTION.value,
        Permission.DELETE_DIRECTION.value,
        Permission.UPDATE_DIRECTION_STATUS.value,
    ],
    GroupEnum.WAREHOUSE_MANAGER: [
        Permission.UPDATE_ORDER.value,
        Permission.DELETE_ORDER.value,
        Permission.VIEW_ORDER.value,
        Permission.CANCEL_ORDER.value,
        Permission.SIGN_ORDER.value,
        Permission.UPDATE_ORDER_STATUS.value,
        Permission.CANCEL_ORDER_LEAD.value,
        Permission.ACCEPT_ORDER_LEAD.value,
        Permission.VIEW_STATISTICS.value,
        Permission.GENERATE_REPORT.value,
        Permission.CREATE_WAREHOUSE.value,
        Permission.UPDATE_WAREHOUSE.value,
        Permission.DELETE_WAREHOUSE.value,
        Permission.VIEW_WAREHOUSE.value,
        Permission.VIEW_WAREHOUSE_ORDER.value,
        Permission.UPDATE_SHIPPING.value,
        Permission.DELETE_SHIPPING.value,
        Permission.VIEW_SHIPPING.value,
        Permission.VIEW_DRIVER.value,
        Permission.ACCEPT_ORDER_TO_WAREHOUSE.value,
        Permission.CREATE_EXPENSE.value,
        Permission.UPDATE_EXPENSE.value,
        Permission.DELETE_EXPENSE.value,
        Permission.VIEW_EXPENSE.value,
        Permission.CREATE_DIRECTION.value,
        Permission.UPDATE_DIRECTION.value,
        Permission.DELETE_DIRECTION.value,
        Permission.UPDATE_DIRECTION_STATUS.value,
        Permission.CREATE_CITY.value,
        Permission.UPDATE_CITY.value,
        Permission.DELETE_CITY.value,
        Permission.CREATE_DISTRICT.value,
        Permission.UPDATE_DISTRICT.value,
        Permission.DELETE_DISTRICT.value,
    ],
    GroupEnum.ACCOUNTANT: [
        Permission.VIEW_ORDER.value,
        Permission.UPDATE_PAYMENT_STATUS_FL.value,
        Permission.UPDATE_PAYMENT_STATUS_UL.value,
        Permission.VIEW_STATISTICS.value,
        Permission.GENERATE_REPORT.value,
    ],
}


class ReviewsDriverCreateSchema(BaseModel):
    star: float | None = None
    comment: str | None = None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example":
            {
                "star": 1,
                "comment": "Nice job!",
            }
        }
    }


class ReviewsDriverViewSchema(BaseModel):
    id: int
    driver_id: int
    driver: UserShortViewSchemas
    creator_id: int | None
    creator: UserShortViewSchemas | None = None
    star: float | None = None
    comment: str | None = None
    created_at: datetime


class ReviewsDriverListViewSchema(BaseModel):
    data: list[ReviewsDriverViewSchema] = []
    number_of_reviews: int = 0

    class Config:
        from_attributes = True


class ForgotPasswordEmail(BaseModel):
    email: str
    is_mobile_device: bool = False
    base_url: str

    class Config:
        json_schema_extra = {
            "example": {
                "base_url": "http://localhost:8000",
                "is_mobile_device": False,
                "email": "mail@gmail.com"
            }
        }


class ResetForegetPassword(BaseModel):
    secret_token: str
    new_password: str
    confirm_password: str

    class Config:
        json_schema_extra = {
            "example": {
                "secret_token": "ehchchsheeyyshshsgetttdtst",
                "new_password": "password",
                "confirm_password": "password"
            }
        }
