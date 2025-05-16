import pandas as pd
from pathlib import Path

def create_titles_website_df():
    base_path = Path(__file__).resolve().parents[1]
    files_websites = {
        r"E:\Apps\GItHubRebo\Web_Scraping-\Data\UpWork.csv": "UpWork",
        r"E:\Apps\GItHubRebo\Web_Scraping-\Data\Freelancer.csv": "Freelancer",
        r"E:\Apps\GItHubRebo\Web_Scraping-\Data\FreelanceYard.csv": "FreelanceYard",
        r"E:\Apps\GItHubRebo\Web_Scraping-\Data\Mostaqel.csv": "Mostaqel",
    }

    final_df = pd.DataFrame(columns=["ID", "Website", "Category", "Title", "Type", "Budget", "Posted", "Link"])
    current_id = 1

    for file_path_str, website_name in files_websites.items():
        file_path = Path(file_path_str)
        try:
            df = pd.read_csv(file_path, encoding="utf-8-sig")

            titles = df['Title'].astype(str) if 'Title' in df else pd.Series([], dtype=str)

            category = df['Category.1'] if 'Category.1' in df else df['Category_English']
            category = category.astype(str)
            if 'Posted' in df:
                posted = df['Posted'].astype(str)
            elif 'Date Posted' in df:
                posted = df['Date Posted'].astype(str)
            else:
                posted = pd.Series([""] * len(df), dtype=str)  # fallback if neither exists

            links = df['Link'].astype(str) if 'Link' in df else pd.Series([], dtype=str)
            budget = (
                df['budget'].astype(str) if 'budget' in df
                else df['Budget'].astype(str) if 'Budget' in df
                else df['Price'].astype(str) if 'Price' in df
                else pd.Series([""] * len(df), dtype=str)
            )
            # if website_name == 'Freelancer':
            #     budget = df['Price'].astype(str) if 'Price' in df else pd.Series([], dtype=str)
            # else:
            #     budget = df['budget'].astype(str) if 'Budget' in df else pd.Series([], dtype=str)
            if website_name == 'Freelancer' or website_name == 'UpWork':
                if 'job_type' in df:
                    job_type = df['job_type'].astype(str)
                elif 'Type' in df:
                    job_type = df['Type'].astype(str)
            else:
                job_type = pd.Series(["Fixed price"] * len(df), dtype=str)  # fallback if neither exists

            rows_count = len(titles)
            website_df = pd.DataFrame({
                "ID": list(range(current_id, current_id + rows_count)),
                "Title": titles,
                "Website": [website_name] * rows_count,
                "Category": category[:rows_count],
                "Type": job_type[:rows_count],
                "Budget": budget[:rows_count],
                "Posted": posted[:rows_count],
                "Link": links[:rows_count],
            })

            final_df = pd.concat([final_df, website_df], ignore_index=True)
            current_id += rows_count

            print(f"✔ Loaded {website_name} with {rows_count} titles")

        except Exception as e:
            print(f"⚠ Failed to load {file_path.name}: {e}")

    # Save the file
    output_path = base_path / "Data/ALL_DATA.csv"
    try:
        final_df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"\n Saved combined titles file with {len(final_df)} jobs at:\n{output_path}")
    except Exception as e:
        print(f" Failed to save file: {e}")

    return final_df

if __name__ == "__main__":
    df_titles_websites = create_titles_website_df()
    print(df_titles_websites.head())
