import datetime
import time
from collections import defaultdict

# Simple, effective in-memory rate limiter for login & registration protection
class SimpleRateLimiter:
    def __init__(self, max_attempts=5, window_seconds=300):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.attempts = defaultdict(list)
    
    def is_rate_limited(self, key):
        now = time.time()
        # Clean older attempts
        self.attempts[key] = [t for t in self.attempts[key] if now - t < self.window_seconds]
        return len(self.attempts[key]) >= self.max_attempts
    
    def record_attempt(self, key):
        self.attempts[key].append(time.time())
    
    def reset(self, key):
        if key in self.attempts:
            del self.attempts[key]

# Global instance for login attempts (5 tries per 5 minutes per IP/username)
login_limiter = SimpleRateLimiter(max_attempts=5, window_seconds=300)

def time_ago(dt):
    """Returns human readable relative time like '3 minutes ago', 'yesterday', etc."""
    if not dt:
        return ""
    now = datetime.datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    if seconds < 60:
        return "just now"
    minutes = int(seconds // 60)
    if minutes < 60:
        return f"{minutes}m ago"
    hours = int(minutes // 60)
    if hours < 24:
        return f"{hours}h ago"
    days = int(hours // 24)
    if days < 7:
        return f"{days}d ago"
    if days < 30:
        weeks = days // 7
        return f"{weeks}w ago"
    months = days // 30
    if months < 12:
        return f"{months}mo ago"
    years = days // 365
    return f"{years}y ago"

def format_file_size(size_in_bytes):
    """Formats raw bytes into human readable KB/MB."""
    if not size_in_bytes:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.1f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.1f} TB"

def get_language_color(lang):
    """GitHub-like language color mapping."""
    colors = {
        'Python': '#3572A5',
        'JavaScript': '#f1e05a',
        'TypeScript': '#3178c6',
        'Rust': '#dea584',
        'Go': '#00ADD8',
        'C++': '#f34b7d',
        'C': '#555555',
        'HTML': '#e34c26',
        'CSS': '#563d7c',
        'Java': '#b07219',
        'Ruby': '#701516',
        'PHP': '#4F5D95',
        'Swift': '#F05138',
        'Kotlin': '#A97BFF',
        'Shell': '#89e051',
        'Dart': '#00B4AB',
        'Solidity': '#AA6746',
        'SQL': '#e38c00',
        'Markdown': '#083fa1',
        'Other': '#8b949e'
    }
    return colors.get(lang, '#8b949e')

def generate_default_avatar_svg(name):
    """Generates a stylish SVG avatar with the user's initial and developer gradient."""
    initial = (name[:1] if name else 'D').upper()
    
    # Simple hash of name to choose gradient colors
    hash_val = sum(ord(c) for c in (name or "dev")) % 6
    gradients = [
        ("#6366f1", "#4f46e5"), # Indigo
        ("#06b6d4", "#0891b2"), # Cyan
        ("#10b981", "#059669"), # Emerald
        ("#f59e0b", "#d97706"), # Amber
        ("#8b5cf6", "#7c3aed"), # Purple
        ("#ec4899", "#db2777"), # Pink
    ]
    c1, c2 = gradients[hash_val]
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100%" height="100%">
  <defs>
    <linearGradient id="grad_{hash_val}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{c1};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{c2};stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="100" height="100" rx="50" fill="url(#grad_{hash_val})" />
  <text x="50" y="62" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="42" font-weight="700" fill="#ffffff" text-anchor="middle">{initial}</text>
</svg>'''
    return svg
