# TrendWear Distribution ERP Platform

TrendWear Distribution ERP Platform is a cloud-ready wholesale garment distribution solution integrating ERP, CRM, and WMS capabilities.

## ERP Module
- Order and fulfillment management
- Sales tracking and status updates
- Inventory coordination with product and order data
- Built for garment distribution workflows and demand forecasting

## CRM Module
- Customer management and relationship tracking
- Contact details, company profiles, and customer reporting
- Role-based access for CRM specialists and sales teams
- Designed to support wholesale garment account management

## WMS Module
- Warehouse inventory tracking and movement
- Product SKUs, stock levels, and low inventory alerts
- Warehouse supervision and stock visibility for distribution centers
- Supports fast fulfillment and stock reconciliation

## Docker Deployment
1. Build and start the stack:
   ```bash
   docker compose up --build
   ```
2. Backend API runs at `http://localhost:8000`
3. Frontend runs at `http://localhost:3000`
4. PostgreSQL database is available on port `5433`
5. PgAdmin is available on port `5051`

## Cloud Deployment Architecture
TrendWear Distribution is designed for a segmented cloud network topology:
- VPC: `172.16.0.0/16`
- Public Subnet: `172.16.10.0/24`
- Application Subnet: `172.16.20.0/24`
- Database Subnet: `172.16.30.0/24`

Key infrastructure components:
- Internet Gateway for public internet access
- NAT Gateway for secure outbound application traffic
- Application Load Balancer for API and frontend routing
- Site-to-Site VPN for private network connectivity
- Auto Scaling Group for scalable application instances

## Company Identity
- Company Name: TrendWear Distribution Ltd
- Domain: trendwear.uz
- Support Email: support@trendwear.uz
- Admin Email: admin@trendwear.uz
