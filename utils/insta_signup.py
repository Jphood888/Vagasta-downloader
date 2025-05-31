import requests
import random
import string
import os
from .temp_mail import create_temp_email, wait_for_instagram_code

def generate_random_username():
    return "vagasta" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def generate_strong_password():
    return ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*", k=12))

def perform_instagram_signup():
    email = create_temp_email()
    username = generate_random_username()
    password = generate_strong_password()

    # Simulate form submission to Instagram
    signup_url = "https://www.instagram.com/accounts/web_create_ajax/"
    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.instagram.com/accounts/emailsignup/",
        "X-Requested-With": "XMLHttpRequest",
    }

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
    if resp.status_code == 200 and "user" in resp.text:
        print("Signup sent successfully.")
        # Wait for verification code (if Instagram sends one)
        code = wait_for_instagram_code(email)
        # You may need to post this code to confirm email (depends on flow)

        # Save cookies
        cookies_dir = 'cookies'
        os.makedirs(cookies_dir, exist_ok=True)
        cookie_path = os.path.join(cookies_dir, f'instagram_cookies_{username}.txt')
        with open(cookie_path, 'w') as f:
            for cookie in session.cookies:
                f.write(f"{cookie.domain}\tTRUE\t{cookie.path}\t{str(cookie.secure).upper()}\t{cookie.expires}\t{cookie.name}\t{cookie.value}\n")

        return {
            "status": "ok",
            "username": username,
            "password": password,
            "email": email
        }
    else:
        return {"status": "fail", "error": "Signup failed"}
