import pytest
from unittest.mock import Mock, patch
from datetime import timedelta, datetime
from jose import jwt
from app.services.auth import AuthService
from app.models.user import UserModel
from app.schemas.auth import UserCreateSchema
from pydantic import ValidationError

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def auth_service(mock_db):
    return AuthService(mock_db)

def test_register_new_user(mock_db, auth_service):
    user_data = UserCreateSchema(
        username="testuser",
        email="test@example.com",
        password="strongpassword123"
    )
    mock_db.find_one.return_value = None
    mock_insert_result = Mock()
    mock_insert_result.inserted_id = "mock_user_id"
    mock_db.insert_one.return_value = mock_insert_result

    result = auth_service.register(user_data)

    assert result == {"user_id": "mock_user_id"}
    mock_db.find_one.assert_called_once_with({"email": user_data.email})
    mock_db.insert_one.assert_called_once()

def test_register_existing_user(mock_db, auth_service):
    user_data = UserCreateSchema(
        username="existinguser",
        email="existing@example.com",
        password="strongpassword123"
    )
    mock_db.find_one.return_value = {"email": user_data.email}

    with pytest.raises(ValueError, match="User with this email already exists"):
        auth_service.register(user_data)

def test_register_invalid_data(mock_db, auth_service):
    with pytest.raises(ValidationError):
        invalid_user_data = UserCreateSchema(
            username="invalid-username",
            email="invalid-email",
            password=1321
        )
        auth_service.register(invalid_user_data)

    

def test_login_successful(mock_db, auth_service):
    email = "login@example.com"
    password = "correctpassword"
    hashed_password = auth_service._create_token({"sub": "user_id"}, timedelta(days=1))

    mock_user = {
        "_id": "user_id",
        "email": email,
        "hashed_password": hashed_password
    }
    mock_db.find_one.return_value = mock_user

    with patch("app.services.auth.verify_password", return_value=True):
        result = auth_service.login(email, password)

        assert "access_token" in result
        assert result["token_type"] == "bearer"

def test_login_user_not_found(mock_db, auth_service):
    mock_db.find_one.return_value = None

    with pytest.raises(ValueError, match="User not found"):
        auth_service.login("nonexistent@example.com", "anypassword")

def test_login_invalid_password(mock_db, auth_service):
    email = "login@example.com"
    password = "wrongpassword"

    mock_user = {
        "_id": "user_id",
        "email": email,
        "hashed_password": "hashedpassword"
    }
    mock_db.find_one.return_value = mock_user

    with patch("app.services.auth.verify_password", return_value=False):
        with pytest.raises(ValueError, match="Invalid password"):
            auth_service.login(email, password)

def test_create_token(auth_service):
    test_data = {"sub": "user_id"}
    expires = timedelta(days=1)

    token = auth_service._create_token(test_data, expires)

    payload = jwt.decode(token, auth_service.SECRET_KEY, algorithms=["HS256"])
    assert payload["sub"] == "user_id"
    assert "exp" in payload

def test_verify_token(auth_service):
    test_data = {"sub": "user_id"}
    token = auth_service._create_token(test_data, timedelta(days=1))

    user_id = auth_service.verify_token(token)
    assert user_id == "user_id"

def test_verify_invalid_token(auth_service):
    invalid_token = "invalid.token.here"

    with pytest.raises(ValueError, match="Invalid token"):
        auth_service.verify_token(invalid_token)

def test_token_expiration(auth_service):
    past_data = {"sub": "user_id", "exp": datetime.utcnow() - timedelta(days=1)}
    expired_token = jwt.encode(past_data, auth_service.SECRET_KEY, algorithm="HS256")

    with pytest.raises(ValueError, match="Invalid token"):
        auth_service.verify_token(expired_token)