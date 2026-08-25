from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.auth import router as auth_router
from backend.routers.user import router as user_router
from backend.routers.parking import router as parking_router, slots_router, sessions_router
from backend.routers.booking import router as booking_router
from backend.routers.admin import router as admin_router

# Initialize FastAPI application
app = FastAPI(
    title="Smart Parking Finder & Management System API",
    description="Backend REST API for Smart Parking Finder (Member 1 - User & Location Module, Member 2 - Parking & Slot Management, Member 3 - Admin & Dashboard)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure Cross-Origin Resource Sharing (CORS) for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register modular routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(parking_router)
app.include_router(slots_router)
app.include_router(sessions_router)
app.include_router(booking_router)
app.include_router(admin_router)



@app.get("/health", tags=["Health"])
def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "service": "Smart Parking Finder & Management API",
        "database": "MySQL (smart_parking_db)",
        "module": "Member 1 - User & Location"
    }


@app.get("/", tags=["Health"])
def root():
    """Root landing endpoint with Swagger link."""
    return {
        "message": "Welcome to Smart Parking Finder API",
        "documentation": "/docs",
        "health": "/health"
    }
