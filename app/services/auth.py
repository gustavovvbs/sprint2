from datetime import datetime, timedelta
import os
from app.models.user import UserModel
from app.schemas.auth import UserCreateSchema, UserLoginSchema
from app.core.security import hash_password, verify_password
from jose import jwt, JWTError
from dotenv import load_dotenv

load_dotenv()

class AuthService:
    def __init__(self, db):
        self.db = db
        self.ACCESS_TOKEN_EXPIRE_DAYS = 7
        self.SECRET_KEY = os.getenv("SECRET_KEY")

    def register(self, user_data: dict):
        existing_user = self.db.users.find_one({"email": user_data["email"]})
        if existing_user:
            raise ValueError("User with this email already exists")

        hashed_password = hash_password(user_data["password"])
        user = UserModel(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=hashed_password,
        )

        result = self.db.users.insert_one(user.model_dump())
        return {"user_id": str(result.inserted_id)}

    def login(self, user_data: dict):
        user = self.db.users.find_one({"email": user_data["email"]})
        if not user:
            raise ValueError("User not found")

        if not verify_password(user_data['password'], user["hashed_password"]):
            raise ValueError("Invalid password")

        access_token = self._create_token(
            data={"sub": str(user["_id"])},
            expires_delta=timedelta(days=self.ACCESS_TOKEN_EXPIRE_DAYS),
        )

        return {"access_token": access_token, "token_type": "bearer"}

    def _create_token(self, data: dict, expires_delta: timedelta):
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm="HS256")

    def verify_token(self, token: str):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("sub")
            if user_id is None:
                raise ValueError("Invalid token")
            return user_id
        except JWTError as e:
            raise ValueError("Invalid token") from e
