from playwright.async_api import Page


class Support:

    async def get_all_text_as_str_by_locator(self, page: Page, locator: str, joiner=', '):
        text_list = await page.locator(locator).evaluate_all('(elements) => elements.map(e => e.innerText)')
        return joiner.join(text_list)

    async def get_text_by_locator(self, page: Page, locator: str):
        return await page.locator(locator).first.inner_text()

    async def click_wait_get_by_locator(self, page: Page, click_loc: str, content_loc: str, joiner='\n'):
        await page.locator(click_loc).click()
        try:
            await page.wait_for_selector(content_loc, timeout=10 * 1000)
            text = await self.get_all_text_as_str_by_locator(page, content_loc, joiner)

            return text
        except TimeoutError:
            return ''

    # async def content_by_click(self, page: Page, click_loc: str, wait_loc: str, joiner='\n'):
    #     return await self.click_wait_get_by_locator(page, click_loc, wait_loc=wait_loc, joiner=joiner)

    async def get_table_content(self, patent_page: Page, locator_click: str, fields: list):
        lenght = len(fields)

        await patent_page.locator(locator_click).click()
        await patent_page.wait_for_selector('//td[contains(@class, "table__cell")]')

        dict_content = {}
        all_elem_in_table = await patent_page.locator('//td[contains(@class, "table__cell")]').all()

        # Make an iterator over all_elem_in_table
        elements_iter = iter(all_elem_in_table)

        # Enumerate starting from 1
        for counter, _ in enumerate(range(len(all_elem_in_table) // lenght), start=1):
            dict_content[counter] = {fields[i]: await row.inner_text() for i, row in
                                     enumerate(next(zip(*[elements_iter] * lenght)))}

        return dict_content
