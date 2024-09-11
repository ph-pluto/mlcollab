import os
import threading
import netron
from mlcollab import netron_servers
from flask import (
    Blueprint,
    redirect,
    render_template,
    url_for,
    flash,
    request,
    current_app,
    send_file,
)
from flask_login import login_user, logout_user, current_user, login_required
from mlcollab.public.forms import (
    LoginForm,
    RegisterForm,
    UpdateProfileForm,
    ChangePasswordForm,
    UploadModelForm,
    EditModelForm,
    PostForm,
    CommentForm,
    ModelFilesForm,
    ModelSearchForm,
    FeedSearchForm,
)
from mlcollab.users.models import (
    Users,
    Users_Info,
    Learners,
    LogHistory,
    Models,
    ModelFiles,
    ModelDetails,
    Posts,
    PostData,
    PostComments,
)
from mlcollab import db, hash_controller
from mlcollab.public.utils import (
    add_datetime,
    save_profile_picture,
    profile_picture_remover,
    file_uploader,
    support_file_uploader,
    load_joblib_model,
    load_pkl_model,
    load_onnx_model,
    fi_fig_draw_joblib,
    start_netron_server,
)

import matplotlib
matplotlib.use("agg")
import onnxruntime
import plotly.graph_objs as go
from plotly.offline import plot


public = Blueprint(name="public", import_name=__name__)


@public.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('public.dashboard'))

    return render_template("public/index.html")


@public.route("/home")
def home():
    return render_template("public/home.html")


@public.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        firstname = form.firstname.data
        lastname = form.lastname.data
        gender = form.gender.data

        pass_hash = hash_controller.generate_password_hash(password).decode("utf-8")

        new_user = Users(
            username=username, pass_hash=pass_hash, email=email, role="Learner"
        )
        db.session.add(new_user)
        db.session.commit()

        new_info = Users_Info(new_user.id, firstname, lastname, gender)
        db.session.add(new_info)

        new_learner = Learners(new_user.id)
        db.session.add(new_learner)

        date, time = add_datetime()
        new_log = LogHistory(new_user.id, "Registration", date, time)
        db.session.add(new_log)
        # Commit to database
        db.session.commit()

        flash("Register Successfully!", category="success")
        return redirect(url_for("public.login"))

    return render_template("public/register.html", form=form, title="Register")


@public.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data

        user: Users = Users.query.filter_by(username=username).first()
        if user and hash_controller.check_password_hash(user.password_hash, password):
            login_user(user, remember)

            date, time = add_datetime()
            new_log = LogHistory(current_user.id, "Login", date, time)
            db.session.add(new_log)
            db.session.commit()

            flash("Login Succesfully!", category="success")
            return redirect(url_for("public.dashboard"))
        else:
            flash("Username or Password Wrong!", category="danger")
            return redirect(url_for("public.login"))

    return render_template("public/login.html", form=form, title="Log In")


@public.route("/logout")
def logout():
    date, time = add_datetime()
    new_log = LogHistory(current_user.id, "Logout", date, time)
    db.session.add(new_log)
    db.session.commit()
    logout_user()

    flash("Log out Successfully!", category="info")
    return redirect(url_for("public.index"))


@public.route("/error")
def error():
    return render_template("public/error.html")


@public.route("/profile")
@login_required
def profile():
    user: Users_Info = Users_Info.query.filter(
        Users_Info.i_id == current_user.id
    ).first_or_404()

    return render_template(
        "public/profile.html", user=user, title=f"{current_user.username}'s Profile"
    )


@public.route("/profile/update", methods=["POST"])
@login_required
def update_profile_handler():
    form = UpdateProfileForm()
    info: Users_Info = Users_Info.query.filter(
        Users_Info.i_id == current_user.id
    ).first_or_404()

    if request.method == "POST":
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
        return redirect(url_for("public.setting"))


@public.route("/dashboard/setting")
@login_required
def setting():
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
        "public/setting.html",
        user=user,
        form=form,
        pass_form=pass_form,
        title="setting",
    )


