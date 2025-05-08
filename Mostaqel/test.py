from selenium.webdriver.chrome.service import Service
from deep_translator import GoogleTranslator
from selenium.webdriver.common.by import By
from selenium import webdriver
from pathlib import Path
import pandas as pd
import datetime
import json
import os
import re

from AllData.functions import process_file, extract_numbers, parse_posted_date

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
    "Budget": budgets,
    "Duration": durations,
    "Number of Offers": number_of_offers,
    "Tags": [", ".join(tag_list) for tag_list in tags],
    "Link": links,
    "Description": descriptions,
}

df = pd.DataFrame(data)

map_file = "../AllData/AllData/translation_map.json"

if os.path.exists(map_file):
    with open(map_file, "r", encoding="utf-8") as f:
        word_map = json.load(f)
else:
    word_map = {}

def translate_with_cache(text, target_lang):
    try:
        if text in word_map:
            return word_map[text]  # Use cached version
        else:
            # Automatically detect the source language
            translation = GoogleTranslator(source='auto', target=target_lang).translate(text)
            word_map[text] = translation
            print(f"Translated '{text}' to {target_lang} as '{translation}' and cached it.")
            return translation
    except Exception as e:
        print(f"Error translating '{text}': {e}")
        return text

# Remove duplicates and add ID
df = df.drop_duplicates(subset=['Title', 'Posted', 'Avg offer', 'Duration', 'Number of Offers', 'Tags', 'Link'])

df['Duration'] = process_file(df, 'Duration', extract_numbers)
df['Posted'] = process_file(df, 'Posted', parse_posted_date)

df["Tags_en"] = translate_with_cache(df["Tags"], target_lang="en")
df["category_arabic"] = translate_with_cache(df["Category_English"], target_lang="ar")

# Reorder columns to place 'category_arabic' right after 'Category_English'
cols = list(tags.columns)
idx = cols.index('Category_English')
# Remove and reinsert at desired position
cols.insert(idx + 1, cols.pop(cols.index('category_arabic')))
tags = tags[cols]

df['Avg offer'] = df['Avg offer'].str.strip('$')
df.rename(columns={'Duration': 'Duration(Days)'}, inplace=True)
df['Tags_en'] = df['Tags_en'].str.replace(r'[\u0600-\u06FF]', '', regex=True).str.strip()

jobs = df.drop(columns=['Tags', 'Tags_en', 'Description', 'Tags_en'])
# --- Save to CSV ---
df.to_csv("job_listings_cleaned.csv", index=True, encoding="utf-8-sig")
tags = jobs['Tags', 'Tags_en']

tags["ID"] = range(1, len(tags) + 1)

# Split both columns only if not null
tags['Tags'] = tags['Tags'].apply(lambda x: x.split(',') if isinstance(x, str) else x)
tags['Tags_en'] = tags['Tags_en'].apply(lambda x: x.split(',') if isinstance(x, str) else x)

# Strip whitespace in both columns
tags['Tags'] = tags['Tags'].apply(lambda x: [tag.strip() for tag in x] if isinstance(x, list) else x)
tags['Tags_en'] = tags['Tags_en'].apply(lambda x: [skill.strip() for skill in x] if isinstance(x, list) else x)

# Ensure both columns have the same number of elements per row
tags = tags[tags['Tags'].str.len() == tags['Tags_en'].str.len()]

# Convert both columns to Series and explode together
tags = tags.explode(['Tags', 'Tags_en']).reset_index(drop=True)



# ---------- 6. Clean up translations (replace 'site' with 'web') ----------
for key in list(word_map):
    value = word_map[key]
    if 'site' in value:
        word_map[key] = value.replace('site', 'web')

# ---------- 7. Save updated map ----------
with open(map_file, "w", encoding="utf-8") as f:
    json.dump(word_map, f, ensure_ascii=False, indent=2)
# Save to new file

tags.to_csv("jobs_expanded.csv", index=True, encoding="utf-8-sig")






