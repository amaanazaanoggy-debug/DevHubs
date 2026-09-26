import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.security import render_safe_markdown
from app.utils.helpers import time_ago, get_language_color

db = SQLAlchemy()

# Association tables
followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.datetime.utcnow)
)

project_stars = db.Table(
    'project_stars',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.datetime.utcnow)
)

post_likes = db.Table(
    'post_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.datetime.utcnow)
)

post_bookmarks = db.Table(
    'post_bookmarks',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.datetime.utcnow)
)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    display_name = db.Column(db.String(64), nullable=False)
    title = db.Column(db.String(120), default="Software Developer")
    bio = db.Column(db.Text, default="")
    location = db.Column(db.String(64), default="")
    website = db.Column(db.String(200), default="")
    github_username = db.Column(db.String(64), default="")
    twitter_username = db.Column(db.String(64), default="")
    skills = db.Column(db.String(256), default="")  # Comma-separated: "Python, Docker, React"
    avatar_path = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    projects = db.relationship('Project', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    posts = db.relationship('Post', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('PostComment', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    activities = db.relationship('Activity', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    # Follow system
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )
    
    # Starred projects
    starred_projects = db.relationship(
        'Project', secondary=project_stars,
        backref=db.backref('stargazers', lazy='dynamic'),
        lazy='dynamic'
    )
    
    # Liked & Bookmarked posts
    liked_posts = db.relationship(
        'Post', secondary=post_likes,
        backref=db.backref('likers', lazy='dynamic'),
        lazy='dynamic'
    )
    bookmarked_posts = db.relationship(
        'Post', secondary=post_bookmarks,
        backref=db.backref('bookmarkers', lazy='dynamic'),
        lazy='dynamic'
    )

    def set_password(self, password):
        """Secure password hashing using Werkzeug default (scrypt/pbkdf2)."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def follow(self, user):
        if not self.is_following(user) and self.id != user.id:
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def star_project(self, project):
        if not self.has_starred(project):
            self.starred_projects.append(project)
            project.stars_count += 1

    def unstar_project(self, project):
        if self.has_starred(project):
            self.starred_projects.remove(project)
            project.stars_count = max(0, project.stars_count - 1)

    def has_starred(self, project):
        return self.starred_projects.filter(project_stars.c.project_id == project.id).count() > 0

    def like_post(self, post):
        if not self.has_liked(post):
            self.liked_posts.append(post)
            post.likes_count += 1

    def unlike_post(self, post):
        if self.has_liked(post):
            self.liked_posts.remove(post)
            post.likes_count = max(0, post.likes_count - 1)

    def has_liked(self, post):
        return self.liked_posts.filter(post_likes.c.post_id == post.id).count() > 0

    def toggle_bookmark(self, post):
        if self.has_bookmarked(post):
            self.bookmarked_posts.remove(post)
            return False
        else:
            self.bookmarked_posts.append(post)
            return True

    def has_bookmarked(self, post):
        return self.bookmarked_posts.filter(post_bookmarks.c.post_id == post.id).count() > 0

    @property
    def skill_list(self):
        if not self.skills:
            return []
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    def __repr__(self):
        return f'<User {self.username}>'


class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    tagline = db.Column(db.String(250), default="")
    description = db.Column(db.Text, default="")
    readme_content = db.Column(db.Text, default="")
    primary_language = db.Column(db.String(50), default="Python")
    topics = db.Column(db.String(200), default="")  # "web, api, ai"
    license = db.Column(db.String(50), default="MIT")
    github_url = db.Column(db.String(256), default="")
    demo_url = db.Column(db.String(256), default="")
    is_pinned = db.Column(db.Boolean, default=False)
    is_public = db.Column(db.Boolean, default=True)
    stars_count = db.Column(db.Integer, default=0)
    forks_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    files = db.relationship('ProjectFile', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    issues = db.relationship('ProjectIssue', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    posts = db.relationship('Post', backref='attached_project', lazy='dynamic')

    @property
    def topic_list(self):
        if not self.topics:
            return []
        return [t.strip() for t in self.topics.split(',') if t.strip()]

    @property
    def language_color(self):
        return get_language_color(self.primary_language)

    @property
    def formatted_readme(self):
        if not self.readme_content:
            return ""
        return render_safe_markdown(self.readme_content)

    @property
    def created_time_ago(self):
        return time_ago(self.created_at)

    @property
    def updated_time_ago(self):
        return time_ago(self.updated_at)

    def __repr__(self):
        return f'<Project {self.name}>'


class ProjectFile(db.Model):
    __tablename__ = 'project_files'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, index=True)
    filename = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text, default="")
    file_size = db.Column(db.Integer, default=0)
    language = db.Column(db.String(50), default="")
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    @property
    def line_count(self):
        if not self.content:
            return 0
        return len(self.content.splitlines())

    def __repr__(self):
        return f'<ProjectFile {self.filename}>'


class ProjectIssue(db.Model):
    __tablename__ = 'project_issues'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, default="")
    status = db.Column(db.String(20), default="open")  # "open" or "closed"
    label = db.Column(db.String(50), default="issue")  # bug, enhancement, question, documentation
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    closed_at = db.Column(db.DateTime, nullable=True)

    author = db.relationship('User', backref='created_issues')
    comments = db.relationship('IssueComment', backref='issue', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def formatted_body(self):
        return render_safe_markdown(self.body)

    @property
    def created_time_ago(self):
        return time_ago(self.created_at)

    def __repr__(self):
        return f'<ProjectIssue #{self.id} {self.title}>'


class IssueComment(db.Model):
    __tablename__ = 'issue_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('project_issues.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    author = db.relationship('User', backref='issue_comments')

    @property
    def formatted_body(self):
        return render_safe_markdown(self.body)

    @property
    def created_time_ago(self):
        return time_ago(self.created_at)


class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    code_snippet = db.Column(db.Text, nullable=True)
    code_language = db.Column(db.String(50), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, index=True)
    
    comments = db.relationship('PostComment', backref='post', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def formatted_content(self):
        return render_safe_markdown(self.content)

    @property
    def created_time_ago(self):
        return time_ago(self.created_at)

    def __repr__(self):
        return f'<Post #{self.id} by User {self.user_id}>'


class PostComment(db.Model):
    __tablename__ = 'post_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    @property
    def formatted_content(self):
        return render_safe_markdown(self.content)

    @property
    def created_time_ago(self):
        return time_ago(self.created_at)


class Activity(db.Model):
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    activity_type = db.Column(db.String(50), nullable=False)  # 'project_created', 'post_created', 'file_added', 'star'
    description = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, index=True)

    @property
    def created_time_ago(self):
        return time_ago(self.created_at)
