from loguru import logger
from playwright.async_api import Page
from playwright._impl._api_types import TimeoutError


class Support:

    async def is_visible_selector(self, page: Page, locator: str, timeout=500):
        try:
            await page.wait_for_selector(locator, timeout=timeout)
            return True
        except TimeoutError:
            return False

    # __________________________________________________ text _________________________________________________________
    async def get_all_text_as_str_by_locator(self, page: Page, locator: str, joiner=', '):
        text_list = await page.locator(locator).evaluate_all('(elements) => elements.map(e => e.innerText)')
        return joiner.join(text_list)

    async def get_text_by_locator(self, page: Page, locator: str):
        return await page.locator(locator).first.inner_text()

    # __________________________________________________ handling error  _______________________________________________
    async def is_not_error(self, page: Page, content_loc: str, joiner='\n'):
        if await self.is_visible_selector(page, content_loc):
            return True
        elif await self.is_visible_selector(page, '//div[contains(@class, "error__container")]'):
            return False
        else:
            logger.info('wait content loading... + 0.5s')
            return await self.is_not_error(page, content_loc, joiner)

    # ________________________________________________ work ________________________________________________________
    async def click_wait_get_by_locator(self, page: Page, click_loc: str, joiner='\n'):
        content_loc = '//div[contains(@class, "text-block__content")]'
        if await self.is_visible_selector(page, click_loc, timeout=5 * 1000):
            await page.locator(click_loc).click()
        else:
            await page.reload(wait_until='networkidle')
            return await self.click_wait_get_by_locator(page, click_loc, joiner)

        if await self.is_not_error(page, content_loc, joiner):
            return await self.get_all_text_as_str_by_locator(page, content_loc, joiner)
        else:
            return ""

    async def get_table_content(self, patent_page: Page, locator_click: str, fields: list):
        lenght = len(fields)

        await patent_page.locator(locator_click).click()
        if await self.is_not_error(patent_page, '//td[contains(@class, "table__cell")]'):
            dict_content = {}

            all_elem_in_table = await patent_page.locator('//td[contains(@class, "table__cell")]').all()

            # Make an iterator over all_elem_in_table
            elements_iter = iter(all_elem_in_table)

            # Enumerate starting from 1
            for counter, _ in enumerate(range(len(all_elem_in_table) // lenght), start=1):
                dict_content[counter] = {fields[i]: await row.inner_text() for i, row in
                                         enumerate(next(zip(*[elements_iter] * lenght)))}

            return dict_content
        else:
            return ""
