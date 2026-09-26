from flask import Blueprint, jsonify, request, abort
from flask_login import login_required, current_user
from app.models import db, User, Project, Post, Activity

api_bp = Blueprint('api', __name__)

@api_bp.route('/star/<int:project_id>', methods=['POST'])
@login_required
def toggle_star(project_id):
    project = Project.query.get_or_404(project_id)
    if not project.is_public and project.user_id != current_user.id:
        abort(403)

    if current_user.has_starred(project):
        current_user.unstar_project(project)
        starred = False
    else:
        current_user.star_project(project)
        starred = True
        # Activity log
        if project.user_id != current_user.id:
            activity = Activity(
                user_id=current_user.id,
                activity_type='star',
                description=f"Starred repository {project.name}",
                link=f"/projects/{project.id}"
            )
            db.session.add(activity)

    db.session.commit()
    return jsonify({
        'success': True,
        'starred': starred,
        'count': project.stars_count
    })

@api_bp.route('/like/<int:post_id>', methods=['POST'])
@login_required
def toggle_like(post_id):
    post = Post.query.get_or_404(post_id)

    if current_user.has_liked(post):
        current_user.unlike_post(post)
        liked = False
    else:
        current_user.like_post(post)
        liked = True

    db.session.commit()
    return jsonify({
        'success': True,
        'liked': liked,
        'count': post.likes_count
    })

@api_bp.route('/bookmark/<int:post_id>', methods=['POST'])
@login_required
def toggle_bookmark(post_id):
    post = Post.query.get_or_404(post_id)
    is_bookmarked = current_user.toggle_bookmark(post)
    db.session.commit()
    return jsonify({
        'success': True,
        'bookmarked': is_bookmarked
    })

@api_bp.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def toggle_follow(user_id):
    if user_id == current_user.id:
        return jsonify({'success': False, 'error': 'Cannot follow yourself'}), 400

    target_user = User.query.get_or_404(user_id)

    if current_user.is_following(target_user):
        current_user.unfollow(target_user)
        following = False
    else:
        current_user.follow(target_user)
        following = True
        # Activity log
        activity = Activity(
            user_id=current_user.id,
            activity_type='follow',
            description=f"Followed @{target_user.username}",
            link=f"/u/{target_user.username}"
        )
        db.session.add(activity)

    db.session.commit()
    return jsonify({
        'success': True,
        'following': following,
        'followers_count': target_user.followers.count()
    })
