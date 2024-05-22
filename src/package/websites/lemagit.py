import requests
from bs4 import BeautifulSoup
import re
from websites.utils.colors import Colors
from websites.utils.save_partial_data import save_partial_data
from websites.utils.group_by_company_name import group_by_company_name
from datetime import date

def ads_for_lemagit(stop_event):
    print(f"{Colors.YELLOW}ads_for_lemagit{Colors.RESET}")
    return {}

def whitepaper_for_lemagit(stop_event):
    print(f"{Colors.YELLOW}whitepaper_for_lemagit{Colors.RESET}")
    initial_url = "https://www.lemagit.fr"

    bitpipe_url = get_bitpipe_url(initial_url)
    print(f"Found Bitpipe URL: {bitpipe_url}")
    if bitpipe_url:
        print(f"Found Bitpipe URL: {bitpipe_url}")
        return loop_over_whitepapers(bitpipe_url, stop_event)
    else:
        print("Bitpipe URL not found.")
        return None

def get_bitpipe_url(initial_url):
    response = requests.get(initial_url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    link = soup.find('a', href=True, text="Livres Blancs")
    if link and link['href']:
        return link['href']
    return None

def loop_over_whitepapers(bitpipe_url, stop_event):
    response = requests.get(bitpipe_url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    articles = soup.find_all("div", class_="sponsorInfo")

    company_data = {}

    for article in articles:
        if stop_event.is_set():
            print("Operation cancelled.")
            break

        # Extract the document link
        document_link_element = article.find("a", class_="primaryButton", href=True)
        if document_link_element:
            document_link = document_link_element['href']
            full_url = f"https://www.bitpipe.fr{document_link}" if not document_link.startswith('http') else document_link
            print(f"{Colors.GREEN}Scraping: {Colors.RESET}", full_url)

            # Extract the company name
            company_name_element = article.find_previous_sibling("span", class_="sponsoredBy").find("strong")
            company_name = company_name_element.text.strip() if company_name_element else "Unknown Company"

            # Normalize company name for consistent key usage
            company_key = company_name.lower()

            # Append the extracted data to the company_data dictionary
            if company_key not in company_data:
                company_data[company_key] = []

            formatted_date = date.today().strftime('%d/%m/%Y')

            company_data[company_key].append({
                "date": formatted_date,  # Placeholder for date if you add it later
                "link": full_url,
                "company": company_name
            })

    return company_data
