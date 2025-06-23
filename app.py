from app import create_app, db
from app.models.models import User, Product, Category, Order, OrderItem, CartItem, Review
import os

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Product': Product,
        'Category': Category,
        'Order': Order,
        'OrderItem': OrderItem,
        'CartItem': CartItem,
        'Review': Review
    }

if __name__ == '__main__':
    with app.app_context():
        try:
            # Ensure tables exist
            db.create_all()
            print("Database tables created/verified successfully!")
            
            # Check if we have any data
            product_count = Product.query.count()
            category_count = Category.query.count()
            user_count = User.query.count()
            
            print(f"Database status:")
            print(f"  Products: {product_count}")
            print(f"  Categories: {category_count}")
            print(f"  Users: {user_count}")
            
            if product_count == 0:
                print("No products found. Run 'python seed_data.py' first!")
            
        except Exception as e:
            print(f"Database error: {e}")
    
    print("Starting Flask application...")
    print("Access the site at: http://your-server-ip:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
