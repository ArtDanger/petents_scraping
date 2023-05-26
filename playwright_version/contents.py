import asyncio

from IPython.lib.pretty import pprint
from loguru import logger
from playwright.async_api import Page
from handl_page import new_tab
from playwright_version.support_method import Support


class Espacenet(Support):
    def __init__(self, browser):
        super().__init__()

        self.browser = browser

    async def __aenter__(self):
        self.page: Page = await new_tab(self.browser, 'https://worldwide.espacenet.com/patent/search?q=US')
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.page.close()

    async def scrap_bibliographic_data(self, patent_page):
        bibliographic_data = {
            'Applicants': await self.get_text_by_locator(patent_page, '#biblio-applicants-content', ),
            'Inventors': await self.get_text_by_locator(patent_page, '#biblio-inventors-content', ),
            'Abstract': await self.get_text_by_locator(patent_page, '#biblio-abstract-content'),
        }

        classifications = {
            'IPC': await self.get_all_text_as_str_by_locator(patent_page, '#biblio-international-content'),
            'CPC': await self.get_all_text_as_str_by_locator(
                patent_page, '//div[@id="biblio-cooperative-content"]//div[contains(@class, "text-collapse__wrapper")]'),
            'Priorities': await self.get_all_text_as_str_by_locator(
                patent_page, '//div[./a[@id="biblio-priority-numbers-content-link"]]'),
            'Application': await self.get_text_by_locator(patent_page, '#biblio-application-number-content'),
            'Publication': await self.get_all_text_as_str_by_locator(patent_page, '#biblio-publication-number-content'),
            'Published as': await self.get_all_text_as_str_by_locator(patent_page, '#biblio-also-published-as-content'),
        }

        bibliographic_data['Classifications'] = classifications

        return bibliographic_data

    async def scrapy_claims(self, patent_page):
        dict_claims = {
            'original': await self.click_wait_get_by_locator(
                patent_page,
                click_loc='//li[@data-qa="claimsTab_resultDescription"]',
                content_loc='//div[contains(@class, "text-block__content")]',
                joiner=' '
            ),
            'tree': await self.click_wait_get_by_locator(
                patent_page,
                click_loc='//li[@data-qa="claimsComponent_ClaimsTreeTab_resultDescription"]',
                content_loc='//div[contains(@class, "text-block__content")]',
                joiner=' '
            ),
        }

        return dict_claims

    async def scrapy_citations(self, patent_page):
        await patent_page.locator('//li[@data-qa="citationsTab_resultDescription"]').click()
        await patent_page.wait_for_selector('//tr[contains(@class, "table__row")]')

        # dict_content = {}
        #
        # CitationOrigin = await patent_page.locator('//td[@label="CitationOrigin"]').all()
        # Publication = await patent_page.locator('//td[@label="Publication"]').all()
        # Title = await patent_page.locator('//td[@label = "Title"]').all()
        # Earliest_priority_date = await patent_page.locator('//td[@label="PriorityDate"]').all()
        # Publication_date = await patent_page.locator('//td[@label="PublicationDate"]').all()
        # Applicant = await patent_page.locator('//td[@label="Applicants"]').all()
        # IPC = await patent_page.locator('//td[@label="InternationalPatentClassification"]').all()
        # CPC = await patent_page.locator('//td[@label="CPCSort"]').all()
        #
        # for count, row in enumerate(CitationOrigin):
        #     dict_content[count] = {
        #         'Citation_origin': await row.inner_text(),
        #         'Publication': await Publication[count].inner_text(),
        #         'Title': await Title[count].inner_text(),
        #         'Earliest_priority_date': await Earliest_priority_date[count].inner_text(),
        #         'Publication_date': await Publication_date[count].inner_text(),
        #         'Applicant': await Applicant[count].inner_text(),
        #         'IPC': await IPC[count].inner_text(),
        #         'CPC': await CPC[count].inner_text(),
        #     }
        labels = [
            "CitationOrigin",
            "Publication",
            "Title",
            "PriorityDate",
            "PublicationDate",
            "Applicants",
            "InternationalPatentClassification",
            "CPCSort",
        ]

        all_elements = {
            label: await patent_page.locator(f'//td[@label="{label}"]').all()
            for label in labels
        }

        dict_content = {
            count: {
                label: await all_elements[label][count].inner_text()
                for label in labels
            }
            for count in range(len(all_elements[labels[0]]))
        }

        return dict_content

    async def scrapy_legal_events(self, patent_page):

        fields = ['Event indicator', 'Category', 'Event description',
                  'Countries', 'Event date', 'Effective date', 'Details']

        return await self.get_table_content(
            patent_page, locator_click='//li[@data-qa="citationsTab_resultDescription"]', fields=fields)

    async def scrapy_family(self, patent_page):
        fields = ['Publication', 'Application number', 'Title', 'Publication date', 'Applicants']

        return await self.get_table_content(
            patent_page, locator_click='//li[@data-qa="patentFamilyTab_resultDescription"]', fields=fields)

    async def scraping_patent(self, url_patent):
        patent_page = await new_tab(self.browser, url_patent)
        try:
            dict_patent = {
                'number_patent': await self.get_text_by_locator(patent_page, '//a[@data-qa="publicationNumber"]/span'),
                'name_patent': await self.get_text_by_locator(patent_page, '//span[@data-qa="publicationTitle"]'),
                'Bibliographic data': await self.scrap_bibliographic_data(patent_page),
                'Description':
                    await self.click_wait_get_by_locator(
                        patent_page,
                        click_loc='//li[@data-qa="descriptionTab_resultDescription"]',
                        content_loc='//div[contains(@class, "text-block__content")]'
                    ),
                'Claims': await self.scrapy_claims(patent_page),
                'Citations': await self.scrapy_citations(patent_page),
                'Legal events': await self.scrapy_legal_events(patent_page),
                'Patent family(Simple family)': await self.scrapy_family(patent_page),
            }

            pprint(dict_patent)
        finally:
            await patent_page.close()

    async def create_task_patent(self, all_patents, clicked_elements):
        for patent in all_patents:
            patent_text = await patent.inner_text()
            if patent_text not in clicked_elements:
                await patent.click()
                clicked_elements.add(patent_text)
                url_patent = await self.page.locator('//a[@data-qa="publicationNumber"]').get_attribute('href')
                task = asyncio.create_task(self.scraping_patent(url_patent))
                yield task

    async def scroll_patents(self):
        counter = 0
        # get all elements
        clicked_elements = set()

        while True:
            counter += 1
            tasks_patent = []

            all_patents = await self.page.locator('//article[@data-qa="result_resultList"]').all()

            if all_patents:
                async for task in self.create_task_patent(all_patents, clicked_elements):
                    # tasks_patent.append(task)
                    await task
                    break

                # scroll down
                await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await self.page.wait_for_load_state('networkidle')

                await asyncio.gather(*tasks_patent)
                logger.info(f'handled: {20 * counter}')

            else:
                break

