from helper.config import get_settings, Settings
import random
import string
import os
class BaseController:
    def __init__(self):
        self.app_settings = get_settings()
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.files_dir = os.path.join(self.base_dir, 'assets/files')

        #function to generate random string of length n
    def generate_random_name(self, lenght: int=12) -> str:

        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=lenght))