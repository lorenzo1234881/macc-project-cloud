import os
from dotenv import load_dotenv

class Config:

    LOCATOR_USER_AGENT = "macc-project"
    UPLOAD_FOLDER = "/home/ll328II/images"
    MAX_CONTENT_LENGTH =  512 * 1000 # 512 kb
    UPLOAD_URL = "https://ll328ii.pythonanywhere.com/images"
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    CLIENT_ID = None
    SECRET_KEY = None
    PASSWORD_DB = None

    def __init__(self):
        project_folder = os.path.expanduser('~/mysite')  # adjust as appropriate
        load_dotenv(os.path.join(project_folder, '.env'))
        self.CLIENT_ID = os.getenv("CLIENT_ID")
        self.SECRET_KEY = os.getenv("SECRET_KEY") or os.urandom(24)
        self.PASSWORD_DB = os.getenv("PASSWORD_DB")
        Config.__instance = self

conf = Config()