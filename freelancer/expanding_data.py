import pandas as pd


df = pd.read_csv("Cleaned.csv")

# Split Skills only if not null
df['Skills'] = df['Skills'].apply(lambda x: x.split(',') if isinstance(x, str) else x)

# Strip whitespace if it's a list
df['Skills'] = df['Skills'].apply(lambda x: [tag.strip() for tag in x] if isinstance(x, list) else x)

# Explode into multiple rows
df = df.explode('Skills').reset_index(drop=True)

# Save to new file
df.to_csv("jobs_expanded.csv", index=False, encoding="utf-8-sig")
