from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.models import Order, User, Product, Category, OrderItem
from functools import wraps

bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_administrator():
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with overview statistics"""
    try:
        # Get statistics
        total_orders = Order.query.count()
        pending_orders = Order.query.filter_by(status='pending').count()
        shipped_orders = Order.query.filter_by(status='shipped').count()
        total_customers = User.query.filter_by(is_admin=False).count()
        total_products = Product.query.count()
        
        # Get recent orders
        recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
        
        stats = {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'shipped_orders': shipped_orders,
            'total_customers': total_customers,
            'total_products': total_products
        }
        
        return render_template('admin/dashboard.html', stats=stats, recent_orders=recent_orders)
        
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('main.index'))

@bp.route('/orders')
@login_required
@admin_required
def orders():
    """View all orders with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        status_filter = request.args.get('status', '')
        
        query = Order.query
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        orders = query.order_by(Order.created_at.desc()).paginate(
            page=page, 
            per_page=20, 
            error_out=False
        )
        
        return render_template('admin/orders.html', orders=orders, status_filter=status_filter)
        
    except Exception as e:
        flash(f'Error loading orders: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))

@bp.route('/order/<int:order_id>')
@login_required
@admin_required
def order_detail(order_id):
    """View detailed information about a specific order"""
    try:
        order = Order.query.get_or_404(order_id)
        return render_template('admin/order_detail.html', order=order)
        
    except Exception as e:
        flash(f'Error loading order details: {str(e)}', 'error')
        return redirect(url_for('admin.orders'))

@bp.route('/order/<int:order_id>/update_status', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id):
    """Update the status of an order"""
    try:
        order = Order.query.get_or_404(order_id)
        new_status = request.form.get('status')
        
        if new_status not in ['pending', 'shipped', 'delivered', 'cancelled']:
            flash('Invalid status selected.', 'error')
            return redirect(url_for('admin.order_detail', order_id=order_id))
        
        old_status = order.status
        order.update_status(new_status)
        db.session.commit()
        
        flash(f'Order #{order.id} status updated from {old_status.title()} to {new_status.title()}.', 'success')
        
        # Redirect back to where the user came from
        next_page = request.form.get('next') or url_for('admin.order_detail', order_id=order_id)
        return redirect(next_page)
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating order status: {str(e)}', 'error')
        return redirect(url_for('admin.order_detail', order_id=order_id))

@bp.route('/customers')
@login_required
@admin_required
def customers():
    """View all customers"""
    try:
        page = request.args.get('page', 1, type=int)
        
        customers = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).paginate(
            page=page, 
            per_page=20, 
            error_out=False
        )
        
        return render_template('admin/customers.html', customers=customers)
        
    except Exception as e:
        flash(f'Error loading customers: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))

@bp.route('/products')
@login_required
@admin_required
def products():
    """View all products"""
    try:
        page = request.args.get('page', 1, type=int)
        
        products = Product.query.order_by(Product.created_at.desc()).paginate(
            page=page, 
            per_page=20, 
            error_out=False
        )
        
        return render_template('admin/products.html', products=products)
        
    except Exception as e:
        flash(f'Error loading products: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))