import os
from flask import (
    Blueprint,
    render_template,
    request,
    abort,
    flash,
    redirect,
    url_for,
    current_app,
)
from flask_login import login_required, current_user
from mlcollab.users.models import (
    Users,
    Learners,
    Devs,
    LogHistory,
    Users_Info,
    Models,
    ModelDetails,
    ModelFiles,
    Posts,
    PostData,
    PostComments,
)
from mlcollab.public.forms import (
    UpdateProfileForm,
    ChangePasswordForm,
    ModelSearchForm,
)
from mlcollab import db, hash_controller
from mlcollab.public.utils import (
    add_datetime,
    save_profile_picture,
    profile_picture_remover,
)


admin = Blueprint(name="admin", import_name=__name__, url_prefix="/admin")


@admin.route("/dashboard/overview")
@login_required
def dashboard():
    if current_user.role != "Admin":
        abort(403)
    
    totals = {
        "learner": Users.query.filter(Users.role == "learner").count(),
        "developer": Users.query.filter(Users.role == "developer").count(),
        "models": Models.query.filter(Models.model_id).count(),
        "posts": Posts.query.filter(Posts.post_id).count(),
        "comments": PostComments.query.filter(PostComments.comment_id).count(),
        "support_files": ModelFiles.query.filter(ModelFiles.file_id).count(),
        "upload_model": LogHistory.query.filter(
            LogHistory.activity == "Upload Model"
        ).count(),
        "delete_support_files": LogHistory.query.filter(
            LogHistory.activity == "Delete Support Files"
        ).count(),
        "delete_model": LogHistory.query.filter(
            LogHistory.activity == "Delete Model"
        ).count(),
        "delete_comments": LogHistory.query.filter(
            LogHistory.activity == "Delete Comment"
        ).count(),
    }
   
    return render_template("admin/overview.html", totals=totals, title="Overview")


@admin.route("/dashboard/profile")
@login_required
def profile():
    return render_template("admin/admin_profile.html")


@admin.route("/dashboard/learner")
@login_required
def learner():
    page = request.args.get("page", 1, int)

    learners = (
        Learners.query.join(Users, Learners.learner_id == Users.id)
        .join(Users_Info, Learners.learner_id == Users_Info.i_id)
        .add_columns(
            Users.id,
            Users.username,
            Users.email,
            Users.points,
            Learners.learner_id,
            Users_Info.last_name,
            Users_Info.first_name,
            Users_Info.address,
            Users_Info.birthdate,
            Users_Info.gender,
        )
        .order_by(Learners.learner_id.desc())
        .paginate(page=page, per_page=10)
    )
    return render_template("admin/learner.html", learners=learners, title="Learners")


@admin.route("/dashboard/learner/<id>/delete")
@login_required
def delete_learner(id):
    user = Users.query.filter(Users.id == int(id)).first_or_404()
    learner: Learners = Learners.query.filter(
        Learners.learner_id == int(id)
    ).first_or_404()
    db.session.delete(user)

    date, time = add_datetime()

    new_log = LogHistory(current_user.id, "Delete Learner Account", date, time)
    db.session.add(new_log)
    db.session.commit()

    flash("Learner Account Deleted Successfully!", category="warning")
    return redirect(url_for("admin.learner"))


@admin.route("/dashboard/developer")
@login_required
def developer():
    page = request.args.get("page", 1, int)

    developers = (
        Devs.query.join(Users, Devs.dev_id == Users.id)
        .join(Users_Info, Devs.dev_id == Users_Info.i_id)
        .add_columns(
            Users.id,
            Users.username,
            Users.email,
            Users.points,
            Devs.dev_id,
            Users_Info.last_name,
            Users_Info.first_name,
            Users_Info.address,
            Users_Info.birthdate,
            Users_Info.gender,
        )
        .order_by(Devs.dev_id.desc())
        .paginate(page=page, per_page=10)
    )
    return render_template(
        "admin/developer.html", developers=developers, title="Developers"
    )


