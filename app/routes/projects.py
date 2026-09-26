import io
import zipfile
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import db, Project, ProjectFile, ProjectIssue, IssueComment, Activity, User
from app.utils.security import highlight_code_file

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/')
def list_projects():
    sort = request.args.get('sort', 'trending')
    language = request.args.get('language')
    
    query = Project.query.filter_by(is_public=True)
    if language:
        query = query.filter_by(primary_language=language)
        
    if sort == 'recent':
        projects = query.order_by(Project.created_at.desc()).limit(30).all()
    elif sort == 'stars':
        projects = query.order_by(Project.stars_count.desc()).limit(30).all()
    else:  # trending
        projects = query.order_by(Project.stars_count.desc(), Project.updated_at.desc()).limit(30).all()

    languages = ['Python', 'JavaScript', 'TypeScript', 'Rust', 'Go', 'C++', 'Java', 'HTML', 'CSS', 'Other']
    return render_template('projects/list.html', projects=projects, sort=sort, selected_lang=language, languages=languages)

@projects_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        tagline = request.form.get('tagline', '').strip()
        description = request.form.get('description', '').strip()
        readme = request.form.get('readme_content', '').strip()
        primary_language = request.form.get('primary_language', 'Python').strip()
        topics = request.form.get('topics', '').strip()
        license_type = request.form.get('license', 'MIT').strip()
        github_url = request.form.get('github_url', '').strip()
        demo_url = request.form.get('demo_url', '').strip()
        is_public = request.form.get('is_public', '1') == '1'

        if not name:
            flash("Project name is required.", 'danger')
            return render_template('projects/create.html')

        # Check duplicate name for this user
        existing = Project.query.filter_by(user_id=current_user.id, name=name).first()
        if existing:
            flash("You already have a project with this name.", 'danger')
            return render_template('projects/create.html')

        # If no custom README was provided, generate a clean default
        if not readme:
            readme = f"# {name}\n\n{tagline or 'A project on DevHub.'}\n\n## Overview\n{description or 'Write your project overview here.'}\n\n## Getting Started\nClone or download this project to get started.\n"

        project = Project(
            user_id=current_user.id,
            name=name,
            tagline=tagline,
            description=description,
            readme_content=readme,
            primary_language=primary_language,
            topics=topics,
            license=license_type,
            github_url=github_url,
            demo_url=demo_url,
            is_public=is_public
        )
        db.session.add(project)
        db.session.commit()

        # Add initial README.md as a project file
        readme_file = ProjectFile(
            project_id=project.id,
            filename='README.md',
            content=readme,
            file_size=len(readme.encode('utf-8')),
            language='markdown'
        )
        db.session.add(readme_file)

        # Log Activity
        activity = Activity(
            user_id=current_user.id,
            activity_type='project_created',
            description=f"Created repository {project.name}",
            link=url_for('projects.view_project', project_id=project.id)
        )
        db.session.add(activity)
        db.session.commit()

        flash(f"Project '{project.name}' successfully created!", 'success')
        return redirect(url_for('projects.view_project', project_id=project.id))

    return render_template('projects/create.html')

@projects_bp.route('/<int:project_id>')
def view_project(project_id):
    project = Project.query.get_or_404(project_id)
    if not project.is_public and (not current_user.is_authenticated or current_user.id != project.user_id):
        abort(403)

    files = project.files.order_by(ProjectFile.filename.asc()).all()
    recent_issues = project.issues.order_by(ProjectIssue.created_at.desc()).limit(5).all()
    open_issues_count = project.issues.filter_by(status='open').count()
    has_starred = current_user.is_authenticated and current_user.has_starred(project)

    return render_template(
        'projects/view.html',
        project=project,
        files=files,
        recent_issues=recent_issues,
        open_issues_count=open_issues_count,
        has_starred=has_starred
    )

