import asyncio
import random
from playwright.async_api import async_playwright
from websites.utils.colors import Colors
import tldextract
from datetime import date

def whitepaper_for_lesechos(stop_event):
    print(f"{Colors.YELLOW}whitepaper_for_lesechos{Colors.RESET}")
    return {}

def ads_for_lesechos(stop_event):
    print(f"{Colors.YELLOW}ads_for_lemoniteur{Colors.RESET}")
    return asyncio.run(ads_for_lesechos_2(stop_event))

async def ads_for_lesechos_2(stop_event):
    company_data = {}
    url = "https://www.lesechos.fr"
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
            await page.click('//*[@id="didomi-notice-agree-button"]', timeout=5000)
            print("Notifications consent")
        except Exception as e:
            print("Cookie consent window not found or could not be clicked", e)

        xpath_ads = [
            '//*[@id="google_ads_iframe_/144148308/LESECHOS_WEB/HOME/PAVE-1_0"]',
        ]

        try:
            print("Page loaded")
            await page.wait_for_selector(xpath_ad, state='visible', timeout=5000)
            ad_found = True

            initial_pages = browser_context.pages

            await page.click(xpath_ad)
            await asyncio.sleep(5)

            current_pages = browser_context.pages


            for xpath_ad in xpath_ads:
                if stop_event.is_set():
                    break
                if len(current_pages) > len(initial_pages):
                    new_tab = current_pages[-1]
                    await new_tab.wait_for_load_state()
                    final_url = new_tab.url
                    print(f"{Colors.GREEN}Scraping: {Colors.RESET}", final_url)
                    # print(f"{Colors.GREEN}Scraping: {Colors.RESET}", final_url)

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

    return company_data

async def simulate_user_interaction(page):
    # Simulate random mouse movements, hovering, and scrolling
    for _ in range(5):
        await page.mouse.move(random.randint(100, 1000), random.randint(100, 700))
        await page.mouse.down()
        await asyncio.sleep(random.uniform(0.1, 0.5))
        await page.mouse.up()

    await page.evaluate('window.scrollBy(0, window.innerHeight)')
    await asyncio.sleep(2)
    await page.evaluate('window.scrollBy(0, -window.innerHeight)')


def extract_company_info(final_url):
    """Extract the second-level domain (SLD) as the company name from the final URL."""
    extracted = tldextract.extract(final_url)
    company_name = extracted.domain
    return company_name