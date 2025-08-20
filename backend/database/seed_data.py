import random
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.database.database import SessionLocal, create_database
from backend.database.models import User, Product, UserSession, PageView, Purchase, Review

def create_sample_data():
    """Generate sample e-commerce user behavior data"""
    create_database()
    db = SessionLocal()
    
    try:
        # Clear existing data
        db.query(Review).delete()
        db.query(Purchase).delete()
        db.query(PageView).delete()
        db.query(UserSession).delete()
        db.query(Product).delete()
        db.query(User).delete()
        db.commit()
        
        # Create sample users
        users = []
        names = ["Alice Johnson", "Bob Smith", "Carol Davis", "David Wilson", "Eva Brown", 
                "Frank Miller", "Grace Taylor", "Henry Anderson", "Ivy Chen", "Jack Williams"]
        locations = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", 
                    "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
        
        for i in range(100):
            user = User(
                email=f"user{i+1}@example.com",
                name=random.choice(names) + f" {i+1}",
                age=random.randint(18, 70),
                gender=random.choice(["M", "F", "Other"]),
                location=random.choice(locations),
                registration_date=datetime.utcnow() - timedelta(days=random.randint(1, 365)),
                is_premium=random.choice([True, False])
            )
            users.append(user)
            db.add(user)
        
        db.commit()
        
        # Create sample products
        products = []
        categories = ["Electronics", "Clothing", "Books", "Home & Garden", "Sports", 
                     "Beauty", "Toys", "Automotive", "Health", "Food"]
        brands = ["Apple", "Samsung", "Nike", "Adidas", "Sony", "LG", "HP", "Dell", "Amazon", "Google"]
        
        for i in range(50):
            product = Product(
                name=f"Product {i+1}",
                category=random.choice(categories),
                price=round(random.uniform(10.0, 1000.0), 2),
                brand=random.choice(brands),
                rating=round(random.uniform(1.0, 5.0), 1),
                stock_quantity=random.randint(0, 1000),
                description=f"This is a great {random.choice(categories).lower()} product with excellent features."
            )
            products.append(product)
            db.add(product)
        
        db.commit()
        
        # Create user sessions
        sessions = []
        devices = ["mobile", "desktop", "tablet"]
        browsers = ["Chrome", "Firefox", "Safari", "Edge"]
        
        for user in users:
            for _ in range(random.randint(1, 10)):
                session_start = datetime.utcnow() - timedelta(days=random.randint(0, 30), 
                                                            hours=random.randint(0, 23),
                                                            minutes=random.randint(0, 59))
                duration = random.randint(1, 120)
                session = UserSession(
                    user_id=user.id,
                    session_start=session_start,
                    session_end=session_start + timedelta(minutes=duration),
                    session_duration_minutes=duration,
                    pages_viewed=random.randint(1, 20),
                    device_type=random.choice(devices),
                    browser=random.choice(browsers)
                )
                sessions.append(session)
                db.add(session)
        
        db.commit()
        
        # Create page views
        page_types = ["product", "category", "home", "cart", "checkout"]
        
        for session in sessions:
            for _ in range(session.pages_viewed):
                page_view = PageView(
                    session_id=session.id,
                    product_id=random.choice(products).id if random.choice([True, False]) else None,
                    page_type=random.choice(page_types),
                    timestamp=session.session_start + timedelta(minutes=random.randint(0, int(session.session_duration_minutes))),
                    time_spent_seconds=random.randint(10, 300)
                )
                db.add(page_view)
        
        db.commit()
        
        # Create purchases
        payment_methods = ["credit_card", "debit_card", "paypal", "apple_pay", "google_pay"]
        
        for user in users:
            for _ in range(random.randint(0, 5)):
                product = random.choice(products)
                quantity = random.randint(1, 3)
                discount = random.uniform(0, 0.3) if random.choice([True, False]) else 0
                
                purchase = Purchase(
                    user_id=user.id,
                    product_id=product.id,
                    quantity=quantity,
                    total_amount=round(product.price * quantity * (1 - discount), 2),
                    purchase_date=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                    payment_method=random.choice(payment_methods),
                    discount_applied=discount
                )
                db.add(purchase)
        
        db.commit()
        
        # Create reviews
        for user in users:
            purchased_products = db.query(Purchase).filter(Purchase.user_id == user.id).all()
            for purchase in purchased_products:
                if random.choice([True, False]):  # 50% chance of leaving a review
                    review = Review(
                        user_id=user.id,
                        product_id=purchase.product_id,
                        rating=random.randint(1, 5),
                        review_text=f"This product is {'great' if random.choice([True, False]) else 'okay'}. Would {'definitely' if random.choice([True, False]) else 'maybe'} recommend to others.",
                        review_date=purchase.purchase_date + timedelta(days=random.randint(1, 14)),
                        helpful_votes=random.randint(0, 50)
                    )
                    db.add(review)
        
        db.commit()
        print("Sample data created successfully!")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()