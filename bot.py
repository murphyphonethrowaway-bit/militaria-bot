import discord
import asyncio
import aiohttp
import json
import os
import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
from datetime import datetime, timezone

# ==================== CONFIGURATION ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = 1510653092721590323
CHECK_INTERVAL = 600  # Check every 10 minutes (in seconds)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ==================== GMAIL CONFIG ====================
GMAIL_USER = "relicregistrybot@gmail.com"
GMAIL_APP_PASSWORD = "hxurgoktwbeznvls"

# ==================== DEALER CONFIG ====================
# Web scraped dealers (still working)
DEALERS = [
    {
        "name": "Weitze Militaria",
        "url": "https://www.weitze.com/neuheiten.html",
        "logo_file": "weitze.png.png",
        "item_selector": "a[href*='/militaria/']",
        "base_url": "https://www.weitze.com"
    },
    {
        "name": "Linda Mae Militaria",
        "url": "https://lindamaemilitaria.com/",
        "logo_file": "lindamae.png.jpeg",
        "item_selector": ".product a",
        "base_url": "https://lindamaemilitaria.com"
    },
]

# Email monitored dealers — matched by sender email domain or name
EMAIL_DEALERS = [
    {
        "name": "The Ruptured Duck",
        "match": ["therupturedduck.com", "ruptured duck"],
        "logo_file": "ruptured_duck.png.png",
        "url": "https://www.therupturedduck.com/collections/recently-added-items"
    },
    {
        "name": "War's End Shop",
        "match": ["warsendshop.com", "war's end", "wars end"],
        "logo_file": "warsend.png.png",
        "url": "https://www.warsendshop.com/collections/new-items"
    },
    {
        "name": "Lakeside Trader",
        "match": ["lakesidetrader.com", "lakeside trader"],
        "logo_file": "lakeside.png.jpg",
        "url": "https://www.lakesidetrader.com/recently-added-items/"
    },
    {
        "name": "Dutch Militaria",
        "match": ["dutchmilitaria.com", "dutch militaria"],
        "logo_file": "dutch_militaria.png.PNG",
        "url": "https://dutchmilitaria.com/"
    },
    {
        "name": "Militaria Sales",
        "match": ["militariasales.com", "militaria sales"],
        "logo_file": "militaria_sales.png.PNG",
        "url": "https://www.militariasales.com/new-item/"
    },
    {
        "name": "Military Collectibles",
        "match": ["militarycollectibles.com", "military collectibles"],
        "logo_file": "military_collectibles.png.PNG",
        "url": "https://militarycollectibles.com/shop?s=n"
    },
    {
        "name": "Military Collectors HQ",
        "match": ["militarycollectorshq.com", "military collectors hq"],
        "logo_file": "militarycollectorshq.png.PNG",
        "url": "https://militarycollectorshq.com/store-catalog"
    },
]

# ==================== BOT STATE ====================
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

SEEN_FILE = "seen_items.json"
STATS_FILE = "stats.json"
SEEN_EMAILS_FILE = "seen_emails.json"

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
    return {}

def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)

