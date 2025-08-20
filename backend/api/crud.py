from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from ..database.models import User, Product, UserSession, PageView, Purchase, Review
from . import schemas

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
    return db.query(Product).offset(skip).limit(limit).all()

def get_product(db: Session, product_id: int) -> Optional[Product]:
    return db.query(Product).filter(Product.id == product_id).first()

def get_user_sessions(db: Session, user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[UserSession]:
    query = db.query(UserSession)
    if user_id:
        query = query.filter(UserSession.user_id == user_id)
    return query.offset(skip).limit(limit).all()

def get_purchases(db: Session, user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Purchase]:
    query = db.query(Purchase)
    if user_id:
        query = query.filter(Purchase.user_id == user_id)
    return query.offset(skip).limit(limit).all()

def get_reviews(db: Session, product_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Review]:
    query = db.query(Review)
    if product_id:
        query = query.filter(Review.product_id == product_id)
    return query.offset(skip).limit(limit).all()

def get_page_views(db: Session, session_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[PageView]:
    query = db.query(PageView)
    if session_id:
        query = query.filter(PageView.session_id == session_id)
    return query.offset(skip).limit(limit).all()

def get_user_behavior_summary(db: Session, user_id: int) -> Optional[schemas.UserBehaviorSummary]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    # Get user session stats
    session_stats = db.query(
        func.count(UserSession.id).label('total_sessions'),
        func.avg(UserSession.session_duration_minutes).label('avg_duration')
    ).filter(UserSession.user_id == user_id).first()
    
    # Get purchase stats
    purchase_stats = db.query(
        func.count(Purchase.id).label('total_purchases'),
        func.sum(Purchase.total_amount).label('total_spent')
    ).filter(Purchase.user_id == user_id).first()
    
    # Get favorite category
    favorite_category = db.query(
        Product.category,
        func.count(Purchase.id).label('purchase_count')
    ).join(Purchase, Product.id == Purchase.product_id)\
     .filter(Purchase.user_id == user_id)\
     .group_by(Product.category)\
     .order_by(desc('purchase_count')).first()
    
    # Get last activity
    last_session = db.query(UserSession).filter(UserSession.user_id == user_id)\
                     .order_by(desc(UserSession.session_start)).first()
    
    return schemas.UserBehaviorSummary(
        user_id=user.id,
        user_name=user.name,
        total_sessions=session_stats.total_sessions or 0,
        total_purchases=purchase_stats.total_purchases or 0,
        total_spent=float(purchase_stats.total_spent or 0),
        avg_session_duration=float(session_stats.avg_duration or 0),
        favorite_category=favorite_category.category if favorite_category else "None",
        last_activity=last_session.session_start if last_session else user.registration_date
    )

def get_product_analytics(db: Session, product_id: int) -> Optional[schemas.ProductAnalytics]:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None
    
    # Get view stats
    total_views = db.query(func.count(PageView.id))\
                   .filter(PageView.product_id == product_id).scalar() or 0
    
    # Get purchase stats
    purchase_stats = db.query(
        func.count(Purchase.id).label('total_purchases'),
        func.sum(Purchase.total_amount).label('total_revenue')
    ).filter(Purchase.product_id == product_id).first()
    
    # Get average rating
    avg_rating = db.query(func.avg(Review.rating))\
                  .filter(Review.product_id == product_id).scalar() or 0
    
    total_purchases = purchase_stats.total_purchases or 0
    conversion_rate = (total_purchases / total_views * 100) if total_views > 0 else 0
    
    return schemas.ProductAnalytics(
        product_id=product.id,
        product_name=product.name,
        total_views=total_views,
        total_purchases=total_purchases,
        total_revenue=float(purchase_stats.total_revenue or 0),
        avg_rating=float(avg_rating),
        conversion_rate=round(conversion_rate, 2)
    )

def get_top_products_by_revenue(db: Session, limit: int = 10) -> List[schemas.ProductAnalytics]:
    products = db.query(Product).all()
    analytics = []
    
    for product in products:
        product_analytics = get_product_analytics(db, product.id)
        if product_analytics:
            analytics.append(product_analytics)
    
    return sorted(analytics, key=lambda x: x.total_revenue, reverse=True)[:limit]

def get_user_activity_by_device(db: Session) -> dict:
    device_stats = db.query(
        UserSession.device_type,
        func.count(UserSession.id).label('session_count'),
        func.avg(UserSession.session_duration_minutes).label('avg_duration')
    ).group_by(UserSession.device_type).all()
    
    return {
        stat.device_type: {
            'session_count': stat.session_count,
            'avg_duration': float(stat.avg_duration or 0)
        }
        for stat in device_stats
    }