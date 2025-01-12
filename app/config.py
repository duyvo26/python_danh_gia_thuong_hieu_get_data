# File cấu hình chung cho ứng dụng

import os
from dotenv import load_dotenv

# Load các biến môi trường từ file .env
load_dotenv()


class Settings:
    # SETTING
    DIR_ROOT = os.path.dirname(os.path.abspath(".env"))

    HOST = os.environ["HOST"]
    DATABASE = os.environ["DATABASE"]
    USER = os.environ["USER"]
    PASSWORD = os.environ["PASSWORD"]

    SERIAL_PORT = os.environ["SERIAL_PORT"]
    
    BRAND_SIMILARITY_PERCENTAGE = os.environ["BRAND_SIMILARITY_PERCENTAGE"]

settings = Settings()
