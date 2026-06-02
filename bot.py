import discord
from discord import app_commands
import asyncio
import aiohttp
import json
import os
import imaplib
import email
import random
from email.header import decode_header
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta

# ==================== CONFIGURATION ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = 1510653092721590323
WAF_ROLE_ID = 1511101033349124318
DEALER_SUGGEST_CHANNEL_ID = 1511487755266556034  # #dealer-reviews channel
REVIEW_LOG_CHANNEL_ID = 1511487836220817561  # #review-log channel
TRUSTED_REVIEWER_ROLE_ID = 1511487130189168802  # @Trusted Reviewer role
TRUSTED_REVIEWER_THRESHOLD = 25  # Number of reviews to get Trusted Reviewer role
CHECK_INTERVAL = 600
EMAIL_CHECK_INTERVAL = 30

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GMAIL_USER = "relicregistrybot@gmail.com"
GMAIL_APP_PASSWORD = "tyvm uvfb jkxv ptvy"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.864.59 Safari/537.36 Edg/91.0.864.59",
    "Mozilla/5.0 (Linux; Android 11; Pixel 4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Mobile Safari/537.36",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
]

WAF_CATEGORIES = [
    {"name": "All WAF Updates", "role_id": 1511112093774905386, "keywords": []},
    {"name": "1957 Medals & Decorations", "role_id": 1511112215544201367, "keywords": ["1957", "medal", "decoration"]},
    {"name": "Medals, Badges & Awards", "role_id": 1511112409451073828, "keywords": ["medal", "badge", "award", "cross", "iron cross"]},
    {"name": "Photos & Paper Items", "role_id": 1511112501792739388, "keywords": ["photo", "paper", "document", "postcard", "soldbuch"]},
    {"name": "Uniforms", "role_id": 1511112564824866897, "keywords": ["uniform", "tunic", "jacket", "trousers", "coat"]},
    {"name": "Flags, Banners & Pennants", "role_id": 1511112671963906068, "keywords": ["flag", "banner", "pennant", "standard"]},
    {"name": "Equipment/Field Gear & Dog Tags", "role_id": 1511112754491297922, "keywords": ["equipment", "field gear", "footwear", "boot", "dog tag", "canteen"]},
    {"name": "Optics", "role_id": 1511112866495729706, "keywords": ["optic", "binocular", "scope", "telescope"]},
    {"name": "Cloth Headgear", "role_id": 1511112942358368307, "keywords": ["cloth", "headgear", "cap", "visor", "field cap"]},
    {"name": "German Helmets", "role_id": 1511113046167130293, "keywords": ["helmet", "stahlhelm", "M35", "M40", "M42"]},
    {"name": "Belts & Buckles", "role_id": 1511113224869773393, "keywords": ["belt", "buckle", "brocade"]},
    {"name": "Edged Weapons", "role_id": 1511113345816854529, "keywords": ["dagger", "sword", "bayonet", "knife", "blade"]},
    {"name": "Firearms & Ordnance", "role_id": 1511113443501932838, "keywords": ["firearm", "pistol", "rifle", "gun", "luger", "p38"]},
    {"name": "Imperial Militaria", "role_id": 1511113528046653520, "keywords": ["imperial", "ww1", "1914", "1918", "pickelhaube"]},
    {"name": "Freikorps / Weimar Period", "role_id": 1511113644015095839, "keywords": ["freikorps", "weimar"]},
    {"name": "U.S. & British Militaria", "role_id": 1511113709328662648, "keywords": ["american", "british", "allied", "usa", "uk"]},
    {"name": "International Militaria", "role_id": 1511113776923938869, "keywords": ["international", "italian", "japanese", "soviet", "french"]},
    {"name": "Books & Media", "role_id": 1511118900488569015, "keywords": ["book", "media", "magazine", "manual"]},
    {"name": "Misc. Third Reich Items", "role_id": 1511119017807581347, "keywords": ["misc", "third reich", "nsdap"]},
]

# ==================== DEALER CONFIG ====================
DEALERS = [
    {"name": "Weitze Militaria", "url": "https://www.weitze.com/neuheiten.html", "logo_file": "weitze.png", "item_selector": "a[href*='/militaria/']", "base_url": "https://www.weitze.com"},
    {"name": "Linda Mae Militaria", "url": "https://lindamaemilitaria.com/", "logo_file": "lindamae.png", "item_selector": ".product a", "base_url": "https://lindamaemilitaria.com"},
]

