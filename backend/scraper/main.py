from config import setup_driver
from url_scraper import URLCollector
from product_scraper import ProductScraper

driver = setup_driver()

collector = URLCollector(driver)

urls = collector.collect_all_product_urls(
    "https://www.nykaa.com/makeup/face/c/13?ptype=lst&id=13&root=nav_2&dir=desc&order=popularity",
    max_pages=2,
)

print(f"Total URLs collected: {len(urls)}")

with open("face_product_urls.txt", "w") as f:
    for url in urls:
        f.write(url + "\n")

driver.quit()
