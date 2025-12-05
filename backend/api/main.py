from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.models import Database, ProductModel

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
