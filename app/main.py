import asyncio
from app.scraper import IgefaScraper
from app.storage import DataStorage
from app.utils import save_to_csv


async def main() -> None:
    storage = DataStorage("../progress.json")
    scraper = IgefaScraper(storage)

    product_urls = [
        "https://store.igefa.de/p/clean-and-clever-smartline-muellbeutel-sma-73-460-mm-x-520-mm-18-l/AHgJ4WmdVM7tj6K7eknSSo",
        "https://store.igefa.de/p/cilan-kosmetiktuch-k20-cilan-kosmetiktuch-k20-2lg/DSnreBDyrHBWeE4LjaeCRK",
        "https://store.igefa.de/p/clean-and-clever-smartline-sanitaerunterhaltsreiniger-sma-80-sma80-sanitaerreiniger-1l-12-saurer-sanitaerunterhaltsreiniger/nvpT3vJoZwmzFmxVdmXDmT",
        "https://store.igefa.de/p/starline-badeslipper-starline-badeslipper-weiss-mit-antirutschsohle-1-paket-25-paar/NeqxryJX6uDU87jKCrGfCU",
    ]

    await scraper.scrape_products(product_urls)
    storage.save_progress()


if __name__ == "__main__":
    asyncio.run(main())
