import re
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta

df = pd.read_csv("job_listings_cleaned.csv")

# Split tags only if not null
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
