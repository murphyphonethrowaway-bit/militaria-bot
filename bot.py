import discord
from discord import app_commands
import asyncpg
from aiohttp import web
import logging
import traceback

# ==================== LOGGING SETUP ====================
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("MilitariaBot")
# Keep discord and aiohttp at INFO to avoid spam
logging.getLogger("discord").setLevel(logging.INFO)
logging.getLogger("aiohttp").setLevel(logging.INFO)
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
WAF_CHANNEL_ID = 1512532164871196864  # #waf-updates — role-gated channel
WAF_ROLE_ID = 1511101033349124318
DEALER_SUGGEST_CHANNEL_ID = 1511487755266556034  # #dealer-reviews channel
REVIEW_LOG_CHANNEL_ID = 1511487836220817561  # #review-log channel
TRUSTED_REVIEWER_ROLE_ID = 1511487130189168802  # @Trusted Reviewer role
TRUSTED_REVIEWER_THRESHOLD = 25  # Number of reviews to get Trusted Reviewer role
CHECK_INTERVAL = 600
EMAIL_CHECK_INTERVAL = 30

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('DB_URL')
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
    {"name": "All WAF Updates", "emoji": "🎖️", "role_id": 1511112093774905386, "keywords": []},
    {"name": "1957 Medals & Decorations", "emoji": "🎖️", "role_id": 1511112215544201367, "keywords": ["1957", "medal", "decoration"]},
    {"name": "Medals, Badges & Awards", "emoji": "🏅", "role_id": 1511112409451073828, "keywords": ["medal", "badge", "award", "cross", "iron cross"]},
    {"name": "Photos & Paper Items", "emoji": "📷", "role_id": 1511112501792739388, "keywords": ["photo", "paper", "document", "postcard", "soldbuch"]},
    {"name": "Uniforms", "emoji": "🪖", "role_id": 1511112564824866897, "keywords": ["uniform", "tunic", "jacket", "trousers", "coat"]},
    {"name": "Flags, Banners & Pennants", "emoji": "🚩", "role_id": 1511112671963906068, "keywords": ["flag", "banner", "pennant", "standard"]},
    {"name": "Equipment/Field Gear & Dog Tags", "emoji": "🎒", "role_id": 1511112754491297922, "keywords": ["equipment", "field gear", "footwear", "boot", "dog tag", "canteen"]},
    {"name": "Optics", "emoji": "🔭", "role_id": 1511112866495729706, "keywords": ["optic", "binocular", "scope", "telescope"]},
    {"name": "Cloth Headgear", "emoji": "🪖", "role_id": 1511112942358368307, "keywords": ["cloth", "headgear", "cap", "visor", "field cap"]},
    {"name": "German Helmets", "emoji": "⛑️", "role_id": 1511113046167130293, "keywords": ["helmet", "stahlhelm", "M35", "M40", "M42"]},
    {"name": "Belts & Buckles", "emoji": "🪢", "role_id": 1511113224869773393, "keywords": ["belt", "buckle", "brocade"]},
    {"name": "Edged Weapons", "emoji": "🗡️", "role_id": 1511113345816854529, "keywords": ["dagger", "sword", "bayonet", "knife", "blade"]},
    {"name": "Firearms & Ordnance", "emoji": "🔫", "role_id": 1511113443501932838, "keywords": ["firearm", "pistol", "rifle", "gun", "luger", "p38"]},
    {"name": "Imperial Militaria", "emoji": "👑", "role_id": 1511113528046653520, "keywords": ["imperial", "ww1", "1914", "1918", "pickelhaube"]},
    {"name": "Freikorps / Weimar Period", "emoji": "📜", "role_id": 1511113644015095839, "keywords": ["freikorps", "weimar"]},
    {"name": "U.S. & British Militaria", "emoji": "🦅", "role_id": 1511113709328662648, "keywords": ["american", "british", "allied", "usa", "uk"]},
    {"name": "International Militaria", "emoji": "🌍", "role_id": 1511113776923938869, "keywords": ["international", "italian", "japanese", "soviet", "french"]},
    {"name": "Books & Media", "emoji": "📚", "role_id": 1511118900488569015, "keywords": ["book", "media", "magazine", "manual"]},
    {"name": "Misc. Third Reich Items", "emoji": "📦", "role_id": 1511119017807581347, "keywords": ["misc", "third reich", "nsdap"]},
]

# ==================== DEALER CONFIG ====================
DEALERS = [
    {"name": "Weitze Militaria", "flag": "🇩🇪", "url": "https://www.weitze.com/neuheiten.html", "logo_file": "weitze.png", "item_selector": "a[href*='/militaria/']", "base_url": "https://www.weitze.com"},
    {"name": "Linda Mae Militaria", "flag": "🇺🇸", "url": "https://lindamaemilitaria.com/", "logo_file": "lindamae.png", "item_selector": ".product a", "base_url": "https://lindamaemilitaria.com"},
]

