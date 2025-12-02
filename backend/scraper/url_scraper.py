from selenium.webdriver.common.by import By
import time


class URLCollector:
    def __init__(self, driver):
        self.driver = driver

    def collect_all_product_urls(self, category_url, max_pages=50):
        self.driver.get(category_url)
        time.sleep(3)

        all_urls = []
        page_num = 1

        while page_num <= max_pages:
            print(f"Collecting from page {page_num}...")

            page_urls = self._get_urls_from_current_page()
            all_urls.extend(page_urls)
            print(f"Found {len(page_urls)} products. Total {len(all_urls)}")

            if not self._go_to_next_page():
                print("No more pages available.")
                break

            page_num += 1

        # unique_urls = list(set(all_urls))
        print(f"\nCollected {len(all_urls)} URLs")
        return all_urls

    def _get_urls_from_current_page(self):
        try:
            product_links = self.driver.find_elements(By.CSS_SELECTOR, "a.css-qlopj4")
            urls = []

            for link in product_links:
                href = link.get_attribute("href")
                if href and "/p/" in href:
                    clean_url = href.split("?")[0]
                    if clean_url.startswith("/"):
                        clean_url = "https://nykaa.com" + clean_url
                    urls.append(clean_url)
            return urls

        except Exception as e:
            print(f"Error extracting URLs: {e}")
            return []

    def _go_to_next_page(self):
        try:
            next_button = self.driver.find_element(By.CSS_SELECTOR, "a.css-1zi560")
            self.driver.execute_script("arguments[0].click();", next_button)
            time.sleep(3)
            return True

        except Exception as e:
            print(f"Next button not found: {e}")
            return False
