from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, String, Numeric, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum


class ShipmentStatus(str, enum.Enum):
    PENDING     = "pending"
    IN_TRANSIT  = "in_transit"
    CUSTOMS     = "customs_clearance"
    ARRIVED     = "arrived"
    RECEIVED    = "received"
    CANCELLED   = "cancelled"


class Shipment(Base):
    """
    Represents an inbound shipment of stock from a supplier to a TrendWear warehouse.
    Receiving a shipment updates inventory stock levels.
    """
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    reference_number = Column(String, unique=True, nullable=False, index=True)
    status = Column(Enum(ShipmentStatus), default=ShipmentStatus.PENDING)
    expected_arrival = Column(DateTime(timezone=True))
    actual_arrival = Column(DateTime(timezone=True))
    shipping_cost = Column(Numeric(12, 2), default=0)
    carrier = Column(String)
    tracking_number = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    supplier = relationship("Supplier", back_populates="shipments")
    items = relationship("ShipmentItem", back_populates="shipment", cascade="all, delete-orphan")


class ShipmentItem(Base):
    """
    A line item within a shipment — links to a product and carries expected quantity.
    """
    __tablename__ = "shipment_items"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity_expected = Column(Numeric(10, 2), nullable=False)
    quantity_received = Column(Numeric(10, 2), default=0)
    unit_cost = Column(Numeric(10, 2), nullable=False)

    shipment = relationship("Shipment", back_populates="items")
    product = relationship("Product")
