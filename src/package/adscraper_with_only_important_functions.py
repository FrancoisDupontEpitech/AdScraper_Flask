#Flask
# from flask import Flask, request, jsonify, render_template
import threading
import json
from websites import *
from get_new_file import retrieve_json_companies_data
import datetime
import os
import pandas as pd
from utils.get_directory_name_from_url import get_directory_name_from_url


# customtkinter
import glob
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import os
import json
from functools import partial
from utils.colors import Colors
from utils.open_json_in_excel import generate_excel_from_json
from utils.get_directory_name_from_url import get_directory_name_from_url
from websites import *
from get_new_file import retrieve_json_companies_data
import datetime
import webbrowser
import pandas as pd
import xlsxwriter
from datetime import date
from colorama import Fore, Back, Style
import platform
from tkinter import PhotoImage
import subprocess
import sys
from PIL import Image, ImageTk
import time


class CustomTkinterAdScraperApp:
    websites = [
        {"url": "https://www.actionco.fr", "name": "actionco", "function_whitepaper": whitepaper_for_actionco, "function_ads": ads_for_actionco},   # ads KO : problème anti-bot detection
        {"url": "https://www.alliancy.fr", "name": "alliancy", "function_whitepaper": whitepaper_for_alliancy, "function_ads": ads_for_alliancy},   # ads OK
        {"url": "https://www.challenges.fr", "name": "challenges", "function_whitepaper": whitepaper_for_challenges, "function_ads": ads_for_challenges}, # ads OK (parfois problème de click sur les pubs)
        {"url": "https://www.channelnews.fr", "name": "channelnews", "function_whitepaper": whitepaper_for_channelnews, "function_ads": ads_for_channelnews}, # ads OK
        {"url": "https://www.itforbusiness.fr", "name": "itforbusiness", "function_whitepaper": whitepaper_for_itforbusiness, "function_ads": ads_for_itforbusiness}, # whitepaper OK
        {"url": "https://itrnews.com", "name": "itrnews", "function_whitepaper": whitepaper_for_itrnews, "function_ads": ads_for_itrnews}, # whitepaper OK
        {"url": "https://www.itsocial.fr", "name": "itsocial", "function_whitepaper": whitepaper_for_itsocial, "function_ads": ads_for_itsocial}, # whitepaper OK : il faut scroll pour que le js affiche les livres blancs suivant. 1
        {"url": "https://www.journaldunet.com", "name": "journaldunet", "function_whitepaper": whitepaper_for_journaldunet, "function_ads": ads_for_journaldunet}, # whitepaper OK
        {"url": "https://www.lemagit.fr", "name": "lemagit", "function_whitepaper": whitepaper_for_lemagit, "function_ads": ads_for_lemagit},  #  whitepaper OK
        {"url": "https://www.lemoniteur.fr", "name": "lemoniteur", "function_whitepaper": whitepaper_for_lemoniteur, "function_ads": ads_for_lemoniteur}, # whitepaper OK
        {"url": "https://www.lesechos.fr", "name": "lesechos", "function_whitepaper": whitepaper_for_lesechos, "function_ads": ads_for_lesechos}, # ads OK (je get les pubs mais pas toutes, pour l'instant a stock pas dans le json)
        # {"url": "https://www.linfocr.com", "name": "linfocr", "function_whitepaper": whitepaper_for_linfocr, "function_ads": ads_for_linfocr}, # c'est les meme pubs que sur linformaticien.com
        {"url": "https://www.linformaticien.com", "name": "linformaticien", "function_whitepaper": whitepaper_for_linformaticien, "function_ads": ads_for_linformaticien}, # whitepaper OK
        {"url": "https://www.optionfinance.fr", "name": "optionfinance", "function_whitepaper": whitepaper_for_optionfinance, "function_ads": ads_for_optionfinance}, # ads OK
        {"url": "https://www.silicon.fr", "name": "silicon", "function_whitepaper": whitepaper_for_silicon, "function_ads": ads_for_silicon}, # whitepaper OK
        {"url": "https://www.solutions-numeriques.com", "name": "solutions-numeriques", "function_whitepaper": whitepaper_for_solutionsnumeriques, "function_ads": ads_for_solutionsnumeriques}, # whitepaper OK
        {"url": "https://www.usine-digitale.fr", "name": "usine-digitale", "function_whitepaper": whitepaper_for_usinedigitale, "function_ads": ads_for_usinedigitale}, # ads OK
        {"url": "https://www.usinenouvelle.com", "name": "usinenouvelle", "function_whitepaper": whitepaper_for_usinenouvelle, "function_ads": ads_for_usinenouvelle}, # whitepaper OK
    ]

    def run_operation(self):
        """Handles the 'Run' button click event."""
        self.is_scraping_active = True

        mode = self.mode_var.get()
        force = self.force_var.get()
        threading.Thread(target=lambda: self.start_scraping(mode, force), daemon=True).start()

    def start_scraping(self, mode, force):
        """Initiates the scraping process and the loading animation."""
        self.loading = True
        threading.Thread(target=self._scrape_and_process_data, args=(mode, force)).start()

    def _scrape_and_process_data(self, mode, force):
        self.get_company_partnership(mode, force)
        self.get_new_company(mode)

    def get_company_partnership(self, mode, flag_force):
        threads = []
        for website in self.websites:

            if self.website_check_vars[website['url']].get():
                thread = threading.Thread(target=self.scrape_and_process_website,
                                args=(website, mode, flag_force),
                                daemon=True)
                threads.append(thread)
                thread.start()

        for thread in threads:
            thread.join()

    def scrape_and_process_website(self, website, mode, flag_force):
        base_directory = self.get_app_data_directory("AdScraper")
        directory_name = get_directory_name_from_url(website['url'])
        today_date = datetime.datetime.now().strftime("%d-%m-%Y")
        directory_path = os.path.join(base_directory, 'output', directory_name, today_date)
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        json_file_path = os.path.join(directory_path, f'{mode}.json')

        print(f"Scraping data for {directory_name}...")

        if not os.path.exists(json_file_path) or flag_force:
            function_mode = website[f'function_{mode}']
            print(f"{Colors.GREEN} Get {mode}: {Colors.RESET}:")
            print(f"{Colors.GREEN}Processing {website['url']}...{Colors.RESET}")
            self.scrape_website(function_mode, mode, website['url'], self.stop_event)

            print(f"{Colors.CYAN}json file path is : {json_file_path} {Colors.RESET}")

            if os.path.exists(json_file_path):
                with open(json_file_path, "r") as json_file:
                    data = json.load(json_file)
                print(f"{Colors.CYAN}json data: {data} {Colors.RESET}")
                print(f"{Colors.CYAN} Generating Excel file for {directory_name}...{Colors.RESET}")
                generate_excel_from_json(data, mode, json_file_path)
                if not self.stop_event.is_set():
                    print(f"{Colors.CYAN}Deleting partial JSON file for {directory_name}...{Colors.RESET}")
                    self.delete_partial_json_file(directory_name, mode)

    def scrape_website(self, function_mode, mode, website_url, stop_event):
        self.scraping_active[website_url] = True

        company_data = function_mode(stop_event)
        if mode == "ads":
            print(f"{Colors.CYAN}Saving ads data for {website_url}...{Colors.RESET}")
            self.save_ads_data(company_data, website_url, stop_event)
        if mode == "whitepaper":
            self.save_whitepaper_data(company_data, website_url, mode, stop_event)

        self.scraping_active[website_url] = False

    def get_new_company(self, mode):
        print(f"{Colors.CYAN}Getting new companies...{Colors.RESET}")
        all_new_companies = []
        all_companies = []

        print(f"{Colors.CYAN}Retrieving data for each website...{Colors.RESET}")
        for website in self.websites:
            if self.website_check_vars[website['url']].get():
                new_companies_detailed, all_companies_detailed = retrieve_json_companies_data(website['name'], mode)
                all_new_companies.extend(new_companies_detailed)
                all_companies.extend(all_companies_detailed)

        # Nettoyer les données pour chaque liste
        cleaned_new_companies_data = self.clean_companies_data(all_new_companies)
        cleaned_all_companies_data = self.clean_companies_data(all_companies)

        print(f"{Colors.CYAN}Creating and opening Excel file...{Colors.RESET}")

        self.create_and_open_excel(cleaned_new_companies_data, cleaned_all_companies_data, mode)

    def clean_companies_data(self, companies_data):
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

    def create_and_open_excel(self, new_companies_data, all_companies_data, mode):
        self.loading = True
        threading.Thread(target=self._create_and_open_excel_thread, args=(new_companies_data, all_companies_data, mode)).start()

    def _create_and_open_excel_thread(self, new_companies_data, all_companies_data, mode):
        base_directory = self.get_app_data_directory("AdScraper")
        output_directory = os.path.join(base_directory, "output")
        excel_filename = f"{mode}_data.xlsx"
        full_excel_path = os.path.join(output_directory, excel_filename)

        os.makedirs(os.path.dirname(full_excel_path), exist_ok=True)
        try:
            writer = pd.ExcelWriter(full_excel_path, engine='xlsxwriter')
            df_new = pd.DataFrame(new_companies_data)
            df_all = pd.DataFrame(all_companies_data)
            df_new.to_excel(writer, sheet_name='New Companies Last 30D', index=False)
            df_all.to_excel(writer, sheet_name='All Companies', index=False)
            writer.close()

            # Ensure the operation completed, so stop the loading animation
            self.loading = False

            # Update the label with the file path on the GUI thread
            self.root.after(0, lambda: self.file_path_label.configure(text=f"File saved at: {full_excel_path}"))

            # Open the Excel file if no errors occurred
            if os.name == 'nt':
                os.startfile(full_excel_path)
            else:
                webbrowser.open('file://' + full_excel_path)

        except PermissionError as e:
            # Stop the loading animation if an error occurs
            self.loading = False
            self.root.after(0, lambda: self.file_path_label.configure(text=f"PermissionError: {e}. See console for details."))

        except Exception as e:
            # Stop the loading animation if an error occurs
            self.loading = False
            self.root.after(0, lambda: self.file_path_label.configure(text=f"An error occurred: {e}. See console for details."))

    def get_app_data_directory(self, app_name):
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

    def clear_files(self):
        """Clears Excel and JSON files for selected websites."""
        for website in self.websites:
            if self.website_check_vars[website['url']].get():
                directory_name = get_directory_name_from_url(website['url'])
                self.delete_files(directory_name, ['xlsx', 'json'])

    def delete_files(self, directory_name, extensions):
        base_directory = self.get_app_data_directory("AdScraper")
        for extension in extensions:
            pattern = os.path.join(base_directory, 'output', directory_name, f'*.{extension}')
            files = glob.glob(pattern)
            for file_path in files:
                try:
                    os.remove(file_path)
                    print(f"{Colors.CYAN}File {file_path} has been successfully deleted.{Colors.RESET}")
                except Exception as e:
                    print(f"{Colors.RED}Error deleting file {file_path}: {e}{Colors.RESET}")

    def delete_partial_json_file(self, directory_name, mode):
        base_directory = self.get_app_data_directory("AdScraper")
        final_json_path = os.path.join(base_directory, 'output', directory_name, f'{mode}.json')
        partial_json_path = os.path.join(base_directory, 'output', directory_name, f'{mode}_data_partial.json')

        print(f"{Colors.CYAN}mode: {mode}...{Colors.RESET}")
        print(f"{Colors.CYAN}2 Deleting partial JSON file for {partial_json_path}...{Colors.RESET}")
        if os.path.exists(final_json_path) and os.path.exists(partial_json_path):
            print(f"{Colors.CYAN}Deleting partial JSON file for {directory_name}...{Colors.RESET}")
            try:
                print(f"{Colors.CYAN}3 Deleting partial JSON file for {directory_name}...{Colors.RESET}")
                os.remove(partial_json_path)
                print(f"{Colors.CYAN}Partial JSON file {partial_json_path} has been successfully deleted.{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}Error deleting partial JSON file: {e}{Colors.RESET}")

    def save_ads_data(self, company_data, website_url, stop_event):
        print(f"{Fore.LIGHTMAGENTA_EX}save_ads_data: {Style.RESET_ALL}")
        base_directory = self.get_app_data_directory("AdScraper")
        name = get_directory_name_from_url(website_url)
        today_date = datetime.datetime.now().strftime("%d-%m-%Y")
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


    def save_whitepaper_data(self, company_data, website_url, mode, stop_event):
        base_directory = self.get_app_data_directory("AdScraper")
        name = get_directory_name_from_url(website_url)
        today_date = datetime.datetime.now().strftime("%d-%m-%Y")
        directory_path = os.path.join(base_directory, 'output', name, today_date)

        os.makedirs(directory_path, exist_ok=True)

        json_file_path = os.path.join(directory_path, f"{mode}.json")

        with open(json_file_path, "w") as json_file:
            json.dump(company_data, json_file, indent=4)

        if stop_event.is_set():
            print("Operation cancelled. Saving partial data...")
        else:
            print(f"Data for {name} saved successfully.")