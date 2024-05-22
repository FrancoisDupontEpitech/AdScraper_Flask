from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
import requests
from websites.utils.colors import Colors
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from playwright.async_api import async_playwright
import tldextract
import asyncio
from datetime import date

def ads_for_itrnews(stop_event):
    print(f"{Colors.YELLOW}ads_for_itrnews{Colors.RESET}")
    return asyncio.run(ads_for_itrnews_2(stop_event))

async def ads_for_itrnews_2(stop_event):
    company_data = {}
    url = "https://itrnews.com/"
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
            '//*[@id="revive-0-1"]/a',
            '//*[@id="revive-0-2"]/a',
            '//*[@id="revive-0-3"]/a',
        ]

        for xpath_ad in xpath_ads:
            if stop_event.is_set():
                break
            try:
                await page.wait_for_selector(xpath_ad, state='visible', timeout=5000)
                print("Ad element found, attempting to click...")

                initial_pages = browser_context.pages
                await page.click(xpath_ad, timeout=5000)
                await asyncio.sleep(5)
                current_pages = browser_context.pages

                if len(current_pages) > len(initial_pages):
                    new_tab = current_pages[-1]
                    await new_tab.wait_for_load_state()
                    final_url = new_tab.url
                    print(f"{Colors.GREEN}Scraping: {Colors.RESET}", final_url)
                    company_name = extract_company_info(final_url)
                    formatted_date = date.today().strftime('%d/%m/%Y')
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

    return company_data


def whitepaper_for_itrnews(stop_event, reload_times=5, minimum_unique_ads=3):
    print(f"{Colors.YELLOW}whitepaper_for_itrnews{Colors.RESET}")
    url = "https://itrnews.com/"

    # Configure Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    # Launch headless Chrome browser
    driver = webdriver.Chrome(options=chrome_options)

    unique_ads = set()
    company_data = {}

    try:
        for _ in range(reload_times):
            if stop_event.is_set():
                print("Operation cancelled.")
                break

            driver.get(url)
            wait = WebDriverWait(driver, 10)
            ads_links = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="revive-0-0"]/a')))

            for ads_link in ads_links:
                link_url = ads_link.get_attribute('href')
                final_url = fetch_final_url(link_url)
                if final_url:
                    print(f"{Colors.GREEN}Scraping: {Colors.RESET}", final_url)
                    company_name = extract_company_info(final_url)

                    # Check if the ad (based on company name or URL) is unique
                    if company_name not in unique_ads:
                        unique_ads.add(company_name)
                        if company_name not in company_data:
                            company_data[company_name] = []
                        company_data[company_name].append({
                            "date": "Not available",  # Placeholder for date if you add it later
                            "link": final_url,
                            "company": company_name
                        })

            # Check if we have reached the minimum unique ads requirement
            if len(unique_ads) >= minimum_unique_ads:
                break

            # Optionally, add a short delay here if needed to mimic human browsing patterns

    finally:
        driver.quit()
        print(company_data)

    return company_data


def fetch_final_url(initial_url):
    """Follow redirects to fetch the final URL."""
    try:
        response = requests.get(initial_url, timeout=10)
        return response.url
    except requests.RequestException as e:
        print(f"Error fetching URL {initial_url}: {e}")
        return None

def extract_company_info(final_url):
    """Extract the second-level domain (SLD) as the company name from the final URL."""
    extracted = tldextract.extract(final_url)
    company_name = extracted.domain
    print(f"DEBUG 1 Company name: {company_name}")
    return company_name