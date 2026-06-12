from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
from ..core.database import get_db
from ..core.dependencies import require_role
from ..models.user import User, UserRole
from ..models.product import Product
from ..models.inventory import Inventory
from ..schemas.product import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter(prefix="/api/wms", tags=["WMS"])

@router.get("/products", response_model=List[ProductResponse])
def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR, UserRole.WAREHOUSE_MANAGER, UserRole.WAREHOUSE_SUPERVISOR, UserRole.SALES_MANAGER, UserRole.EMPLOYEE]))
):
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    products = query.offset(skip).limit(limit).all()
    return products

@router.post("/products", response_model=ProductResponse)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR, UserRole.WAREHOUSE_MANAGER, UserRole.WAREHOUSE_SUPERVISOR]))
):
    existing = db.query(Product).filter(Product.sku == product_data.sku).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product with this SKU already exists")
    
    new_product = Product(**product_data.dict())
    db.add(new_product)
    db.flush()
    
    # Create inventory record
    inventory = Inventory(product_id=new_product.id, stock_quantity=0, reserved_quantity=0)
    db.add(inventory)
    
    db.commit()
    db.refresh(new_product)
    return new_product

@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR, UserRole.WAREHOUSE_MANAGER, UserRole.WAREHOUSE_SUPERVISOR, UserRole.SALES_MANAGER, UserRole.EMPLOYEE]))
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR, UserRole.WAREHOUSE_MANAGER, UserRole.WAREHOUSE_SUPERVISOR]))
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    for field, value in product_data.dict(exclude_unset=True).items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product

@router.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if product has orders
    from ..models.order import OrderItem
    has_orders = db.query(OrderItem).filter(OrderItem.product_id == product_id).first()
    if has_orders:
        raise HTTPException(status_code=400, detail="Cannot delete product with existing orders")
    
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}

@router.get("/inventory")
def get_inventory(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR, UserRole.WAREHOUSE_MANAGER, UserRole.WAREHOUSE_SUPERVISOR]))
):
    inventory = db.query(Inventory).all()
    result = []
    for inv in inventory:
        result.append({
            "product_id": inv.product_id,
            "product_name": inv.product.name,
            "sku": inv.product.sku,
            "stock_quantity": inv.stock_quantity,
            "reserved_quantity": inv.reserved_quantity,
            "available_quantity": inv.stock_quantity - inv.reserved_quantity
        })
    return result

@router.put("/inventory/{product_id}")
def update_inventory(
    product_id: int,
    stock_quantity: Decimal,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR, UserRole.WAREHOUSE_MANAGER, UserRole.WAREHOUSE_SUPERVISOR]))
):
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    
    inventory.stock_quantity = stock_quantity
    db.commit()
    return {"message": "Inventory updated", "stock_quantity": float(stock_quantity)}

@router.get("/inventory/low")
def get_low_stock(
    threshold: int = Query(10, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR, UserRole.WAREHOUSE_MANAGER, UserRole.WAREHOUSE_SUPERVISOR]))
):
    low_stock = db.query(Inventory).filter(Inventory.stock_quantity <= threshold).all()
    result = []
    for inv in low_stock:
        result.append({
            "product_id": inv.product_id,
            "product_name": inv.product.name,
            "sku": inv.product.sku,
            "stock_quantity": inv.stock_quantity
        })
    return result