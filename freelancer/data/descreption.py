import pandas as pd

# Load the CSV files
desc_cat_df = pd.read_csv('description_category.csv', encoding='ISO-8859-1')
classified_df = pd.read_csv('Classified_Job_Descriptions.csv', encoding='ISO-8859-1')

# Ensure ID is the same type
desc_cat_df['ID'] = desc_cat_df['ID'].astype(str)
classified_df['ID'] = classified_df['ID'].astype(str)

# Merge on ID to bring Reclassified_Category into desc_cat_df
merged_df = desc_cat_df.merge(
    classified_df[['ID', 'Reclassified_Category']], on='ID', how='left'
)

# Create a new column: Updated_Category
def update_category(row):
    if row['Category'] == 'Other' and pd.notna(row['Reclassified_Category']):
        return row['Reclassified_Category']
    return row['Category']

merged_df['Updated_Category'] = merged_df.apply(update_category, axis=1)

# Save the updated dataframe
merged_df.to_csv('updated_description_category.csv', index=False)
print("'Updated_Category' column added and saved.")
