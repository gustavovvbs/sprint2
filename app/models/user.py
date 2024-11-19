from datetime import datetime
from pydantic import BaseModel, EmailStr, Field 
from typing import Optional 
from bson import ObjectId

class UserModel(BaseModel):
    id: Optional[str] = None
    username: str
    email: str
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @classmethod 
    def get_by_email(cls, email: str):
        db = get_db()
        user_data = db.users.find_one({"email": email})

        if user_data: 
            return cls(**user_data)