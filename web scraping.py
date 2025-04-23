from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

url = "https://www.freelancer.com/search/projects?projectLanguages=en&projectSort=latest&q=data"
url2 = "http://upwork.com/nx/search/jobs/?nbs=1&q=data%20analysis"
path = 'E:/Pycharm/chrome/chromedriver-win64/chromedriver.exe'  # Make sure the path ends with chromedriver.exe

service = Service(executable_path=path)
driver = webdriver.Chrome(service=service)

driver.get(url2)
time.sleep(5)
# Use find_elements to get all matching job links

#titles = driver.find_elements(By.XPATH, '//a[@class="air3-link"]')
#experience_level =driver.find_elements(By.XPATH, '//li[@data-test="experience-level"]')
#job_type =driver.find_elements(By.XPATH, '//li[@data-test="job-type-label"]"]')

job_Title = []
Posted_Date = []
Job_Type = []
Experience_Level=[]
Price_OR_Duration = []
Job_Link = []




Job = driver.find_element(By.XPATH, '//article')
Posted_date = Job.find_element(By.XPATH, './/small/span[2]')                                                           #
title = Job.find_element(By.XPATH, './/h2/a')
job_type =Job.find_element(By.XPATH, './/ul/li[1]')
experience_level =Job.find_element(By.XPATH, './/ul/li[2]')
Price_Duration =Job.find_element(By.XPATH, './/ul/li[3]')
link = title.get_attribute('href')

skills = Job.find_element(By.XPATH, './/div[@class="air3-token-container"]')

print(Posted_date.text)
print(title.text)
print(experience_level.text)
print(job_type.text)
print(Price_Duration.text)
print(link)
print (skills.text)
driver.quit()