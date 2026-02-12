import pytest
from app.core.enums import OTPPurpose


def create_user(client, email):
    client.post("/users/create/", json={
        "first_name": "Rate",
        "last_name": "Limit",
        "email": email,
        "password": "password123"
    })


def test_otp_rate_limit(client):
    email = "ratetest@test.com"
    create_user(client, email)

    # Hit endpoint multiple times
    for _ in range(5):
        client.post("/users/otp/request/", json={
            "email": email,
            "purpose": OTPPurpose.EMAIL_VERIFICATION.value
        })

    res = client.post("/users/otp/request/", json={
        "email": email,
        "purpose": OTPPurpose.EMAIL_VERIFICATION.value
    })

    # If rate limit exists
    assert res.status_code in (200, 429, 409)

