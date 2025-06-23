from flask import Blueprint, render_template, request
from app.models.models import Product, Category

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    try:
        # Get featured products (limit to 8)
        products = Product.query.filter(Product.stock_quantity > 0).limit(8).all()
        
        # Get all categories
        categories = Category.query.all()
        
        return render_template('index.html', products=products, categories=categories)
    except Exception as e:
        print(f"Error in index route: {e}")
        # Return with empty data if there's an error
        return render_template('index.html', products=[], categories=[])

@bp.route('/products')
def products():
    try:
        page = request.args.get('page', 1, type=int)
        category_id = request.args.get('category', type=int)
        
        query = Product.query
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        products = query.paginate(
            page=page, 
            per_page=12, 
            error_out=False
        )
        categories = Category.query.all()
        
        return render_template('products.html', products=products, categories=categories)
    except Exception as e:
        print(f"Error in products route: {e}")
        from flask import abort
        abort(500)

@bp.route('/product/<int:id>')
def product_detail(id):
    try:
        product = Product.query.get_or_404(id)
        reviews = product.reviews
        return render_template('product_detail.html', product=product, reviews=reviews)
    except Exception as e:
        print(f"Error in product_detail route: {e}")
        from flask import abort
        abort(404)
