import random
import string
from utils.temp_mail import create_temp_mail, wait_for_instagram_code
from playwright_scripts.signup import signup_instagram

def generate_random_username():
    return "vagasta_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def generate_strong_password():
    return ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*", k=12))

async def perform_instagram_signup():
    # 1. Create a temp mail account
    temp = await create_temp_mail()
    email = temp["email"]
    username = generate_random_username()
    password = generate_strong_password()

    print(f"🟢 Email created: {email}")
    print(f"📛 Username: {username} | 🔑 Password: {password}")

    # 2. Wait for the Instagram email verification code
    print("⏳ Waiting for Instagram verification code...")
    code = await wait_for_instagram_code(temp["token"])

    print(f"✅ Code received: {code}")

    # 3. Complete signup using Playwright
    cookies = await signup_instagram(email, username, password, code)

    return {
        "status": "ok",
        "email": email,
        "username": username,
        "password": password,
        "cookies": cookies
    }
