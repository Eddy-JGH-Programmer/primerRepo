"""EXTRACTING POPULATION-CONTINENT TABLE DATA"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import random
import time
from datetime import datetime
from config2 import url_W, output_path
import os

# Start timing
start_time = time.time()

# Get a random header


def get_headers():
    headers_list = [
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/115.0.0.0 Safari/537.36",
         "Accept-Language": "es-ES,es;q=0.9,en-US;q=0.8"},
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
         "Accept-Language": "en-US,en;q=0.9"},
        {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/537.36",
         "Accept-Language": "es-ES,es;q=0.9"},
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/115.0.0.0 Safari/537.36 Edg/110.0.1587.57",
         "Accept-Language": "en-US,en;q=0.9"},
    ]
    return random.choice(headers_list)

# Extract all tables and export in 4 formats


def extract_tables(url, destination_folder):
    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        response.raise_for_status()
        print(f"Connected ({response.status_code}) → Page processed")
        time.sleep(random.uniform(1, 2))

        # Extract tables using pandas
        tables = pd.read_html(response.text)
        print(f"📊 Found {len(tables)} tables.")

        os.makedirs(destination_folder, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")

        for i, df in enumerate(tables):
            base_name = f"table_{i+1}_{timestamp}"

            csv_path = os.path.join(destination_folder, base_name + ".csv")
            excel_path = os.path.join(destination_folder, base_name + ".xlsx")
            json_path = os.path.join(destination_folder, base_name + ".json")
            html_path = os.path.join(destination_folder, base_name + ".html")

            df.to_csv(csv_path, index=False, encoding="utf-8-sig")
            df.to_excel(excel_path, index=False)
            df.to_json(json_path, orient="records",
                       indent=2, force_ascii=False)
            df.to_html(html_path, index=False)

            print(
                f"✅ Exported table {i+1} in:\n📄 {csv_path}\n📊 {excel_path}\n🧾 {json_path}\n🌐 {html_path}\n")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing the page: {e}")
    except ValueError:
        print("⚠️ No valid tables found on the page.")


# Run
if __name__ == "__main__":
    print("📘 Starting table scraping...\n")
    extract_tables(url_W, output_path)
    end_time = time.time()
    print(f"⏱️ Execution time: {end_time - start_time:.2f} seconds")