@public.route("/dashboard/setting/change_password", methods=["POST"])
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
            return redirect(url_for("public.setting"))
        else:
            flash("Sorry, Your current password did not match!", category="danger")
            return redirect(url_for("public.setting"))
    else:
        flash("Sorry, Password update fail!", category="danger")
        return redirect(url_for("public.setting"))


@public.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "Admin":
        return redirect(url_for("admin.dashboard"))
    else:
        return redirect(url_for("public.user_dashboard"))


@public.route("/dashboard/user")
@login_required
def user_dashboard():
    return render_template("public/dashboard.html")


@public.route("/dashboard/feeds", methods=["GET", "POST"])
@login_required
def feeds():
    page = request.args.get("page", 1, int)
    form = FeedSearchForm()
    find = "no"

    posts = (
        Posts.query.join(PostData, PostData.post_id == Posts.post_id)
        .join(Users, Users.id == Posts.post_user_id)
        .join(Users_Info, Users_Info.i_id == Posts.post_user_id)
        .add_columns(
            Users_Info.last_name,
            Users_Info.first_name,
            Users_Info.profile_img,
            Users.role,
            Posts.post_id,
            PostData.post_title,
            PostData.post_date,
            PostData.post_time,
        )
        .order_by(PostData.post_id.desc())
        .paginate(page=page, per_page=6)
    )

    if form.validate_on_submit():
        if page > 1:
            page = 1
        find = "yes"
        posts = (
            Posts.query.join(PostData, PostData.post_id == Posts.post_id)
            .filter(PostData.post_title.icontains(form.keyword.data))
            .join(Users, Users.id == Posts.post_user_id)
            .join(Users_Info, Users_Info.i_id == Posts.post_user_id)
            .add_columns(
                Users_Info.last_name,
                Users_Info.first_name,
                Users_Info.profile_img,
                Users.role,
                Posts.post_id,
                PostData.post_title,
                PostData.post_date,
                PostData.post_time,
            )
            .order_by(PostData.post_id.desc())
            .paginate(page=page, per_page=20)
        )

    return render_template(
        "public/feeds.html", posts=posts, find=find, form=form, title="Community Feeds"
    )


@public.route("/feeds/view_post/<post_id>")
@login_required
def view_post_page(post_id):
    form = CommentForm()

    post = (
        PostData.query.filter(PostData.post_id == int(post_id))
        .join(Posts, Posts.post_id == PostData.post_id)
        .join(Users_Info, Users_Info.i_id == Posts.post_user_id)
        .add_columns(
            Posts.post_id,
            Posts.post_user_id,
            PostData.post_title,
            PostData.post_body,
            PostData.post_date,
            PostData.post_time,
            Users_Info.last_name,
            Users_Info.first_name,
        )
        .first_or_404()
    )

    comments = (
        PostComments.query.filter(PostComments.com_post_id == int(post_id))
        .join(Users_Info, Users_Info.i_id == PostComments.com_user_id)
        .add_columns(
            PostComments.comment_id,
            PostComments.com_user_id,
            PostComments.comment,
            PostComments.com_date,
            PostComments.com_time,
            Users_Info.last_name,
            Users_Info.first_name,
        )
        .all()
    )

    return render_template(
        "public/view_post_page.html",
        form=form,
        post=post,
        comments=comments,
        title=f"{ post.post_title }",
    )


