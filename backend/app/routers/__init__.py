from .auth import router as auth_router
from .users import router as users_router
from .crm import router as crm_router
from .erp import router as erp_router
from .wms import router as wms_router
from .reports import router as reports_router

__all__ = [
    "auth_router",
    "users_router",
    "crm_router",
    "erp_router",
    "wms_router",
    "reports_router",
]