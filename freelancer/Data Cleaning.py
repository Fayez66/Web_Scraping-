import re
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta

df = pd.read_csv("job_listings.csv")

# Remove duplicates and add ID
df = df.drop_duplicates(subset=['Title'])
df['ID'] = range(1, len(df) + 1)

last_col = df.columns[-1]
df = df[[last_col] + list(df.columns[:-1])]

print(df)