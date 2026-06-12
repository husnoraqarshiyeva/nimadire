from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class Supplier(Base):
    """
    Represents a garment supplier from whom TrendWear sources products.
    Suppliers are linked to products via SupplierProduct and to shipments.
    """
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    contact_person = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    address = Column(Text)
    country = Column(String, nullable=False, default="Uzbekistan")
    tax_id = Column(String, unique=True)
    is_active = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to shipments
    shipments = relationship("Shipment", back_populates="supplier")
