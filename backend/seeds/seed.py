# backend/seeds/seed.py
import sys
from pathlib import Path

# Add parent directory to path so that "app" module can be found
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.customer import Customer
from app.models.product import Product
from app.models.order import Order, OrderItem, OrderStatus
from app.models.inventory import Inventory
from app.core.security import get_password_hash
from decimal import Decimal
from datetime import datetime, timedelta
import random

def seed_database():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if already seeded (if any user exists)
        if db.query(User).count() > 0:
            print("Database already has data. Skipping seed.")
            return
        
        print("🌱 Seeding database...")
        
        # 1. Create users
        admin = User(
            full_name="TrendWear Admin",
            email="admin@trendwear.uz",
            password_hash=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        system_admin = User(
            full_name="System Administrator",
            email="sysadmin@trendwear.uz",
            password_hash=get_password_hash("sysadmin123"),
            role=UserRole.SYSTEM_ADMINISTRATOR,
            is_active=True
        )
        erp_manager = User(
            full_name="ERP Manager",
            email="erpmanager@trendwear.uz",
            password_hash=get_password_hash("erp123"),
            role=UserRole.ERP_MANAGER,
            is_active=True
        )
        crm_specialist = User(
            full_name="CRM Specialist",
            email="crm@trendwear.uz",
            password_hash=get_password_hash("crm123"),
            role=UserRole.CRM_SPECIALIST,
            is_active=True
        )
        warehouse_supervisor = User(
            full_name="Warehouse Supervisor",
            email="warehouse@trendwear.uz",
            password_hash=get_password_hash("warehouse123"),
            role=UserRole.WAREHOUSE_SUPERVISOR,
            is_active=True
        )
        db.add_all([admin, system_admin, erp_manager, crm_specialist, warehouse_supervisor])
        db.commit()
        print(f"✅ Created {db.query(User).count()} users")
        
        # 2. Create customers
        customers_data = [
            {"company_name": "Fashion World LLC", "contact_person": "Amina Davronova", "phone": "+998901234567", "email": "amina@fashionworld.uz", "address": "Tashkent, City Center 12", "tax_id": "TW-1001"},
            {"company_name": "Urban Style Ltd", "contact_person": "Bekzod Ismoilov", "phone": "+998902345678", "email": "bekzod@urbanstyle.uz", "address": "Tashkent, Business Avenue 8", "tax_id": "TW-1002"},
            {"company_name": "Premium Garments Co", "contact_person": "Dilnoza Karimova", "phone": "+998903456789", "email": "dilnoza@premiumgarments.uz", "address": "Tashkent, Fashion Street 5", "tax_id": "TW-1003"},
            {"company_name": "Elite Wear Group", "contact_person": "Javlon Rustamov", "phone": "+998904567890", "email": "javlon@elitewear.uz", "address": "Tashkent, Market Road 21", "tax_id": "TW-1004"},
            {"company_name": "Modern Apparel Traders", "contact_person": "Nilufar Ochilova", "phone": "+998905678901", "email": "nilufar@modernapparel.uz", "address": "Tashkent, Trade Park 3", "tax_id": "TW-1005"}
        ]
        customers = []
        for c in customers_data:
            cust = Customer(**c)
            db.add(cust)
            customers.append(cust)
        db.commit()
        print(f"✅ Created {len(customers)} customers")
        
        # 3. Create products
        products_data = [
            {"name": "Premium Cotton T-Shirt", "sku": "TWT-1001", "description": "Soft cotton crew neck tee", "unit_price": Decimal("25.00"), "category": "Apparel"},
            {"name": "Denim Jacket", "sku": "TWT-1002", "description": "Classic denim trucker jacket", "unit_price": Decimal("89.00"), "category": "Outerwear"},
            {"name": "Formal Shirt", "sku": "TWT-1003", "description": "Slim-fit dress shirt", "unit_price": Decimal("45.00"), "category": "Menswear"},
            {"name": "Casual Hoodie", "sku": "TWT-1004", "description": "Fleece-lined pullover hoodie", "unit_price": Decimal("55.00"), "category": "Casual"},
            {"name": "Sports Tracksuit", "sku": "TWT-1005", "description": "Performance tracksuit set", "unit_price": Decimal("95.00"), "category": "Sportswear"},
            {"name": "Women's Blazer", "sku": "TWT-1006", "description": "Tailored women's blazer", "unit_price": Decimal("99.00"), "category": "Womenswear"},
            {"name": "Cargo Pants", "sku": "TWT-1007", "description": "Utility cargo pants", "unit_price": Decimal("48.00"), "category": "Menswear"},
            {"name": "Polo Shirt", "sku": "TWT-1008", "description": "Breathable pique polo", "unit_price": Decimal("35.00"), "category": "Casual"},
            {"name": "Winter Coat", "sku": "TWT-1009", "description": "Insulated winter coat", "unit_price": Decimal("120.00"), "category": "Outerwear"},
            {"name": "Training Shorts", "sku": "TWT-1010", "description": "Quick-dry training shorts", "unit_price": Decimal("28.00"), "category": "Sportswear"}
        ]
        products = []
        for p in products_data:
            prod = Product(**p)
            db.add(prod)
            products.append(prod)
        db.commit()
        print(f"✅ Created {len(products)} products")
        
        # 4. Create inventory for products
        for prod in products:
            inv = Inventory(
                product_id=prod.id,
                stock_quantity=Decimal(str(random.randint(10, 200))),
                reserved_quantity=Decimal("0")
            )
            db.add(inv)
        db.commit()
        print(f"✅ Created inventory for {len(products)} products")
        
        # 5. Create orders
        order_statuses = [OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.PROCESSING, OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.CANCELLED]
        orders_created = 0
        for i in range(20):
            customer = random.choice(customers)
            status = random.choice(order_statuses)
            order = Order(
                customer_id=customer.id,
                order_date=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                status=status,
                notes=f"Buyurtma {i+1} uchun eslatma",
                total_amount=Decimal("0")
            )
            db.add(order)
            db.flush()
            
            total = Decimal("0")
            num_items = random.randint(1, 3)
            used_products = random.sample(products, min(num_items, len(products)))
            for prod in used_products:
                quantity = Decimal(str(random.randint(1, 10)))
                inventory = db.query(Inventory).filter(Inventory.product_id == prod.id).first()
                if inventory and inventory.stock_quantity >= quantity:
                    # Decrease stock
                    inventory.stock_quantity -= quantity
                    if status in [OrderStatus.CONFIRMED, OrderStatus.PROCESSING, OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
                        inventory.reserved_quantity += quantity
                    
                    subtotal = prod.unit_price * quantity
                    total += subtotal
                    
                    item = OrderItem(
                        order_id=order.id,
                        product_id=prod.id,
                        quantity=quantity,
                        unit_price=prod.unit_price,
                        subtotal=subtotal
                    )
                    db.add(item)
                else:
                    continue
            if total > 0:
                order.total_amount = total
                orders_created += 1
            else:
                db.delete(order)
        db.commit()
        print(f"✅ Created {orders_created} orders with items")
        
        print("\n🎉 Seed completed successfully!")
        print(f"   Users: {db.query(User).count()}")
        print(f"   Customers: {db.query(Customer).count()}")
        print(f"   Products: {db.query(Product).count()}")
        print(f"   Orders: {db.query(Order).count()}")
        print(f"   Order Items: {db.query(OrderItem).count()}")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()