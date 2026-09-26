import re
from urllib.parse import urlparse
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User, Activity
from app.utils.helpers import login_limiter

auth_bp = Blueprint('auth', __name__)

def is_safe_redirect_url(target):
    """Prevents Open Redirect attacks by validating destination is strictly local."""
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(target)
    return test_url.scheme in ('', 'http', 'https') and ref_url.netloc == (test_url.netloc or ref_url.netloc)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        display_name = request.form.get('display_name', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        title = request.form.get('title', '').strip() or "Software Developer"
        skills = request.form.get('skills', '').strip()

        # Validation
        errors = []
        if not username or len(username) < 3 or len(username) > 30:
            errors.append("Username must be between 3 and 30 characters.")
        if not re.match(r'^[a-zA-Z0-9_\-]+$', username):
            errors.append("Username can only contain alphanumeric characters, underscores, and dashes.")
        
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not email or not re.match(email_regex, email):
            errors.append("Please provide a valid email address.")
        
        if not display_name:
            display_name = username
            
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters long.")
            
        if password != confirm_password:
            errors.append("Passwords do not match.")

        if User.query.filter_by(username=username).first():
            errors.append("That username is already taken. Please pick another.")

        if User.query.filter_by(email=email).first():
            errors.append("An account with that email already exists.")

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html', 
                                   username=username, 
                                   email=email, 
                                   display_name=display_name,
                                   title=title,
                                   skills=skills)

        # Create user
        new_user = User(
            username=username,
            email=email,
            display_name=display_name,
            title=title,
            skills=skills
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Log initial registration activity
        activity = Activity(
            user_id=new_user.id,
            activity_type='joined',
            description=f"Joined DevHub! Welcome aboard.",
            link=url_for('profile.view_profile', username=new_user.username)
        )
        db.session.add(activity)
        db.session.commit()

        login_user(new_user)
        flash(f"Welcome to DevHub, {new_user.display_name}! Your account has been created.", 'success')
        return redirect(url_for('main.index'))

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        login_identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        # Brute-force rate limiting check by client IP
        client_ip = request.remote_addr or '127.0.0.1'
        rate_key = f"{client_ip}:{login_identifier}"

        if login_limiter.is_rate_limited(rate_key):
            flash("Too many failed login attempts. Please wait 5 minutes before trying again.", 'danger')
            return render_template('auth/login.html', identifier=login_identifier)

        user = User.query.filter(
            (User.username == login_identifier) | (User.email == login_identifier.lower())
        ).first()

        if user and user.check_password(password):
            login_limiter.reset(rate_key)
            login_user(user, remember=remember)
            flash(f"Welcome back, {user.display_name}!", 'success')

            next_page = request.args.get('next')
            if next_page and is_safe_redirect_url(next_page):
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            login_limiter.record_attempt(rate_key)
            flash("Invalid username/email or password.", 'danger')
            return render_template('auth/login.html', identifier=login_identifier)

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been securely logged out.", 'info')
    return redirect(url_for('main.index'))
