import os
import shutil
from ..config import get_settings
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def save_user_documents(
    front_content, back_content, front_path, back_path, new_directory
):
    os.makedirs(new_directory)
    with open(front_path, "wb") as front_file:
        front_file.write(front_content)
    with open(back_path, "wb") as back_file:
        back_file.write(back_content)


def delete_directory_user_documents(directory_name):
    base_directory = os.path.join(os.getcwd(), "resources")
    base_directory = os.path.join(base_directory, "certifications_files")
    to_delete_directory = os.path.join(base_directory, directory_name)
    if os.path.exists(to_delete_directory):
        shutil.rmtree(to_delete_directory)


def get_user_document_url(path: str, certification_url: str):
    normalized_path = Path(path).as_posix()
    return f"{get_settings().base_url}{certification_url}{normalized_path}"


def get_path(file_path):
    base_directory = os.path.join(os.getcwd(), "resources")
    base_directory = os.path.join(base_directory, "certifications_files")
    current_path = os.path.join(base_directory, file_path)
    if os.path.exists(current_path):
        return current_path
    else:
        logger.warning(f"File {current_path} not found")
        return None
