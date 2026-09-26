import os
from flask import Flask, render_template, request, session, abort
from flask_login import LoginManager
from config import Config
from app.models import db, User
from app.utils.security import generate_csrf_token, validate_csrf
from app.utils.helpers import time_ago, generate_default_avatar_svg

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure required runtime folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PROJECTS_CODE_FOLDER'], exist_ok=True)
    os.makedirs(app.config['AVATARS_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.projects import projects_bp
    from app.routes.posts import posts_bp
    from app.routes.profile import profile_bp
    from app.routes.api import api_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(projects_bp, url_prefix='/projects')
    app.register_blueprint(posts_bp, url_prefix='/posts')
    app.register_blueprint(profile_bp, url_prefix='/u')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Security headers (Zero risk for user PC)
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        # Local development friendly CSP
        response.headers['Content-Security-Policy'] = (
            "default-src 'self' data: https: 'unsafe-inline' 'unsafe-eval'; "
            "img-src 'self' data: https: blob:; "
            "font-src 'self' https: data:;"
        )
        return response

    # Global context processors for templates
    @app.context_processor
    def inject_globals():
        return {
            'csrf_token': generate_csrf_token,
            'time_ago': time_ago,
            'get_avatar_svg': generate_default_avatar_svg
        }

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden_access(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(413)
    def file_too_large(e):
        return render_template('errors/413.html'), 413

    return app
