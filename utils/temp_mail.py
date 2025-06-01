# utils/temp_mail.py

import httpx
import asyncio
import uuid
import re

MAIL_TM_BASE = "https://api.mail.tm"

async def create_temp_mail():
    async with httpx.AsyncClient() as client:
        domains_res = await client.get(f"{MAIL_TM_BASE}/domains")
        domain = domains_res.json()["hydra:member"][0]["domain"]

        username = f"vagasta_{uuid.uuid4().hex[:8]}"
        email = f"{username}@{domain}"
        password = "VagastaTemp123!"

        await client.post(f"{MAIL_TM_BASE}/accounts", json={
            "address": email,
            "password": password
        })

        token_res = await client.post(f"{MAIL_TM_BASE}/token", json={
            "address": email,
            "password": password
        })

        token = token_res.json()["token"]

        return {
            "username": username,
            "email": email,
            "password": password,
            "token": token
        }

async def wait_for_instagram_code(token, max_wait_seconds=90):
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        waited = 0
        while waited < max_wait_seconds:
            try:
                res = await client.get(f"{MAIL_TM_BASE}/messages", headers=headers)
                msgs = res.json().get("hydra:member", [])
                for msg in msgs:
                    if "instagram" in msg["from"]["address"].lower():
                        full = await client.get(f"{MAIL_TM_BASE}/messages/{msg['id']}", headers=headers)
                        text = full.json().get("text", "")
                        code_match = re.search(r"(\d{6})", text)
                        if code_match:
                            return code_match.group(1)
            except Exception as e:
                print(f"⚠️ Error checking mail: {e}")
            await asyncio.sleep(5)
            waited += 5

        raise TimeoutError("❌ No Instagram verification code received after waiting.")
