from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    location = Column(String)
    registration_date = Column(DateTime, default=datetime.utcnow)
    is_premium = Column(Boolean, default=False)
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user")
    purchases = relationship("Purchase", back_populates="user")
    reviews = relationship("Review", back_populates="user")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    category = Column(String)
    price = Column(Float)
    brand = Column(String)
    rating = Column(Float)
    stock_quantity = Column(Integer)
    description = Column(Text)
    
    # Relationships
    purchases = relationship("Purchase", back_populates="product")
    page_views = relationship("PageView", back_populates="product")
    reviews = relationship("Review", back_populates="product")

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_start = Column(DateTime, default=datetime.utcnow)
    session_end = Column(DateTime)
    session_duration_minutes = Column(Float)
    pages_viewed = Column(Integer)
    device_type = Column(String)  # mobile, desktop, tablet
    browser = Column(String)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    page_views = relationship("PageView", back_populates="session")

class PageView(Base):
    __tablename__ = "page_views"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("user_sessions.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    page_type = Column(String)  # product, category, home, cart, checkout
    timestamp = Column(DateTime, default=datetime.utcnow)
    time_spent_seconds = Column(Float)
    
    # Relationships
    session = relationship("UserSession", back_populates="page_views")
    product = relationship("Product", back_populates="page_views")

class Purchase(Base):
    __tablename__ = "purchases"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    total_amount = Column(Float)
    purchase_date = Column(DateTime, default=datetime.utcnow)
    payment_method = Column(String)
    discount_applied = Column(Float, default=0.0)
    
    # Relationships
    user = relationship("User", back_populates="purchases")
    product = relationship("Product", back_populates="purchases")

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    rating = Column(Integer)  # 1-5 stars
    review_text = Column(Text)
    review_date = Column(DateTime, default=datetime.utcnow)
    helpful_votes = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")