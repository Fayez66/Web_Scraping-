import re
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta


def extract_numbers(text):
    """
    Extract and average numeric values from text.
    Handles ranges like '2 - 3' and avoids treating hyphens as negative signs.
    """
    if isinstance(text, (int, float)):
        return text

    # Replace dash variants with a space to split properly
    text = str(text).replace(',', '').replace('–', '-').replace('—', '-').strip()
    # Explicitly match ranges like '2 - 3' or '2 to 3'
    range_match = re.findall(r'\d+(?:\.\d+)?', text)

    if range_match:
        nums = list(map(float, range_match))
        if len(nums) == 1:
            return nums[0]
        elif len(nums) >= 2:
            return sum(nums[:2]) / 2  # average of first two numbers

    return None

print(extract_numbers("Est. budget:$3,500.00"))