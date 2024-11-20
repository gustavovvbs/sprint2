import pytest
from unittest.mock import MagicMock
from app.services.user import UserService

@pytest.fixture
def mock_db():
    db = MagicMock()
    return db

@pytest.fixture
def user_service(mock_db):
    return UserService(mock_db)

def test_get_user_by_id(user_service, mock_db):
    mock_db.users.find_one.return_value = {"_id": "507f1f77bcf86cd799439011", "username": "testuser", "email": "test@example.com"}
    user = user_service.get_user_by_id("507f1f77bcf86cd799439011")
    assert user == {"_id": "507f1f77bcf86cd799439011", "username": "testuser", "email": "test@example.com"}

def test_get_user_by_id_not_found(user_service, mock_db):
    mock_db.users.find_one.return_value = None
    with pytest.raises(ValueError, match="User not found"):
        user_service.get_user_by_id("507f1f77bcf86cd799439011")

def test_get_user_by_email(user_service, mock_db):
    mock_db.users.find_one.return_value = {"email": "test@example.com", "username": "testuser"}
    user = user_service.get_user_by_email("test@example.com")
    assert user == {"email": "test@example.com", "username": "testuser"}

def test_get_user_by_email_not_found(user_service, mock_db):
    mock_db.users.find_one.return_value = None
    with pytest.raises(ValueError, match="User not found"):
        user_service.get_user_by_email("test@example.com")

def test_update_user(user_service, mock_db):
    mock_db.users.update_one.return_value.modified_count = 1
    response = user_service.update_user("507f1f77bcf86cd799439011", {"username": "newuser"})
    assert response == {"message": "user updated successfully"}

def test_update_user_invalid_data(user_service, mock_db):
    with pytest.raises(ValueError, match="Invalid update data"):
        user_service.update_user("507f1f77bcf86cd799439011", {"invalid_field": "value"})

def test_update_user_no_modifications(user_service, mock_db):
    mock_db.users.update_one.return_value.modified_count = 0
    with pytest.raises(ValueError, match="No modifications were made"):
        user_service.update_user("507f1f77bcf86cd799439011", {"username": "newuser"})

def test_delete_user(user_service, mock_db):
    mock_db.users.delete_one.return_value.deleted_count = 1
    response = user_service.delete_user("507f1f77bcf86cd799439011")
    assert response == {"message": "user deleted successfully"}

def test_delete_user_not_found(user_service, mock_db):
    mock_db.users.delete_one.return_value.deleted_count = 0
    with pytest.raises(ValueError, match="User not found"):
        user_service.delete_user("507f1f77bcf86cd799439011")