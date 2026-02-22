import requests
import os
import sys

# Get secrets from GitHub Environment
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DATA_FILE = "comps.txt"
API_URL = "https://www.worldcubeassociation.org/api/v0/competitions?upcoming=true"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

# 1. Load seen IDs
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f: pass
with open(DATA_FILE, "r") as f:
    seen_names = set(line.strip() for line in f if line.strip())

# 2. Fetch Comps
try:
    response = requests.get(API_URL)
    comps = response.json()
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

# 3. Filter and Notify
new_found = False
for c in comps:
    # Filter for UK and check if new
    if c.get('country_iso2') == "GB" and c['name'] not in seen_names:
        name = c.get('name', 'N/A')
        city = c.get('city', 'N/A')
        date = c.get('start_date', 'N/A')
        reg_open = c.get('registration_open', 'Not set')
        link = c.get('url', f"https://www.worldcubeassociation.org/competitions/{c['id']}")

        message = (
            f"🇬🇧 *NEW UK COMP!*\n\n"
            f"🏆 *Name:* {name}\n"
            f"📍 *Location:* {city}\n"
            f"📅 *Date:* {date}\n"
            f"🕒 *Reg Opens:* {reg_open}\n\n"
            f"[Link]({link})"
        )
        
        send_telegram(message)
        
        # Add to local list to save later
        with open(DATA_FILE, "a") as f:
            f.write(c['id'] + "\n")
        new_found = True

if not new_found:
    print("No new UK competitions.")
