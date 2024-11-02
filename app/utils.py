import csv


def save_to_csv(data, file_path="../result.csv"):
    data_list = list(data)
    print(f"save_to_csv: {data_list}")
    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=data_list[0].keys())
        writer.writeheader()
        writer.writerows(data_list)
