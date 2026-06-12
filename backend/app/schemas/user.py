from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    SYSTEM_ADMINISTRATOR = "system_administrator"
    ERP_MANAGER = "erp_manager"
    CRM_SPECIALIST = "crm_specialist"
    WAREHOUSE_MANAGER = "warehouse_manager"
    WAREHOUSE_SUPERVISOR = "warehouse_supervisor"
    SALES_MANAGER = "sales_manager"
    EMPLOYEE = "employee"

class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    role: UserRole = UserRole.EMPLOYEE

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True