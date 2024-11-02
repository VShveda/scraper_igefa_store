import json
import os


class DataStorage:
    def __init__(self, progress_path):
        self.progress_path = progress_path
        self.data = self.load_progress()

    def load_progress(self):
        if os.path.exists(self.progress_path):
            with open(self.progress_path, "r") as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    return {}
        return {}

    def save_progress(self):
        with open(self.progress_path, "w") as file:
            json.dump(self.data, file)

    def save_product(self, url, product_data):
        self.data[url] = product_data
        self.save_progress()
