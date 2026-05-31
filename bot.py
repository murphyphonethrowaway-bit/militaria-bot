import discord
import asyncio
import aiohttp
import json
import os
from bs4 import BeautifulSoup
from datetime import datetime, timezone

# ==================== CONFIGURATION ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = 1510426647239725198
CHECK_INTERVAL = 600  # Check every 10 minutes (in seconds)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ==================== DEALER CONFIG ====================
DEALERS = [
    {
        "name": "The Ruptured Duck",
        "url": "https://www.therupturedduck.com/collections/recently-added-items",
        "logo_file": "ruptured_duck.png.png",
        "item_selector": ".product-item a",
        "base_url": "https://www.therupturedduck.com"
    },
    {
        "name": "War's End Shop",
        "url": "https://www.warsendshop.com/collections/new-items",
        "logo_file": "warsend.png.png",
        "item_selector": ".product-item a",
        "base_url": "https://www.warsendshop.com"
    },
    {
        "name": "Weitze Militaria",
        "url": "https://www.weitze.com/neuheiten.html",
        "logo_file": "weitze.png.png",
        "item_selector": "a[href*='/militaria/']",
        "base_url": "https://www.weitze.com"
    },
    {
        "name": "Lakeside Trader",
        "url": "https://www.lakesidetrader.com/recently-added-items/",
        "logo_file": "lakeside.png.jpg",
        "item_selector": ".product a",
        "base_url": "https://www.lakesidetrader.com"
    },
    {
        "name": "Dutch Militaria",
        "url": "https://dutchmilitaria.com/",
        "logo_file": "dutch_militaria.png.PNG",
        "item_selector": ".product a",
        "base_url": "https://dutchmilitaria.com"
    },
    {
        "name": "Linda Mae Militaria",
        "url": "https://lindamaemilitaria.com/",
        "logo_file": "lindamae.png.jpeg",
        "item_selector": ".product a",
        "base_url": "https://lindamaemilitaria.com"
    },
    {
        "name": "Militaria Sales",
        "url": "https://www.militariasales.com/new-item/",
        "logo_file": "militaria_sales.png.PNG",
        "item_selector": ".woocommerce-loop-product__title",
        "base_url": "https://www.militariasales.com"
    },
    {
        "name": "Military Collectibles",
        "url": "https://militarycollectibles.com/shop?s=n",
        "logo_file": "military_collectibles.png.PNG",
        "item_selector": ".woocommerce-loop-product__title",
        "base_url": "https://militarycollectibles.com"
    },
    {
        "name": "Military Collectors HQ",
        "url": "https://militarycollectorshq.com/store-catalog",
        "logo_file": "militarycollectorshq.png.PNG",
        "item_selector": ".product a",
        "base_url": "https://militarycollectorshq.com"
    },
]

# ==================== BOT STATE ====================
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

SEEN_FILE = "seen_items.json"
STATS_FILE = "stats.json"

bot_state = {
    "paused": False,
    "last_check": None,
    "force_rescan": False,
}

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return json.load(f)
    return {}

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(seen, f)

def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    return {d["name"]: 0 for d in DEALERS}

def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)

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
    try:
        soup = BeautifulSoup(html_bytes, "html.parser", from_encoding="utf-8")
        items = soup.select(selector)
        links = set()
        for item in items:
            a = item if item.name == "a" else item.find("a")
            if a and a.get("href"):
                href = a["href"]
                if href.startswith("/"):
                    href = base_url + href
                href = href.split("?")[0].split("#")[0]
                links.add(href)
            else:
                text = item.get_text(strip=True)
                if text and len(text) > 3:
                    links.add(text)
        return links
    except Exception as e:
        print(f"Error parsing HTML: {e}")
        return set()

async def send_alert(channel, name, url, logo_file, test=False):
    title = f"🧪 TEST — {name}" if test else f"🆕 New Items at {name}!"
    description = f"This is a test notification for [{name}]({url})\n\n[**Click here to view items →**]({url})" if test else f"New items have been added to [{name}]({url})\n\n[**Click here to view new items →**]({url})"

    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.blurple() if test else discord.Color.dark_gold(),
        timestamp=datetime.now(timezone.utc)
    )
    embed.set_footer(text="Militaria Alerts Bot — Test" if test else "Militaria Alerts Bot")

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

async def check_dealer(session, dealer, seen, channel):
    name = dealer["name"]
    url = dealer["url"]
    logo_file = os.path.join(SCRIPT_DIR, "logos", dealer["logo_file"])
    selector = dealer["item_selector"]
    base_url = dealer["base_url"]

    html_bytes = await fetch_page(session, url)
    if not html_bytes:
        print(f"[{name}] Could not fetch page.")
        return

    current_items = extract_item_links(html_bytes, selector, base_url)
    items_key = name + "_items"

    if not current_items:
        print(f"[{name}] No items found with selector '{selector}' — skipping.")
        return

    old_items = set(seen.get(items_key, []))

    if not old_items:
        seen[items_key] = list(current_items)
        print(f"[{name}] First check — saved {len(current_items)} items as baseline.")
        return

    new_items = current_items - old_items
    if new_items:
        print(f"[{name}] {len(new_items)} NEW ITEM(S) DETECTED — sending alert!")
        seen[items_key] = list(current_items)
        stats = load_stats()
        stats[name] = stats.get(name, 0) + 1
        save_stats(stats)
        await send_alert(channel, name, url, logo_file)
    else:
        print(f"[{name}] No new items ({len(current_items)} items unchanged).")

