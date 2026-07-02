import os
import re
from .BaseController import BaseController
from .ProjectController import ProjectController
from fastapi import UploadFile
from models import ResponseSignal
class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1024 * 1024  # Convert MB to Bytes

    def validate_uploaded_file(self,file: UploadFile):

        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        if file.size > self.app_settings.FILE_ALLOWED_SIZE_MB * self.size_scale:
            return False , ResponseSignal.FILE_SIZE_EXCEEDED.value
        return True, ResponseSignal.FILE_VALIDATION_SUCCESS.value
    
    def get_clean_file_name(self, orig_file_name: str):
        # Remove any special characters except . and _ from the file name
        cleaned_name = re.sub(r'[^\w.]', '', orig_file_name.strip())
        cleaned_name = cleaned_name.replace(' ', '_')  # Replace spaces with underscores
        return cleaned_name
    
    def generate_unique_file_path(self, original_file_name: str, project_id: str):

        random_key = self.generate_random_name()
        cleaned_name = self.get_clean_file_name(
            orig_file_name=original_file_name)
        project_dir = ProjectController().get_project_path(project_id=project_id)
        unique_file_path = os.path.join(project_dir, random_key + "_" + cleaned_name)
        # Check if the generated file name already exists in the project directory create a new random key until a unique name is found
        while os.path.exists(unique_file_path):
            random_key = self.generate_random_name(8)
            unique_file_path = os.path.join(project_dir, random_key + "_" + cleaned_name)
        return unique_file_path ,  random_key + "_" + cleaned_name