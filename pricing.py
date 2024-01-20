import re
import os

import requests
from bs4 import BeautifulSoup
from scrapingbee import ScrapingBeeClient

def priceFlipkart(url):
    try:
        HEADERS = {
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'),
            'Accept-Language': 'en-US, en;q=0.5'
        }
        id_ = "_30jeq3 _16Jk6d"
        html = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(html.content, "html.parser")
        results_price = soup.find(class_=id_).text[1:]
        result_name = soup.find(class_="B_NuCI").text
        results_image = soup.find(class_="_396cs4").get('src')
        if "," in results_price:
            results_price = results_price.replace(",", "")
        return {"price":int(results_price) , "name":result_name , "images":results_image}
    except Exception as e:
        return f"Error in priceFlipkart: {str(e)}"

def priceAmazon(url):
    client = ScrapingBeeClient(api_key=os.getenv("ScrapingBeeClient_API"))
    response = client.get(
        url,
        params={
            'extract_rules': {
                "name": {
                    "selector": "span[id='productTitle']",
                    "output": "text",
                },
                "price": {
                    "selector": "span[class='a-price aok-align-center reinventPricePriceToPayMargin priceToPay'] > span[aria-hidden='true']",
                    "output": "text",
                },
                "rating": {
                    "selector": "i[class='a-icon a-icon-star a-star-4-5'] > span",
                    "output": "text",
                },
                "description": {
                    "selector": "div[id='productDescription']",
                    "output": "text",
                },
                "full_html": {
                    "selector": "html",
                    "output": "html",
                },
            }
        }
    )
    if response.ok:
        scraped_data = response.json()
        images = re.findall('"hiRes":"(.+?)"', response.json()['full_html'])
    return {"name":scraped_data['name'] , "price":int(scraped_data['price'].split(' ')[1].split(',')[0] +scraped_data['price'].split(' ')[1].split(',')[1]) , "images":images[0]}
