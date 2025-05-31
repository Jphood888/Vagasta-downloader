import requests
import random
import string
import os
from .temp_mail import create_temp_email, wait_for_instagram_code
from .insta_login import save_session_cookies  # Reuse login's cookie saver

def generate_random_username():
    return "vagasta_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def generate_strong_password():
    return ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*", k=12))

def perform_instagram_signup():
    email = create_temp_email()
    username = generate_random_username()
    password = generate_strong_password()

    signup_url = "https://www.instagram.com/accounts/web_create_ajax/"
    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.instagram.com/accounts/emailsignup/",
        "X-Requested-With": "XMLHttpRequest",
    }

    # Initial GET to get CSRF
    session.get("https://www.instagram.com/")
    csrf_token = session.cookies.get("csrftoken")
    headers["X-CSRFToken"] = csrf_token

    payload = {
        "email": email,
        "username": username,
        "password": password,
        "first_name": "Vagasta User",
        "opt_into_one_tap": False,
    }

    resp = session.post(signup_url, headers=headers, data=payload)

    if resp.status_code == 200 and ("user" in resp.text or "account_created" in resp.text):
        print("Signup request sent successfully.")

        # OPTIONAL: Wait for email verification
        code = wait_for_instagram_code(email)
        # (Not implemented yet — use Playwright later to handle code entry)

        # Save cookies
        save_session_cookies(session, username)

        return {
            "status": "ok",
            "username": username,
            "password": password,
            "email": email
        }

    else:
        return {
            "status": "fail",
            "error": f"Signup failed: {resp.text}",
            "debug": {
                "response_code": resp.status_code,
                "response_body": resp.text
            }
        }
