import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, Response, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import db, User, Project, Post, Activity
from app.utils.helpers import generate_default_avatar_svg
from app.utils.security import is_safe_path

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/<username>')
def view_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    tab = request.args.get('tab', 'projects')
    
    # Filter projects: owner sees both private & public, others see only public
    if current_user.is_authenticated and current_user.id == user.id:
        projects = user.projects.order_by(Project.is_pinned.desc(), Project.updated_at.desc()).all()
    else:
        projects = user.projects.filter_by(is_public=True).order_by(Project.is_pinned.desc(), Project.updated_at.desc()).all()

    posts = user.posts.order_by(Post.created_at.desc()).limit(20).all()
    activities = user.activities.order_by(Activity.created_at.desc()).limit(15).all()

    is_following = current_user.is_authenticated and current_user.is_following(user)

    # Calculate contribution stats
    total_stars_received = sum(p.stars_count for p in user.projects)
    total_repos = user.projects.count()
    total_posts = user.posts.count()

    return render_template(
        'profile/view.html',
        user=user,
        projects=projects,
        posts=posts,
        activities=activities,
        is_following=is_following,
        tab=tab,
        total_stars=total_stars_received,
        total_repos=total_repos,
        total_posts=total_posts
    )

@profile_bp.route('/settings/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.display_name = request.form.get('display_name', '').strip() or current_user.username
        current_user.title = request.form.get('title', '').strip()
        current_user.bio = request.form.get('bio', '').strip()
        current_user.location = request.form.get('location', '').strip()
        current_user.website = request.form.get('website', '').strip()
        current_user.github_username = request.form.get('github_username', '').strip()
        current_user.twitter_username = request.form.get('twitter_username', '').strip()
        current_user.skills = request.form.get('skills', '').strip()

        # Handle avatar file upload
        avatar_file = request.files.get('avatar')
        if avatar_file and avatar_file.filename:
            filename = secure_filename(avatar_file.filename)
            ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
            if ext in current_app.config['ALLOWED_AVATAR_EXTENSIONS']:
                saved_filename = f"user_{current_user.id}_{int(os.times().elapsed)}.{ext}"
                target_path = os.path.join(current_app.config['AVATARS_FOLDER'], saved_filename)
                avatar_file.save(target_path)
                current_user.avatar_path = saved_filename
            else:
                flash("Invalid image format. Allowed: PNG, JPG, GIF, WEBP, SVG.", 'warning')

        db.session.commit()
        flash("Profile updated successfully!", 'success')
        return redirect(url_for('profile.view_profile', username=current_user.username))

    return render_template('profile/edit.html')

@profile_bp.route('/settings/security', methods=['GET', 'POST'])
@login_required
def security_settings():
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not current_user.check_password(current_password):
            flash("Incorrect current password.", 'danger')
            return render_template('profile/security.html')

        if len(new_password) < 6:
            flash("New password must be at least 6 characters.", 'danger')
            return render_template('profile/security.html')

        if new_password != confirm_password:
            flash("New passwords do not match.", 'danger')
            return render_template('profile/security.html')

        current_user.set_password(new_password)
        db.session.commit()
        flash("Password changed successfully.", 'success')
        return redirect(url_for('profile.view_profile', username=current_user.username))

    return render_template('profile/security.html')

@profile_bp.route('/<username>/followers')
def followers_list(username):
    user = User.query.filter_by(username=username).first_or_404()
    followers = user.followers.all()
    return render_template('profile/followers.html', user=user, users=followers, title="Followers")

@profile_bp.route('/<username>/following')
def following_list(username):
    user = User.query.filter_by(username=username).first_or_404()
    following = user.followed.all()
    return render_template('profile/followers.html', user=user, users=following, title="Following")

@profile_bp.route('/avatar/<username>.svg')
def get_user_avatar(username):
    """Dynamic generator for user avatars."""
    user = User.query.filter_by(username=username).first()
    name = user.display_name if user else username
    svg_data = generate_default_avatar_svg(name)
    return Response(svg_data, mimetype='image/svg+xml')

@profile_bp.route('/avatar/uploaded/<filename>')
def serve_avatar(filename):
    """Safely serves uploaded profile avatars."""
    safe_name = secure_filename(filename)
    avatars_dir = current_app.config['AVATARS_FOLDER']
    if not is_safe_path(avatars_dir, os.path.join(avatars_dir, safe_name)):
        abort(403)
    return send_from_directory(avatars_dir, safe_name)
