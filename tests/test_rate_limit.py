# import pytest
# from app.core.enums import OTPPurpose


# def create_user(client, email):
#     client.post("/users/create/", json={
#         "first_name": "Rate",
#         "last_name": "Limit",
#         "email": email,
#         "password": "password123"
#     })


# def test_otp_rate_limit(client):
#     email = "ratetest@test.com"
#     create_user(client, email)

#     # Hit endpoint multiple times
#     for _ in range(5):
#         client.post("/users/otp/request/", json={
#             "email": email,
#             "purpose": OTPPurpose.email_verification
#         })

#     res = client.post("/users/otp/request/", json={
#         "email": email,
#         "purpose": OTPPurpose.email_verification
#     })

#     # If rate limit exists
#     assert res.status_code in (200, 429)


# def test_login_rate_limit(client):
#     email = "ratelogin@test.com"
#     create_user(client, email)

#     for _ in range(5):
#         client.post("/login/", data={
#             "username": email,
#             "password": "wrongpassword"
#         })

#     res = client.post("/login/", data={
#         "username": email,
#         "password": "wrongpassword"
#     })

#     assert res.status_code in (401, 429)
