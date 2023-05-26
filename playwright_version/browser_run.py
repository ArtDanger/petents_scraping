import asyncio

from playwright.async_api import async_playwright
from loguru import logger

from contents import Espacenet


@logger.catch
async def main():
    async with async_playwright() as p:

        # phone = p.devices["Pixel 4a (5G)"]
        # browser = await p.chromium.launch(
        #     headless=False,
        #     proxy={
        #         'server': 'http://host:22225',
        #         'username': 'user',
        #         'password': 'pswd'
        #     }
        # )
        # context = await browser.new_context(
        #     **phone,
        # )

        # phone = p.devices["Pixel 4a (5G)"]
        phone = p.devices["Desktop Firefox"]
        browser = await p.firefox.launch(
            headless=False,
        )
        context = await browser.new_context(
            **phone,
        )

        async with Espacenet(context) as creator:
            # action on page
            await creator.scroll_patents()

        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
