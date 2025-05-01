import re
import pandas as pd


# Load the data
df = pd.read_csv("job_listings.csv")
df.insert(0, 'ID', range(1, len(df) + 1))

# Remove duplicates and add ID
df = df.drop_duplicates(subset=['Title','Link','client name','Type','Budget','Category','Date Posted'])

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


# --- Budget Cleaning ---
def process_file(df):
    df['Budget'] = df['Budget'].apply(extract_and_convert_budget)
    return df

df = process_file(df)

df['Category'] = df['Category'].str.strip(")")
df['Category'] = df['Category'].str.strip("(")

# If it's a column in your DataFrame:
df['Date Posted'] = df['Date Posted'].str.extract(r'(\d{2}-\d{2}-\d{4})')  # extract the date part
df['Date Posted'] = pd.to_datetime(df['Date Posted'], format='%d-%m-%Y')

# --- Save to CSV ---
df.to_csv("job_listings_cleaned.csv", index=False, encoding="utf-8-sig")

