from mlcollab import db
from flask_login import UserMixin


class Users(db.Model, UserMixin):
    """
    #### Users has 3 types of role:
        - Learners
        - Devs
        - Admin

    Default -> Learner
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(45), nullable=True)
    password_hash = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(45), nullable=False)
    role = db.Column(db.String(45), nullable=False)
    points = db.Column(db.Integer, nullable=False)

    def __init__(self, username, pass_hash, email, role="Learner"):
        super().__init__()
        self.username = username
        self.password_hash = pass_hash
        self.email = email
        self.role = role
        self.points = 10

    def get_id(self):
        return self.id

    def __str__(self) -> str:
        return f"User({self.id}): {self.username}/{self.role}"


class Users_Info(db.Model):
    __tablename__ = "users_info"

    i_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), primary_key=True, nullable=False
    )
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    birthdate = db.Column(db.Date, nullable=True)
    address = db.Column(db.String(255), nullable=True)
    profile_img = db.Column(db.String(100), nullable=True)

    def __init__(self, i_id, first_name, last_name, gender):
        super().__init__()
        self.i_id = i_id
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.profile_img = "default.png"


class Learners(db.Model):
    __tablename__ = "learners"

    learner_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), primary_key=True, nullable=False
    )

    def __init__(self, learner_id):
        super().__init__()
        self.learner_id = learner_id


class Devs(db.Model):
    __tablename__ = "devs"

    dev_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), primary_key=True, nullable=False
    )

    def __init__(self, dev_id):
        super().__init__()
        self.dev_id = dev_id


class Admins(db.Model):
    __tablename__ = "admins"

    admin_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), primary_key=True, nullable=False
    )

    def __init__(self, admin_id):
        super().__init__()
        self.admin_id = admin_id


class LogHistory(db.Model):
    __tablename__ = "log_history"

    log_id = db.Column(db.Integer, primary_key=True, nullable=False)
    log_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    activity = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    details = db.Column(db.String(255), nullable=True)

    def __init__(self, log_user_id, activity, date, time):
        super().__init__()
        self.log_user_id = log_user_id
        self.activity = activity
        self.date = date
        self.time = time

    def __str__(self) -> str:
        return f"Log of #({self.log_user_id}): {self.activity} {self.date}"


class Models(db.Model):
    __tablename__ = "models"

    model_id = db.Column(
        db.Integer, primary_key=True, autoincrement=True, nullable=False
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), primary_key=True, nullable=False
    )
    model_name = db.Column(db.String(100), nullable=False)
    model_file_type = db.Column(db.String(100), nullable=False)

    def __init__(self, user_id, model_name, model_file_type):
        super().__init__()
        self.user_id = user_id
        self.model_name = model_name
        self.model_file_type = model_file_type


class ModelDetails(db.Model):
    __tablename__ = "model_details"

    model_id = db.Column(
        db.Integer, db.ForeignKey("models.model_id"), primary_key=True, nullable=False
    )
    description = db.Column(db.Text, nullable=True)
    upload_date = db.Column(db.Date, nullable=False)
    upload_time = db.Column(db.Time, nullable=False)
    file_path = db.Column(db.String(255), nullable=True)

    def __init__(self, model_id, description, file_path, upload_date, upload_time):
        super().__init__()
        self.model_id = model_id
        self.upload_date = upload_date
        self.upload_time = upload_time
        self.description = description
        self.file_path = file_path


class ModelFiles(db.Model):
    __tablename__ = "model_files"

    file_id = db.Column(
        db.Integer, primary_key=True, autoincrement=True, nullable=False
    )
    file_model_id = db.Column(
        db.Integer, db.ForeignKey("models.model_id"), primary_key=True, nullable=False
    )
    file_path = db.Column(db.String(255), nullable=True)
    file_name = db.Column(db.String(255), nullable=True)
    upload_date = db.Column(db.Date, nullable=False)
    upload_time = db.Column(db.Time, nullable=False)

    def __init__(self, file_model_id, file_path, file_name, upload_date, upload_time):
        super().__init__()
        self.file_model_id = file_model_id
        self.file_path = file_path
        self.file_name = file_name
        self.upload_date = upload_date
        self.upload_time = upload_time


class Posts(db.Model):
    __tablename__ = "posts"

    post_id = db.Column(
        db.Integer, primary_key=True, autoincrement=True, nullable=False
    )
    post_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), primary_key=True, nullable=False
    )

    def __init__(self, post_user_id):
        super().__init__()
        self.post_user_id = post_user_id


class PostData(db.Model):
    __tablename__ = "post_data"

    post_id = db.Column(
        db.Integer, db.ForeignKey("posts.post_id"), primary_key=True, nullable=False
    )
    post_title = db.Column(db.String(255), nullable=False)
    post_body = db.Column(db.Text, nullable=False)
    post_date = db.Column(db.Date, nullable=False)
    post_time = db.Column(db.Time, nullable=False)

    def __init__(self, post_id, post_title, post_body, post_date, post_time):
        super().__init__()
        self.post_id = post_id
        self.post_title = post_title
        self.post_body = post_body
        self.post_date = post_date
        self.post_time = post_time


class PostComments(db.Model):
    __tablename__ = "post_comments"

    comment_id = db.Column(
    db.Integer, primary_key=True, autoincrement=True, nullable=False
    )
    com_post_id = db.Column(
        db.Integer, db.ForeignKey("posts.post_id"), primary_key=True, nullable=False
    )
    com_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), primary_key=True, nullable=False
    )
    comment = db.Column(db.Text, nullable=False)
    com_date = db.Column(db.Date, nullable=False)
    com_time = db.Column(db.Time, nullable=False)

    def __init__(self, post_id, user_id, comment, com_date, com_time):
        super().__init__()
        self.com_post_id = post_id
        self.com_user_id = user_id
        self.comment = comment
        self.com_date = com_date
        self.com_time = com_time

