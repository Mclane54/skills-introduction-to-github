import pandas as pd
import re
from datetime import date

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

def extract_dates(text):
    """Return comma-separated dates if keywords present.

    Handles shorthand like "06, 07 May2022" by inferring month/year
    from the nearest reference.
    """
    if not isinstance(text, str):
        return ""

    keywords = ["temp log", "log missing", "logs not found", "te>", "te<"]
    lowered = text.lower()
    if not any(k in lowered for k in keywords):
        return ""

    search_text = text.split(":", 1)[1] if ":" in text else text
    tokens = re.split(r"[\s,]+", search_text)

    months = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    }

    current_month = None
    current_year = None
    pending = []
    dates = []

    i = 0
    while i < len(tokens):
        token = tokens[i].strip().strip(".").strip(":")
        i += 1
        if not token:
            continue

        m = re.match(r"(\d{1,2})([A-Za-z]{3,})(\d{4})$", token)
        if m:
            day = int(m.group(1))
            month = months.get(m.group(2)[:3].lower())
            year = int(m.group(3))
            current_month = month
            current_year = year
            for d in pending:
                if month and year:
                    dates.append(date(year, month, d))
            pending.clear()
            if month and year:
                dates.append(date(year, month, day))
            continue

        m = re.match(r"(\d{1,2})([A-Za-z]{3,})$", token)
        if m and not token.isdigit():
            day = int(m.group(1))
            month = months.get(m.group(2)[:3].lower())
            year = current_year or 2022
            current_month = month
            if month and year:
                dates.append(date(year, month, day))
            continue

        m = re.match(r"([A-Za-z]{3,})(\d{4})$", token)
        if m:
            month = months.get(m.group(1)[:3].lower())
            year = int(m.group(2))
            current_month = month
            current_year = year
            for d in pending:
                if month and year:
                    dates.append(date(year, month, d))
            pending.clear()
            continue

        if token[:3].lower() in months:
            month = months[token[:3].lower()]
            current_month = month
            if i < len(tokens) and tokens[i].isdigit() and len(tokens[i]) == 4:
                current_year = int(tokens[i])
                i += 1
                for d in pending:
                    dates.append(date(current_year, current_month, d))
                pending.clear()
            continue

        if token.isdigit() and len(token) == 4:
            current_year = int(token)
            for d in pending:
                if current_month:
                    dates.append(date(current_year, current_month, d))
            pending.clear()
            continue

        if token.isdigit():
            pending.append(int(token))

    if current_month and current_year:
        for d in pending:
            dates.append(date(current_year, current_month, d))

    unique_sorted = sorted(set(dates))
    return ", ".join(dt.strftime("%Y-%m-%d") for dt in unique_sorted)

rows = []
for _, row in df.iterrows():
    for comment in split_comments(row['AbbVie Response (include date and initials)']):
        new_row = row.copy()
        new_row['AbbVie Response (include date and initials)'] = comment
        new_row['Missing Log Dates'] = extract_dates(comment)
        rows.append(new_row)

flat_df = pd.DataFrame(rows)
print(flat_df)
