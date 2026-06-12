from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from decimal import Decimal
from ..core.database import get_db
from ..core.dependencies import require_role
from ..models.user import User, UserRole
from ..models.order import Order, OrderStatus
from ..models.customer import Customer
from ..models.product import Product
from ..models.inventory import Inventory

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("/dashboard")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR, UserRole.SALES_MANAGER, UserRole.WAREHOUSE_MANAGER, UserRole.ERP_MANAGER, UserRole.WAREHOUSE_SUPERVISOR]))
):
    # Total customers
    total_customers = db.query(Customer).count()
    
    # Total products
    total_products = db.query(Product).count()
    
    # Total orders
    total_orders = db.query(Order).count()
    
    # Orders by status
    orders_by_status = {}
    for status in OrderStatus:
        count = db.query(Order).filter(Order.status == status).count()
        orders_by_status[status.value] = count
    
    # Recent orders (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_orders = db.query(Order).filter(Order.created_at >= week_ago).count()
    
    # Total revenue (from completed orders)
    total_revenue = db.query(func.sum(Order.total_amount)).filter(Order.status == OrderStatus.DELIVERED).scalar() or Decimal('0')
    
    # Low stock items
    low_stock = db.query(Inventory).filter(Inventory.stock_quantity <= 10).count()
    
    return {
        "total_customers": total_customers,
        "total_products": total_products,
        "total_orders": total_orders,
        "recent_orders": recent_orders,
        "total_revenue": float(total_revenue),
        "orders_by_status": orders_by_status,
        "low_stock_items": low_stock
    }

@router.get("/sales")
def get_sales_report(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR, UserRole.SALES_MANAGER, UserRole.ERP_MANAGER]))
):
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Daily sales
    daily_sales = db.query(
        func.date(Order.order_date).label("date"),
        func.sum(Order.total_amount).label("total"),
        func.count(Order.id).label("order_count")
    ).filter(
        Order.created_at >= start_date,
        Order.status == OrderStatus.DELIVERED
    ).group_by(func.date(Order.order_date)).all()
    
    # Top products
    from ..models.order import OrderItem
    top_products = db.query(
        Product.name,
        func.sum(OrderItem.quantity).label("total_quantity"),
        func.sum(OrderItem.subtotal).label("total_revenue")
    ).join(OrderItem, Product.id == OrderItem.product_id)\
     .group_by(Product.id)\
     .order_by(func.sum(OrderItem.subtotal).desc())\
     .limit(10).all()
    
    return {
        "period_days": days,
        "daily_sales": [{"date": str(s.date), "total": float(s.total), "orders": s.order_count} for s in daily_sales],
        "top_products": [{"name": p.name, "quantity": float(p.total_quantity), "revenue": float(p.total_revenue)} for p in top_products]
    }

@router.get("/inventory")
def get_inventory_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR, UserRole.WAREHOUSE_MANAGER, UserRole.WAREHOUSE_SUPERVISOR]))
):
    # Stock value
    total_stock_value = db.query(func.sum(Inventory.stock_quantity * Product.unit_price)).join(Product).scalar() or Decimal('0')
    
    # Categories distribution
    categories = db.query(
        Product.category,
        func.count(Product.id).label("product_count"),
        func.sum(Inventory.stock_quantity).label("total_stock")
    ).join(Inventory, Product.id == Inventory.product_id)\
     .group_by(Product.category).all()
    
    # Out of stock
    out_of_stock = db.query(Inventory).filter(Inventory.stock_quantity <= 0).count()
    
    return {
        "total_stock_value": float(total_stock_value),
        "out_of_stock_items": out_of_stock,
        "categories": [{"category": c.category or "Uncategorized", "products": c.product_count, "stock": float(c.total_stock)} for c in categories]
    }

@router.get("/orders-status")
def get_orders_status_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR, UserRole.SALES_MANAGER, UserRole.ERP_MANAGER]))
):
    status_counts = db.query(
        Order.status,
        func.count(Order.id).label("count"),
        func.avg(Order.total_amount).label("avg_value")
    ).group_by(Order.status).all()
    
    # Average processing time for completed orders
    completed_orders = db.query(Order).filter(Order.status == OrderStatus.DELIVERED).all()
    avg_processing_days = 0
    if completed_orders:
        total_days = sum((order.updated_at - order.created_at).days for order in completed_orders if order.updated_at)
        avg_processing_days = total_days / len(completed_orders) if completed_orders else 0
    
    return {
        "status_breakdown": [{"status": s.status.value, "count": s.count, "avg_order_value": float(s.avg_value) if s.avg_value else 0} for s in status_counts],
        "average_processing_days": round(avg_processing_days, 1)
    }