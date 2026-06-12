from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
from ..core.database import get_db
from ..core.dependencies import require_role
from ..models.user import User, UserRole
from ..models.customer import Customer
from ..models.product import Product
from ..models.order import Order, OrderItem, OrderStatus
from ..models.inventory import Inventory
from ..schemas.order import OrderCreate, OrderUpdate, OrderResponse

router = APIRouter(prefix="/api/erp", tags=["ERP"])

@router.get("/orders", response_model=List[OrderResponse])
def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[OrderStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR, UserRole.ERP_MANAGER, UserRole.SALES_MANAGER, UserRole.EMPLOYEE]))
):
    query = db.query(Order)
    if status:
        query = query.filter(Order.status == status)
    orders = query.offset(skip).limit(limit).all()
    return orders

@router.post("/orders", response_model=OrderResponse)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR, UserRole.ERP_MANAGER, UserRole.SALES_MANAGER]))
):
    # Verify customer exists
    customer = db.query(Customer).filter(Customer.id == order_data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Create order
    new_order = Order(
        customer_id=order_data.customer_id,
        notes=order_data.notes,
        status=OrderStatus.PENDING
    )
    db.add(new_order)
    db.flush()
    
    total = Decimal('0')
    # Process each item
    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            db.rollback()
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        
        # Check inventory
        inventory = db.query(Inventory).filter(Inventory.product_id == item.product_id).first()
        if not inventory or inventory.stock_quantity < item.quantity:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Insufficient stock for product {product.name}")
        
        subtotal = product.unit_price * item.quantity
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=product.unit_price,
            subtotal=subtotal
        )
        db.add(order_item)
        total += subtotal
        
        # Reserve stock
        inventory.reserved_quantity += item.quantity
    
    new_order.total_amount = total
    db.commit()
    db.refresh(new_order)
    return new_order

@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR, UserRole.ERP_MANAGER, UserRole.SALES_MANAGER, UserRole.EMPLOYEE]))
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.put("/orders/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR, UserRole.ERP_MANAGER, UserRole.SALES_MANAGER]))
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order_data.status:
        order.status = order_data.status
    if order_data.notes is not None:
        order.notes = order_data.notes
    
    db.commit()
    db.refresh(order)
    return order

@router.delete("/orders/{order_id}")
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR]))
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Release reserved stock
    for item in order.items:
        inventory = db.query(Inventory).filter(Inventory.product_id == item.product_id).first()
        if inventory:
            inventory.reserved_quantity -= item.quantity
    
    db.delete(order)
    db.commit()
    return {"message": "Order deleted successfully"}

@router.put("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    status: OrderStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR, UserRole.ERP_MANAGER, UserRole.SALES_MANAGER]))
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status
    db.commit()
    return {"message": f"Order status updated to {status.value}"}

@router.get("/orders/customer/{customer_id}")
def get_orders_by_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR, UserRole.ERP_MANAGER, UserRole.SALES_MANAGER]))
):
    orders = db.query(Order).filter(Order.customer_id == customer_id).all()
    return orders