from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

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
