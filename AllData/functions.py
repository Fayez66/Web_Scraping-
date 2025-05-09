from dateutil.relativedelta import relativedelta
from deep_translator import GoogleTranslator
from rapidfuzz import fuzz
from pathlib import Path
import pandas as pd
import datetime
import json
import os
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


map_file = "../AllData/AllData/translation_map.json"

def translate_with_cache(text_series, target_lang):
    # Load cache if available
    if os.path.exists(map_file):
        with open(map_file, "r", encoding="utf-8") as f:
            word_map = json.load(f)
    else:
        word_map = {}

    def translate(text):
        try:
            if text in word_map:
                return word_map[text]  # use cached version
            else:
                # Automatically detect the source language
                translation = GoogleTranslator(source='auto', target=target_lang).translate(text)
                word_map[text] = translation
                print(f"Translated '{text}' to {target_lang} as '{translation}' and cached it.")
                return translation
        except Exception as e:
            print(f"Error translating '{text}': {e}")
            return text

    # Apply correction to old translations
    for key in list(word_map):
        value = word_map[key]
        if 'site' in value:
            word_map[key] = value.replace('site', 'web')

    # Save updated cache
    with open(map_file, "w", encoding="utf-8") as f:
        json.dump(word_map, f, ensure_ascii=False, indent=2)

    # Apply to series if needed
    if isinstance(text_series, pd.Series):
        return text_series.apply(translate)
    else:
        return translate(text_series)


def process_file(df,column,function):
    df[f'{column}'] = df[f'{column}'].apply(function)
    return df