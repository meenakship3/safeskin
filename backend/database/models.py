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

    def search_by_name(self, query, limit=20, use_fuzzy=True):
        """
        Smart search with automatic fuzzy fallback

        :param query: Search term
        :param limit: Max results
        :param use_fuzzy: Enable fuzzy matching for typos (default True)
        """
        self.db.cursor.execute(
            """
            SELECT
                id, nykaa_product_id, name, category, image_url,
                ts_rank(to_tsvector('english', name), plainto_tsquery('english', %s)) as relevance
            FROM products
            WHERE to_tsvector('english', name) @@ plainto_tsquery('english', %s)
            ORDER BY relevance DESC, name
            LIMIT %s
        """,
            (query, query, limit),
        )

        results = self.db.cursor.fetchall()

        if not results and use_fuzzy:
            self.db.cursor.execute(
                """
                SELECT
                    id, nykaa_product_id, name, category, image_url,
                    similarity(name, %s) as relevance
                FROM products
                WHERE similarity(name, %s) > 0.3
                ORDER BY relevance DESC, name
                LIMIT %s
            """,
                (query, query, limit),
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
