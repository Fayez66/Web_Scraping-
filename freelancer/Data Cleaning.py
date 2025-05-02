import re
import pandas as pd


# Load dataset
df = pd.read_csv("job_listings.csv")

# Assign unique ID
df['ID'] = range(1, len(df) + 1)

# Remove duplicates based on 'Title'
df = df.drop_duplicates(subset=['Title'])

# Move the last column to the front
last_col = df.columns[-1]
df = df[[last_col] + list(df.columns[:-1])]

# Rename column for consistency
df.rename(columns={'Days Left to pid': 'Days Left to Bid'}, inplace=True)

# Drop rows with missing Bids or Price
df.dropna(subset=['Bids', 'Price'], inplace=True)

# Remove entries that indicate private projects or contests
df = df[~df['Title'].str.contains("Private project or contest", case=False, na=False)]

# Extract numeric values from Bids
df['Bids'] = df['Bids'].astype(str).apply(
    lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0
)

def extract_value(column: str) -> int | None:
    """
    Extract the number of days from a text string. If 'hour' is found, return 0.
    Returns None if no match is found.
    """
    match = re.search(r'(\d+)\s*(days?|hours?)', column, re.IGNORECASE)
    if match:
        value = int(match.group(1))
        if 'hour' in match.group(2).lower():
            return 0
        return value
    return None

# Apply extraction logic to 'Days Left to Bid'
df['Days Left to Bid'] = df['Days Left to Bid'].apply(extract_value)

def clean_price(value: str) -> float | None:
    """
    Cleans a price string by removing currency symbols and text.
    If the string contains a range, returns the average of the two numbers.
    """
    cleaned = re.sub(r'[^0-9\-.]', '', str(value))
    if '-' in cleaned:
        parts = cleaned.split('-')
        try:
            return (float(parts[0]) + float(parts[1])) / 2
        except (ValueError, IndexError):
            return None
    try:
        return float(cleaned)
    except ValueError:
        return None

# Apply price cleaning
df['Price'] = df['Price'].apply(clean_price)

# Display info and export cleaned data
print(df.info())



#Load the CSV files
job_df = df
classified_df = pd.read_csv('jobs_category.csv')

# Merge category from classified_df into job_df based on ID
merged_df = job_df.merge(classified_df[['ID', 'Category']], on='ID', how='left')

# Save the result

merged_df.to_csv("Cleaned.csv", index=False, encoding="utf-8-sig")


