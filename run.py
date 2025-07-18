import asyncio
from py_lead_generation.src.google_maps.selenium_engine import GoogleMapsSeleniumEngine
import csv
import os

QUERIES = [
    ("coworking spaces", "Kansas City"),
    ("law offices", "Kansas City"),
    ("medical clinics", "Kansas City"),
    ("chiropractor offices", "Kansas City"),
    ("dentist offices", "Kansas City"),
    ("office buildings", "Kansas City"),
    ("daycare centers", "Kansas City"),
    ("fitness centers", "Kansas City"),
    ("retail stores", "Kansas City"),
    ("auto dealerships", "Kansas City"),
    ("apartment complexes", "Kansas City"),
    ("property management", "Kansas City"),
    ("real estate offices", "Kansas City"),
]

def slugify(text):
    return text.lower().replace(' ', '_').replace(',', '').replace('-', '').replace('&', 'and')

def main():
    all_rows = []
    master_fieldnames = ['QueryType', 'Title', 'Address', 'PhoneNumber', 'WebsiteURL']
    for query, location in QUERIES:
        print(f"[INFO] Searching for: {query} in {location}")
        engine = GoogleMapsSeleniumEngine(query, location, headless=False)
        engine.run()
        filename = f"{slugify(query)}_{slugify(location)}.csv"
        engine.save_to_csv(filename)
        print(f"[INFO] Saved {len(engine.entries)} results to {filename}\n")
        # Read rows and add query type
        with open(filename, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['QueryType'] = query
                all_rows.append(row)
    # Write master CSV
    master_csv = 'all_kansas_city_leads.csv'
    with open(master_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=master_fieldnames)
        writer.writeheader()
        for row in all_rows:
            writer.writerow(row)
    print(f"[INFO] Compiled all leads into {master_csv} ({len(all_rows)} rows)")

if __name__ == '__main__':
    main()