@admin.route("/dashboard/developer/<id>/delete")
@login_required
def delete_developer(id):
    user = Users.query.filter(Users.id == int(id)).first_or_404()
    developer: Devs = Devs.query.filter(Devs.dev_id == int(id)).first_or_404()
    db.session.delete(user)

    date, time = add_datetime()

    new_log = LogHistory(current_user.id, "Delete Developer Account", date, time)
    db.session.add(new_log)
    db.session.commit()

    flash("Developer Account Deleted Successfully!", category="warning")
    return redirect(url_for("admin.developer"))


@admin.route("/dashboard/histoty")
@login_required
def history():
    page = request.args.get("page", 1, int)

    logs = (
        LogHistory.query.order_by(LogHistory.log_id.desc())
        .join(Users, LogHistory.log_user_id == Users.id)
        .add_columns(
            Users.id,
            Users.username,
            Users.role,
            LogHistory.log_id,
            LogHistory.activity,
            LogHistory.date,
            LogHistory.time,
        )
        .paginate(page=page, per_page=15)
    )

    return render_template("admin/history.html", logs=logs, title="Logs")


@admin.route("/dashboard/manage_feeds")
@login_required
def manage_feeds():
    page = request.args.get("page", 1, int)

    posts = (
        Posts.query.join(Users, Posts.post_user_id == Users.id)
        .join(PostData, Posts.post_id == PostData.post_id)
        .add_columns(
            Users.id,
            Users.username,
            Posts.post_id,
            Posts.post_user_id,
            PostData.post_title,
            PostData.post_body,
            PostData.post_date,
            PostData.post_time,
        )
        .order_by(Posts.post_id.desc())
        .paginate(page=page, per_page=10)
    )
    return render_template("admin/manage_feeds.html", posts=posts, title="Manage Feeds")


@admin.route("/dashboard/manage_feeds/<post_id>/delete")
@login_required
def delete_post(post_id):
    post = Posts.query.filter(Posts.post_id == int(post_id)).first_or_404()
    db.session.delete(post)

    date, time = add_datetime()

    new_log = LogHistory(current_user.id, "Delete Post", date, time)
    db.session.add(new_log)
    db.session.commit()

    flash("Post Deleted Successfully!", category="warning")
    return redirect(url_for("admin.manage_feeds"))


@admin.route("/dashboard/model_list", methods=["GET", "POST"])
@login_required
def model_list():
    page = request.args.get("page", 1, int)
    form = ModelSearchForm()
    find = "no"

    lists = (
        Models.query.join(Users, Models.user_id == Users.id)
        .join(ModelDetails, Models.model_id == ModelDetails.model_id)
        .add_columns(
            Users.id,
            Users.username,
            Models.model_id,
            Models.model_name,
            Models.model_file_type,
            ModelDetails.description,
            ModelDetails.upload_date,
            ModelDetails.upload_time,
        )
        .order_by(Models.model_id.desc())
        .paginate(page=page, per_page=10)
    )

    if form.validate_on_submit():
        if page > 1:
            page = 1
        find = "yes"
        lists = (
            Models.query.join(Users, Models.user_id == Users.id)
            .join(ModelDetails, Models.model_id == ModelDetails.model_id)
            .filter(
                Models.model_name.icontains(form.keyword.data)
                | Models.model_file_type.icontains(form.keyword.data)
            )
            .add_columns(
                Users.id,
                Users.username,
                Models.model_id,
                Models.model_name,
                Models.model_file_type,
                ModelDetails.upload_date,
            )
            .order_by(Models.model_id.desc())
            .paginate(page=page, per_page=25)
        )

    return render_template(
        "admin/model_list.html", form=form, lists=lists, find=find, title="Model Lists"
    )


@admin.route("/dashboard/model_list/<model_id>/delete")
@login_required
def delete_model(model_id):
    model: Models = Models.query.filter(Models.model_id == int(model_id)).first_or_404()
    details: ModelDetails = ModelDetails.query.filter(
        ModelDetails.model_id == model.model_id
    ).first()

    os.remove(
        os.path.join(current_app.root_path, "static/model_file/", details.file_path)
    )

    db.session.delete(model)
    db.session.commit()

    date, time = add_datetime()
    new_log = LogHistory(current_user.id, "Delete Model", date, time)
    db.session.add(new_log)
    db.session.commit()

    flash("Model deleted successfully!", category="warning")
    return redirect(url_for("admin.model_list"))


