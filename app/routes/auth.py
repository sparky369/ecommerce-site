from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.models import User
from app.forms.forms import LoginForm, RegistrationForm, AdminLoginForm

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user)
            flash(f'Welcome back, {user.first_name}!', 'success')
            
            # Redirect to next page or home
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        
        flash('Invalid username or password.', 'error')
    
    return render_template('auth/login.html', form=form)

@bp.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if current_user.is_authenticated and current_user.is_administrator():
        return redirect(url_for('admin.dashboard'))
    
    form = AdminLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.verify_password(form.password.data) and user.is_administrator():
            login_user(user)
            flash(f'Welcome to Admin Panel, {user.first_name}!', 'success')
            return redirect(url_for('admin.dashboard'))
        
        flash('Invalid admin credentials or insufficient privileges.', 'error')
    
    return render_template('auth/admin_login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        existing_user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.email.data)
        ).first()
        
        if existing_user:
            if existing_user.username == form.username.data:
                flash('Username already exists. Please choose a different one.', 'error')
            else:
                flash('Email already exists. Please choose a different one.', 'error')
            return render_template('auth/register.html', form=form)
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('auth/register.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    user_name = current_user.first_name
    logout_user()
    flash(f'Goodbye, {user_name}! You have been logged out.', 'info')
    return redirect(url_for('main.index'))