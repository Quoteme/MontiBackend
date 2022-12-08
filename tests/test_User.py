from pytest_mock import mocker
from src.User import User, Administrator, Guest
import pandas
import pytest


EXAMPLE_USER_CFG_ONE_ADMIN = pandas.DataFrame({
    'user': ['test'],
    'password': ['passwort'],
    'userrole': ['administrator']
})

EXAMPLE_USER_CFG_ONE_GUEST = pandas.DataFrame({
    'user': ['test'],
    'password': ['passwort'],
    'userrole': ['guest']
})

def test_user_can_be_created():
    user = User()
    assert user is not None


def test_user_can_be_created_with_data():
    user = User(
        username="test",
        password="passwort",
    )
    assert user is not None


@pytest.mark.mock
def test_can_find_userrole_by_name_admin(mocker):
    # Create a mock for the `pandas.read_csv()` function using the `mocker` fixture
    mock_read_csv = mocker.patch('pandas.read_csv', return_value=EXAMPLE_USER_CFG_ONE_ADMIN)
    role = User.find_role("test")
    assert role == "admin"

@pytest.mark.mock
def test_can_find_userrole_by_name_guest(mocker):
    # Create a mock for the `pandas.read_csv()` function using the `mocker` fixture
    mock_read_csv = mocker.patch('pandas.read_csv', return_value=EXAMPLE_USER_CFG_ONE_GUEST)
    role = User.find_role("test")
    assert role == "guest"

@pytest.mark.mock
def test_valid_guest_found_in_db(mocker):
    mock_read_csv = mocker.patch('pandas.read_csv', return_value=EXAMPLE_USER_CFG_ONE_GUEST)
    u = User.parse("test", "passwort")
    assert isinstance(u, Guest)
    assert not isinstance(u, Administrator)

@pytest.mark.mock
def test_valid_admin_found_in_db(mocker):
    mock_read_csv = mocker.patch('pandas.read_csv', return_value=EXAMPLE_USER_CFG_ONE_ADMIN)
    u = User.parse("test", "passwort")
    assert not isinstance(u, Guest)
    assert isinstance(u, Administrator)

@pytest.mark.mock
def test_invalid_username(mocker):
    mock_read_csv = mocker.patch('pandas.read_csv', return_value=EXAMPLE_USER_CFG_ONE_ADMIN)
    u = User.parse("invalid_name", "passwort")
    assert not isinstance(u, Guest)
    assert not isinstance(u, Administrator)
    assert u is None

@pytest.mark.mock
def test_invalid_password(mocker):
    mock_read_csv = mocker.patch('pandas.read_csv', return_value=EXAMPLE_USER_CFG_ONE_ADMIN)
    u = User.parse("test", "invalid_password")
    assert not isinstance(u, Guest)
    assert not isinstance(u, Administrator)
    assert u is None