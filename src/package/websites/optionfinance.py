import requests
from bs4 import BeautifulSoup
import re
from websites.utils.colors import Colors
from websites.utils.save_partial_data import save_partial_data
from websites.utils.group_by_company_name import group_by_company_name
from playwright.async_api import async_playwright
import tldextract
import asyncio
from datetime import date

def whitepaper_for_optionfinance(stop_event):
    print(f"{Colors.YELLOW}whitepaper_for_optionfinance{Colors.RESET}")
    return {}

def ads_for_optionfinance(stop_event):
    print(f"{Colors.YELLOW}ads_for_optionfinance{Colors.RESET}")
    return asyncio.run(ads_for_optionfinance_2(stop_event))

async def ads_for_optionfinance_2(stop_event):
    company_data = {}
    url = "https://www.optionfinance.fr"
    ad_found = False

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security'])
        browser_context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = await browser_context.new_page()
        await page.goto(url)

        try:
            print("Page loaded")
            await page.click('//*[@id="sd-cmp"]/div[2]/div/div/div/div/div/div/div[2]/div[2]/button[2]', timeout=5000)
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
            '//*[@id="sas_1-99155"]/a',
            '//*[@id="sas_1-99149"]/a',
            '//*[@id="sas_1-99149_iframe"]',
            '//*[@id="sas_1-99150"]/a',
        ]

        for xpath_ad in xpath_ads:
            if stop_event.is_set():
                break
            try:
                await page.wait_for_selector(xpath_ad, state='visible', timeout=5000)
                print("Ad element found, attempting to click...")
                ad_found = True

                initial_pages = browser_context.pages

                await page.click(xpath_ad)
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

    if not ad_found:  # If no ads were found
        raise TimeoutError("No ads found within the specified timeout")


    print(f"DEBUG 3 Company data: {company_data}")
    return company_data

def extract_company_info(final_url):
    """Extract the second-level domain (SLD) as the company name from the final URL."""
    extracted = tldextract.extract(final_url)
    company_name = extracted.domain
    return company_name