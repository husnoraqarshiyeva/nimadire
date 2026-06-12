from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True, nullable=False)
    stock_quantity = Column(Numeric(10, 2), default=0)
    reserved_quantity = Column(Numeric(10, 2), default=0)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())

    product = relationship("Product")