@admin.route("/dashboard/interaction")
def interaction():
    page = request.args.get("page", 1, int)

    coms = (
        PostComments.query.join(Users, PostComments.com_user_id == Users.id)
        .add_columns(
            Users.id,
            Users.username,
            PostComments.comment_id,
            PostComments.com_user_id,
            PostComments.com_post_id,
            PostComments.comment,
            PostComments.com_date,
            PostComments.com_date,
        )
        .order_by(PostComments.comment_id.desc())
        .paginate(page=page, per_page=10)
    )
    return render_template(
        "admin/interaction.html", coms=coms, title="Manage Interaction"
    )


@admin.route("/dashboard/interaction/delete/comment/<int:com_id>")
@login_required
def delete_comment(com_id):
    comment: PostComments = PostComments.query.filter(
        PostComments.comment_id == com_id
    ).first_or_404()
    db.session.delete(comment)

    date, time = add_datetime()
    new_log = LogHistory(current_user.id, "Delete Comment", date, time)
    db.session.add(new_log)
    db.session.commit()

    flash("Comment deleted successfully!", category="warning")
    return redirect(url_for("admin.interaction"))


@admin.route("/dashboard/settings")
def settings():
    form = UpdateProfileForm()
    pass_form = ChangePasswordForm()
    user: Users_Info = Users_Info.query.filter(
        Users_Info.i_id == current_user.id
    ).first_or_404()

    if request.method == "GET":
        form.firstname.data = user.first_name
        form.lastname.data = user.last_name
        form.gender.data = user.gender
        form.email.data = current_user.email
        form.address.data = user.address
        form.birthdate.data = user.birthdate

    return render_template(
        "admin/settings.html",
        user=user,
        form=form,
        pass_form=pass_form,
        title="setting",
    )


@admin.route("/dashboard/settings/update", methods=["POST"])
@login_required
def admin_profile_handler():
    form = UpdateProfileForm()
    user: Users = Users.query.filter(Users.id == current_user.id).first_or_404()
    info: Users_Info = Users_Info.query.filter(
        Users_Info.i_id == current_user.id
    ).first_or_404()

    if form.validate_on_submit():
        profile_img = ""
        if form.profile_img.data:
            if info.profile_img == "default.png":
                profile_img = save_profile_picture(form.profile_img.data)
            else:
                # Remove old image
                profile_picture_remover(info.profile_img)
                # Store new image
                profile_img = save_profile_picture(form.profile_img.data)

            info.profile_img = profile_img

        info.first_name = form.firstname.data
        info.last_name = form.lastname.data
        info.gender = form.gender.data
        info.birthdate = form.birthdate.data
        info.address = form.address.data

        date, time = add_datetime()
        new_log = LogHistory(current_user.id, "Update Profile", date, time)
        db.session.add(new_log)
        db.session.commit()

        flash("Your account has been updated!", category="success")
        return redirect(url_for("admin.settings"))


@admin.route("/dashboard/setting/change_password", methods=["POST"])
@login_required
def change_password_handler():
    pass_form = ChangePasswordForm()

    if pass_form.validate_on_submit():
        current_pass = pass_form.current_pass.data
        if hash_controller.check_password_hash(
            current_user.password_hash, current_pass
        ):
            new_pass = pass_form.confirm_pass.data
            pass_hash = hash_controller.generate_password_hash(new_pass).decode("utf-8")

            user = Users.query.filter_by(id=current_user.id).first_or_404()
            user.password_hash = pass_hash

            date, time = add_datetime()
            new_log = LogHistory(current_user.id, "Change Password", date, time)
            db.session.add(new_log)
            db.session.commit()

            flash("Your password has been changed!", category="success")
            return redirect(url_for("admin.setting"))
        else:
            flash("Sorry, Your current password did not match!", category="danger")
            return redirect(url_for("admin.setting"))
    else:
        flash("Sorry, Password update fail!", category="danger")
        return redirect(url_for("admin.setting"))
