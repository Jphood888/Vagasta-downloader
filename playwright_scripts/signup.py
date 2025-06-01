from playwright.async_api import async_playwright
import asyncio

async def signup_with_playwright(email, username, password, verification_code):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto("https://www.instagram.com/accounts/emailsignup/")
            await page.wait_for_selector("input[name=emailOrPhone]")

            await page.fill("input[name=emailOrPhone]", email)
            await page.fill("input[name=fullName]", "Vagasta User")
            await page.fill("input[name=username]", username)
            await page.fill("input[name=password]", password)

            await page.click("button[type=submit]")
            await page.wait_for_timeout(5000)

            # Wait for confirmation code field to appear
            await page.wait_for_selector("input[name=email_confirmation_code]", timeout=30000)
            await page.fill("input[name=email_confirmation_code]", verification_code)

            await page.click("button[type=submit]")
            await page.wait_for_timeout(5000)

            # Optional: handle birthday step
            if await page.query_selector('select[title="Month:"]'):
                await page.select_option('select[title="Month:"]', '1')
                await page.select_option('select[title="Day:"]', '1')
                await page.select_option('select[title="Year:"]', '2000')
                await page.click("button[type=submit]")
                await page.wait_for_timeout(3000)

            await browser.close()
            return {"status": "ok", "message": "Signup complete", "username": username}

        except Exception as e:
            await browser.close()
            return {"status": "fail", "error": str(e)}

# ✅ This is the function your backend expects
def signup_instagram(email, username, password, verification_code):
    return asyncio.run(signup_with_playwright(email, username, password, verification_code))
