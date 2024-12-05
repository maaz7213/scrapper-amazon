from dataclasses import dataclass

@dataclass
class Product:
    def __init__(self, title, price, image_url, total_reviews, product_url, availability, rating=None,
                 scrape_date=None, creation_timestamp=None, update_timestamp=None):
        self.title = title
        self.price = price
        self.image_url = image_url
        self.total_reviews = total_reviews
        self.product_url = product_url
        self.availability = availability
        self.rating = rating  
        self.scrape_date = scrape_date
        self.creation_timestamp = creation_timestamp
        self.update_timestamp = update_timestamp

    def __repr__(self):
        return f"Product(title={self.title}, price={self.price}, rating={self.rating}, total_reviews={self.total_reviews})"
