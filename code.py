import time
import csv
import os
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

# --- SET UP PARAMETERS ---
AMAZON_USERNAME = "your_amazon_email@example.com"  # Replace with your email
AMAZON_PASSWORD = "your_password_here"            # Replace with your password
CATEGORY_URLS = [
    "https://www.amazon.com/Best-Sellers/zgbs/electronics",
    "https://www.amazon.com/Best-Sellers/zgbs/home-garden",
    # Add 10 Amazon Best Seller URLs for categories here
]
OUTPUT_FILE = "amazon_best_sellers.json"

# Initialize Selenium WebDriver
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(service=Service(r"C:\Users\KIIT0001\OneDrive\Desktop\Assignmet Python\chromedriver.exe"), options=chrome_options)
    return driver

# Amazon Login
def amazon_login(driver):
    driver.get("https://www.amazon.com/")
    time.sleep(2)
    
    try:
        sign_in_btn = driver.find_element(By.ID, "nav-link-accountList")
        sign_in_btn.click()
        
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ap_email"))
        )
        email_input.send_keys(AMAZON_USERNAME)
        driver.find_element(By.ID, "continue").click()
        
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ap_password"))
        )
        password_input.send_keys(AMAZON_PASSWORD)
        driver.find_element(By.ID, "signInSubmit").click()
        print("Login successful.")
        time.sleep(3)
    except Exception as e:
        print("Error during login:", e)
        driver.quit()

# Extract product details
def scrape_category(driver, category_url, max_products=1500):
    driver.get(category_url)
    time.sleep(2)

    product_data = []
    product_count = 0

    try:
        while product_count < max_products:
            products = driver.find_elements(By.CSS_SELECTOR, ".zg-item-immersion")
            
            for product in products:
                if product_count >= max_products:
                    break
                
                try:
                    name = product.find_element(By.CSS_SELECTOR, ".p13n-sc-truncated").text
                    price = product.find_element(By.CSS_SELECTOR, ".p13n-sc-price").text
                    discount = product.find_element(By.CSS_SELECTOR, ".a-color-price").text
                    rating = product.find_element(By.CSS_SELECTOR, ".a-icon-alt").get_attribute("innerHTML")
                    num_bought = product.find_element(By.CSS_SELECTOR, ".a-size-small").text

                    # Store data
                    product_data.append({
                        "Product Name": name,
                        "Product Price": price,
                        "Sale Discount": discount,
                        "Best Seller Rating": rating,
                        "Number Bought": num_bought,
                    })
                    product_count += 1
                except NoSuchElementException:
                    continue

            # Pagination
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, ".a-last a")
                next_btn.click()
                time.sleep(3)
            except (NoSuchElementException, ElementClickInterceptedException):
                break
    except Exception as e:
        print("Error scraping category:", e)

    return product_data

# Save data to JSON
def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Main function
def main():
    driver = init_driver()
    try:
        amazon_login(driver)
        all_product_data = []

        for i, url in enumerate(CATEGORY_URLS[:10]):
            print(f"Scraping category {i+1}: {url}")
            category_data = scrape_category(driver, url)
            for item in category_data:
                item["Category"] = url.split("/")[-1]
            all_product_data.extend(category_data)
        
        save_to_json(all_product_data, OUTPUT_FILE)
        print(f"Data successfully saved to {OUTPUT_FILE}")
    except Exception as e:
        print("An error occurred:", e)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
