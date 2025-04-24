from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
path = r"E:\Apps\chromedriver-win64\chromedriver.exe"
categories = [531770282580668420,531770282580668418,531770282580668419]
i=0
j=1
for category in categories:
    for j in range(1, 5):
        url = f"https://www.upwork.com/nx/search/jobs/?category2_uid={categories[i]}&nbs=1&per_page=50&sort=recency&page={j}"
        service = Service(executable_path=path)
        driver = webdriver.Chrome(service=service)

        driver.maximize_window()
        driver.get(url)

        j += 1
        print(f"Category: {categories[i]} Page: {j} \t ((Done))\n")
        time.sleep(5)
    i += 1

