from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from websites.utils.colors import Colors
import time
from datetime import date

def ads_for_linfocr(stop_event):
    print(f"{Colors.YELLOW}ads_for_linfocr{Colors.RESET}")
    return {}

def whitepaper_for_linfocr(stop_event):
    print(f"{Colors.YELLOW}whitepaper_for_linfocr{Colors.RESET}")
    driver = setup_driver()
    try:
        driver.get("https://www.linfocr.com/livres-blancs-info-cr.html")
        auto_scroll(driver)  # Scroll to load all elements

        links = find_links_by_xpath(driver)

        for link in links:
            print(link)
    finally:
        driver.quit()
    return {}


def setup_driver():
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    return driver

def auto_scroll(driver):
    # Scroll to the bottom of the page
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def find_links_by_xpath(driver):
    xpath1 = '//*[@id="t3-content"]/div[3]/div/div/article/div/div[2]/section/p[3]/a'
    xpath2 = '//*[@id="t3-content"]/div[3]/div/div/article/div/div[2]/section/p/span/a'

    elements_xpath1 = driver.find_elements(By.XPATH, xpath1)
    elements_xpath2 = driver.find_elements(By.XPATH, xpath2)

    links = [element.get_attribute('href') for element in elements_xpath1]
    links.extend(element.get_attribute('href') for element in elements_xpath2)

    return links
