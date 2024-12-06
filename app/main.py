from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from input_data.amazon_scraper import AmazonScraper
from input_data.data_writer import DataWriter
import json
import os
from typing import List
import time
from fastapi.responses import JSONResponse
app = FastAPI()
scraper = AmazonScraper()

app = FastAPI()
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}



@app.post("/scrape")
async def scrape_query(background_tasks: BackgroundTasks):
    background_tasks.add_task(scrape_and_save)    
    return JSONResponse(content={"message": "Scraping started for all queries in user_queries.json."}, status_code=202)



def scrape_and_save():
    scraper = AmazonScraper()
    try:
        with open("scraper/user_queries.json", "r") as f:
            data = json.load(f)
        queries = data
    except FileNotFoundError:
        queries = []
        print("user_queries.json not found. No queries to scrape.")
        return

    print("Scraping started for all queries in user_queries.json.")

    all_scraped_data = {}
    for query in queries:
        print(f"Scraping for query: {query}")
        
        try:
            all_products = scraper.scrape_query(query, num_pages=5)
            product_data = [product.__dict__ for product in all_products]
            all_scraped_data[query] = product_data
            time.sleep(random.uniform(1, 3))

        except Exception as e:
            print(f"Error scraping query {query}: {e}")
            continue

    os.makedirs("scraped_data", exist_ok=True)
    for query, product_data in all_scraped_data.items():
        file_path = f"scraped_data/{query}.json"
        
        try:
           
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    existing_data = json.load(f)
            else:
                existing_data = {}
            existing_data.update({query: product_data})
            with open(file_path, "w") as f:
                json.dump(existing_data, f, indent=4)
            print(f"Scraping for query '{query}' completed and saved.")
        
        except Exception as e:
            print(f"Error saving data for query {query}: {e}")





@app.get("/data/{query}", response_model=List[dict])
async def get_scraped_data(query: str):
 
    file_path = f"scraped_data/{query}.json"
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    else:
        return JSONResponse(content={"message": "Data not available for this query"}, status_code=404)
