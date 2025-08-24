import os
import json
from firebase_admin import auth, credentials, initialize_app
from typing import Optional


class FirebaseConfig:
    def __init__(self):
        self.app = None
        self.initialize()
    
    def initialize(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Try to get credentials from environment variable (JSON string)
            firebase_credentials = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
            
            if firebase_credentials:
                # Parse JSON string from environment
                cred_dict = json.loads(firebase_credentials)
                cred = credentials.Certificate(cred_dict)
            else:
                # Fallback to service account file
                service_account_path = os.getenv(
                    "FIREBASE_SERVICE_ACCOUNT_PATH", 
                    "config/firebase-service-account.json"
                )
                cred = credentials.Certificate(service_account_path)
            
            self.app = initialize_app(cred)
            print("Firebase initialized successfully")
            
        except Exception as e:
            print(f"Failed to initialize Firebase: {e}")
            raise
    
    async def verify_token(self, id_token: str) -> Optional[dict]:
        """Verify Firebase ID token and return user info"""
        try:
            decoded_token = auth.verify_id_token(id_token)
            return {
                "uid": decoded_token["uid"],
                "email": decoded_token.get("email"),
                "name": decoded_token.get("name", decoded_token.get("email", "Unknown"))
            }
        except Exception as e:
            print(f"Token verification failed: {e}")
            return None


# Global Firebase instance
firebase_config = FirebaseConfig()