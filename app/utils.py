import csv


def save_to_csv(data, file_path: str = "./result.csv") -> None:
    data_list = list(data.values())
    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=data_list[0].keys())
        writer.writeheader()
        writer.writerows(data_list)
