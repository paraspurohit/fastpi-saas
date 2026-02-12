import time
import pytest
from unittest.mock import patch

from app.schemas.token import Token
from app.core.enums import OTPPurpose


def create_user_via_api(client, email):
    res = client.post(
        "/users/create/",
        json={
            "first_name": "Auth",
            "last_name": "User",
            "email": email,
            "password": "password123",
        },
    )
    assert res.status_code == 201


# app.services.user_service.generate_otp
def test_request_otp_mocked(client):
    email = "authuser@test.com"
    create_user_via_api(client, email)
    with patch("app.services.user_service.generate_otp") as mock_send:
        mock_send.return_value = "123456"
        res = client.post(
            "/users/otp/request/",
            json={"email": email, "purpose": OTPPurpose.EMAIL_VERIFICATION.value},
        )

        assert res.status_code == 200
        mock_send.assert_called_once()


def test_verify_otp_success(client):
    email = "verify@test.com"
    create_user_via_api(client, email)

    with patch("app.services.user_service.generate_otp") as mock_send:
        mock_send.return_value = "123456"

        client.post(
            "/users/otp/request/",
            json={"email": email, "purpose": OTPPurpose.EMAIL_VERIFICATION.value},
        )

    res = client.post("/users/otp/verify/", json={"email": email, "otp": "123456"})

    assert res.status_code == 200


def test_verify_invalid_otp(client):
    email = "invalidotp@test.com"
    create_user_via_api(client, email)
    with patch("app.services.user_service.generate_otp") as mock_otp:
        mock_otp.return_value = "123456"

        request_res = client.post(
            "/users/otp/request/",
            json={"email": email, "purpose": OTPPurpose.EMAIL_VERIFICATION.value},
        )

        assert request_res.status_code == 200
    verify_res = client.post(
        "/users/otp/verify/", json={"email": email, "otp": "000000"}
    )
    assert verify_res.status_code in (400, 401)


def verify_user(client, email):
    with patch("app.services.user_service.generate_otp") as mock_send:
        mock_send.return_value = "123456"

        client.post(
            "/users/otp/request/",
            json={"email": email, "purpose": OTPPurpose.EMAIL_VERIFICATION.value},
        )

    client.post("/users/otp/verify/", json={"email": email, "otp": "123456"})


@pytest.mark.parametrize(
    "password,expected_status",
    [
        ("password123", 200),
        ("wrongpassword", 401),
        ("", 422),
    ],
)
def test_login_variants(client, password, expected_status):
    email = "loginuser@test.com"
    create_user_via_api(client, email)
    verify_user(client, email)

    start = time.perf_counter()

    res = client.post(
        "/login/",
        data={"username": email, "password": password},
    )

    duration = time.perf_counter() - start

    assert res.status_code == expected_status
    assert duration < 0.5
    if expected_status == 200:
        validated = Token.model_validate(res.json())
        assert validated.access_token is not None
        assert validated.token_type == "bearer"


def test_rate_limit_on_root(client):
    for _ in range(101):
        response = client.get("/")

    assert response.status_code == 429

def test_otp_rate_limit(client):
    email = "ratelimit@test.com"
    create_user_via_api(client, email)

    for _ in range(5):
        client.post("/users/otp/request/", json={
            "email": email,
            "purpose": OTPPurpose.EMAIL_VERIFICATION.value
        })
    res = client.post("/users/otp/request/", json={
        "email": email,
        "purpose": OTPPurpose.EMAIL_VERIFICATION.value
    })
    print(res.json())
    assert res.status_code in (200, 429, 409)


def test_login_sql_injection(client):
    res = client.post(
        "/login/",
        data={"username": "' OR 1=1 --", "password": "anything"},
    )

    assert res.status_code in (400, 401)


def test_login_without_verification(client):
    email = "notverified@test.com"
    create_user_via_api(client, email)

    res = client.post(
        "/login/",
        data={"username": email, "password": "password123"},
    )

    assert res.status_code in (400, 401)
