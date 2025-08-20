from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    email: str
    name: str
    age: int
    gender: str
    location: str
    is_premium: bool

class UserResponse(UserBase):
    id: int
    registration_date: datetime
    
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str
    category: str
    price: float
    brand: str
    rating: float
    stock_quantity: int
    description: str

class ProductResponse(ProductBase):
    id: int
    
    class Config:
        from_attributes = True

class UserSessionResponse(BaseModel):
    id: int
    user_id: int
    session_start: datetime
    session_end: Optional[datetime]
    session_duration_minutes: Optional[float]
    pages_viewed: int
    device_type: str
    browser: str
    
    class Config:
        from_attributes = True

class PurchaseResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    total_amount: float
    purchase_date: datetime
    payment_method: str
    discount_applied: float
    
    class Config:
        from_attributes = True

class ReviewResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    rating: int
    review_text: str
    review_date: datetime
    helpful_votes: int
    
    class Config:
        from_attributes = True

class PageViewResponse(BaseModel):
    id: int
    session_id: int
    product_id: Optional[int]
    page_type: str
    timestamp: datetime
    time_spent_seconds: float
    
    class Config:
        from_attributes = True

class UserBehaviorSummary(BaseModel):
    user_id: int
    user_name: str
    total_sessions: int
    total_purchases: int
    total_spent: float
    avg_session_duration: float
    favorite_category: str
    last_activity: datetime

class ProductAnalytics(BaseModel):
    product_id: int
    product_name: str
    total_views: int
    total_purchases: int
    total_revenue: float
    avg_rating: float
    conversion_rate: float