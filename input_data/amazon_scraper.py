# import requests
# from bs4 import BeautifulSoup
# import random
# import time
# from datetime import datetime
# from .data_model import Product

# class AmazonScraper:
#     def __init__(self, base_url="https://www.amazon.com/s"):
#         self.base_url = base_url
#         self.headers = {
#             "User-Agent": random.choice([
#                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#                 "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#             ]),
#             "Accept-Language": "en-US,en;q=0.9",  # Simulate real browser language preference
#             "Accept-Encoding": "gzip, deflate, br",  # Simulate real browser encoding
#             "Connection": "keep-alive",  # Browser keeps connection alive
#             "Upgrade-Insecure-Requests": "1",  # Simulate browser request
#             "TE": "Trailers",
#             "Referer": "https://www.amazon.com/",  # Simulate a referrer
#             "DNT": "1",  # Do Not Track
# }

#     def fetch_page(self, query, page_num):
#         url = f"{self.base_url}?k={query}&page={page_num}"
#         print(f"Fetching URL: {url}")
#         try:
#             response = requests.get(url, headers=self.headers)
#             response.raise_for_status()
#             page_content = response.text
#             print(page_content[:500])  # Print the first 500 characters of the page
#             return page_content
#         except requests.RequestException as e:
#             print(f"Error fetching page {page_num} for query '{query}': {e}")
#             return None



#     def parse_product_details(self, page_content):
#         soup = BeautifulSoup(page_content, 'html.parser')
#         products = []

#         for product_div in soup.find_all('div', {'data-asin': True}):
#             try:
#                 # Get the title, safely handling None values
#                 title = product_div.find('span', {'class': 'a-text-normal'})
#                 title = title.get_text() if title else "N/A"

#                 # Get the price, safely handling None values
#                 price = product_div.find('span', {'class': 'a-price-whole'})
#                 price = price.get_text() if price else "N/A"

#                 # Get the image URL, safely handling None values
#                 image_url = product_div.find('img', {'class': 's-image'})
#                 image_url = image_url['src'] if image_url else "N/A"

#                 # Get the total reviews, safely handling None values
#                 total_reviews = product_div.find('span', {'class': 'a-size-base'})
#                 total_reviews = total_reviews.get_text() if total_reviews else "N/A"

#                 # Create Product object
#                 product = Product(
#                     title=title,
#                     price=price,
#                     image_url=image_url,
#                     total_reviews=total_reviews,
#                     scrape_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                     creation_timestamp=datetime.now().timestamp(),
#                     update_timestamp=datetime.now().timestamp()
#                 )
#                 products.append(product)

#             except AttributeError as e:
#                 print(f"Error while parsing product: {e}")
#                 continue  # Skip products that might not have all the data fields

#         return products


#     def scrape_query(self, query, num_pages=20):
#         all_products = []
#         for page_num in range(1, num_pages + 1):
#             page_content = self.fetch_page(query, page_num)
#             if page_content:
#                 products = self.parse_product_details(page_content)
#                 all_products.extend(products)
#                 time.sleep(random.uniform(1, 3))  # Sleep to avoid being blocked
#         return all_products
import requests
from bs4 import BeautifulSoup
import random
import time
from datetime import datetime
from .data_model import Product
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class AmazonScraper:
    def __init__(self, base_url="https://www.amazon.com/s", proxies=None):
        self.base_url = base_url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/115.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "TE": "Trailers",
            "Referer": "https://www.amazon.com/",
            "DNT": "1",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # Updated retry initialization: use allowed_methods instead of method_whitelist
        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        self.proxies = proxies

    def fetch_page(self, query, page_num):
        url = f"{self.base_url}?k={query}&page={page_num}"
        print(f"Fetching URL: {url}")
        try:
            # If using proxy rotation
            if self.proxies:
                proxy = random.choice(self.proxies)
                response = self.session.get(
                    url,
                    proxies={"http": proxy, "https": proxy},
                    timeout=10
                )
            else:
                response = self.session.get(url, timeout=10)
            
            response.raise_for_status()
            page_content = response.text
            
            return page_content
        except requests.RequestException as e:
            print(f"Error fetching page {page_num} for query '{query}': {e}")
            return None

    def parse_product_details(self, page_content):
        soup = BeautifulSoup(page_content, 'html.parser')
        products = []

        # Improved selector to ensure correct product containers
        for product_div in soup.find_all('div', {'data-asin': True, 'data-component-type': 's-search-result'}):
            try:
                
                title = product_div.find('span', {'class': 'a-text-normal'})
                title = title.get_text().strip() if title else "N/A"

                
                price_whole = product_div.find('span', {'class': 'a-price-whole'})
                price_fraction = product_div.find('span', {'class': 'a-price-fraction'})
                if price_whole and price_fraction:
                    price = f"{price_whole.get_text().strip()}.{price_fraction.get_text().strip()}"
                elif price_whole:
                    price = price_whole.get_text().strip()
                else:
                    price = "N/A"

                
                image_tag = product_div.find('img', {'class': 's-image'})
                image_url = image_tag['src'] if image_tag else "N/A"

                
                rating = product_div.find('span', {'class': 'a-icon-alt'})
                rating = rating.get_text().strip() if rating else "N/A"

                
                total_reviews = product_div.find('span', {'class': 'a-size-base'})
                total_reviews = total_reviews.get_text().strip() if total_reviews else "N/A"

                
                product_link = product_div.find('a', {'class': 'a-link-normal', 'href': True})
                product_url = f"https://www.amazon.com{product_link['href']}" if product_link else "N/A"

                
                availability = "N/A"

                
                product = Product(
                    title=title,
                    price=price,
                    image_url=image_url,
                    rating=rating,
                    total_reviews=total_reviews,
                    product_url=product_url,
                    availability=availability,
                    scrape_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    creation_timestamp=datetime.now().timestamp(),
                    update_timestamp=datetime.now().timestamp()
                )
                products.append(product)

            except AttributeError as e:
                print(f"Error while parsing product: {e}")
                continue  # Skip products that might not have all the data fields

        return products

    def scrape_query(self, query, num_pages=20):
        all_products = []
        for page_num in range(1, num_pages + 1):
            page_content = self.fetch_page(query, page_num)
            if page_content:
                products = self.parse_product_details(page_content)
                all_products.extend(products)
                # Random sleep between 2 to 5 seconds to mimic human behavior
                time.sleep(random.uniform(2, 5))
            else:
                print(f"Skipping page {page_num} due to fetch error.")
        return all_products
