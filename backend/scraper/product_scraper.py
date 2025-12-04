import html
import re
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from urllib.parse import urlparse, parse_qs


class ProductScraper:
    def __init__(self, driver):
        self.driver = driver

    def scrape_product(self, url):
        name = self._extract_product_name()
        category = self._extract_product_category()
        image_url = self._extract_image_url()
        ingredients = self._extract_ingredients()
        product_id = self.extract_product_id(url)

        return {
            "name": name,
            "category": category,
            "image_url": image_url,
            "ingredients": ingredients,
            "product_id": product_id,
            "url": url,
        }

    def _extract_product_name(self):
        try:
            product_name = self.driver.title
            cleaned_product_name = " ".join(product_name.split()[1:-1])
            return cleaned_product_name
        except Exception:
            return None

    def _extract_product_category(self):
        try:
            product_category = self.driver.find_element(
                By.CSS_SELECTOR, value=".last-list a"
            )
            return product_category.text
        except NoSuchElementException:
            return None

    def _extract_product_url(self):
        product_url = self.driver.current_url
        return product_url

    def _extract_image_url(self):
        selectors = [".css-5n0nl4 img", ".css0b4a0jg img"]
        try:
            image_url = self.driver.find_element(By.CSS_SELECTOR, value=selectors[0])
        except NoSuchElementException:
            image_url = self.driver.find_element(By.CSS_SELECTOR, value=selectors[1])
        return image_url.get_attribute("src")

    @staticmethod
    def _clean_ingredient_name(ingredient):
        """
        Clean ingredient name by removing CI codes and other suffixes.

        Examples:
        - "Bismuth Oxychloride (Ci 77163)" -> "Bismuth Oxychloride"
        - "Iron Oxides (Ci 77491, Ci 77492)" -> "Iron Oxides"
        - "Red 7 Lake (Ci 15850)" -> "Red 7 Lake"
        """
        # Remove CI codes in parentheses: (Ci 12345) or (CI 12345)
        cleaned = re.sub(r'\s*\([Cc][Ii]\s+\d+(?:,\s*[Cc][Ii]\s+\d+)*\)', '', ingredient)

        # Remove trailing/leading whitespace
        cleaned = cleaned.strip()

        return cleaned

    def _extract_ingredients(self):
        """
        Extract ingredients list from Nykaa product page.
        Returns: Clean string of ingredients or None if not found
        """
        try:
            # Get page source directly instead of iterating through stale elements
            page_source = self.driver.page_source

            # Look for ingredients pattern in the entire page source
            ingredient_pattern = r'"ingredients":\s*"([^"]*)"'
            matches = re.findall(ingredient_pattern, page_source, re.IGNORECASE)

            if matches:
                raw_ingredients = matches[0]

                def clean_ingredient_string(raw_string):
                    cleaned = html.unescape(raw_string)
                    cleaned = re.sub(r"<[^>]+>", "", cleaned)
                    cleaned = cleaned.replace("\\n", " ").replace("\\t", " ")
                    cleaned = re.sub(r"\s+", " ", cleaned)
                    cleaned = cleaned.strip()
                    return cleaned

                cleaned_ingredients = clean_ingredient_string(raw_ingredients)
                cleaned_ingredients_list = list(
                    map(str.strip, cleaned_ingredients.split(","))
                )

                # Clean each ingredient to remove CI codes and other suffixes
                cleaned_ingredients_list = [
                    self._clean_ingredient_name(ing) for ing in cleaned_ingredients_list
                ]

                return cleaned_ingredients_list

            return None

        except Exception as e:
            print(f"Error extracting ingredients: {e}")
            return None

    @staticmethod
    def extract_product_id(url):
        parsed_url = urlparse(url)

        path_parts = parsed_url.path.split("/")
        if "p" in path_parts:
            p_index = path_parts.index("p")
            if len(path_parts) > p_index + 1:
                return path_parts[p_index + 1]

        query_params = parse_qs(parsed_url.query)
        product_id = query_params.get("productId", [None])[0]
        return product_id
