import asyncio
import time

import aiohttp
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

from app.storage import DataStorage, IgefaScraperLoaderProgressUrl

BESET_URL = "https://store.igefa.de/c/kategorien/f4SXre6ovVohkGNrAvh3zR"


class IgefaScraper(IgefaScraperLoaderProgressUrl):
    def __init__(
            self,
            storage: DataStorage = DataStorage("../progress.json")
    ) -> None:
        self.base_url = BESET_URL
        self.storage = storage
        super().__init__()

    @staticmethod
    async def fetch_page(session: aiohttp.ClientSession, url: str) -> str:
        async with session.get(url) as response:
            return await response.text()

    async def fetch_page_with_selenium(self, driver: WebDriver) -> str:
        return await asyncio.to_thread(self.selenium_fetch, driver)

    async def get_all_product_urls(self) -> list[str]:
        page_number = self.last_page
        all_product_urls = []
        driver = webdriver.Chrome()
        driver.get(self.base_url)
        time.sleep(2)
        IgefaScraper.accept_cookies(driver)
        while True:
            page_url = f"{self.base_url}?limit=10&page={page_number}"
            driver.get(page_url)
            try:
                product_urls = await self.fetch_page_with_selenium(driver)
            except Exception:
                product_urls = []
            self.save_progress(product_urls, page_number)
            all_product_urls.extend(product_urls)
            if not product_urls:
                break
            page_number += 1

        return all_product_urls

    @staticmethod
    def accept_cookies(driver: WebDriver) -> None:
        try:
            accept_button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        "a#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll",
                    )
                )
            )
            accept_button.click()
            print("Cookies accepted")
        except Exception:
            print("Cookies already accepted")

    @staticmethod
    def selenium_fetch(driver: WebDriver) -> list[str]:
        urls_products = []
        for num in range(1, 11):
            selector = (
                f"div:nth-child({num}) > div > div > "
                f"div.ProductCard_productDescription__e4363 > span > span"
            )
            WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            product_card = driver.find_element(By.CSS_SELECTOR, selector)
            product_card.click()
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            try:
                supplier_url = soup.select_one("head > link[rel=canonical]")["href"]
                urls_products.append(supplier_url)
            except AttributeError:
                print("Supplier URL not found for product.")

            driver.back()
        return urls_products

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

    async def scrape_products(self, urls: list[str]) -> None:
        async with aiohttp.ClientSession() as session:
            for url in urls:
                if self.storage.data.get(url):
                    print(f"Product at {url} already scraped, skipping.")
                    continue

                page_content = await self.fetch_page(session, url)
                product_data = await self.parse_product_page(page_content)
                self.storage.save_product(url, product_data)
