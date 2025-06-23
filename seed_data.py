from app import create_app, db
from app.models.models import User, Product, Category

def create_sample_data():
    app = create_app()
    
    with app.app_context():
        try:
            # Drop and create all tables
            print("Creating database tables...")
            db.drop_all()
            db.create_all()
            
            # Create categories
            print("Creating categories...")
            electronics = Category(name='Electronics', description='Electronic devices and gadgets')
            clothing = Category(name='Clothing', description='Fashion and apparel')
            books = Category(name='Books', description='Books and literature')
            home = Category(name='Home & Garden', description='Home improvement and garden supplies')
            
            db.session.add_all([electronics, clothing, books, home])
            db.session.commit()
            print("Categories created successfully!")
            
            # Create sample products
            print("Creating products...")
            products = [
                Product(
                    name='Laptop Computer', 
                    description='High-performance laptop with 16GB RAM and 512GB SSD. Perfect for work and gaming.', 
                    price=999.99, 
                    stock_quantity=10, 
                    category_id=electronics.id,
                    image_url='https://cdn.pixabay.com/photo/2021/06/03/11/06/apple-macbook-pro-6306821_1280.png'
                ),
                Product(
                    name='Smartphone', 
                    description='Latest model smartphone with advanced camera and long battery life.', 
                    price=699.99, 
                    stock_quantity=15, 
                    category_id=electronics.id,
                    image_url='https://cdn.pixabay.com/photo/2024/10/04/05/13/ai-generated-9095396_1280.jpg'
                ),
                Product(
                    name='Wireless Headphones', 
                    description='Noise-cancelling wireless headphones with premium sound quality.', 
                    price=199.99, 
                    stock_quantity=25, 
                    category_id=electronics.id,
                    image_url='https://cdn.pixabay.com/photo/2016/01/09/07/44/headphone-1129896_1280.png'
                ),
                Product(
                    name='Cotton T-Shirt', 
                    description='Comfortable 100% cotton t-shirt available in multiple colors.', 
                    price=19.99, 
                    stock_quantity=50, 
                    category_id=clothing.id,
                    image_url='https://cdn.pixabay.com/photo/2016/03/16/21/43/t-shirt-1261820_1280.png'
                ),
                Product(
                    name='Blue Jeans', 
                    description='Classic blue jeans made from premium denim. Available in various sizes.', 
                    price=59.99, 
                    stock_quantity=30, 
                    category_id=clothing.id,
                    image_url='https://cdn.pixabay.com/photo/2014/04/02/10/40/jeans-304196_1280.png'
                ),
                Product(
                    name='Winter Jacket', 
                    description='Warm winter jacket with waterproof exterior and thermal lining.', 
                    price=129.99, 
                    stock_quantity=20, 
                    category_id=clothing.id,
                    image_url='https://cdn.pixabay.com/photo/2012/04/13/14/55/jacket-32714_1280.png'
                ),
                Product(
                    name='Python Programming Book', 
                    description='Complete guide to Python programming for beginners and advanced users.', 
                    price=39.99, 
                    stock_quantity=20, 
                    category_id=books.id,
                    image_url='https://cdn.pixabay.com/photo/2017/01/31/00/08/book-2022460_1280.png'
                ),
                Product(
                    name='Web Development Guide', 
                    description='Comprehensive guide to modern web development technologies and frameworks.', 
                    price=49.99, 
                    stock_quantity=15, 
                    category_id=books.id,
                    image_url='https://cdn.pixabay.com/photo/2019/05/14/17/07/web-development-4202909_1280.png'
                ),
                Product(
                    name='Coffee Maker', 
                    description='Automatic coffee maker with programmable timer and thermal carafe.', 
                    price=89.99, 
                    stock_quantity=12, 
                    category_id=home.id,
                    image_url='https://cdn.pixabay.com/photo/2020/11/23/13/16/coffee-5769721_1280.png'
                ),
                Product(
                    name='Garden Tools Set', 
                    description='Complete set of essential garden tools including spade, rake, and pruners.', 
                    price=79.99, 
                    stock_quantity=18, 
                    category_id=home.id,
                    image_url='https://cdn.pixabay.com/photo/2023/11/12/16/26/garden-tools-8383397_1280.jpg'
                ),
            ]
            
            db.session.add_all(products)
            db.session.commit()
            print(f"Created {len(products)} products successfully!")
            
            # Create admin user
            print("Creating admin user...")
            admin = User(
                username='admin',
                email='admin@example.com',
                first_name='Admin',
                last_name='User',
                address='123 Admin Street, Admin City, AC 12345',
                phone='555-0123',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Create sample customer
            print("Creating sample customer...")
            customer = User(
                username='customer',
                email='customer@example.com',
                first_name='John',
                last_name='Doe',
                address='456 Customer Lane, Customer City, CC 67890',
                phone='555-0456',
                is_admin=False
            )
            customer.set_password('customer123')
            db.session.add(customer)
            
            db.session.commit()
            print("Users created successfully!")
            
            print("\n" + "="*50)
            print("SAMPLE DATA CREATED SUCCESSFULLY!")
            print("="*50)
            print("Admin Login:")
            print("  Username: admin")
            print("  Password: admin123")
            print("\nCustomer Login:")
            print("  Username: customer")
            print("  Password: customer123")
            print("="*50)
            
        except Exception as e:
            print(f"Error creating sample data: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    create_sample_data()