@projects_bp.route('/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        project.tagline = request.form.get('tagline', '').strip()
        project.description = request.form.get('description', '').strip()
        project.readme_content = request.form.get('readme_content', '').strip()
        project.primary_language = request.form.get('primary_language', 'Python').strip()
        project.topics = request.form.get('topics', '').strip()
        project.license = request.form.get('license', 'MIT').strip()
        project.github_url = request.form.get('github_url', '').strip()
        project.demo_url = request.form.get('demo_url', '').strip()
        project.is_public = request.form.get('is_public', '1') == '1'
        project.is_pinned = bool(request.form.get('is_pinned'))

        # Also update README.md file in project files if it exists
        readme_file = project.files.filter_by(filename='README.md').first()
        if readme_file:
            readme_file.content = project.readme_content
            readme_file.file_size = len(project.readme_content.encode('utf-8'))

        db.session.commit()
        flash("Project settings updated successfully.", 'success')
        return redirect(url_for('projects.view_project', project_id=project.id))

    return render_template('projects/edit.html', project=project)

@projects_bp.route('/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)

    name = project.name
    db.session.delete(project)
    db.session.commit()
    flash(f"Project '{name}' was deleted.", 'info')
    return redirect(url_for('profile.view_profile', username=current_user.username))

@projects_bp.route('/<int:project_id>/files/add', methods=['GET', 'POST'])
@login_required
def add_file(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        filename = request.form.get('filename', '').strip()
        content = request.form.get('content', '')
        
        # Check if an uploaded file was provided instead
        uploaded_file = request.files.get('file_upload')
        if uploaded_file and uploaded_file.filename:
            filename = secure_filename(uploaded_file.filename)
            try:
                content = uploaded_file.read().decode('utf-8', errors='replace')
            except Exception:
                content = ""

        filename = secure_filename(filename)
        if not filename:
            flash("A valid filename is required.", 'danger')
            return render_template('projects/add_file.html', project=project)

        # Check if file already exists
        existing_file = project.files.filter_by(filename=filename).first()
        if existing_file:
            existing_file.content = content
            existing_file.file_size = len(content.encode('utf-8'))
            existing_file.updated_at = datetime.utcnow()
            flash(f"File '{filename}' updated successfully.", 'success')
        else:
            new_file = ProjectFile(
                project_id=project.id,
                filename=filename,
                content=content,
                file_size=len(content.encode('utf-8'))
            )
            db.session.add(new_file)
            flash(f"File '{filename}' added to repository.", 'success')

        project.updated_at = datetime.utcnow()
        db.session.commit()
        return redirect(url_for('projects.view_project', project_id=project.id))

    return render_template('projects/add_file.html', project=project)

@projects_bp.route('/<int:project_id>/files/<int:file_id>')
def view_file(project_id, file_id):
    project = Project.query.get_or_404(project_id)
    if not project.is_public and (not current_user.is_authenticated or current_user.id != project.user_id):
        abort(403)

    file = ProjectFile.query.filter_by(id=file_id, project_id=project.id).first_or_404()
    highlighted_code = highlight_code_file(file.content, filename=file.filename)

    return render_template(
        'projects/file_view.html',
        project=project,
        file=file,
        highlighted_code=highlighted_code
    )

@projects_bp.route('/<int:project_id>/files/<int:file_id>/delete', methods=['POST'])
@login_required
def delete_file(project_id, file_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)

    file = ProjectFile.query.filter_by(id=file_id, project_id=project.id).first_or_404()
    filename = file.filename
    db.session.delete(file)
    project.updated_at = datetime.utcnow()
    db.session.commit()
    flash(f"File '{filename}' was removed from the repository.", 'info')
    return redirect(url_for('projects.view_project', project_id=project.id))

@projects_bp.route('/<int:project_id>/download')
def download_zip(project_id):
    """Safely streams an in-memory ZIP of repository files without writing temporary files to disk."""
    project = Project.query.get_or_404(project_id)
    if not project.is_public and (not current_user.is_authenticated or current_user.id != project.user_id):
        abort(403)

    files = project.files.all()
    memory_file = io.BytesIO()

    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        # If no files, add README
        if not files:
            zf.writestr(f"{project.name}/README.md", project.readme_content or f"# {project.name}")
        for f in files:
            # Safe zip entry path
            safe_name = secure_filename(f.filename) or 'file'
            zf.writestr(f"{project.name}/{safe_name}", f.content or "")

    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f"{project.name}-main.zip"
    )

@projects_bp.route('/<int:project_id>/issues')
def list_issues(project_id):
    project = Project.query.get_or_404(project_id)
    status_filter = request.args.get('status', 'open')
    
    issues = project.issues.filter_by(status=status_filter).order_by(ProjectIssue.created_at.desc()).all()
    open_count = project.issues.filter_by(status='open').count()
    closed_count = project.issues.filter_by(status='closed').count()

    return render_template(
        'projects/issues.html',
        project=project,
        issues=issues,
        status_filter=status_filter,
        open_count=open_count,
        closed_count=closed_count
    )

@projects_bp.route('/<int:project_id>/issues/new', methods=['GET', 'POST'])
@login_required
def create_issue(project_id):
    project = Project.query.get_or_404(project_id)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        body = request.form.get('body', '').strip()
        label = request.form.get('label', 'issue').strip()

        if not title:
            flash("Issue title is required.", 'danger')
            return render_template('projects/create_issue.html', project=project)

        issue = ProjectIssue(
            project_id=project.id,
            user_id=current_user.id,
            title=title,
            body=body,
            label=label
        )
        db.session.add(issue)
        db.session.commit()

        flash("Issue opened successfully.", 'success')
        return redirect(url_for('projects.view_issue', project_id=project.id, issue_id=issue.id))

    return render_template('projects/create_issue.html', project=project)

@projects_bp.route('/<int:project_id>/issues/<int:issue_id>')
def view_issue(project_id, issue_id):
    project = Project.query.get_or_404(project_id)
    issue = ProjectIssue.query.filter_by(id=issue_id, project_id=project.id).first_or_404()
    comments = issue.comments.order_by(IssueComment.created_at.asc()).all()

    return render_template(
        'projects/view_issue.html',
        project=project,
        issue=issue,
        comments=comments
    )

@projects_bp.route('/<int:project_id>/issues/<int:issue_id>/comment', methods=['POST'])
@login_required
def comment_issue(project_id, issue_id):
    project = Project.query.get_or_404(project_id)
    issue = ProjectIssue.query.filter_by(id=issue_id, project_id=project.id).first_or_404()
    
    body = request.form.get('body', '').strip()
    if body:
        comment = IssueComment(
            issue_id=issue.id,
            user_id=current_user.id,
            body=body
        )
        db.session.add(comment)
        db.session.commit()
        flash("Comment added.", 'success')

    return redirect(url_for('projects.view_issue', project_id=project.id, issue_id=issue.id))

@projects_bp.route('/<int:project_id>/issues/<int:issue_id>/toggle', methods=['POST'])
@login_required
def toggle_issue_status(project_id, issue_id):
    project = Project.query.get_or_404(project_id)
    issue = ProjectIssue.query.filter_by(id=issue_id, project_id=project.id).first_or_404()

    # Only project owner or issue creator can toggle status
    if current_user.id != project.user_id and current_user.id != issue.user_id:
        abort(403)

    if issue.status == 'open':
        issue.status = 'closed'
        issue.closed_at = datetime.utcnow()
        flash("Issue marked as closed.", 'info')
    else:
        issue.status = 'open'
        issue.closed_at = None
        flash("Issue re-opened.", 'success')

    db.session.commit()
    return redirect(url_for('projects.view_issue', project_id=project.id, issue_id=issue.id))
