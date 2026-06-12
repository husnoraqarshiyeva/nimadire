from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from ..core.database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    SYSTEM_ADMINISTRATOR = "system_administrator"
    ERP_MANAGER = "erp_manager"
    CRM_SPECIALIST = "crm_specialist"
    WAREHOUSE_MANAGER = "warehouse_manager"
    WAREHOUSE_SUPERVISOR = "warehouse_supervisor"
    SALES_MANAGER = "sales_manager"
    EMPLOYEE = "employee"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.EMPLOYEE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())