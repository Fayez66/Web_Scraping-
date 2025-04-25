from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

path = r"E:\Apps\chromedriver-win64\chromedriver.exe"
categories = [531770282580668420,531770282580668418,531770282580668419]
categories_name = {531770282580668420: "Data Science & Analytics", 531770282580668418: "Web, Mobile & Software Dev",
                   531770282580668419: "IT & NETWORKING"}  # Add more categories as needed
i=0
j=1

# Containers for data
titles = []
links = []
times = []
descriptions = []
budgets = []
experience_levels = []
tags = []
field = []

for category in categories:
    for j in range(1, 100):
        url = f"https://www.upwork.com/nx/search/jobs/?category2_uid={categories[i]}&nbs=1&per_page=50&sort=recency&page={j}"
        service = Service(executable_path=path)
        driver = webdriver.Chrome(service=service)

        driver.maximize_window()
        driver.get(url)
        wait = WebDriverWait(driver, 10)

        job_tiles = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'article[data-test="JobTile"]')))

        for tile in job_tiles:
            # Title & Link
            try:
                title_el = tile.find_element(By.CSS_SELECTOR, 'h2.job-tile-title a')
                titles.append(title_el.text.strip())
                links.append(title_el.get_attribute('href'))
            except:
                titles.append("")
                links.append("")

            # Posted time
            try:
                posted = tile.find_element(By.CSS_SELECTOR, '[data-test="job-pubilshed-date"]').text
                times.append(posted.strip())
            except:
                times.append("")

            # Description
            try:
                desc = tile.find_element(By.CSS_SELECTOR, '[data-test="UpCLineClamp JobDescription"] p').text
                descriptions.append(desc.strip())
            except:
                descriptions.append("")

            # Budget
            try:
                budget = tile.find_element(By.CSS_SELECTOR, '[data-test="is-fixed-price"]').text
                budgets.append(budget.strip())
            except:
                budgets.append("")

            # Experience Level
            try:
                level = tile.find_element(By.CSS_SELECTOR, '[data-test="experience-level"]').text
                experience_levels.append(level.strip())
            except:
                experience_levels.append("")

            # Tags (skills)
            try:
                skill_elements = tile.find_elements(By.CSS_SELECTOR, '[data-test="token"] span')
                skills = [tag.text.strip() for tag in skill_elements]
                tags.append(skills)
            except:
                tags.append([])

            # Convert dict to list of tuples and get the (key, value) pair at index i
            category_id, category_name = list(categories_name.items())[i]
            field.append(category_name)  # adds a tuple (ID, name)]
        category_id, category_name = list(categories_name.items())[i]
        print(f"Category: {category_name} Page: {j} \t ((Done))\n")
        driver.quit()
        j += 1
    i += 1


# Prepare data dictionary
data = {
    "Title": titles,
    "Link": links,
    "Posted": times,
    "Experience Level": experience_levels,
    "Budget": budgets,
    "Description": descriptions,
    "Tags": [", ".join(tag_list) for tag_list in tags]  # join tags into one string
}

# Convert to DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv(r"E:\Apps\GItHubRebo\Web_Scraping-\job_listings.csv", index=False, encoding="utf-8-sig")

print("Data saved to job_listings.csv")


