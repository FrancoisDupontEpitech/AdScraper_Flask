import os
import json

def save_partial_data(company_data, site_name, mode="whitepaper"):
    directory_path = os.path.join(os.getcwd(), "output", site_name)
    os.makedirs(directory_path, exist_ok=True)
    json_file_path = os.path.join(directory_path, f"{mode}_data_partial.json")
    with open(json_file_path, "w") as json_file:
        json.dump(company_data, json_file, indent=4)
