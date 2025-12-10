import psycopg2


class Database:
    """Database connection manager"""

    def __init__(self, conn_params):
        self.conn_params = conn_params
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = psycopg2.connect(**self.conn_params)
        self.cursor = self.conn.cursor()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()


class ProductModel:
    """CRUD operations for products table"""

    def __init__(self, db):
        self.db = db

    def create(self, nykaa_product_id, name, category, url, image_url):
        """Insert product and return its ID"""
        self.db.cursor.execute(
            """
            INSERT INTO products (nykaa_product_id, name, category, url, image_url)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (nykaa_product_id) DO UPDATE
            SET name = EXCLUDED.name, updated_at = CURRENT_TIMESTAMP
            RETURNING id
            """,
            (nykaa_product_id, name, category, url, image_url),
        )
        return self.db.cursor.fetchone()[0]

    def get_by_id(self, product_id):
        """Get product by ID"""
        self.db.cursor.execute(
            """
            SELECT id, nykaa_product_id, name, category, url, image_url
            FROM products WHERE id = %s
            """,
            (product_id,),
        )
        row = self.db.cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "nykaa_product_id": row[1],
                "name": row[2],
                "category": row[3],
                "url": row[4],
                "image_url": row[5],
            }
        return None

    def search_by_name(self, query, limit=20, offset=0, use_fuzzy=True):
        """
        Search products by name with fuzzy matching for typos

        Uses combined ILIKE + trigram similarity for best results

        :param query: Search term
        :param limit: Max results
        :param offset: Number of results to skip (for pagination)
        :param use_fuzzy: Enable fuzzy matching for typos (default True)
        """
        if use_fuzzy:
            # Combined approach: ILIKE for exact substrings + trigram similarity for typos
            # Lower threshold (0.1) + word_similarity catches more typos like "concelar"
            self.db.cursor.execute(
                """
                SELECT DISTINCT
                    id, nykaa_product_id, name, category, image_url,
                    GREATEST(
                        CASE
                            WHEN LOWER(name) = LOWER(%s) THEN 1.0
                            WHEN LOWER(name) LIKE LOWER(%s) THEN 0.9
                            WHEN LOWER(name) LIKE LOWER(%s) THEN 0.7
                            ELSE 0.0
                        END,
                        similarity(name, %s),
                        word_similarity(%s, name)
                    ) as relevance
                FROM products
                WHERE
                    LOWER(name) LIKE LOWER(%s)
                    OR similarity(name, %s) > 0.1
                    OR word_similarity(%s, name) > 0.1
                ORDER BY relevance DESC, name
                LIMIT %s OFFSET %s
            """,
                (
                    query,
                    query + "%",
                    "%" + query + "%",
                    query,
                    query,
                    "%" + query + "%",
                    query,
                    query,
                    limit,
                    offset,
                ),
            )
        else:
            # Simple ILIKE only
            self.db.cursor.execute(
                """
                SELECT
                    id, nykaa_product_id, name, category, image_url,
                    CASE
                        WHEN LOWER(name) = LOWER(%s) THEN 1.0
                        WHEN LOWER(name) LIKE LOWER(%s) THEN 0.9
                        ELSE 0.5
                    END as relevance
                FROM products
                WHERE LOWER(name) LIKE LOWER(%s)
                ORDER BY relevance DESC, name
                LIMIT %s OFFSET %s
            """,
                (query, query + "%", "%" + query + "%", limit, offset),
            )

        results = self.db.cursor.fetchall()

        return [
            {
                "id": row[0],
                "nykaa_product_id": row[1],
                "name": row[2],
                "category": row[3],
                "image_url": row[4],
                "relevance": float(row[5]),
            }
            for row in results
        ]

    def get_product_with_safety_analysis(self, product_id):
        """
        Get product with comedogenic safety analysis using fuzzy matching.

        Returns product info along with:
        - safety_status: 'safe' or 'unsafe'
        - comedogenic_ingredients: list of problematic ingredients
        - comedogenic_count: number of comedogenic ingredients
        - all_ingredients: complete list of all ingredients with fuzzy-matched comedogenic status
        """
        # Get product basic info
        self.db.cursor.execute(
            """
            SELECT id, nykaa_product_id, name, category, url, image_url
            FROM products
            WHERE id = %s
            """,
            (product_id,),
        )

        product_row = self.db.cursor.fetchone()

        if not product_row:
            return None

        # Get all product ingredients
        self.db.cursor.execute(
            """
            SELECT i.id, i.name, pi.position
            FROM ingredients i
            JOIN product_ingredients pi ON i.id = pi.ingredient_id
            WHERE pi.product_id = %s
            ORDER BY pi.position NULLS LAST, i.name
            """,
            (product_id,),
        )

        product_ingredients = self.db.cursor.fetchall()

        # Get all comedogenic ingredients from the database
        self.db.cursor.execute(
            """
            SELECT name FROM ingredients WHERE is_comedogenic = TRUE
            """
        )
        comedogenic_list = [row[0].lower() for row in self.db.cursor.fetchall()]

        # Fuzzy match: check if any comedogenic ingredient is contained in product ingredient
        comedogenic_ingredients = []
        all_ingredients = []

        for _, ing_name, position in product_ingredients:
            # Clean the ingredient name for matching (remove brackets, CI codes, etc.)
            clean_name = ing_name.lower()
            # Remove common prefixes/suffixes
            clean_name = (
                clean_name.replace("[+/-", "")
                .replace("]", "")
                .replace("(", "")
                .replace(")", "")
            )

            # Check if any comedogenic ingredient matches
            is_comedogenic = False
            for comedogenic_name in comedogenic_list:
                # Check if the comedogenic ingredient is in the product ingredient name
                if comedogenic_name in clean_name or clean_name in comedogenic_name:
                    is_comedogenic = True
                    if ing_name not in comedogenic_ingredients:
                        comedogenic_ingredients.append(ing_name)
                    break

            all_ingredients.append(
                {
                    "name": ing_name,
                    "is_comedogenic": is_comedogenic,
                    "position": position,
                }
            )

        # Determine safety status
        if not all_ingredients:
            # No ingredients found for this product
            safety_status = "unknown"
        elif comedogenic_ingredients:
            # Has comedogenic ingredients
            safety_status = "unsafe"
        else:
            # Has ingredients, none are comedogenic
            safety_status = "safe"

        return {
            "id": product_row[0],
            "nykaa_product_id": product_row[1],
            "name": product_row[2],
            "category": product_row[3],
            "url": product_row[4],
            "image_url": product_row[5],
            "safety_status": safety_status,
            "comedogenic_ingredients": comedogenic_ingredients,
            "comedogenic_count": len(comedogenic_ingredients),
            "all_ingredients": all_ingredients,
        }


