import pandas as pd
import requests
import urllib.parse
import sys
import time
import os

sys.stdout.reconfigure(line_buffering=True)

API_KEY = "e0da6f22bda6c4fcc8fa7d49a518f4ab58ec87d403dbc39bca55a090c54ef76b"
FILE_NAME = 'Verified_Dataset_Links_Updated_Final.xlsx'

df = pd.read_excel(FILE_NAME)

def extract_source(url):
    if pd.isna(url) or not isinstance(url, str):
        return "Unknown"
    try:
        domain = urllib.parse.urlparse(url).netloc
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return "Unknown"

source_mapping = {
    'rbi.org.in': 'Reserve Bank of India (RBI)',
    'sebi.gov.in': 'SEBI',
    'pib.gov.in': 'Press Information Bureau (PIB)',
    'economictimes.indiatimes.com': 'The Economic Times',
    'timesofindia.indiatimes.com': 'The Times of India',
    'thehindu.com': 'The Hindu',
    'business-standard.com': 'Business Standard',
    'livemint.com': 'LiveMint',
    'moneycontrol.com': 'Moneycontrol',
    'cnbctv18.com': 'CNBC TV18',
    'financialexpress.com': 'Financial Express',
    'indianexpress.com': 'The Indian Express',
    'ndtv.com': 'NDTV',
    'hindustantimes.com': 'Hindustan Times',
    'news18.com': 'News18',
    'indiatoday.in': 'India Today'
}

missing_indices = df[df['Link of Evidence'].isna()].index
print(f'Starting SerpApi search for {len(missing_indices)} missing links...')

processed_count = 0
for idx in missing_indices:
    claim = df.at[idx, 'Claim']
    query = claim[:150]
    
    url = f"https://serpapi.com/search.json?engine=google&q={urllib.parse.quote(query)}&api_key={API_KEY}"
    
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        
        if 'error' in data:
            print(f"SerpApi Error at row {idx}: {data['error']}")
            break # likely hit API limit, stop trying
            
        if 'organic_results' in data and len(data['organic_results']) > 0:
            found_url = data['organic_results'][0]['link']
            df.at[idx, 'Link of Evidence'] = found_url
            
            raw_source = extract_source(found_url)
            df.at[idx, 'Source'] = source_mapping.get(raw_source, raw_source)
            
    except Exception as e:
        print(f'Exception at row {idx}: {e}')
        
    processed_count += 1
    if processed_count % 10 == 0:
        print(f'Processed {processed_count}/{len(missing_indices)}...')
        # Save periodically so we don't lose data
        try:
            df.to_excel(FILE_NAME, index=False)
        except Exception as save_err:
            print(f"Failed to auto-save: {save_err}")
            
    time.sleep(0.5)

try:
    df.to_excel(FILE_NAME, index=False)
    print(f'\nFinished! Remaining missing links: {df["Link of Evidence"].isna().sum()}')
    print(f'Saved to {FILE_NAME}')
except Exception as e:
    print(f'FATAL SAVE ERROR: {e}')
    # save to a backup if the main file is locked
    df.to_excel('Backup_Dataset.xlsx', index=False)
    print('Saved to Backup_Dataset.xlsx instead!')
