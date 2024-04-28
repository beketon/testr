from enum import Enum

from sqlalchemy import (DECIMAL, Boolean, Column, Float, ForeignKey, Integer,
                        String, Table, UniqueConstraint, text)
from sqlalchemy.orm import relationship

from src.common.models import TimestampMixin
from src.database import Base
from src.shipping.models import Shipping, ShippingRespond


class Group(Base):
    __tablename__ = 'fastapi_auth_group'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), comment="group name")
    name_ru = Column(String(150), nullable=True,
                     comment="group name in English")
    user = relationship("Users", back_populates="group", )
    permissions = relationship(
        "Permission",
        secondary="fastapi_auth_group_permission",
        back_populates="groups"
    )


class ReviewsDriver(Base, TimestampMixin):
    __tablename__ = 'reviews_driver'
    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    driver = relationship(
        "Users",
        back_populates="review",
        lazy="selectin",
        foreign_keys=[driver_id])
    star = Column(Float, nullable=True)
    comment = Column(String, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    creator = relationship(
        "Users",
        back_populates="review_creator",
        lazy="selectin",
        foreign_keys=[creator_id])


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    middle_name = Column(String, nullable=True)
    email = Column(String, nullable=False, unique=True)
    phone = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)
    is_superuser = Column(Boolean, server_default=text(
        'false'), comment="Are you a super administrator")
    is_active = Column(Boolean, server_default=text('true'),
                       comment="Whether to engrave to log in")
    is_delete = Column(Boolean, server_default=text(
        'false'), comment="delete or not")
    is_direction_user = Column(Boolean, server_default=text(
        'false'), comment="Is it a direction user")
    group_id = Column(Integer, ForeignKey(
        "fastapi_auth_group.id"), nullable=True)
    group = relationship("Group", back_populates="user", lazy="selectin")
    creator = Column(Integer, ForeignKey("users.id"), nullable=True)
    city = Column(Integer, ForeignKey("cities.id"), nullable=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=True)
    longitude = Column(Float, nullable=True)
    latitude = Column(Float, nullable=True)
    car_mark = Column(String, nullable=True)
    car_plate_number = Column(String, nullable=True)
    car_engine_volume = Column(Float, nullable=True)
    device_registration_id = Column(String, nullable=True)
    shipping_driver = relationship(
        "ShippingRespond",
        back_populates="driver",
        foreign_keys=ShippingRespond.driver_id)
    shipping = relationship(
        "Shipping", back_populates="driver", foreign_keys=Shipping.driver_id)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    direction_id = Column(Integer, ForeignKey("directions.id"), nullable=True)
    direction = relationship(
        "Directions",
        back_populates="user",
        lazy="selectin"
    )
    review = relationship(
        "ReviewsDriver",
        back_populates="driver",
        foreign_keys=ReviewsDriver.driver_id)
    rating = Column(Float, nullable=True)
    review_creator = relationship(
        "ReviewsDriver",
        back_populates="creator",
        foreign_keys=ReviewsDriver.creator_id)
    selected_orders = Column(Integer, default=0)
    total_profit = Column(Float, default=0)
    delivered_orders = Column(Integer, default=0)
    orders = relationship("UsersOrders", back_populates="user")

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"

    @property
    def fl_name(self):
        return f"{self.last_name} {self.first_name}"


auth_group_permission = Table(  # Many-to-many third-party tables are actually generated by themselves. .
    'fastapi_auth_group_permission',
    Base.metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("group_id", Integer, ForeignKey("fastapi_auth_group.id")),
    Column("codename", String(100), ForeignKey(
        "fastapi_auth_permission.codename")),
    UniqueConstraint('group_id', 'codename',
                     name='idx_group_id_permission_id'),
)


class Permission(Base):
    __tablename__ = 'fastapi_auth_permission'
    name = Column(String(128), unique=True, index=True,
                  comment="Permission Name")  # Permission name
    # The permission field is also the field for us to judge the permission input
    codename = Column(
        String(100), comment="Permission Field", primary_key=True)
    groups = relationship(
        "Group",
        secondary="fastapi_auth_group_permission",
        back_populates="permissions"
    )

    def __str__(self):
        return self.name


class EmailCode(Base, TimestampMixin):
    __tablename__ = 'email_code'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), nullable=False, comment="email")
    user_id = Column(Integer, ForeignKey("users.id"))
    code = Column(String(100), nullable=False, comment="code")


class OTPType(Enum):
    DRIVER_CONTRACT = "DRIVER_CONTRACT"
    PUBLIC_OFFER = "PUBLIC_OFFER"
    WAIVER_AGREEMENT = "WAIVER_AGREEMENT"


class OTPSigningCode(Base, TimestampMixin):
    __tablename__ = 'otp_signing_code'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    shipping_id = Column(Integer, ForeignKey("shipping.id"), nullable=True)
    code = Column(String(100), nullable=False, comment="code")
    phone = Column(String(100), nullable=False, comment="phone")
    is_used = Column(Boolean, server_default=text('false'),
                     comment="Whether to use it or not")
    otp_type = Column(String(100), nullable=True, comment="otp type")


class UsersOrders(Base, TimestampMixin):
    __tablename__ = 'users_orders'

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    status = Column(String, nullable=False)
    user = relationship("Users", back_populates="orders")
    order = relationship("Orders", back_populates="users")