EMAIL_DEALERS = [
    {"name": "The Ruptured Duck", "flag": "🇺🇸", "match": ["therupturedduck.com", "ruptured duck"], "logo_file": "ruptured_duck.png", "url": "https://www.therupturedduck.com/collections/recently-added-items"},
    {"name": "War's End Shop", "flag": "🇺🇸", "match": ["warsendshop.com", "war's end", "wars end"], "logo_file": "warsend.png", "url": "https://www.warsendshop.com/collections/new-items"},
    {"name": "Lakeside Trader", "flag": "🇺🇸", "match": ["lakesidetrader.com", "lakeside trader"], "logo_file": "lakeside.png", "url": "https://www.lakesidetrader.com/recently-added-items/"},
    {"name": "Dutch Militaria", "flag": "🇳🇱", "match": ["dutchmilitaria.com", "dutch militaria"], "logo_file": "dutch_militaria.png", "url": "https://dutchmilitaria.com/"},
    {"name": "Militaria Sales", "flag": "🇺🇸", "match": ["militariasales.com", "militaria sales"], "logo_file": "militaria_sales.png", "url": "https://www.militariasales.com/new-item/"},
    {"name": "Military Collectibles", "flag": "🇺🇸", "match": ["militarycollectibles.com", "military collectibles"], "logo_file": "military_collectibles.png", "url": "https://militarycollectibles.com/shop?s=n"},
    {"name": "Military Collectors HQ", "flag": "🇺🇸", "match": ["militarycollectorshq.com", "military collectors hq"], "logo_file": "militarycollectorshq.png", "url": "https://militarycollectorshq.com/store-catalog"},
    {"name": "Soviet Orders", "flag": "🇺🇸", "match": ["sovietorders.com", "soviet orders"], "logo_file": "Soviet_Orders.png", "url": "https://sovietorders.com/new-in-store/"},
    {"name": "Empire's Past", "flag": "🇺🇸", "match": ["empirespast.com", "empire's past", "empires past"], "logo_file": "Empire_past.png", "url": "https://empirespast.com/newly-listed/"},
    {"name": "1944 Militaria", "flag": "🇺🇸", "match": ["1944militaria.com", "1944 militaria"], "logo_file": "1944militaria.png", "url": "https://www.1944militaria.com/New_Original_Items_s/1900.htm"},
    {"name": "International Military Antiques", "flag": "🇺🇸", "match": ["ima-usa.com", "international military antiques", "ima usa"], "logo_file": "ima.png", "url": "https://www.ima-usa.com/collections/new-arrivals"},
    {"name": "Wolfgang Historica", "flag": "🇩🇪", "match": ["wolfganghistorica.com", "wolfgang historica"], "logo_file": "wolfgang_historica.png", "url": "https://wolfganghistorica.com/"},
    {"name": "Enemy Militaria", "flag": "🇺🇸", "match": ["enemymilitaria.com", "enemy militaria"], "logo_file": "Enemy_Militaria.png", "url": "https://enemymilitaria.com/"},
    {"name": "Hiscoll Military Antiques", "flag": "🇬🇧", "match": ["hiscoll.com", "hiscoll military antiques", "hiscoll"], "logo_file": "hiscoll.png", "url": "https://hiscoll.com/shop"},
    {"name": "Relics of the Reich", "flag": "🇺🇸", "match": ["relicsofthereich.com", "relics of the reich"], "logo_file": "relicsofthereich.png", "url": "https://www.relicsofthereich.com/home"},
    {"name": "Epic Artifacts", "flag": "🇺🇸", "match": ["epicartifacts.com", "epic artifacts"], "logo_file": "Epic_artifacts.png", "url": "https://epicartifacts.com/newly-listed/"},
    {"name": "RG Militaria", "flag": "🇳🇱", "match": ["rg-militaria.com", "rg militaria"], "logo_file": "rgmilitaria.png", "url": "https://www.rg-militaria.com/new-items-nieuwe-items"},
    {"name": "Military Antiques Stockholm", "flag": "🇸🇪", "match": ["military-antiques-stockholm.com", "military antiques stockholm"], "logo_file": "Military_Antiques_Stockholm.png", "url": "https://www.military-antiques-stockholm.com/shop/"},
    {"name": "Oorlogsspullen", "flag": "🇳🇱", "match": ["oorlogsspullen.nl", "oorlogsspullen"], "logo_file": "Oorlogspullen.png", "url": "https://oorlogsspullen.nl/product-categorie/new/"},
    {"name": "Wittmann Antique Militaria", "flag": "🇩🇪", "match": ["wwiidaggers.com", "wittmann antique militaria", "wittmann"], "logo_file": "wam.png", "url": "https://www.wwiidaggers.com/updates.htm"},
    {"name": "RBNr Militaria", "flag": "🇩🇪", "match": ["rbnr.it", "rbnr militaria", "rbnr"], "logo_file": "RBNR.png", "url": "https://en.rbnr.it/collections/all"},
    {"name": "Iraqi Militaria", "flag": "🇺🇸", "match": ["iraqimilitaria.com", "iraqi militaria"], "logo_file": "iraqi_militaria.png", "url": "https://www.iraqimilitaria.com/"},
    {"name": "Danzig Militaria", "flag": "🇵🇱", "match": ["danzigmilitaria.com", "danzig militaria"], "logo_file": "Danzig_Militaria.png", "url": "https://danzigmilitaria.com/shop/"},
    {"name": "FJM44", "flag": "🇫🇷", "match": ["fjm44.com", "fjm44", "fjm 44"], "logo_file": "fjm44.png", "url": "https://fjm44.com/product-category/militaria/"},
    {"name": "Kurland", "flag": "🇩🇪", "match": ["kurland-docs.com", "kurland"], "logo_file": "kurland.png", "url": "https://www.kurland-docs.com/shop.php"},
    {"name": "Queen City Militaria", "flag": "🇺🇸", "match": ["queencitymilitaria.com", "queen city militaria"], "logo_file": "queen_city_militaria.png", "url": "https://www.queencitymilitaria.com/"},
    {"name": "Combat Relics", "flag": "🇺🇸", "match": ["combat-relics.com", "combat relics"], "logo_file": "Combat_relics.png", "url": "https://www.combat-relics.com/"},
    {"name": "Tiger Militaria", "flag": "🇬🇧", "match": ["tigermilitaria.com", "tiger militaria"], "logo_file": "TigerMilitaria.png", "url": "https://tigermilitaria.com/shop?showPerPage=24"},
    {"name": "WAF Estate", "flag": "🇺🇸", "match": ["wehrmacht-awards.com", "waf estate", "e-stand", "estand", "militaria e-stand"], "logo_file": "waf.png", "url": "https://www.wehrmacht-awards.com/forums/forum/the-militaria-e-stand", "waf": True},
    {"name": "Griffin Militaria", "flag": "🇺🇸", "match": ["griffinmilitaria.com", "griffin militaria"], "logo_file": "Griffin_Militaria.png", "url": "https://griffinmilitaria.com/"},
    {"name": "EA Militaria", "flag": "🇳🇱", "match": ["ea-militaria.com", "ea militaria"], "logo_file": "eamilitaria.png", "url": "https://www.ea-militaria.com/new-items"},
    {"name": "Militaria Plaza", "flag": "🇳🇱", "match": ["militariaplaza.nl", "militaria plaza"], "logo_file": "Militaria_Plaza.png", "url": "https://militariaplaza.nl/new"},
    {"name": "The Collector's Guild", "flag": "🇺🇸", "match": ["germanmilitaria.com", "collector's guild", "collectors guild"], "logo_file": "germanmilitaria.png", "url": "https://www.germanmilitaria.com/Advanced.html"},
    {"name": "General Assault Militaria", "flag": "🇺🇸", "match": ["generalassaultmilitaria.com", "general assault militaria", "gam"], "logo_file": "gam.png", "url": "https://www.generalassaultmilitaria.com/"},
    {"name": "Bevo Militaria", "flag": "🇩🇪", "match": ["bevo-militaria.com", "bevo militaria"], "logo_file": "Bevo_Militaria.png", "url": "https://bevo-militaria.com/shop/"},
    {"name": "The Canadian Soldier", "flag": "🇨🇦", "match": ["thecanadiansoldier.com", "canadian soldier"], "logo_file": "the_canadian_soldier.png", "url": "https://thecanadiansoldier.com/en-us/collections/newly-listed"},
    {"name": "Wehrmacht Militaria", "flag": "🇺🇸", "match": ["wehrmacht-militaria.com", "Wehrmacht militaria"], "logo_file": "Wehrmacht_Militaria.png", "url": "https://wehrmacht-militaria.com/shop"},
    {"name": "ThirdReich Militaria", "flag": "🇮🇹", "match": ["thirdreich-militaria.com", "thirdreich militaria", "third reich militaria"], "logo_file": "thirdreich_militaria.png", "url": "https://www.thirdreich-militaria.com/"},
    {"name": "Richter Historica", "flag": "🇩🇪", "match": ["richter-historica.de", "richter historica"], "logo_file": "Richter_Historica.png", "url": "https://richter-historica.de/en/10-militaria"},
    {"name": "Military Antiques Toronto", "flag": "🇨🇦", "match": ["militaryantiquestoronto.com", "military antiques toronto"], "logo_file": "Military_Antiques_Toronto.png", "url": "https://militaryantiquestoronto.com/new-items/"},
    {"name": "Giel's Militaria", "flag": "🇧🇪", "match": ["gielsmilitaria.com", "giel's militaria", "giels militaria"], "logo_file": "giels_militaria.png", "url": "https://www.gielsmilitaria.com/"},
    {"name": "SMG War Relics", "flag": "🇺🇸", "match": ["war-relics.com", "smg war relics", "smg militaria"], "logo_file": "smg_war_relics.png", "url": "https://war-relics.com/shop/"},
    {"name": "Hanna's Militaria", "flag": "🇺🇸", "match": ["hannasmilitaria.com", "hanna's militaria", "hannas militaria"], "logo_file": "hannas_militaria.png", "url": "https://hannasmilitaria.com/newly-listed/"},
    {"name": "Marna Militaria", "flag": "🇳🇱", "match": ["marnamilitaria.com", "marna militaria"], "logo_file": "Marna_militaria.png", "url": "https://marnamilitaria.com/shop.php"},
    {"name": "CS Militaria", "flag": "🇬🇧", "match": ["csmilitaria.co.uk", "cs militaria"], "logo_file": "cs_militaria.png", "url": "https://csmilitaria.co.uk/shop.php"},
    {"name": "Chase Militaria", "flag": "🇬🇧", "match": ["chasemilitaria.com", "chase militaria"], "logo_file": "chase_militaria.png", "url": "https://chasemilitaria.com/shop.php"},
    {"name": "WorldWar 2 Collectibles", "flag": "🇬🇧", "match": ["worldwarcollectibles.com", "worldwar2collectibles.com", "world war 2 collectibles", "worldwar 2 collectibles"], "logo_file": "Worldwar2collectibles.png", "url": "https://www.worldwarcollectibles.com/shop.php"},
    {"name": "E-Medals", "flag": "🇨🇦", "match": ["emedals.com", "e-medals", "emedals"], "logo_file": "e_medals.png", "url": "https://www.emedals.com/collections/newly-listed"},
    {"name": "Espenlaub Militaria", "flag": "🇪🇪", "match": ["aboutww2militaria.com", "espenlaub militaria", "espenlaub"], "logo_file": "espenlaub_militaria.png", "url": "https://aboutww2militaria.com/new-items.html"},
]

