from playwright.async_api import async_playwright

async def login_to_instagram(username, password):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto("https://www.instagram.com/accounts/login/")
        await page.fill("input[name='username']", username)
        await page.fill("input[name='password']", password)
        await page.click("button[type='submit']")
        await page.wait_for_timeout(5000)

        # Check login success or failure
        cookies = await context.cookies()
        await browser.close()
        return cookies
