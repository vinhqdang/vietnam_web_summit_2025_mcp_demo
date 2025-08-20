from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn

from ..database.database import get_db, create_database
from ..database.seed_data import create_sample_data
from . import crud, schemas

app = FastAPI(
    title="E-commerce User Behavior API",
    description="REST API for querying e-commerce user behavior data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database and create sample data"""
    create_database()
    try:
        create_sample_data()
    except Exception:
        pass  # Data might already exist

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {"message": "E-commerce User Behavior API", "docs": "/docs"}

@app.get("/users", response_model=List[schemas.UserResponse], tags=["Users"])
async def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """Get all users with pagination"""
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.UserResponse, tags=["Users"])
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID"""
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/{user_id}/behavior", response_model=schemas.UserBehaviorSummary, tags=["Users"])
async def get_user_behavior_summary(user_id: int, db: Session = Depends(get_db)):
    """Get comprehensive behavior summary for a specific user"""
    summary = crud.get_user_behavior_summary(db, user_id=user_id)
    if summary is None:
        raise HTTPException(status_code=404, detail="User not found")
    return summary

@app.get("/products", response_model=List[schemas.ProductResponse], tags=["Products"])
async def get_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """Get all products with pagination"""
    products = crud.get_products(db, skip=skip, limit=limit)
    return products

@app.get("/products/{product_id}", response_model=schemas.ProductResponse, tags=["Products"])
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID"""
    product = crud.get_product(db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.get("/products/{product_id}/analytics", response_model=schemas.ProductAnalytics, tags=["Products"])
async def get_product_analytics(product_id: int, db: Session = Depends(get_db)):
    """Get analytics data for a specific product"""
    analytics = crud.get_product_analytics(db, product_id=product_id)
    if analytics is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return analytics

@app.get("/sessions", response_model=List[schemas.UserSessionResponse], tags=["Sessions"])
async def get_user_sessions(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """Get user sessions, optionally filtered by user ID"""
    sessions = crud.get_user_sessions(db, user_id=user_id, skip=skip, limit=limit)
    return sessions

@app.get("/purchases", response_model=List[schemas.PurchaseResponse], tags=["Purchases"])
async def get_purchases(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """Get purchases, optionally filtered by user ID"""
    purchases = crud.get_purchases(db, user_id=user_id, skip=skip, limit=limit)
    return purchases

@app.get("/reviews", response_model=List[schemas.ReviewResponse], tags=["Reviews"])
async def get_reviews(
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """Get reviews, optionally filtered by product ID"""
    reviews = crud.get_reviews(db, product_id=product_id, skip=skip, limit=limit)
    return reviews

@app.get("/page-views", response_model=List[schemas.PageViewResponse], tags=["Page Views"])
async def get_page_views(
    session_id: Optional[int] = Query(None, description="Filter by session ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """Get page views, optionally filtered by session ID"""
    page_views = crud.get_page_views(db, session_id=session_id, skip=skip, limit=limit)
    return page_views

@app.get("/analytics/top-products", response_model=List[schemas.ProductAnalytics], tags=["Analytics"])
async def get_top_products_by_revenue(
    limit: int = Query(10, ge=1, le=50, description="Number of top products to return"),
    db: Session = Depends(get_db)
):
    """Get top products by revenue"""
    return crud.get_top_products_by_revenue(db, limit=limit)

@app.get("/analytics/device-usage", tags=["Analytics"])
async def get_user_activity_by_device(db: Session = Depends(get_db)):
    """Get user activity statistics by device type"""
    return crud.get_user_activity_by_device(db)

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "E-commerce User Behavior API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)