# utils/insta_signup.py

import random
import string
from utils.temp_mail import create_temp_mail, wait_for_instagram_code
from playwright_scripts.signup import signup_instagram

def generate_random_username():
    return "vagasta_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def generate_strong_password():
    return ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*", k=12))

async def perform_instagram_signup(username=None, password=None, email=None):
    try:
        # 1. Create a temporary email if none provided
        if not email:
            temp = await create_temp_mail()
            email = temp["email"]
            token = temp["token"]
        else:
            temp = await create_temp_mail(custom_email=email)
            token = temp["token"]

        # 2. Generate random username/password if not provided
        if not username:
            username = generate_random_username()
        if not password:
            password = generate_strong_password()

        print(f"🟢 Email: {email}")
        print(f"📛 Username: {username} | 🔑 Password: {password}")

        # 3. Wait for Instagram verification code
        print("⏳ Waiting for Instagram verification code...")
        code = await wait_for_instagram_code(token)
        print(f"✅ Code received: {code}")

        # 4. Complete signup using Playwright
        cookies = await signup_instagram(email, username, password, code)
        print("🎉 Signup successful!")

        return {
            "status": "ok",
            "email": email,
            "username": username,
            "password": password,
            "cookies": cookies
        }

    except TimeoutError as te:
        print(f"⏱️ TimeoutError: {str(te)}")
        return {
            "status": "fail",
            "error": f"Timeout: {str(te)}"
        }

    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")

        if "Invalid code" in str(e):
            return {
                "status": "fail",
                "error": "Instagram code expired or invalid"
            }

        return {
            "status": "fail",
            "error": str(e)
        }
