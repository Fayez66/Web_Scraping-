from Scripts.functions import classify_job, extract_numbers, process_file, parse_posted_date
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from pathlib import Path
import pandas as pd
import random
import time
import re

def main():
    base_path = Path(__file__).resolve().parents[1]

    path = base_path / r"chromedriver-win64\chromedriver.exe"

    categories = [531770282580668420
                ,531770282580668418,
                531770282580668419]
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

    # Create Chrome instance with undetected_chromedriver
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # DO NOT add `excludeSwitches`, `useAutomationExtension`, etc.
    driver = uc.Chrome(options=options)

    for category in categories:
        category_start = time.time()
        for page in range(1, 99):
            try:
                if category == 531770282580668419 and page == 81:
                    break
                url = f"https://www.upwork.com/nx/search/jobs/?category2_uid={category}&nbs=1&per_page=50&sort=recency&page={page}"
                driver.get(url)
                time.sleep(random.uniform(3, 6))  # simulate human delay

                # Optional scroll to trigger dynamic content
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
                time.sleep(random.uniform(1, 3))

                wait = WebDriverWait(driver, 10)
                job_tiles = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'article[data-test="JobTile"]')))
                if not job_tiles:
                    break
            except Exception as e:
                print(f"⚠️ Failed on page {page} of category {category}: {e}")
                continue

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
                'Category': field,
                'job_type': job_type,
                "Title": titles,
                "Posted": times_,
                "Experience Level": experience_levels,
                "Budget": budgets,
                'duration': duration,
                "Tags": [", ".join(tag_list) for tag_list in tags],
                "Link": links,
                "Description": descriptions,
            }
            df = pd.DataFrame(data)
            df.to_csv(base_path/"Data/UpWork.csv", index=False, encoding="utf-8-sig")



        driver.quit()

        category_time = time.time() - category_start
        print(f"in {category_time:.2f} seconds\n")
        i += 1

    total_time = time.time() - start_all
    print(f"====> All Categories Done in {total_time:.2f} seconds")

    # Load the data
    data = {
        'Category': field,
        'job_type': job_type,
        "Title": titles,
        "Posted": times_,
        "Experience Level": experience_levels,
        "Budget": budgets,
        'duration': duration,
        "Tags": [", ".join(tag_list) for tag_list in tags],
        "Link": links,
        "Description": descriptions,
    }
    start = pd.DataFrame(data)
    # Remove duplicates and add ID
    start = start.drop_duplicates(subset=['Title','Posted','Link'])
    start['Category.1'] = start['Description'].apply(classify_job)
    start = start.drop(columns=['Description'])
    df = start.drop(columns=["Tags"])


    # --- Job Type Simplification ---
    def simplify_job_type(text):
        if isinstance(text, str) and 'Hourly' in text:
            return text[:6]
        return text

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
                return f"{nums[0]} - {nums[1]}"  # average of first two numbers

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

    df['est. budget'] = df['job_type'].str.split(':', expand=True)[1]
    df['job_type'] = df['job_type'].str.split(':', expand=True)[0]

    df = process_file(df,'est. budget',extract_numbers)
    df = process_file(df,'Budget',extract_numbers)
    df = process_file(df,'job_type',simplify_job_type)
    df = process_file(df,'Posted',parse_posted_date)


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


    df = process_file(df,'hours/week',normalize_hours)

    df['duration'] = df['duration'].apply(normalize_duration)

    df['ID'] = range(1, len(df) + 1)
    # --- Save to CSV ---
    df.to_csv(base_path/"Data/UpWork.csv", index=False, encoding="utf-8-sig")




    '''Expanding The Skills'''
    start['ID'] = range(1, len(start) + 1)
    Tags = start[['ID', 'Tags']]

    Tags.loc[:, 'Tags'] = Tags['Tags'].apply(lambda x: x.split(',') if isinstance(x, str) else x)
    Tags.loc[:, 'Tags'] = Tags['Tags'].apply(lambda x: [tag.strip() for tag in x] if isinstance(x, list) else x)

    # Explode into multiple rows
    Tags = Tags.explode('Tags').reset_index(drop=False)
    Tags.index = Tags.index + 1
    Tags = Tags.drop(columns=['ID'])
    Tags = Tags.rename(columns={'index': 'ID'})
    # Save to new file

    Tags.loc[:, 'ID'] = Tags['ID'] + 1
    Tags["WebSite"]= "Upwork"
    Tags.index.name = 'index'
    Tags.to_csv(base_path/"Data/UpWorkSkills.csv", index=True, encoding="utf-8-sig")

if __name__ == "__main__":
    main()