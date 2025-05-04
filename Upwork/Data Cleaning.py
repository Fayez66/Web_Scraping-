import re
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta

# Load the data
df = pd.read_csv("job_listings.csv")

# Remove duplicates and add ID
df = df.drop_duplicates(subset=['Title'])
df['ID'] = range(1, len(df) + 1)

# --- Utility Functions ---

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

# --- Budget Cleaning ---
def process_file(df):
    df['est. budget'] = df['est. budget'].apply(extract_numbers)
    df['Budget'] = df['Budget'].apply(extract_numbers)
    return df

df = process_file(df)

# --- Job Type Simplification ---
def simplify_job_type(text):
    if isinstance(text, str) and 'Hourly' in text:
        return text[:6]
    return text

df['job_type'] = df['job_type'].apply(simplify_job_type)

# --- Date Parsing ---
def parse_posted_date(text):
    today = datetime.date.today()
    if not isinstance(text, str):
        return text

    text = text.lower()

    if any(unit in text for unit in ['second', 'minute', 'hour']):
        return today
    elif 'yesterday' in text:
        return today - datetime.timedelta(days=1)
    elif 'last week' in text:
        return today - datetime.timedelta(weeks=1)
    elif 'last month' in text:
        return today - relativedelta(months=1)
    elif 'last quarter' in text:
        return today - relativedelta(months=3)
    elif 'last year' in text:
        return today - relativedelta(years=1)
    elif 'days ago' in text:
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

df['Posted'] = df['Posted'].apply(parse_posted_date)

# --- Duration Split ---
df[['est. time', 'hours/week']] = df['duration'].str.split(',', n=1, expand=True)
df['est. time'] = df['est. time'].str.strip()
df['hours/week'] = df['hours/week'].str.strip()

# --- Reorder Columns ---
cols = df.columns.tolist()
duration_index = cols.index('duration')
cols.insert(duration_index , cols.pop(cols.index('est. time')))
cols.insert(duration_index +1, cols.pop(cols.index('hours/week')))
df = df[cols]

# --- Normalize hours/week ---
def normalize_hours(text):
    if not isinstance(text, str):
        return None
    if 'Not sure' in text or 'Hours to be determined' in text:
        return None
    elif 'Less than' in text:
        return '<30'
    elif '30+' in text:
        return '>30'
    return text

df['hours/week'] = df['hours/week'].apply(normalize_hours)

# --- Normalize duration ---
def normalize_duration(text):
    if not isinstance(text, str):
        return None
    if 'Less than' in text:
        return '<1'
    elif 'More than' in text:
        return '>6'
    elif 'to' in text:
        text = text.replace('to', '-')
        return extract_numbers(text)
    return text

df['duration'] = df['duration'].apply(normalize_duration)

# --- Save to CSV ---
df.to_csv("job_listings_cleaned.csv", index=False, encoding="utf-8-sig")

df['Tags'] = df['Tags'].apply(lambda x: x.split(',') if isinstance(x, str) else x)

# Strip whitespace if it's a list
df['Tags'] = df['Tags'].apply(lambda x: [tag.strip() for tag in x] if isinstance(x, list) else x)

# Explode into multiple rows
df = df.explode('Tags').reset_index(drop=False)
df.index = df.index + 1
df = df.drop(columns=['ID'])
df = df.rename(columns={'index': 'ID'})
# Save to new file
df.to_csv("jobs_expanded.csv", index=False, encoding="utf-8-sig")

