import re
import pandas as pd
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta

df = pd.read_csv("job_listings.csv")

# Remove duplicates and add ID
df = df.drop_duplicates(subset=['Title'])
df['ID'] = range(1, len(df) + 1)

last_col = df.columns[-1]
df = df[[last_col] + list(df.columns[:-1])]

df.rename(columns={'Days Left to pid': 'Days Left to Bid'}, inplace=True)
#
#
df.dropna(subset=['Bids', 'Price'], inplace=True)
#
#
df = df[~df['Title'].str.contains("Private project or contest", case=False, na=False)]
#

df['Bids'] = df['Bids'].astype(str).apply(lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0)


# Clean 'Days Left to pid' column:
# Replace hours with 0, extract days, convert to int

# df['Days Left to Bid'] = df['Days Left to Bid'].apply(
#     lambda x: 0 if pd.isna(x) or 'hour' in x.lower() else int(re.search(r'\d+', x).group())
# )


def extract_value(column):
    # Regex to match values followed by hours (e.g., '6 days', '2 hours', etc.)
    match = re.search(r'(\d+)\s*(days?|hours?)', column, re.IGNORECASE)

    if match:
        value = int(match.group(1))  # Extract the numerical value

        # Check if the match contains 'hours'
        if 'hour' in match.group(2).lower():
            value = 0  # Replace with 0 if hours are found

        return value
    else:
        return None  # If no match is found


# Example usage:

df['Days Left to Bid'] = df['Days Left to Bid'].apply(extract_value)


def clean_price(value):
    # Remove dollar signs and text (keep only digits, dot, and dash)
    cleaned = re.sub(r'[^0-9\-.]', '', str(value))

    if '-' in cleaned:
        parts = cleaned.split('-')
        try:
            return (float(parts[0]) + float(parts[1])) / 2
        except:
            return None
    else:
        try:
            return float(cleaned)
        except:
            return None


# Apply the cleaning function to the 'Price' column
df['Price'] = df['Price'].apply(clean_price)
print(df.info())
df.to_csv("Cleaned.csv", index=False, encoding="utf-8-sig")