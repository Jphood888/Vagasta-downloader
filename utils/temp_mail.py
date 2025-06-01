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

async def wait_for_instagram_code(token):
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        for _ in range(30):
            res = await client.get(f"{MAIL_TM_BASE}/messages", headers=headers)
            msgs = res.json()["hydra:member"]
            for msg in msgs:
                if "instagram" in msg["from"]["address"].lower():
                    full = await client.get(f"{MAIL_TM_BASE}/messages/{msg['id']}", headers=headers)
                    text = full.json()["text"]
                    code_match = re.search(r"(\d{6})", text)
                    if code_match:
                        return code_match.group(1)
            await asyncio.sleep(2)
        raise TimeoutError("No Instagram code received")
