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

def ads_for_challenges(stop_event):
    print(f"{Colors.YELLOW}ads_for_challenges{Colors.RESET}")
    return asyncio.run(ads_for_challenges_2(stop_event))

def whitepaper_for_challenges(stop_event):
    print(f"{Colors.YELLOW}whitepaper_for_challenges{Colors.RESET}")
    return {}

def extract_company_info(final_url):
    """Extract company name and base URL from the final URL, excluding common subdomains."""
    parsed_url = urlparse(final_url)
    domain_parts = [part for part in parsed_url.netloc.split('.') if part not in ['www', 'wwws', 'co', 'org', 'com']]
    company_name = domain_parts[0] if domain_parts else 'unknown'
    # base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return company_name

# Listen for new popup pages
async def handle_popup(popup, company_data):
    print(f"New tab detected with URL: {popup.url}")

    formatted_date = date.today().strftime('%d/%m/%y')
    # You can handle the popup directly here
    final_url = popup.url
    print(f"{Colors.GREEN}Scraping: {Colors.RESET}", final_url)
    company_name = extract_company_info(final_url)
    if company_name not in company_data:
        company_data[company_name] = []
    company_data[company_name].append({
        "date": formatted_date,
        "link": final_url,
        "company": company_name
    })
    await popup.close()

async def auto_scroll(page):
    print("Starting auto-scrolling...")
    await page.evaluate("""() => {
        return new Promise((resolve, reject) => {
            var totalHeight = 0;
            var distance = 100;
            var timer = setInterval(() => {
                var scrollHeight = document.body.scrollHeight;
                window.scrollBy(0, distance);
                totalHeight += distance;

                if(totalHeight >= scrollHeight){
                    clearInterval(timer);
                    resolve();
                }
            }, 100);
        })
    }""")
    print("Finished auto-scrolling.")


async def ads_for_challenges_2(stop_event):
    company_data = {}
    url = "https://www.challenges.fr/"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security'])
        browser_context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await browser_context.new_page()
        await page.goto(url)

        # Set up the popup event listener here
        page.on('popup', lambda popup: asyncio.create_task(handle_popup(popup, company_data)))

        try:
            print("Page loaded")
            await page.click('//*[@id="didomi-notice-agree-button"]', timeout=5000)
            print("Clicked consent")
        except Exception as e:
            print("Cookie consent window not found or could not be clicked", e)

        # Perform auto-scrolling to ensure all ads are loaded
        await auto_scroll(page)

        xpath_ads = [
            '//*[@id="prisma-banner-header"]',
            '//*[@id="prisma-mpu-top"]',
            '//*[@id="prisma-mpu-middle"]',
            '//*[@id="corps"]/div[2]/div[1]/aside/div',
            '//*[@id="corps"]/div[2]/div[12]/aside',
            '//*[@id="google_ads_iframe_/228216569,205069399/regie-challenges/_Homepage/HP/Banniere-Basse_0__container__"]',
        ]

        await asyncio.sleep(2)

        for xpath_ad in xpath_ads:
            if stop_event.is_set():
                break
            try:
                await page.wait_for_selector(xpath_ad, state='visible', timeout=5000)
                print(f"Ad element found, attempting to click on {xpath_ad}")

                await page.click(xpath_ad)
                await asyncio.sleep(5)

            except Exception as e:
                print("Ad element not found or no redirection occurred", e)

        await asyncio.sleep(2)
        await browser.close()

    return company_data
