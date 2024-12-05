import json
import os

class DataWriter:
    @staticmethod
    def save_to_json(products, query):
        output_dir = "scraped_data"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{query}.json")
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump([product.__dict__ for product in products], f, ensure_ascii=False, indent=4)
            print(f"Data for '{query}' saved to {output_file}")
        except IOError as e:
            print(f"Error saving data for '{query}': {e}")
