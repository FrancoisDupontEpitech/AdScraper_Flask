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

def ads_for_lemoniteur(stop_event):
    print(f"{Colors.YELLOW}ads_for_lemoniteur{Colors.RESET}")
    return asyncio.run(ads_for_lemoniteur_2(stop_event))

async def ads_for_lemoniteur_2(stop_event):
    company_data = {}
    url = "https://www.lemoniteur.fr"
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
            await page.click('//*[@id="cmpargustestagree2"]', timeout=5000)
            print("Notifications consent")
        except Exception as e:
            print("Cookie consent window not found or could not be clicked", e)

        xpath_ads = [
            '//*[@id="google_ads_iframe_/21799741328/lme/hp_0"]',
            '//*[@id="google_ads_iframe_/21799741328/lme/hp_2"]',
            '//*[@id="google_ads_iframe_/21799741328/lme/hp_3"]',
            '//*[@id="google_ads_iframe_/144148308/LESECHOS_WEB/HOME/BANNIERE-HAUTE_0"]',
            '//*[@id="google_ads_iframe_/144148308/LESECHOS_WEB/HOME/PAVE-1_0"]'
            '//*[@id="bnr"]/div/div/div'
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
    print(f"DEBUG 1 Company name: {company_name}")
    return company_name

def whitepaper_for_lemoniteur(stop_event):
    print(f"{Colors.YELLOW}whitepaper_for_lemoniteur{Colors.RESET}")
    base_url = "https://www.lemoniteur.fr/nos-webinars/tous-les-webinars-de-nos-partenaires"
    page = 1
    company_data = {}

    while True:
        if stop_event.is_set():
            print("Operation cancelled.")
            break

        webinars_url = f"{base_url}/{page}"
        print(f"{Colors.GREEN}Scraping: {Colors.RESET}", webinars_url)
        articles = get_url_code(webinars_url)

        # Break the loop if no articles are found
        if not articles:
            print("No more articles to process.")
            break

        # Process the articles and update company_data
        page_data = loop_over_webinars(articles, stop_event)
        for key, value in page_data.items():
            if key not in company_data:
                company_data[key] = []
            company_data[key].extend(value)

        page += 1

    return company_data


def get_url_code(webinars_url):
    response = requests.get(webinars_url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    articles = soup.find_all("div", class_="webinarSliderItem")
    return articles

def loop_over_webinars(articles, stop_event):
    company_data = {}

    full_url = ""

    for article in articles:
        if stop_event.is_set():
            print("Operation cancelled.")
            break

        # Extract the webinar replay link
        replay_button_element = article.find("button", class_="webinarCardV__btn")
        if replay_button_element and replay_button_element.has_attr('onClick'):
            replay_link = replay_button_element['onClick'].split("'")[1]
            full_url = f"https://www.example.com{replay_link}"  # Adjust the base URL as needed

        # Extract the company name
        company_name_element = article.find("b")
        company_name = company_name_element.text.strip() if company_name_element else "Unknown Company"

        # Extract the webinar date
        date_element = article.find("li", text=re.compile(r"\d{1,2} \w+ \d{4} à \d{2}:\d{2}"))
        date_text = date_element.text.strip() if date_element else "Unknown Date"

        # Normalize company name for consistent key usage
        company_key = company_name.lower()

        # Append the extracted data to the company_data dictionary
        if company_key not in company_data:
            company_data[company_key] = []

        company_data[company_key].append({
            "date": date_text,
            "link": full_url,
            "company": company_name
        })

    return company_data

