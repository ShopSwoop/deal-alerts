import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
import csv
import os

# ------------------ CONFIG ------------------
TODAY_CSV = "books_today.csv"
YESTERDAY_CSV = "books_yesterday.csv"
BASE_URL = "http://books.toscrape.com"
# --------------------------------------------

# Step 1: Rotate the CSV files [storage box]
# If today's file exists, rename it to yesterday's file
if os.path.exists(TODAY_CSV):
    if os.path.exists(YESTERDAY_CSV):
        os.remove(YESTERDAY_CSV)  # Delete old yesterday file
    os.rename(TODAY_CSV, YESTERDAY_CSV)  # Today becomes yesterday

# Step 2: Scrape all books from the test bookstore
current_url = BASE_URL
page_number = 1
total_books = 0

# Open today's CSV file [storage box] for writing
with open(TODAY_CSV, "w", newline="", encoding="utf-8") as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["title", "price"])  # Header row (matches price_detector)

    while current_url:
        print(f"--- Page {page_number} ---")
        try:
            response = requests.get(current_url, timeout=10)
            response.encoding = 'utf-8'
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            books = soup.find_all("article", class_="product_pod")

            for book in books:
                try:
                    title = book.h3.a['title']
                    price_text = book.find("p", class_="price_color").text
                    # Clean price: remove £ sign and convert to float
                    price = float(price_text.replace("£", "").replace("Â", ""))
                    print(f"  {title} - £{price}")
                    csv_writer.writerow([title, price])
                    total_books += 1
                except (AttributeError, ValueError) as e:
                    print(f"  [Skipping malformed entry: {e}]")
                    continue

            # Find the "next" button for pagination
            next_button = soup.find("li", class_="next")
            if next_button:
                current_url = urljoin(response.url, next_button.a['href'])
                page_number += 1
                time.sleep(1)  # Be polite to the server
            else:
                current_url = None  # No more pages

        except requests.exceptions.RequestException as e:
            print(f"  Network error: {e}")
            print("  Retrying in 5 seconds...")
            time.sleep(5)
            continue

print(f"\nDone. {total_books} books saved to {TODAY_CSV}")
