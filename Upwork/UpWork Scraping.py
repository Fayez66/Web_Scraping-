from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from dateutil.relativedelta import relativedelta
from selenium.webdriver.common.by import By
from selenium import webdriver
import pandas as pd
import datetime
import time
import re


path = r"E:\Apps\chromedriver-win64\chromedriver.exe"
categories = [531770282580668420,531770282580668418,531770282580668419]
categories_name = {531770282580668420: "Data Science & Analytics", 531770282580668418: "Web, Mobile & Software Dev",
                   531770282580668419: "IT & NETWORKING"}
i = 0

# Containers for data
titles = []
links = []
times_ = []
descriptions = []
budgets = []
experience_levels = []
tags = []
field = []
job_type = []
duration = []

start_all = time.time()

for category in categories:
    category_start = time.time()
    for page in range(1, 101):
        page_start = time.time()
        url = f"https://www.upwork.com/nx/search/jobs/?category2_uid={categories[i]}&nbs=1&per_page=50&sort=recency&page={page}"
        service = Service(executable_path=path)
        driver = webdriver.Chrome(service=service)

        driver.maximize_window()
        driver.get(url)
        wait = WebDriverWait(driver, 10)

        job_tiles = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'article[data-test="JobTile"]')))

        if not job_tiles:
            break  # No jobs found, stop the loop for this category

        for tile in job_tiles:
            try:
                title_el = tile.find_element(By.CSS_SELECTOR, 'h2.job-tile-title a')
                titles.append(title_el.text.strip())
                links.append(title_el.get_attribute('href'))
            except:
                titles.append("")
                links.append("")

            try:
                posted = tile.find_element(By.CSS_SELECTOR, '[data-test="job-pubilshed-date"]').text
                times_.append(posted.strip())
            except:
                times_.append("")

            try:
                desc = tile.find_element(By.CSS_SELECTOR, '[data-test="UpCLineClamp JobDescription"] p').text
                descriptions.append(desc.strip())
            except:
                descriptions.append("")

            try:
                budget = tile.find_element(By.CSS_SELECTOR, '[data-test="is-fixed-price"]').text
                budgets.append(budget.strip())
            except:
                budgets.append("")

            try:
                level = tile.find_element(By.CSS_SELECTOR, '[data-test="experience-level"]').text
                experience_levels.append(level.strip())
            except:
                experience_levels.append("")

            try:
                jobtype = tile.find_element(By.CSS_SELECTOR, '[data-test="job-type-label"]').text
                job_type.append(jobtype.strip())
            except:
                job_type.append("")

            try:
                due = tile.find_element(By.CSS_SELECTOR, '[data-test="duration-label"]').text
                duration.append(due.strip())
            except:
                duration.append("")

            try:
                skill_elements = tile.find_elements(By.CSS_SELECTOR, '[data-test="token"] span')
                skills = [tag.text.strip() for tag in skill_elements]
                tags.append(skills)
            except:
                tags.append([])

            category_id, category_name = list(categories_name.items())[i]
            field.append(category_name)

        # Save incrementally after each page
        data = {
            "ID": list(range(1, len(titles) + 1)),
            'Category': field,
            'job_type': job_type,
            "Title": titles,
            "Posted": times_,
            "Experience Level": experience_levels,
            "Budget": budgets,
            'duration': duration,
            "Tags": [", ".join(tag_list) for tag_list in tags],
            "Link": links,
        }
        df = pd.DataFrame(data)
        df.to_csv(r"E:\Apps\GItHubRebo\Web_Scraping-\Upwork\job_listings.csv", index=False, encoding="utf-8-sig")

        desc_data = {
            "ID": list(range(1, len(titles) + 1)),
            "Description": descriptions,
        }
        df_desc = pd.DataFrame(desc_data)
        df_desc.to_csv(r"E:\Apps\GItHubRebo\Web_Scraping-\Upwork\Description.csv", index=False, encoding="utf-8-sig")

        page_time = time.time() - page_start
        print(f"Category: {category_name} | Page {page} done in {page_time:.2f} seconds")

        driver.quit()

    category_time = time.time() - category_start
    print(f"==> Finished Category: {category_name} in {category_time:.2f} seconds\n")
    i += 1

total_time = time.time() - start_all
print(f"====> All Categories Done in {total_time:.2f} seconds")

# Load the data
data = {
    "ID": list(range(1, len(titles) + 1)),
    'Category': field,
    'job_type': job_type,
    "Title": titles,
    "Posted": times_,
    "Experience Level": experience_levels,
    "Budget": budgets,
    'duration': duration,
    "Tags": [", ".join(tag_list) for tag_list in tags],
    "Link": links,
}
df = pd.DataFrame(data)
# Remove duplicates and add ID
df = df.drop_duplicates(subset=['Title'])
df['ID'] = range(1, len(df) + 1)

# --- Utility Functions ---

