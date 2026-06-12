from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, Numeric, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum


class AlertType(str, enum.Enum):
    LOW_STOCK    = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    OVERSTOCK    = "overstock"
    REORDER      = "reorder_point"


class AlertSeverity(str, enum.Enum):
    INFO     = "info"
    WARNING  = "warning"
    CRITICAL = "critical"


class InventoryAlert(Base):
    """
    Triggered automatically when an inventory record crosses a defined threshold.
    Warehouse Supervisors receive alerts for action.
    """
    __tablename__ = "inventory_alerts"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    alert_type = Column(Enum(AlertType), nullable=False)
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.WARNING)
    threshold_quantity = Column(Numeric(10, 2), nullable=False)
    current_quantity = Column(Numeric(10, 2), nullable=False)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product")
