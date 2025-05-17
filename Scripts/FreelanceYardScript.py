from Scripts.functions import classify_job, process_file, extract_and_convert_budget, translate_with_cache
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
from pathlib import Path
import pandas as pd

def main():
    base_path = Path(__file__).resolve().parents[1]

    path = base_path / r"chromedriver-win64\chromedriver.exe"

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
    should_break = False
    # Loop through pages
    for page in range(1, 469):  # 469 pages total
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
        df.to_csv(base_path/"Data/FreelanceYard.csv", index=False, encoding="utf-8-sig")

        # Try clicking next
        try:
            next_button = WebDriverWait(driver, 0.5).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@dusk="nextPage" and contains(text(), "next")]'))
            )
            next_button.click()
        except Exception as e:
            print("No more pages or next button not found:", e)
            break

    # Clean up
    driver.quit()
    print("Scraping completed.")

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
    # Remove duplicates and add ID
    df = df.drop_duplicates(subset=['Title','Link','Client','Type','Budget','Category','Date Posted'])

    # --- Budget Cleaning ---
    df = process_file(df, 'Budget', extract_and_convert_budget)

    df['Category'] = df['Category'].str.strip(")")
    df['Category'] = df['Category'].str.strip("(")

    df['Title'] = translate_with_cache(df['Title'], target_lang="en", use_cache=False)

    df['Category.1'] = df['Title'].apply(classify_job)

    # If it's a column in your DataFrame:
    df['Date Posted'] = df['Date Posted'].str.extract(r'(\d{2}-\d{2}-\d{4})')  # extract the date part
    df['Date Posted'] = pd.to_datetime(df['Date Posted'], format='%d-%m-%Y')

    # --- Save to CSV ---
    df.to_csv(base_path/"Data/FreelanceYard.csv", index=False, encoding="utf-8-sig")

if __name__ == "__main__":
    main()