import os
from dotenv import load_dotenv
load_dotenv()

TORTOISE_CONFIG = {
    "connections": {
        "default": os.getenv("DATABASE_URL")
    },
    "apps": {
        "cvbot": {
            "models": ["src.models.db", "aerich.models"],
            "default_connection": "default"
        }
    }
}