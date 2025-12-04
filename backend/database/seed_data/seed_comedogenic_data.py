"""
Seed comedogenic ingredient data from CSV into database.
Run this script to populate the ingredients table.
"""

import csv
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def seed_comedogenic_ingredients():
    """Load comedogenic ingredient data from CSV into database"""

    # Connect to database
    db_params = {
        "host": os.getenv("DB_HOST"),
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "port": os.getenv("DB_PORT"),
    }

    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    with open("comedogenic_ingredients.csv", "r", encoding="utf-8") as f:
        # Use tab delimiter since Excel saved it that way
        reader = csv.DictReader(f, delimiter="\t")
        rows = list(reader)

    print(f"Loading {len(rows)} ingredients...")

    for row in rows:
        name = row["name"].strip()

        # Handle "yes"/"no" or "true"/"false"
        is_comedogenic_str = row["is_comedogenic"].strip().lower()
        is_comedogenic = is_comedogenic_str in ("yes", "true", "1")

        # Parse common names (pipe-separated)
        common_names_str = row["common_names"].strip()
        common_names = (
            [n.strip() for n in common_names_str.split("|") if n.strip()]
            if common_names_str
            else []
        )

        # Insert ingredient
        cursor.execute(
            """
            INSERT INTO ingredients (name, is_comedogenic, common_names)
            VALUES (%s, %s, %s)
            ON CONFLICT (name) DO UPDATE
            SET is_comedogenic = EXCLUDED.is_comedogenic,
                common_names = EXCLUDED.common_names,
                updated_at = CURRENT_TIMESTAMP
            """,
            (name, is_comedogenic, common_names),
        )

    conn.commit()

    # Get counts
    cursor.execute("SELECT COUNT(*) FROM ingredients WHERE is_comedogenic = TRUE")
    comedogenic_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ingredients WHERE is_comedogenic = FALSE")
    safe_count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    print(f"✓ Successfully loaded {len(rows)} ingredients")
    print(f"  - Comedogenic: {comedogenic_count}")
    print(f"  - Safe: {safe_count}")


if __name__ == "__main__":
    print("=" * 50)
    print("SEEDING COMEDOGENIC INGREDIENT DATA")
    print("=" * 50)
    print()

    seed_comedogenic_ingredients()

    print()
    print("=" * 50)
    print("Done!")
    print("=" * 50)
