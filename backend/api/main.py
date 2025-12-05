from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import sys
import re
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.models import Database, ProductModel
from scraper.product_scraper import ProductScraper
from scraper.config import setup_driver

load_dotenv()

ip_address = os.getenv("HOTSPOT_IP_ADDRESS")

app = FastAPI(
    title="Safeskin API",
    description="API for checking comedogenicity of cosmetic products",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        f"http://{ip_address}:3000",  # Mobile testing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db_connection():
    db_params = {
        "host": os.getenv("DB_HOST"),
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "port": os.getenv("DB_PORT"),
    }
    db = Database(db_params)
    db.connect()
    return db


class IngredientResponse(BaseModel):
    """Response model for an ingredient"""

    name: str
    is_comedogenic: bool
    position: Optional[int] = None


class ProductSearchResult(BaseModel):
    """Response model for product search results"""

    id: int
    nykaa_product_id: str
    name: str
    category: str
    image_url: str
    relevance: float


class ProductDetailResponse(BaseModel):
    """Response model for detailed product information"""

    id: int
    nykaa_product_id: str
    name: str
    category: str
    url: str
    image_url: str
    safety_status: str
    comedogenic_ingredients: List[str]
    comedogenic_count: int
    all_ingredients: List[IngredientResponse]


class HealthResponse(BaseModel):
    """Response model for health check"""

    status: str
    message: str


class ScrapeRequest(BaseModel):
    """Request model for scraping a product URL"""

    url: str


class ScrapeResponse(BaseModel):
    """Response model for scraped product with safety analysis"""

    nykaa_product_id: str
    name: str
    category: str
    url: str
    image_url: str
    safety_status: str
    comedogenic_ingredients: List[str]
    comedogenic_count: int
    all_ingredients: List[IngredientResponse]


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - simple health check"""
    return {
        "status": "ok",
        "message": "Safeskin API is running. Visit /docs for API documentation.",
    }


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        db = get_db_connection()
        db.cursor.execute("SELECT 1")  # Test DB connection
        db.close()
        return {"status": "ok", "message": "API and database are healthy"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Database connection failed: {str(e)}"
        )


@app.get("/api/products/search", response_model=List[ProductSearchResult])
async def search_products(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
):
    """Search for products by name"""
    db = get_db_connection()
    product_model = ProductModel(db)

    try:
        results = product_model.search_by_name(q, limit=limit, use_fuzzy=True)
        db.close()
        return results
    except Exception as e:
        db.close()
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/api/products/{product_id}", response_model=ProductDetailResponse)
async def get_product(product_id: int):
    """Get detailed product information with safety analysis"""
    db = get_db_connection()
    product_model = ProductModel(db)

    try:
        result = product_model.get_product_with_safety_analysis(product_id)
        db.close()

        if not result:
            raise HTTPException(status_code=404, detail="Product not found")

        return result
    except HTTPException:
        db.close()
        raise
    except Exception as e:
        db.close()
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch product: {str(e)}"
        )


@app.post("/api/products/scrape", response_model=ScrapeResponse)
async def scrape_product(request: ScrapeRequest):
    """Scrape a Nykaa product URL and analyze ingredients in real-time"""
    db = get_db_connection()
    product_model = ProductModel(db)
    driver = None

    try:
        # Extract product ID from URL
        match = re.search(r'/p/(\d+)', request.url)
        if not match:
            db.close()
            raise HTTPException(status_code=400, detail="Invalid Nykaa URL")

        nykaa_product_id = match.group(1)

        # CHECK CACHE FIRST: Query database for existing product by nykaa_product_id
        db.cursor.execute(
            "SELECT id FROM products WHERE nykaa_product_id = %s",
            (nykaa_product_id,)
        )
        cached_row = db.cursor.fetchone()

        if cached_row:
            # Found in cache - return analysis from database
            cached_product = product_model.get_product_with_safety_analysis(cached_row[0])
            db.close()
            return cached_product

        # NOT IN CACHE: Scrape the product
        driver = setup_driver()
        scraper = ProductScraper(driver)

        # Navigate to URL and scrape the product
        driver.get(request.url)

        # Add a small delay to ensure page JavaScript has loaded
        import time
        time.sleep(3)

        scraped_data = scraper.scrape_product(request.url)

        if not scraped_data or not scraped_data.get("ingredients"):
            if driver:
                driver.quit()
            db.close()
            raise HTTPException(
                status_code=404,
                detail="Could not extract product data or ingredients from URL",
            )

        # Get all comedogenic ingredients from database
        db.cursor.execute(
            "SELECT name FROM ingredients WHERE is_comedogenic = TRUE"
        )
        comedogenic_list = [row[0].lower() for row in db.cursor.fetchall()]

        # Analyze scraped ingredients
        comedogenic_ingredients = []
        all_ingredients = []

        for position, ing_name in enumerate(scraped_data["ingredients"], start=1):
            # Clean the ingredient name for matching
            clean_name = ing_name.lower()
            clean_name = (
                clean_name.replace("[+/-", "")
                .replace("]", "")
                .replace("(", "")
                .replace(")", "")
            )

            # Check if any comedogenic ingredient matches
            is_comedogenic = False
            for comedogenic_name in comedogenic_list:
                if comedogenic_name in clean_name or clean_name in comedogenic_name:
                    is_comedogenic = True
                    if ing_name not in comedogenic_ingredients:
                        comedogenic_ingredients.append(ing_name)
                    break

            all_ingredients.append(
                {"name": ing_name, "is_comedogenic": is_comedogenic, "position": position}
            )

        # Determine safety status
        if comedogenic_ingredients:
            safety_status = "unsafe"
        else:
            safety_status = "safe"

        # SAVE TO DATABASE (cache for future requests)
        from database.models import IngredientModel, ProductIngredientModel

        ingredient_model = IngredientModel(db)
        product_ingredient_model = ProductIngredientModel(db)

        # Create product record
        product_id = product_model.create(
            scraped_data["product_id"],
            scraped_data["name"],
            scraped_data["category"],
            request.url,
            scraped_data["image_url"]
        )

        # Create ingredient records and link to product
        if scraped_data["ingredients"]:
            for position, ingredient_name in enumerate(scraped_data["ingredients"], start=1):
                ingredient_id = ingredient_model.create_or_get(ingredient_name)
                product_ingredient_model.link(product_id, ingredient_id, position)

        db.conn.commit()

        # Close driver and database
        if driver:
            driver.quit()
        db.close()

        return {
            "nykaa_product_id": scraped_data["product_id"],
            "name": scraped_data["name"],
            "category": scraped_data["category"],
            "url": request.url,
            "image_url": scraped_data["image_url"],
            "safety_status": safety_status,
            "comedogenic_ingredients": comedogenic_ingredients,
            "comedogenic_count": len(comedogenic_ingredients),
            "all_ingredients": all_ingredients,
        }
    except HTTPException:
        if driver:
            driver.quit()
        db.close()
        raise
    except Exception as e:
        import traceback
        print(f"Error in scrape_product: {str(e)}")
        print(traceback.format_exc())
        if driver:
            driver.quit()
        db.close()
        raise HTTPException(status_code=500, detail=f"Failed to scrape product: {str(e)}")
