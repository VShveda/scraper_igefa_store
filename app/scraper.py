import aiohttp
from bs4 import BeautifulSoup

from app.storage import DataStorage


BESET_URL = "https://store.igefa.de/c/kategorien/f4SXre6ovVohkGNrAvh3zR"


class IgefaScraper:
    def __init__(self, storage: DataStorage) -> None:
        self.base_url = BESET_URL
        self.storage = storage

    @staticmethod
    async def fetch_page(session: aiohttp.ClientSession, url: str) -> str:
        async with session.get(url) as response:
            return await response.text()

    # async def get_all_product_urls(self):
    #     async with aiohttp.ClientSession() as session:
    #         page_number = 1
    #         all_product_urls = []
    #
    #         while True:
    #             page_url = f"{self.base_url}?page={page_number}"
    #             product_urls = await self.get_product_urls(session, page_url)
    #
    #             if not product_urls:
    #                 break
    #
    #             all_product_urls.extend(product_urls)
    #             page_number += 1
    #
    #         return all_product_urls

    @staticmethod
    async def parse_product_page(html: str) -> dict:
        soup = BeautifulSoup(html, "html.parser")
        try:
            product_name = soup.select(
                "div.ProductInformation_productInfo__fcd94 > h1"
            )[0].get_text()
        except AttributeError:
            product_name = None

        try:
            data_column_1 = "/".join(
                span.get_text()
                for span in soup.select(
                    "span.ant-typography.CategoryBreadcrumbs_breadcrumb__e6d88"
                )
            )
        except AttributeError:
            data_column_1 = None

        data = {
            "Ausführung": None,
            "Artikelnummer": None,
            "EAN": None,
            "Herstellernummer": None,
        }
        for i in soup.select("div.ProductInformation_variantInfo__5cb1d > div"):
            try:
                data[i.get_text().split(":")[0]] = i.get_text().split(":")[1].strip()
            except AttributeError:
                pass

        try:
            description = soup.select_one(
                "div.ProductDetail_description__929ca > div > div > p"
            ).get_text()
        except AttributeError:
            description = None

        try:
            supplier_url = soup.select_one("head > link[rel=canonical]")["href"]
        except AttributeError:
            supplier_url = None

        try:
            image_url = soup.select_one(
                "div.image-gallery-slide-wrapper.bottom > div > div > img"
            )["src"]
        except AttributeError:
            image_url = None

        try:
            manufacturer = (
                soup.select("tbody.ant-table-tbody > tr[data-row-key='33'] > td")[1]
            ).get_text()
        except AttributeError:
            manufacturer = None

        try:
            data_column_3 = "/".join(
                span.get_text()
                for span in soup.select(
                    "div.ProductBenefits_productBenefits__1b77a > ul > li"
                )
            )
        except AttributeError:
            data_column_3 = None

        return {
            "Product Name": product_name,
            "Original Data Column 1 (Breadcrumb)": data_column_1,
            "Original Data Column 2 (Ausführung)": data["Ausführung"],
            "Supplier Article Number": data["Artikelnummer"],
            "EAN/GTIN": data["EAN"],
            "Article Number": data["Herstellernummer"],
            "Product Description": description,
            "Supplier": "igefa Handelsgesellschaft",
            "Supplier-URL": supplier_url,
            "Product Image URL": image_url,
            "Manufacturer": manufacturer,
            "Original Data Column 3 (Add. Description)": data_column_3,
        }

    async def scrape_products(self, urls):
        async with aiohttp.ClientSession() as session:
            for url in urls:
                if self.storage.data.get(url):
                    print(f"Product at {url} already scraped, skipping.")
                    continue

                page_content = await self.fetch_page(session, url)
                product_data = await self.parse_product_page(page_content)
                self.storage.save_product(url, product_data)
