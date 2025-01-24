from pymongo import MongoClient
from datetime import datetime
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/"))
        self.db = self.client["feedback_db"]
        self.feedback_collection = self.db["feedback"]
        self.users_collection = self.db["users"]
        self._ensure_admin_exists()

    def _ensure_admin_exists(self):
        """Ensure admin user exists in the database"""
        if self.users_collection.count_documents({"username": "admin"}) == 0:
            hashed_password = bcrypt.hashpw("admin".encode('utf-8'), bcrypt.gensalt())
            admin_user = {
                "username": "admin",
                "password": hashed_password,
                "role": "admin",
                "created_at": datetime.now()
            }
            self.users_collection.insert_one(admin_user)

    def verify_user(self, username: str, password: str) -> bool:
        """Verify user credentials"""
        user = self.users_collection.find_one({"username": username})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            return True
        return False

    def save_feedback(self, feedback_data: dict):
        """Save feedback to database"""
        feedback_data["created_at"] = datetime.now()
        return self.feedback_collection.insert_one(feedback_data)

    def get_all_feedback(self):
        """Get all feedback entries"""
        return list(self.feedback_collection.find())

    def get_feedback_metrics(self):
        """Get aggregated feedback metrics"""
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "avg_usability": {"$avg": "$usability_rating"},
                    "avg_performance": {"$avg": "$performance_rating"},
                    "avg_ui": {"$avg": "$ui_rating"},
                    "avg_documentation": {"$avg": "$documentation_rating"},
                    "total_feedback": {"$sum": 1},
                    "avg_sentiment": {"$avg": "$sentiment_score"}
                }
            }
        ]
        metrics = list(self.feedback_collection.aggregate(pipeline))
        return metrics[0] if metrics else None

    def get_feedback_by_date(self):
        """Get feedback grouped by date"""
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$created_at"
                        }
                    },
                    "count": {"$sum": 1},
                    "avg_sentiment": {"$avg": "$sentiment_score"}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        return list(self.feedback_collection.aggregate(pipeline))