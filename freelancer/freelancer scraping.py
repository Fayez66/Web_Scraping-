from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

path = r"E:\Apps\chromedriver-win64\chromedriver.exe"
splits = ['&fixed=true&fixed_min=0&fixed_max=100','&fixed=true&fixed_min=100&fixed_max=500','&fixed=true&fixed_min=500','&hourly=true']
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
    page = 1
    while page < 2:
        page_start = time.time()
        url = f"https://www.freelancer.com/jobs?pg={page}{split}"
        service = Service(executable_path=path)
        driver = webdriver.Chrome(service=service)

        driver.maximize_window()
        driver.get(url)
        #time.sleep(3)

        jobs = driver.find_elements(By.CLASS_NAME, 'JobSearchCard-item')

        if not jobs:
            break           # No jobs found, stop the loop for this category

        for job in jobs:
            #title & link
            try:
                title = job.find_element(By.CLASS_NAME, 'JobSearchCard-primary-heading-link')
                titles.append(title.text.strip())
                links.append(title.get_attribute('href'))
            except:
                titles.append("")
                links.append("")


            # Days left
            try:
                left = job.find_element(By.CLASS_NAME, "JobSearchCard-primary-heading-days")
                days_left.append(left.text.strip())
            except:
                days_left.append("")


            #description
            try:
                desc = job.find_element(By.CLASS_NAME, 'JobSearchCard-primary-description').text
                descriptions.append(desc.strip())
            except:
                descriptions.append("")


            #price & job type
            try:
                price = job.find_element(By.CLASS_NAME, 'JobSearchCard-primary-price').text.strip()
                prices.append(price)
                if "/ hr" in price:
                    job_type.append("Hourly")
                else:
                    job_type.append("Fixed")
            except:
                prices.append("")
                job_type.append("")


            # Bids
            try:
                bid = job.find_element(By.CLASS_NAME, "JobSearchCard-secondary-entry").text
                bids.append(bid)
            except:
                bids.append("")


            #tags
            try:
                skills = [tag.text for tag in job.find_elements(By.CLASS_NAME, "JobSearchCard-primary-tagsLink")]
                tags.append(skills)
            except:
                tags.append([])




            data = {
                "ID": list(range(1, len(titles) + 1)),
                'Title': titles,
                'Bids':bids,
                'Days Left to pid': days_left,
                'Price': prices,
                'Type': job_type,
                'Skills': tags,
                "Link": links,
            }
            desc_data = {
                "ID": list(range(1, len(titles) + 1)),
                "Description": descriptions,
            }
            df = pd.DataFrame(data)
            df.to_csv(r"E:\Apps\GItHubRebo\Web_Scraping-\freelancer\job_listings.csv", index=False, encoding="utf-8-sig")

            df_desc = pd.DataFrame(desc_data)
            df_desc.to_csv(r"E:\Apps\GItHubRebo\Web_Scraping-\freelancer\Description.csv", index=False, encoding="utf-8-sig")
        page_time = time.time() - page_start
        print(f"Scraped page {page} with {len(jobs)} jobs in time {page_time:.2f} seconds.")
        page += 1


        driver.quit()
    print(f"==> Finished\n")

