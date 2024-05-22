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

def ads_for_silicon(stop_event):
    print(f"{Colors.YELLOW}ads_for_silicon{Colors.RESET}")
    return asyncio.run(ads_for_silicon_2(stop_event))

async def ads_for_silicon_2(stop_event):
    company_data = {}
    url = "https://www.silicon.fr"
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
            await page.click('//*[@id="didomi-notice-agree-button"]', timeout=2000)
            print("Notifications consent")
        except Exception as e:
            print("Cookie consent window not found or could not be clicked", e)


        try:
            await page.evaluate('''() => {
                document.querySelector('#nl-overlay > div:nth-child(1) > div:nth-child(1)').click();
            }''')
            print("Newsletter popup closed")
        except Exception as e:
            print("Newsletter popup not found or could not be closed", e)



        xpath_ads = [
            '//*[@id="google_ads_iframe_/14668010/silicon/home_2"]',
            '//*[@id="google_ads_iframe_/14668010/silicon/home_3__container__"]',
            '//*[@id="google_ads_iframe_/14668010/silicon/home_5"]',
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


def whitepaper_for_silicon(stop_event):
    print(f"{Colors.YELLOW}whitepaper_for_silicon{Colors.RESET}")
    whitepaper_url = "https://livreblanc.silicon.fr/?utm_source=silicon_structure&utm_medium=email&utm_campaign=newsletter&utm_content=livres_blancs"
    articles = get_url_code(whitepaper_url)
    return loop_over(articles, stop_event)

def get_url_code(webinars_url):
    response = requests.get(webinars_url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    gamma_list = soup.find("div", id="gammaList")
    if gamma_list:
        articles = gamma_list.find_all("li")
        return articles
    else:
        return []


def loop_over(articles, stop_event):
    company_data = {}
    for company in articles:  # Directly iterate over each company <li> element
        if stop_event.is_set():
            print("Operation cancelled.")
            break


        # Extract company name
        company_name_element = company.find("span", class_="name")
        company_name = company_name_element.text.strip() if company_name_element else "Unknown Company"

        # Extract the link
        link_element = company.find("a", href=True)
        full_url = link_element['href'] if link_element else None

        print(f"{Colors.GREEN} Scraping page: {full_url} {Colors.RESET}")

        date_text = "Not available"  # Placeholder for date
        company_key = company_name.lower()

        # Append the extracted data to the company_data dictionary
        if company_key not in company_data:
            company_data[company_key] = []

        company_data[company_key].append({
            "date": date_text,  # Placeholder for date if you add it later
            "link": full_url,
            "company": company_name
        })

    return company_data

def extract_company_info(final_url):
    """Extract the second-level domain (SLD) as the company name from the final URL."""
    extracted = tldextract.extract(final_url)
    company_name = extracted.domain
    return company_name