class IngredientModel:
    """CRUD operations for ingredients table"""

    def __init__(self, db):
        self.db = db

    def create_or_get(self, name, is_comedogenic=False, common_names=None):
        """Insert or update ingredient, return its ID"""
        self.db.cursor.execute(
            """
            INSERT INTO ingredients (name, is_comedogenic, common_names)
            VALUES (%s, %s, %s)
            ON CONFLICT (name) DO UPDATE
            SET is_comedogenic = EXCLUDED.is_comedogenic,
                common_names = EXCLUDED.common_names,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """,
            (name, is_comedogenic, common_names or []),
        )
        return self.db.cursor.fetchone()[0]

    def get_comedogenic(self):
        self.db.cursor.execute(
            """
            SELECT id, name, common_names
            FROM ingredients
            WHERE is_comedogenic = TRUE
            ORDER BY name
        """
        )
        return [
            {"id": row[0], "name": row[1], "common_names": row[2]}
            for row in self.db.cursor.fetchall()
        ]


class ProductIngredientModel:
    """CRUD operations for product_ingredients junction table"""

    def __init__(self, db):
        self.db = db

    def link(self, product_id, ingredient_id, position):
        self.db.cursor.execute(
            """
            INSERT INTO product_ingredients (product_id, ingredient_id, position)
            VALUES (%s, %s, %s)
            ON CONFLICT (product_id, ingredient_id) DO NOTHING
        """,
            (product_id, ingredient_id, position),
        )

    def get_product_ingredients(self, product_id):
        self.db.cursor.execute(
            """
            SELECT i.id, i.name, i.is_comedogenic, pi.position
            FROM ingredients i
            JOIN product_ingredients pi ON i.id = pi.ingredient_id
            WHERE pi.product_id = %s
            ORDER BY pi.position NULLS LAST, i.name
        """,
            (product_id,),
        )
        return [
            {"id": row[0], "name": row[1], "is_comedogenic": row[2], "position": row[3]}
            for row in self.db.cursor.fetchall()
        ]


class ScrapeLogModel:
    """CRUD operations for scrape_logs table"""

    def __init__(self, db):
        self.db = db

    def log(self, source, status, product_id=None, error_message=None):
        """ "Log scraping activity"""
        self.db.cursor.execute(
            """
            INSERT INTO scrape_logs (source, product_id, status, error_message)
            VALUES (%s, %s, %s, %s)
        """,
            (source, product_id, status, error_message),
        )
