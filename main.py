import requests
import os
import sys
import datetime

# Get secrets from GitHub Environment
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DATA_FILE = "comps.txt"

# --- PAGINATION FIX ---
# We use 'per_page=100' to get more results at once.
# We use 'start=' with today's date so we don't miss upcoming ones.
today = datetime.date.today().isoformat()
API_URL = "https://www.worldcubeassociation.org/api/v0/competitions?region=United+Kingdom&per_page=100"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram error: {e}")

# Load existing comps
if not os.path.exists(DATA_FILE):
    open(DATA_FILE, "w").close()
with open(DATA_FILE, "r") as f:
    seen_ids = set(line.strip() for line in f if line.strip())

try:
    print(f"Fetching from: {API_URL}")
    response = requests.get(API_URL)
    comps = response.json()
except Exception as e:
    print(f"API Error: {e}")
    sys.exit(1)

new_found = False
for c in comps:
    comp_id = c['id']
    
    # Filter: Must be UK (GB) and not already seen
    if c.get('country_iso2') == "GB" and comp_id not in seen_ids:
        name = c.get('name', 'N/A')
        city = c.get('city', 'N/A')
        date = c.get('start_date', 'N/A')
        reg_open = c.get('registration_open', 'Not set')
        link = c.get('url', f"https://www.worldcubeassociation.org/competitions/{comp_id}")


    

        message = (
            f"NEW UK COMP!\n\n"
            f"🏆 *Name:* {name}\n"
            f"📍 *Location:* {city}\n"
            f"📅 *Date:* {date}\n"
            f"🕒 *Reg Opens:* {reg_open}\n\n"
            f"[View Competition]({link})"
        )
        
        send_telegram(message)
        
        with open(DATA_FILE, "a") as f:
            f.write(comp_id + "\n")
        seen_ids.add(comp_id) # Prevent duplicates in same run
        new_found = True

if not new_found:
    print(f"Checked {len(comps)} total comps. No new UK ones found.")
