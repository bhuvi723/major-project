import json
import csv

# Read the mf.json file
with open('mf.json', 'r') as file:
    data = json.load(file)

# Create a CSV file with schemeCode and schemeName
with open('mutual_funds.csv', 'w', newline='', encoding='utf-8') as csvfile:
    # Create a CSV writer
    csv_writer = csv.writer(csvfile)
    
    # Write the header
    csv_writer.writerow(['schemeCode', 'schemeName'])
    
    # Write the data
    for scheme in data:
        csv_writer.writerow([scheme['schemeCode'], scheme['schemeName']])

print(f"Successfully extracted {len(data)} mutual fund schemes to mutual_funds.csv")
