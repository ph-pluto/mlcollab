import os
import datetime
import secrets

from flask import current_app, request, jsonify
from datetime import date
from PIL import Image, ImageOps
import joblib
import pickle
import onnx
import matplotlib.pyplot as plt
import netron


def add_datetime():
    """
    Return list [date, time]
    """
    date_now = date.today()
    time_now = datetime.datetime.now().strftime("%H:%M:%S")
    return [date_now, time_now]


def save_profile_picture(form_picture):
    """
    Input: Picture picture image file from user form
    - Convert input picture to 1000x1000
    - Save it with random hex(8) name

    Return: Saved image name
    """
    random_hex = secrets.token_hex(8)

    _, file_extension = os.path.splitext(form_picture.filename)
    picture_file_name = random_hex + file_extension

    picture_path = os.path.join(
        current_app.root_path, "static/profile_imgs", picture_file_name
    )

    output_size = (1000, 1000)
    i = Image.open(form_picture)
    i = ImageOps.exif_transpose(i)
    i.thumbnail(output_size, Image.Resampling.LANCZOS)
    i.save(picture_path)

    return picture_file_name


def profile_picture_remover(picture_name):
    """
    ### Input:
    #### 1. picture_name
            - Pass the current avatar file name if exists
            - Remove the avatar file from the system
    #### 2. user_role
            - Pass the user role with small letters
            - Roles: patient, doctor, manager
    ### Return: None
    """
    os.remove(os.path.join(current_app.root_path, "static/profile_imgs", picture_name))


def save_model_file(user_id, model_type, model_file):
    if not model_file:
        return None

    # Ensure the upload directory exists
    upload_dir = os.path.join(current_app.root_path, "uploads", "models")
    os.makedirs(upload_dir, exist_ok=True)

    # Save the file to the upload directory
    filename = model_file.filename
    file_path = os.path.join(upload_dir, filename)
    model_file.save(file_path)

    # Return the URL of the saved file
    file_url = f"/uploads/models/{filename}"  # Example URL, adjust as needed
    return file_url


def upload_file():

    UPLOAD_FOLDER = "uploads"

    if "file" not in request.files:
        return jsonify({"error": "No file part"})
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"})
    if file:
        filename = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filename)
        # Save file metadata in database
        # Insert code here
        return jsonify({"message": "File uploaded successfully"})


def file_uploader(filedata):
    _, file_extension = os.path.splitext(filedata.filename)
    random_hex = secrets.token_hex(20)
    file_path_name = random_hex + file_extension

    file_path = os.path.join(
        current_app.root_path, "static/model_file/", file_path_name
    )
    filedata.save(file_path)

    return file_path_name


def support_file_uploader(filedata):
    _, file_extension = os.path.splitext(filedata.filename)
    random_hex = secrets.token_hex(20)
    file_path_name = random_hex + file_extension

    file_path = os.path.join(
        current_app.root_path, "static/support_files/", file_path_name
    )
    filedata.save(file_path)

    return file_path_name


def load_joblib_model(file_path):
    with open(file_path, "rb") as file:
        model = joblib.load(file)

    return model

def load_pkl_model(file_path):
    with open(file_path, "rb") as file:
        model = pickle.load(file)

    return model

def load_onnx_model(file_path):
    with open(file_path, "rb") as file:
        model = onnx.load(file)

    return model


def fi_fig_draw_joblib(model_id, model, fig_folder) -> str:
    # Generate a plot of feature importances if applicable
    if hasattr(model, "feature_importances_"):
        fig, axix = plt.subplots()
        axix.plot(
            range(len(model.feature_importances_)),
            model.feature_importances_,
        )
        axix.set_xlabel("Features")
        axix.set_ylabel("Importance")
        axix.set_title("Feature Importances")

        fig_path = os.path.join(fig_folder, f"feature_importance_{model_id}.png")

        fig.savefig(fig_path)
        plt.close(fig)

        return "done"
    else:
        return "fail"


def start_netron_server(model_path, port):
    netron.start(model_path, address=("0.0.0.0", port), browse=False)


