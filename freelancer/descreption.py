import pandas as pd

# Step 1: Load files
csv_df = pd.read_csv('Classified_Job_Descriptions.csv')
excel_df = pd.read_excel('description_category.xlsx')

# Step 2: Clean column names to avoid hidden spaces
csv_df.columns = csv_df.columns.str.strip()
excel_df.columns = excel_df.columns.str.strip()

# Step 3: Merge both files on 'ID'
merged_df = pd.merge(excel_df, csv_df[['ID', 'Reclassified_Category']], on='ID', how='left')

# Step 4: Create new column 'final_category'
merged_df['final_category'] = merged_df.apply(
    lambda row: row['Reclassified_Category'] if row['description_category'] == 'Other' else row['description_category'],
    axis=1
)

# Step 5: Save result
merged_df.to_csv('jobs_category.csv', index=False)
