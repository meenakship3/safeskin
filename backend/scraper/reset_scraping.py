"""
Reset scraping status and database for a clean rescrape.
Use this when you've made changes to scrapers or database schema.
"""

import csv
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def reset_csv():
    """Mark all URLs in CSV as pending"""
    rows = []
    with open("product_urls.csv", "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for row in rows:
        row["status"] = "pending"
        row["scraped_at"] = ""
        row["error_message"] = ""

    with open("product_urls.csv", "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["url", "status", "scraped_at", "error_message"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"✓ Reset {len(rows)} URLs to pending status")


def clear_database():
    """Truncate all database tables"""
    db_params = {
        "host": os.getenv("DB_HOST"),
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "port": os.getenv("DB_PORT"),
    }

    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Truncate in correct order (child tables first)
        cursor.execute("TRUNCATE TABLE product_ingredients CASCADE;")
        cursor.execute("TRUNCATE TABLE scrape_logs CASCADE;")
        cursor.execute("TRUNCATE TABLE products CASCADE;")
        cursor.execute("TRUNCATE TABLE ingredients CASCADE;")

        conn.commit()
        cursor.close()
        conn.close()

        print("✓ Cleared all database tables")

    except Exception as e:
        print(f"✗ Error clearing database: {e}")


def main():
    print("=" * 50)
    print("RESETTING SCRAPING STATE")
    print("=" * 50)
    print()

    # Ask for confirmation
    response = input(
        "This will:\n"
        "  1. Mark all URLs as pending\n"
        "  2. Delete all data from database\n"
        "\nAre you sure? (yes/no): "
    )

    if response.lower() != "yes":
        print("Aborted.")
        return

    print()
    reset_csv()
    clear_database()
    print()
    print("=" * 50)
    print("Done! Run 'python main.py' to rescrape.")
    print("=" * 50)


if __name__ == "__main__":
    main()