EMAIL_DEALERS = [
    {"name": "The Ruptured Duck", "match": ["therupturedduck.com", "ruptured duck"], "logo_file": "ruptured_duck.png", "url": "https://www.therupturedduck.com/collections/recently-added-items"},
    {"name": "War's End Shop", "match": ["warsendshop.com", "war's end", "wars end"], "logo_file": "warsend.png", "url": "https://www.warsendshop.com/collections/new-items"},
    {"name": "Lakeside Trader", "match": ["lakesidetrader.com", "lakeside trader"], "logo_file": "lakeside.png", "url": "https://www.lakesidetrader.com/recently-added-items/"},
    {"name": "Dutch Militaria", "match": ["dutchmilitaria.com", "dutch militaria"], "logo_file": "dutch_militaria.png", "url": "https://dutchmilitaria.com/"},
    {"name": "Militaria Sales", "match": ["militariasales.com", "militaria sales"], "logo_file": "militaria_sales.png", "url": "https://www.militariasales.com/new-item/"},
    {"name": "Military Collectibles", "match": ["militarycollectibles.com", "military collectibles"], "logo_file": "military_collectibles.png", "url": "https://militarycollectibles.com/shop?s=n"},
    {"name": "Military Collectors HQ", "match": ["militarycollectorshq.com", "military collectors hq"], "logo_file": "militarycollectorshq.png", "url": "https://militarycollectorshq.com/store-catalog"},
    {"name": "Soviet Orders", "match": ["sovietorders.com", "soviet orders"], "logo_file": "Soviet_Orders.png", "url": "https://sovietorders.com/new-in-store/"},
    {"name": "Empire's Past", "match": ["empirespast.com", "empire's past", "empires past"], "logo_file": "Empire_past.png", "url": "https://empirespast.com/newly-listed/"},
    {"name": "1944 Militaria", "match": ["1944militaria.com", "1944 militaria"], "logo_file": "1944militaria.png", "url": "https://www.1944militaria.com/New_Original_Items_s/1900.htm"},
    {"name": "International Military Antiques", "match": ["ima-usa.com", "international military antiques", "ima usa"], "logo_file": "ima.png", "url": "https://www.ima-usa.com/collections/new-arrivals"},
    {"name": "Wolfgang Historica", "match": ["wolfganghistorica.com", "wolfgang historica"], "logo_file": "wolfgang_historica.png", "url": "https://wolfganghistorica.com/"},
    {"name": "Enemy Militaria", "match": ["enemymilitaria.com", "enemy militaria"], "logo_file": "Enemy_Militaria.png", "url": "https://enemymilitaria.com/"},
    {"name": "Hiscoll Military Antiques", "match": ["hiscoll.com", "hiscoll military antiques", "hiscoll"], "logo_file": "hiscoll.png", "url": "https://hiscoll.com/shop"},
    {"name": "Relics of the Reich", "match": ["relicsofthereich.com", "relics of the reich"], "logo_file": "relicsofthereich.png", "url": "https://www.relicsofthereich.com/home"},
    {"name": "Epic Artifacts", "match": ["epicartifacts.com", "epic artifacts"], "logo_file": "Epic_artifacts.png", "url": "https://epicartifacts.com/newly-listed/"},
    {"name": "RG Militaria", "match": ["rg-militaria.com", "rg militaria"], "logo_file": "rgmilitaria.png", "url": "https://www.rg-militaria.com/new-items-nieuwe-items"},
    {"name": "Military Antiques Stockholm", "match": ["military-antiques-stockholm.com", "military antiques stockholm"], "logo_file": "Military_Antiques_Stockholm.png", "url": "https://www.military-antiques-stockholm.com/shop/"},
    {"name": "Oorlogsspullen", "match": ["oorlogsspullen.nl", "oorlogsspullen"], "logo_file": "Oorlogspullen.png", "url": "https://oorlogsspullen.nl/product-categorie/new/"},
    {"name": "Wittmann Antique Militaria", "match": ["wwiidaggers.com", "wittmann antique militaria", "wittmann"], "logo_file": "wam.png", "url": "https://www.wwiidaggers.com/updates.htm"},
    {"name": "RBNr Militaria", "match": ["rbnr.it", "rbnr militaria", "rbnr"], "logo_file": "RBNR.png", "url": "https://en.rbnr.it/collections/all"},
    {"name": "Iraqi Militaria", "match": ["iraqimilitaria.com", "iraqi militaria"], "logo_file": "iraqi_militaria.png", "url": "https://www.iraqimilitaria.com/"},
    {"name": "Danzig Militaria", "match": ["danzigmilitaria.com", "danzig militaria"], "logo_file": "Danzig_Militaria.png", "url": "https://danzigmilitaria.com/shop/"},
    {"name": "FJM44", "match": ["fjm44.com", "fjm44", "fjm 44"], "logo_file": "fjm44.png", "url": "https://fjm44.com/product-category/militaria/"},
    {"name": "Kurland", "match": ["kurland-docs.com", "kurland"], "logo_file": "kurland.png", "url": "https://www.kurland-docs.com/shop.php"},
    {"name": "Queen City Militaria", "match": ["queencitymilitaria.com", "queen city militaria"], "logo_file": "queen_city_militaria.png", "url": "https://www.queencitymilitaria.com/"},
    {"name": "Combat Relics", "match": ["combat-relics.com", "combat relics"], "logo_file": "Combat_relics.png", "url": "https://www.combat-relics.com/"},
    {"name": "Tiger Militaria", "match": ["tigermilitaria.com", "tiger militaria"], "logo_file": "TigerMilitaria.png", "url": "https://tigermilitaria.com/shop?showPerPage=24"},
    {"name": "WAF Estate", "match": ["wehrmacht-awards.com", "waf estate", "e-stand", "estand", "militaria e-stand"], "logo_file": "waf.png", "url": "https://www.wehrmacht-awards.com/forums/forum/the-militaria-e-stand", "waf": True},
    {"name": "EA Militaria", "match": ["ea-militaria.com", "ea militaria"], "logo_file": "eamilitaria.png", "url": "https://www.ea-militaria.com/new-items"},
    {"name": "Militaria Plaza", "match": ["militariaplaza.nl", "militaria plaza"], "logo_file": "Militaria_Plaza.png", "url": "https://militariaplaza.nl/new"},
    {"name": "The Collector's Guild", "match": ["germanmilitaria.com", "collector's guild", "collectors guild"], "logo_file": "germanmilitaria.png", "url": "https://www.germanmilitaria.com/Advanced.html"},
    {"name": "General Assault Militaria", "match": ["generalassaultmilitaria.com", "general assault militaria", "gam"], "logo_file": "gam.png", "url": "https://www.generalassaultmilitaria.com/"},
    {"name": "Bevo Militaria", "match": ["bevo-militaria.com", "bevo militaria"], "logo_file": "Bevo_Militaria.png", "url": "https://bevo-militaria.com/shop/"},
]

# ==================== BOT SETUP ====================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class MilitariaBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("Slash commands synced!")

client = MilitariaBot()

# ==================== FILE PATHS ====================
SEEN_FILE = "seen_items.json"
STATS_FILE = "stats.json"
SEEN_EMAILS_FILE = "seen_emails.json"
REVIEWS_FILE = "reviews.json"
DEALER_WARNINGS_FILE = "dealer_warnings.json"

bot_state = {
    "paused": False,
    "last_check": None,
    "force_rescan": False,
    "promo_paused": False,
    "last_email_check": None,
    "last_promo": None,
}

# ==================== DATA FUNCTIONS ====================
def load_json(filepath, default):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return default

def save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

