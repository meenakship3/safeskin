# SafeSkin

A full-stack web application that analyzes skincare and cosmetic products to determine if they're safe for acne-prone skin by identifying comedogenic (pore-clogging) ingredients.


## Features

- **Fuzzy Search with pg_trgm** - PostgreSQL trigram-based search handles typos and partial matches for intuitive product discovery
- **Safety Analysis Engine** - Analyzes ingredients against 300+ known comedogenic substances with detailed explanations of problematic ingredients
- **Real-time Web Scraping** - Selenium-based scraper extracts product data with manual link fallback when products aren't found in database
- **Intelligent Caching** - PostgreSQL-based caching layer prevents redundant scraping and speeds up repeat queries
- **RESTful API** - 5 FastAPI endpoints with automatic OpenAPI documentation, Pydantic validation, and CORS configuration
- **Paginated Search Results** - Server-side pagination with relevance scoring for efficient browsing of products
- **Dynamic Product Pages** - React 19 server components render ingredient breakdowns with visual safety indicators


## Tech Stack

- **Next.js 15** - App Router with server actions
- **React 19** - Modern UI development with TypeScript
- **Tailwind CSS** - Utility-first styling framework
- **FastAPI** - High-performance Python API framework with 5 endpoints
- **PostgreSQL 14+** - Relational database with pg_trgm extension
- **Selenium WebDriver** - Automated browser for web scraping
- **psycopg2** - PostgreSQL adapter for Python
- **Pydantic** - Data validation and settings management


## Screenshots
<div align="center">
  <img src="https://github.com/user-attachments/assets/3a55ecca-f54a-4ce7-894f-008a06b7288c" width="30%" style="margin: 0 10px;">
  <img src="https://github.com/user-attachments/assets/46d466eb-cf52-478d-8959-7dde3bc5a329" width="30%" style="margin: 0 10px;">
  <img src="https://github.com/user-attachments/assets/4bdea04b-a18c-467c-87a6-d030bcae2537" width="30%" style="margin: 0 10px;"> 
</div>



## Setup & Installation

### Prerequisites

- Node.js 18+
- Python 3.13+
- PostgreSQL 14+

### Database Setup

```bash
# Create database and enable extensions
createdb safeskin_db
psql safeskin_db -c "CREATE EXTENSION pg_trgm;"

# Run migrations
psql safeskin_db < backend/database/migrations/001_initial_schema.sql
```

### Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Add .env file with database credentials
echo "DB_HOST=localhost
DB_PORT=5432
DB_NAME=safeskin_db
DB_USER=your_user
DB_PASSWORD=your_password" > .env

# Run API server
uvicorn api.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

- The project will run on [http://localhost:3000](http://localhost:3000)


## License

This project was created as part of an MCA academic project (Year II, Semester III).

**Data Attribution**: Product data sourced from Nykaa.com for educational purposes. List of comedogenic ingredients from AcneClinicNYC.
