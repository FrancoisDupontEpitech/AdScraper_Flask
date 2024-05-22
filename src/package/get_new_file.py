import os
import platform
import re
import json
from datetime import datetime, timedelta

def read_json(file_path, fallback_date=None):
    """Read a JSON file and return its contents as a dictionary.
    If the file does not exist or is empty, return an empty dictionary.
    Replace dates that do not match the 'DD/MM/YY' pattern with fallback_date if provided."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
            if not file_content:
                print(f"File is empty: {file_path}. Returning empty data.")
                return {}
            data = json.loads(file_content)

            date_pattern = re.compile(r'\d{2}/\d{2}/\d{4}$')

            # If a fallback_date is provided, iterate through the data and replace invalid dates
            if fallback_date:
                for company, entries in data.items():
                    for entry in entries:
                        if not date_pattern.match(str(entry['date'])):
                            entry['date'] = fallback_date

            return data
    except FileNotFoundError:
        print(f"File not found: {file_path}. Returning empty data.")
        return {}
    except json.JSONDecodeError:
        print(f"Invalid JSON in file: {file_path}. Returning empty data.")
        return {}

def find_new_companies(old_data, new_data):
    """Find and return a set of new companies that are in new_data but not in old_data."""
    added_companies = {}
    for company, details in new_data.items():
        if company not in old_data:
            added_companies[company] = details
    return added_companies

def get_directories_dates_within_30_days(path):
    """Get a list of directories within a path, filtering for those within the last 30 days."""
    current_date = datetime.now()
    thirty_days_ago = current_date - timedelta(days=30)

    dirs = []
    for d in os.listdir(path):
        full_path = os.path.join(path, d)
        if os.path.isdir(full_path):
            try:
                dir_date = datetime.strptime(d, "%d-%m-%Y")
                # Include the directory if its date is within the last 30 days
                if thirty_days_ago <= dir_date <= current_date:
                    dirs.append(d)
            except ValueError:
                # Skip directories that do not match the expected date format
                continue

    dirs.sort(key=lambda x: datetime.strptime(x, "%d-%m-%Y"))
    return dirs


def get_all_directory_dates(path):
    """Get a list of all directories within a path based on a specific date format."""
    dirs = []
    for d in os.listdir(path):
        full_path = os.path.join(path, d)
        if os.path.isdir(full_path):
            try:
                # Vérifiez simplement si le nom du dossier correspond au format de date attendu
                datetime.strptime(d, "%d-%m-%Y")
                dirs.append(d)
            except ValueError:
                # Ignore les répertoires qui ne correspondent pas au format de date attendu
                continue

    dirs.sort(key=lambda x: datetime.strptime(x, "%d-%m-%Y"))  # Trier les dossiers par date
    return dirs


def get_all_new_companies(base_path, mode):
    directories_30d = get_directories_dates_within_30_days(base_path)

    if not directories_30d:
        print("No data directories found within the last 30 days.")
        return

    all_new_companies = {}

    for i in range(1, len(directories_30d)):
        old_dir, new_dir = directories_30d[i - 1], directories_30d[i]
        old_file_path = os.path.join(base_path, old_dir, f"{mode}.json")
        new_file_path = os.path.join(base_path, new_dir, f"{mode}.json")

        print(f"Comparing files: old: {old_file_path} and new: {new_file_path}")

        # Use the directory name (new_dir) as the fallback date, after converting it to your desired format
        fallback_date = datetime.strptime(new_dir, "%d-%m-%Y").strftime('%d/%m/%Y')

        old_data = read_json(old_file_path)
        new_data = read_json(new_file_path, fallback_date=fallback_date)

        new_companies = find_new_companies(old_data, new_data)

        # Merge new_companies into all_new_companies
        for company, details_list in new_companies.items():
            if company in all_new_companies:
                all_new_companies[company].extend(details_list)
            else:
                all_new_companies[company] = details_list

    return all_new_companies

def get_all_new_companies(base_path, mode):
    all_directories = get_all_directory_dates(base_path)

    if not all_directories:
        print("No data directories found.")
        return

    all_companies = {}
        # Traitement pour tous les répertoires
    for directory in all_directories:
        file_path = os.path.join(base_path, directory, f"{mode}.json")

        # Utiliser le nom du répertoire comme date de secours
        fallback_date = datetime.strptime(directory, "%d-%m-%Y").strftime('%d/%m/%Y')

        data = read_json(file_path, fallback_date=fallback_date)

        # Fusionner les données dans all_companies
        for company, details_list in data.items():
            if company in all_companies:
                all_companies[company].extend(details_list)
            else:
                all_companies[company] = details_list

    return all_companies

def arrange_companies_data(companies_details):
    detailed_companies_data = []
    for company, details_list in companies_details.items():
        for detail in details_list:
            detailed_companies_data.append({
                "company": company,
                "date": detail["date"],
                "link": detail["link"]
            })
    return detailed_companies_data

def get_app_data_directory(app_name):
    """Get the application data directory based on the operating system."""
    if platform.system() == "Windows":
        base_dir = os.environ['APPDATA']
    elif platform.system() == "Darwin":  # macOS
        base_dir = os.path.expanduser('~/Library/Application Support')
    else:  # Assuming Linux/Unix
        base_dir = os.path.expanduser('~/.local/share')

    app_data_directory = os.path.join(base_dir, app_name)
    os.makedirs(app_data_directory, exist_ok=True)
    return app_data_directory

def get_new_file(website_name, mode):
    print(f"get_new_file from {website_name}...")

    base_directory = get_app_data_directory("Scraper")
    base_path = os.path.join(base_directory, "output", website_name)

    all_new_companies = get_all_new_companies(base_path, mode)
    all_companies = get_all_new_companies(base_path, mode)
    all_new_companies_detailed = arrange_companies_data(all_new_companies)
    all_companies_detailed = arrange_companies_data(all_companies)

    return all_new_companies_detailed, all_companies_detailed


def retrieve_json_companies_data(website_name, mode):
    print(f"retrieve_json_companies_data from {website_name}...")

    base_directory = get_app_data_directory("Scraper")
    base_path = os.path.join(base_directory, "output", website_name)

    all_new_companies = get_all_new_companies(base_path, mode)
    all_companies = get_all_new_companies(base_path, mode)
    all_new_companies_detailed = arrange_companies_data(all_new_companies)
    all_companies_detailed = arrange_companies_data(all_companies)

    return all_new_companies_detailed, all_companies_detailed
