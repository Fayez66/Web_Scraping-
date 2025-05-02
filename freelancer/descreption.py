import pandas as pd

# Load the files
classified_df = pd.read_csv('Classified_Job_Descriptions.csv')
desc_cat_df = pd.read_excel('description_category.xlsx')

# Ensure IDs match in type
classified_df['ID'] = classified_df['ID'].astype(str)
desc_cat_df['ID'] = desc_cat_df['ID'].astype(str)

# Merge the two DataFrames on ID
merged_df = classified_df.merge(desc_cat_df[['ID', 'Category']], on='ID', how='left')

# Replace 'others' or NaN in Reclassified_Category with Category
def replace_if_needed(row):
    if row['Reclassified_Category'] == 'others' or pd.isna(row['Reclassified_Category']):
        return row['Category']
    return row['Reclassified_Category']

merged_df['Reclassified_Category'] = merged_df.apply(replace_if_needed, axis=1)

# Drop helper column
merged_df = merged_df.drop(columns=['Category_y'])

# Save result
merged_df.to_csv('updated_classified_descriptions.csv', index=False)
print("Reclassified_Category column updated and saved.")
