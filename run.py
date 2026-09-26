import os
import sys
from app import create_app
from app.models import db, User
from seed_data import seed_database

app = create_app()

def initialize():
    """Ensure database and tables exist, and seed on first run."""
    with app.app_context():
        db.create_all()
        # Seed if empty
        if not User.query.first():
            print("\n[*] First run detected! Seeding initial developer network data...")
            seed_database()
            print("[*] Database initialized successfully!\n")

# Initialize database tables and seeds on server startup
initialize()

if __name__ == '__main__':
    
    port = int(os.environ.get('PORT', 5000))
    host = '127.0.0.1'  # Strictly localhost for complete PC security

    print("=" * 65)
    print(" 🚀 DevHub - Developer Social Network & GitHub Showcase")
    print("=" * 65)
    print(f" [✓] Safe Local-First Architecture Active")
    print(f" [✓] Running on: http://{host}:{port}")
    print(f" [✓] Zero external telemetry or open firewall ports")
    print(f" [✓] Sample accounts: alex_dev, sarah_ai, marcus_rust, elena_ui")
    print(f"     Default password: password123")
    print("=" * 65)
    print(" Press Ctrl+C in this terminal window to stop the server.\n")

    app.run(host=host, port=port, debug=False)
