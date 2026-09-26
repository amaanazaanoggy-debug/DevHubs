# DevHub 🚀

> **The Safe, Self-Hosted Developer Social Network & GitHub-like Showcase**

DevHub is a full-featured developer social media platform and code showcase designed specifically to run **safely and privately on your personal computer**. It allows developers to share updates, publish code snippets, host and view multi-file repositories with syntax highlighting, track issues, follow other engineers, and build developer portfolios without relying on external cloud providers.

---

## 🛡️ Security & Safe PC Architecture

One of the core design goals of DevHub is **complete PC and data safety**:

- **100% Local-First Sandbox**: Binds strictly to your computer's loopback interface (`127.0.0.1`). It never opens external listening ports on your router or firewall, and never sends telemetry to remote cloud servers.
- **Zero Administrative Privileges**: Runs entirely in standard user space. It requires no administrator or `root` permissions, installs no background system services, and alters no Windows registry keys.
- **Self-Contained Database**: Uses a local SQLite database (`devhub.db`) with zero external database server setup (no Postgres/MySQL services needed on your machine).
- **Cryptographic Password Hashing**: Passwords are securely hashed with memory-hard algorithms (`scrypt` / `pbkdf2:sha256`) with unique cryptographic salts. Passwords are never stored in plaintext.
- **Brute-Force Rate Limiting**: Built-in login throttle automatically temporarily locks repeated failed attempts, preventing dictionary attacks.
- **Strict XSS & HTML Sanitization**: All markdown posts, README files, and comments are sanitized through `bleach` to completely neutralize malicious scripts, iframes, and JavaScript event injections (`onerror`, `onload`).
- **Path Traversal Protection**: File viewers and repository download handlers enforce directory boundary checks (`os.path.commonpath`), guaranteeing that access outside the project directory is blocked.
- **In-Memory ZIP Generation**: Repository downloads are generated dynamically in RAM via Python's `zipfile` and streamed directly to the browser without writing temporary files to your drive.

---

## 🌟 Key Features

### 1. GitHub-like Repositories & Code Browser
- **Project Repositories**: Create and showcase projects with titles, taglines, primary language, topics/tags, and licenses (MIT, Apache 2.0, GPL, etc.).
- **Code Viewer**: Syntax-highlighted code viewer powered by Pygments with line numbers, file sizes, line counts, and 1-click clipboard copy.
- **Add / Upload Code Files**: Add new code files directly in the browser or upload existing scripts from your computer.
- **README.md Auto-Rendering**: Formatted markdown documentation rendered directly under the repository file tree.
- **In-Memory ZIP Downloads**: Download any repository's files as a clean `.zip` archive with one click.
- **Project Issue Tracker**: Open bugs, feature requests, and questions with custom labels and threaded discussions; toggle issues between Open and Closed.

### 2. Developer Social Feed
- **Interactive Feed**: Share updates, architecture thoughts, and announcements with Markdown support.
- **Embedded Code Snippets**: Attach syntax-highlighted code snippets in Python, JavaScript, Rust, Go, SQL, Bash, and more.
- **Repository Showcases**: Link repositories directly to social posts with live star counters and language badges.
- **Instant Reactions (AJAX)**: Like, bookmark, and comment on posts with instant real-time UI updates without page reloads.
- **Following vs. Global Streams**: Filter your feed between all developers or only the engineers you follow.

### 3. Developer Profiles & Portfolios
- **Custom Profiles**: Display name, developer title, bio, location, personal website, and social links (GitHub, Twitter/X).
- **Tech Stack Pills**: Showcase your programming languages and tools (e.g. `Python`, `Rust`, `Docker`, `React`).
- **GitHub-Style Contribution Heatmap**: Visual contribution squares representing developer activity.
- **Pinned Repositories**: Highlight your best open-source creations at the top of your profile.
- **Follow Network**: Follow and unfollow developers with live follower and following lists.

### 4. Explore & Search
- Search across repositories, posts, and developers with category filters.
- Trending tags and topics (`#python`, `#machine-learning`, `#rust`, `#api`, `#webdev`, `#ai`).
- Top starred repositories and suggested developers to follow.

---

## ⚡ Quick Start (Windows)

### Option A: One-Click Run (Easiest)
Simply double-click the included batch file in this directory:
```batch
setup_and_run.bat
```
This script will:
1. Detect your Python installation.
2. Initialize an isolated virtual environment (`.venv`).
3. Install the required libraries safely.
4. Automatically open your browser to `http://127.0.0.1:5000`.

### Option B: Command Line (PowerShell or Command Prompt)
```powershell
# 1. Activate the virtual environment
.\.venv\Scripts\activate

# 2. Run the server
python run.py
```
Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

---

## 👥 Pre-Seeded Sample Accounts

DevHub comes pre-loaded with sample developer profiles and repositories so you can explore all features immediately:

| Username | Role | Password | Sample Repositories |
| :--- | :--- | :--- | :--- |
| `alex_dev` | Senior Backend Engineer | `password123` | `secure-auth-gateway` |
| `sarah_ai` | ML Engineer & Researcher | `password123` | `neural-search-engine` |
| `marcus_rust` | Systems Engineer | `password123` | `rusty-kv` |
| `elena_ui` | Frontend Architect | `password123` | `micro-router` |

*You can also click **Sign Up** on the top navigation bar to create your own custom account!*

---

## 🧪 Running Automated Tests

To run the automated security and functionality test suite:
```powershell
.\.venv\Scripts\python test_app.py
```

Tests verify:
- Cryptographic password hashing (`scrypt`/`pbkdf2`)
- XSS neutralization via `bleach`
- Path traversal defense
- Brute-force rate limiting
- In-memory ZIP archive generation
- HTTP route status codes

---

## 📂 Project Structure

```
developers social media/
├── app/
│   ├── __init__.py           # Application factory & security headers
│   ├── models.py             # User, Project, File, Issue, Post models
│   ├── routes/
│   │   ├── auth.py           # Register, login, rate limiting
│   │   ├── main.py           # Feed, explore, search, security docs
│   │   ├── projects.py       # GitHub-like repositories & file viewer
│   │   ├── posts.py          # Social posts, snippets & discussions
│   │   ├── profile.py        # Developer profiles & settings
│   │   └── api.py            # AJAX star, like, follow, bookmark endpoints
│   ├── utils/
│   │   ├── security.py       # Bleach XSS sanitizer & path traversal check
│   │   └── helpers.py        # Avatars, formatters & rate limiter
│   ├── templates/            # Clean, dark-mode GitHub-styled Jinja2 templates
│   └── static/
│       ├── css/              # Pygments syntax highlighting & custom styles
│       └── js/app.js         # Client-side AJAX interactions
├── config.py                 # Security & database configuration
├── requirements.txt          # Python dependencies
├── run.py                    # Server runner
├── seed_data.py              # Sample developers & showcase repositories
├── setup_and_run.bat         # 1-click Windows launcher
├── run.bat                   # Fast subsequent launcher
├── test_app.py               # Automated unit & security test suite
└── README.md                 # Full documentation
```
