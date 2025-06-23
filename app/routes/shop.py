from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.models import Product, CartItem, Order, OrderItem, Review
from app.forms.forms import ReviewForm

bp = Blueprint('shop', __name__)

@bp.route('/add_to_cart/<int:product_id>')
@login_required
def add_to_cart(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        quantity = request.args.get('quantity', 1, type=int)
        
        # Check if product has enough stock
        if product.stock_quantity < quantity:
            flash(f'Sorry, only {product.stock_quantity} items available in stock.', 'warning')
            return redirect(url_for('main.product_detail', id=product_id))
        
        # Check if item already exists in cart
        cart_item = CartItem.query.filter_by(
            user_id=current_user.id,
            product_id=product_id
        ).first()
        
        if cart_item:
            # Update quantity if item already in cart
            new_quantity = cart_item.quantity + quantity
            if new_quantity <= product.stock_quantity:
                cart_item.quantity = new_quantity
                flash(f'Updated {product.name} quantity in cart.', 'success')
            else:
                flash(f'Cannot add more items. Only {product.stock_quantity} available.', 'warning')
                return redirect(url_for('main.product_detail', id=product_id))
        else:
            # Add new item to cart
            cart_item = CartItem(
                user_id=current_user.id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(cart_item)
            flash(f'Added {product.name} to cart.', 'success')
        
        db.session.commit()
        return redirect(url_for('shop.cart'))
        
    except Exception as e:
        print(f"Error adding to cart: {e}")
        flash('Error adding item to cart.', 'error')
        return redirect(url_for('main.product_detail', id=product_id))

@bp.route('/cart')
@login_required
def cart():
    try:
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        total = sum(item.product.price * item.quantity for item in cart_items)
        return render_template('shop/cart.html', cart_items=cart_items, total=total)
    except Exception as e:
        print(f"Error loading cart: {e}")
        flash('Error loading cart.', 'error')
        return render_template('shop/cart.html', cart_items=[], total=0)

@bp.route('/remove_from_cart/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    try:
        cart_item = CartItem.query.filter_by(
            id=item_id,
            user_id=current_user.id
        ).first_or_404()
        
        product_name = cart_item.product.name
        db.session.delete(cart_item)
        db.session.commit()
        
        flash(f'Removed {product_name} from cart.', 'info')
        return redirect(url_for('shop.cart'))
        
    except Exception as e:
        print(f"Error removing from cart: {e}")
        flash('Error removing item from cart.', 'error')
        return redirect(url_for('shop.cart'))

@bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    try:
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        
        if not cart_items:
            flash('Your cart is empty.', 'warning')
            return redirect(url_for('shop.cart'))
        
        # Check stock availability
        for cart_item in cart_items:
            if cart_item.product.stock_quantity < cart_item.quantity:
                flash(f'Insufficient stock for {cart_item.product.name}. Available: {cart_item.product.stock_quantity}', 'error')
                return redirect(url_for('shop.cart'))
        
        # Calculate total
        total = sum(item.product.price * item.quantity for item in cart_items)
        
        # Create order
        order = Order(
            user_id=current_user.id,
            total_amount=total,
            shipping_address=current_user.address or 'Default Address - Please update your profile',
            status='pending'
        )
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Create order items and update stock
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            db.session.add(order_item)
            
            # Update stock
            cart_item.product.stock_quantity -= cart_item.quantity
        
        # Clear cart
        CartItem.query.filter_by(user_id=current_user.id).delete()
        
        db.session.commit()
        flash(f'Order #{order.id} placed successfully! Total: ${total:.2f}', 'success')
        return redirect(url_for('shop.order_history'))
        
    except Exception as e:
        db.session.rollback()
        print(f"Error during checkout: {e}")
        flash('Error processing your order. Please try again.', 'error')
        return redirect(url_for('shop.cart'))

@bp.route('/orders')
def order_history():
    try:
        if current_user.is_authenticated:
            orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
        else:
            orders = []
        return render_template('shop/orders.html', orders=orders)
    except Exception as e:
        print(f"Error loading orders: {e}")
        flash('Error loading order history.', 'error')
        return render_template('shop/orders.html', orders=[])

@bp.route('/review/<int:product_id>', methods=['GET', 'POST'])
@login_required
def add_review(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        
        # Check if user has already reviewed this product
        existing_review = Review.query.filter_by(
            user_id=current_user.id,
            product_id=product_id
        ).first()
        
        if existing_review:
            flash('You have already reviewed this product.', 'info')
            return redirect(url_for('main.product_detail', id=product_id))
        
        form = ReviewForm()
        
        if form.validate_on_submit():
            review = Review(
                user_id=current_user.id,
                product_id=product_id,
                rating=form.rating.data,
                comment=form.comment.data
            )
            db.session.add(review)
            db.session.commit()
            flash('Review added successfully!', 'success')
            return redirect(url_for('main.product_detail', id=product_id))
        
        return render_template('shop/review.html', form=form, product=product)
        
    except Exception as e:
        print(f"Error adding review: {e}")
        flash('Error adding review.', 'error')
        return redirect(url_for('main.product_detail', id=product_id))
