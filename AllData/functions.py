from rapidfuzz import fuzz
import json
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from dateutil.relativedelta import relativedelta
from selenium.webdriver.common.by import By
from selenium import webdriver
from pathlib import Path
import pandas as pd
import datetime
import time
import re

base_path = Path(__file__).resolve().parents[1]

with open(base_path/r'AllData\categorization.json', 'r', encoding='utf-8') as f:
    categories = json.load(f)


def classify_job(desc):
    desc = desc.lower()
    top_words = 0
    threshold = 80
    best_category = None

    for category, keywords in categories.items():
        category_words = 0
        for keyword in keywords:
            score = fuzz.partial_ratio(keyword.lower(), desc)

            if score > threshold:
                category_words =+ 1
        if category_words > top_words:
            top_words = category_words
            best_category = category
        print(f"Category: {category}, Keywords Matched: {category_words}, Best Category: {best_category}")
    if top_words != 0 :  # Adjust this threshold if needed
        return best_category
    else:
        return "Other"


def extract_numbers(text):
    """
    Extract and average numeric values from text.
    Handles ranges like '2 - 3' and avoids treating hyphens as negative signs.
    """
    if isinstance(text, (int, float)):
        return text

    # Replace dash variants with a space to split properly
    text = str(text).replace(',', '').replace('–', '-').replace('—', '-').strip()

    # Explicitly match ranges like '2 - 3' or '2 to 3' or '1,000 - 3,000'
    range_match = re.findall(r'\d+(?:\.\d+)?', text)

    if range_match:
        nums = list(map(float, range_match))
        if len(nums) == 1:
            return nums[0]
        elif len(nums) >= 2:
            return sum(nums[:2]) / 2  # average of first two numbers

    return None

# --- Date Parsing ---
def parse_posted_date(text):
    today = datetime.date.today()
    if not isinstance(text, str):
        return text

    text = text.lower()

    if any(unit in text for unit in ['second', 'minute', 'hour', 'دقيقة', 'ساعة','ساعتين','ساعات']):
        return today
    elif 'yesterday' in text or 'يوم' in text:
        return today - datetime.timedelta(days=1)
    elif 'يومين' in text :
        return today - datetime.timedelta(days=2)
    elif 'last week' in text:
        return today - datetime.timedelta(weeks=1)
    elif 'last month' in text:
        return today - relativedelta(months=1)
    elif 'last quarter' in text:
        return today - relativedelta(months=3)
    elif 'last year' in text:
        return today - relativedelta(years=1)
    elif 'days ago' or 'يوما' in text or 'أيام' in text in text:
        return today - datetime.timedelta(days=extract_numbers(text))
    elif 'weeks ago' in text:
        return today - datetime.timedelta(weeks=extract_numbers(text))
    elif 'months ago' in text:
        return today - relativedelta(months=extract_numbers(text))
    elif 'quarters ago' in text:
        return today - relativedelta(months=extract_numbers(text) * 3)
    elif 'years ago' in text:
        return today - relativedelta(years=extract_numbers(text))

    return text

def process_file(df,column,function):
    df[f'{column}'] = df[f'{column}'].apply(function)
    return df