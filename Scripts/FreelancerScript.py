from selenium.webdriver.support import expected_conditions as EC
from Scripts.functions import translate_with_cache, classify_job
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
from pathlib import Path
import pandas as pd
import time
import re

def main():

    base_path = Path(__file__).resolve().parents[1]
    path = base_path / r"chromedriver-win64\chromedriver.exe"

    splits = ['/?hourly=true']

    '''they are put on order please don't change the order'''
    #['/?fixed=true&fixed_min=0&fixed_max=100', '/?fixed=true&fixed_min=100&fixed_max=500'  ,'/?fixed=true&fixed_min=500',]

    pages=[ 37]

    '''they are put on order please don't change the order'''
    #[56, 57,25,]

    # Containers for data
    titles = []
    links = []
    descriptions = []
    prices = []
    tags = []
    job_type = []
    days_left = []
    bids = []

    for split in splits:
        index = pages[int(splits.index(split))]
        """change the page number here"""
        for page in range(1,2):
            page_start = time.time()
            url = f"https://www.freelancer.com/jobs/{page}{split}"
            service = Service(executable_path=path)
            driver = webdriver.Chrome(service=service)

            driver.maximize_window()
            driver.get(url)

            search_button = driver.find_element(By.ID, "search-submit")
            search_button.click()
            time.sleep(1)
            wait = WebDriverWait(driver, 1)
            #jobs = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'JobSearchCard-item')))
            jobs = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="JobSearchCard-item "]')))

            for job in jobs:
                #title & link
                try:
                    title = job.find_element(By.CLASS_NAME, 'JobSearchCard-primary-heading-link')
                    titles.append(title.text.strip())
                    links.append(title.get_attribute('href'))
                except:
                    titles.append("Blank")
                    links.append("Blank")


                # Days left
                try:
                    left = job.find_element(By.CLASS_NAME, "JobSearchCard-primary-heading-days")
                    days_left.append(left.text.strip())
                except:
                    days_left.append("Blank")


                #description
                try:
                    desc = job.find_element(By.CLASS_NAME, 'JobSearchCard-primary-description').text
                    descriptions.append(desc.strip())
                except:
                    descriptions.append("Blank")


                #price & job type
                try:
                    price = job.find_element(By.XPATH, './/div[contains(@class, "JobSearchCard-secondary-price")]')
                    price_text = price.text.strip()
                    prices.append(price_text)
                    job_type.append("Hourly" if "hr" in price_text else "Fixed")
                    # if "/ hr" in price:
                    #     job_type.append("Hourly")
                    # else:
                    #     job_type.append("Fixed")
                except:
                    prices.append("Blank")
                    job_type.append("Blank")


                # Bids
                try:
                    bid = job.find_element(By.CLASS_NAME, "JobSearchCard-secondary-entry").text
                    bids.append(bid)
                except:
                    bids.append("Blank")


                #tags
                try:
                    skill_elements = job.find_elements(By.XPATH, './/a[contains(@class, "JobSearchCard-primary-tags")]')
                    skills = [tag.text.strip() for tag in skill_elements if tag.text.strip()]
                    tags.append(skills)
                except:
                    tags.append(['Blank'])

            # Save incrementally after each page
            data = {
                'Title': titles,
                'Bids':bids,
                'Days Left to pid': days_left,
                'Price': prices,
                'Type': job_type,
                'Skills': [", ".join(tag_list) for tag_list in tags],
                "Link": links,
                "Description": descriptions,

            }
            df = pd.DataFrame(data)
            df.to_csv(base_path/"Data/Freelancer.csv", index=False, encoding="utf-8-sig")

            page_time = time.time() - page_start
            print(f"Scraped page {page} with {len(jobs)} jobs in time {page_time:.2f} seconds.")

            driver.quit()
        print(f"==> Finished\n")

    data = {
        'Title': titles,
        'Bids': bids,
        'Days Left to bid': days_left,
        'Price': prices,
        'Type': job_type,
        'Skills': [", ".join(tag_list) for tag_list in tags],
        "Link": links,
        "Description": descriptions,

    }

    df = pd.DataFrame(data)


    # Remove duplicates based on 'Title'
    df = df.drop_duplicates(subset=['Title', 'Bids', 'Days Left to bid', 'Price', 'Type', 'Skills', 'Link', 'Description'])

    # Move the last column to the front
    last_col = df.columns[-1]
    df = df[[last_col] + list(df.columns[:-1])]

    # Drop rows with missing Bids or Price
    df.dropna(subset=['Bids', 'Price'], inplace=True)
    df['Title'] = translate_with_cache(df['Title'], target_lang="en", use_cache=False)
    # Remove entries that indicate private projects or contests
    df = df[~df['Title'].str.contains("Private project or contest", case=False, na=False)]

    # Extract numeric values from Bids
    df['Bids'] = df['Bids'].astype(str).apply(
        lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0
    )

    def extract_value(column: str) -> int | None:
        """
        Extract the number of days from a text string. If 'hour' is found, return 0.
        Returns None if no match is found.
        """
        match = re.search(r'(\d+)\s*(days?|hours?)', column, re.IGNORECASE)
        if match:
            value = int(match.group(1))
            if 'hour' in match.group(2).lower():
                return 0
            return value
        return None

    # Apply extraction logic to 'Days Left to Bid'
    df['Days Left to bid'] = df['Days Left to bid'].apply(extract_value)

    def clean_price(value: str) -> float | None:
        """
        Cleans a price string by removing currency symbols and text.
        If the string contains a range, returns the average of the two numbers.
        """
        cleaned = re.sub(r'[^0-9\-.]', '', str(value))
        if '-' in cleaned:
            parts = cleaned.split('-')
            try:
                return (float(parts[0]) + float(parts[1])) / 2
            except (ValueError, IndexError):
                return None
        try:
            return float(cleaned)
        except ValueError:
            return None

    # Apply price cleaning
    df['Price'] = df['Price'].apply(clean_price)

    df['Category.1'] = df['Description'].apply(classify_job)
    # Display info and export cleaned data
    print(df.info())

    #Load the CSV files
    job_df = df.drop(columns=['Skills', 'Description'])
    job_df.index.name = 'ID'
    job_df.to_csv(base_path/"Data/Freelancer.csv", index=True, encoding="utf-8-sig")


    decs_df = df[['Skills']].copy()

    # Split Skills only if not null
    decs_df['Skills'] = decs_df['Skills'].apply(lambda x: x.split(',') if isinstance(x, str) else x)

    # Strip whitespace if it's a list
    decs_df['Skills'] = decs_df['Skills'].apply(lambda x: [tag.strip() for tag in x] if isinstance(x, list) else x)

    # Explode into multiple rows
    decs_df = decs_df.explode('Skills').reset_index(drop=False)
    decs_df.index = decs_df.index + 1
    decs_df = decs_df.rename(columns={'index': 'ID'})


    decs_df.loc[:, 'ID'] = decs_df['ID'] + 1

    decs_df.index.name = 'index'
    decs_df.to_csv(base_path/"Data/FreelancerSkills.csv", index=True, encoding="utf-8-sig")

if __name__ == "__main__":
    main()