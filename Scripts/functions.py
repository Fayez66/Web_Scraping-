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

with open(base_path/r'Scripts\categorization.json', 'r', encoding='utf-8') as f:
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
                category_words += 1
        if category_words > top_words:
            top_words = category_words
            best_category = category
        print(f"Keywords Matched: {top_words}, Best Category: {best_category}")
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
    elif 'يومين' in text:
        return today - datetime.timedelta(days=2)
    elif 'last week' in text:
        return today - datetime.timedelta(weeks=1)
    elif 'last month' in text:
        return today - relativedelta(months=1)
    elif 'last quarter' in text:
        return today - relativedelta(months=3)
    elif 'last year' in text:
        return today - relativedelta(years=1)

    elif 'days ago' in text or 'يوما' in text or 'أيام' in text:
        num = extract_numbers(text)
        if num is not None:
            return today - datetime.timedelta(days=num)

    elif 'weeks ago' in text:
        num = extract_numbers(text)
        if num is not None:
            return today - datetime.timedelta(weeks=num)

    elif 'months ago' in text:
        num = extract_numbers(text)
        if num is not None:
            return today - relativedelta(months=num)

    elif 'quarters ago' in text:
        num = extract_numbers(text)
        if num is not None:
            return today - relativedelta(months=num * 3)

    elif 'years ago' in text:
        num = extract_numbers(text)
        if num is not None:
            return today - relativedelta(years=num)

    return text  # fallback: return original if nothing matched

file_path = base_path / "Scripts/translation_map.json"

def translate_with_cache(text_series, target_lang, use_cache=True):
    word_map = {}
    if use_cache and os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            word_map = json.load(f)

    def translate(text):
        try:
            if use_cache and text in word_map:
                return word_map[text]
            else:
                translation = GoogleTranslator(source='auto', target=target_lang).translate(text)
                if use_cache:
                    word_map[text] = translation
                    print(f"Translated '{text}' to {target_lang} as '{translation}' and cached it.")
                else:
                    print(f"Translated '{text}' to {target_lang} without caching.")
                return translation
        except Exception as e:
            print(f"Error translating '{text}': {e}")
            return text

    # Handle series or string
    if isinstance(text_series, pd.Series):
        result = text_series.apply(translate)
    else:
        result = translate(text_series)

    # Save updated cache after translation
    if use_cache:
        for key in list(word_map):
            value = word_map[key]
            if 'site' in value:
                word_map[key] = value.replace('site', 'web')

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(word_map, f, ensure_ascii=False, indent=2)

    # Handle series or string
    if isinstance(text_series, pd.Series):
        return text_series.apply(translate)
    else:
        return translate(text_series)

# --- Utility Functions ---

# Define your exchange rates (you can later fetch these live if needed)
exchange_rates = {
    "USD": 1.0,
    "EGP": 0.032,  # example rate
    "EUR": 1.07  # example rate
}


def extract_and_convert_budget(text):
    """
    Extracts numeric budget value from a text and converts to USD.
    Handles ranges like '1 - 5 EGP', or fixed values like '10 EUR'.
    """
    if not isinstance(text, str):
        return None

    text = text.strip()
    currency = None

    # Detect currency in text
    for cur in exchange_rates:
        if cur in text:
            currency = cur
            break

    if currency is None:
        return None  # No recognized currency

    # Remove everything except digits, dot, dash, and space
    cleaned = re.sub(r'[^0-9\.\-\s]', '', text)

    # Extract all numbers (for ranges or single values)
    matches = re.findall(r'\d+(?:\.\d+)?', cleaned)

    if not matches:
        return None

    nums = list(map(float, matches))

    # Average if it's a range, or take the single number
    value = sum(nums[:2]) / len(nums[:2])

    # Convert to USD
    return round(value * exchange_rates[currency], 2)

def process_file(df,column,function):
    df[f'{column}'] = df[f'{column}'].apply(function)
    return df
