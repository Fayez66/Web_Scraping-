from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

url = "https://www.freelancer.com/search/projects?projectLanguages=en&projectSort=latest&q=data"
url2 = "https://www.upwork.com/nx/search/jobs/?nbs=1&q=data%20analysis&page=1&per_page=50"
path = 'E:/Pycharm/chrome/chromedriver-win64/chromedriver.exe'  # Make sure the path ends with chromedriver.exe

service = Service(executable_path=path)
driver = webdriver.Chrome(service=service)
driver.maximize_window()
driver.get(url2)
time.sleep(5)
# Use find_elements to get all matching job links

#titles = driver.find_elements(By.XPATH, '//a[@class="air3-link"]')
#experience_level =driver.find_elements(By.XPATH, '//li[@data-test="experience-level"]')
#job_type =driver.find_elements(By.XPATH, '//li[@data-test="job-type-label"]"]')

body = driver.find_element(By.TAG_NAME, 'body')
# for _ in range(15):
#     body.send_keys(Keys.PAGE_DOWN)
#     time.sleep(0.1)
# # Next = driver.find_element(By.XPATH, '//button[@data-ev-label="pagination_next_page"]')
# # Next.click()
# next_xpath = '//button[@data-ev-label="pagination_next_page"]'
# elements = driver.find_elements(By.XPATH, next_xpath)
# print(f"next elements found: {len(elements)}")
#
# # Scroll if found
# if elements:
#     next.click()
# else:
#     print("next not found.")
from selenium.common.exceptions import ElementClickInterceptedException

elements = driver.find_elements(By.XPATH, '//button[@data-ev-label="pagination_next_page"]')

if elements:
    next_btn = elements[0]
    for _ in range(15):
         body.send_keys(Keys.PAGE_DOWN)
         time.sleep(0.1)
    try:
        time.sleep(1)
        next_btn.click()
        print("Clicked the next button.")
    except ElementClickInterceptedException:
        print("Click was intercepted")
        driver.execute_script("arguments[0].click();", next_btn)
else:
    print("Next button not found.")

job_Title = []
Posted_Date = []
Job_Type = []
Experience_Level=[]
Price_OR_Duration = []
Job_Link = []

# dropdown = select(driver.find_element(By.XPATH, '//div[@data-test="jobs_per_page UpCDropdown"]'))
# dropdown.select_by_visible_text('50')
# Open dropdown

#Job = driver.find_element(By.XPATH, '//article')
# Posted_date = Job.find_element(By.XPATH, './/small/span[2]')
# title = Job.find_element(By.XPATH, './/h2/a')
# job_type =Job.find_element(By.XPATH, './/ul/li[1]')
# experience_level =Job.find_element(By.XPATH, './/ul/li[2]')
# Price_Duration =Job.find_element(By.XPATH, './/ul/li[3]')
# link = title.get_attribute('href')
#
# skills = Job.find_element(By.XPATH, './/div[@class="air3-token-container"]')
#
# print(Posted_date.text)
# print(title.text)
# print(experience_level.text)
# print(job_type.text)
# print(Price_Duration.text)
# print(link)
# print (skills.text)
time.sleep(60)

driver.quit()
# pd.DataFrame({})