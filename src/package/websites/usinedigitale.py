import requests
from bs4 import BeautifulSoup
import re
from websites.utils.colors import Colors
from websites.utils.save_partial_data import save_partial_data
from websites.utils.group_by_company_name import group_by_company_name
import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urlparse
from datetime import date

def whitepaper_for_usinedigitale(stop_event):
    print("whitepaper_for_usinedigitale")
    print(f"{Colors.YELLOW}whitepaper_for_usinedigitale{Colors.RESET}")
    return {}

def ads_for_usinedigitale(stop_event):
    print(f"{Colors.YELLOW}ads_for_usinedigitale{Colors.RESET}")
    return asyncio.run(ads_for_usinedigitale_2(stop_event))

def extract_company_info(final_url):
    """Extract company name and base URL from the final URL, excluding common subdomains."""
    parsed_url = urlparse(final_url)
    domain_parts = [part for part in parsed_url.netloc.split('.') if part not in ['www', 'co', 'org', 'com']]
    company_name = domain_parts[0] if domain_parts else 'unknown'
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return company_name, base_url

async def ads_for_usinedigitale_2(stop_event):
    company_data = {}
    url = "https://www.usine-digitale.fr/"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        browser_context = await browser.new_context()
        page = await browser_context.new_page()
        await page.goto(url)

        try:
            print("Page loaded")
            await page.click('//*[@id="didomi-notice-agree-button"]', timeout=5000)
        except Exception as e:
            print("Cookie consent window not found or could not be clicked", e)

        xpath_ads = [
            '//*[@id="bannerArche_1"]',
            '//*[@id="pave_1"]',
            '//*[@id="banner_2"]',
            '//*[@id="pave_2"]',
            '//*[@id="pave_3"]',
        ]

        for xpath_ad in xpath_ads:
            if stop_event.is_set():
                break
            try:
                await page.wait_for_selector(xpath_ad, state='visible', timeout=5000)
                print("Ad element found, attempting to click...")

                initial_pages = browser_context.pages

                await page.click(xpath_ad)
                await asyncio.sleep(5)

                current_pages = browser_context.pages

                if len(current_pages) > len(initial_pages):
                    new_tab = current_pages[-1]
                    await new_tab.wait_for_load_state()
                    final_url = new_tab.url
                    company_name, base_url = extract_company_info(final_url)
                    formatted_date = date.today().strftime('%d/%m/%Y')
                    if company_name not in company_data:
                        company_data[company_name] = []
                    company_data[company_name].append({
                        "date": formatted_date,
                        "link": base_url,
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