def load_seen(): return load_json(SEEN_FILE, {})
def save_seen(d): save_json(SEEN_FILE, d)
def load_stats(): return load_json(STATS_FILE, {})
def save_stats(d): save_json(STATS_FILE, d)
def load_seen_emails(): return set(load_json(SEEN_EMAILS_FILE, []))
def save_seen_emails(d): save_json(SEEN_EMAILS_FILE, list(d))
def load_reviews(): return load_json(REVIEWS_FILE, {})
def save_reviews(d): save_json(REVIEWS_FILE, d)
def load_warnings(): return load_json(DEALER_WARNINGS_FILE, {})
def save_warnings(d): save_json(DEALER_WARNINGS_FILE, d)

def is_mod(member):
    return member.guild_permissions.administrator or member.guild_permissions.manage_guild

# ==================== REVIEW HELPERS ====================
def get_dealer_rating(dealer_name):
    reviews = load_reviews()
    dealer_reviews = reviews.get(dealer_name, [])
    if not dealer_reviews:
        return None, 0
    avg = sum(r["rating"] for r in dealer_reviews) / len(dealer_reviews)
    return round(avg, 1), len(dealer_reviews)

def stars_display(rating):
    if rating is None:
        return "⭐ No ratings yet"
    full = int(rating)
    half = 1 if rating - full >= 0.5 else 0
    empty = 5 - full - half
    return "⭐" * full + "✨" * half + "☆" * empty + f" {rating}/5"

def get_all_dealers():
    return DEALERS + EMAIL_DEALERS

async def dealer_autocomplete(interaction: discord.Interaction, current: str):
    all_dealers = sorted(get_all_dealers(), key=lambda x: x["name"].lower())
    return [
        app_commands.Choice(name=d["name"], value=d["name"])
        for d in all_dealers
        if current.lower() in d["name"].lower()
    ][:25]

def find_dealer(name):
    name_lower = name.lower()
    for d in get_all_dealers():
        if d["name"].lower() == name_lower or name_lower in d["name"].lower():
            return d
    return None

# ==================== SCRAPING ====================
async def fetch_page(session, url, retries=3):
    for attempt in range(retries):
        try:
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    return await resp.read()
                print(f"Attempt {attempt+1}/{retries} — status {resp.status} for {url}")
        except Exception as e:
            print(f"Attempt {attempt+1}/{retries} — error: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(30)
    return None

def extract_item_links(html_bytes, selector, base_url):
    try:
        soup = BeautifulSoup(html_bytes, "html.parser", from_encoding="utf-8")
        items = soup.select(selector)
        if not items:
            items = soup.find_all('a', class_='shopitemTitle')
        if not items:
            items = soup.find_all('li', class_='entry')
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

# ==================== ALERTS ====================
async def send_alert(channel, name, url, logo_file, test=False, waf=False):
    warnings = load_warnings()
    warning = warnings.get(name)
    rating, review_count = get_dealer_rating(name)

    title = f"🧪 TEST — {name}" if test else f"🆕 New Items at {name}!"
    description = f"This is a test notification for [{name}]({url})\n\n[**Click here to view items →**]({url})" if test else f"New items have been added to [{name}]({url})\n\n[**Click here to view new items →**]({url})"

    if warning and not test:
        description = f"⚠️ **WARNING: {warning}**\n\n" + description

    color = discord.Color.blurple() if test else (discord.Color.red() if warning else discord.Color.dark_gold())

    embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.now(timezone.utc))
    embed.add_field(name="Rating", value=stars_display(rating), inline=True)
    embed.add_field(name="Total Reviews", value=f"📝 {review_count}", inline=True)
    embed.set_footer(text="The Relic Registry — Dealer Update")

    file = None
    if os.path.exists(logo_file):
        file = discord.File(logo_file, filename="logo.png")
        embed.set_thumbnail(url="attachment://logo.png")

    content_msg = f"<@&{WAF_ROLE_ID}> New WAF Estate listing!" if waf and not test else None

    try:
        if file:
            await channel.send(content=content_msg, file=file, embed=embed)
        else:
            await channel.send(content=content_msg, embed=embed)
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
        print(f"[{name}] {len(new_items)} NEW ITEM(S) DETECTED!")
        seen[items_key] = list(current_items)
        stats = load_stats()
        stats[name] = stats.get(name, 0) + 1
        save_stats(stats)
        await send_alert(channel, name, url, logo_file)
    else:
        print(f"[{name}] No new items ({len(current_items)} items unchanged).")

