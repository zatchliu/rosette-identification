from __future__ import annotations

import os
from pathlib import Path
from typing import List

from flask import Flask, request, url_for, send_from_directory, render_template
from markupsafe import Markup
from werkzeug.utils import secure_filename

from image import Image

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "tif", "tiff", "bmp"}
PROJECT_ROOT = Path(__file__).resolve().parent.parent
UPLOAD_DIR = PROJECT_ROOT / "uploads"

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024  # 32 MB
app.config["UPLOAD_FOLDER"] = str(UPLOAD_DIR)


class ImageInput:
    def __init__(self):
        """
        Initialize ImageInput.

        Args:
            None

        Returns:
            None
        """
        pass

    def _allowed_file(self, filename: str) -> bool:
        """
        Check allowed image extension.

        Args:
            filename (str): Filename to validate.

        Returns:
            bool: True if allowed, else False.
        """
        return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

    def _ensure_upload_dir(self) -> None:
        """
        Ensure upload directory exists.

        Returns:
            None
        """
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    def get_image_lone(self, image_path: str) -> Image:
        """
        Wrap a path in an Image.

        Args:
            image_path (str): Filesystem path.

        Returns:
            Image: Wrapped image.
        """
        return Image(image_path)

    def get_image_directory(self, dir_path: str) -> List[Image]:
        """
        Return list of Images from a directory.

        Args:
            dir_path (str): Directory path.

        Returns:
            list[Image]: Images found.
        """
        return []

    def process_image(self, image: Image, noise: float, contrast: float) -> None:
        """
        Placeholder for Step 2 preprocessing.

        Args:
            image (Image): Image object.
            noise (float): Noise reduction level.
            contrast (float): Contrast factor.

        Returns:
            None
        """
        image.contrast(contrast)
        image.noise(noise)

    def save_filestorage(self, file_storage) -> Image:
        """
        Save an uploaded file and return an Image.

        Args:
            file_storage: Werkzeug FileStorage.

        Returns:
            Image: Wrapped saved image.

        Raises:
            ValueError: If unsupported/missing type.
        """
        self._ensure_upload_dir()
        filename = secure_filename(file_storage.filename or "")
        if not filename or not self._allowed_file(filename):
            raise ValueError("Unsupported or missing file type.")

        save_path = UPLOAD_DIR / filename
        file_storage.save(save_path)
        return Image.from_path(str(save_path))


@app.route("/uploads/<path:filename>", methods=["GET"])
def uploaded_file(filename: str):
    """
    Serve an uploaded file by filename.

    Args:
        filename (str): Saved filename.

    Returns:
        Response: File response.
    """
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/", methods=["GET"])
def index():
    """
    Render upload form.

    Returns:
        str: Upload page HTML.
    """
    return render_template("upload.html")


@app.route("/upload", methods=["POST"])
def upload():
    """
    Handle upload and render preview.

    Returns:
        str: Result page HTML.
    """
    img_input = ImageInput()
    if "file" not in request.files:
        return "No file part in request.", 400

    file = request.files["file"]
    if file.filename == "":
        return "No file selected.", 400

    try:
        image_obj = img_input.save_filestorage(file)
        filename = os.path.basename(image_obj.img_path)
        preview_url = url_for("uploaded_file", filename=filename)
        return render_template("result.html", filename=filename, preview_url=preview_url)
    except ValueError as exc:
        return f"Upload error: {Markup.escape(str(exc))}", 400
    except Exception:
        return "Unexpected server error during upload.", 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
