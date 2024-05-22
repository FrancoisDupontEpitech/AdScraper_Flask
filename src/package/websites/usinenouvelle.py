import requests
from bs4 import BeautifulSoup
from websites.utils.colors import Colors
from websites.utils.save_partial_data import save_partial_data
from websites.utils.group_by_company_name import group_by_company_name
from playwright.async_api import async_playwright, TimeoutError
from urllib.parse import urlparse
import asyncio
from datetime import date

def ads_for_usinenouvelle(stop_event):
    print(f"{Colors.YELLOW}ads_for_usinenouvelle{Colors.RESET}")
    return asyncio.run(ads_for_usinenouvelle_2(stop_event))

async def ads_for_usinenouvelle_2(stop_event):
    company_data = {}
    url = "https://www.usinenouvelle.com/"
    ad_found = False

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
            await page.click('//*[@id="cmpargustestagree1"]', timeout=5000)
            print("Notifications consent")
        except Exception as e:
            print("Cookie consent window not found or could not be clicked", e)

        # Scroll down the page to trigger loading of dynamic content
        last_height = await page.evaluate("document.body.scrollHeight")
        while True:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)  # Wait for page to load
            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            if stop_event.is_set():
                break

        xpath_ads = [
            '//*[@id="google_ads_iframe_/21799741328/un/hp_0"]',
            '/html/body/div[5]/a',

            # '//*[@id="pave_1"]',
            # '//*[@id="google_ads_iframe_/21799741328/un/hp_4"]',
            # '//*[@id="pave_2"]',
            # '//*[@id="banner_2"]',
        ]

        for xpath_ad in xpath_ads:
            try:
                ad_element = await page.wait_for_selector(xpath_ad, state='visible', timeout=5000)
                print("Ad element found, attempting to click...")

                ad_found = True
                initial_pages = browser_context.pages

                try:
                    print(f"Clicking ad for the xpath {xpath_ad}...")
                    await ad_element.click(timeout=5000)
                    print("Ad clicked, waiting for redirection...")
                    await asyncio.sleep(5)
                except TimeoutError:
                    print(f"Timeout exceeded while trying to click ad element {xpath_ad}. Skipping...")
                    continue

                current_pages = browser_context.pages

                # After clicking the first ad and waiting for the new tab to open
                if len(current_pages) > len(initial_pages):
                    new_tab = current_pages[-1]
                    print(f"New tab detected with URL: {new_tab.url}")
                    await new_tab.wait_for_load_state('domcontentloaded')
                    print("New tab loaded")
                    ad_url = new_tab.url
                    company_name = get_company_name_from_url(ad_url)  # Use the new function to get the company name
                    today = date.today()

                    # Assume "undefined" for the date, as specified
                    ad_entry = {
                        'date': today,
                        'company': company_name,
                        'link': ad_url
                    }

                    company_key = company_name.lower()
                    if company_key not in company_data:
                        company_data[company_key] = []
                    company_data[company_key].append(ad_entry)

                    print(f"Added {company_name} to the company data")
                    await new_tab.close()
            except Exception as e:
                print("Ad element not found or no redirection occurred", e)

        await asyncio.sleep(2)
        await browser.close()

    if not ad_found:  # If no ads were found
        raise TimeoutError("No ads found within the specified timeout")

    return company_data



def get_company_name_from_url(url):
    parsed_url = urlparse(url)
    domain_name = parsed_url.netloc
    # Optionally, remove 'www.' if present
    company_name = domain_name.replace("www.", "").split('.')[0]  # Keeps only the first part of the domain
    return company_name




def whitepaper_for_usinenouvelle(stop_event):
    print(f"{Colors.YELLOW}whitepaper_for_usinenouvelle{Colors.RESET}")
    base_url = "https://www.usinenouvelle.com/nos-webinars/"
    start_page = 1
    end_page = 9
    company_data = fetch_webinars(start_page, end_page, base_url, stop_event)
    return company_data

def fetch_webinars(start_page, end_page, base_url, stop_event):
    company_data = {}  # Changed from list to dict

    for page_num in range(start_page, end_page + 1):
        if stop_event.is_set():
            break
        page_url = f"{base_url}{page_num}"
        print(f"{Colors.GREEN}Scraping page: {page_url}{Colors.RESET}")

        webinars = fetch_webinar_details(page_url, stop_event)

        for webinar in webinars:
            company_key = webinar['company'].lower()  # Normalize company name to lowercase
            if company_key not in company_data:
                company_data[company_key] = []
            company_data[company_key].append(webinar)

    return company_data

def fetch_webinar_details(webinar_url, stop_event):
    response = requests.get(webinar_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    webinar_cards = soup.find_all('div', class_='webinarCard')

    webinars = []

    for card in webinar_cards:
        if stop_event.is_set():
            break

        # Extracting the date
        date_tag = card.find('p', class_='txtDiffuser')
        date = date_tag.text.strip() if date_tag else date.today().strftime('%d/%m/%Y')

        # Extracting the company name
        company_name_tag = card.find('span', class_='txtProposerPar__colored')
        company_name = company_name_tag.text.strip() if company_name_tag else "Unknown Company"

        # Extracting the link
        link_tag = card.find('a', class_='webinarCard__contentLink')
        link = "https://www.usinenouvelle.com" + link_tag['href'] if link_tag else None

        webinars.append({
            'date': date,
            'company': company_name,
            'link': link
        })

    return webinars