def check_gmail(seen_emails):
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
            msg_id = msg.get("Message-ID", str(eid))
            if msg_id in seen_emails:
                continue
            seen_emails.add(msg_id)
            sender = msg.get("From", "").lower()
            subject_raw = msg.get("Subject", "")
            subject = decode_header(subject_raw)[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode(errors="replace")
            subject = subject.lower()
            print(f"[Gmail] New email from: {sender} | Subject: {subject}")
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

# ==================== BACKGROUND TASKS ====================
async def check_all_dealers():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    if not channel:
        print("ERROR: Could not find channel.")
        return
    print(f"Bot ready! Monitoring {len(DEALERS)} web dealers + {len(EMAIL_DEALERS)} email dealers.")
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

async def check_email_dealers():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    if not channel:
        return
    print(f"Email checker ready! Checking every {EMAIL_CHECK_INTERVAL} seconds.")
    while not client.is_closed():
        if bot_state["paused"]:
            await asyncio.sleep(30)
            continue
        bot_state["last_email_check"] = datetime.now(timezone.utc)
        seen_emails = load_seen_emails()
        triggered = await asyncio.get_event_loop().run_in_executor(None, check_gmail, seen_emails)
        save_seen_emails(seen_emails)
        for dealer in triggered:
            logo_file = os.path.join(SCRIPT_DIR, "logos", dealer["logo_file"])
            stats = load_stats()
            stats[dealer["name"]] = stats.get(dealer["name"], 0) + 1
            save_stats(stats)
            is_waf = dealer.get("waf", False)
            await send_alert(channel, dealer["name"], dealer["url"], logo_file, waf=is_waf)
        await asyncio.sleep(EMAIL_CHECK_INTERVAL)

async def send_promo():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    if not channel:
        return
    while not client.is_closed():
        await asyncio.sleep(48 * 3600)
        if bot_state["promo_paused"]:
            continue
        banner_file = os.path.join(SCRIPT_DIR, "logos", "Server_Banner.png")
        embed = discord.Embed(
            title="🎖️ The Relic Registry",
            description="Looking for a great militaria community?\n\n**The Relic Registry** is a server for collectors, by collectors.\n\n📬 Get new item alerts from top dealers\n🏛️ Connect with fellow collectors\n\n[**Click here to join →**](http://discord.gg/therelicregistry)",
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
            bot_state["last_promo"] = datetime.now(timezone.utc)
            print("Promo message sent!")
        except Exception as e:
            print(f"Failed to send promo: {e}")

# ==================== SLASH COMMANDS ====================

@client.tree.command(name="help", description="Shows all available bot commands")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="🎖️ The Relic Registry — Commands", color=discord.Color.dark_gold())
    embed.add_field(name="👥 Member Commands", value="​", inline=False)
    embed.add_field(name="/help & /dealers", value="This message / List all dealers", inline=True)
    embed.add_field(name="/status & /lastcheck", value="Site status / Last check time", inline=True)
    embed.add_field(name="/dealerprofile & /ratedealer", value="View profile / Rate dealer", inline=True)
    embed.add_field(name="/suggestdealer & /leaderboard", value="Suggest dealer / Leaderboard", inline=True)
    embed.add_field(name="/joinwaf & /leavewaf", value="Subscribe/unsubscribe WAF alerts", inline=True)
    embed.add_field(name="/myroles", value="Your WAF subscriptions", inline=True)
    embed.add_field(name="🔒 Mod Commands", value="​", inline=False)
    embed.add_field(name="/rescan & /pause & /resume", value="Force check / Pause / Resume", inline=True)
    embed.add_field(name="/stats & /test", value="Alert stats / Test notifications", inline=True)
    embed.add_field(name="/promo & /pausepromo & /resumepromo", value="Send/pause/resume promo", inline=True)
    embed.add_field(name="/adddealer & /approvedealer", value="Add/approve a dealer", inline=True)
    embed.add_field(name="/warningdealer & /removewarning", value="Add/remove warning", inline=True)
    embed.add_field(name="/deletereview & /nextemail & /nextpromo", value="Delete review / Countdowns", inline=True)
    embed.set_footer(text="🔒 = Mod only")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@client.tree.command(name="dealers", description="Lists all monitored dealers")
async def dealers_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="🏪 Monitored Dealers", color=discord.Color.dark_gold())
    for dealer in DEALERS:
        rating, count = get_dealer_rating(dealer["name"])
        embed.add_field(name=f"🌐 {dealer['name']}", value=f"[Visit]({dealer['url']})\n{stars_display(rating)}", inline=True)
    for dealer in EMAIL_DEALERS:
        rating, count = get_dealer_rating(dealer["name"])
        embed.add_field(name=f"📧 {dealer['name']}", value=f"[Visit]({dealer['url']})\n{stars_display(rating)}", inline=True)
    embed.set_footer(text="The Relic Registry — Dealer Update")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@client.tree.command(name="status", description="Check which dealer websites are reachable")
async def status_cmd(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(title="📡 Dealer Status", color=discord.Color.dark_gold(), timestamp=datetime.now(timezone.utc))
    async with aiohttp.ClientSession() as session:
        for dealer in DEALERS:
            html = await fetch_page(session, dealer["url"])
            status = "✅ Online" if html else "❌ Unreachable"
            embed.add_field(name=dealer["name"], value=status, inline=True)
            await asyncio.sleep(1)
    for dealer in EMAIL_DEALERS:
        embed.add_field(name=dealer["name"], value="📧 Via Email", inline=True)
    await interaction.followup.send(embed=embed, ephemeral=True)

@client.tree.command(name="lastcheck", description="Shows when the bot last checked dealers")
async def lastcheck_cmd(interaction: discord.Interaction):
    if bot_state["last_check"]:
        ts = int(bot_state["last_check"].timestamp())
        await interaction.response.send_message(f"🕐 Last check was <t:{ts}:R> at <t:{ts}:T>", ephemeral=True)
    else:
        await interaction.response.send_message("⚠️ No check has run yet since the bot started.", ephemeral=True)

@client.tree.command(name="joinwaf", description="Subscribe to WAF Estate alerts by category")
async def joinwaf_cmd(interaction: discord.Interaction):
    try:
        options = [discord.SelectOption(label=cat["name"][:100], value=str(cat["role_id"])) for cat in WAF_CATEGORIES]
        select = discord.ui.Select(placeholder="Choose WAF categories...", min_values=1, max_values=len(options), options=options)

        async def select_callback(i: discord.Interaction):
            added = []
            already_have = []
            for value in select.values:
                role_id = int(value)
                role = i.guild.get_role(role_id)
                if role:
                    if role in i.user.roles:
                        already_have.append(role.name)
                    else:
                        await i.user.add_roles(role)
                        added.append(role.name)
            waf_role = i.guild.get_role(WAF_ROLE_ID)
            if waf_role and waf_role not in i.user.roles:
                await i.user.add_roles(waf_role)
            parts = []
            if added:
                parts.append(f"✅ Subscribed to: {', '.join(added)}")
            if already_have:
                parts.append(f"⚠️ Already had: {', '.join(already_have)}")
            await i.response.send_message("\n".join(parts) if parts else "No changes made.", ephemeral=True)

        select.callback = select_callback
        view = discord.ui.View()
        view.add_item(select)
        await interaction.response.send_message("🎖️ **Select which WAF Estate categories you want alerts for:**", view=view, ephemeral=True)
    except Exception as e:
        print(f"joinwaf error: {e}")
        await interaction.response.send_message(f"⚠️ Error: {e}", ephemeral=True)

@client.tree.command(name="leavewaf", description="Unsubscribe from WAF Estate alerts")
async def leavewaf_cmd(interaction: discord.Interaction):
    options = [
        discord.SelectOption(label=cat["name"], value=str(cat["role_id"]))
        for cat in WAF_CATEGORIES
        if any(r.id == cat["role_id"] for r in interaction.user.roles)
    ]
    if not options:
        await interaction.response.send_message("⚠️ You don't have any WAF Estate subscriptions.", ephemeral=True)
        return
    select = discord.ui.Select(placeholder="Choose categories to unsubscribe from...", min_values=1, max_values=len(options), options=options)

    async def leave_callback(i: discord.Interaction):
        removed = []
        for value in select.values:
            role_id = int(value)
            role = i.guild.get_role(role_id)
            if role and role in i.user.roles:
                await i.user.remove_roles(role)
                removed.append(role.name)
        remaining = [r for r in i.user.roles if any(r.id == cat["role_id"] for cat in WAF_CATEGORIES)]
        if not remaining:
            waf_role = i.guild.get_role(WAF_ROLE_ID)
            if waf_role and waf_role in i.user.roles:
                await i.user.remove_roles(waf_role)
        await i.response.send_message(f"✅ Unsubscribed from: {', '.join(removed)}", ephemeral=True)

    select.callback = leave_callback
    view = discord.ui.View()
    view.add_item(select)
    await interaction.response.send_message("Select categories to unsubscribe from:", view=view, ephemeral=True)

@client.tree.command(name="myroles", description="Shows your current WAF alert subscriptions")
async def myroles_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="🎖️ Your WAF Alert Subscriptions", color=discord.Color.dark_gold(), timestamp=datetime.now(timezone.utc))
    subscribed = [cat["name"] for cat in WAF_CATEGORIES if any(r.id == cat["role_id"] for r in interaction.user.roles)]
    embed.add_field(name="✅ Subscribed", value="\n".join(subscribed) if subscribed else "None — use `/joinwaf` to subscribe", inline=False)
    embed.set_footer(text="The Relic Registry — Dealer Update")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@client.tree.command(name="dealerprofile", description="View a dealer's full profile including ratings and reviews")