async def check_all_dealers():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    if not channel:
        print("ERROR: Could not find channel. Check your CHANNEL_ID.")
        return

    print(f"Bot ready! Monitoring {len(DEALERS)} dealers. Checking every {CHECK_INTERVAL//60} minutes.")

    while not client.is_closed():
        if bot_state["paused"] and not bot_state["force_rescan"]:
            await asyncio.sleep(30)
            continue

        bot_state["force_rescan"] = False
        print(f"\n--- Checking dealers at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
        bot_state["last_check"] = datetime.now(timezone.utc)
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

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    cmd = message.content.lower().strip()

    # !help
    if cmd == "!help":
        embed = discord.Embed(
            title="🎖️ Militaria Alerts Bot — Commands",
            color=discord.Color.dark_gold()
        )
        embed.add_field(name="!help", value="Shows this help message", inline=False)
        embed.add_field(name="!status", value="Shows which dealers are reachable", inline=False)
        embed.add_field(name="!dealers", value="Lists all monitored dealers with links", inline=False)
        embed.add_field(name="!lastcheck", value="Shows when the bot last checked dealers", inline=False)
        embed.add_field(name="!rescan", value="Forces an immediate check of all dealers", inline=False)
        embed.add_field(name="!pause", value="Pauses automatic dealer checking", inline=False)
        embed.add_field(name="!resume", value="Resumes automatic dealer checking", inline=False)
        embed.add_field(name="!stats", value="Shows how many alerts each dealer has triggered", inline=False)
        embed.add_field(name="!test", value="Sends a test notification for all dealers", inline=False)
        await message.channel.send(embed=embed)

    # !status
    elif cmd == "!status":
        await message.channel.send("🔍 Checking all dealer websites, please wait...")
        embed = discord.Embed(
            title="📡 Dealer Status",
            color=discord.Color.dark_gold(),
            timestamp=datetime.now(timezone.utc)
        )
        async with aiohttp.ClientSession() as session:
            for dealer in DEALERS:
                html = await fetch_page(session, dealer["url"])
                status = "✅ Online" if html else "❌ Unreachable"
                embed.add_field(name=dealer["name"], value=status, inline=True)
                await asyncio.sleep(1)
        embed.set_footer(text="Militaria Alerts Bot")
        await message.channel.send(embed=embed)

    # !dealers
    elif cmd == "!dealers":
        embed = discord.Embed(
            title="🏪 Monitored Dealers",
            description="Here are all the dealers currently being monitored:",
            color=discord.Color.dark_gold()
        )
        for dealer in DEALERS:
            embed.add_field(name=dealer["name"], value=f"[View New Items]({dealer['url']})", inline=True)
        embed.set_footer(text="Militaria Alerts Bot")
        await message.channel.send(embed=embed)

    # !lastcheck
    elif cmd == "!lastcheck":
        if bot_state["last_check"]:
            ts = int(bot_state["last_check"].timestamp())
            await message.channel.send(f"🕐 Last check was <t:{ts}:R> at <t:{ts}:T>")
        else:
            await message.channel.send("⚠️ No check has run yet since the bot started.")

    # !rescan
    elif cmd == "!rescan":
        await message.channel.send("🔄 Forcing an immediate rescan of all dealers...")
        bot_state["force_rescan"] = True

    # !pause
    elif cmd == "!pause":
        if bot_state["paused"]:
            await message.channel.send("⚠️ Bot is already paused. Use `!resume` to turn it back on.")
        else:
            bot_state["paused"] = True
            await message.channel.send("⏸️ Bot paused — no more automatic checks until you use `!resume`.")

    # !resume
    elif cmd == "!resume":
        if not bot_state["paused"]:
            await message.channel.send("⚠️ Bot is already running. Use `!pause` to pause it.")
        else:
            bot_state["paused"] = False
            await message.channel.send("▶️ Bot resumed — automatic checks are back on!")

    # !stats
    elif cmd == "!stats":
        stats = load_stats()
        embed = discord.Embed(
            title="📊 Alert Statistics",
            description="Number of times each dealer has triggered a new item alert:",
            color=discord.Color.dark_gold(),
            timestamp=datetime.now(timezone.utc)
        )
        for dealer in DEALERS:
            count = stats.get(dealer["name"], 0)
            embed.add_field(name=dealer["name"], value=f"🔔 {count} alert(s)", inline=True)
        embed.set_footer(text="Militaria Alerts Bot")
        await message.channel.send(embed=embed)

    # !test
    elif cmd == "!test":
        await message.channel.send("🧪 Running test — sending a sample notification for each dealer...")
        channel = client.get_channel(CHANNEL_ID)
        for dealer in DEALERS:
            logo_file = os.path.join(SCRIPT_DIR, "logos", dealer["logo_file"])
            await send_alert(channel, dealer["name"], dealer["url"], logo_file, test=True)
            await asyncio.sleep(1)
        await message.channel.send("✅ Test complete!")

async def main():
    async with client:
        client.loop.create_task(check_all_dealers())
        await client.start(BOT_TOKEN)

asyncio.run(main())
