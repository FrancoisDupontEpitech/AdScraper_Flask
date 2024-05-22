#!/usr/bin/env python

import os
import platform
import threading
import pandas as pd
from get_new_file import retrieve_json_companies_data
from utils.colors import Colors

def get_new_company(mode, selected_websites):
    print(f"{Colors.CYAN}Getting new companies...{Colors.RESET}")
    all_new_companies = []
    all_companies = []

    print(f"{Colors.CYAN}Retrieving data for each website...{Colors.RESET}")
    for website in selected_websites:
        new_companies_detailed, all_companies_detailed = retrieve_json_companies_data(website['name'], mode)
        all_new_companies.extend(new_companies_detailed)
        all_companies.extend(all_companies_detailed)

    cleaned_new_companies_data = clean_companies_data(all_new_companies)
    cleaned_all_companies_data = clean_companies_data(all_companies)

    print(f"{Colors.CYAN}Creating and opening Excel file...{Colors.RESET}")
    create_and_open_excel(cleaned_new_companies_data, cleaned_all_companies_data, mode)

def create_and_open_excel(new_companies_data, all_companies_data, mode):
    # self.loading = True
    threading.Thread(target=create_and_open_excel_thread, args=(new_companies_data, all_companies_data, mode)).start()

def create_and_open_excel_thread(new_companies_data, all_companies_data, mode):
    base_directory = get_app_data_directory("AdScraper")
    output_directory = os.path.join(base_directory, "output")
    excel_filename = f"{mode}_data.xlsx"
    full_excel_path = os.path.join(output_directory, excel_filename)

    os.makedirs(os.path.dirname(full_excel_path), exist_ok=True)
    writer = pd.ExcelWriter(full_excel_path, engine='xlsxwriter')
    df_new = pd.DataFrame(new_companies_data)
    df_all = pd.DataFrame(all_companies_data)
    df_new.to_excel(writer, sheet_name='New Companies Last 30D', index=False)
    df_all.to_excel(writer, sheet_name='All Companies', index=False)
    writer.close()

    print(f"{Colors.GREEN}Excel file created successfully.{Colors.RESET}")

    # Open the Excel file if no errors occurred
    if os.name == 'nt':
        os.startfile(full_excel_path)
    else:
        webbrowser.open('file://' + full_excel_path)

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


def clean_companies_data(companies_data):
    """Cleans the companies data by removing duplicates based on 'link' and sorting by company name."""
    # Use a set to track unique links
    seen_links = set()
    unique_companies = []

    for company_data in companies_data:
        link = company_data['link']
        if link not in seen_links:
            seen_links.add(link)
            unique_companies.append(company_data)

    # Sort the unique companies by company name
    unique_companies.sort(key=lambda x: x['company'])
    return unique_companies