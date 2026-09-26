from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models import db, Post, PostComment, Project, Activity
from app.utils.security import highlight_code_file

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/create', methods=['POST'])
@login_required
def create():
    content = request.form.get('content', '').strip()
    code_snippet = request.form.get('code_snippet', '').strip()
    code_language = request.form.get('code_language', '').strip()
    project_id = request.form.get('project_id')

    if not content and not code_snippet:
        flash("Post content or code snippet cannot be empty.", 'danger')
        return redirect(request.referrer or url_for('main.index'))

    # Validate project attachment if provided
    valid_project_id = None
    if project_id and project_id.isdigit():
        p = Project.query.get(int(project_id))
        if p and (p.is_public or p.user_id == current_user.id):
            valid_project_id = p.id

    post = Post(
        user_id=current_user.id,
        content=content,
        code_snippet=code_snippet if code_snippet else None,
        code_language=code_language if code_language else None,
        project_id=valid_project_id
    )
    db.session.add(post)
    db.session.commit()

    # Activity log
    activity = Activity(
        user_id=current_user.id,
        activity_type='post_created',
        description=f"Shared a developer update",
        link=url_for('posts.view_post', post_id=post.id)
    )
    db.session.add(activity)
    db.session.commit()

    flash("Post shared successfully!", 'success')
    return redirect(url_for('main.index'))

@posts_bp.route('/<int:post_id>')
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    comments = post.comments.order_by(PostComment.created_at.asc()).all()
    
    highlighted_code = None
    if post.code_snippet:
        highlighted_code = highlight_code_file(post.code_snippet, language=post.code_language)

    has_liked = current_user.is_authenticated and current_user.has_liked(post)
    has_bookmarked = current_user.is_authenticated and current_user.has_bookmarked(post)

    return render_template(
        'posts/view.html',
        post=post,
        comments=comments,
        highlighted_code=highlighted_code,
        has_liked=has_liked,
        has_bookmarked=has_bookmarked
    )

@posts_bp.route('/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form.get('content', '').strip()

    if content:
        comment = PostComment(
            post_id=post.id,
            user_id=current_user.id,
            content=content
        )
        post.comments_count += 1
        db.session.add(comment)
        db.session.commit()
        flash("Comment posted.", 'success')

    return redirect(url_for('posts.view_post', post_id=post.id))

@posts_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        abort(403)

    db.session.delete(post)
    db.session.commit()
    flash("Post deleted.", 'info')
    return redirect(url_for('main.index'))

@posts_bp.route('/bookmarks')
@login_required
def bookmarks():
    bookmarked_posts = current_user.bookmarked_posts.order_by(Post.created_at.desc()).all()
    return render_template('posts/bookmarks.html', posts=bookmarked_posts)
