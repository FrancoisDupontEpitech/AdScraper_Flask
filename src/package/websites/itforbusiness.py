from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
from websites.utils.colors import Colors
import requests
from playwright.async_api import async_playwright
import tldextract
import asyncio
from datetime import date

def ads_for_itforbusiness(stop_event):
    print(f"{Colors.YELLOW}ads_for_itforbusiness{Colors.RESET}")
    return asyncio.run(ads_for_itforbusiness_2(stop_event))

async def ads_for_itforbusiness_2(stop_event):
    company_data = {}
    url = "https://www.itforbusiness.fr/cloud"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security'])
        browser_context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await browser_context.new_page()
        await page.goto(url)

        try:
            print("Page loaded")
            await page.click('//*[@id="CookieBoxSaveButton"]', timeout=5000)
            print("Notifications consent")
        except Exception as e:
            print("Cookie consent window not found or could not be clicked", e)

        xpath_ads = [
            '//*[@id="revive-0-0"]/a',
            '//*[@id="revive-0-1"]',
            '//*[@id="prisma-mpu-top"]',
        ]

        for xpath_ad in xpath_ads:
            if stop_event.is_set():
                break
            try:
                await page.wait_for_selector(xpath_ad, state='visible', timeout=5000)
                initial_pages = browser_context.pages
                await page.click(xpath_ad, timeout=5000)
                await asyncio.sleep(5)
                current_pages = browser_context.pages

                if len(current_pages) > len(initial_pages):
                    new_tab = current_pages[-1]

                    await new_tab.wait_for_load_state('domcontentloaded')
                    final_url = new_tab.url
                    print(f"{Colors.GREEN}Scraping: {Colors.RESET}", final_url)
                    company_name = extract_company_info(final_url)
                    formatted_date = date.today().strftime('%d/%m/%y')
                    if company_name not in company_data:
                        company_data[company_name] = []
                    company_data[company_name].append({
                        "date": formatted_date,
                        "link": final_url,
                        "company": company_name
                    })
                    await new_tab.close()
                else:
                    print("No new tab detected or the original page was navigated away from.")

            except Exception as e:
                print("Ad element not found or no redirection occurred", e)

        await asyncio.sleep(2)
        await browser.close()

    print(f"DEBUG 3 Company data: {company_data}")
    return company_data


def extract_company_info(final_url):
    """Extract the second-level domain (SLD) as the company name from the final URL."""
    extracted = tldextract.extract(final_url)
    company_name = extracted.domain
    print(f"DEBUG 1 Company name: {company_name}")
    return company_name

def whitepaper_for_itforbusiness(stop_event):
    print(f"{Colors.YELLOW}whitepaper_for_itforbusiness{Colors.RESET}")
    url = "https://www.itforbusiness.fr/"

    # Configure Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    # Launch headless Chrome browser
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    try:
        ads_links = driver.find_elements(By.XPATH, '//ins[@data-revive-zoneid="182"]/a')
        company_data = {}

        for ads_link in ads_links:
            if stop_event.is_set():
                print("Operation cancelled.")
                break
            link_url = ads_link.get_attribute('href')
            final_url = fetch_final_url(link_url)
            if final_url:
                print(f"{Colors.GREEN}Scraping: {Colors.RESET}", final_url)
                company_name = extract_company_info(final_url)
                if company_name not in company_data:
                    company_data[company_name] = []
                company_data[company_name].append({
                    "date": "Not available",
                    "link": final_url,
                    "company": company_name
                })

        print(company_data)
    finally:
        driver.quit()

    return company_data


def fetch_final_url(initial_url):
    """Follow redirects to fetch the final URL."""
    try:
        response = requests.get(initial_url, timeout=10)
        return response.url
    except requests.RequestException as e:
        print(f"Error fetching URL {initial_url}: {e}")
        return None

# def extract_company_info(final_url):
#     """Extract company name and base URL from the final URL, excluding common subdomains."""
#     parsed_url = urlparse(final_url)
#     domain_parts = [part for part in parsed_url.netloc.split('.') if part not in ['www', 'co', 'org']]
#     company_name = domain_parts[0] if domain_parts else 'unknown'
#     base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
#     return company_name, base_url