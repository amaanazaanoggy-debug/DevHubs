import os
import re
import bleach
import markdown
from functools import wraps
from flask import session, abort, request
import secrets
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer, TextLexer
from pygments.formatters import HtmlFormatter

# Allowed tags & attributes for safe Markdown rendering (Strict XSS Prevention)
ALLOWED_TAGS = [
    'p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'strong', 'em', 'b', 'i', 'u', 'strike', 'del', 's',
    'code', 'pre', 'blockquote', 'hr', 'br',
    'ul', 'ol', 'li', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'a', 'img'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'title', 'width', 'height', 'loading'],
    'code': ['class'],
    'pre': ['class'],
    'span': ['class'],
    'div': ['class'],
    'th': ['align'],
    'td': ['align']
}

ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']

def render_safe_markdown(text):
    """
    Converts Markdown to sanitized, safe HTML.
    Prevents script injection, event handler exploits (e.g. onload, onerror), and malicious URIs.
    """
    if not text:
        return ""
    
    # Render markdown with codehilite and fenced_code extensions
    raw_html = markdown.markdown(
        text,
        extensions=[
            'fenced_code',
            'codehilite',
            'tables',
            'nl2br',
            'sane_lists'
        ]
    )
    
    # Strictly sanitize HTML with bleach
    cleaned_html = bleach.clean(
        raw_html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True
    )
    
    # Linkify URLs automatically and enforce noopener noreferrer
    cleaned_html = bleach.linkify(
        cleaned_html,
        callbacks=[_sanitize_link_callback]
    )
    
    return cleaned_html

def _sanitize_link_callback(attrs, new=False):
    """Ensure all links are safe and have secure rel attributes."""
    attrs[(None, 'rel')] = 'noopener noreferrer nofollow'
    attrs[(None, 'target')] = '_blank'
    return attrs

def is_safe_path(base_directory, path, follow_symlinks=True):
    """
    Prevents directory traversal (e.g. ../../Windows/System32).
    Verifies that the target path is strictly within the allowed base directory.
    """
    if follow_symlinks:
        matchpath = os.path.realpath(path)
        basepath = os.path.realpath(base_directory)
    else:
        matchpath = os.path.abspath(path)
        basepath = os.path.abspath(base_directory)
    
    return basepath == os.path.commonpath((basepath, matchpath))

def generate_csrf_token():
    """Generates or retrieves a session CSRF token."""
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(24)
    return session['_csrf_token']

def validate_csrf():
    """Validates the CSRF token on mutating requests."""
    token = request.form.get('csrf_token') or request.headers.get('X-CSRFToken')
    expected_token = session.get('_csrf_token')
    if not token or not expected_token or not secrets.compare_digest(token, expected_token):
        abort(400, description="Invalid or missing CSRF security token.")

def highlight_code_file(code_content, language=None, filename=None):
    """
    Performs server-side syntax highlighting using Pygments with line numbers.
    """
    try:
        if language:
            lexer = get_lexer_by_name(language.lower(), stripall=True)
        elif filename:
            # Determine from filename extension
            ext = filename.split('.')[-1].lower() if '.' in filename else ''
            ext_map = {
                'py': 'python',
                'js': 'javascript',
                'ts': 'typescript',
                'jsx': 'jsx',
                'tsx': 'tsx',
                'html': 'html',
                'css': 'css',
                'json': 'json',
                'sql': 'sql',
                'c': 'c',
                'cpp': 'cpp',
                'h': 'c',
                'hpp': 'cpp',
                'rs': 'rust',
                'go': 'go',
                'java': 'java',
                'sh': 'bash',
                'bat': 'bat',
                'yml': 'yaml',
                'yaml': 'yaml',
                'toml': 'toml',
                'md': 'markdown'
            }
            lexer_name = ext_map.get(ext)
            if lexer_name:
                lexer = get_lexer_by_name(lexer_name, stripall=True)
            else:
                lexer = guess_lexer(code_content)
        else:
            lexer = guess_lexer(code_content)
    except Exception:
        lexer = TextLexer()

    formatter = HtmlFormatter(
        linenos='table',
        cssclass='syntax-highlight',
        linespans='line'
    )
    return highlight(code_content, lexer, formatter)
