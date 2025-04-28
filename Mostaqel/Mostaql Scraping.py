from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time

path = r"E:\Apps\chromedriver-win64\chromedriver.exe"

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
    "ID": list(range(1, len(titles) + 1)),
    "Title": titles,
    "Posted": times,
    "Budget": budgets,
    "Duration": durations,
    "Number of Offers": number_of_offers,
    "Tags": [", ".join(tag_list) for tag_list in tags],
    "Link": links,
}

df = pd.DataFrame(data)
df.to_csv(r"E:\Apps\GItHubRebo\Web_Scraping-\Mostaqel\job_listings.csv", index=False, encoding="utf-8-sig")

desc_data = {
    "ID": list(range(1, len(titles) + 1)),
    "Description": descriptions,
}
df_desc = pd.DataFrame(desc_data)
df_desc.to_csv(r"E:\Apps\GItHubRebo\Web_Scraping-\Mostaqel\Description.csv", index=False, encoding="utf-8-sig")
