# utils/insta_signup.py

import random
import string
import asyncio
from utils.temp_mail import create_temp_mail, wait_for_instagram_code
from playwright_scripts.signup import signup_instagram

def generate_random_username():
    return "vagasta_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def generate_strong_password():
    return ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*", k=12))

def perform_instagram_signup():
    try:
        return asyncio.run(_signup_async())
    except Exception as e:
        return {
            "status": "fail",
            "error": f"Top-level async failure: {str(e)}"
        }

async def _signup_async():
    try:
        # 1. Create a temporary email
        temp = await create_temp_mail()
        email = temp["email"]
        token = temp["token"]
        username = generate_random_username()
        password = generate_strong_password()

        print(f"🟢 Temp Email Created: {email}")
        print(f"📛 Username: {username} | 🔑 Password: {password}")

        # 2. Wait for Instagram verification code
        print("⏳ Waiting for Instagram verification code...")
        code = await wait_for_instagram_code(token)
        print(f"✅ Code received: {code}")

        # 3. Complete Instagram signup using Playwright
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
        return {
            "status": "fail",
            "error": str(e)
    }
