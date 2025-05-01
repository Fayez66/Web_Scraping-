
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

path = r"E:\Apps\chromedriver-win64\chromedriver.exe"

# Containers for data
titles = []
links = []
users = []
prices = []
categories = []
date_posted = []
user_types = []

# Setup browser
service = Service(executable_path=path)
driver = webdriver.Chrome(service=service)
driver.get('https://www.freelanceyard.com/en/jobs?filter[category_id]=2&page=1')
driver.maximize_window()

# Loop through pages
for page in range(1, 455):  # 455 pages total
    print(f"Scraping page {page}...")

    jobs = driver.find_elements(By.CSS_SELECTOR, 'div.h-full.p-4.mb-4.bg-white.border.rounded-lg')

    for job in jobs:
        try:
            title = job.find_element(By.TAG_NAME, "h3").text.strip()
            link = job.find_element(By.TAG_NAME, "a").get_attribute("href")

            # Extract username (fallback if structure is tricky)
            try:
                user = job.find_element(By.CLASS_NAME, "uil-user").find_element(By.XPATH, "..").text.strip()
            except:
                user = "N/A"

            try:
                user_type = job.find_element(By.CSS_SELECTOR, "span.text-xs").text.strip()
            except:
                user_type = "N/A"

            try:
                category = job.find_element(By.CSS_SELECTOR, "div.mb-0").text.strip()
            except:
                category = "N/A"

            try:
                budget = job.find_element(By.CSS_SELECTOR, "span.font-bold").text.strip()
            except:
                budget = "N/A"

            try:
                posted = job.find_element(By.CSS_SELECTOR, "div.text-sm.text-gray-400").text.strip()
            except:
                posted = "N/A"

            # Save data
            titles.append(title)
            links.append(link)
            users.append(user)
            prices.append(budget)
            categories.append(category)
            date_posted.append(posted)
            user_types.append(user_type)
        except Exception as e:
            print("Error parsing job:", e)

    # Save to CSV incrementally
    df = pd.DataFrame({
        'Title': titles,
        'Link': links,
        'Client': users,
        'Type': user_types,
        'Budget': prices,
        'Category': categories,
        'Date Posted': date_posted,
    })
    df.to_csv(r"E:\Apps\GItHubRebo\Web_Scraping-\Freelance Yard\job_listings.csv", index=False, encoding="utf-8-sig")

    # Try clicking next
    try:
        next_button = WebDriverWait(driver, 0).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@dusk="nextPage" and contains(text(), "next")]'))
        )
        next_button.click()
    except Exception as e:
        print("No more pages or next button not found:", e)
        break

# Clean up
driver.quit()
print("Scraping completed.")


