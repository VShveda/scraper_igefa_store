import asyncio
from app.scraper import IgefaScraper
from app.storage import DataStorage
from app.utils import save_to_csv


async def main() -> None:
    storage = DataStorage("./progress.json")
    scraper = IgefaScraper(storage)

    product_urls = await scraper.get_all_product_urls()

    print(product_urls)

    await scraper.scrape_products(product_urls)
    storage.save_progress()

    print(storage.data)

    save_to_csv(storage.data)


if __name__ == "__main__":
    asyncio.run(main())
