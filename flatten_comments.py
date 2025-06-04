import pandas as pd
import re

df = pd.read_excel('test1.xlsx')

pattern = r'(?:^|\n)(\d{1,2}[A-Za-z-]+\d{2,5}\s+[A-Z]{2}[: -])'

def split_comments(text):
    if not isinstance(text, str):
        return [text]
    parts = re.split(pattern, text)
    if len(parts) == 1:
        return [text.strip()]
    comments = []
    for i in range(1, len(parts), 2):
        start = parts[i].strip()
        body = parts[i+1].strip()
        comments.append(f"{start} {body}".strip())
    return comments

rows = []
for _, row in df.iterrows():
    for comment in split_comments(row['AbbVie Response (include date and initials)']):
        new_row = row.copy()
        new_row['AbbVie Response (include date and initials)'] = comment
        rows.append(new_row)

flat_df = pd.DataFrame(rows)
print(flat_df)
