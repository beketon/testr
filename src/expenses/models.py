from sqlalchemy import DECIMAL, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from src.database import Base

order_expenses = Table('order_expenses', Base.metadata,
    Column('order_id', Integer, ForeignKey('orders.id')),
    Column('expense_id', Integer, ForeignKey('expenses.id'))
)

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    orders = relationship("Orders", secondary=order_expenses, back_populates="expenses")
    creator = Column(Integer, ForeignKey("users.id"), nullable=False)