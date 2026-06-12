from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

from ..core.database import get_db
from ..core.dependencies import require_role
from ..models.user import User, UserRole
from ..models.supplier import Supplier
from ..models.shipment import Shipment, ShipmentItem, ShipmentStatus
from ..models.inventory import Inventory
from ..models.inventory_alert import InventoryAlert, AlertType, AlertSeverity

router = APIRouter(prefix="/api/wms/shipments", tags=["Shipments"])


# ─── Supplier endpoints ────────────────────────────────────────────────────────

supplier_router = APIRouter(prefix="/api/wms/suppliers", tags=["Suppliers"])


@supplier_router.get("/")
def list_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([
        UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR,
        UserRole.WAREHOUSE_SUPERVISOR, UserRole.WAREHOUSE_MANAGER
    ]))
):
    q = db.query(Supplier)
    if active_only:
        q = q.filter(Supplier.is_active == True)
    return q.offset(skip).limit(limit).all()


@supplier_router.post("/")
def create_supplier(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([
        UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR, UserRole.WAREHOUSE_SUPERVISOR
    ]))
):
    supplier = Supplier(**data)
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@supplier_router.get("/{supplier_id}")
def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([
        UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR,
        UserRole.WAREHOUSE_SUPERVISOR, UserRole.WAREHOUSE_MANAGER
    ]))
):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


# ─── Shipment endpoints ────────────────────────────────────────────────────────

@router.get("/")
def list_shipments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[ShipmentStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([
        UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR,
        UserRole.WAREHOUSE_SUPERVISOR, UserRole.WAREHOUSE_MANAGER
    ]))
):
    q = db.query(Shipment)
    if status:
        q = q.filter(Shipment.status == status)
    return q.offset(skip).limit(limit).all()


@router.post("/")
def create_shipment(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([
        UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR, UserRole.WAREHOUSE_SUPERVISOR
    ]))
):
    items = data.pop("items", [])
    shipment = Shipment(**data)
    db.add(shipment)
    db.flush()

    for item in items:
        si = ShipmentItem(shipment_id=shipment.id, **item)
        db.add(si)

    db.commit()
    db.refresh(shipment)
    return shipment


@router.put("/{shipment_id}/receive")
def receive_shipment(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([
        UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR, UserRole.WAREHOUSE_SUPERVISOR
    ]))
):
    """
    Mark a shipment as received and update inventory stock levels accordingly.
    Also checks for and resolves any related low-stock inventory alerts.
    """
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    if shipment.status == ShipmentStatus.RECEIVED:
        raise HTTPException(status_code=400, detail="Shipment already received")

    LOW_STOCK_THRESHOLD = Decimal("10")

    for item in shipment.items:
        inventory = db.query(Inventory).filter(Inventory.product_id == item.product_id).first()
        if inventory:
            inventory.stock_quantity += item.quantity_expected
            item.quantity_received = item.quantity_expected

            # Auto-resolve low-stock alerts for this product
            db.query(InventoryAlert).filter(
                InventoryAlert.product_id == item.product_id,
                InventoryAlert.is_resolved == False
            ).update({"is_resolved": True, "resolved_at": datetime.utcnow()})

            # Raise new alert if still below threshold after receiving
            if inventory.stock_quantity <= LOW_STOCK_THRESHOLD:
                alert = InventoryAlert(
                    product_id=item.product_id,
                    alert_type=AlertType.LOW_STOCK,
                    severity=AlertSeverity.WARNING,
                    threshold_quantity=LOW_STOCK_THRESHOLD,
                    current_quantity=inventory.stock_quantity
                )
                db.add(alert)

    shipment.status = ShipmentStatus.RECEIVED
    shipment.actual_arrival = datetime.utcnow()
    db.commit()
    return {"message": f"Shipment {shipment.reference_number} received. Inventory updated."}


# ─── Inventory Alert endpoints ─────────────────────────────────────────────────

alert_router = APIRouter(prefix="/api/wms/alerts", tags=["Inventory Alerts"])


@alert_router.get("/")
def list_alerts(
    resolved: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([
        UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR,
        UserRole.WAREHOUSE_SUPERVISOR, UserRole.WAREHOUSE_MANAGER
    ]))
):
    return db.query(InventoryAlert).filter(
        InventoryAlert.is_resolved == resolved
    ).order_by(InventoryAlert.created_at.desc()).all()


@alert_router.put("/{alert_id}/resolve")
def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([
        UserRole.ADMIN, UserRole.SYSTEM_ADMINISTRATOR, UserRole.WAREHOUSE_SUPERVISOR
    ]))
):
    alert = db.query(InventoryAlert).filter(InventoryAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    db.commit()
    return {"message": "Alert resolved"}
