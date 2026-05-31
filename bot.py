import discord
import asyncio
import aiohttp
import json
import os
import hashlib
from bs4 import BeautifulSoup
from datetime import datetime

# ==================== CONFIGURATION ====================
BOT_TOKEN = BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = 1158055385958199360
CHECK_INTERVAL = 600  # Check every 10 minutes (in seconds)

# ==================== DEALER CONFIG ====================
# Logo files should be placed in a "logos" folder next to this script
# Name them exactly as shown in "logo_file" below
DEALERS = [
    {
        "name": "The Ruptured Duck",
        "url": "https://www.therupturedduck.com/collections/recently-added-items",
        "logo_file": "ruptured_duck.png",
        "item_selector": ".product-item",
        "link_selector": "a",
        "base_url": "https://www.therupturedduck.com"
    },
    {
        "name": "War's End Shop",
        "url": "https://www.warsendshop.com/collections/new-items",
        "logo_file": "warsend.png",
        "item_selector": ".product-item",
        "link_selector": "a",
        "base_url": "https://www.warsendshop.com"
    },
    {
        "name": "Weitze Militaria",
        "url": "https://www.weitze.com/neuheiten.html#?n=mi,,",
        "logo_file": "weitze.png",
        "item_selector": ".artikel",
        "link_selector": "a",
        "base_url": "https://www.weitze.com"
    },
    {
        "name": "Lakeside Trader",
        "url": "https://www.lakesidetrader.com/recently-added-items/",
        "logo_file": "lakeside.png",
        "item_selector": ".product",
        "link_selector": "a",
        "base_url": "https://www.lakesidetrader.com"
    },
    {
        "name": "Dutch Militaria",
        "url": "https://dutchmilitaria.com/",
        "logo_file": "dutch_militaria.png",
        "item_selector": ".product",
        "link_selector": "a",
        "base_url": "https://dutchmilitaria.com"
    },
    {
        "name": "Linda Mae Militaria",
        "url": "https://lindamaemilitaria.com/",
        "logo_file": "lindamae.png",
        "item_selector": ".product",
        "link_selector": "a",
        "base_url": "https://lindamaemilitaria.com"
    },
    {
        "name": "Militaria Sales",
        "url": "https://www.militariasales.com/new-item/",
        "logo_file": "militaria_sales.png",
        "item_selector": ".product",
        "link_selector": "a",
        "base_url": "https://www.militariasales.com"
    },
    {
        "name": "Military Collectibles",
        "url": "https://militarycollectibles.com/shop?s=n",
        "logo_file": "military_collectibles.png",
        "item_selector": ".product",
        "link_selector": "a",
        "base_url": "https://militarycollectibles.com"
    },
    {
        "name": "Military Collectors HQ",
        "url": "https://militarycollectorshq.com/store-catalog",
        "logo_file": "militarycollectorshq.png",
        "item_selector": ".product",
        "link_selector": "a",
        "base_url": "https://militarycollectorshq.com"
    },
]

# ==================== BOT SETUP ====================
intents = discord.Intents.default()
client = discord.Client(intents=intents)

SEEN_FILE = "seen_items.json"

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return json.load(f)
    return {}

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(seen, f)

def hash_page(content):
    return hashlib.md5(content.encode()).hexdigest()

async def fetch_page(session, url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status == 200:
                return await resp.text()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None

async def check_dealer(session, dealer, seen, channel):
    name = dealer["name"]
    url = dealer["url"]
    logo_file = os.path.join("logos", dealer["logo_file"])

    html = await fetch_page(session, url)
    if not html:
        print(f"[{name}] Could not fetch page.")
        return

    page_hash = hash_page(html)
    old_hash = seen.get(name)

    if old_hash is None:
        # First run — just save the hash, don't alert
        seen[name] = page_hash
        print(f"[{name}] First check — saved baseline.")
        return

    if page_hash != old_hash:
        seen[name] = page_hash
        print(f"[{name}] NEW ITEMS DETECTED — sending alert!")

        embed = discord.Embed(
            title=f"🆕 New Items at {name}!",
            description=f"New items have been added to [{name}]({url})\n\n[**Click here to view new items →**]({url})",
            color=discord.Color.dark_gold(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Militaria Alerts Bot")

        file = None
        if os.path.exists(logo_file):
            file = discord.File(logo_file, filename="logo.png")
            embed.set_thumbnail(url="attachment://logo.png")
        else:
            print(f"[{name}] Logo not found at {logo_file} — sending without logo.")

        try:
            if file:
                await channel.send(file=file, embed=embed)
            else:
                await channel.send(embed=embed)
        except Exception as e:
            print(f"[{name}] Failed to send message: {e}")
    else:
        print(f"[{name}] No changes detected.")

async def check_all_dealers():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    if not channel:
        print("ERROR: Could not find channel. Check your CHANNEL_ID.")
        return

    print(f"Bot ready! Monitoring {len(DEALERS)} dealers. Checking every {CHECK_INTERVAL//60} minutes.")

    while not client.is_closed():
        print(f"\n--- Checking dealers at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
        seen = load_seen()

        async with aiohttp.ClientSession() as session:
            for dealer in DEALERS:
                await check_dealer(session, dealer, seen, channel)
                await asyncio.sleep(2)  # Be polite between requests

        save_seen(seen)
        print(f"--- Done. Next check in {CHECK_INTERVAL//60} minutes. ---")
        await asyncio.sleep(CHECK_INTERVAL)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

async def main():
    async with client:
        client.loop.create_task(check_all_dealers())
        await client.start(BOT_TOKEN)

asyncio.run(main())
