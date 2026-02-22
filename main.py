import requests
import os
import sys
import datetime

# Get secrets from GitHub Environment
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DATA_FILE = "comps.txt"

today = datetime.date.today().isoformat()

# API URL: Specifically for the UK, fetching 100 results to ensure we see everything
API_URL = f"https://www.worldcubeassociation.org/api/v0/competitions?country_iso2=GB&start_date={today}&per_page=100"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram error: {e}")

# 1. Load the seen IDs from the text file
if not os.path.exists(DATA_FILE):
    open(DATA_FILE, "w").close()

with open(DATA_FILE, "r") as f:
    seen_ids = set(line.strip() for line in f if line.strip())

# 2. Fetch the data from the WCA
try:
    print(f"Checking UK competition list...")
    response = requests.get(API_URL)
    response.raise_for_status()
    comps = response.json()
except Exception as e:
    print(f"API Error: {e}")
    sys.exit(1)

# 3. Process the results
new_found_count = 0
for c in comps:
    comp_id = c.get('id')
    
    # If the ID is not in our seen_ids list, it's a new one!
    if comp_id and comp_id not in seen_ids:
        name = c.get('name', 'N/A')
        city = c.get('city', 'N/A')
        date = c.get('start_date', 'N/A')
        reg_open = c.get('registration_open', 'Not set')
        link = c.get('url', f"https://www.worldcubeassociation.org/competitions/{comp_id}")

        # Simple, standard message for every UK comp
        message = (
            "🇬🇧 *NEW UK COMPETITION!*\n\n"
            f"🏆 *Name:* {name}\n"
            f"📍 *Location:* {city}\n"
            f"📅 *Date:* {date}\n"
            f"🕒 *Reg Opens:* {reg_open}\n\n"
            f"[View Details on WCA]({link})"
        )
        
        send_telegram(message)
        
        # Add to the file so we don't notify again
        with open(DATA_FILE, "a") as f:
            f.write(comp_id + "\n")
        seen_ids.add(comp_id)
        new_found_count += 1

print(f"Process complete. Found {new_found_count} new competitions.")
