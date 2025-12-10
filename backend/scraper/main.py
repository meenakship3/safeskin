import csv
from datetime import datetime
from config import setup_driver
from product_scraper import ProductScraper
from url_scraper import URLCollector
import os
from dotenv import load_dotenv
import sys

# Add parent directory to path to access database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.models import (
    Database,
    ProductModel,
    IngredientModel,
    ProductIngredientModel,
)

load_dotenv()


def save_urls_to_csv(urls, filename="product_urls.csv"):
    """Save collected URLs to CSV file with pending status"""
    existing_urls = set()
    try:
        with open(filename, "r") as f:
            reader = csv.DictReader(f)
            existing_urls = {row["url"] for row in reader}
    except FileNotFoundError:
        pass

    new_urls = [url for url in urls if url not in existing_urls]

    mode = "a" if existing_urls else "w"
    with open(filename, mode, newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["url", "status", "scraped_at", "error_message"]
        )
        if not existing_urls:
            writer.writeheader()

        for url in new_urls:
            writer.writerow(
                {"url": url, "status": "pending", "scraped_at": "", "error_message": ""}
            )
    print(f"Saved {len(new_urls)} new URLs to {filename}")
    print(f"Skipped {len(urls) - len(new_urls)} duplicate URLs")


def update_url_status(url, status, error=None):
    """Update status in CSV file"""
    rows = []
    with open("product_urls.csv", "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for row in rows:
        if row["url"] == url:
            row["status"] = status
            row["scraped_at"] = (
                datetime.now().isoformat() if status == "scraped" else ""
            )
            row["error_message"] = error or ""

    with open("product_urls.csv", "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["url", "status", "scraped_at", "error_message"]
        )
        writer.writeheader()
        writer.writerows(rows)


def scrape_pending_urls(include_failed=False):
    """
    Scrape URLs from CSV based on status.

    Args:
        include_failed: If True, also retry failed URLs. Default False (only pending).
    """
    driver = setup_driver()
    scraper = ProductScraper(driver)

    # connect to db
    db_params = {
        "host": os.getenv("DB_HOST"),
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "port": os.getenv("DB_PORT"),
    }

    database = Database(db_params)
    database.connect()

    # instantiate models
    product_model = ProductModel(database)
    ingredient_model = IngredientModel(database)
    product_ingredient_model = ProductIngredientModel(database)

    with open("product_urls.csv", "r") as f:
        reader = csv.DictReader(f)
        if include_failed:
            urls_to_scrape = [
                row for row in reader if row["status"] in ("pending", "failed")
            ]
        else:
            urls_to_scrape = [row for row in reader if row["status"] == "pending"]

    print(f"Found {len(urls_to_scrape)} URLs to scrape")
    if include_failed:
        failed_count = sum(1 for row in urls_to_scrape if row["status"] == "failed")
        print(f"  - {failed_count} failed (retrying)")
        print(f"  - {len(urls_to_scrape) - failed_count} pending")

    for i, row in enumerate(urls_to_scrape, 1):
        url = row["url"]

        try:
            print(f"[{i}/{len(urls_to_scrape)}] Scraping: {url}")

            driver.get(url)
            product_data = scraper.scrape_product(url)

            product_id = product_model.create(
                product_data["product_id"],
                product_data["name"],
                product_data["category"],
                url,
                product_data["image_url"],
            )

            if product_data["ingredients"]:
                for position, ingredient_name in enumerate(product_data["ingredients"]):
                    ingredient_id = ingredient_model.create_or_get(ingredient_name)
                    product_ingredient_model.link(product_id, ingredient_id, position)

            database.conn.commit()
            update_url_status(url, "scraped")
            print(f"Success: {product_data['name']}")

        except Exception as e:
            print(f"Error: {e}")
            database.conn.rollback()
            update_url_status(url, "failed")

    database.close()
    driver.quit()


def main():
    driver = setup_driver()
    collector = URLCollector(driver)

    urls = collector.collect_all_product_urls(
        "https://www.nykaa.com/makeup/face/c/13?ptype=lst&id=13&root=nav_2&dir=desc&order=popularity",
        max_pages=27,
    )

    print(f"Total URLs collected: {len(urls)}")
    save_urls_to_csv(urls)
    driver.quit()

    scrape_pending_urls()


if __name__ == "__main__":
    main()
