from datetime import datetime
from app.db.mongo_client import get_db
from app.models.user import UserModel 
from app.schemas.auth import UserCreateSchema 
from app.core.security import hash_password, verify_password
from datetime import timedelta  
from jose import jwt, JWTError
import os 
from dotenv import load_dotenv 
from pydantic import ValidationError

load_dotenv()


class AuthService:
    def __init__(self, db):
        self.db = db 
        self.ACCESS_TOKEN_EXPIRE_DAYS = 7
        self.SECRET_KEY = os.getenv("SECRET_KEY")

    def register(self, user_data: dict):
        existing_user = self.db.find_one({"email": user_data["email"]})
        if existing_user:
            raise ValueError("User with this email already exists")

        hashed_password = hash_password(user_data["password"])
        try:
            user = UserModel(
                username = user_data["username"],
                email = user_data["email"],
                hashed_password = hashed_password,
            )

            result = self.db.insert_one(user.dict())
            return {"user_id": str(result.inserted_id)}

        except ValidationError as e:
            raise ValidationError(e)

    def login(self, email: str, password: str):
        user = self.db.find_one({"email": email})

        if not user:
            raise ValueError("User not found")
        
        if not verify_password(password, user["hashed_password"]):
            raise ValueError("Invalid password or email")

        access_token = self._create_token(
            data = {"sub": str(user["_id"])},
            expires_delta = timedelta(self.ACCESS_TOKEN_EXPIRE_DAYS)
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    def _create_token(self, data: dict, expires_delta: timedelta):
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})

        return jwt.encode(to_encode, self.SECRET_KEY)

    def verify_token(self, token: str):
        try:
            payload = jwt.decode(token, self.SECRET_KEY)
            user_id = payload.get("sub")
            if user_id is None:
                raise ValueError("Invalid token")
            return user_id
        except JWTError:
            raise ValueError("Invalid token")



