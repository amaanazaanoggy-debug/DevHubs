import unittest
import io
import zipfile
from app import create_app
from app.models import db, User, Project, ProjectFile, ProjectIssue, Post
from app.utils.security import render_safe_markdown, is_safe_path
from app.utils.helpers import SimpleRateLimiter
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class DevHubTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_user_password_hashing(self):
        """Verify passwords are cryptographic hashes and not plaintext."""
        user = User(username='testdev', email='test@dev.com', display_name='Test Dev')
        user.set_password('supersecret123')
        self.assertNotEqual(user.password_hash, 'supersecret123')
        self.assertTrue(user.check_password('supersecret123'))
        self.assertFalse(user.check_password('wrongpass'))

    def test_markdown_xss_sanitization(self):
        """Ensure harmful script tags and inline events are scrubbed."""
        dangerous_input = "<script>alert('xss')</script> Hello **World** <img src=x onerror=alert(1)>"
        safe_output = render_safe_markdown(dangerous_input)
        self.assertNotIn("<script>", safe_output)
        self.assertNotIn("onerror", safe_output)
        self.assertIn("Hello", safe_output)
        self.assertIn("<strong>World</strong>", safe_output)

    def test_path_traversal_prevention(self):
        """Ensure path traversal checks work strictly."""
        base_dir = r"C:\fake\uploads"
        safe = r"C:\fake\uploads\project_1\main.py"
        traversal = r"C:\fake\uploads\..\..\Windows\System32\cmd.exe"
        self.assertTrue(is_safe_path(base_dir, safe))
        self.assertFalse(is_safe_path(base_dir, traversal))

    def test_rate_limiter(self):
        """Verify rate limiting blocks brute-force after threshold."""
        limiter = SimpleRateLimiter(max_attempts=3, window_seconds=60)
        key = "127.0.0.1:testuser"
        self.assertFalse(limiter.is_rate_limited(key))
        limiter.record_attempt(key)
        limiter.record_attempt(key)
        self.assertFalse(limiter.is_rate_limited(key))
        limiter.record_attempt(key)
        self.assertTrue(limiter.is_rate_limited(key))
        limiter.reset(key)
        self.assertFalse(limiter.is_rate_limited(key))

    def test_project_and_in_memory_zip(self):
        """Verify project creation and in-memory zip download."""
        user = User(username='alex', email='alex@test.com', display_name='Alex')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        project = Project(
            user_id=user.id,
            name='demo-repo',
            readme_content='# Demo Project\nThis is a test.'
        )
        db.session.add(project)
        db.session.commit()

        file1 = ProjectFile(
            project_id=project.id,
            filename='main.py',
            content='print("Hello DevHub")',
            file_size=23
        )
        db.session.add(file1)
        db.session.commit()

        res = self.client.get(f'/projects/{project.id}/download')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.mimetype, 'application/zip')

        # Read zip in memory
        zip_buf = io.BytesIO(res.data)
        with zipfile.ZipFile(zip_buf, 'r') as zf:
            file_names = zf.namelist()
            self.assertIn('demo-repo/main.py', file_names)
            content = zf.read('demo-repo/main.py').decode('utf-8')
            self.assertEqual(content, 'print("Hello DevHub")')

    def test_routes_status(self):
        """Verify public endpoints return 200 OK."""
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)

        res = self.client.get('/explore')
        self.assertEqual(res.status_code, 200)

        res = self.client.get('/security')
        self.assertEqual(res.status_code, 200)

        res = self.client.get('/auth/login')
        self.assertEqual(res.status_code, 200)

        res = self.client.get('/auth/register')
        self.assertEqual(res.status_code, 200)

if __name__ == '__main__':
    unittest.main()
