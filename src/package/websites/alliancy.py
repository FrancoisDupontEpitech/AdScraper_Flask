import requests
from bs4 import BeautifulSoup
import re
from websites.utils.colors import Colors
from websites.utils.save_partial_data import save_partial_data
from websites.utils.group_by_company_name import group_by_company_name
from urllib.parse import urlparse
from datetime import date

def ads_for_alliancy(stop_event):
    print(f"{Colors.YELLOW}whitepaper_for_alliancy{Colors.RESET}")
    return {}

def whitepaper_for_alliancy(stop_event):
    print(f"{Colors.YELLOW}ads_for_alliancy{Colors.RESET}")
    url = "https://www.alliancy.fr/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Adjust this line to correctly target the parent container of all articles
    guides_container = soup.find("div", class_="slide-to-guides")

    # Now find all child divs with the class `slide-to-guide guide-information` within the parent container
    articles = guides_container.find_all("div", class_="slide-to-guide guide-information")
    return find_article_link(articles, stop_event)

def find_article_link(articles, stop_event):
    print("Redirecting to article")
    company_data = {}

    for article in articles:
        if stop_event.is_set():
            print("Operation cancelled.")
            break
        a_tag = article.find("a", href=True)  # This finds the first <a> tag with an href attribute
        if a_tag:  # Check if an <a> tag was found
            url = a_tag['href']  # Extract the href attribute value
            print(f"{Colors.GREEN}Scraping: {Colors.RESET}", url)
            company_info = redirect_to_article(url, stop_event)
            if company_info:
                group_by_company_name(company_data, company_info)
    return company_data

def extract_company_name_from_url(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    domain = domain.replace('www.', '')
    company_name = domain.split('.')[0]
    return company_name

def redirect_to_article(article_url, stop_event):
    response = requests.get(article_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    def find_company_data(photo_containers):
        for container in photo_containers:
            if stop_event.is_set():
                print("Operation cancelled.")
                break
            a_tag = container.find("a", href=True)
            if a_tag and a_tag['href'] not in ["https://www.alliancy.fr/", "#stack-1"]:
                company_url = a_tag['href']
                company_name = extract_company_name_from_url(company_url)
                formatted_date = date.today().strftime('%d/%m/%Y')
                return {"date": formatted_date, "company": company_name, "link": company_url}
        return None  # Indicates no valid data was found in the current set of containers.

    # First, try with '.fl-photo-content fl-photo-img-png'
    photo_containers = soup.find_all("div", class_="fl-photo-content fl-photo-img-png")
    company_data = find_company_data(photo_containers)
    if company_data:
        return company_data

    # If no valid data was found, try with '.fl-photo-content fl-photo-img-jpg'
    photo_containers = soup.find_all("div", class_="fl-photo-content fl-photo-img-jpg")
    company_data = find_company_data(photo_containers)
    if company_data:
        return company_data

    # If the function reaches this point, no company URL was found
    print("No company URL found in the article:", article_url)
    return None
