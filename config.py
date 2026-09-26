import os
import secrets

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def get_or_create_secret_key():
    """Ensure a persistent, unique secret key per installation for session security."""
    key_file = os.path.join(BASE_DIR, '.secret_key')
    if os.path.exists(key_file):
        with open(key_file, 'r', encoding='utf-8') as f:
            key = f.read().strip()
            if key:
                return key
    new_key = secrets.token_hex(32)
    try:
        with open(key_file, 'w', encoding='utf-8') as f:
            f.write(new_key)
    except Exception:
        pass
    return new_key

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or get_or_create_secret_key()
    _raw_db = os.environ.get('DATABASE_URL')
    if _raw_db and _raw_db.startswith("postgres://"):
        _raw_db = _raw_db.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _raw_db or f"sqlite:///{os.path.join(BASE_DIR, 'devhub.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload limits & directories
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    PROJECTS_CODE_FOLDER = os.path.join(UPLOAD_FOLDER, 'projects')
    AVATARS_FOLDER = os.path.join(UPLOAD_FOLDER, 'avatars')
    
    # Session cookie security (Safe for local PC execution)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 86400 * 30  # 30 days
    
    # Allowed file extensions for code repositories
    ALLOWED_EXTENSIONS = {
        'txt', 'md', 'py', 'js', 'jsx', 'ts', 'tsx', 'html', 'css', 'json', 
        'sql', 'c', 'cpp', 'h', 'hpp', 'java', 'rs', 'go', 'rb', 'php', 
        'sh', 'bat', 'yaml', 'yml', 'toml', 'xml', 'dockerfile', 'gitignore',
        'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'zip'
    }
    
    # Allowed extensions for profile avatars
    ALLOWED_AVATAR_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
