import html
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from urllib.parse import urlparse, parse_qs


def setup_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)
    return webdriver.Chrome(options=chrome_options)


def extract_product_name(driver):
    try:
        product_name = driver.title
        cleaned_product_name = " ".join(product_name.split()[1:-1])
        return cleaned_product_name
    except:
        return None


def extract_product_category(driver):
    try:
        product_category = driver.find_element(By.CSS_SELECTOR, value=".last-list a")
        return product_category
    except NoSuchElementException:
        return None


def extract_product_url(driver):
    product_url = driver.current_url
    return product_url


def extract_image_url(driver):
    selectors = [".css-5n0nl4 img", ".css0b4a0jg img"]
    try:
        image_url = driver.find_element(By.CSS_SELECTOR, value=selectors[0])
    except NoSuchElementException:
        image_url = driver.find_element(By.CSS_SELECTOR, value=selectors[1])
    return image_url.get_attribute("src")


def extract_ingredients(driver):
    """
    Extract ingredients list from Nykaa product page.
    Returns: Clean string of ingredients or None if not found
    """
    try:
        # Get all script tags
        script_tags = driver.find_elements(By.TAG_NAME, "script")

        for script in script_tags:
            script_content = script.get_attribute("innerHTML")
            if not script_content:
                continue

            # Look for ingredients pattern in the script
            ingredient_pattern = r'"ingredients":\s*"([^"]*)"'
            matches = re.findall(ingredient_pattern, script_content, re.IGNORECASE)

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

        return cleaned_ingredients_list

    except Exception as e:
        print(f"Error extracting ingredients: {e}")
        return None


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


def main():
    test_urls = [
        "https://www.nykaa.com/kay-beauty-jelly-lip-cheek-popsicle-wand/p/20245932?productId=20245932&skuId=15608811&pps=4",
        "https://www.nykaa.com/charlotte-tilbury-hollywood-filter/p/985214?root=cav_pd&skuId=959726",
    ]

    driver = setup_driver()

    for url in test_urls:
        driver.get(url)
        print("\nProduct Details:")
        print(f"Name: {extract_product_name(driver)}")
        print(f"Category: {extract_product_category(driver).text}")
        print(f"URL: {extract_product_url(driver)}")
        print(f"Image URL: {extract_image_url(driver)}")
        print(f"Ingredients: {extract_ingredients(driver)}")
        print(f"Product ID: {extract_product_id(url)}")


if __name__ == "__main__":
    main()

# driver.close()
# driver.quit()
