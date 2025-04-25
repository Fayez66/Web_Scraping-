'''#Containers for data
titles = []
links = []
times_ = []
descriptions = []
budgets = []
experience_levels = []
tags = []
field = []
job_type = []
duration = []

page = 1
path = r"E:\Apps\chromedriver-win64\chromedriver.exe"
url = f"https://mostaql.com/projects?page={page}>&category=development&budget_max=10000&sort=latest"

data = {
    "ID": list(range(1, len(titles) + 1)),
    'Category': field,
    'job_type': job_type,
    "Title": titles,
    "Posted": times_,
    "Experience Level": experience_levels,
    "Budget": budgets,
    'duration': duration,
    "Tags": [", ".join(tag_list) for tag_list in tags],
    "Link": links,
}
df = pd.DataFrame(data)
df.to_csv(r"E:\Apps\GItHubRebo\Web_Scraping-\Upwork\job_listings.csv", index=False, encoding="utf-8-sig")

desc_data = {
    "ID": list(range(1, len(titles) + 1)),
    "Description": descriptions,
}
df_desc = pd.DataFrame(desc_data)
df_desc.to_csv(r"E:\Apps\GItHubRebo\Web_Scraping-\Upwork\Description.csv", index=False, encoding="utf-8-sig")'''