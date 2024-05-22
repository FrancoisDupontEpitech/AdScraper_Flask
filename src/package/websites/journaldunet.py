import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from websites.utils.colors import Colors
from playwright.async_api import async_playwright
import tldextract
import asyncio
from datetime import date

def ads_for_journaldunet(stop_event):
    print(f"{Colors.YELLOW}ads_for_journaldunet{Colors.RESET}")
    return asyncio.run(ads_for_journaldunet_2(stop_event))

async def ads_for_journaldunet_2(stop_event):
    company_data = {}
    url = "https://www.journaldunet.com"
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
            iframe_element = await page.wait_for_selector('//*[@id="appconsent"]/iframe')
            iframe_content = await iframe_element.content_frame()
            button_locator = iframe_content.locator('xpath=/html/body/div/div/div/div/div/aside/section/button[2]')
            await button_locator.wait_for(state="visible")
            await button_locator.click()
            print("Notifications consent clicked")
        except Exception as e:
            print("Cookie consent window not found or could not be clicked:", e)

        await asyncio.sleep(5)

        xpath_ads = [
            '//*[@id="hbv-custom-render"]',
            '//*[@id="google_ads_iframe_/31695825/journaldunet/webmobile_tablette_nos/tablet_fr_journaldunet_divers_home_homesite_mban_atf_c_0__container__"]',
            '//*[@id="sublime-iframe-container"]/div/div/iframe',
            '//*[@id="ba_right"]',

            '//*[@id="jSidebarSticky"]/div[2]/div/aside[2]',

            '//*[@id="google_ads_iframe_/31695825/journaldunet/webmobile_tablette_nos/tablet_fr_journaldunet_divers_home_homesite_mban_atf_c_0"]',
            '//*[@id="google_ads_iframe_/31695825/journaldunet/web_desktop_nos/desktop_fr_journaldunet_divers_home_homesite_mban_atf_c_0"]',
            '//*[@id="google_ads_iframe_/31695825/journaldunet/web_desktop_nos/desktop_fr_journaldunet_divers_home_homesite_mban_atf_r_4"]',
            '//*[@id="google_ads_iframe_/31695825/journaldunet/web_desktop_nos/desktop_fr_journaldunet_divers_home_homesite_special_atf_c_0"]',
        ]

        for xpath_ad in xpath_ads:
            if stop_event.is_set():
                break
            try:
                await page.wait_for_selector(xpath_ad, state='visible', timeout=5000)
                print(f"xpath ads found = {xpath_ad}")
                print("Ad element found, attempting to click...")

                initial_pages = browser_context.pages

                print("clicking on ad")
                await page.click(xpath_ad, timeout=5000)
                await asyncio.sleep(5)
                current_pages = browser_context.pages

                if len(current_pages) > len(initial_pages):
                    new_tab = current_pages[-1]
                    final_url = new_tab.url  # Directly get the URL of the new tab
                    print(f"{Colors.GREEN}Scraping: {Colors.RESET}", final_url)
                    company_name = extract_company_info(final_url)
                    formatted_date = date.today().strftime('%d/%m/%Y')
                    if company_name:
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

def extract_company_info(final_url):
    """Extract the second-level domain (SLD) as the company name from the final URL."""
    extracted = tldextract.extract(final_url)
    company_name = extracted.domain
    return company_name

def whitepaper_for_journaldunet(stop_event):
    print(f"{Colors.YELLOW}whitepaper_for_journaldunet{Colors.RESET}")
    base_url = "https://www.journaldunet.com"
    whitepaper_url = "https://www.journaldunet.com/livres-blancs/"
    response = requests.get(whitepaper_url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    containers = soup.find_all("div", class_="ccmcss_align_c")
    aggregated_company_data = {}  # This will collect data from all containers

    for container in containers:
        if stop_event and stop_event.is_set():
            print("Operation cancelled.")
            break
        links = container.find_all('a')

        for link in links:
            if stop_event and stop_event.is_set():
                print("Operation cancelled.")
                break
            href = link.get('href')
            full_url = urljoin(base_url, href)
            print(f"{Colors.GREEN}Scraping: {Colors.RESET}", full_url)
            # Get company data for each URL
            company_data = redirect_to_each_whitepapers(full_url, stop_event)
            # Aggregate company_data
            for key, value in company_data.items():
                if key in aggregated_company_data:
                    aggregated_company_data[key].extend(value)
                else:
                    aggregated_company_data[key] = value
    return aggregated_company_data

def redirect_to_each_whitepapers(full_url, stop_event):
    base_url = "https://www.journaldunet.com"  # Define base_url again for clarity, though it could be passed as a parameter
    company_data = {}

    response = requests.get(full_url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    containers = soup.find_all("div", class_="grid_last")

    for container in containers:
        if stop_event and stop_event.is_set():
            print("Operation cancelled.")
            break

        whitepaper_link_element = container.find("a", href=True)
        if whitepaper_link_element:
            whitepaper_link = urljoin(base_url, whitepaper_link_element['href'])  # Make the link absolute
        else:
            whitepaper_link = None  # Or keep as full_url if you prefer to always have a link

        company_name_element = container.find("span", class_="bu_wb_title1")
        company_name = company_name_element.get_text().strip() if company_name_element else "Unknown Company"
        company_key = company_name  # Ensure uniqueness as needed

        if company_key not in company_data:
            company_data[company_key] = []

        company_data[company_key].append({
            "date": None,
            "link": whitepaper_link if whitepaper_link else full_url,  # Use the absolute link
            "company": company_name
        })

    return company_data


# Assuming stop_event is a threading.Event object or similar; if not using multithreading, pass None or adjust the code
