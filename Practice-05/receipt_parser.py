import re
import json

with open("raw.txt", "r", encoding="utf-8") as f:
    text = f.read()

# --- Extract product names ---
products = re.findall(r'\d+\.\s*\n([^\n]+)', text)

# --- Extract prices ---
prices = re.findall(r'Стоимость\s*\n([\d\s]+,\d{2})', text)

# Convert prices to float
prices_float = [float(p.replace(" ", "").replace(",", ".")) for p in prices]

# --- Extract total ---
total_match = re.search(r'ИТОГО:\s*\n?([\d\s]+,\d{2})', text)
total = total_match.group(1) if total_match else None

# --- Extract date and time ---
datetime_match = re.search(r'(\d{2}\.\d{2}\.\d{4})\s+(\d{2}:\d{2}:\d{2})', text)
date = datetime_match.group(1) if datetime_match else None
time = datetime_match.group(2) if datetime_match else None

# --- Extract payment method ---
payment_match = re.search(r'Банковская карта', text)
payment_method = payment_match.group() if payment_match else None

# --- Structured output ---
data = {
    "products": products,
    "prices": prices,
    "calculated_total": sum(prices_float),
    "receipt_total": total,
    "date": date,
    "time": time,
    "payment_method": payment_method
}

print(json.dumps(data, indent=4, ensure_ascii=False))