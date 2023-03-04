import json
import urllib
import pickle
import re
import requests
import time
import pandas as pd
from csv import DictReader

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

info_glob = []

url = 'https://www.coach.com/shop/women/handbags/view-all'
headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }

def load_cookies(driver):
    with open("coach-cookies.csv", encoding='utf-8-sig') as f:
        dict_reader = DictReader(f)
        list_of_dicts = list(dict_reader)
    print("Logging all unused cookies...")
    for cookie in list_of_dicts:
        try:
            driver.add_cookie(cookie)
        except:
            pass
    driver.refresh()

def scrollLoop(driver, loop):
    actions = ActionChains(driver)
    for _ in range(loop):
        print("scrolling down...")
        for _ in range(10):
            actions.send_keys(Keys.DOWN).perform()
        exitPopup(driver)

def scrapeProductInfo(driver):
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')

    # Find item name
    name = soup.find("h1", class_="chakra-heading").text

    # Find item price
    price = soup.select(".chakra-text.active-price")[0].text

    # Find item variants (via images, maybe later add name)
    product_images = soup.find_all("img", class_="chakra-image")
    pattern = ".*desktopThumbnail\$"
    img_list = []
    for img in product_images:
        img_src = img.get('src')
        if re.match(pattern, img_src): # maybe include color name
            img_list.append(img_src)
       
    # Check available
    add_to_cart = soup.select("button", class_=".chakra-button.add-to-cart")
    is_available = False
    for add_to_cart_btn in add_to_cart:
        if add_to_cart_btn.text == "I WANT IT": # Beware that these words are hard-coded
            is_available = True
            break
            
    rtn_data = pd.DataFrame(data = {
        'name': name,
        'price': price,
        'is_available': is_available,
        'img_list': [img_list],
    })
    # print(rtn_data)
    return rtn_data

def exitPopup(driver):
    time.sleep(4)
    # print("exiting popup...")
    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()

if __name__ == '__main__':
    # Initialize webpage
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)
    exitPopup(driver)
    export_df = pd.DataFrame(data={'name': ['name'], 'price': ['price'], 'is_available': ['True'], 'img_list': [[]]})

    product_counter = 0
    for _ in range(15):
        # Scan product thumbnails
        product_thumbnails = driver.find_elements(By.CLASS_NAME, 'product-thumbnail')
        print("Length of product thumbnails: " + str(len(product_thumbnails)))

        # Iterate through products and scrape product listing
        while product_counter < len(product_thumbnails):
            print("Counter: " + str(product_counter))
            product = product_thumbnails[product_counter]

            # Open product in a new tab
            action = ActionChains(driver)
            action.key_down(Keys.COMMAND).click(product).key_up(Keys.COMMAND).perform() 
            exitPopup(driver)

            # Switch to new tab (try)
            if len(driver.window_handles) < 2:
                print("WEIRD ERROR: realigning scroll")
                scrollLoop(driver, 1)
                continue
            driver.switch_to.window(driver.window_handles[1])
            exitPopup(driver)

            # Scrape product info
            data = scrapeProductInfo(driver)
            export_df = pd.concat([export_df, data])

            # Exit and switch back to main tab
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            exitPopup(driver)

            product_counter+=1

        export_df.to_csv('test.csv', encoding='utf-8', index=False)
        scrollLoop(driver, 1)
        exitPopup(driver)
    
    time.sleep(5)
