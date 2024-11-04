import json
import os


class DataStorage:
    def __init__(self, progress_path: str) -> None:
        self.progress_path = progress_path
        self.data = self.load_progress()

    def load_progress(self) -> dict:
        if os.path.exists(self.progress_path):
            with open(self.progress_path, "r") as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    return {}
        return {}

    def save_progress(self) -> None:
        with open(self.progress_path, "w") as file:
            json.dump(self.data, file)

    def save_product(self, url: str, product_data: dict) -> None:
        self.data[url] = product_data
        self.save_progress()


class IgefaScraperLoaderProgressUrl:
    def __init__(self) -> None:
        self.progress_file = "scraped_urls.json"
        self.progress_data = self.load_progress()
        self.scraped_urls = self.progress_data.get("urls", [])
        self.last_page = self.progress_data.get("last_page", 1)

    def load_progress(self) -> dict:
        if os.path.exists(self.progress_file):
            with open(self.progress_file, "r") as file:
                return json.load(file)
        return {"urls": [], "last_page": 1}

    def save_progress(
            self,
            urls: list[str],
            page_number: int
    ) -> None:
        self.scraped_urls.extend(urls)
        self.progress_data = {
            "urls": self.scraped_urls,
            "last_page": page_number,
        }
        with open(self.progress_file, "w") as file:
            json.dump(self.progress_data, file)
