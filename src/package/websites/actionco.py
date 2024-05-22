import requests
from bs4 import BeautifulSoup
import re
from websites.utils.colors import Colors
from websites.utils.save_partial_data import save_partial_data
from websites.utils.group_by_company_name import group_by_company_name
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import random
from datetime import date


def whitepaper_for_actionco(stop_event):
    print(f"{Colors.YELLOW}whitepaper_for_actionco{Colors.RESET}")
    whitepaper_url = "https://www.actionco.fr/LivreBlanc/"
    return load_all_articles(whitepaper_url, stop_event)

def ads_for_actionco(stop_event):
    print(f"{Colors.YELLOW}ads_for_actionco{Colors.RESET}")
    return {}

def load_all_articles(url, stop_event):
    options = Options()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36")
    options.add_argument("--headless")  # Run in headless mode, optional
    options.add_argument('--no-sandbox')  # Bypass OS security model, required on Linux if you're not root
    options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    service = Service(executable_path=r"C:\Users\FrançoisDUPONT\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    driver.get(url)
    sleep(random.randint(2, 5))
    try:
        # Wait for the cookies popup to appear and accept it
        accept_button = driver.find_element(By.XPATH, "//*[contains(text(), 'Accepter & Fermer')]")
        accept_button.click()
        print("Cookies accepted.")
    except Exception as e:
        print(f"Could not find or click the cookies acceptance button: {e}")

    while True:
        if stop_event.is_set():
            print("Operation cancelled.")
            break
        try:
            load_more_button = driver.find_element(By.XPATH, "//a[@onclick='getArticles()']")
            driver.execute_script("arguments[0].click();", load_more_button)
            sleep(2)  # Adjust the sleep time based on your network speed
        except NoSuchElementException:
            print("No more articles to load.")
            break

    # Now that all articles are loaded, you can proceed to scrape them
    articles = driver.find_elements(By.TAG_NAME, "article")
    print("Loop over Articles:")
    # company_data = loop_over_website(articles, stop_event, driver)

    driver.quit()
    print("Driver closed.")
    company_data = {}
    return company_data

def loop_over_website(articles, stop_event, driver):
    company_data = {}
    base_url = "https://www.actionco.fr"
    for article_element in articles:  # Limit to first 5 articles for example
        if stop_event.is_set():
            print("Operation cancelled.")
            break
        # Adjust the way you extract href from the article_element
        try:
            href = article_element.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
            src = href if href.startswith('http') else f"{base_url}{href}"
            print(f"{Colors.GREEN}Scraping: {Colors.RESET}", src)
            # Adjust the get_info_after_redirect function call if necessary
            info = get_info_after_redirect(src)
            if info:
                group_by_company_name(company_data, info)
                save_partial_data(company_data, "actionco", "whitepaper")
            else:
                print(f"{Colors.RED}Failed to retrieve information from the redirected page.{Colors.RESET}")
        except NoSuchElementException:
            print(f"{Colors.RED}Link not found in the article.{Colors.RESET}")
    return company_data



def get_info_after_redirect(url):
    response = requests.get(url)
    html_content = response.text
    date_match = re.search(r"'publicationDate': '(\d{4}_\d{2}_\d{2})'", html_content)
    company_match = re.search(r"'author': '([^']+)'", html_content)
    date = date_match.group(1) if date_match else None
    company = company_match.group(1) if company_match else None
    formatted_date = date.today().strftime('%d/%m/%Y')

    return {
        "date": formatted_date,
        "link": url,
        "company": company
    }

