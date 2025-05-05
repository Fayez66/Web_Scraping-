import pandas as pd


df = pd.read_csv("Cleaned.csv")

# Split Skills only if not null
df['Skills'] = df['Skills'].apply(lambda x: x.split(',') if isinstance(x, str) else x)

# Strip whitespace if it's a list
df['Skills'] = df['Skills'].apply(lambda x: [tag.strip() for tag in x] if isinstance(x, list) else x)

# Explode into multiple rows
df = df.explode('Skills').reset_index(drop=False)
df.index = df.index + 1
df = df.drop(columns=['ID'])
df = df.rename(columns={'index': 'ID'})
# Save to new file
expanded = df[['ID' , 'Skills']]

expanded.loc[:, 'ID'] = expanded['ID'] + 1

expanded.index.name = 'index'
expanded.to_csv("jobs_expanded.csv", index=True, encoding="utf-8-sig")