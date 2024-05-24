#!/usr/bin/env python

import json
import os
import threading
from datetime import datetime
from colorama import Fore, Style
from utils.websites_variable import websites
from utils.colors import Colors
from utils.get_directory_name_from_url import get_directory_name_from_url
from utils.open_json_in_excel import generate_excel_from_json
from utils.get_app_data_directory import get_app_data_directory
from utils.delete_partial_json_file import delete_partial_json_file

def get_company_partnership(mod, flag_force, stop_event, selected_websites):
    threads = []
    print(f"{Colors.GREEN}Selected websites: {selected_websites}{Colors.RESET}")
    print(f"{Colors.GREEN}Selected mode: {mod}{Colors.RESET}")
    for website in selected_websites:
        thread = threading.Thread(target=scrape_and_process_website,
                        args=(website, mod, flag_force, stop_event),
                        daemon=True)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

def scrape_and_process_website(website, mod, flag_force, stop_event):
    base_directory = get_app_data_directory("AdScraper")
    directory_name = get_directory_name_from_url(website['url'])
    today_date = datetime.now().strftime("%d-%m-%Y")
    directory_path = os.path.join(base_directory, 'output', directory_name, today_date)
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    json_file_path = os.path.join(directory_path, f'{mod}.json')

    print(f"Scraping data for {directory_name}...")

    if not os.path.exists(json_file_path) or flag_force:
        function_mod = website[f'function_{mod}']
        print(f"{Colors.GREEN} Get {mod}: {Colors.RESET}:")
        print(f"{Colors.GREEN}Processing {website['url']}...{Colors.RESET}")
        scrape_website(function_mod, mod, website['url'], stop_event)

        print(f"{Colors.CYAN}json file path is : {json_file_path} {Colors.RESET}")

        if os.path.exists(json_file_path):
            with open(json_file_path, "r") as json_file:
                data = json.load(json_file)
            print(f"{Colors.CYAN}json data: {data} {Colors.RESET}")
            print(f"{Colors.CYAN} Generating Excel file for {directory_name}...{Colors.RESET}")
            generate_excel_from_json(data, mod, json_file_path)


def scrape_website(function_mod, mod, website_url, stop_event):
    company_data = function_mod(stop_event)
    if mod == "ads":
        print(f"{Colors.CYAN}Saving ads data for {website_url}...{Colors.RESET}")
        save_ads_data(company_data, website_url, stop_event)
    # if mod == "whitepaper":
    #     save_whitepaper_data(company_data, website_url, mod, stop_event)

def save_ads_data(company_data, website_url, stop_event):
    print(f"{Fore.LIGHTMAGENTA_EX}save_ads_data: {Style.RESET_ALL}")
    base_directory = get_app_data_directory("AdScraper")
    name = get_directory_name_from_url(website_url)
    today_date = datetime.now().strftime("%d-%m-%Y")
    directory_path = os.path.join(base_directory, 'output', name, today_date)

    print(f"{Fore.LIGHTMAGENTA_EX}directory_path: {directory_path} {Style.RESET_ALL}")
    os.makedirs(directory_path, exist_ok=True)
    json_file_path = os.path.join(directory_path, "ads.json")
    print(f"{Fore.LIGHTMAGENTA_EX}json_file_path: {json_file_path} {Style.RESET_ALL}")

    # Initialize existing_data as an empty dictionary
    existing_data = {}

    # Try to read existing data if file exists and is not empty
    if os.path.exists(json_file_path) and os.path.getsize(json_file_path) > 0:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                print(f"{Fore.RED}Error reading {json_file_path}. File might be corrupted or not properly formatted.{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}No existing data found or file is empty. Starting fresh.{Style.RESET_ALL}")

    print(f"{Fore.LIGHTMAGENTA_EX}company_data: {company_data}{Style.RESET_ALL}")

    # Merge existing data with new data and remove duplicates
    for company, ads in company_data.items():
        if company in existing_data:
            existing_ads_set = {json.dumps(ad, sort_keys=True) for ad in existing_data[company]}
            new_ads_filtered = [ad for ad in ads if json.dumps(ad, sort_keys=True) not in existing_ads_set]
            existing_data[company].extend(new_ads_filtered)
        else:
            existing_data[company] = ads

    # Write merged data back to the JSON file
    with open(json_file_path, "w", encoding='utf-8') as file:
        json.dump(existing_data, file, indent=4, ensure_ascii=False)

    if stop_event.is_set():
        print("Operation cancelled. Saving partial data...")
    else:
        print(f"Data for {name} saved successfully.")