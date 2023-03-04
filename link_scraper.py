import urllib
import re
import requests
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

url_bag = "https://www.coach.com/products/cara-satchel/CE741.html?frp=CE741%20B4%2FBK" # bag
url_shoe = "https://www.coach.com/products/leah-loafer/CB990.html?frp=CB990%20BLK%20%207.5%20B" # shoe
url_jewlery = "https://www.coach.com/products/quilted-padlock-chain-bracelet/CD834.html?frp=CD834%20GD%2FBKONE" # jewlery
url_clothing = "https://www.coach.com/products/signature-jacquard-denim-bonnie-coat/CG989.html?frp=CG989%20BLC%20%20M%2FL" # clothing

url_clothing_sale = "https://www.coach.com/products/shearling-ski-hoodie/CE896.html?frp=CE896%20LJN%20%20L" # clothing + sale

url_clothing_oos = "https://www.coach.com/products/plaid-shearling-aviator/CF033.html?frp=CF033%20BR%2FCRXS" # clothing + out of stock

headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }

if __name__ == '__main__':
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url_clothing_oos)
    time.sleep(3) # need to sleep for 3s for javascript to load (to check if size is in stock)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')

    # Find item name
    name = soup.find("h1", class_="chakra-heading").text
    print(name)

    # Find item price
    price = soup.select(".chakra-text.active-price")[0].text
    print(price)

    # Find item variants (via images, maybe later add name)
    product_images = soup.find_all("img", class_="chakra-image")
    pattern = ".*desktopSwatchImage\$"
    for img in product_images:
        img_src = img.get('src')
        if re.match(pattern, img_src): # maybe include color name
            print(img_src)

    # Find item sizes - need to find sold out or not
    item_sizes = soup.select(".chakra-button.css-59lkga")
    for item_size in item_sizes:
        print(item_size.text)
        if "allow-disabled" in item_size['class']:
            print("unavailable")
        else:
            print("available")