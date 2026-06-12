from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from ..core.dependencies import require_role
from ..models.user import User, UserRole
from ..models.customer import Customer
from ..models.order import Order
from ..schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse

router = APIRouter(prefix="/api/crm", tags=["CRM"])

@router.get("/customers", response_model=List[CustomerResponse])
def get_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR, UserRole.CRM_SPECIALIST, UserRole.SALES_MANAGER, UserRole.EMPLOYEE]))
):
    query = db.query(Customer)
    if search:
        query = query.filter(
            Customer.company_name.ilike(f"%{search}%") |
            Customer.contact_person.ilike(f"%{search}%") |
            Customer.phone.ilike(f"%{search}%")
        )
    customers = query.offset(skip).limit(limit).all()
    return customers

@router.post("/customers", response_model=CustomerResponse)
def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR, UserRole.CRM_SPECIALIST, UserRole.SALES_MANAGER]))
):
    new_customer = Customer(**customer_data.dict())
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer

@router.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR, UserRole.CRM_SPECIALIST, UserRole.SALES_MANAGER, UserRole.EMPLOYEE]))
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.put("/customers/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR, UserRole.CRM_SPECIALIST, UserRole.SALES_MANAGER]))
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    for field, value in customer_data.dict(exclude_unset=True).items():
        setattr(customer, field, value)
    
    db.commit()
    db.refresh(customer)
    return customer

@router.delete("/customers/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    db.delete(customer)
    db.commit()
    return {"message": "Customer deleted successfully"}

@router.get("/customers/{customer_id}/orders")
def get_customer_orders(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR, UserRole.CRM_SPECIALIST, UserRole.SALES_MANAGER]))
):
    orders = db.query(Order).filter(Order.customer_id == customer_id).all()
    return orders