import re
import pandas as pd
import datetime

# Load the data
df = pd.read_csv("job_listings.csv")


# Arabic label mapping
arabic_labels = {
    "Web Development": "تطوير الويب",
    "Mobile Development": "تطوير التطبيقات",
    "Cyber Security": "الأمن السيبراني",
    "Data Science": "علم البيانات",
    "Artificial Intelligence / Machine Learning": "الذكاء الاصطناعي / تعلم الآلة",
    "Software Engineering": "هندسة البرمجيات",
    "Database Management": "إدارة قواعد البيانات",
    "Cloud Computing": "الحوسبة السحابية",
    "Networking": "الشبكات",
    "DevOps": "ديف أوبس",
    "Game Development": "تطوير الألعاب",
    "ERP system": "تخطيط موارد المؤسسات",
    "IT Support": "دعم تكنولوجيا المعلومات",
    "system testing": "اختبار النظام",
    "Other": "أخرى"
}

# Create the Arabic category column
df['category_arabic'] = df['Category_English'].map(arabic_labels).fillna('غير معروف')

# Reorder columns to place 'category_arabic' right after 'Category_English'
cols = list(df.columns)
idx = cols.index('Category_English')
# Remove and reinsert at desired position
cols.insert(idx + 1, cols.pop(cols.index('category_arabic')))
df = df[cols]

# Remove duplicates and add ID
df = df.drop_duplicates(subset=[
    'Title',
    'Category_English',
    'Posted',
    'Avg offer',
    'Duration',
    'Number of Offers',
    'Tags',
    'Tags_en',
    'Link'
])
# --- Utility Functions ---

def extract_numbers(text):
    """
    Extract and average numeric values from text.
    Handles ranges like '2 - 3' and avoids treating hyphens as negative signs.
    """
    if isinstance(text, (int, float)):
        return text

    # Replace dash variants with a space to split properly
    text = str(text).replace('–', '-').replace('—', '-').strip()

    # Explicitly match ranges like '2 - 3' or '2 to 3'
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
    df['Duration'] = df['Duration'].apply(extract_numbers)
    return df

df = process_file(df)

# --- Date Parsing ---
def parse_posted_date(text):
    today = datetime.date.today()
    if not isinstance(text, str):
        return text

    text = text.lower()

    if any(unit in text for unit in ['دقيقة', 'ساعة','ساعتين','ساعات']):
        return today
    elif 'يوم' in text:
        return today - datetime.timedelta(days=1)
    elif 'يومين' in text :
        return today - datetime.timedelta(days=2)
    elif 'يوما' in text or 'أيام' in text:
        return today - datetime.timedelta(days=extract_numbers(text))
    return text

df['Posted'] = df['Posted'].apply(parse_posted_date)

df['Avg offer'] = df['Avg offer'].str.strip('$')
df.rename(columns={'Duration': 'Duration(Days)'}, inplace=True)
df['Tags_en'] = df['Tags_en'].str.replace(r'[\u0600-\u06FF]', '', regex=True).str.strip()

# --- Save to CSV ---
df.to_csv("job_listings_cleaned.csv", index=False, encoding="utf-8-sig")

# Split both columns only if not null
df['Tags'] = df['Tags'].apply(lambda x: x.split(',') if isinstance(x, str) else x)
df['Tags_en'] = df['Tags_en'].apply(lambda x: x.split(',') if isinstance(x, str) else x)

# Strip whitespace in both columns
df['Tags'] = df['Tags'].apply(lambda x: [tag.strip() for tag in x] if isinstance(x, list) else x)
df['Tags_en'] = df['Tags_en'].apply(lambda x: [skill.strip() for skill in x] if isinstance(x, list) else x)

# Ensure both columns have the same number of elements per row
df = df[df['Tags'].str.len() == df['Tags_en'].str.len()]

# Convert both columns to Series and explode together
df = df.explode(['Tags', 'Tags_en']).reset_index(drop=True)

# Save to new file
df.to_csv("jobs_expanded.csv", index=False, encoding="utf-8-sig")
