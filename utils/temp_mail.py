import time
import random
import requests

def create_temp_email():
    # Use a public API like 1secmail.com
    domain = "1secmail.com"
    username = ''.join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=10))
    return f"{username}@{domain}"

def wait_for_instagram_code(email):
    # Optional - You can replace this with real polling logic
    time.sleep(10)
    return "123456"  # Simulated return, to be updated with real email polling
