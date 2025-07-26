import pytest
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../app/Api')))
from models import *

# test the User model
def test_user_model():
    """
    Tests the functionality of the `User` model.

    This function performs the following tests:
    1. Creates a new `User` object with predefined attributes.
    2. Inserts the `User` object into the `USER_TABLE` using the `put()` method.
    3. Verifies that the `get()` method retrieves the correct user data from the table.
    4. Checks that the `to_json()` method accurately converts the user object to a JSON string.

    Assertions:
        - The `get()` method should return the expected dictionary of user attributes.
        - The `to_json()` method should return the correct JSON representation of the user.

    Raises:
        AssertionError: If any of the assertions fail.
    """
    user = User(user_id='123', name='John Doe', username='johndoe', email='john.doe@example.com', hashed_password='password')
    user.put()  # Insert into USER_TABLE
    assert User.get('123') == {'user_id': '123', 'name': 'John Doe', 'username': 'johndoe', 'hashed_password': 'password', 'email': 'john.doe@example.com'}
    assert user.to_json() == '{"user_id": "123", "name": "John Doe", "username": "johndoe", "hashed_password": "password", "email": "john.doe@example.com"}'

# test the UserFiles model
def test_user_files_model():
    """
    Tests the functionality of the `UserFiles` model.

    This function performs the following tests:
    1. Creates a new `UserFiles` object with a user ID and associated file list.
    2. Inserts the `UserFiles` object into the `USER_FILES_TABLE` using the `put()` method.
    3. Verifies that the `get()` method retrieves the correct data for the specified user ID.
    4. Checks that the `to_json()` method accurately converts the `UserFiles` object to a JSON string.

    Assertions:
        - The `get()` method should return the expected dictionary containing the user ID and file list.
        - The `to_json()` method should return the correct JSON representation of the `UserFiles` object.

    Raises:
        AssertionError: If any of the assertions fail.
    """
    user_files = UserFiles(user_id='123', files=['file1', 'file2'])
    user_files.put()  # Insert into USER_FILES_TABLE
    print(UserFiles.get('123'))
    assert UserFiles.get('123') == {'user_id': '123', 'files': ['file1', 'file2']}
    assert user_files.to_json() == '{"user_id": "123", "files": ["file1", "file2"]}'
