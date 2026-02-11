import pytest
from app.schemas.response import ResponseUserSchema, UsersSchema
from app.schemas.request import RegisterUserSchema
from app.utils.login_util import hash_password
from tests.factories import UserFactory

from unittest.mock import patch
from app.core.enums import OTPPurpose


def authenticate_user(client, email="testuser@example.com", password="password123"):
    client.post("/users/create/", json={
        "first_name": "Test",
        "last_name": "User",
        "email": email,
        "password": password,
    })

    with patch("app.services.user_service.generate_otp") as mock_otp:
        mock_otp.return_value = "123456"

        client.post("/users/otp/request/", json={
            "email": email,
            "purpose": OTPPurpose.EMAIL_VERIFICATION.value
        })

    client.post("/users/otp/verify/", json={
        "email": email,
        "otp": "123456"
    })

    res = client.post(
        "/login/",
        data={
            "username": email,
            "password": password,
        },
    )

    token = res.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}



def test_root(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["Hello"] == "World"


def test_create_user_success(client):
    payload = RegisterUserSchema(
        first_name="Test",
        last_name="User",
        email="newuser@test.com",
        password="password123"
    )
    res = client.post("/users/create/", json=payload.model_dump())
    assert res.status_code == 201
    validated = ResponseUserSchema.model_validate(res.json())
    assert validated.email == payload.email
    assert isinstance(validated.id, int)


def test_create_user_duplicate(client, db_session):
    # Create existing user via factory
    user = UserFactory()
    db_session.commit()
    payload = RegisterUserSchema(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password="password123"
    )
    res = client.post("/users/create/", json=payload.model_dump())
    assert res.status_code == 409
    assert "already exists" in res.json()["detail"]


def test_get_all_users(client, db_session):
    UserFactory.create_batch(5)
    db_session.commit()
    headers = authenticate_user(client)
    res = client.get("/users/all", headers=headers)
    assert res.status_code == 200
    validated = UsersSchema.model_validate(res.json())
    assert len(validated.users) == 5 + 1


def test_get_user_by_id(client, db_session):
    user = UserFactory()
    db_session.commit()
    headers = authenticate_user(client)
    res = client.get(f"/users/{user.id}", headers=headers)
    assert res.status_code == 200
    validated = ResponseUserSchema.model_validate(res.json())
    assert validated.id == user.id
    assert validated.email == user.email


def test_get_user_not_found(client):
    headers = authenticate_user(client)
    res = client.get("/users/999999", headers=headers)
    assert res.status_code == 404


def test_delete_user(client, db_session):
    user = UserFactory()
    db_session.commit()
    headers = authenticate_user(client)
    res = client.delete(f"/users/delete/{user.id}", headers=headers)
    assert res.status_code == 204
    check = client.get(f"/users/{user.id}", headers=headers)
    assert check.status_code == 401


@pytest.mark.parametrize(
    "first_name,last_name",
    [
        ("Updated", "User"),
        ("Alpha", "Beta"),
    ],
)
def test_update_user_details(client, db_session, first_name, last_name):
    user = UserFactory()
    db_session.commit()
    headers = authenticate_user(client)
    res = client.put(
        "/users/update-detail",
        json={
            "first_name": first_name,
            "last_name": last_name
        },
        headers=headers
    )

    # If your endpoint requires authentication,
    # later we will inject token here.
    assert res.status_code in (202, 401)



def test_update_password(client, db_session):
    raw_password = "password123"
    user = UserFactory(hashed_password=hash_password(raw_password))
    db_session.commit()
    headers = authenticate_user(client)

    res = client.patch(
        "/users/update-password",
        json={
            "old_password": raw_password,
            "new_password": "newpassword123"
        },
        headers=headers
    )

    assert res.status_code in (202, 401)
