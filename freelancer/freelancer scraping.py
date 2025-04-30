from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

path = r"E:\Apps\chromedriver-win64\chromedriver.exe"
splits = ['/?hourly=true']

'''they are put on order please don't change the order'''
#['/?fixed=true&fixed_min=0&fixed_max=100', '/?fixed=true&fixed_min=100&fixed_max=500'  ,'/?fixed=true&fixed_min=500',]

pages=[ 37]

'''they are put on order please don't change the order'''
#[56, 57,25,]

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
    index = pages[int(splits.index(split))]
    """change the page number here"""
    for page in range(36,index):
        page_start = time.time()
        url = f"https://www.freelancer.com/jobs/{page}{split}"
        service = Service(executable_path=path)
        driver = webdriver.Chrome(service=service)

        driver.maximize_window()
        driver.get(url)

        search_button = driver.find_element(By.ID, "search-submit")
        search_button.click()
        time.sleep(1)
        wait = WebDriverWait(driver, 1)
        #jobs = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'JobSearchCard-item')))
        jobs = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="JobSearchCard-item "]')))

        for job in jobs:
            #title & link
            try:
                title = job.find_element(By.CLASS_NAME, 'JobSearchCard-primary-heading-link')
                titles.append(title.text.strip())
                links.append(title.get_attribute('href'))
            except:
                titles.append("Blank")
                links.append("Blank")


            # Days left
            try:
                left = job.find_element(By.CLASS_NAME, "JobSearchCard-primary-heading-days")
                days_left.append(left.text.strip())
            except:
                days_left.append("Blank")


            #description
            try:
                desc = job.find_element(By.CLASS_NAME, 'JobSearchCard-primary-description').text
                descriptions.append(desc.strip())
            except:
                descriptions.append("Blank")


            #price & job type
            try:
                price = job.find_element(By.XPATH, './/div[contains(@class, "JobSearchCard-secondary-price")]')
                price_text = price.text.strip()
                prices.append(price_text)
                job_type.append("Hourly" if "hr" in price_text else "Fixed")
                # if "/ hr" in price:
                #     job_type.append("Hourly")
                # else:
                #     job_type.append("Fixed")
            except:
                prices.append("Blank")
                job_type.append("Blank")


            # Bids
            try:
                bid = job.find_element(By.CLASS_NAME, "JobSearchCard-secondary-entry").text
                bids.append(bid)
            except:
                bids.append("Blank")


            #tags
            try:
                skill_elements = job.find_elements(By.XPATH, './/a[contains(@class, "JobSearchCard-primary-tags")]')
                skills = [tag.text.strip() for tag in skill_elements if tag.text.strip()]
                tags.append(skills)
            except:
                tags.append(['Blank'])

        # Save incrementally after each page
        data = {
            "ID": list(range(1, len(titles) + 1)),
            'Title': titles,
            'Bids':bids,
            'Days Left to pid': days_left,
            'Price': prices,
            'Type': job_type,
            'Skills': [", ".join(tag_list) for tag_list in tags],
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

        driver.quit()
    print(f"==> Finished\n")

