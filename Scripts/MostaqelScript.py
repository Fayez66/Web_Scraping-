from Scripts.functions import process_file, extract_numbers, parse_posted_date, translate_with_cache, classify_job
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
from pathlib import Path
import pandas as pd
import re

def main():
    base_path = Path(__file__).resolve().parents[1]

    path = base_path / r"chromedriver-win64\chromedriver.exe"

    # Final containers for all data
    titles = []
    links = []
    posted_dates = []
    descriptions = []
    budget_val = []
    durations = []
    number_of_offers = []
    tags = []


    #---- Web Scraping ---------

    for page in range(0, 1):
        url = f"https://mostaql.com/projects?page={page}&category=development&budget_max=10000&sort=latest"
        service = Service(executable_path=path)
        driver = webdriver.Chrome(service=service)
        driver.get(url)
        driver.maximize_window()

        # Collect project links

        project_links = driver.find_elements(By.CSS_SELECTOR, "h2.mrg--bt-reset a")
        unique_links = set(link.get_attribute("href") for link in project_links if link.get_attribute("href"))

        # Get Posted Date for each job in page
        times_posted = driver.find_elements(By.CSS_SELECTOR, "li.text-muted time")
        times_posted = [time.text for time in times_posted]
        link_time_map = dict(zip(unique_links, times_posted))

        # Get Number of offers for each job in page
        offers = driver.find_elements(By.XPATH, "//i[contains(@class,'fa-ticket')]/..")
        offers = [offer.text for offer in offers]
        link_offers_map = dict(zip(unique_links, offers))

        for href in unique_links:
            driver.get(href)
            posted_time = link_time_map.get(href)
            job_offers = link_offers_map.get(href)

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
            duration = "N/A"
            offers = "N/A"
            avg_offer_val = "N/A"
            budget = "N/A"

            try:
                # Find the container by a single class name
                meta_rows_container = driver.find_element(By.CLASS_NAME, "meta-rows")
                rows = meta_rows_container.find_elements(By.CLASS_NAME, "meta-row")

                for row in rows:
                    try:
                        label_elem = row.find_element(By.CLASS_NAME, "meta-label")
                        value_elem = row.find_element(By.CLASS_NAME, "meta-value")
                        label = label_elem.text.strip()
                        value = value_elem.text.strip()

                        if label == "الميزانية":
                            budget = value
                        elif label == "مدة التنفيذ":
                            duration = value
                    except:
                        continue
            except:
                duration = "N/A"
                avg_offer_val = "N/A"
                budget = "N/A"

            posted_dates.append(posted_time)
            durations.append(duration)
            number_of_offers.append(job_offers)

            budget_val.append(budget if budget != "N/A" else page_budget)
            # Tags
            try:
                skill_elements = driver.find_elements(By.CSS_SELECTOR, "ul.skills li.skills__item bdi")
                project_tags = [skill.text.strip() for skill in skill_elements]
            except:
                project_tags = []
            tags.append(project_tags)

        print(f"Finished page {page} - Total titles: {len(titles)}")

        driver.quit()

    # After all pages, save the data
    data = {
        "Title": titles,
        "Posted": posted_dates,
        "Budget": budget_val,
        "Duration": durations,
        "Tags": [", ".join(tag_list) for tag_list in tags],
        "Description": descriptions,
        "number of offers": number_of_offers,
        "Link": links

    }


    #------- Data Cleaning -------

    df = pd.DataFrame(data)

    def extract_avg_offer(value):
        try:
            # Remove any currency symbols and whitespace
            parts = value.replace('$', '').split('-')
            if len(parts) == 2:
                low, high = float(parts[0].strip()), float(parts[1].strip())
                return round((low + high) / 2, 2)
            else:
                return float(parts[0].strip())  # Single value fallback
        except:
            return None

    df["Budget"] = df["Budget"].apply(extract_avg_offer)
    #-----------

    def extract_number(text):
        if "واحد" in text:
            return 1
        elif "عرضين" in text or "عرضان" in text:
            return 2

        else:
            text = text.strip()

            # Extract the first number in the text
            match = re.search(r'\d+', text)  # This will match the first sequence of digits
            if match:
                return int(match.group())
            else:
                return 0

    # Apply cleaning
    df['number of offers'] = df['number of offers'].apply(extract_number)
    #-----------

    # Remove duplicates and add ID
    df = df.drop_duplicates(subset=['Title', 'Posted', 'Budget', 'Duration',  'Tags', 'Link'])

    df = process_file(df, 'Duration', extract_numbers)
    df = process_file(df, 'Posted', parse_posted_date)

    df['Description'] = translate_with_cache(df["Description"], target_lang="en", use_cache=False)
    df['Category_English'] = df['Description'].apply(classify_job)
    df["Category_Arabic"] = translate_with_cache(df["Category_English"], target_lang="ar")

    df.rename(columns={'Duration': 'Duration(Days)'}, inplace=True)


    jobs = df.drop(columns=['Tags', 'Description'])
    df.index += 1  # Start index from 1
    df.index.name = 'ID'
    # --- Save to CSV ---
    jobs.to_csv(base_path/"Data/Mostaqel.csv", index=True, encoding="utf-8-sig")

    # Correct column selection
    # tags = df[['Tags']].copy()
    #
    # # Add ID safely
    # tags["ID"] = range(1, len(tags) + 1)
    #
    # # Clean and split tags
    # tags['Tags'] = tags['Tags'].apply(lambda x: x.split(',') if isinstance(x, str) else x)
    # tags['Tags'] = tags['Tags'].apply(lambda x: [tag.strip() for tag in x] if isinstance(x, list) else x)
    #
    # tags = tags.explode(['Tags']).reset_index(drop=True)
    # tags = tags.dropna()
    #
    # tags["Tags_en"] = translate_with_cache(tags["Tags"], target_lang="en")
    # tags['Tags_en'] = tags['Tags_en'].str.replace(r'[\u0600-\u06FF]', '', regex=True).str.strip()
    # # Filter rows where lists are of equal length
    #
    # tags = tags[tags['Tags'].str.len() == tags['Tags_en'].str.len()]


    #expanding
    df['ID'] = range(1, len(df) + 1)
    Tags = df[['ID', 'Tags']]

    Tags.loc[:, 'Tags'] = Tags['Tags'].apply(lambda x: x.split(',') if isinstance(x, str) else x)
    Tags.loc[:, 'Tags'] = Tags['Tags'].apply(lambda x: [tag.strip() for tag in x] if isinstance(x, list) else x)

    # Explode into multiple rows
    Tags = Tags.explode('Tags').reset_index(drop=True)
    Tags = Tags.dropna(subset=['Tags'])
    Tags['ID'] = range(1, len(Tags) + 1)
    Tags.index.name = 'index'
    # Save to new file

    Tags.loc[:, 'ID'] = Tags['ID'] + 1
    Tags.index.name = 'index'
    Tags["Tags_en"] = translate_with_cache(Tags["Tags"], target_lang="en")
    Tags['Tags_en'] = Tags['Tags_en'].str.replace(r'[\u0600-\u06FF]', '', regex=True).str.strip()
    # Save to CSV
    Tags.to_csv(base_path/"Data/MostaqelSkills.csv", index=True, encoding="utf-8-sig")

if __name__ == "__main__":
    main()
