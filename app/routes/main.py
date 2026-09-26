from flask import Blueprint, render_template, request
from flask_login import current_user
from sqlalchemy import or_, desc
from app.models import db, User, Project, Post, Activity

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    feed_type = request.args.get('feed', 'global')
    
    # Query posts based on feed tab
    if feed_type == 'following' and current_user.is_authenticated:
        # Get posts from people the current user follows + their own
        following_ids = [u.id for u in current_user.followed.all()]
        following_ids.append(current_user.id)
        posts_query = Post.query.filter(Post.user_id.in_(following_ids))
    else:
        feed_type = 'global'
        posts_query = Post.query

    posts = posts_query.order_by(Post.created_at.desc()).limit(30).all()

    # Sidebar data: Top trending projects and suggested developers
    trending_projects = Project.query.filter_by(is_public=True).order_by(
        Project.stars_count.desc(), Project.created_at.desc()
    ).limit(5).all()

    suggested_users = []
    if current_user.is_authenticated:
        # Find users the current user does not yet follow
        following_ids = [u.id for u in current_user.followed.all()]
        following_ids.append(current_user.id)
        suggested_users = User.query.filter(~User.id.in_(following_ids)).limit(4).all()
    else:
        suggested_users = User.query.limit(4).all()

    # User's recent projects for quick access in left sidebar
    user_projects = []
    if current_user.is_authenticated:
        user_projects = Project.query.filter_by(user_id=current_user.id).order_by(
            Project.updated_at.desc()
        ).limit(6).all()

    return render_template(
        'main/index.html',
        posts=posts,
        feed_type=feed_type,
        trending_projects=trending_projects,
        suggested_users=suggested_users,
        user_projects=user_projects
    )

@main_bp.route('/explore')
def explore():
    query = request.args.get('q', '').strip()
    tag = request.args.get('tag', '').strip()
    category = request.args.get('category', 'all')
    
    projects = []
    posts = []
    users = []

    if query:
        search_term = f"%{query}%"
        if category in ('all', 'projects'):
            projects = Project.query.filter(
                Project.is_public == True,
                or_(
                    Project.name.ilike(search_term),
                    Project.tagline.ilike(search_term),
                    Project.description.ilike(search_term),
                    Project.topics.ilike(search_term),
                    Project.primary_language.ilike(search_term)
                )
            ).order_by(Project.stars_count.desc()).limit(20).all()

        if category in ('all', 'posts'):
            posts = Post.query.filter(
                Post.content.ilike(search_term)
            ).order_by(Post.created_at.desc()).limit(20).all()

        if category in ('all', 'users'):
            users = User.query.filter(
                or_(
                    User.username.ilike(search_term),
                    User.display_name.ilike(search_term),
                    User.title.ilike(search_term),
                    User.skills.ilike(search_term),
                    User.bio.ilike(search_term)
                )
            ).limit(20).all()
    elif tag:
        tag_term = f"%{tag}%"
        projects = Project.query.filter(
            Project.is_public == True,
            Project.topics.ilike(tag_term)
        ).order_by(Project.stars_count.desc()).limit(20).all()
    else:
        # Default explore view: Most starred projects and active devs
        projects = Project.query.filter_by(is_public=True).order_by(
            Project.stars_count.desc(), Project.updated_at.desc()
        ).limit(12).all()
        users = User.query.order_by(User.created_at.desc()).limit(8).all()

    popular_tags = [
        'python', 'javascript', 'react', 'machine-learning', 'rust',
        'api', 'webdev', 'docker', 'database', 'tools', 'ai', 'cloud'
    ]

    return render_template(
        'main/explore.html',
        query=query,
        tag=tag,
        category=category,
        projects=projects,
        posts=posts,
        users=users,
        popular_tags=popular_tags
    )

@main_bp.route('/security')
def security_info():
    """Security transparency page explaining the local-first safeguards."""
    return render_template('main/security.html')
