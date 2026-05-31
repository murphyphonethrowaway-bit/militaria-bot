import discord
import asyncio
import aiohttp
import json
import os
import hashlib
from bs4 import BeautifulSoup
from datetime import datetime
 
# ==================== CONFIGURATION ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = 1510426647239725198
CHECK_INTERVAL = 600  # Check every 10 minutes (in seconds)
 
# ==================== DEALER CONFIG ====================
DEALERS = [
    {
        "name": "The Ruptured Duck",
        "url": "https://www.therupturedduck.com/collections/recently-added-items",
        "logo_file": "ruptured_duck.png",
        "item_selector": ".product-item",
        "base_url": "https://www.therupturedduck.com"
    },
    {
        "name": "War's End Shop",
        "url": "https://www.warsendshop.com/collections/new-items",
        "logo_file": "warsend.png",
        "item_selector": ".product-item",
        "base_url": "https://www.warsendshop.com"
    },
    {
        "name": "Weitze Militaria",
        "url": "https://www.weitze.com/neuheiten.html",
        "logo_file": "weitze.png",
        "item_selector": "a.artikel_link",
        "base_url": "https://www.weitze.com"
    },
    {
        "name": "Lakeside Trader",
        "url": "https://www.lakesidetrader.com/recently-added-items/",
        "logo_file": "lakeside.png",
        "item_selector": ".product",
        "base_url": "https://www.lakesidetrader.com"
    },
    {
        "name": "Dutch Militaria",
        "url": "https://dutchmilitaria.com/",
        "logo_file": "dutch_militaria.png",
        "item_selector": ".product",
        "base_url": "https://dutchmilitaria.com"
    },
    {
        "name": "Linda Mae Militaria",
        "url": "https://lindamaemilitaria.com/",
        "logo_file": "lindamae.png",
        "item_selector": ".product",
        "base_url": "https://lindamaemilitaria.com"
    },
    {
        "name": "Militaria Sales",
        "url": "https://www.militariasales.com/new-item/",
        "logo_file": "militaria_sales.png",
        "item_selector": ".woocommerce-loop-product__title",
        "base_url": "https://www.militariasales.com"
    },
    {
        "name": "Military Collectibles",
        "url": "https://militarycollectibles.com/shop?s=n",
        "logo_file": "military_collectibles.png",
        "item_selector": ".woocommerce-loop-product__title",
        "base_url": "https://militarycollectibles.com"
    },
    {
        "name": "Military Collectors HQ",
        "url": "https://militarycollectorshq.com/store-catalog",
        "logo_file": "militarycollectorshq.png",
        "item_selector": ".product",
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
 
async def fetch_page(session, url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status == 200:
                return await resp.read()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None
 
def extract_item_links(html_bytes, selector, base_url):
    """Extract just the product links/titles — ignore dynamic page content."""
    try:
        soup = BeautifulSoup(html_bytes, "html.parser", from_encoding="utf-8")
        items = soup.select(selector)
        links = set()
        for item in items:
            # Try to get a link href
            a = item if item.name == "a" else item.find("a")
            if a and a.get("href"):
                href = a["href"]
                if href.startswith("/"):
                    href = base_url + href
                links.add(href)
            else:
                # Fall back to text content
                text = item.get_text(strip=True)
                if text:
                    links.add(text)
        return links
    except Exception as e:
        print(f"Error parsing HTML: {e}")
        return set()
 
async def check_dealer(session, dealer, seen, channel):
    name = dealer["name"]
    url = dealer["url"]
    logo_file = os.path.join("logos", dealer["logo_file"])
    selector = dealer["item_selector"]
    base_url = dealer["base_url"]
 
    html_bytes = await fetch_page(session, url)
    if not html_bytes:
        print(f"[{name}] Could not fetch page.")
        return
 
    current_items = extract_item_links(html_bytes, selector, base_url)
 
    if not current_items:
        # Fallback: hash the whole page if no items found with selector
        page_hash = hashlib.md5(html_bytes).hexdigest()
        old_hash = seen.get(name)
        if old_hash is None:
            seen[name] = page_hash
            print(f"[{name}] First check (fallback hash) — saved baseline.")
            return
        if page_hash != old_hash:
            seen[name] = page_hash
            await send_alert(channel, name, url, logo_file)
        else:
            print(f"[{name}] No changes detected.")
        return
 
    # Convert to a stable sorted string for comparison
    items_key = name + "_items"
    old_items = set(seen.get(items_key, []))
 
    if not old_items:
        seen[items_key] = list(current_items)
        print(f"[{name}] First check — saved {len(current_items)} items as baseline.")
        return
 
    new_items = current_items - old_items
    if new_items:
        print(f"[{name}] {len(new_items)} NEW ITEM(S) DETECTED — sending alert!")
        seen[items_key] = list(current_items)
        await send_alert(channel, name, url, logo_file)
    else:
        print(f"[{name}] No new items ({len(current_items)} items unchanged).")
 
async def send_alert(channel, name, url, logo_file):
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
        print(f"Logo not found at {logo_file} — sending without logo.")
 
    try:
        if file:
            await channel.send(file=file, embed=embed)
        else:
            await channel.send(embed=embed)
    except Exception as e:
        print(f"Failed to send message for {name}: {e}")
 
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
                await asyncio.sleep(2)
 
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