def extract_numbers(text):
    """
    Extract and average numeric values from text.
    Handles ranges like '2 - 3' and avoids treating hyphens as negative signs.
    """
    if isinstance(text, (int, float)):
        return text

    # Replace dash variants with a space to split properly
    text = str(text).replace(',', '').replace('–', '-').replace('—', '-').strip()

    # Explicitly match ranges like '2 - 3' or '2 to 3' or '1,000 - 3,000'
    range_match = re.findall(r'\d+(?:\.\d+)?', text)

    if range_match:
        nums = list(map(float, range_match))
        if len(nums) == 1:
            return nums[0]
        elif len(nums) >= 2:
            return sum(nums[:2]) / 2  # average of first two numbers

    return None

# --- Budget Cleaning ---
def process_file(df):
    df['est. budget'] = df['est. budget'].apply(extract_numbers)
    df['Budget'] = df['Budget'].apply(extract_numbers)
    return df

df = process_file(df)

# --- Job Type Simplification ---
def simplify_job_type(text):
    if isinstance(text, str) and 'Hourly' in text:
        return text[:6]
    return text

df['job_type'] = df['job_type'].apply(simplify_job_type)

# --- Date Parsing ---
def parse_posted_date(text):
    today = datetime.date.today()
    if not isinstance(text, str):
        return text

    text = text.lower()

    if any(unit in text for unit in ['second', 'minute', 'hour']):
        return today
    elif 'yesterday' in text:
        return today - datetime.timedelta(days=1)
    elif 'last week' in text:
        return today - datetime.timedelta(weeks=1)
    elif 'last month' in text:
        return today - relativedelta(months=1)
    elif 'last quarter' in text:
        return today - relativedelta(months=3)
    elif 'last year' in text:
        return today - relativedelta(years=1)
    elif 'days ago' in text:
        return today - datetime.timedelta(days=extract_numbers(text))
    elif 'weeks ago' in text:
        return today - datetime.timedelta(weeks=extract_numbers(text))
    elif 'months ago' in text:
        return today - relativedelta(months=extract_numbers(text))
    elif 'quarters ago' in text:
        return today - relativedelta(months=extract_numbers(text) * 3)
    elif 'years ago' in text:
        return today - relativedelta(years=extract_numbers(text))

    return text

df['Posted'] = df['Posted'].apply(parse_posted_date)

# --- Duration Split ---
df[['est. time', 'hours/week']] = df['duration'].str.split(',', n=1, expand=True)
df['est. time'] = df['est. time'].str.strip()
df['hours/week'] = df['hours/week'].str.strip()

# --- Reorder Columns ---
cols = df.columns.tolist()
duration_index = cols.index('duration')
cols.insert(duration_index , cols.pop(cols.index('est. time')))
cols.insert(duration_index +1, cols.pop(cols.index('hours/week')))
df = df[cols]

# --- Normalize hours/week ---
def normalize_hours(text):
    if not isinstance(text, str):
        return None
    if 'Not sure' in text or 'Hours to be determined' in text:
        return None
    elif 'Less than' in text:
        return '<30'
    elif '30+' in text:
        return '>30'
    return text

df['hours/week'] = df['hours/week'].apply(normalize_hours)
def duration_numbers(text):
    if isinstance(text, (int, float)):
        return text
    # Replace dash variants with a space to split properly
    text = str(text).replace(',', '').replace('–', '-').replace('—', '-').strip()

    # Explicitly match ranges like '2 - 3' or '2 to 3' or '1,000 - 3,000'
    range_match = re.findall(r'\d+(?:\.\d+)?', text)

    if range_match:
        nums = list(map(float, range_match))
        if len(nums) == 1:
            return nums[0]
        elif len(nums) >= 2:
            return f"{nums[0]} to {nums[1]}"  # average of first two numbers

    return None
# --- Normalize duration ---
def normalize_duration(text):
    if not isinstance(text, str):
        return None
    if 'Less than' in text:
        return '<1'
    elif 'More than' in text:
        return '>6'
    elif 'to' in text:
        text = text.replace('to', '-')
        return duration_numbers(text)
    return text

df['duration'] = df['duration'].apply(normalize_duration)

# --- Save to CSV ---
df.to_csv("job_listings_cleaned.csv", index=False, encoding="utf-8-sig")

df['Tags'] = df['Tags'].apply(lambda x: x.split(',') if isinstance(x, str) else x)

# Strip whitespace if it's a list
df['Tags'] = df['Tags'].apply(lambda x: [tag.strip() for tag in x] if isinstance(x, list) else x)

# Explode into multiple rows
df = df.explode('Tags').reset_index(drop=False)
df.index = df.index + 1
df = df.drop(columns=['ID'])
df = df.rename(columns={'index': 'ID'})
# Save to new file
expanded = df[['ID' , 'Tags']]

expanded.loc[:, 'ID'] = expanded['ID'] + 1

expanded.index.name = 'index'
expanded.to_csv("jobs_expanded.csv", index=True, encoding="utf-8-sig")

