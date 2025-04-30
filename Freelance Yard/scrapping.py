from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

path = r"E:\Apps\chromedriver-win64\chromedriver.exe"

# Containers for data
titles = []
links = []
descriptions = []
prices = []
tags = []
days_left = []
