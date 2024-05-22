import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from websites.utils.colors import Colors
from playwright.async_api import async_playwright
import tldextract
import asyncio
from datetime import date

def ads_for_itsocial(stop_event):
    print(f"{Colors.YELLOW}ads_for_itsocial{Colors.RESET}")
    return asyncio.run(ads_for_itsocial_2(stop_event))

async def ads_for_itsocial_2(stop_event):
    company_data = {}
    url = "https://itsocial.fr/"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security'])
        browser_context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await browser_context.new_page()
        await page.goto(url)

        xpath_ads = [
            '//*[@id="td-outer-wrap"]/div[1]/div/div[2]/div/div[2]/div/div/div/a',
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


def whitepaper_for_itsocial(stop_event):
    print(f"{Colors.YELLOW}whitepaper_for_itsocial{Colors.RESET}")
    homepage_url = "https://itsocial.fr/"
    response = requests.get(homepage_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    textwidget_divs = soup.find_all('div', class_='textwidget')
    formatted_date = date.today().strftime('%d/%m/%Y')

    company_data = {}

    for div in textwidget_divs:
        print("Scraping div")
        if stop_event.is_set():
            print("Operation cancelled.")
            break
        link_tags = div.find_all('a', href=True)
        for link_tag in link_tags:
            if stop_event.is_set():
                print("Operation cancelled.")
                break
            initial_link = link_tag['href']
            final_url = fetch_final_url(initial_link)
            if final_url:
                print(f"{Colors.GREEN}Scraping: {Colors.RESET}", final_url)
                company_name = extract_company_info(final_url)
                if company_name not in company_data:
                    company_data[company_name] = []
                company_data[company_name].append({
                    "date": formatted_date,
                    "link": final_url,
                    "company": company_name
                })

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
    return company_name