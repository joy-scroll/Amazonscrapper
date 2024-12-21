import os
import time
import json
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

# User credentials
USER_EMAIL = "your_email@example.com"
USER_PASSWORD = "your_password"

# Amazon Best Sellers URL
BEST_SELLERS_URL = "https://www.amazon.com/Best-Sellers/zgbs"

def login_to_amazon(driver):
    """Logs into Amazon using provided credentials."""
    driver.get("https://www.amazon.com/ap/signin")
    
    # Wait for email input and enter the email
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ap_email"))).send_keys(USER_EMAIL + Keys.RETURN)
    
    # Wait for password input and enter the password
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ap_password"))).send_keys(USER_PASSWORD + Keys.RETURN)
    
    # Wait for the login to complete
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "nav-link-accountList")))

def scrape_category(driver, category_url, category_name):
    """Scrapes product details in a single category."""
    driver.get(category_url)
    products = []
    
    while len(products) < 1500:
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".zg-item-immersion")))
        product_elements = driver.find_elements(By.CSS_SELECTOR, ".zg-item-immersion")
        
        for product in product_elements:
            try:
                # Extract product details
                name = product.find_element(By.CSS_SELECTOR, ".p13n-sc-truncated").text
                price = product.find_element(By.CSS_SELECTOR, ".p13n-sc-price").text
                discount = None
                rating = None
                num_bought = None
                ship_from = None
                sold_by = None
                product_desc = None
                images = []

                # Discount and additional info
                try:
                    discount_text = product.find_element(By.CSS_SELECTOR, ".a-icon-row.a-spacing-none").text
                    if "Save" in discount_text:
                        discount = int(discount_text.split("Save ")[1].split("%")[0])
                except:
                    pass
                
                # Product Rating
                try:
                    rating = product.find_element(By.CSS_SELECTOR, ".a-icon-alt").text
                except:
                    pass
                
                # Images
                try:
                    images_elements = product.find_elements(By.CSS_SELECTOR, "img")
                    images = [img.get_attribute("src") for img in images_elements]
                except:
                    pass
                
                # Only add products with discounts > 50%
                if discount and discount > 50:
                    products.append({
                        "Category Name": category_name,
                        "Product Name": name,
                        "Product Price": price,
                        "Sale Discount": discount,
                        "Best Seller Rating": rating,
                        "Ship From": ship_from,
                        "Sold By": sold_by,
                        "Rating": rating,
                        "Product Description": product_desc,
                        "Number Bought in the Past Month": num_bought,
                        "All Available Images": images,
                    })
            except Exception as e:
                continue
        
        # Navigate to the next page if available
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, ".a-last a")
            next_button.click()
            time.sleep(2)
        except:
            break
    
    return products

def save_to_file(data, filename, file_format="csv"):
    """Saves data to CSV or JSON file."""
    if file_format == "csv":
        keys = data[0].keys()
        with open(filename, "w", newline="", encoding="utf-8") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
    elif file_format == "json":
        with open(filename, "w", encoding="utf-8") as output_file:
            json.dump(data, output_file, ensure_ascii=False, indent=4)

def main():
    # Set up the WebDriver using GeckoDriverManager
    service = Service(GeckoDriverManager().install())
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")  # Run in headless mode for efficiency
    driver = webdriver.Firefox(service=service, options=options)
    
    try:
        login_to_amazon(driver)
        
        # Navigate to Best Sellers
        driver.get(BEST_SELLERS_URL)
        
        # Collect links to top 10 categories
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".zg_homeWidget")))
        category_elements = driver.find_elements(By.CSS_SELECTOR, ".zg_homeWidget")[:10]
        categories = [
            {
                "name": el.find_element(By.CSS_SELECTOR, ".p13n-sc-truncated").text,
                "url": el.find_element(By.CSS_SELECTOR, "a").get_attribute("href"),
            }
            for el in category_elements
        ]
        
        all_products = []
        for idx, category in enumerate(categories):
            print(f"Scraping category {idx + 1}: {category['name']}")
            category_products = scrape_category(driver, category["url"], category["name"])
            all_products.extend(category_products)
        
        # Save the data
        save_to_file(all_products, "amazon_best_sellers.csv", file_format="csv")
        save_to_file(all_products, "amazon_best_sellers.json", file_format="json")
        print("Scraping complete. Data saved to 'amazon_best_sellers.csv' and 'amazon_best_sellers.json'.")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