def load_seen_emails():
    if os.path.exists(SEEN_EMAILS_FILE):
        with open(SEEN_EMAILS_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen_emails(seen):
    with open(SEEN_EMAILS_FILE, "w") as f:
        json.dump(list(seen), f)

async def fetch_page(session, url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
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
    embed.set_footer(text="The Relic Registry — Dealer Update")

    file = None
    if os.path.exists(logo_file):
        file = discord.File(logo_file, filename="logo.png")
        embed.set_thumbnail(url="attachment://logo.png")
    else:
        print(f"Logo not found at {logo_file}")

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

def check_gmail(seen_emails):
    """Check Gmail for new dealer emails. Returns list of matched dealers."""
    triggered = []
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        mail.select("inbox")

        _, messages = mail.search(None, "UNSEEN")
        email_ids = messages[0].split()

        print(f"[Gmail] Found {len(email_ids)} unread email(s).")

        for eid in email_ids:
            _, msg_data = mail.fetch(eid, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            # Get message ID to avoid duplicates
            msg_id = msg.get("Message-ID", str(eid))
            if msg_id in seen_emails:
                continue

            seen_emails.add(msg_id)

            # Get sender and subject
            sender = msg.get("From", "").lower()
            subject_raw = msg.get("Subject", "")
            subject = decode_header(subject_raw)[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode(errors="replace")
            subject = subject.lower()

            print(f"[Gmail] New email from: {sender} | Subject: {subject}")

            # Match against dealer list
            for dealer in EMAIL_DEALERS:
                for keyword in dealer["match"]:
                    if keyword.lower() in sender or keyword.lower() in subject:
                        print(f"[Gmail] Matched dealer: {dealer['name']}")
                        triggered.append(dealer)
                        break

        mail.logout()
    except Exception as e:
        print(f"[Gmail] Error checking email: {e}")

    return triggered

async def check_all_dealers():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    if not channel:
        print("ERROR: Could not find channel. Check your CHANNEL_ID.")
        return

    print(f"Bot ready! Monitoring {len(DEALERS)} web dealers + {len(EMAIL_DEALERS)} email dealers. Checking every {CHECK_INTERVAL//60} minutes.")

    while not client.is_closed():
        if bot_state["paused"] and not bot_state["force_rescan"]:
            await asyncio.sleep(30)
            continue

        bot_state["force_rescan"] = False
        print(f"\n--- Checking dealers at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
        bot_state["last_check"] = datetime.now(timezone.utc)
        seen = load_seen()

        # Check web dealers
        async with aiohttp.ClientSession() as session:
            for dealer in DEALERS:
                await check_dealer(session, dealer, seen, channel)
                await asyncio.sleep(2)

        save_seen(seen)

        # Check email dealers
        seen_emails = load_seen_emails()
        triggered = await asyncio.get_event_loop().run_in_executor(None, check_gmail, seen_emails)
        save_seen_emails(seen_emails)

        for dealer in triggered:
            logo_file = os.path.join(SCRIPT_DIR, "logos", dealer["logo_file"])
            stats = load_stats()
            stats[dealer["name"]] = stats.get(dealer["name"], 0) + 1
            save_stats(stats)
            await send_alert(channel, dealer["name"], dealer["url"], logo_file)

        print(f"--- Done. Next check in {CHECK_INTERVAL//60} minutes. ---")
        await asyncio.sleep(CHECK_INTERVAL)

async def send_promo():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    if not channel:
        return

    PROMO_INTERVAL = 48 * 3600

    while not client.is_closed():
        await asyncio.sleep(PROMO_INTERVAL)
        banner_file = os.path.join(SCRIPT_DIR, "logos", "Server_Banner.png")

        embed = discord.Embed(
            title="🎖️ The Relic Registry",
            description=(
                "Looking for a great militaria community?\n\n"
                "**The Relic Registry** is a server for collectors, by collectors.\n\n"
                "📬 Get new item alerts from top dealers\n"
                "🏛️ Connect with fellow collectors\n\n"
                "[**Click here to join →**](http://discord.gg/therelicregistry)"
            ),
            color=discord.Color.dark_red(),
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_footer(text="The Relic Registry — Dealer Update")

        file = None
        if os.path.exists(banner_file):
            file = discord.File(banner_file, filename="banner.png")
            embed.set_image(url="attachment://banner.png")

        try:
            if file:
                await channel.send(file=file, embed=embed)
            else:
                await channel.send(embed=embed)
            print("Promo message sent!")
        except Exception as e:
            print(f"Failed to send promo message: {e}")

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    print(f"SCRIPT_DIR: {SCRIPT_DIR}")
    logos_path = os.path.join(SCRIPT_DIR, "logos")
    print(f"Logos folder: {logos_path}")
    if os.path.exists(logos_path):
        print(f"Logos found: {os.listdir(logos_path)}")
    else:
        print("ERROR: Logos folder not found!")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    cmd = message.content.lower().strip()

    if cmd == "!help":
        embed = discord.Embed(
            title="🎖️ The Relic Registry — Dealer Update Bot Commands",
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
        embed.add_field(name="!promo", value="Sends the server promo message manually", inline=False)
        await message.channel.send(embed=embed)

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
        for dealer in EMAIL_DEALERS:
            embed.add_field(name=dealer["name"], value="📧 Via Email", inline=True)
        embed.set_footer(text="The Relic Registry — Dealer Update")
        await message.channel.send(embed=embed)

    elif cmd == "!dealers":
        embed = discord.Embed(
            title="🏪 Monitored Dealers",
            description="Here are all the dealers currently being monitored:",
            color=discord.Color.dark_gold()
        )
        for dealer in DEALERS:
            embed.add_field(name=f"🌐 {dealer['name']}", value=f"[View New Items]({dealer['url']})", inline=True)
        for dealer in EMAIL_DEALERS:
            embed.add_field(name=f"📧 {dealer['name']}", value=f"[Visit Site]({dealer['url']})", inline=True)
        embed.set_footer(text="The Relic Registry — Dealer Update")
        await message.channel.send(embed=embed)

    elif cmd == "!lastcheck":
        if bot_state["last_check"]:
            ts = int(bot_state["last_check"].timestamp())
            await message.channel.send(f"🕐 Last check was <t:{ts}:R> at <t:{ts}:T>")
        else:
            await message.channel.send("⚠️ No check has run yet since the bot started.")

    elif cmd == "!rescan":
        await message.channel.send("🔄 Forcing an immediate rescan of all dealers...")
        bot_state["force_rescan"] = True

    elif cmd == "!pause":
        if bot_state["paused"]:
            await message.channel.send("⚠️ Bot is already paused. Use `!resume` to turn it back on.")
        else:
            bot_state["paused"] = True
            await message.channel.send("⏸️ Bot paused — no more automatic checks until you use `!resume`.")

    elif cmd == "!resume":
        if not bot_state["paused"]:
            await message.channel.send("⚠️ Bot is already running. Use `!pause` to pause it.")
        else:
            bot_state["paused"] = False
            await message.channel.send("▶️ Bot resumed — automatic checks are back on!")

    elif cmd == "!stats":
        stats = load_stats()
        embed = discord.Embed(
            title="📊 Alert Statistics",
            description="Number of times each dealer has triggered a new item alert:",
            color=discord.Color.dark_gold(),
            timestamp=datetime.now(timezone.utc)
        )
        all_dealers = DEALERS + EMAIL_DEALERS
        for dealer in all_dealers:
            count = stats.get(dealer["name"], 0)
            embed.add_field(name=dealer["name"], value=f"🔔 {count} alert(s)", inline=True)
        embed.set_footer(text="The Relic Registry — Dealer Update")
        await message.channel.send(embed=embed)

    elif cmd == "!test":
        await message.channel.send("🧪 Running test — sending a sample notification for each dealer...")
        channel = client.get_channel(CHANNEL_ID)
        all_dealers = DEALERS + EMAIL_DEALERS
        for dealer in all_dealers:
            logo_file = os.path.join(SCRIPT_DIR, "logos", dealer["logo_file"])
            await send_alert(channel, dealer["name"], dealer["url"], logo_file, test=True)
            await asyncio.sleep(1)
        await message.channel.send("✅ Test complete!")

    elif cmd == "!promo":
        await message.channel.send("📣 Sending promo message...")
        channel = client.get_channel(CHANNEL_ID)
        banner_file = os.path.join(SCRIPT_DIR, "logos", "Server_Banner.png")
        embed = discord.Embed(
            title="🎖️ The Relic Registry",
            description=(
                "Looking for a great militaria community?\n\n"
                "**The Relic Registry** is a server for collectors, by collectors.\n\n"
                "📬 Get new item alerts from top dealers\n"
                "🏛️ Connect with fellow collectors\n\n"
                "[**Click here to join →**](http://discord.gg/therelicregistry)"
            ),
            color=discord.Color.dark_red(),
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_footer(text="The Relic Registry — Dealer Update")
        file = None
        if os.path.exists(banner_file):
            file = discord.File(banner_file, filename="banner.png")
            embed.set_image(url="attachment://banner.png")
        if file:
            await channel.send(file=file, embed=embed)
        else:
            await channel.send(embed=embed)
        await message.channel.send("✅ Promo sent!")

async def main():
    async with client:
        client.loop.create_task(check_all_dealers())
        client.loop.create_task(send_promo())
        await client.start(BOT_TOKEN)

asyncio.run(main())
