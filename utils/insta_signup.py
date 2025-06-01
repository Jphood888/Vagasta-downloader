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
    return asyncio.run(_signup_async())

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

        # 2. Wait for Instagram code
        print("⏳ Waiting for verification code...")
        code = await wait_for_instagram_code(token)
        print(f"✅ Code received: {code}")

        # 3. Sign up using Playwright
        cookies = await signup_instagram(email, username, password, code)

        return {
            "status": "ok",
            "email": email,
            "username": username,
            "password": password,
            "cookies": cookies
        }

    except Exception as e:
        return {
            "status": "fail",
            "error": str(e)
        }