@app_commands.describe(dealer_name="Name of the dealer")
@app_commands.autocomplete(dealer_name=dealer_autocomplete)
async def dealerprofile_cmd(interaction: discord.Interaction, dealer_name: str):
    dealer = find_dealer(dealer_name)
    if not dealer:
        await interaction.response.send_message(f"⚠️ Dealer '{dealer_name}' not found. Use `/dealers` to see all dealers.", ephemeral=True)
        return

    reviews = load_reviews()
    warnings = load_warnings()
    dealer_reviews = reviews.get(dealer["name"], [])
    rating, count = get_dealer_rating(dealer["name"])
    warning = warnings.get(dealer["name"])

    logo_file = os.path.join(SCRIPT_DIR, "logos", dealer["logo_file"])

    color = discord.Color.red() if warning else discord.Color.dark_gold()
    embed = discord.Embed(title=f"🏪 {dealer['name']}", color=color, timestamp=datetime.now(timezone.utc))

    if warning:
        embed.add_field(name="⚠️ WARNING", value=f"```{warning}```", inline=False)

    embed.add_field(name="Website", value=f"[Visit Site]({dealer['url']})", inline=True)
    embed.add_field(name="Rating", value=stars_display(rating), inline=True)
    embed.add_field(name="Total Reviews", value=f"📝 {count}", inline=True)

    # Show last 5 reviews (anonymous)
    if dealer_reviews:
        last_5 = dealer_reviews[-5:]
        review_text = ""
        for r in reversed(last_5):
            stars = "⭐" * r["rating"]
            review_text += f"{stars}\n"
            if r.get("review"):
                review_text += f"*\"{r['review'][:100]}\"*\n"
            review_text += f"<t:{r['timestamp']}:R>\n\n"
        embed.add_field(name="Recent Reviews", value=review_text[:1024], inline=False)
    else:
        embed.add_field(name="Recent Reviews", value="No reviews yet — be the first with `/ratedealer`!", inline=False)

    embed.set_footer(text="The Relic Registry — Dealer Update")

    file = None
    if os.path.exists(logo_file):
        file = discord.File(logo_file, filename="logo.png")
        embed.set_thumbnail(url="attachment://logo.png")

    if file:
        await interaction.response.send_message(file=file, embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message(embed=embed, ephemeral=True)

@client.tree.command(name="ratedealer", description="Rate a dealer 1-5 stars with an optional review")
@app_commands.describe(dealer_name="Name of the dealer", rating="Rating from 1 to 5 stars", review="Optional written review")
@app_commands.autocomplete(dealer_name=dealer_autocomplete)
@app_commands.choices(rating=[
    app_commands.Choice(name="⭐ 1 Star", value=1),
    app_commands.Choice(name="⭐⭐ 2 Stars", value=2),
    app_commands.Choice(name="⭐⭐⭐ 3 Stars", value=3),
    app_commands.Choice(name="⭐⭐⭐⭐ 4 Stars", value=4),
    app_commands.Choice(name="⭐⭐⭐⭐⭐ 5 Stars", value=5),
])
async def ratedealer_cmd(interaction: discord.Interaction, dealer_name: str, rating: int, review: str = None):
    dealer = find_dealer(dealer_name)
    if not dealer:
        await interaction.response.send_message(f"⚠️ Dealer '{dealer_name}' not found. Use `/dealers` to see all dealers.", ephemeral=True)
        return

    reviews = load_reviews()
    dealer_reviews = reviews.get(dealer["name"], [])

    # Check if user already reviewed today
    today = datetime.now(timezone.utc).date().isoformat()
    user_id = str(interaction.user.id)
    already_today = any(r.get("user_id") == user_id and r.get("date") == today for r in dealer_reviews)

    if already_today:
        await interaction.response.send_message(f"⚠️ You've already reviewed **{dealer['name']}** today. Come back tomorrow!", ephemeral=True)
        return

    # Save review
    new_review = {
        "user_id": user_id,
        "username": str(interaction.user),
        "rating": rating,
        "review": review,
        "date": today,
        "timestamp": int(datetime.now(timezone.utc).timestamp())
    }

    dealer_reviews.append(new_review)
    reviews[dealer["name"]] = dealer_reviews
    save_reviews(reviews)

    # Check for Trusted Reviewer role
    total_user_reviews = sum(1 for d_reviews in reviews.values() for r in d_reviews if r.get("user_id") == user_id)
    if total_user_reviews >= TRUSTED_REVIEWER_THRESHOLD:
        trusted_role = interaction.guild.get_role(TRUSTED_REVIEWER_ROLE_ID)
        if trusted_role and trusted_role not in interaction.user.roles:
            await interaction.user.add_roles(trusted_role)
            await interaction.followup.send(f"🎖️ Congratulations! You've earned the **@Trusted Reviewer** role for leaving {TRUSTED_REVIEWER_THRESHOLD} reviews!", ephemeral=True)

    # Confirm to user
    stars = "⭐" * rating
    await interaction.response.send_message(f"✅ Thanks for rating **{dealer['name']}** {stars}!", ephemeral=True)

    # Log to review-log channel (shows username to mods)
    log_channel = client.get_channel(REVIEW_LOG_CHANNEL_ID)
    if log_channel:
        log_embed = discord.Embed(
            title=f"New Review — {dealer['name']}",
            color=discord.Color.dark_gold(),
            timestamp=datetime.now(timezone.utc)
        )
        log_embed.add_field(name="Member", value=f"{interaction.user.mention} ({interaction.user})", inline=True)
        log_embed.add_field(name="Rating", value=stars, inline=True)
        if review:
            log_embed.add_field(name="Review", value=review[:500], inline=False)
        log_embed.set_footer(text="Visible to mods only")
        await log_channel.send(embed=log_embed)

@client.tree.command(name="suggestdealer", description="Suggest a new dealer to be added to the bot")
@app_commands.describe(dealer_name="Name of the dealer", url="Dealer website URL", reason="Why should this dealer be added?")
async def suggestdealer_cmd(interaction: discord.Interaction, dealer_name: str, url: str, reason: str = None):
    suggest_channel = client.get_channel(DEALER_SUGGEST_CHANNEL_ID)

    embed = discord.Embed(
        title="📬 New Dealer Suggestion",
        color=discord.Color.blurple(),
        timestamp=datetime.now(timezone.utc)
    )
    embed.add_field(name="Dealer Name", value=dealer_name, inline=True)
    embed.add_field(name="URL", value=url, inline=True)
    embed.add_field(name="Suggested By", value=f"{interaction.user.mention} ({interaction.user})", inline=False)
    if reason:
        embed.add_field(name="Reason", value=reason, inline=False)
    embed.add_field(name="Action", value="Use `/approvedealer` to approve or simply ignore to reject.", inline=False)
    embed.set_footer(text="Dealer Suggestion")

    if suggest_channel:
        await suggest_channel.send(embed=embed)
        await interaction.response.send_message(f"✅ Your suggestion for **{dealer_name}** has been sent to the mods for review!", ephemeral=True)
    else:
        await interaction.response.send_message("⚠️ Could not find the suggestions channel. Please contact a mod.", ephemeral=True)

@client.tree.command(name="leaderboard", description="Shows top rated dealers and most active reviewers")
async def leaderboard_cmd(interaction: discord.Interaction):
    reviews = load_reviews()

    # Top dealers by rating (min 3 reviews)
    dealer_ratings = []
    for dealer in get_all_dealers():
        rating, count = get_dealer_rating(dealer["name"])
        if rating and count >= 3:
            dealer_ratings.append((dealer["name"], rating, count))
    dealer_ratings.sort(key=lambda x: (x[1], x[2]), reverse=True)
    top_dealers = dealer_ratings[:10]

    # Top reviewers
    reviewer_counts = {}
    reviewer_names = {}
    for dealer_reviews in reviews.values():
        for r in dealer_reviews:
            uid = r.get("user_id")
            if uid:
                reviewer_counts[uid] = reviewer_counts.get(uid, 0) + 1
                reviewer_names[uid] = r.get("username", "Unknown")
    top_reviewers = sorted(reviewer_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    embed = discord.Embed(title="🏆 The Relic Registry Leaderboard", color=discord.Color.gold(), timestamp=datetime.now(timezone.utc))

    if top_dealers:
        dealer_text = ""
        medals = ["🥇", "🥈", "🥉"]
        for i, (name, rating, count) in enumerate(top_dealers):
            medal = medals[i] if i < 3 else f"**{i+1}.**"
            dealer_text += f"{medal} **{name}** — {stars_display(rating)} ({count} reviews)\n"
        embed.add_field(name="⭐ Top Rated Dealers", value=dealer_text, inline=False)
    else:
        embed.add_field(name="⭐ Top Rated Dealers", value="Not enough reviews yet — use `/ratedealer` to get started!", inline=False)

    if top_reviewers:
        reviewer_text = ""
        medals = ["🥇", "🥈", "🥉"]
        for i, (uid, count) in enumerate(top_reviewers):
            medal = medals[i] if i < 3 else f"**{i+1}.**"
            name = reviewer_names.get(uid, "Unknown")
            reviewer_text += f"{medal} **{name}** — {count} review(s)\n"
        embed.add_field(name="📝 Most Active Reviewers", value=reviewer_text, inline=False)
    else:
        embed.add_field(name="📝 Most Active Reviewers", value="No reviews yet!", inline=False)

    embed.set_footer(text="The Relic Registry — Dealer Update")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ==================== MOD COMMANDS ====================

@client.tree.command(name="rescan", description="🔒 Force an immediate check of all dealers")
async def rescan_cmd(interaction: discord.Interaction):
    if not is_mod(interaction.user):
        await interaction.response.send_message("🚫 You need Moderator permissions.", ephemeral=True)
        return
    bot_state["force_rescan"] = True
    await interaction.response.send_message("🔄 Forcing an immediate rescan...", ephemeral=True)

@client.tree.command(name="pause", description="🔒 Pause automatic dealer checking")
async def pause_cmd(interaction: discord.Interaction):
    if not is_mod(interaction.user):
        await interaction.response.send_message("🚫 You need Moderator permissions.", ephemeral=True)
        return
    if bot_state["paused"]:
        await interaction.response.send_message("⚠️ Bot is already paused.", ephemeral=True)
    else:
        bot_state["paused"] = True
        await interaction.response.send_message("⏸️ Bot paused.", ephemeral=True)

@client.tree.command(name="resume", description="🔒 Resume automatic dealer checking")
async def resume_cmd(interaction: discord.Interaction):
    if not is_mod(interaction.user):
        await interaction.response.send_message("🚫 You need Moderator permissions.", ephemeral=True)
        return
    if not bot_state["paused"]:
        await interaction.response.send_message("⚠️ Bot is already running.", ephemeral=True)
    else:
        bot_state["paused"] = False
        await interaction.response.send_message("▶️ Bot resumed!", ephemeral=True)

@client.tree.command(name="stats", description="🔒 Shows alert counts per dealer")
async def stats_cmd(interaction: discord.Interaction):
    if not is_mod(interaction.user):
        await interaction.response.send_message("🚫 You need Moderator permissions.", ephemeral=True)
        return
    stats = load_stats()
    embed = discord.Embed(title="📊 Alert Statistics", color=discord.Color.dark_gold(), timestamp=datetime.now(timezone.utc))
    for dealer in get_all_dealers():
        count = stats.get(dealer["name"], 0)
        embed.add_field(name=dealer["name"], value=f"🔔 {count} alert(s)", inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@client.tree.command(name="test", description="🔒 Send test notifications for all dealers")
async def test_cmd(interaction: discord.Interaction):
    if not is_mod(interaction.user):
        await interaction.response.send_message("🚫 You need Moderator permissions.", ephemeral=True)
        return
    await interaction.response.send_message("🧪 Running test...", ephemeral=True)
    channel = client.get_channel(CHANNEL_ID)
    for dealer in get_all_dealers():
        logo_file = os.path.join(SCRIPT_DIR, "logos", dealer["logo_file"])
        await send_alert(channel, dealer["name"], dealer["url"], logo_file, test=True)
        await asyncio.sleep(1)
    await interaction.followup.send("✅ Test complete!", ephemeral=True)

@client.tree.command(name="promo", description="🔒 Send the server promo message manually")
async def promo_cmd(interaction: discord.Interaction):
    if not is_mod(interaction.user):
        await interaction.response.send_message("🚫 You need Moderator permissions.", ephemeral=True)
        return
    channel = client.get_channel(CHANNEL_ID)
    banner_file = os.path.join(SCRIPT_DIR, "logos", "Server_Banner.png")
    embed = discord.Embed(
        title="🎖️ The Relic Registry",
        description="Looking for a great militaria community?\n\n**The Relic Registry** is a server for collectors, by collectors.\n\n📬 Get new item alerts from top dealers\n🏛️ Connect with fellow collectors\n\n[**Click here to join →**](http://discord.gg/therelicregistry)",
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
    bot_state["last_promo"] = datetime.now(timezone.utc)
    await interaction.response.send_message("✅ Promo sent!", ephemeral=True)

@client.tree.command(name="pausepromo", description="🔒 Pause the automatic 48 hour promo")
async def pausepromo_cmd(interaction: discord.Interaction):
    if not is_mod(interaction.user):
        await interaction.response.send_message("🚫 You need Moderator permissions.", ephemeral=True)
        return
    bot_state["promo_paused"] = True
    await interaction.response.send_message("⏸️ Promo messages paused.", ephemeral=True)

@client.tree.command(name="resumepromo", description="🔒 Resume the automatic 48 hour promo")
async def resumepromo_cmd(interaction: discord.Interaction):
    if not is_mod(interaction.user):
        await interaction.response.send_message("🚫 You need Moderator permissions.", ephemeral=True)
        return
    bot_state["promo_paused"] = False
    await interaction.response.send_message("▶️ Promo messages resumed!", ephemeral=True)

@client.tree.command(name="adddealer", description="🔒 Add a new dealer to monitor")
@app_commands.describe(name="Dealer name", url="Dealer website URL", logo_url="Direct URL to dealer logo image")
async def adddealer_cmd(interaction: discord.Interaction, name: str, url: str, logo_url: str = None):
    if not is_mod(interaction.user):
        await interaction.response.send_message("🚫 You need Moderator permissions.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    logo_filename = name.lower().replace(" ", "_").replace("'", "").replace(".", "") + ".png"
    logo_path = os.path.join(SCRIPT_DIR, "logos", logo_filename)
    if logo_url:
        async with aiohttp.ClientSession() as session:
            async with session.get(logo_url) as resp:
                if resp.status == 200:
                    with open(logo_path, "wb") as f:
                        f.write(await resp.read())
                else:
                    logo_filename = None
    match_keywords = [url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0], name.lower()]
    EMAIL_DEALERS.append({"name": name, "match": match_keywords, "logo_file": logo_filename or "", "url": url})
    embed = discord.Embed(title="✅ Dealer Added!", description=f"**{name}** added to email monitoring!\n\n[Visit Site]({url})", color=discord.Color.green())
    if logo_filename and os.path.exists(logo_path):
        file = discord.File(logo_path, filename="logo.png")
        embed.set_thumbnail(url="attachment://logo.png")
        await interaction.followup.send(file=file, embed=embed, ephemeral=True)
    else:
        await interaction.followup.send(embed=embed, ephemeral=True)

@client.tree.command(name="warningdealer", description="🔒 Flag a dealer as untrustworthy")
@app_commands.describe(dealer_name="Name of the dealer", reason="Reason for the warning")
@app_commands.autocomplete(dealer_name=dealer_autocomplete)
async def warningdealer_cmd(interaction: discord.Interaction, dealer_name: str, reason: str):
    if not is_mod(interaction.user):
        await interaction.response.send_message("🚫 You need Moderator permissions.", ephemeral=True)
        return
    dealer = find_dealer(dealer_name)
    if not dealer:
        await interaction.response.send_message(f"⚠️ Dealer '{dealer_name}' not found.", ephemeral=True)
        return
    warnings = load_warnings()
    warnings[dealer["name"]] = reason
    save_warnings(warnings)
    await interaction.response.send_message(f"⚠️ Warning added to **{dealer['name']}**: {reason}", ephemeral=True)

@client.tree.command(name="removewarning", description="🔒 Remove a warning from a dealer")
@app_commands.describe(dealer_name="Name of the dealer")
@app_commands.autocomplete(dealer_name=dealer_autocomplete)
async def removewarning_cmd(interaction: discord.Interaction, dealer_name: str):
    if not is_mod(interaction.user):
        await interaction.response.send_message("🚫 You need Moderator permissions.", ephemeral=True)
        return
    dealer = find_dealer(dealer_name)
    if not dealer:
        await interaction.response.send_message(f"⚠️ Dealer '{dealer_name}' not found.", ephemeral=True)
        return
    warnings = load_warnings()
    if dealer["name"] in warnings:
        del warnings[dealer["name"]]
        save_warnings(warnings)
        await interaction.response.send_message(f"✅ Warning removed from **{dealer['name']}**.", ephemeral=True)
    else:
        await interaction.response.send_message(f"⚠️ **{dealer['name']}** has no warning.", ephemeral=True)

@client.tree.command(name="deletereview", description="🔒 Delete an abusive review")
@app_commands.describe(dealer_name="Name of the dealer", review_index="Review number to delete (1 = most recent)")
async def deletereview_cmd(interaction: discord.Interaction, dealer_name: str, review_index: int):
    if not is_mod(interaction.user):
        await interaction.response.send_message("🚫 You need Moderator permissions.", ephemeral=True)
        return
    dealer = find_dealer(dealer_name)
    if not dealer:
        await interaction.response.send_message(f"⚠️ Dealer '{dealer_name}' not found.", ephemeral=True)
        return
    reviews = load_reviews()
    dealer_reviews = reviews.get(dealer["name"], [])
    if not dealer_reviews:
        await interaction.response.send_message(f"⚠️ No reviews found for **{dealer['name']}**.", ephemeral=True)
        return
    idx = len(dealer_reviews) - review_index
    if idx < 0 or idx >= len(dealer_reviews):
        await interaction.response.send_message(f"⚠️ Review #{review_index} not found.", ephemeral=True)
        return
    removed = dealer_reviews.pop(idx)
    reviews[dealer["name"]] = dealer_reviews
    save_reviews(reviews)
    await interaction.response.send_message(f"✅ Deleted review #{review_index} for **{dealer['name']}** by {removed.get('username', 'Unknown')}.", ephemeral=True)

@client.tree.command(name="approvedealer", description="🔒 Approve a suggested dealer and add them")
@app_commands.describe(name="Dealer name", url="Dealer website URL", logo_url="Direct URL to dealer logo")
async def approvedealer_cmd(interaction: discord.Interaction, name: str, url: str, logo_url: str = None):
    if not is_mod(interaction.user):
        await interaction.response.send_message("🚫 You need Moderator permissions.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    logo_filename = name.lower().replace(" ", "_").replace("'", "").replace(".", "") + ".png"
    logo_path = os.path.join(SCRIPT_DIR, "logos", logo_filename)
    if logo_url:
        async with aiohttp.ClientSession() as session:
            async with session.get(logo_url) as resp:
                if resp.status == 200:
                    with open(logo_path, "wb") as f:
                        f.write(await resp.read())
    match_keywords = [url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0], name.lower()]
    EMAIL_DEALERS.append({"name": name, "match": match_keywords, "logo_file": logo_filename, "url": url})
    await interaction.followup.send(f"✅ **{name}** has been approved and added to the bot!", ephemeral=True)

@client.tree.command(name="nextemail", description="🔒 Shows countdown to next email check")
async def nextemail_cmd(interaction: discord.Interaction):
    if not is_mod(interaction.user):
        await interaction.response.send_message("🚫 You need Moderator permissions.", ephemeral=True)
        return
    if bot_state["last_email_check"]:
        next_ts = int(bot_state["last_email_check"].timestamp()) + EMAIL_CHECK_INTERVAL
        last_ts = int(bot_state["last_email_check"].timestamp())
        await interaction.response.send_message(f"📧 **Next email check:** <t:{next_ts}:R>\n🕐 **Last check:** <t:{last_ts}:R>", ephemeral=True)
    else:
        await interaction.response.send_message("⚠️ No email check has run yet.", ephemeral=True)

@client.tree.command(name="nextpromo", description="🔒 Shows countdown to next automatic promo")
async def nextpromo_cmd(interaction: discord.Interaction):
    if not is_mod(interaction.user):
        await interaction.response.send_message("🚫 You need Moderator permissions.", ephemeral=True)
        return
    if bot_state["promo_paused"]:
        await interaction.response.send_message("⏸️ Promo is currently paused. Use `/resumepromo` to turn it back on.", ephemeral=True)
        return
    if bot_state["last_promo"]:
        next_ts = int(bot_state["last_promo"].timestamp()) + (48 * 3600)
        last_ts = int(bot_state["last_promo"].timestamp())
        await interaction.response.send_message(f"📣 **Next promo:** <t:{next_ts}:R>\n🕐 **Last promo:** <t:{last_ts}:R>", ephemeral=True)
    else:
        await interaction.response.send_message("📣 No promo sent yet. First auto-promo fires 48 hours after bot start.", ephemeral=True)

# ==================== EVENTS ====================
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    print(f"SCRIPT_DIR: {SCRIPT_DIR}")
    logos_path = os.path.join(SCRIPT_DIR, "logos")
    if os.path.exists(logos_path):
        print(f"Logos found: {os.listdir(logos_path)}")

async def main():
    async with client:
        client.loop.create_task(check_all_dealers())
        client.loop.create_task(check_email_dealers())
        client.loop.create_task(send_promo())
        await client.start(BOT_TOKEN)

asyncio.run(main())
