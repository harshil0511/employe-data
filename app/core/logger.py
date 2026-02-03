import datetime
from pymongo import MongoClient
from app.core.config import settings

class MongoDBLogger:
    def __init__(self):
        try:
            self.client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=2000)
            self.db = self.client[settings.MONGODB_DB]
            self.collection = self.db["logs"]
            # Test connection
            self.client.server_info()
            self.enabled = True
        except Exception as e:
            print(f"Warning: MongoDB logging disabled. Error connecting to MongoDB: {e}")
            self.enabled = False

    def log(self, level, message, details=None):
        if not self.enabled:
            print(f"[{level}] {message} - {details}")
            return

        log_entry = {
            "timestamp": datetime.datetime.utcnow(),
            "level": level,
            "message": message,
            "details": details or {}
        }
        try:
            self.collection.insert_one(log_entry)
        except Exception as e:
            print(f"Error writing log to MongoDB: {e}")

    def info(self, message, details=None):
        self.log("INFO", message, details)

    def error(self, message, details=None):
        self.log("ERROR", message, details)

    def warning(self, message, details=None):
        self.log("WARNING", message, details)

# Create a singleton instance
mongo_logger = MongoDBLogger()