# ==================== BOT SETUP ====================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class MilitariaBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.db = None

    async def setup_hook(self):
        try:
            self.db = await asyncpg.create_pool(DATABASE_URL)
            logger.info("Database connection pool created successfully")
            await self.init_db()
            await self.tree.sync()
            logger.info("Slash commands synced!")
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            logger.error(traceback.format_exc())
            raise

    async def init_db(self):
        async with self.db.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS reviews (
                    id SERIAL PRIMARY KEY,
                    dealer_name TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    username TEXT NOT NULL,
                    rating INTEGER NOT NULL,
                    review TEXT,
                    date TEXT NOT NULL,
                    timestamp BIGINT NOT NULL,
                    status TEXT DEFAULT 'pending'
                )
            ''')
            await conn.execute('''
                ALTER TABLE reviews ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'pending'
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS warnings (
                    dealer_name TEXT PRIMARY KEY,
                    reason TEXT NOT NULL
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS seen_emails (
                    msg_id TEXT PRIMARY KEY
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS dealer_stats (
                    dealer_name TEXT PRIMARY KEY,
                    alert_count INTEGER DEFAULT 0
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS blocked_reviewers (
                    user_id TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    reason TEXT,
                    timestamp BIGINT NOT NULL
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS reviewer_warnings (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    username TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    timestamp BIGINT NOT NULL
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS dealer_follows (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    dealer_name TEXT NOT NULL,
                    timestamp BIGINT NOT NULL,
                    UNIQUE(user_id, dealer_name)
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS waf_watchlist (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    forum_url TEXT NOT NULL,
                    item_title TEXT NOT NULL,
                    last_price TEXT DEFAULT '',
                    date_added BIGINT NOT NULL,
                    UNIQUE(user_id, forum_url)
                )
            ''')
        logger.info("Database initialized successfully!")

client = MilitariaBot()

# ==================== FILE PATHS (still used for seen_items) ====================
SEEN_FILE = "seen_items.json"

# Griffin Militaria page title to URL mapping
GRIFFIN_PAGES = {
    "cloth insignia": "https://griffinmilitaria.com/product-category/united-states/world-war-ii/cloth-insignia/",
    "chevrons": "https://griffinmilitaria.com/product-category/united-states/world-war-ii/chevrons/",
    "crest": "https://griffinmilitaria.com/product-category/united-states/world-war-ii/crest-dis/",
    "headgear": "https://griffinmilitaria.com/product-category/united-states/world-war-ii/headgear/",
    "medals and ribbons": "https://griffinmilitaria.com/product-category/united-states/world-war-ii/medals-and-ribbons/",
    "metal insignia": "https://griffinmilitaria.com/product-category/united-states/world-war-ii/metal-insignia/",
    "navy rates": "https://griffinmilitaria.com/product-category/united-states/world-war-ii/navy-rates/",
    "posters": "https://griffinmilitaria.com/product-category/united-states/world-war-ii/posters/",
    "sweetheart": "https://griffinmilitaria.com/product-category/united-states/world-war-ii/sweetheart-homefront/",
    "uniforms": "https://griffinmilitaria.com/product-category/united-states/world-war-ii/uniforms/",
    "united states paper": "https://griffinmilitaria.com/product-category/united-states/world-war-ii/paper/",
    "wings": "https://griffinmilitaria.com/product-category/united-states/world-war-ii/wings/",
    "wwi": "https://griffinmilitaria.com/product-category/united-states/world-war-i/",
    "dog tags": "https://griffinmilitaria.com/product-category/united-states/world-war-i/dog-tags/",
    "field gear": "https://griffinmilitaria.com/product-category/united-states/world-war-i/field-gear/",
    "patches": "https://griffinmilitaria.com/product-category/united-states/world-war-i/patches/",
    "cold war": "https://griffinmilitaria.com/product-category/united-states/cold-war-steins/",
    "pre-wwi": "https://griffinmilitaria.com/product-category/united-states/pre-wwi/",
    "accoutrements": "https://griffinmilitaria.com/product-category/united-states/revolutionary-war-to-civil-war/accoutrements/",
    "edged weapons": "https://griffinmilitaria.com/product-category/united-states/revolutionary-war-to-civil-war/edged-weapons/",
    "civil war": "https://griffinmilitaria.com/product-category/united-states/civil-war/veterans/",
    "japanese": "https://griffinmilitaria.com/product-category/japan/",
    "german photos": "https://griffinmilitaria.com/product-category/military-photographs/german/",
    "american photos": "https://griffinmilitaria.com/product-category/military-photographs/american/",
    "other countries photos": "https://griffinmilitaria.com/product-category/military-photographs/other-countries/",
    "vietnam": "https://griffinmilitaria.com/product-category/vietnam-war-era/",
    "other countries": "https://griffinmilitaria.com/product-category/other-countries/",
    "belts": "https://griffinmilitaria.com/product-category/germany/world-war-ii/belts-buckles/",
    "documents": "https://griffinmilitaria.com/product-category/germany/world-war-ii/documents-photos/",
    "flags": "https://griffinmilitaria.com/product-category/germany/world-war-ii/flags-banners/",
    "medals": "https://griffinmilitaria.com/product-category/germany/world-war-ii/medals-badges/",
    "ribbon bars": "https://griffinmilitaria.com/product-category/germany/world-war-ii/ribbon-bars/",
    "stickpins": "https://griffinmilitaria.com/product-category/germany/world-war-ii/stickpins/",
    "steins": "https://griffinmilitaria.com/product-category/germany/world-war-ii/third-reich-steins/",
    "tinnies": "https://griffinmilitaria.com/product-category/germany/world-war-ii/tinnies/",
    "imperial": "https://griffinmilitaria.com/product-category/germany/world-war-i/imperial-steins/",
}

def lookup_griffin_url(title):
    """Try to match a Changedetection.io watch title to a Griffin page URL."""
    if not title:
        return "https://griffinmilitaria.com/"
    title_lower = title.lower()
    for keyword, url in GRIFFIN_PAGES.items():
        if keyword in title_lower:
            return url
    return "https://griffinmilitaria.com/"

bot_state = {
    "paused": False,
    "last_check": None,
    "force_rescan": False,
    "promo_paused": False,
    "last_email_check": None,
    "last_promo": None,
    "griffin_buffer": [],
    "griffin_timer": None,
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

# ==================== DATABASE FUNCTIONS ====================
async def db_get_reviews(dealer_name, status='approved'):
    async with client.db.acquire() as conn:
        if status == 'all':
            rows = await conn.fetch("SELECT * FROM reviews WHERE dealer_name=$1 ORDER BY timestamp ASC", dealer_name)
        else:
            rows = await conn.fetch("SELECT * FROM reviews WHERE dealer_name=$1 AND status=$2 ORDER BY timestamp ASC", dealer_name, status)
        return [dict(r) for r in rows]

async def db_approve_review(review_id):
    async with client.db.acquire() as conn:
        await conn.execute("UPDATE reviews SET status='approved' WHERE id=$1", review_id)

async def db_decline_review(review_id):
    async with client.db.acquire() as conn:
        await conn.execute("UPDATE reviews SET status='declined' WHERE id=$1", review_id)

async def db_is_blocked(user_id):
    async with client.db.acquire() as conn:
        row = await conn.fetchrow("SELECT 1 FROM blocked_reviewers WHERE user_id=$1", str(user_id))
        return row is not None

async def db_block_reviewer(user_id, username, reason):
    async with client.db.acquire() as conn:
        await conn.execute(
            "INSERT INTO blocked_reviewers (user_id, username, reason, timestamp) VALUES ($1,$2,$3,$4) ON CONFLICT (user_id) DO UPDATE SET reason=$3",
            str(user_id), username, reason, int(datetime.now(timezone.utc).timestamp())
        )

async def db_unblock_reviewer(user_id):
    async with client.db.acquire() as conn:
        await conn.execute("DELETE FROM blocked_reviewers WHERE user_id=$1", str(user_id))

async def db_add_reviewer_warning(user_id, username, reason):
    async with client.db.acquire() as conn:
        await conn.execute(
            "INSERT INTO reviewer_warnings (user_id, username, reason, timestamp) VALUES ($1,$2,$3,$4)",
            str(user_id), username, reason, int(datetime.now(timezone.utc).timestamp())
        )

# ==================== WAF WATCHLIST DB FUNCTIONS ====================

async def db_watch_item(user_id, forum_url, item_title, price=""):
    async with client.db.acquire() as conn:
        await conn.execute(
            "INSERT INTO waf_watchlist (user_id, forum_url, item_title, last_price, date_added) VALUES ($1,$2,$3,$4,$5) ON CONFLICT (user_id, forum_url) DO NOTHING",
            str(user_id), forum_url, item_title, price, int(datetime.now(timezone.utc).timestamp())
        )

async def db_unwatch_item(user_id, forum_url):
    async with client.db.acquire() as conn:
        await conn.execute("DELETE FROM waf_watchlist WHERE user_id=$1 AND forum_url=$2", str(user_id), forum_url)

async def db_get_watchlist(user_id):
    async with client.db.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM waf_watchlist WHERE user_id=$1 ORDER BY date_added DESC", str(user_id))
        return [dict(r) for r in rows]

async def db_get_item_watchers(forum_url):
    async with client.db.acquire() as conn:
        rows = await conn.fetch("SELECT user_id, last_price FROM waf_watchlist WHERE forum_url=$1", forum_url)
        return [dict(r) for r in rows]

async def db_update_watch_price(user_id, forum_url, new_price):
    async with client.db.acquire() as conn:
        await conn.execute("UPDATE waf_watchlist SET last_price=$1 WHERE user_id=$2 AND forum_url=$3", new_price, str(user_id), forum_url)

async def db_is_watching(user_id, forum_url):
    async with client.db.acquire() as conn:
        row = await conn.fetchrow("SELECT 1 FROM waf_watchlist WHERE user_id=$1 AND forum_url=$2", str(user_id), forum_url)
        return row is not None

async def db_cleanup_watchlist():
    cutoff = int(datetime.now(timezone.utc).timestamp()) - (90 * 24 * 3600)
    async with client.db.acquire() as conn:
        deleted = await conn.fetchval("SELECT COUNT(*) FROM waf_watchlist WHERE date_added < $1", cutoff)
        await conn.execute("DELETE FROM waf_watchlist WHERE date_added < $1", cutoff)
        if deleted:
            logger.info(f"[Watchlist] Cleaned up {deleted} expired watchlist entries")

async def db_follow_dealer(user_id, dealer_name):
    async with client.db.acquire() as conn:
        await conn.execute(
            "INSERT INTO dealer_follows (user_id, dealer_name, timestamp) VALUES ($1,$2,$3) ON CONFLICT DO NOTHING",
            str(user_id), dealer_name, int(datetime.now(timezone.utc).timestamp())
        )

async def db_unfollow_dealer(user_id, dealer_name):
    async with client.db.acquire() as conn:
        await conn.execute("DELETE FROM dealer_follows WHERE user_id=$1 AND dealer_name=$2", str(user_id), dealer_name)

async def db_is_following(user_id, dealer_name):
    async with client.db.acquire() as conn:
        row = await conn.fetchrow("SELECT 1 FROM dealer_follows WHERE user_id=$1 AND dealer_name=$2", str(user_id), dealer_name)
        return row is not None

async def db_get_follows(user_id):
    async with client.db.acquire() as conn:
        rows = await conn.fetch("SELECT dealer_name FROM dealer_follows WHERE user_id=$1 ORDER BY timestamp ASC", str(user_id))
        return [r["dealer_name"] for r in rows]

async def db_get_dealer_followers(dealer_name):
    async with client.db.acquire() as conn:
        rows = await conn.fetch("SELECT user_id FROM dealer_follows WHERE dealer_name=$1", dealer_name)
        return [r["user_id"] for r in rows]

async def db_get_reviewer_stats(user_id):
    async with client.db.acquire() as conn:
        total = await conn.fetchval("SELECT COUNT(*) FROM reviews WHERE user_id=$1", str(user_id))
        approved = await conn.fetchval("SELECT COUNT(*) FROM reviews WHERE user_id=$1 AND status='approved'", str(user_id))
        declined = await conn.fetchval("SELECT COUNT(*) FROM reviews WHERE user_id=$1 AND status='declined'", str(user_id))
        pending = await conn.fetchval("SELECT COUNT(*) FROM reviews WHERE user_id=$1 AND status='pending'", str(user_id))
        warnings = await conn.fetchval("SELECT COUNT(*) FROM reviewer_warnings WHERE user_id=$1", str(user_id))
        blocked = await db_is_blocked(user_id)
        return {"total": total, "approved": approved, "declined": declined, "pending": pending, "warnings": warnings, "blocked": blocked}

async def db_get_all_reviews(status='approved'):
    async with client.db.acquire() as conn:
        if status == 'all':
            rows = await conn.fetch("SELECT * FROM reviews ORDER BY timestamp ASC")
        else:
            rows = await conn.fetch("SELECT * FROM reviews WHERE status=$1 ORDER BY timestamp ASC", status)
        result = {}
        for r in rows:
            d = dict(r)
            if d["dealer_name"] not in result:
                result[d["dealer_name"]] = []
            result[d["dealer_name"]].append(d)
        return result

async def db_add_review(dealer_name, user_id, username, rating, review, date, timestamp):
    async with client.db.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO reviews (dealer_name, user_id, username, rating, review, date, timestamp) VALUES ($1,$2,$3,$4,$5,$6,$7) RETURNING id",
            dealer_name, user_id, username, rating, review, date, timestamp
        )
        return row["id"]

async def db_delete_review(review_id):
    async with client.db.acquire() as conn:
        await conn.execute("DELETE FROM reviews WHERE id=$1", review_id)

async def db_get_warning(dealer_name):
    async with client.db.acquire() as conn:
        row = await conn.fetchrow("SELECT reason FROM warnings WHERE dealer_name=$1", dealer_name)
        return row["reason"] if row else None

async def db_set_warning(dealer_name, reason):
    async with client.db.acquire() as conn:
        await conn.execute(
            "INSERT INTO warnings (dealer_name, reason) VALUES ($1,$2) ON CONFLICT (dealer_name) DO UPDATE SET reason=$2",
            dealer_name, reason
        )

async def db_remove_warning(dealer_name):
    async with client.db.acquire() as conn:
        await conn.execute("DELETE FROM warnings WHERE dealer_name=$1", dealer_name)

async def db_is_email_seen(msg_id):
    async with client.db.acquire() as conn:
        row = await conn.fetchrow("SELECT 1 FROM seen_emails WHERE msg_id=$1", msg_id)
        return row is not None

async def db_mark_email_seen(msg_id):
    async with client.db.acquire() as conn:
        await conn.execute("INSERT INTO seen_emails (msg_id) VALUES ($1) ON CONFLICT DO NOTHING", msg_id)

async def db_get_stat(dealer_name):
    async with client.db.acquire() as conn:
        row = await conn.fetchrow("SELECT alert_count FROM dealer_stats WHERE dealer_name=$1", dealer_name)
        return row["alert_count"] if row else 0

async def db_increment_stat(dealer_name):
    async with client.db.acquire() as conn:
        await conn.execute(
            "INSERT INTO dealer_stats (dealer_name, alert_count) VALUES ($1,1) ON CONFLICT (dealer_name) DO UPDATE SET alert_count=dealer_stats.alert_count+1",
            dealer_name
        )

async def db_get_all_stats():
    async with client.db.acquire() as conn:
        rows = await conn.fetch("SELECT dealer_name, alert_count FROM dealer_stats")
        return {r["dealer_name"]: r["alert_count"] for r in rows}



def is_mod(member):
    return member.guild_permissions.administrator or member.guild_permissions.manage_guild

# ==================== REVIEW HELPERS ====================
def get_dealer_rating_sync(dealer_reviews):
    if not dealer_reviews:
        return None, 0
    avg = sum(r["rating"] for r in dealer_reviews) / len(dealer_reviews)
    return round(avg, 1), len(dealer_reviews)

async def get_dealer_rating(dealer_name):
    dealer_reviews = await db_get_reviews(dealer_name)
    return get_dealer_rating_sync(dealer_reviews)

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
    filtered = [d for d in all_dealers if current.lower() in d["name"].lower()]
    return [app_commands.Choice(name=d["name"], value=d["name"]) for d in filtered][:25]

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
    warning = await db_get_warning(name)
    dealer_reviews = await db_get_reviews(name)
    rating, review_count = get_dealer_rating_sync(dealer_reviews)

    dealer_info = find_dealer(name)
    flag = dealer_info.get("flag", "🌐") if dealer_info else "🌐"
    title = f"🧪 TEST — {name}" if test else f"🆕 {flag} New Items at {name}!"
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
        logger.error(f"Failed to send message for {name}: {e}\n{traceback.format_exc()}")

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
        await db_increment_stat(name)
        await send_alert(channel, name, url, logo_file)
    else:
        print(f"[{name}] No new items ({len(current_items)} items unchanged).")

async def check_gmail_async():
    triggered = []
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        mail.select("inbox")
        _, messages = mail.search(None, "UNSEEN")
        email_ids = messages[0].split()
        logger.info(f"[Gmail] Found {len(email_ids)} unread email(s).")
        for eid in email_ids:
            _, msg_data = mail.fetch(eid, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            msg_id = msg.get("Message-ID", str(eid))
            logger.debug(f"[Gmail] Checking msg_id: {msg_id}")
            if await db_is_email_seen(msg_id):
                logger.info(f"[Gmail] Skipping already seen email: {msg_id}")
                continue
            await db_mark_email_seen(msg_id)
            sender = msg.get("From", "").lower()
            subject_raw = msg.get("Subject", "")
            subject = decode_header(subject_raw)[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode(errors="replace")
            subject = subject.lower()
            # Extract body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors="replace")
                        break
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode(errors="replace")
            logger.info(f"[Gmail] New email from: {sender} | Subject: {subject}")
            logger.debug(f"[Gmail] Body preview: {body[:100]}")
            matched = False
            for dealer in EMAIL_DEALERS:
                for keyword in dealer["match"]:
                    if keyword.lower() in sender or keyword.lower() in subject:
                        logger.info(f"[Gmail] Matched dealer: {dealer['name']}")
                        triggered.append((dealer, subject, body))
                        matched = True
                        break
                if matched:
                    break
            if not matched:
                logger.info(f"[Gmail] No dealer matched for: {subject}")
        mail.logout()
    except Exception as e:
        logger.error(f"[Gmail] Error checking email: {e}\n{traceback.format_exc()}")
    return triggered

# ==================== BACKGROUND TASKS ====================
async def check_all_dealers():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    if not channel:
        print("ERROR: Could not find channel.")
        return
    logger.info(f"Bot ready! Monitoring {len(DEALERS)} web dealers + {len(EMAIL_DEALERS)} email dealers.")
    while not client.is_closed():
        if bot_state["paused"] and not bot_state["force_rescan"]:
            await asyncio.sleep(30)
            continue
        bot_state["force_rescan"] = False
        logger.info(f"--- Checking dealers at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
        bot_state["last_check"] = datetime.now(timezone.utc)
        seen = load_seen()
        async with aiohttp.ClientSession() as session:
            for dealer in DEALERS:
                await check_dealer(session, dealer, seen, channel)
                await asyncio.sleep(2)
        save_seen(seen)
        logger.info(f"--- Done. Next check in {CHECK_INTERVAL//60} minutes. ---")
        await asyncio.sleep(CHECK_INTERVAL)

# ==================== WAF EMAIL PARSER ====================

BUMP_KEYWORDS = ["up", "bump", "still available", "still for sale", "ttt", "to the top", "glws", "price reduced", "price drop", "make offer", "reduced"]

def parse_waf_email(subject, body):
    """Parse a WAF email and extract item title, prices and check if it's a bump."""
    import re

    # Extract item title — line immediately after "has made a new post under"
    title_match = re.search(r"has made a new post under\s*\n+(.+)", body, re.IGNORECASE)
    item_title = title_match.group(1).strip() if title_match else subject.strip()

    # Extract poster name
    poster_match = re.search(r"Dear ZiM,\s*\n+(\S+)\s+has made a new post", body, re.IGNORECASE)
    poster = poster_match.group(1).strip() if poster_match else "Unknown"

    # Extract forum URL
    url_match = re.search(r"https?://www\.wehrmacht-awards\.com/forums/node/\d+", body)
    forum_url = url_match.group(0).strip() if url_match else ""

    # Extract message body between *** delimiters
    msg_match = re.search(r"\*{3,}(.+?)\*{3,}", body, re.DOTALL)
    msg_body = msg_match.group(1).strip() if msg_match else ""

    # Strip BBCode-like tags from msg_body
    msg_body_clean = re.sub(r"\[/?[A-Z]+[^\]]*\]", "", msg_body, flags=re.IGNORECASE).strip()

    # Check if it's a bump — only look inside the actual message body
    is_bump = False
    if msg_body_clean:
        msg_lower = msg_body_clean.lower().strip()
        is_bump = (
            any(keyword == msg_lower for keyword in BUMP_KEYWORDS) or
            (len(msg_lower) < 15 and any(keyword in msg_lower for keyword in BUMP_KEYWORDS))
        )

    # Extract prices from message body only (avoids grabbing node IDs from URLs)
    price_pattern = r"(?:[\$\u20ac\xa3]\s*\d{2,6}(?:[.,]\d{2})?|\d{2,6}(?:[.,]\d{2})?\s*(?:EUR|USD|GBP))"
    raw_prices = re.findall(price_pattern, msg_body_clean, re.IGNORECASE)
    clean_prices = []
    seen_prices = set()
    for p in raw_prices:
        p = p.strip().upper().replace("EURO", "EUR").replace("DOLLARS", "USD")
        if p not in seen_prices:
            seen_prices.add(p)
            clean_prices.append(p)
    clean_prices = clean_prices[:5]

    # Determine category from the email subject line
    # Subject format: "A new post in your Forum Channel subscription: CATEGORY NAME"
    subject_cat_match = re.search(r"subscription:\s*(.+)", subject, re.IGNORECASE)
    subject_category = subject_cat_match.group(1).strip().lower() if subject_cat_match else ""

    # Match subject category to a WAF role by name first
    matched_role_id = None
    for cat in WAF_CATEGORIES:
        if cat["name"] == "All WAF Updates":
            continue
        if subject_category and cat["name"].lower() == subject_category:
            matched_role_id = cat["role_id"]
            break

    # Fall back to keyword matching against subject category string
    if not matched_role_id:
        for cat in WAF_CATEGORIES:
            if cat["name"] == "All WAF Updates":
                continue
            for keyword in cat["keywords"]:
                if keyword.lower() in subject_category:
                    matched_role_id = cat["role_id"]
                    break
            if matched_role_id:
                break

    # Default to All WAF Updates
    if not matched_role_id:
        matched_role_id = WAF_CATEGORIES[0]["role_id"]

    # Resolve category display name from role ID
    category_name = "General"
    for cat in WAF_CATEGORIES:
        if cat["role_id"] == matched_role_id:
            category_name = cat["name"]
            break

    logger.debug(f"[WAF] Parsed: title='{item_title}' | category='{category_name}' | poster='{poster}' | url='{forum_url}' | prices={clean_prices} | bump={is_bump}")

    return {
        "item_title": item_title,
        "category": category_name,
        "poster": poster,
        "forum_url": forum_url,
        "is_bump": is_bump,
        "prices": clean_prices,
        "role_id": matched_role_id,
        "msg_body": msg_body_clean,
    }

async def send_waf_alert(channel, parsed, guild):
    """Send a formatted WAF Estate alert to members with the correct role."""
    if parsed["is_bump"]:
        logger.info(f"[WAF] Skipping bump for: {parsed['item_title']}")
        return

    role = guild.get_role(parsed["role_id"]) if guild else None

    price_str = " | ".join(parsed["prices"]) if parsed["prices"] else ""

    # Look up emoji for this category
    cat_emoji = "🎖️"
    for cat in WAF_CATEGORIES:
        if cat["role_id"] == parsed["role_id"]:
            cat_emoji = cat.get("emoji", "🎖️")
            break

    # Embed: category as title, item name in description
    description = f"**{cat_emoji} {parsed['item_title']}**\n"
    if price_str:
        description += f"\n💰 **{price_str}**\n"
    if parsed["forum_url"]:
        description += f"\n[**View Listing →**]({parsed['forum_url']})"

    embed = discord.Embed(
        title=f"{cat_emoji} {parsed['category']}",
        description=description,
        color=discord.Color.dark_gold(),
        timestamp=datetime.now(timezone.utc)
    )
    embed.set_footer(text="WAF Estate — The Relic Registry")

    logo_file = os.path.join(SCRIPT_DIR, "logos", "waf.png")
    file = None
    if os.path.exists(logo_file):
        file = discord.File(logo_file, filename="logo.png")
        embed.set_thumbnail(url="attachment://logo.png")

    content_msg = f"<@&{parsed['role_id']}>" if role else None

    watch_view = WatchItemView(parsed["forum_url"], parsed["item_title"], price_str) if parsed["forum_url"] else None

    try:
        if file:
            await channel.send(content=content_msg, file=file, embed=embed, view=watch_view)
        else:
            await channel.send(content=content_msg, embed=embed, view=watch_view)
        logger.info(f"[WAF] Alert sent for: {parsed['item_title']} | Price: {price_str} | Role: {role.name if role else 'Unknown'}")
    except Exception as e:
        logger.error(f"[WAF] Failed to send alert: {e}")

    # DM watchers if this is a bump with price update
    if parsed["forum_url"]:
        watchers = await db_get_item_watchers(parsed["forum_url"])
        for watcher in watchers:
            uid = watcher["user_id"]
            old_price = watcher["last_price"]
            new_price = price_str
            # Only DM if price changed or bump keywords found
            price_changed = new_price and old_price and new_price != old_price
            has_offer = any(k in parsed.get("msg_body", "").lower() for k in ["make offer", "price reduced", "reduced"])
            if price_changed or has_offer:
                try:
                    user = await client.fetch_user(int(uid))
                    dm_embed = discord.Embed(
                        title=f"🔔 Update: {parsed['item_title']}",
                        color=discord.Color.dark_gold(),
                        timestamp=datetime.now(timezone.utc)
                    )
                    if price_changed:
                        dm_embed.add_field(name="Price Update", value=f"~~{old_price}~~ → **{new_price}**", inline=False)
                    if has_offer:
                        dm_embed.add_field(name="Note", value="Seller may accept offers!", inline=False)
                    if parsed["forum_url"]:
                        dm_embed.add_field(name="Listing", value=f"[View on WAF]({parsed['forum_url']})", inline=False)
                    dm_embed.set_footer(text="WAF Watchlist — The Relic Registry")
                    await user.send(embed=dm_embed)
                    await db_update_watch_price(uid, parsed["forum_url"], new_price)
                except Exception as e:
                    logger.error(f"[Watchlist] Failed to DM watcher {uid}: {e}")

async def check_email_dealers():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    if not channel:
        return
    logger.info(f"Email checker ready! Checking every {EMAIL_CHECK_INTERVAL} seconds.")
    while not client.is_closed():
        if bot_state["paused"]:
            await asyncio.sleep(30)
            continue
        bot_state["last_email_check"] = datetime.now(timezone.utc)
        triggered = await check_gmail_async()
        for dealer, subject, body in triggered:
            await db_increment_stat(dealer["name"])
            is_waf = dealer.get("waf", False)
            if is_waf:
                try:
                    parsed = parse_waf_email(subject, body)
                    guild = client.guilds[0] if client.guilds else None
                    waf_channel = client.get_channel(WAF_CHANNEL_ID)
                    await send_waf_alert(waf_channel, parsed, guild)
                except Exception as e:
                    logger.error(f"[WAF] Error processing email '{subject}': {e}\n{traceback.format_exc()}")
            else:
                logo_file = os.path.join(SCRIPT_DIR, "logos", dealer["logo_file"])
                await send_alert(channel, dealer["name"], dealer["url"], logo_file)
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

# ==================== WAF WATCH ITEM BUTTONS ====================

class WatchItemView(discord.ui.View):
    def __init__(self, forum_url, item_title, price=""):
        super().__init__(timeout=None)
        self.forum_url = forum_url
        self.item_title = item_title
        self.price = price

    @discord.ui.button(label="Watch Item", emoji="🔔", style=discord.ButtonStyle.secondary)
    async def watch(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        if await db_is_watching(user_id, self.forum_url):
            await interaction.response.send_message(f"⚠️ You are already watching **{self.item_title}**!", ephemeral=True)
            return
        await db_watch_item(user_id, self.forum_url, self.item_title, self.price)
        await interaction.response.send_message(f"🔔 You are now watching **{self.item_title}**! You will be notified of any price changes or updates.", ephemeral=True)

    @discord.ui.button(label="Unwatch", emoji="🔕", style=discord.ButtonStyle.secondary)
    async def unwatch(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        if not await db_is_watching(user_id, self.forum_url):
            await interaction.response.send_message(f"⚠️ You are not watching **{self.item_title}**.", ephemeral=True)
            return
        await db_unwatch_item(user_id, self.forum_url)
        await interaction.response.send_message(f"🔕 You have stopped watching **{self.item_title}**.", ephemeral=True)

    @discord.ui.button(label="Send to DM", emoji="📬", style=discord.ButtonStyle.secondary)
    async def send_to_dm(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            price_line = f"\n💰 **{self.price}**" if self.price else ""
            dm_embed = discord.Embed(
                title=f"📌 Bookmarked: {self.item_title}",
                description=f"You saved this WAF listing for later.{price_line}\n\n[**View Listing →**]({self.forum_url})",
                color=discord.Color.dark_gold(),
                timestamp=datetime.now(timezone.utc)
            )
            dm_embed.set_footer(text="WAF Bookmark — The Relic Registry")
            await interaction.user.send(embed=dm_embed)
            await interaction.response.send_message(f"📬 **{self.item_title}** has been sent to your DMs!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("⚠️ I couldn't DM you — please enable DMs from server members in your privacy settings.", ephemeral=True)
        except Exception as e:
            logger.error(f"[WAF] DM bookmark failed: {e}")
            await interaction.response.send_message("⚠️ Something went wrong sending the DM.", ephemeral=True)

# ==================== FOLLOW DEALER BUTTONS ====================

class FollowDealerView(discord.ui.View):
    def __init__(self, dealer_name):
        super().__init__(timeout=None)
        self.dealer_name = dealer_name

    @discord.ui.button(label="Follow Dealer", emoji="🔔", style=discord.ButtonStyle.secondary)
    async def follow(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        if await db_is_following(user_id, self.dealer_name):
            await interaction.response.send_message(f"⚠️ You are already following **{self.dealer_name}**!", ephemeral=True)
            return
        await db_follow_dealer(user_id, self.dealer_name)
        await interaction.response.send_message(f"🔔 You are now following **{self.dealer_name}**! You'll receive a DM whenever they have new items.", ephemeral=True)

    @discord.ui.button(label="Unfollow Dealer", emoji="🔕", style=discord.ButtonStyle.secondary)
    async def unfollow(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        if not await db_is_following(user_id, self.dealer_name):
            await interaction.response.send_message(f"⚠️ You are not following **{self.dealer_name}**.", ephemeral=True)
            return
        await db_unfollow_dealer(user_id, self.dealer_name)
        await interaction.response.send_message(f"🔕 You have unfollowed **{self.dealer_name}**.", ephemeral=True)

# ==================== REVIEW MODERATION BUTTONS ====================

class ReviewModerationView(discord.ui.View):
    def __init__(self, review_id, user_id, username, dealer_name):
        super().__init__(timeout=None)
        self.review_id = review_id
        self.user_id = user_id
        self.username = username
        self.dealer_name = dealer_name

    @discord.ui.button(label="Approve", emoji="✅", style=discord.ButtonStyle.success)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_mod(interaction.user):
            await interaction.response.send_message("🚫 You need Moderator permissions.", ephemeral=True)
            return
        await db_approve_review(self.review_id)
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.green()
        embed.title = embed.title.replace("📝 Pending", "✅ Approved")
        embed.set_footer(text=f"Approved by {interaction.user} | Review ID: {self.review_id}")
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(embed=embed, view=self)
        await interaction.response.send_message(f"✅ Review approved for **{self.dealer_name}**!", ephemeral=True)

    @discord.ui.button(label="Decline", emoji="❌", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_mod(interaction.user):
            await interaction.response.send_message("🚫 You need Moderator permissions.", ephemeral=True)
            return
        await db_decline_review(self.review_id)
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.red()
        embed.title = embed.title.replace("📝 Pending", "❌ Declined")
        embed.set_footer(text=f"Declined by {interaction.user} | Review ID: {self.review_id}")
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(embed=embed, view=self)
        await interaction.response.send_message(f"❌ Review declined for **{self.dealer_name}**.", ephemeral=True)

    @discord.ui.button(label="Warn", emoji="⚠️", style=discord.ButtonStyle.secondary)
    async def warn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_mod(interaction.user):
            await interaction.response.send_message("🚫 You need Moderator permissions.", ephemeral=True)
            return
        modal = WarnModal(self.user_id, self.username)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Block", emoji="🚫", style=discord.ButtonStyle.danger)
    async def block(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_mod(interaction.user):
            await interaction.response.send_message("🚫 You need Moderator permissions.", ephemeral=True)
            return
        modal = BlockModal(self.user_id, self.username)
        await interaction.response.send_modal(modal)

class WarnModal(discord.ui.Modal, title="Warn Reviewer"):
    reason = discord.ui.TextInput(
        label="Warning Message",
        placeholder="Enter the warning message to send to the user...",
        style=discord.TextStyle.paragraph,
        max_length=500
    )

    def __init__(self, user_id, username):
        super().__init__()
        self.user_id = user_id
        self.username = username

    async def on_submit(self, interaction: discord.Interaction):
        await db_add_reviewer_warning(self.user_id, self.username, str(self.reason))
        # Try to DM the user
        try:
            user = await interaction.client.fetch_user(int(self.user_id))
            if user:
                dm_embed = discord.Embed(
                    title="⚠️ Review Warning",
                    description=f"You have received a warning from **{interaction.guild.name}** regarding a review you submitted:\n\n{self.reason}",
                    color=discord.Color.orange(),
                    timestamp=datetime.now(timezone.utc)
                )
                await user.send(embed=dm_embed)
                await interaction.response.send_message(f"⚠️ Warning sent to **{self.username}** via DM!", ephemeral=True)
        except:
            await interaction.response.send_message(f"⚠️ Warning logged but could not DM **{self.username}** (DMs may be disabled).", ephemeral=True)

class BlockModal(discord.ui.Modal, title="Block Reviewer"):
    reason = discord.ui.TextInput(
        label="Reason for blocking",
        placeholder="Enter the reason for blocking this user...",
        style=discord.TextStyle.paragraph,
        max_length=500
    )

    def __init__(self, user_id, username):
        super().__init__()
        self.user_id = user_id
        self.username = username

    async def on_submit(self, interaction: discord.Interaction):
        await db_block_reviewer(self.user_id, self.username, str(self.reason))
        await interaction.response.send_message(f"🚫 **{self.username}** has been blocked from leaving reviews.", ephemeral=True)

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
    embed.add_field(name="/following", value="See dealers you are following", inline=True)
    embed.add_field(name="/myroles", value="Your WAF subscriptions", inline=True)
    embed.add_field(name="🔒 Mod Commands", value="​", inline=False)
    embed.add_field(name="/rescan & /pause & /resume", value="Force check / Pause / Resume", inline=True)
    embed.add_field(name="/stats & /test", value="Alert stats / Test notifications", inline=True)
    embed.add_field(name="/promo & /pausepromo & /resumepromo", value="Send/pause/resume promo", inline=True)
    embed.add_field(name="/adddealer & /approvedealer", value="Add/approve a dealer", inline=True)
    embed.add_field(name="/warningdealer & /removewarning", value="Add/remove warning", inline=True)
    embed.add_field(name="/blockreviewer & /unblockreviewer", value="Block/unblock reviewer", inline=True)
    embed.add_field(name="/reviewerstats", value="View reviewer stats", inline=True)
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

    dealer_reviews = await db_get_reviews(dealer["name"])
    rating, count = get_dealer_rating_sync(dealer_reviews)
    warning = await db_get_warning(dealer["name"])

    logo_file = os.path.join(SCRIPT_DIR, "logos", dealer["logo_file"])

    color = discord.Color.red() if warning else discord.Color.dark_gold()
    flag = dealer.get("flag", "🌐")
    embed = discord.Embed(title=f"{flag} {dealer['name']}", color=color, timestamp=datetime.now(timezone.utc))

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

    follow_view = FollowDealerView(dealer["name"])
    if file:
        await interaction.response.send_message(file=file, embed=embed, view=follow_view, ephemeral=True)
    else:
        await interaction.response.send_message(embed=embed, view=follow_view, ephemeral=True)

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
    # Defer immediately to avoid Discord timeout
    await interaction.response.defer(ephemeral=True)
    # Fix review being string "None"
    if review == "None" or review == "":
        review = None
    logger.info(f"[ratedealer] Called by {interaction.user} for dealer='{dealer_name}' rating={rating} review='{review}'")

    dealer = find_dealer(dealer_name)
    if not dealer:
        await interaction.followup.send(f"⚠️ Dealer '{dealer_name}' not found. Use `/dealers` to see all dealers.", ephemeral=True)
        return

    user_id = str(interaction.user.id)

    # Check if user is blocked
    if await db_is_blocked(user_id):
        await interaction.followup.send("🚫 You have been restricted from leaving reviews on **The Relic Registry**. If you believe this is an error please contact a moderator at http://discord.gg/therelicregistry", ephemeral=True)
        return

    today = datetime.now(timezone.utc).date().isoformat()
    dealer_reviews = await db_get_reviews(dealer["name"], status='all')
    already_today = any(str(r.get("user_id")) == user_id and r.get("date") == today for r in dealer_reviews)

    if already_today:
        await interaction.followup.send(f"⚠️ You've already reviewed **{dealer['name']}** today. Come back tomorrow!", ephemeral=True)
        return

    ts = int(datetime.now(timezone.utc).timestamp())
    stars = "⭐" * rating

    await interaction.followup.send(f"✅ Thanks for rating **{dealer['name']}** {stars}! Your review has been submitted.", ephemeral=True)

    # Do database work after responding
    review_id = await db_add_review(dealer["name"], user_id, str(interaction.user), rating, review, today, ts)

    # Check for Trusted Reviewer role
    try:
        async with client.db.acquire() as conn:
            total_user_reviews = await conn.fetchval("SELECT COUNT(*) FROM reviews WHERE user_id=$1 AND status='approved'", user_id)
        if total_user_reviews >= TRUSTED_REVIEWER_THRESHOLD:
            trusted_role = interaction.guild.get_role(TRUSTED_REVIEWER_ROLE_ID)
            if trusted_role and trusted_role not in interaction.user.roles:
                await interaction.user.add_roles(trusted_role)
                await interaction.followup.send(f"🎖️ Congratulations! You've earned the **@Trusted Reviewer** role!", ephemeral=True)
    except Exception as e:
        logger.error(f"Trusted reviewer check error: {e}")

    # Log to review-log channel with buttons
    try:
        log_channel = client.get_channel(REVIEW_LOG_CHANNEL_ID)
        if log_channel:
            stats = await db_get_reviewer_stats(user_id)
            account_created = interaction.user.created_at
            account_age = (datetime.now(timezone.utc) - account_created).days
            years = account_age // 365
            months = (account_age % 365) // 30
            age_str = f"{years}y {months}m" if years > 0 else f"{months}m"

            log_embed = discord.Embed(
                title=f"📝 Pending Review — {dealer['name']}",
                color=discord.Color.orange(),
                timestamp=datetime.now(timezone.utc)
            )
            log_embed.add_field(name="Member", value=f"{interaction.user.mention} ({interaction.user})", inline=True)
            log_embed.add_field(name="Rating", value=stars, inline=True)
            log_embed.add_field(name="Account Age", value=age_str, inline=True)
            log_embed.add_field(name="Server", value=interaction.guild.name if interaction.guild else "DM", inline=True)
            reviews_val = f"✅ {stats['approved']} approved | ❌ {stats['declined']} declined | ⏳ {stats['pending']} pending"
            log_embed.add_field(name="Reviews", value=reviews_val, inline=True)
            log_embed.add_field(name="Warnings", value=f"⚠️ {stats['warnings']} warning(s)", inline=True)
            if review:
                log_embed.add_field(name="Full Review", value=review[:500], inline=False)
            log_embed.set_footer(text=f"Review ID: {review_id} | Use buttons to moderate")

            view = ReviewModerationView(review_id, user_id, str(interaction.user), dealer["name"])
            await log_channel.send(embed=log_embed, view=view)
    except Exception as e:
        logger.error(f"Review log error: {e}\n{traceback.format_exc()}")

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
    all_reviews = await db_get_all_reviews(status="approved")

    # Top dealers by rating (min 3 reviews)
    dealer_ratings = []
    for dealer in get_all_dealers():
        dealer_reviews = all_reviews.get(dealer["name"], [])
        rating, count = get_dealer_rating_sync(dealer_reviews)
        if rating and count >= 3:
            dealer_ratings.append((dealer["name"], rating, count))
    dealer_ratings.sort(key=lambda x: (x[1], x[2]), reverse=True)
    top_dealers = dealer_ratings[:10]

    # Top reviewers
    reviewer_counts = {}
    reviewer_names = {}
    for dealer_reviews in all_reviews.values():
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
    stats = await db_get_all_stats()
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
    await db_set_warning(dealer["name"], reason)
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
    warning = await db_get_warning(dealer["name"])
    if warning:
        await db_remove_warning(dealer["name"])
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
    dealer_reviews = await db_get_reviews(dealer["name"])
    if not dealer_reviews:
        await interaction.response.send_message(f"⚠️ No reviews found for **{dealer['name']}**.", ephemeral=True)
        return
    idx = len(dealer_reviews) - review_index
    if idx < 0 or idx >= len(dealer_reviews):
        await interaction.response.send_message(f"⚠️ Review #{review_index} not found.", ephemeral=True)
        return
    removed = dealer_reviews[idx]
    await db_delete_review(removed["id"])
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

@client.tree.command(name="reviewerstats", description="🔒 Shows review stats for a specific member")
@app_commands.describe(member="The member to look up")
async def reviewerstats_cmd(interaction: discord.Interaction, member: discord.Member):
    if not is_mod(interaction.user):
        await interaction.response.send_message("🚫 You need Moderator permissions.", ephemeral=True)
        return
    stats = await db_get_reviewer_stats(str(member.id))
    account_age = (datetime.now(timezone.utc) - member.created_at).days
    years = account_age // 365
    months = (account_age % 365) // 30
    age_str = f"{years}y {months}m" if years > 0 else f"{months}m"
    embed = discord.Embed(
        title=f"📊 Reviewer Stats — {member}",
        color=discord.Color.red() if stats["blocked"] else discord.Color.dark_gold(),
        timestamp=datetime.now(timezone.utc)
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="Account Age", value=age_str, inline=True)
    embed.add_field(name="Status", value="🚫 Blocked" if stats["blocked"] else "✅ Active", inline=True)
    embed.add_field(name="Total Reviews", value=str(stats["total"]), inline=True)
    embed.add_field(name="✅ Approved", value=str(stats["approved"]), inline=True)
    embed.add_field(name="❌ Declined", value=str(stats["declined"]), inline=True)
    embed.add_field(name="⏳ Pending", value=str(stats["pending"]), inline=True)
    embed.add_field(name="⚠️ Warnings", value=str(stats["warnings"]), inline=True)
    embed.set_footer(text="The Relic Registry — Dealer Update")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@client.tree.command(name="blockreviewer", description="🔒 Block a member from leaving reviews")
@app_commands.describe(member="The member to block", reason="Reason for blocking")
async def blockreviewer_cmd(interaction: discord.Interaction, member: discord.Member, reason: str):
    if not is_mod(interaction.user):
        await interaction.response.send_message("🚫 You need Moderator permissions.", ephemeral=True)
        return
    await db_block_reviewer(str(member.id), str(member), reason)
    await interaction.response.send_message(f"🚫 **{member}** has been blocked from leaving reviews.", ephemeral=True)

@client.tree.command(name="unblockreviewer", description="🔒 Unblock a member from leaving reviews")
@app_commands.describe(member="The member to unblock")
async def unblockreviewer_cmd(interaction: discord.Interaction, member: discord.Member):
    if not is_mod(interaction.user):
        await interaction.response.send_message("🚫 You need Moderator permissions.", ephemeral=True)
        return
    await db_unblock_reviewer(str(member.id))
    await interaction.response.send_message(f"✅ **{member}** has been unblocked and can leave reviews again.", ephemeral=True)

@client.tree.command(name="following", description="Shows all dealers you are currently following")
async def following_cmd(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    follows = await db_get_follows(str(interaction.user.id))
    if not follows:
        await interaction.followup.send("🔕 You are not following any dealers yet. Use the 🔔 button on a dealer notification or `/dealerprofile` to follow a dealer!", ephemeral=True)
        return
    embed = discord.Embed(
        title="🔔 Your Followed Dealers",
        color=discord.Color.dark_gold(),
        timestamp=datetime.now(timezone.utc)
    )
    for dealer_name in follows:
        dealer = find_dealer(dealer_name)
        flag = dealer.get("flag", "🌐") if dealer else "🌐"
        url = dealer.get("url", "") if dealer else ""
        embed.add_field(name=f"{flag} {dealer_name}", value=f"[Visit Site]({url})" if url else "No URL", inline=True)
    embed.set_footer(text="The Relic Registry — Dealer Update")
    await interaction.followup.send(embed=embed, ephemeral=True)

@client.tree.command(name="mywatchlist", description="Shows all WAF items you are watching")
async def mywatchlist_cmd(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    watchlist = await db_get_watchlist(str(interaction.user.id))
    if not watchlist:
        await interaction.followup.send("🔕 You are not watching any WAF items. Click the 🔔 **Watch Item** button on any WAF alert to start!", ephemeral=True)
        return
    embed = discord.Embed(
        title="🔔 Your WAF Watchlist",
        color=discord.Color.dark_gold(),
        timestamp=datetime.now(timezone.utc)
    )
    for item in watchlist[:25]:
        added = datetime.fromtimestamp(item["date_added"], tz=timezone.utc).strftime("%b %d, %Y")
        price_info = f" — {item['last_price']}" if item["last_price"] else ""
        url_text = f"[View Listing]({item['forum_url']})" if item["forum_url"] else "No link"
        embed.add_field(
            name=item["item_title"][:50],
            value=f"{url_text}{price_info}\nAdded: {added}",
            inline=False
        )
    embed.set_footer(text="Watchlist entries expire after 90 days — The Relic Registry")
    await interaction.followup.send(embed=embed, ephemeral=True)

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
async def on_error(event, *args, **kwargs):
    logger.error(f"Discord error in event '{event}': {traceback.format_exc()}")

@client.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    logger.error(f"Slash command error in '{interaction.command.name if interaction.command else 'unknown'}': {error}")
    logger.error(traceback.format_exc())
    try:
        if not interaction.response.is_done():
            await interaction.response.send_message(f"⚠️ An error occurred. Please try again or contact a mod.", ephemeral=True)
        else:
            await interaction.followup.send(f"⚠️ An error occurred. Please try again or contact a mod.", ephemeral=True)
    except:
        pass

@client.event
async def on_ready():
    logger.info(f"Logged in as {client.user}")
    logger.info(f"SCRIPT_DIR: {SCRIPT_DIR}")
    logos_path = os.path.join(SCRIPT_DIR, "logos")
    if os.path.exists(logos_path):
        logger.info(f"Logos found: {os.listdir(logos_path)}")
    else:
        logger.warning(f"Logos folder NOT found at {logos_path}!")

async def send_griffin_combined():
    """Sends a combined Griffin Militaria alert after 5 minute buffer."""
    await asyncio.sleep(300)  # Wait 5 minutes to collect all changes
    if not bot_state["griffin_buffer"]:
        return
    channel = client.get_channel(CHANNEL_ID)
    if not channel:
        return

    pages = bot_state["griffin_buffer"].copy()
    bot_state["griffin_buffer"] = []
    bot_state["griffin_timer"] = None

    logo_file = os.path.join(SCRIPT_DIR, "logos", "Griffin_Militaria.png")
    warning = await db_get_warning("Griffin Militaria")

    description = "New items have been found on the following Griffin Militaria pages:\n\n"
    for page_name, page_url in pages:
        description += f"• [**{page_name}**]({page_url})\n"

    if warning:
        description = f"⚠️ **WARNING: {warning}**\n\n" + description

    color = discord.Color.red() if warning else discord.Color.dark_gold()
    embed = discord.Embed(
        title="🆕 🇺🇸 New Items at Griffin Militaria!",
        description=description,
        color=color,
        timestamp=datetime.now(timezone.utc)
    )

    rating, review_count = await get_dealer_rating("Griffin Militaria")
    embed.add_field(name="Rating", value=stars_display(rating), inline=True)
    embed.add_field(name="Total Reviews", value=f"📝 {review_count}", inline=True)
    embed.set_footer(text="The Relic Registry — Dealer Update")

    file = None
    if os.path.exists(logo_file):
        file = discord.File(logo_file, filename="logo.png")
        embed.set_thumbnail(url="attachment://logo.png")

    try:
        if file:
            await channel.send(file=file, embed=embed, view=FollowDealerView("Griffin Militaria"))
        else:
            await channel.send(embed=embed, view=FollowDealerView("Griffin Militaria"))
        await db_increment_stat("Griffin Militaria")
        logger.info(f"[Griffin] Combined alert sent for {len(pages)} pages!")
    except Exception as e:
        logger.error(f"[Griffin] Failed to send combined alert: {e}")

    # DM followers
    try:
        followers = await db_get_dealer_followers("Griffin Militaria")
        for follower_id in followers:
            try:
                user = await client.fetch_user(int(follower_id))
                if user:
                    dm_embed = discord.Embed(
                        title="🆕 🇺🇸 New Items at Griffin Militaria!",
                        description=description,
                        color=discord.Color.dark_gold(),
                        timestamp=datetime.now(timezone.utc)
                    )
                    dm_embed.set_footer(text="You are following Griffin Militaria — The Relic Registry")
                    if os.path.exists(logo_file):
                        dm_file = discord.File(logo_file, filename="logo.png")
                        dm_embed.set_thumbnail(url="attachment://logo.png")
                        await user.send(file=dm_file, embed=dm_embed)
                    else:
                        await user.send(embed=dm_embed)
            except Exception as e:
                logger.error(f"[Griffin] Failed to DM follower {follower_id}: {e}")
    except Exception as e:
        logger.error(f"[Griffin] Failed to send DMs to followers: {e}")

async def handle_webhook(request):
    """Receives webhook from Changedetection.io when a page changes."""
    try:
        from urllib.parse import unquote
        dealer_name = request.query.get("dealer", "")
        page_name = request.query.get("page", "")
        page_url = unquote(request.query.get("url", ""))

        # Also try to get URL from request body or title header
        if not page_url or "%7B" in page_url:
            try:
                # Check title header (Changedetection.io sends watch_url there)
                title = request.headers.get("Title", "") or request.headers.get("X-Title", "")
                if title and title.startswith("http"):
                    page_url = title.strip()
                    logger.info(f"[Webhook] Got URL from title header: {page_url}")
                else:
                    # Try request body
                    body = await request.text()
                    if body:
                        # Extract first URL from body
                        import re
                        urls = re.findall(r'https?://[^\s<>"]+', body)
                        if urls:
                            page_url = urls[0].strip()
                            logger.info(f"[Webhook] Got URL from body: {page_url}")
            except Exception as e:
                logger.error(f"[Webhook] Error extracting URL: {e}")

        if not dealer_name:
            return web.Response(text="Missing dealer parameter", status=400)

        logger.info(f"[Webhook] Change detected for: {dealer_name} — {page_name}")

        # Special handling for Griffin Militaria — buffer changes
        if dealer_name == "Griffin Militaria":
            # Get title from request headers (Changedetection.io sends watch title there)
            watch_title = request.headers.get("Title", "") or request.headers.get("X-Title", "")
            # Look up the URL from the title if we don't have it
            if not page_url or "griffinmilitaria.com/" == page_url or "%7B" in page_url:
                page_url = lookup_griffin_url(watch_title)
                logger.info(f"[Griffin] Looked up URL from title '{watch_title}': {page_url}")
            # Extract readable name from URL path
            if page_url and page_url != "https://griffinmilitaria.com/":
                path_parts = page_url.rstrip("/").split("/")
                url_name = path_parts[-1].replace("-", " ").replace("_", " ").title()
                # Clean up common prefixes
                for prefix in ["Us Wwii ", "Us Wwi ", "Germany Wwii ", "Germany Wwi ", "Japanese ", "Vietnam War "]:
                    url_name = url_name.replace(prefix, "")
                display_name = url_name
            else:
                display_name = watch_title.replace(" – Griffin Militaria", "").replace(" - Griffin Militaria", "").strip() or page_name or "New Items"
            bot_state["griffin_buffer"].append((display_name, page_url))
            if bot_state["griffin_timer"] is None:
                bot_state["griffin_timer"] = asyncio.create_task(send_griffin_combined())
                print(f"[Griffin] Buffer started — waiting 5 minutes for more changes...")
            return web.Response(text="OK", status=200)

        dealer = find_dealer(dealer_name)
        if not dealer:
            logger.warning(f"[Webhook] Unknown dealer: {dealer_name}")
            return web.Response(text="Unknown dealer", status=404)

        channel = client.get_channel(CHANNEL_ID)
        if channel:
            # Use specific page URL if provided, otherwise use dealer default
            alert_url = page_url if page_url else dealer["url"]
            logo_file = os.path.join(SCRIPT_DIR, "logos", dealer["logo_file"])
            await db_increment_stat(dealer_name)

            warning = await db_get_warning(dealer["name"])
            dealer_reviews = await db_get_reviews(dealer["name"])
            rating, review_count = get_dealer_rating_sync(dealer_reviews)

            color = discord.Color.red() if warning else discord.Color.dark_gold()
            desc = f"New items have been added to [{dealer['name']}]({alert_url})\n\n[**Click here to view new items \u2192**]({alert_url})"
            if warning:
                desc = f"⚠️ **WARNING: {warning}**\n\n" + desc

            dealer_flag = dealer.get("flag", "🌐")
            embed = discord.Embed(title=f"🆕 {dealer_flag} New Items at {dealer['name']}!", description=desc, color=color, timestamp=datetime.now(timezone.utc))
            embed.add_field(name="Rating", value=stars_display(rating), inline=True)
            embed.add_field(name="Total Reviews", value=f"📝 {review_count}", inline=True)
            embed.set_footer(text="The Relic Registry — Dealer Update")

            file = None
            if os.path.exists(logo_file):
                file = discord.File(logo_file, filename="logo.png")
                embed.set_thumbnail(url="attachment://logo.png")

            if file:
                await channel.send(file=file, embed=embed)
            else:
                await channel.send(embed=embed)
            logger.info(f"[Webhook] Alert sent for {dealer_name}!")

        return web.Response(text="OK", status=200)
    except Exception as e:
        logger.error(f"[Webhook] Error: {e}\n{traceback.format_exc()}")
        return web.Response(text=str(e), status=500)

async def handle_guide(request):
    guide_path = os.path.join(SCRIPT_DIR, "guide.html")
    if os.path.exists(guide_path):
        with open(guide_path, "r") as f:
            return web.Response(text=f.read(), content_type="text/html")
    return web.Response(text="Guide not found", status=404)

async def start_web_server():
    await client.wait_until_ready()
    app = web.Application()
    app.router.add_get("/", handle_guide)
    app.router.add_get("/guide", handle_guide)
    app.router.add_get("/alert", handle_webhook)
    app.router.add_post("/alert", handle_webhook)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    logger.info("Webhook server running on port 8080!")

async def daily_cleanup():
    await client.wait_until_ready()
    while not client.is_closed():
        await asyncio.sleep(24 * 3600)
        await db_cleanup_watchlist()

async def main():
    async with client:
        client.loop.create_task(check_all_dealers())
        client.loop.create_task(check_email_dealers())
        client.loop.create_task(send_promo())
        client.loop.create_task(start_web_server())
        client.loop.create_task(daily_cleanup())
        await client.start(BOT_TOKEN)

asyncio.run(main())
