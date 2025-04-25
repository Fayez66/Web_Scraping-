from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time

path = r"E:\Apps\chromedriver-win64\chromedriver.exe"

# Containers for data
titles = []
links = []
times = []
descriptions = []
budgets = []
durations = []
number_of_offers = []
tags = []

for page in range(1, 35):
    url = f"https://mostaql.com/projects?page={page}>&category=development&budget_max=10000&sort=latest"
    service = Service(executable_path=path)
    driver = webdriver.Chrome(service=service)
    driver.get(url)
    driver.maximize_window()
      # wait for page to load

    # Collect all project links
    project_links = driver.find_elements(By.CSS_SELECTOR, "h2.mrg--bt-reset a")

    # Store unique links
    unique_links = set()
    for link in project_links:
        href = link.get_attribute("href")
        if href:
            unique_links.add(href)

    for href in unique_links:
        driver.get(href)
        

        links.append(href)

        try:
            title = driver.find_element(By.TAG_NAME, "h1").text
            titles.append(title)
        except:
            print("Couldn't extract title from:", href)
            titles.append("N/A")

        try:
            description_div = driver.find_element(By.CSS_SELECTOR, "div.text-wrapper-div.carda__content")
            descriptions.append(description_div.text)
        except:
            print("Couldn't extract description from:", href)
            descriptions.append("N/A")

        # Extract budget from top of the page
        page_budget = "N/A"
        try:
            page_budget = driver.find_element(By.CSS_SELECTOR, "span.carda__budget").text
        except:
            print("Couldn't extract page budget:", href)

        # Extract project table info
        found_budget_in_table = False
        try:
            table = driver.find_element(By.TAG_NAME, "tbody")
            rows = table.find_elements(By.TAG_NAME, "tr")

            post_date = "N/A"
            duration = "N/A"
            offers = "N/A"
            budget_from_table = "N/A"

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
                    elif label == "الميزانية":
                        budget_from_table = value
                        found_budget_in_table = True

            times.append(post_date)
            durations.append(duration)
            number_of_offers.append(offers)
            if found_budget_in_table:
                budgets.append(budget_from_table)
            else:
                budgets.append(page_budget)

        except:
            print("Couldn't extract budget or other details from:", href)
            times.append("N/A")
            durations.append("N/A")
            number_of_offers.append("N/A")
            budgets.append(page_budget)

        # Extract tags
        try:
            skill_elements = driver.find_elements(By.CSS_SELECTOR, "ul.skills li.skills__item bdi")
            project_tags = [skill.text.strip() for skill in skill_elements]
            tags.append(project_tags)
        except:
            print("Couldn't extract skills.")
            tags.append([])

        driver.back()


    print("Titles:", len(titles))
    print("Times:", len(times))
    print("Budgets:", len(budgets))
    print("Durations:", len(durations))
    print("Offers:", len(number_of_offers))
    print("Tags:", len(tags))
    print("Links:", len(links))

    # Save main data
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

    # Save descriptions separately
    desc_data = {
        "ID": list(range(1, len(titles) + 1)),
        "Description": descriptions,
    }
    df_desc = pd.DataFrame(desc_data)
    df_desc.to_csv(r"E:\Apps\GItHubRebo\Web_Scraping-\Mostaqel\Description.csv", index=False, encoding="utf-8-sig")

    driver.quit()
