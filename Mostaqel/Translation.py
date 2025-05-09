import pandas as pd
import json
import os
import re
from deep_translator import GoogleTranslator

# ---------- 1. Load existing translation map ----------
map_file = "../AllData/translation_map.json"

if os.path.exists(map_file):
    with open(map_file, "r", encoding="utf-8") as f:
        word_map = json.load(f)
else:
    word_map = {}

# ---------- 2. Load CSV file ----------
df = pd.read_csv("jobs_expanded.csv")

# ---------- 3. Detect if text is Arabic using Unicode range ----------
def is_arabic(text):
    return bool(re.search(r'[\u0600-\u06FF]', str(text)))

# ---------- 4. Translate with cache ----------
def translate_with_cache(text):
    try:
        if is_arabic(text):
            if text in word_map:
                return word_map[text]  # use cached version
            else:
                # Translate using Google Translate
                translation = GoogleTranslator(source='ar', target='en').translate(text)
                word_map[text] = translation
                print(f"Translated '{text}' to '{translation}' and cached it.")
                return translation
        else:
            return text  # not Arabic, return as-is
    except Exception as e:
        print(f"Error translating '{text}': {e}")
        return text

# ---------- 5. Translate and add new column ----------
df["Tags_en"] = df["Tags"].apply(translate_with_cache)

# ---------- 6. Clean up translations (replace 'site' with 'web') ----------
for key in list(word_map):
    value = word_map[key]
    if 'site' in value:
        word_map[key] = value.replace('site', 'web')

# ---------- 7. Save updated map ----------
with open(map_file, "w", encoding="utf-8") as f:
    json.dump(word_map, f, ensure_ascii=False, indent=2)

# ---------- 8. Save translated CSV ----------
df.to_csv("translated_output.csv", index=False, encoding="utf-8-sig")

print("✅ Translation complete. Output saved to 'translated_output.csv'")
