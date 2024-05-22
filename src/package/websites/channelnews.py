import requests
from bs4 import BeautifulSoup
import re
from websites.utils.colors import Colors
from websites.utils.save_partial_data import save_partial_data
from websites.utils.group_by_company_name import group_by_company_name
import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urlparse
import tldextract
from datetime import date

def whitepaper_for_channelnews(stop_event):
    print(f"{Colors.YELLOW}whitepaper_for_channelnews{Colors.RESET}")
    return asyncio.run(whitepaper_for_channelnews_2(stop_event))

async def whitepaper_for_channelnews_2(stop_event):
    company_data = {}
    base_url = "https://www.channelnews.fr/fournisseurs/page/"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for page_num in range(1, 11):  # Loop from page 1 to 10
            page_url = f"{base_url}{page_num}"  # Construct the URL for the current page
            page = await browser.new_page()
            await page.goto(page_url)

            for i in range(1, 11):  # Assuming each page has up to 10 articles
                xpath_date = f'//*[@id="content"]/div/div[2]/section/article[{i}]/footer/strong/time'
                xpath_company_1 = f'//*[@id="content"]/div/div[2]/section/article[{i}]/header/div/div/span'
                xpath_company_2 = f'//*[@id="content"]/div/div[2]/section/article[{i}]/header/div/div/ul/li'
                xpath_link_1 = f'//*[@id="content"]/div/div[2]/section/article[{i}]/header/h2/a'
                xpath_link_2 = f'//*[@id="content"]/div/div[2]/section/article[{i}]/header/div/h2/a'

                try:
                    date_text = await page.locator(xpath_date).first.text_content(timeout=1000)
                except Exception as e:
                    date_text = "Date not found"
                    print(f"Page {page_num}, Article {i}, Error retrieving date: {str(e)}")

                try:
                    company_text = await page.locator(xpath_company_1).first.text_content(timeout=1000)
                    if not company_text or company_text in ["DOCUMENTATION", "FOURNISSEURS"]:
                        raise Exception("Invalid company text from first xpath.")
                except:
                    try:
                        company_text = await page.locator(xpath_company_2).first.text_content(timeout=1000)
                    except Exception as e:
                        company_text = "Company not found"
                        print(f"Page {page_num}, Article {i}, Error retrieving company: {str(e)}")

                try:
                    whitepaper_link = await page.locator(xpath_link_1).get_attribute('href', timeout=1000)
                except:
                    try:
                        whitepaper_link = await page.locator(xpath_link_2).get_attribute('href', timeout=1000)
                    except Exception as e:
                        whitepaper_link = "Link not found"
                        print(f"Page {page_num}, Article {i}, Error retrieving link: {str(e)}")

                print(f"Page {page_num}, Article {i}, Date: {date_text.strip()}")
                print(f"Page {page_num}, Article {i}, Company: {company_text.strip()}")
                print(f"Page {page_num}, Article {i}, Link: {whitepaper_link.strip()}")

                if company_text not in company_data:
                    company_data[company_text] = []
                company_data[company_text].append({
                    "date": date_text.strip(),  # Stripping potential whitespace
                    "link": whitepaper_link.strip(),  # Assuming company_text now represents the link for some reason
                    "company": company_text.strip()  # Using whitepaper_link as the company identifier
                })

            await page.close()

        await browser.close()

    return company_data






def ads_for_channelnews(stop_event):
    print(f"{Colors.YELLOW}ads_for_channelnews{Colors.RESET}")
    return asyncio.run(ads_for_channelnews_2(stop_event))

async def ads_for_channelnews_2(stop_event):
    company_data = {}
    url = "https://www.channelnews.fr/"
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
            await page.click('//*[@id="onesignal-slidedown-cancel-button"]', timeout=5000)
            print("Notifications consent")
        except Exception as e:
            print("Cookie consent window not found or could not be clicked", e)

        xpath_ads = [
            '//*[@id="main"]/div/div',
            '//*[@id="sidebar"]/div',
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

                formatted_date = date.today().strftime('%d/%m/%y')

                if len(current_pages) > len(initial_pages):
                    new_tab = current_pages[-1]
                    await new_tab.wait_for_load_state()
                    final_url = new_tab.url
                    print(f"{Colors.GREEN}Scraping: {Colors.RESET}", final_url)
                    company_name = extract_company_info(final_url)
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

    print(f"DEBUG 3 Company data: {company_data}")
    return company_data


def extract_company_info(final_url):
    """Extract the second-level domain (SLD) as the company name from the final URL."""
    extracted = tldextract.extract(final_url)
    company_name = extracted.domain
    print(f"DEBUG 1 Company name: {company_name}")
    return company_name