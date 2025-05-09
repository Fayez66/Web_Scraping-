from AllData.functions import process_file, extract_numbers, parse_posted_date, translate_with_cache, classify_job
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
from pathlib import Path
import pandas as pd

base_path = Path(__file__).resolve().parents[1]

path = base_path / r"chromedriver-win64\chromedriver.exe"

# Final containers for all data
titles = []
links = []
times = []
descriptions = []
budgets = []
durations = []
number_of_offers = []
tags = []

for page in range(7, 8):
    url = f"https://mostaql.com/projects?page={page}&category=development&budget_max=10000&sort=latest"
    service = Service(executable_path=path)
    driver = webdriver.Chrome(service=service)
    driver.get(url)
    driver.maximize_window()

    # Collect project links
    project_links = driver.find_elements(By.CSS_SELECTOR, "h2.mrg--bt-reset a")
    unique_links = set(link.get_attribute("href") for link in project_links if link.get_attribute("href"))

    for href in unique_links:
        driver.get(href)


        links.append(href)

        # Title
        try:
            title = driver.find_element(By.TAG_NAME, "h1").text
        except:
            title = "N/A"
        titles.append(title)

        # Description
        try:
            description_div = driver.find_element(By.CSS_SELECTOR, "div.text-wrapper-div.carda__content")
            description = description_div.text
        except:
            description = "N/A"
        descriptions.append(description)

        # Budget from top
        try:
            page_budget = driver.find_element(By.CSS_SELECTOR, "span.carda__budget").text
        except:
            page_budget = "N/A"

        # Initialize table values
        post_date = "N/A"
        duration = "N/A"
        offers = "N/A"
        avg_offer_val = "N/A"
        budget_val = "N/A"

        try:
            table = driver.find_element(By.TAG_NAME, "tbody")
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) == 2:
                    label = cols[0].text.strip()
                    value = cols[1].text.strip()
                    if label == "تاريخ النشر":
                        post_date = value
                    elif label == "مدة التنفيذ":
                        duration = value
                    elif label == "عدد العروض":
                        offers = value
                    elif label == "متوسط العروض":
                        avg_offer_val = value
                    elif label == "الميزانية":
                        budget_val = value
        except:
            pass

        times.append(post_date)
        durations.append(duration)
        number_of_offers.append(offers)

        if avg_offer_val and avg_offer_val != "&0.00":
            budgets.append(avg_offer_val)
        else:
            budgets.append(budget_val if budget_val != "N/A" else page_budget)

        # Tags
        try:
            skill_elements = driver.find_elements(By.CSS_SELECTOR, "ul.skills li.skills__item bdi")
            project_tags = [skill.text.strip() for skill in skill_elements]
        except:
            project_tags = []
        tags.append(project_tags)

    print(f"✅ Finished page {page} - Total titles: {len(titles)}")

    driver.quit()

# After all pages, save the data
data = {
    "Title": titles,
    "Posted": times,
    "Avg offer": budgets,
    "Duration": durations,
    "Number of Offers": number_of_offers,
    "Tags": [", ".join(tag_list) for tag_list in tags],
    "Link": links,
    "Description": descriptions,
}

df = pd.DataFrame(data)


# Remove duplicates and add ID
df = df.drop_duplicates(subset=['Title', 'Posted', 'Avg offer', 'Duration', 'Number of Offers', 'Tags', 'Link'])

df = process_file(df, 'Duration', extract_numbers)
df = process_file(df, 'Posted', parse_posted_date)

df['Description'] = translate_with_cache(df["Description"], target_lang="en", use_cache=False)
df['Category_English'] = df['Description'].apply(classify_job)
df["Category_Arabic"] = translate_with_cache(df["Category_English"], target_lang="ar")

df['Avg offer'] = df['Avg offer'].str.strip('$')
df.rename(columns={'Duration': 'Duration(Days)'}, inplace=True)


jobs = df.drop(columns=['Tags', 'Description'])
# --- Save to CSV ---
jobs.to_csv("Mostaqel.csv", index=True, encoding="utf-8-sig")

# Correct column selection
tags = df[['Tags']].copy()

# Add ID safely
tags["ID"] = range(1, len(tags) + 1)

# Clean and split tags
tags['Tags'] = tags['Tags'].apply(lambda x: x.split(',') if isinstance(x, str) else x)
tags['Tags'] = tags['Tags'].apply(lambda x: [tag.strip() for tag in x] if isinstance(x, list) else x)

tags = tags.explode(['Tags']).reset_index(drop=True)
tags = tags.dropna()

tags["Tags_en"] = translate_with_cache(tags["Tags"], target_lang="en")
tags['Tags_en'] = tags['Tags_en'].str.replace(r'[\u0600-\u06FF]', '', regex=True).str.strip()
# Filter rows where lists are of equal length

tags = tags[tags['Tags'].str.len() == tags['Tags_en'].str.len()]

# Save to CSV
tags.to_csv("MostaqelSkills.csv", index=True, encoding="utf-8-sig")