@public.route("/posts/<int:post_id>/comment", methods=["POST"])
def post_comment(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        user: Users = Users.query.filter(Users.id == current_user.id).first_or_404()
        date, time = add_datetime()
        new_comment = PostComments(
            post_id=post_id,
            user_id=current_user.id,
            comment=form.body.data,
            com_date=date,
            com_time=time,
        )
        db.session.add(new_comment)
        db.session.commit()

        date, time = add_datetime()
        new_log = LogHistory(current_user.id, "New Comment", date, time)
        db.session.add(new_log)

        user.points = user.points + 2
        db.session.commit()

        flash("Your comment has been posted!", category="success")
        return redirect(url_for("public.view_post_page", post_id=post_id))


@public.route("/dashboard/feeds/posts/<int:post_id>/delete/comment/<int:com_id>")
@login_required
def delete_comment(post_id, com_id):
    comment: PostComments = PostComments.query.filter(
        PostComments.comment_id == com_id
    ).first_or_404()

    if comment.com_user_id == current_user.id:
        db.session.delete(comment)
    else:
        flash("Permission denied!", category="danger")
        return redirect(url_for("public.view_post_page", post_id=post_id))

    date, time = add_datetime()
    new_log = LogHistory(current_user.id, "Delete Comment", date, time)
    db.session.add(new_log)
    db.session.commit()

    flash("Comment deleted successfully!", category="warning")
    return redirect(url_for("public.view_post_page", post_id=post_id))


@public.route("/dashboard/models")
@login_required
def models():
    return render_template("public/models.html")


@public.route("/dashboard/models/upload", methods=["GET", "POST"])
@login_required
def upload():
    form = UploadModelForm()
    if form.validate_on_submit():
        user: Users = Users.query.filter(Users.id == current_user.id).first_or_404()
        model_file_type = form.model_file_type.data
        file = form.file.data
        model_name = form.model_name.data
        description = form.description.data
        file_path = ""

        if file:
            file_path = file_uploader(filedata=file)

        new_model = Models(current_user.id, model_name, model_file_type)
        db.session.add(new_model)
        db.session.commit()

        date, time = add_datetime()
        new_detail = ModelDetails(
            new_model.model_id, description, file_path, date, time
        )
        db.session.add(new_detail)

        user.points = user.points + 30
        db.session.commit()

        date, time = add_datetime()
        new_log = LogHistory(current_user.id, "Upload Model", date, time)
        db.session.add(new_log)
        db.session.commit()

        flash("Upload Model Success!", category="success")
        return redirect(url_for("public.upload"))

    elif request.method == "POST":
        flash("Upload File Fail!", category="danger")
        return redirect(url_for("public.upload"))

    return render_template("public/upload.html", form=form, title="upload")


@public.route("/dashboard/models/view_model")
@login_required
def view_model():
    page = request.args.get("page", 1, int)
    form = EditModelForm()

    details = (
        Models.query.filter(Models.user_id == current_user.id)
        .join(Users, Models.user_id == Users.id)
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
        .paginate(page=page, per_page=6)
    )

    return render_template(
        "public/view_model.html", form=form, details=details, title="Details"
    )


@public.route("/dashboard/models/<model_id>")
@login_required
def model_view_page(model_id):
    model: Models = Models.query.filter(Models.model_id == int(model_id)).first_or_404()
    details: ModelDetails = ModelDetails.query.filter(
        ModelDetails.model_id == model.model_id
    ).first()
    files: ModelFiles = ModelFiles.query.filter(
        ModelFiles.file_model_id == int(model_id)
    ).all()

    upload_form = ModelFilesForm()

    return render_template(
        "public/model_view_page.html",
        upload_form=upload_form,
        model=model,
        details=details,
        files=files,
        title=f"{model.model_name}",
    )


@public.route("/dashboard/models/<model_id>/upload/files", methods=["POST"])
@login_required
def model_file_upload_handler(model_id):
    upload_form = ModelFilesForm()

    if upload_form.validate_on_submit():
        file_name = upload_form.file_name.data
        file_path = support_file_uploader(upload_form.file.data)

        date, time = add_datetime()
        new_model_file = ModelFiles(int(model_id), file_path, file_name, date, time)
        db.session.add(new_model_file)

        new_log = LogHistory(current_user.id, "Upload Support File", date, time)
        new_log.details = f"Model #{model_id}, Support file: {file_name}"
        db.session.add(new_log)

        db.session.commit()

        flash(f"{file_name} uploaded successfully!", category="success")
        return redirect(url_for("public.model_view_page", model_id=model_id))

    else:
        flash("Upload file failed!", category="danger")
        return redirect(url_for("public.model_view_page", model_id=model_id))


@public.route("/dashboard/models/<int:model_id>/delete/files/<int:file_id>")
@login_required
def delete_file(model_id, file_id):
    file: ModelFiles = ModelFiles.query.filter(
        ModelFiles.file_id == file_id
    ).first_or_404()

    os.remove(
        os.path.join(current_app.root_path, "static/support_files/", file.file_path)
    )

    db.session.delete(file)

    date, time = add_datetime()
    new_log = LogHistory(current_user.id, "Delete File", date, time)
    db.session.add(new_log)
    db.session.commit()

    flash("File deleted successfully!", category="warning")
    return redirect(url_for("public.model_view_page", model_id=model_id))


@public.route("/dashboard/models/view_model/model/<model_id>", methods=["GET", "POST"])
@login_required
def model_update(model_id):
    model: Models = Models.query.filter(Models.model_id == int(model_id)).first_or_404()
    model_detail: ModelDetails = ModelDetails.query.filter(
        ModelDetails.model_id == model.model_id
    ).first()
    edit_form = EditModelForm()

    if edit_form.validate_on_submit():
        model.model_name = edit_form.model_name.data
        model.model_file_type = edit_form.model_file_type.data
        model_detail.description = edit_form.description.data

        db.session.commit()

        date, time = add_datetime()
        new_log = LogHistory(current_user.id, "Update Model", date, time)
        db.session.add(new_log)
        db.session.commit()

        flash("Model updated successfully!", category="success")
        return redirect(url_for("public.model_view_page", model_id=model_id))

    elif request.method == "GET":
        edit_form.model_name.data = model.model_name
        edit_form.model_file_type.data = model.model_file_type
        edit_form.description.data = model_detail.description

    return render_template(
        "public/model_update.html",
        edit_form=edit_form,
        model=model,
        title=f"{model.model_name}",
    )


@public.route("/dashboard/models/view_model/model/<model_id>/delete")
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
    return redirect(url_for("public.view_model"))


@public.route("/dashboard/models/post")
@login_required
def post():
    return render_template("public/post.html")


@public.route("/dashboard/models/add_post", methods=["GET", "POST"])
@login_required
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        user: Users = Users.query.filter(Users.id == current_user.id).first_or_404()
        date, time = add_datetime()

        new_post: Posts = Posts(current_user.id)
        db.session.add(new_post)
        db.session.commit()

        new_post_data = PostData(
            new_post.post_id, form.title.data, form.body.data, date, time
        )
        db.session.add(new_post_data)

        new_log = LogHistory(current_user.id, "New Post", date, time)
        new_log.details = f"Post #{new_post.post_id}: {new_post_data.post_title}"

        user.points = user.points + 10
        db.session.commit()

        flash("New post successfully!", category="success")
        return redirect(url_for("public.add_post"))

    return render_template("public/add_post.html", form=form, title="Write new post")


@public.route("/dashboard/models/model_catalog", methods=["GET", "POST"])
@login_required
def model_catalog():
    page = request.args.get("page", 1, int)
    form = ModelSearchForm()
    find = "no"

    catalogs = (
        Models.query.join(Users, Models.user_id == Users.id)
        .join(ModelDetails, Models.model_id == ModelDetails.model_id)
        .add_columns(
            Users.id,
            Users.username,
            Models.model_id,
            Models.model_name,
            Models.model_file_type,
            ModelDetails.upload_date,
        )
        .order_by(Models.model_id.desc())
        .paginate(page=page, per_page=20)
    )

    if form.validate_on_submit():
        if page > 1:
            page = 1
        find = "yes"
        catalogs = (
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
        "public/model_catalog.html",
        form=form,
        catalogs=catalogs,
        find=find,
        title="Model Catalog",
    )


@public.route("/dashboard/models/model_catalog/<model_id>")
@login_required
def model_details(model_id):
    model: Models = Models.query.filter(Models.model_id == int(model_id)).first_or_404()
    model_detail: ModelDetails = ModelDetails.query.filter(
        ModelDetails.model_id == model.model_id
    ).first()

    files: ModelFiles = ModelFiles.query.filter(
        ModelFiles.file_model_id == int(model_id)
    ).all()

    return render_template(
        "public/model_details.html",
        model=model,
        model_detail=model_detail,
        files=files,
        title=f"{ model.model_name } Details",
    )


@public.route("/dashboard/models/<model_id>/download/file")
@login_required
def download_model_file(model_id):
    model: Models = Models.query.filter(Models.model_id == int(model_id)).first_or_404()
    detail: ModelDetails = ModelDetails.query.filter(
        ModelDetails.model_id == int(model_id)
    ).first_or_404()

    return send_file(
        os.path.join(
            current_app.root_path,
            "static/model_file/",
            detail.file_path,
        ),
        download_name=f"{model.model_name}_{detail.file_path}",
        as_attachment=True,
    )


@public.route("/dashboard/models/download/support_file/<file_id>")
@login_required
def download_model_support_file(file_id):
    file: ModelFiles = ModelFiles.query.filter(
        ModelFiles.file_id == int(file_id)
    ).first_or_404()

    return send_file(
        os.path.join(
            current_app.root_path,
            "static/support_files/",
            file.file_path,
        ),
        download_name=f"{file.file_name}_{file.file_path}",
        as_attachment=True,
    )


@public.route("/dashboard/models/model_visualization")
@login_required
def model_visualization():
    return render_template("public/model_visualization.html")


@public.route("/dashboard/models/model_visualize/<type>/<model_id>")
@login_required
def model_visualize(type, model_id):
    if type == "joblib":
        return redirect(url_for("public.model_visualize_joblib", model_id=model_id))

    elif type == "pkl":
        return redirect(url_for("public.model_visualize_pkl", model_id=model_id))

    elif type == "pb":
        return redirect(url_for("public.model_visualize_pb", model_id=model_id))

    elif type == "onnx":
        return redirect(url_for("public.model_visualize_onnx", model_id=model_id))


@public.route("/dashboard/models/model_visualize/joblib/<model_id>")
def model_visualize_joblib(model_id):
    model: Models = Models.query.filter(Models.model_id == int(model_id)).first_or_404()
    details: ModelDetails = ModelDetails.query.filter_by(model_id=model_id).first()

    # Define paths
    fi_plots_path = os.path.join(current_app.static_folder, "fi_plots_joblib")
    fi_fig_path = os.path.join(fi_plots_path, f"feature_importance_{model_id}.png")
    model_path = os.path.join(
        current_app.static_folder, "model_file", details.file_path
    )

    load_model = load_joblib_model(model_path)
    # Get model information
    params = load_model.get_params() if hasattr(load_model, "get_params") else "fail"

    if not os.path.exists(fi_fig_path):
        draw_fig_img = fi_fig_draw_joblib(model.model_id, load_model, fi_plots_path)
        if draw_fig_img == "fail":
            fi_fig_img = "fail"
        else:
            fi_fig_img = url_for(
                "static", filename=f"fi_plots_joblib/feature_importance_{model_id}.png"
            )
    else:
        fi_fig_img = url_for(
            "static", filename=f"fi_plots_joblib/feature_importance_{model_id}.png"
        )

    return render_template(
        "public/model_visualize_joblib.html",
        model=model,
        fi_fig=fi_fig_img,
        summary=str(load_model),
        params=params,
        title="(joblib) Model Analysis",
    )

@public.route("/dashboard/models/model_visualize/pkl/<model_id>")
def model_visualize_pkl(model_id):
    model: Models = Models.query.filter(Models.model_id == int(model_id)).first_or_404()
    details: ModelDetails = ModelDetails.query.filter_by(model_id=model_id).first()

    # Define paths
    fi_plots_path = os.path.join(current_app.static_folder, "fi_plots_pkl")
    fi_fig_path = os.path.join(fi_plots_path, f"feature_importance_{model_id}.png")
    model_path = os.path.join(
        current_app.static_folder, "model_file", details.file_path
    )

    load_model = load_pkl_model(model_path)
    # Get model information
    params = load_model.get_params() if hasattr(load_model, "get_params") else "fail"

    if not os.path.exists(fi_fig_path):
        draw_fig_img = fi_fig_draw_joblib(model.model_id, load_model, fi_plots_path)
        if draw_fig_img == "fail":
            fi_fig_img = "fail"
        else:
            fi_fig_img = url_for(
                "static", filename=f"fi_plots_pkl/feature_importance_{model_id}.png"
            )
    else:
        fi_fig_img = url_for(
            "static", filename=f"fi_plots_pkl/feature_importance_{model_id}.png"
        )

    return render_template(
        "public/model_visualize_pkl.html",
        model=model,
        fi_fig=fi_fig_img,
        summary=str(load_model),
        params=params,
        title="(pkl) Model Analysis",
    )


@public.route("/dashboard/models/model_visualize/onnx/<model_id>")
@login_required
def model_visualize_onnx(model_id):
    model: Models = Models.query.filter(Models.model_id == int(model_id)).first_or_404()
    details: ModelDetails = ModelDetails.query.filter_by(model_id=model_id).first()

    model_path = os.path.join(
        current_app.static_folder, "model_file", details.file_path
    )

    load_model = load_onnx_model(model_path)
    info = get_onnx_model_details(load_model)
    session = onnxruntime.InferenceSession(load_model.SerializeToString())

    return render_template(
        "public/model_visualize_onnx.html",
        model=model,
        details=details,
        info=info,
        title="(onnx) Model Analysis",
    )


def generate_io_plot(io_details, title):
    names = [io["name"] for io in io_details]
    shapes = [len(io["shape"]) for io in io_details]

    fig = go.Figure(
        data=[go.Bar(x=names, y=shapes)],
        layout=go.Layout(
            title=title,
            xaxis={"title": "Tensor Name"},
            yaxis={"title": "Shape Dimension"},
        ),
    )
    return plot(fig, output_type="div")


def get_onnx_model_details(model):
    inputs = get_io_details(model.graph.input)
    outputs = get_io_details(model.graph.output)

    input_plot = generate_io_plot(inputs, "Input Tensors")
    output_plot = generate_io_plot(outputs, "Output Tensors")

    details = {
        "type": "onnx",
        "inputs": inputs,
        "outputs": outputs,
        "nodes": get_node_summary(model.graph.node),
        "input_plot": input_plot,
        "output_plot": output_plot,
    }
    return details

def get_io_details(io_tensors):
    io_details = []
    for tensor in io_tensors:
        io_details.append(
            {
                "name": tensor.name,
                "shape": [dim.dim_value for dim in tensor.type.tensor_type.shape.dim],
            }
        )
    return io_details


def get_node_summary(nodes):
    node_summary = []
    for node in nodes:
        node_summary.append(
            {
                "name": node.name,
                "op_type": node.op_type,
                "input": node.input,
                "output": node.output,
            }
        )
    return node_summary


@public.route("/netron/view_model/<model_id>", methods=["GET"])
@login_required
def view_onnx_netron(model_id):
    details: ModelDetails = ModelDetails.query.filter(
        ModelDetails.model_id == int(model_id)
    ).first_or_404()
    model_path = os.path.join(
        current_app.static_folder, "model_file", details.file_path
    )

    if model_id in netron_servers:
        port = netron_servers[model_id]["port"]
    else:
        port = 8080 + len(netron_servers)
        netron_servers[model_id] = {"port": port, "thread": None}

        netron_thread = threading.Thread(
            target=start_netron_server, args=(model_path, port)
        )
        netron_thread.start()
        netron_servers[model_id]["thread"] = netron_thread

    return redirect(f"http://localhost:{port}")


@public.route("/close_netron_server", methods=["GET", "POST"])
@login_required
def close_netron_server():
    data = request.get_json()
    model_id = data.get("model_id")

    if model_id in netron_servers:
        netron.stop()
        del netron_servers[model_id]
        return {"message": "Netron server stopped"}, 200
    else:
        return {"message": "Netron server not found"}, 404



@public.route("/dashboard/activities")
@login_required
def activities():
    page = request.args.get("page", 1, int)

    logs = (
        LogHistory.query.filter(LogHistory.log_user_id == current_user.id)
        .order_by(LogHistory.log_id.desc())
        .join(Users, LogHistory.log_user_id == Users.id)
        .add_columns(
            Users.id,
            Users.username,
            LogHistory.log_id,
            LogHistory.activity,
            LogHistory.date,
            LogHistory.time,
        )
        .paginate(page=page, per_page=10)
    )

    return render_template("public/activities.html", logs=logs, title="Logs")
