from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from input_data.amazon_scraper import AmazonScraper
from input_data.data_writer import DataWriter
import json
import os
from typing import List

# Initialize FastAPI app
app = FastAPI()

# Create the scraper instance
scraper = AmazonScraper()

# Endpoint to scrape a specific queryfrom fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse

app = FastAPI()

# Define the endpoint to start scraping in the background
@app.post("/scrape")
async def scrape_query(background_tasks: BackgroundTasks):
    """
    Endpoint to start scraping for the queries listed in user_queries.json.
    It runs the scraping task in the background.
    """
    # Add the scrape_and_save function to be executed in the background
    background_tasks.add_task(scrape_and_save)
    
    return JSONResponse(content={"message": "Scraping started for all queries in user_queries.json."}, status_code=202)


# Background task to handle scraping and saving
 # Assuming you have a Product class defined

def scrape_and_save():
    # Initialize scraper
    scraper = AmazonScraper()

    # Load the queries from 'user_queries.json'
    with open("scraper/user_queries.json", "r") as f:
            data = json.load(f)
            print(data)
    try:
            queries = data
    except FileNotFoundError:
        queries = []
        print("user_queries.json not found. No queries to scrape.")
        return

    # Print message indicating the start of scraping for all queries
    print("Scraping started for all queries in user_queries.json.")

    all_scraped_data = {}

    # Iterate over all the queries and scrape data
    for query in queries:
        print(f"Scraping for query: {query}")
        
        try:
            # Scrape 5 pages for each query
            all_products = scraper.scrape_query(query, num_pages=20)
            
            # Convert Product objects to dictionaries
            product_data = [product.__dict__ for product in all_products]
            
            # Save the scraped data for the current query
            all_scraped_data[query] = product_data

            # Optional: Add a random delay to avoid triggering anti-scraping mechanisms
            # time.sleep(random.uniform(1, 3))

        except Exception as e:
            print(f"Error scraping query {query}: {e}")
            continue

    # Load existing data from the file if it exists
    try:
        with open("user_queries.json", "r") as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = {}

    # Add the newly scraped data to the existing data
    existing_data.update(all_scraped_data)

    # Write the updated data back to 'user_queries.json'
    try:
        with open("scraped_data/{query}.json.json", "w") as f:
            json.dump(existing_data, f, indent=4)
        print("Scraping completed and saved.")
    except Exception as e:
        print(f"Error saving data: {e}")



# Endpoint to get the scraped data for a specific query
@app.get("/data/{query}", response_model=List[dict])
async def get_scraped_data(query: str):
    """
    Endpoint to retrieve the scraped product data for a specific query.
    """
    file_path = f"scraped_data/{query}.json"
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    else:
        return JSONResponse(content={"message": "Data not available for this query"}, status_code=404)
