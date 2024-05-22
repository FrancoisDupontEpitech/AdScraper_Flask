from utils.get_app_data_directory import get_app_data_directory
from websites.utils.colors import Colors
import os

def delete_partial_json_file(directory_name, mode):
    base_directory = get_app_data_directory("AdScraper")
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
