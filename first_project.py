"""Books to scrape - Multi-format scraper and exporter"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import random
import time
from urllib.parse import urljoin
from datetime import datetime
from config2 import CATALOG_URL, BASE_DETAIL, MAX_NUM_PAGES  # Hidden data


start = time.time()


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


def extract_data(url):
    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        response.raise_for_status()
        print(f"Connected ({response.status_code}) → Page processed")
        time.sleep(random.uniform(1, 2))

        soup = BeautifulSoup(response.text, 'lxml')
        books = soup.select('article.product_pod')
        data = []

        for book in books:
            title = book.h3.a.get('title', 'untitled')

            price_tag = book.select_one('.price_color')
            clean_price = price_tag.text.strip().replace(
                '\u00a0', '').replace('Â', '') if price_tag else 'no price'

            availability_tag = book.select_one('.availability')
            availability = availability_tag.get_text(
                strip=True) if availability_tag else 'Not available'

            img_tag = book.select_one('img')

            image_url = urljoin(BASE_DETAIL, img_tag['src']) if img_tag and img_tag.get(
                'src') else 'no image'

            relative_link = book.h3.a.get('href')
            detail_url = urljoin(url, relative_link)

            try:
                detail = requests.get(
                    detail_url, headers=get_headers(), timeout=10)
                detail.raise_for_status()
                time.sleep(random.uniform(1, 2))

                detail_soup = BeautifulSoup(detail.text, 'lxml')
                breadcrumb = detail_soup.select('ul.breadcrumb li a')
                genre = breadcrumb[2].get_text(strip=True) if len(
                    breadcrumb) > 2 else 'no genre'
            except requests.exceptions.RequestException as e:
                print(f"❌ Failed to access detail: {detail_url}")
                print(f"   Reason: {e}")
                genre = 'no genre'

            data.append({
                'Title': title,
                'Price': clean_price,
                'Availability': availability,
                'Image_url': image_url,
                'Genre': genre
            })

        return data

    except requests.exceptions.RequestException as e:
        print(f"Error accessing the page: {e}")
        return []


def extract_all_pages():
    total_data = []
    page = 1

    while page <= MAX_NUM_PAGES:
        url = CATALOG_URL.format(page)
        books = extract_data(url)

        if not books:
            print(f"\n🛑 Scraping finished. Pages processed: {page - 1}")
            break

        print(f"✅ Page {page}: {len(books)} books found.")
        total_data.extend(books)
        page += 1
        time.sleep(random.uniform(1, 2))

    return total_data


def export_data(data):
    if not data:
        print("No data to export.")
        return

    df = pd.DataFrame(data)
    sorted_df = df.sort_values(by='Genre')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    sorted_df.to_csv(f'books_{timestamp}.csv',
                     index=False, sep=';', encoding='utf-8-sig')
    sorted_df.to_excel(f'books_{timestamp}.xlsx',
                       index=False, engine='openpyxl')
    sorted_df.to_json(f'books_{timestamp}.json',
                      orient='records', indent=4, force_ascii=False)

    with open('books.html', 'w', encoding='utf-8') as f:
        f.write(sorted_df.style
                .set_table_styles([
                    {'selector': 'th', 'props': [
                        ('background-color', '#2E75B6'), ('color', 'white')]},
                    {'selector': 'td', 'props': [('text-align', 'center')]}
                ])
                .hide(axis='index')
                .to_html())

    print("✅ Data exported: CSV, Excel, JSON, and HTML.")


if __name__ == "__main__":
    print("📘 Starting full catalog scraping...\n")
    data = extract_all_pages()
    export_data(data)

    for _ in range(1000000):
        pass

    end = time.time()
    print(f"Execution time: {end - start:.2f} seconds")
