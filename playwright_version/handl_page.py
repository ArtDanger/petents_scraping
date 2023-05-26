from playwright.async_api import Browser, BrowserContext, Page

from playwright_stealth import stealth_async


async def new_tab(browser: Browser | BrowserContext, link) -> Page:
    page = await browser.new_page()
    await stealth_async(page)

    await page.goto(link, wait_until='networkidle', timeout=120000)
    return page

