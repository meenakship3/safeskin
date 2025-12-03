-- Safeskin Database Schema
-- Migration 001: Initial schema creation

-- Create products table
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    nykaa_product_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    category VARCHAR(100),
    url TEXT NOT NULL,
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for products
CREATE INDEX idx_products_name ON products USING GIN (to_tsvector('english', name));
CREATE INDEX idx_products_nykaa_id ON products (nykaa_product_id);
CREATE INDEX idx_products_category ON products (category);

-- Create ingredients table
CREATE TABLE ingredients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL,
    is_comedogenic BOOLEAN NOT NULL DEFAULT FALSE,
    common_names TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for ingredients
CREATE INDEX idx_ingredients_name ON ingredients (LOWER(name));
CREATE INDEX idx_ingredients_comedogenic ON ingredients (is_comedogenic);

-- Create product_ingredients junction table
CREATE TABLE product_ingredients (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    ingredient_id INTEGER NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    position INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id, ingredient_id)
);

-- Create indexes for product_ingredients
CREATE INDEX idx_product_ingredients_product ON product_ingredients (product_id);
CREATE INDEX idx_product_ingredients_ingredient ON product_ingredients (ingredient_id);

-- Create scrape_logs table
CREATE TABLE scrape_logs (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
    status VARCHAR(20) NOT NULL,
    error_message TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for scrape_logs
CREATE INDEX idx_scrape_logs_scraped_at ON scrape_logs (scraped_at DESC);
CREATE INDEX idx_scrape_logs_status ON scrape_logs (status);