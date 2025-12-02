from selenium import webdriver


def setup_driver():
    """Create and configure Chrome WebDriver"""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)
    return webdriver.Chrome(options=chrome_options)


NYKAA_CATEGORIES = {
    "face": "https://www.nykaa.com/makeup/face/c/13?ptype=lst&id=13&root=nav_2&dir=desc&order=popularity",
    "skin": {
        "moisturisers": "https://www.nykaa.com/skin/moisturizers/c/8393",
        "serums": "https://www.nykaa.com/skin/serums/c/73006",
        "cleansers": "https://www.nykaa.com/skin/cleansers/c/8378",
        "masks": "https://www.nykaa.com/skin/masks/c/8399",
        "toners": "https://www.nykaa.com/skin/toners-mists/c/8391",
        "sun_care": "https://www.nykaa.com/skin/sun-care/c/8428",
    },
    "hair": {
        "hair_serum": "https://www.nykaa.com/hair-care/hair/hair-serum/c/320?ptype=lst&id=320&root=nav_3&dir=desc&order=popularity",
        "hair_cream": "https://www.nykaa.com/hair-care/hair/hair-creams-masks/c/2041?ptype=lst&id=2041&root=nav_3&dir=desc&order=popularity",
        "leave_in": "https://www.nykaa.com/hair-care/hair/leave-in-conditioner/c/25980",
    },
}

test_urls = [
    "https://www.nykaa.com/kay-beauty-jelly-lip-cheek-popsicle-wand/p/20245932?productId=20245932&skuId=15608811&pps=4",
    "https://www.nykaa.com/charlotte-tilbury-hollywood-filter/p/985214?root=cav_pd&skuId=959726",
]
