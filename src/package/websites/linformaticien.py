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

def ads_for_linformaticien(stop_event):
    print(f"{Colors.YELLOW}ads_for_linformaticien{Colors.RESET}")
    return asyncio.run(ads_for_linformaticien_2(stop_event))

async def ads_for_linformaticien_2(stop_event):
    company_data = {}
    url = "https://www.linformaticien.fr"
    ad_found = False

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security'])
        browser_context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await browser_context.new_page()
        await page.goto(url)


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
            '//*[@id="t3-content"]/div[3]/div[2]/div/div[6]/div[1]/a',
            '//*[@id="sas-clickMap3_12139334"]',
            '//*[@id="sas-clickMap11_12139334"]',
            '//*[@id="sas-clickMap22_12139349"]',
            '//*[@id="sas_100972"]/a',
            '//*[@id="sas_i_12801"]',
            '//*[@id="revive-0-1"]/a',
            '//*[@id="revive-0-2"]/a',
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

    if not ad_found:
        raise TimeoutError("No ads found within the specified timeout")

    return company_data

def extract_company_info(final_url):
    """Extract the second-level domain (SLD) as the company name from the final URL."""
    extracted = tldextract.extract(final_url)
    company_name = extracted.domain
    return company_name

def whitepaper_for_linformaticien(stop_event):
    print(f"{Colors.YELLOW}whitepaper_for_informaticien{Colors.RESET}")
    whitepaper_url = "https://www.linformaticien.com/livres-blancs.html"
    page_nb = 1
    articles = get_url_code_linformaticien(whitepaper_url, page_nb)
    return loop_over_linformaticien(articles, stop_event)

def get_url_code_linformaticien(whitepaper_url, page_number):
    url = whitepaper_url
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    articles = soup.find_all('article')
    return articles

def loop_over_linformaticien(articles, stop_event):
    company_data = {}
    base_url = "https://www.linformaticien.com"
    progress = 0
    for index, article in enumerate(articles[:5]):
        if stop_event.is_set():
            print("Operation cancelled.")
            break
        article_intro = article.find('section', class_='article-intro clearfix')
        if article_intro:
            links = article_intro.find_all('a')
            if links:
                last_link = links[-1]
                if last_link.has_attr('href'):
                    href = last_link['href']
                    src = href if href.startswith('http') else base_url + href
                    print(f"{Colors.GREEN}Scraping: {Colors.RESET}", src)
                    info = get_info_after_redirect_linformaticien(src)
                    if info:
                        group_by_company_name(company_data, info)
                        save_partial_data(company_data, "linformaticien")
                    else:
                        print(f"{Colors.RED}Failed to retrieve information from the redirected page.{Colors.RESET}")
                else:
                    print(f"{Colors.RED}No href attribute found in the last link.{Colors.RESET}")
            else:
                print(f"{Colors.RED}No links found in the article intro section.{Colors.RESET}")
        else:
            print(f"{Colors.RED}Article intro section not found{Colors.RESET}.")
    return company_data

def get_info_after_redirect_linformaticien(url):
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    date = None
    link = url
    company = None

    main_content = soup.find("div", class_="t3-content-main")
    if main_content:
        images = main_content.find_all("img")
        for img in images:
            if "logo_linformaticien.png" not in img['src']:
                alt_text = img.get('alt', '')
                company_match = re.search(r"LB couv (\w+)", alt_text)
                if not company_match:
                    company_match = re.search(r"/images/(\w+)/", img['src'])

                if company_match:
                    company = company_match.group(1)
                    break

    return {
        "date": date,
        "link": link,
        "company": company
    }