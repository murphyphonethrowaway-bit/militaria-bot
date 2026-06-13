import discord
from discord import app_commands
import asyncpg
from aiohttp import web
import logging
import traceback
import psutil

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
# Keep discord and aiohttp at INFO to avoid spam
logger = logging.getLogger("MilitariaBot")
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
BOT_OWNER_ID = 161988117862023169  # Murphy's Discord user ID
GUILD_ID = 1357352905857826887  # Main server
TEST_GUILD_ID = 1513233559878369422  # Test server
OWNER_GUILD_ID = 1357352905857826887  # Owner commands go here (main server)
IMAGE_HOST_CHANNEL_ID = 1513273241043599530  # #image-host — test server
CHANNEL_ID = 1513271593273655387  # #adrian — test server
WAF_CHANNEL_ID = 1513271593273655387  # #adrian — test server
WAF_ROLE_ID = 1511101033349124318
DEALER_SUGGEST_CHANNEL_ID = 1511487755266556034  # #dealer-reviews channel
REVIEW_LOG_CHANNEL_ID = 1513271782436639011  # #review-log — test server
BOT_FEEDBACK_CHANNEL_ID = 1513271765982511126  # #bot-feedback — test server
GUERRILLA_WARFARE_ROLE_ID = 1513272208045244598  # Guerrilla Warfare — test server
ADRIAN_VERIFIED_ROLE_ID = 1513272151912747100  # Adrian Verified — test server
ADRIAN_UPDATES_CHANNEL_ID = 1513271624172834836  # #adrian-updates — test server
PRIVATE_LOG_CHANNEL_ID = 1513271737167380541  # #mod-log — test server
ESTATE_CHANNEL_ID = 1513273443087417614  # #estate-listings — test server
ESTATE_SOLD_TAG_ID = 1513274158128173146  # Sold tag — test server
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
    {"name": "Weitze Militaria", "flag": "🇩🇪", "region": "EU", "url": "https://www.weitze.com/neuheiten.html", "logo_file": "weitze.png", "item_selector": "a[href*='/militaria/']", "base_url": "https://www.weitze.com", "eras": [1, 2, 3, 6], "countries": ['D']},
    {"name": "Linda Mae Militaria", "flag": "🇺🇸", "region": "NA", "url": "https://lindamaemilitaria.com/", "logo_file": "lindamae.png", "item_selector": ".product a", "base_url": "https://lindamaemilitaria.com", "eras": [3], "countries": ['A', 'D', 'G']},
]

EMAIL_DEALERS = [
    {"name": "The Ruptured Duck", "flag": "🇺🇸", "region": "NA", "match": ["therupturedduck.com", "ruptured duck"], "logo_file": "ruptured_duck.png", "url": "https://www.therupturedduck.com/collections/recently-added-items", "eras": [2, 3], "countries": ['A', 'D']},
    {"name": "War's End Shop", "flag": "🇺🇸", "region": "NA", "match": ["warsendshop.com", "war's end", "wars end"], "logo_file": "warsend.png", "url": "https://www.warsendshop.com/collections/new-items", "eras": [0], "countries": ['D']},
    {"name": "Lakeside Trader", "flag": "🇺🇸", "region": "NA", "match": ["lakesidetrader.com", "lakeside trader"], "logo_file": "lakeside.png", "url": "https://www.lakesidetrader.com/recently-added-items/", "eras": [0], "countries": ['Z']},
    {"name": "Dutch Militaria", "flag": "🇳🇱", "region": "EU", "match": ["dutchmilitaria.com", "dutch militaria"], "logo_file": "dutch_militaria.png", "url": "https://dutchmilitaria.com/", "eras": [2, 3], "countries": ['D']},
    {"name": "Militaria Sales", "flag": "🇺🇸", "region": "NA", "match": ["militariasales.com", "militaria sales"], "logo_file": "militaria_sales.png", "url": "https://www.militariasales.com/new-item/", "eras": [2, 3, 6], "countries": ['A', 'D', 'J', 'G']},
    {"name": "Military Collectibles", "flag": "🇺🇸", "region": "NA", "match": ["militarycollectibles.com", "military collectibles"], "logo_file": "military_collectibles.png", "url": "https://militarycollectibles.com/shop?s=n", "eras": [2, 3], "countries": ['D']},
    {"name": "Military Collectors HQ", "flag": "🇺🇸", "region": "NA", "match": ["militarycollectorshq.com", "military collectors hq"], "logo_file": "militarycollectorshq.png", "url": "https://militarycollectorshq.com/store-catalog", "eras": [0], "countries": ['Z']},
    {"name": "Soviet Orders", "flag": "🇺🇸", "region": "NA", "match": ["sovietorders.com", "soviet orders"], "logo_file": "Soviet_Orders.png", "url": "https://sovietorders.com/new-in-store/", "eras": [2, 3], "countries": ['E']},
    {"name": "Empire's Past", "flag": "🇺🇸", "region": "NA", "match": ["empirespast.com", "empire's past", "empires past"], "logo_file": "Empire_past.png", "url": "https://empirespast.com/newly-listed/", "eras": [2, 3], "countries": ['D', 'J']},
    {"name": "1944 Militaria", "flag": "🇺🇸", "region": "NA", "match": ["1944militaria.com", "1944 militaria"], "logo_file": "1944militaria.png", "url": "https://www.1944militaria.com/New_Original_Items_s/1900.htm", "eras": [2, 3], "countries": ['A', 'D', 'J']},
    {"name": "International Military Antiques", "flag": "🇺🇸", "region": "NA", "match": ["ima-usa.com", "international military antiques", "ima usa"], "logo_file": "ima.png", "url": "https://www.ima-usa.com/collections/new-arrivals", "eras": [0], "countries": ['Z']},
    {"name": "Wolfgang Historica", "flag": "🇩🇪", "region": "EU", "match": ["wolfganghistorica.com", "wolfgang historica"], "logo_file": "wolfgang_historica.png", "url": "https://wolfganghistorica.com/", "eras": [2, 3, 6], "countries": ['D', 'E', 'K', 'B']},
    {"name": "Enemy Militaria", "flag": "🇺🇸", "region": "NA", "match": ["enemymilitaria.com", "enemy militaria"], "logo_file": "Enemy_Militaria.png", "url": "https://enemymilitaria.com/", "eras": [2, 3, 4, 6, 7], "countries": ['A', 'D', 'J']},
    {"name": "Hiscoll Military Antiques", "flag": "🇬🇧", "region": "EU", "match": ["hiscoll.com", "hiscoll military antiques", "hiscoll"], "logo_file": "hiscoll.png", "url": "https://hiscoll.com/shop", "eras": [2, 3], "countries": ['D']},
    {"name": "Relics of the Reich", "flag": "🇺🇸", "region": "NA", "match": ["relicsofthereich.com", "relics of the reich"], "logo_file": "relicsofthereich.png", "url": "https://www.relicsofthereich.com/home", "eras": [3], "countries": ['D']},
    {"name": "Epic Artifacts", "flag": "🇺🇸", "region": "NA", "match": ["epicartifacts.com", "epic artifacts"], "logo_file": "Epic_artifacts.png", "url": "https://epicartifacts.com/newly-listed/", "eras": [2, 3], "countries": ['A', 'D', 'J']},
    {"name": "RG Militaria", "flag": "🇳🇱", "region": "EU", "match": ["rg-militaria.com", "rg militaria"], "logo_file": "rgmilitaria.png", "url": "https://www.rg-militaria.com/new-items-nieuwe-items", "eras": [3], "countries": ['D']},
    {"name": "Military Antiques Stockholm", "flag": "🇸🇪", "region": "EU", "match": ["military-antiques-stockholm.com", "military antiques stockholm"], "logo_file": "Military_Antiques_Stockholm.png", "url": "https://www.military-antiques-stockholm.com/shop/", "eras": [2, 3], "countries": ['A', 'B', 'D', 'J', 'E']},
    {"name": "Oorlogsspullen", "flag": "🇳🇱", "region": "EU", "match": ["oorlogsspullen.nl", "oorlogsspullen"], "logo_file": "Oorlogspullen.png", "url": "https://oorlogsspullen.nl/product-categorie/new/", "cooldown_hours": 6, "eras": [3, 6], "countries": ['D']},
    {"name": "Wittmann Antique Militaria", "flag": "🇩🇪", "region": "EU", "match": ["wwiidaggers.com", "wittmann antique militaria", "wittmann"], "logo_file": "wam.png", "url": "https://www.wwiidaggers.com/updates.htm", "eras": [3], "countries": ['D']},
    {"name": "RBNr Militaria", "flag": "🇩🇪", "region": "EU", "match": ["rbnr.it", "rbnr militaria", "rbnr"], "logo_file": "RBNR.png", "url": "https://en.rbnr.it/collections/all", "eras": [2, 3], "countries": ['D', 'H']},
    {"name": "Iraqi Militaria", "flag": "🇺🇸", "region": "NA", "match": ["iraqimilitaria.com", "iraqi militaria"], "logo_file": "iraqi_militaria.png", "url": "https://www.iraqimilitaria.com/", "eras": [6, 7], "countries": ['A', 'L']},
    {"name": "Danzig Militaria", "flag": "🇵🇱", "region": "EU", "match": ["danzigmilitaria.com", "danzig militaria"], "logo_file": "Danzig_Militaria.png", "url": "https://danzigmilitaria.com/shop/", "eras": [3], "countries": ['D']},
    {"name": "FJM44", "flag": "🇫🇷", "region": "EU", "match": ["fjm44.com", "fjm44", "fjm 44"], "logo_file": "fjm44.png", "url": "https://fjm44.com/product-category/militaria/", "eras": [3], "countries": ['A', 'D']},
    {"name": "Kurland", "flag": "🇩🇪", "region": "EU", "match": ["kurland-docs.com", "kurland"], "logo_file": "kurland.png", "url": "https://www.kurland-docs.com/shop.php", "eras": [3], "countries": ['D']},
    {"name": "Queen City Militaria", "flag": "🇺🇸", "region": "NA", "match": ["queencitymilitaria.com", "queen city militaria"], "logo_file": "queen_city_militaria.png", "url": "https://www.queencitymilitaria.com/", "eras": [2, 3, 6], "countries": ['A', 'E', 'D']},
    {"name": "Combat Relics", "flag": "🇺🇸", "region": "NA", "match": ["combat-relics.com", "combat relics"], "logo_file": "Combat_relics.png", "url": "https://www.combat-relics.com/", "eras": [2, 3], "countries": ['A', 'B', 'C', 'D']},
    {"name": "Tiger Militaria", "flag": "🇬🇧", "region": "EU", "match": ["tigermilitaria.com", "tiger militaria"], "logo_file": "TigerMilitaria.png", "url": "https://tigermilitaria.com/shop?showPerPage=24", "eras": [3], "countries": ['D']},
    {"name": "WAF Estate", "flag": "🇺🇸", "region": "NA", "match": ["wehrmacht-awards.com", "waf estate", "e-stand", "estand", "militaria e-stand"], "logo_file": "waf.png", "url": "https://www.wehrmacht-awards.com/forums/forum/the-militaria-e-stand", "waf": True},
    {"name": "Griffin Militaria", "flag": "🇺🇸", "region": "NA", "match": ["griffinmilitaria.com", "griffin militaria"], "logo_file": "Griffin_Militaria.png", "url": "https://griffinmilitaria.com/", "eras": [0], "countries": ['Z']},
    {"name": "EA Militaria", "flag": "🇳🇱", "region": "EU", "match": ["ea-militaria.com", "ea militaria"], "logo_file": "eamilitaria.png", "url": "https://www.ea-militaria.com/new-items?hideSold=1", "eras": [3], "countries": ['D']},
    {"name": "Militaria Plaza", "flag": "🇳🇱", "region": "EU", "match": ["militariaplaza.nl", "militaria plaza"], "logo_file": "Militaria_Plaza.png", "url": "https://militariaplaza.nl/new", "eras": [2, 3], "countries": ['A', 'B', 'C', 'E', 'D']},
    {"name": "The Collector's Guild", "flag": "🇺🇸", "region": "NA", "match": ["germanmilitaria.com", "collector's guild", "collectors guild"], "logo_file": "germanmilitaria.png", "url": "https://www.germanmilitaria.com/Advanced.html", "eras": [0], "countries": ['Z']},
    {"name": "General Assault Militaria", "flag": "🇺🇸", "region": "NA", "match": ["generalassaultmilitaria.com", "general assault militaria", "gam"], "logo_file": "gam.png", "url": "https://www.generalassaultmilitaria.com/", "eras": [3], "countries": ['D']},
    {"name": "Bevo Militaria", "flag": "🇩🇪", "region": "EU", "match": ["bevo-militaria.com", "bevo militaria"], "logo_file": "Bevo_Militaria.png", "url": "https://bevo-militaria.com/shop/", "eras": [2, 3], "countries": ['D']},
    {"name": "The Canadian Soldier", "flag": "🇨🇦", "region": "NA", "match": ["thecanadiansoldier.com", "canadian soldier"], "logo_file": "the_canadian_soldier.png", "url": "https://thecanadiansoldier.com/en-us/collections/newly-listed", "eras": [0], "countries": ['C']},
    {"name": "Wehrmacht Militaria", "flag": "🇺🇸", "region": "NA", "match": ["wehrmacht-militaria.com", "Wehrmacht militaria"], "logo_file": "Wehrmacht_Militaria.png", "url": "https://wehrmacht-militaria.com/shop", "eras": [2, 3], "countries": ['A', 'D']},
    {"name": "ThirdReich Militaria", "flag": "🇮🇹", "region": "EU", "match": ["thirdreich-militaria.com", "thirdreich militaria", "third reich militaria"], "logo_file": "thirdreich_militaria.png", "url": "https://www.thirdreich-militaria.com/", "eras": [3], "countries": ['D']},
    {"name": "Richter Historica", "flag": "🇩🇪", "region": "EU", "match": ["richter-historica.de", "richter historica"], "logo_file": "Richter_Historica.png", "url": "https://richter-historica.de/en/10-militaria", "eras": [3], "countries": ['D']},
    {"name": "Military Antiques Toronto", "flag": "🇨🇦", "region": "NA", "match": ["militaryantiquestoronto.com", "military antiques toronto"], "logo_file": "Military_Antiques_Toronto.png", "url": "https://militaryantiquestoronto.com/new-items/", "eras": [0], "countries": ['Z']},
    {"name": "Giel's Militaria", "flag": "🇧🇪", "region": "EU", "match": ["gielsmilitaria.com", "giel's militaria", "giels militaria"], "logo_file": "giels_militaria.png", "url": "https://www.gielsmilitaria.com/", "eras": [2, 3], "countries": ['D']},
    {"name": "SMG War Relics", "flag": "🇺🇸", "region": "NA", "match": ["war-relics.com", "smg war relics", "smg militaria"], "logo_file": "smg_war_relics.png", "url": "https://war-relics.com/shop/", "eras": [2, 3], "countries": ['A', 'B', 'D']},
    {"name": "Hanna's Militaria", "flag": "🇺🇸", "region": "NA", "match": ["hannasmilitaria.com", "hanna's militaria", "hannas militaria"], "logo_file": "hannas_militaria.png", "url": "https://hannasmilitaria.com/newly-listed/", "eras": [3], "countries": ['D']},
    {"name": "Marna Militaria", "flag": "🇳🇱", "region": "EU", "match": ["marnamilitaria.com", "marna militaria"], "logo_file": "Marna_militaria.png", "url": "https://marnamilitaria.com/shop.php", "eras": [2, 3], "countries": ['D', 'I']},
    {"name": "CS Militaria", "flag": "🇬🇧", "region": "EU", "match": ["csmilitaria.co.uk", "cs militaria"], "logo_file": "cs_militaria.png", "url": "https://csmilitaria.co.uk/shop.php", "eras": [2, 3], "countries": ['A', 'B', 'C', 'D', 'F']},
    {"name": "Chase Militaria", "flag": "🇬🇧", "region": "EU", "match": ["chasemilitaria.com", "chase militaria"], "logo_file": "chase_militaria.png", "url": "https://chasemilitaria.com/shop.php", "eras": [2, 3, 6], "countries": ['A', 'B', 'D', 'G', 'E']},
    {"name": "WorldWar 2 Collectibles", "flag": "🇬🇧", "region": "EU", "match": ["worldwarcollectibles.com", "worldwar2collectibles.com", "world war 2 collectibles", "worldwar 2 collectibles"], "logo_file": "Worldwar2collectibles.png", "url": "https://www.worldwarcollectibles.com/shop.php", "eras": [3, 5], "countries": ['A', 'B']},
    {"name": "E-Medals", "flag": "🇨🇦", "region": "NA", "match": ["emedals.com", "e-medals", "emedals"], "logo_file": "e_medals.png", "url": "https://www.emedals.com/collections/newly-listed", "eras": [0], "countries": ['Z']},
    {"name": "Espenlaub Militaria", "flag": "🇪🇪", "region": "EU", "match": ["aboutww2militaria.com", "espenlaub militaria", "espenlaub"], "logo_file": "espenlaub_militaria.png", "url": "https://aboutww2militaria.com/new-items.html", "eras": [2, 3], "countries": ['D', 'E']},
    {"name": "US Militaria Forum", "flag": "🇺🇸", "region": "NA", "match": ["usmilitariaforum.com", "us militaria forum", "usmf", "u.s. militaria forum"], "logo_file": "usmf.png", "url": "https://www.usmilitariaforum.com/forums/", "usmf": True, "eras": [0], "countries": ['Z']},
    {"name": "VIP Militaria", "flag": "🇩🇪", "region": "EU", "match": ["vip-militaria.de", "vip militaria"], "logo_file": "vip_militaria.png", "url": "https://www.vip-militaria.de/NEU-im-Shop/", "eras": [3], "countries": ['D']},
    {"name": "G.K. Militaria", "flag": "🇩🇪", "region": "EU", "match": ["gkmilitaria@emailer500.com", "gkmilitaria", "g.k. militaria", "gerhard kloucek"], "logo_file": "GK_Militaria.png", "url": "https://gkmilitaria.at/shop.php", "eras": [2, 3], "countries": ["I", "D"]},
    {"name": "WW2 German Daggers", "flag": "🇬🇧", "region": "EU", "match": ["ww2germandaggers@emailer500.com", "ww2germandaggers"], "logo_file": "ww2germandaggers.png", "url": "https://ww2germandaggers.com/shop.php", "eras": [3], "countries": ["D"]},
    {"name": "MV40-45", "flag": "🇳🇱", "region": "EU", "match": ["mv40-45@emailer500.com", "mv40-45"], "logo_file": "mv40_45.png", "url": "https://mv40-45.com/shop", "eras": [3], "countries": ["A", "B", "D"]},
    {"name": "Epsom1944", "flag": "🇳🇱", "region": "EU", "match": ["epsom1944@emailer500.com", "epsom1944"], "logo_file": "Epsom_1944.png", "url": "https://epsom1944.com/shop.php", "eras": [3], "countries": ["D"]},
    {"name": "Time Traveler Militaria", "flag": "🇺🇸", "region": "NA", "match": ["ttmilitaria.com", "time traveler militaria"], "logo_file": "Time_traveler_militaria.png", "url": "https://www.ttmilitaria.com/", "eras": [0], "countries": ["Z"]},
    {"name": "Joe's Military Collectibles", "flag": "🇺🇸", "region": "NA", "match": ["joesmilitary@emailer500.com", "joe's military collectibles", "joesmilitary"], "logo_file": "joes_military_collectibles.png", "url": "https://joesmilitary.com/shop.php", "eras": [2, 3], "countries": ["A"]},
    {"name": "Summer Vacation Militaria", "flag": "🇺🇸", "region": "NA", "match": ["svmilitaria", "summer vacation militaria", "sv militaria", "noreply@svmilitaria.com"], "logo_file": "summer_vacation_militaria.png", "url": "https://www.svmilitaria.com/NewItems.htm", "eras": [2, 3], "countries": ['A', 'H', 'D']},
    {"name": "Clements Militaria", "flag": "🇳🇱", "region": "EU", "match": ["clementsm@emailer500.com", "clements militaria", "clementsmilitaria.com"], "logo_file": "clements_militaria.png", "url": "https://clementsmilitaria.com/shop.php", "eras": [3], "countries": ['B', 'A', 'D']},
]

USMF_CHANNEL_ID = 1513271593273655387  # #adrian — test server


# ==================== BOT SETUP ====================
intents = discord.Intents.all()

class MilitariaBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.db = None

    async def setup_hook(self):
        try:
            # DB connection with retry
            for attempt in range(5):
                try:
                    self.db = await asyncpg.create_pool(
                        DATABASE_URL,
                        min_size=2,
                        max_size=10,
                        command_timeout=30,
                        max_inactive_connection_lifetime=300
                    )
                    logger.info("Database connection pool created successfully")
                    break
                except Exception as db_err:
                    if attempt < 4:
                        logger.warning(f"DB connection attempt {attempt+1}/5 failed: {db_err} — retrying in 5s...")
                        await asyncio.sleep(5)
                    else:
                        raise
            await self.init_db()
            # Sync to known guilds for instant command availability
            for gid in [GUILD_ID, TEST_GUILD_ID]:
                try:
                    g = discord.Object(id=gid)
                    self.tree.copy_global_to(guild=g)
                    await self.tree.sync(guild=g)
                    logger.info(f"Slash commands synced to guild {gid}")
                except discord.Forbidden:
                    logger.warning(f"Could not sync to guild {gid} — bot may not be in that server yet")
                except Exception as sync_err:
                    logger.warning(f"Guild sync failed for {gid}: {sync_err}")
            # Sync globally so new servers get commands within ~1 hour
            await self.tree.sync()
            logger.info("Slash commands synced globally!")
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
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id TEXT PRIMARY KEY,
                    estand_agreed INTEGER DEFAULT 0,
                    created_at BIGINT DEFAULT 0,
                    region TEXT DEFAULT 'both',
                    eras TEXT DEFAULT '',
                    updated_at BIGINT NOT NULL
                )
            ''')
            await conn.execute("ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS eras TEXT DEFAULT ''")
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS pending_alerts (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    dealer_name TEXT NOT NULL,
                    dealer_url TEXT NOT NULL,
                    dealer_flag TEXT DEFAULT '🌐',
                    created_at BIGINT NOT NULL
                )
            ''')
            await conn.execute("ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS countries TEXT DEFAULT ''")
            await conn.execute("ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS forums TEXT DEFAULT ''")
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS estate_transactions (
                    id SERIAL PRIMARY KEY,
                    thread_id TEXT NOT NULL,
                    thread_name TEXT NOT NULL,
                    seller_id TEXT NOT NULL,
                    buyer_id TEXT,
                    rating INTEGER,
                    review TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at BIGINT NOT NULL,
                    completed_at BIGINT
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS estate_ratings (
                    id SERIAL PRIMARY KEY,
                    buyer_id TEXT NOT NULL,
                    seller_id TEXT NOT NULL,
                    thread_id TEXT NOT NULL,
                    rating INTEGER NOT NULL,
                    review TEXT,
                    timestamp BIGINT NOT NULL
                )
            ''')
            # Add new columns if they don't exist (safe migration)
            try:
                await conn.execute("ALTER TABLE server_config ADD COLUMN view_all_channels INTEGER DEFAULT 0")
            except Exception as _e:

                logger.debug(f"[Silent] {_e}")
            try:
                await conn.execute("ALTER TABLE server_config ADD COLUMN welcome_message_id TEXT")
            except Exception:
                pass
            try:
                await conn.execute("ALTER TABLE server_config ADD COLUMN estand_verified_role_id TEXT")
            except Exception:
                pass
            try:
                await conn.execute("ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS estand_agreed INTEGER DEFAULT 0")
            except Exception:
                pass
            try:
                await conn.execute("ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS created_at BIGINT DEFAULT 0")
            except Exception:
                pass  # Column already exists

            await conn.execute('''
                CREATE TABLE IF NOT EXISTS estand_blocked_tags (
                    id SERIAL PRIMARY KEY,
                    guild_id TEXT NOT NULL,
                    tag_name TEXT NOT NULL,
                    UNIQUE(guild_id, tag_name)
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS scam_flags (
                    id SERIAL PRIMARY KEY,
                    flagged_user_id TEXT NOT NULL,
                    flagged_by TEXT NOT NULL,
                    guild_id TEXT NOT NULL,
                    reason TEXT,
                    created_at BIGINT NOT NULL,
                    UNIQUE(flagged_user_id, flagged_by)
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS keyword_watchlist (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    keyword TEXT NOT NULL,
                    keyword_type TEXT DEFAULT 'forum',
                    created_at BIGINT NOT NULL,
                    UNIQUE(user_id, keyword)
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS listing_blocks (
                    id SERIAL PRIMARY KEY,
                    seller_id TEXT NOT NULL,
                    buyer_id TEXT NOT NULL,
                    thread_id TEXT NOT NULL,
                    created_at BIGINT NOT NULL
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS cross_post_mirrors (
                    id SERIAL PRIMARY KEY,
                    original_thread_id TEXT NOT NULL,
                    original_guild_id TEXT NOT NULL,
                    original_seller_id TEXT NOT NULL,
                    mirror_thread_id TEXT,
                    mirror_guild_id TEXT NOT NULL,
                    mirror_channel_id TEXT NOT NULL,
                    item_title TEXT,
                    status TEXT DEFAULT 'active',
                    created_at BIGINT NOT NULL
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS image_url_cache (
                    key TEXT PRIMARY KEY,
                    url TEXT NOT NULL,
                    updated_at BIGINT DEFAULT 0
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS user_warnings (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    warning_type TEXT DEFAULT 'warning',
                    issued_by TEXT,
                    guild_id TEXT,
                    timestamp BIGINT NOT NULL
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS server_config (
                    guild_id TEXT PRIMARY KEY,
                    guild_name TEXT,
                    owner_id TEXT,
                    channel_id TEXT,
                    updates_channel_id TEXT,
                    estate_channel_id TEXT,
                    estate_cross_posts_channel_id TEXT,
                    mod_log_channel_id TEXT,
                    bot_feedback_channel_id TEXT,
                    review_log_channel_id TEXT,
                    image_host_channel_id TEXT,
                    verified_role_id TEXT,
                    premium_role_id TEXT,
                    guerrilla_role_id TEXT,
                    estate_sold_tag_id TEXT,
                    estate_name TEXT DEFAULT 'Estate',
                    alerts_region TEXT DEFAULT 'both',
                    alerts_forums TEXT DEFAULT 'both',
                    accept_cross_posts INTEGER DEFAULT 0,
                    setup_complete INTEGER DEFAULT 0,
                    premium INTEGER DEFAULT 0,
                    view_all_channels INTEGER DEFAULT 0,
                    welcome_message_id TEXT,
                    estand_verified_role_id TEXT,
                    image_cache_version INTEGER DEFAULT 0,
                    created_at BIGINT NOT NULL
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
    "dealer_cooldowns": {},
    "waf_notification_count": 0,
    "startup_time": None,
    "alert_count": 0,
    "error_count": 0,
    "last_error": None,
    "last_error_time": None,
    "db_query_count": 0,
    "cross_post_count": 0,
    "estand_listing_count": 0,
    "question1_img_url": None,
    "question2_img_url": None,
    "question3_img_url": None,
    "question4_img_url": None,
    "question5_img_url": None,
    "thankyou_img_url": None,
    "check_before_buy_img_url": None,
    "setup_img_url": None,
    "setup_q1_img_url": None,
    "setup_q2_img_url": None,
    "setup_end_img_url": None,
    "setup_stop_img_url": None,
    "setup_estand_img_url": None,
    "setup_crosspost_img_url": None,
    "setup_please_img_url": None,
    "error_404_img_url": None,
    "command_cooldowns": {},
    "health_status": "starting",
    "startup_time": None,
    "watched_channels": {},
    "pending_pings": {},
    "ping_task_running": False,
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

async def db_follow_dealer(user_id, dealer_name, is_premium=False):
    logger.debug(f"[DB] db_follow_dealer: user={user_id} dealer={dealer_name}")
    async with client.db.acquire() as conn:
        # Check free limit
        if not is_premium:
            count = await conn.fetchval(
                "SELECT COUNT(*) FROM dealer_follows WHERE user_id=$1",
                str(user_id)
            )
            if count >= FREE_DEALER_FOLLOW_LIMIT:
                return False, f"You\'ve reached the free limit of {FREE_DEALER_FOLLOW_LIMIT} dealer follows. Upgrade to premium for unlimited follows!"
        await conn.execute(
            "INSERT INTO dealer_follows (user_id, dealer_name, timestamp) VALUES ($1,$2,$3) ON CONFLICT DO NOTHING",
            str(user_id), dealer_name, int(datetime.now(timezone.utc).timestamp())
        )
        return True, f"✅ Now following **{dealer_name}**!"

async def db_unfollow_dealer(user_id, dealer_name):
    logger.debug(f"[DB] db_unfollow_dealer: user={user_id} dealer={dealer_name}")
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


# ==================== SERVER CONFIG DB ====================

async def db_get_server_config(guild_id):
    """Get config for a specific server. Returns dict or None if not set up."""
    async with client.db.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM server_config WHERE guild_id=$1", str(guild_id))
        return dict(row) if row else None

async def db_save_server_config(guild_id, **kwargs):
    """Insert or update a server config."""
    logger.debug(f"[DB] db_save_server_config guild={guild_id} keys={list(kwargs.keys())}")
    async with client.db.acquire() as conn:
        existing = await conn.fetchrow("SELECT guild_id FROM server_config WHERE guild_id=$1", str(guild_id))
        if existing:
            set_clause = ", ".join([f"{k}=${i+2}" for i, k in enumerate(kwargs.keys())])
            values = [str(guild_id)] + list(kwargs.values())
            await conn.execute(f"UPDATE server_config SET {set_clause} WHERE guild_id=$1", *values)
        else:
            kwargs["created_at"] = int(datetime.now(timezone.utc).timestamp())
            cols = "guild_id, " + ", ".join(kwargs.keys())
            placeholders = ", ".join([f"${i+1}" for i in range(len(kwargs)+1)])
            values = [str(guild_id)] + list(kwargs.values())
            await conn.execute(f"INSERT INTO server_config ({cols}) VALUES ({placeholders})", *values)

async def db_get_all_servers():
    """Get all server configs — for owner dashboard."""
    async with client.db.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM server_config ORDER BY created_at DESC")
        logger.debug(f"[DB] db_get_all_servers: returned {len(rows)} server(s)")
        return [dict(r) for r in rows]

async def db_is_setup(guild_id):
    """Check if a server has completed setup."""
    config = await db_get_server_config(guild_id)
    return config and config.get("setup_complete") == "1"

def get_config_value(config, key, fallback=None):
    """Safely get a value from server config, converting to int if it looks like an ID."""
    if not config:
        return fallback
    val = config.get(key)
    if val is None:
        return fallback
    try:
        return int(val)
    except (ValueError, TypeError):
        return val

# ==================== ESTATE DB FUNCTIONS ====================

async def db_create_transaction(thread_id, thread_name, seller_id):
    async with client.db.acquire() as conn:
        await conn.execute(
            "INSERT INTO estate_transactions (thread_id, thread_name, seller_id, status, created_at) VALUES ($1,$2,$3,'pending',$4) ON CONFLICT DO NOTHING",
            str(thread_id), thread_name, str(seller_id), int(datetime.now(timezone.utc).timestamp())
        )

async def db_set_transaction_buyer(thread_id, buyer_id):
    async with client.db.acquire() as conn:
        await conn.execute(
            "UPDATE estate_transactions SET buyer_id=$1, status='awaiting_rating' WHERE thread_id=$2",
            str(buyer_id), str(thread_id)
        )

async def db_get_transaction(thread_id):
    async with client.db.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM estate_transactions WHERE thread_id=$1", str(thread_id))
        return dict(row) if row else None

async def db_complete_transaction(thread_id, rating, review=""):
    async with client.db.acquire() as conn:
        await conn.execute(
            "UPDATE estate_transactions SET rating=$1, review=$2, status='completed', completed_at=$3 WHERE thread_id=$4",
            rating, review, int(datetime.now(timezone.utc).timestamp()), str(thread_id)
        )

async def db_add_estate_rating(buyer_id, seller_id, thread_id, rating, review=""):
    async with client.db.acquire() as conn:
        await conn.execute(
            "INSERT INTO estate_ratings (buyer_id, seller_id, thread_id, rating, review, timestamp) VALUES ($1,$2,$3,$4,$5,$6)",
            str(buyer_id), str(seller_id), str(thread_id), rating, review, int(datetime.now(timezone.utc).timestamp())
        )

async def db_get_buyer_rating(buyer_id):
    async with client.db.acquire() as conn:
        rows = await conn.fetch("SELECT rating FROM estate_ratings WHERE buyer_id=$1", str(buyer_id))
        if not rows:
            return None, 0
        ratings = [r["rating"] for r in rows]
        return round(sum(ratings) / len(ratings), 1), len(ratings)

async def db_get_seller_rating(seller_id):
    async with client.db.acquire() as conn:
        rows = await conn.fetch("SELECT rating FROM estate_ratings WHERE seller_id=$1", str(seller_id))
        if not rows:
            return None, 0
        ratings = [r["rating"] for r in rows]
        return round(sum(ratings) / len(ratings), 1), len(ratings)

async def db_get_user_reviews(user_id):
    """Get reviews left for a user as either buyer or seller."""
    async with client.db.acquire() as conn:
        rows = await conn.fetch(
            "SELECT rating, review, buyer_id, seller_id, timestamp FROM estate_ratings WHERE buyer_id=$1 OR seller_id=$1 ORDER BY timestamp DESC LIMIT 5",
            str(user_id)
        )
        return [dict(r) for r in rows]

async def db_get_completed_transactions(user_id):
    """Get count of completed transactions as buyer and seller."""
    async with client.db.acquire() as conn:
        seller_count = await conn.fetchval(
            "SELECT COUNT(*) FROM estate_transactions WHERE seller_id=$1 AND status='completed'",
            str(user_id)
        )
        buyer_count = await conn.fetchval(
            "SELECT COUNT(*) FROM estate_transactions WHERE buyer_id=$1 AND status='completed'",
            str(user_id)
        )
        return seller_count or 0, buyer_count or 0

# ==================== HELPER FUNCTIONS ====================

def format_stars(avg):
    """Format a star rating for display."""
    if avg is None:
        return "No ratings yet"
    return "⭐" * full + "☆" * (5 - full) + f" ({avg:.1f})"

# ==================== ESTAND BLOCKED TAGS DB ====================

async def db_get_blocked_tags(guild_id):
    async with client.db.acquire() as conn:
        rows = await conn.fetch("SELECT tag_name FROM estand_blocked_tags WHERE guild_id=$1", str(guild_id))
        return [r["tag_name"] for r in rows]

async def db_set_blocked_tags(guild_id, tag_names):
    async with client.db.acquire() as conn:
        await conn.execute("DELETE FROM estand_blocked_tags WHERE guild_id=$1", str(guild_id))
        for tag_name in tag_names:
            await conn.execute(
                "INSERT INTO estand_blocked_tags (guild_id, tag_name) VALUES ($1,$2) ON CONFLICT DO NOTHING",
                str(guild_id), tag_name
            )

async def is_listing_blocked_for_guild(thread, dest_guild_id):
    """Check if a listing's tags are blocked by the destination guild."""
    blocked = await db_get_blocked_tags(str(dest_guild_id))
    if not blocked:
        return False
    thread_tag_names = {t.name for t in getattr(thread, "applied_tags", [])}
    for blocked_tag in blocked:
        if blocked_tag in thread_tag_names:
            return True
    return False

# ==================== ESTAND STANDARD TAGS ====================

ESTAND_STANDARD_TAGS = [
    # Status tags
    discord.ForumTag(name="Active", emoji=discord.PartialEmoji(name="🟢")),
    discord.ForumTag(name="Sold", emoji=discord.PartialEmoji(name="🔴")),
    discord.ForumTag(name="On Hold", emoji=discord.PartialEmoji(name="🟡")),
    discord.ForumTag(name="Cross-Posted", emoji=discord.PartialEmoji(name="🌐")),
    # Country tags
    discord.ForumTag(name="🇺🇸 American"),
    discord.ForumTag(name="🇩🇪 German"),
    discord.ForumTag(name="🇬🇧 British"),
    discord.ForumTag(name="🇷🇺 Soviet"),
    discord.ForumTag(name="🇯🇵 Japanese"),
    discord.ForumTag(name="🇫🇷 French"),
    discord.ForumTag(name="🇮🇹 Italian"),
    discord.ForumTag(name="🇨🇦 Canadian"),
    discord.ForumTag(name="🇦🇹 Austro-Hungarian"),
    discord.ForumTag(name="🌍 Other"),
    # Era tags
    discord.ForumTag(name="WWI"),
    discord.ForumTag(name="WWII"),
    discord.ForumTag(name="Pre-WWI"),
    discord.ForumTag(name="Cold War"),
    discord.ForumTag(name="Vietnam"),
    discord.ForumTag(name="Korea"),
    discord.ForumTag(name="GWOT"),
]

async def add_standard_tags_to_forum(forum_channel):
    """Add any missing standard tags to an existing Estand forum channel."""
    existing_names = {t.name for t in forum_channel.available_tags}
    new_tags = list(forum_channel.available_tags)
    added = []
    for tag in ESTAND_STANDARD_TAGS:
        if tag.name not in existing_names and len(new_tags) < 20:  # Discord limit is 20 tags
            new_tags.append(tag)
            added.append(tag.name)
    if added:
        await forum_channel.edit(available_tags=new_tags)
    return added

# ==================== SCAM FLAG SYSTEM ====================

SCAM_FLAG_THRESHOLD = 2  # Number of mod flags needed to trigger global ban

async def db_add_scam_flag(flagged_user_id, flagged_by, guild_id, reason):
    """Add a scam flag. Returns (total_flags, newly_added)."""
    async with client.db.acquire() as conn:
        try:
            await conn.execute(
                "INSERT INTO scam_flags (flagged_user_id, flagged_by, guild_id, reason, created_at) VALUES ($1,$2,$3,$4,$5)",
                str(flagged_user_id), str(flagged_by), str(guild_id), reason,
                int(datetime.now(timezone.utc).timestamp())
            )
            newly_added = True
        except Exception:
            newly_added = False  # Already flagged by this mod
        total = await conn.fetchval(
            "SELECT COUNT(*) FROM scam_flags WHERE flagged_user_id=$1",
            str(flagged_user_id)
        )
        return total or 0, newly_added

async def db_get_scam_flags(user_id):
    async with client.db.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM scam_flags WHERE flagged_user_id=$1 ORDER BY created_at ASC",
            str(user_id)
        )
        return [dict(r) for r in rows]

async def db_remove_scam_flag(flagged_user_id):
    """Clear all scam flags for a user (bot owner only)."""
    async with client.db.acquire() as conn:
        await conn.execute("DELETE FROM scam_flags WHERE flagged_user_id=$1", str(flagged_user_id))
        await conn.execute(
            "DELETE FROM user_warnings WHERE user_id=$1 AND warning_type='scammer'",
            str(flagged_user_id)
        )

# ==================== KEYWORD WATCHLIST DB ====================

FREE_DEALER_FOLLOW_LIMIT = 5
FREE_KEYWORD_LIMIT = 3

async def db_get_user_keywords(user_id):
    async with client.db.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM keyword_watchlist WHERE user_id=$1 ORDER BY created_at ASC",
            str(user_id)
        )
        return [dict(r) for r in rows]

async def db_add_keyword(user_id, keyword, is_premium=False):
    """Add keyword — returns (success, message)."""
    async with client.db.acquire() as conn:
        # Check limit for free users
        if not is_premium:
            count = await conn.fetchval(
                "SELECT COUNT(*) FROM keyword_watchlist WHERE user_id=$1",
                str(user_id)
            )
            if count >= FREE_KEYWORD_LIMIT:
                return False, f"You've reached the free limit of {FREE_KEYWORD_LIMIT} keyword alerts. Upgrade to premium for unlimited keywords!"
        # Check duplicate
        existing = await conn.fetchrow(
            "SELECT 1 FROM keyword_watchlist WHERE user_id=$1 AND LOWER(keyword)=LOWER($2)",
            str(user_id), keyword
        )
        if existing:
            return False, f"You're already watching the keyword **{keyword}**."
        await conn.execute(
            "INSERT INTO keyword_watchlist (user_id, keyword, created_at) VALUES ($1,$2,$3)",
            str(user_id), keyword.lower().strip(), int(datetime.now(timezone.utc).timestamp())
        )
        return True, f"✅ Keyword **{keyword}** added to your watchlist!"

async def db_remove_keyword(user_id, keyword):
    async with client.db.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM keyword_watchlist WHERE user_id=$1 AND LOWER(keyword)=LOWER($2)",
            str(user_id), keyword.lower().strip()
        )
        return result != "DELETE 0"

async def db_get_users_for_keyword(keyword):
    """Get all users watching a specific keyword."""
    async with client.db.acquire() as conn:
        rows = await conn.fetch(
            "SELECT user_id FROM keyword_watchlist WHERE $1 ILIKE '%' || keyword || '%'",
            keyword
        )
        return [r["user_id"] for r in rows]

async def db_get_dealer_follow_count(user_id):
    async with client.db.acquire() as conn:
        return await conn.fetchval(
            "SELECT COUNT(*) FROM dealer_follows WHERE user_id=$1",
            str(user_id)
        ) or 0

async def db_is_premium(user_id):
    """Check if user has premium — placeholder until premium system is built."""
    return False  # Everyone is free for now

# ==================== LISTING NEGOTIATION DB ====================

async def db_block_buyer(seller_id, buyer_id, thread_id):
    async with client.db.acquire() as conn:
        await conn.execute(
            "INSERT INTO listing_blocks (seller_id, buyer_id, thread_id, created_at) VALUES ($1,$2,$3,$4) ON CONFLICT DO NOTHING",
            str(seller_id), str(buyer_id), str(thread_id),
            int(datetime.now(timezone.utc).timestamp())
        )

async def db_is_buyer_blocked(seller_id, buyer_id, thread_id):
    async with client.db.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT 1 FROM listing_blocks WHERE seller_id=$1 AND buyer_id=$2 AND thread_id=$3",
            str(seller_id), str(buyer_id), str(thread_id)
        )
        return row is not None

# ==================== CROSS-POST DB ====================

async def db_save_cross_post_mirror(original_thread_id, original_guild_id, original_seller_id, mirror_guild_id, mirror_channel_id, item_title, mirror_thread_id=None):
    async with client.db.acquire() as conn:
        await conn.execute(
            """INSERT INTO cross_post_mirrors
               (original_thread_id, original_guild_id, original_seller_id, mirror_thread_id, mirror_guild_id, mirror_channel_id, item_title, created_at)
               VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
               ON CONFLICT DO NOTHING""",
            str(original_thread_id), str(original_guild_id), str(original_seller_id),
            str(mirror_thread_id) if mirror_thread_id else None,
            str(mirror_guild_id), str(mirror_channel_id), item_title,
            int(datetime.now(timezone.utc).timestamp())
        )

async def db_get_mirror_servers(original_thread_id):
    """Get servers that already have a mirror for this thread."""
    async with client.db.acquire() as conn:
        rows = await conn.fetch(
            "SELECT mirror_guild_id FROM cross_post_mirrors WHERE original_thread_id=$1",
            str(original_thread_id)
        )
        return [r["mirror_guild_id"] for r in rows]

async def db_mark_mirror_sold(original_thread_id):
    """Mark all mirrors of a thread as sold."""
    async with client.db.acquire() as conn:
        rows = await conn.fetch(
            "SELECT mirror_channel_id, mirror_thread_id FROM cross_post_mirrors WHERE original_thread_id=$1 AND status='active'",
            str(original_thread_id)
        )
        await conn.execute(
            "UPDATE cross_post_mirrors SET status='sold' WHERE original_thread_id=$1",
            str(original_thread_id)
        )
        return [dict(r) for r in rows]

# ==================== RANK SYSTEM ====================

RANKS = [
    (0,     "🪖 Private"),
    (30,    "🪖 Private 1st Class"),
    (100,   "⚔️ Corporal"),
    (300,   "⚔️ Sergeant"),
    (600,   "⚔️ Sergeant Major"),
    (1000,  "🎖️ Warrant Officer"),
    (1500,  "🎖️ Lieutenant"),
    (2000,  "🎖️ Captain"),
    (3000,  "🏅 Major"),
    (5000,  "🏅 Colonel"),
    (10000, "👑 Maréchal d'Empire"),
]

async def db_get_user_points(user_id):
    """Calculate total rank points for a user."""
    logger.debug(f"[DB] db_get_user_points: user={user_id}")
    async with client.db.acquire() as conn:
        # Points from completed transactions (30 each)
        tx_count = await conn.fetchval(
            "SELECT COUNT(*) FROM estate_transactions WHERE (seller_id=$1 OR buyer_id=$1) AND status='completed'",
            str(user_id)
        ) or 0
        # Points from dealer reviews (10 each)
        review_count = await conn.fetchval(
            "SELECT COUNT(*) FROM reviews WHERE user_id=$1 AND status='approved'",
            str(user_id)
        ) or 0
        return (tx_count * 30) + (review_count * 10)

async def db_get_user_warnings(user_id):
    """Check if user has active warnings."""
    try:
        async with client.db.acquire() as conn:
            count = await conn.fetchval(
                "SELECT COUNT(*) FROM user_warnings WHERE user_id=$1",
                str(user_id)
            )
            return count or 0
    except Exception:
        return 0

async def db_add_user_warning(user_id, reason, warning_type="warning", issued_by=None, guild_id=None):
    """Add a warning to a user."""
    async with client.db.acquire() as conn:
        await conn.execute(
            "INSERT INTO user_warnings (user_id, reason, warning_type, issued_by, guild_id, timestamp) VALUES ($1,$2,$3,$4,$5,$6)",
            str(user_id), reason, warning_type, str(issued_by) if issued_by else None,
            str(guild_id) if guild_id else None, int(datetime.now(timezone.utc).timestamp())
        )

async def db_get_user_warning_list(user_id):
    """Get all warnings for a user."""
    async with client.db.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM user_warnings WHERE user_id=$1 ORDER BY timestamp DESC",
            str(user_id)
        )
        return [dict(r) for r in rows]

async def db_remove_user_warning(warning_id):
    """Remove a specific warning by ID."""
    async with client.db.acquire() as conn:
        await conn.execute("DELETE FROM user_warnings WHERE id=$1", warning_id)

def get_rank(points, has_warnings=False):
    """Get rank name based on points. Warnings block above Corporal."""
    rank_name = RANKS[0][1]
    for threshold, name in RANKS:
        if points >= threshold:
            rank_name = name
        else:
            break
    # Warnings block progression past Corporal
    if has_warnings:
        corporal_rank = RANKS[2][1]
        rank_index = [r[1] for r in RANKS].index(rank_name)
        if rank_index > 2:
            rank_name = corporal_rank + " ⚠️"
    return rank_name

async def db_get_top_percent(user_id):
    """Calculate what percentile a user is in globally."""
    logger.debug(f"[DB] db_get_top_percent: user={user_id}")
    user_points = await db_get_user_points(str(user_id))
    if user_points == 0:
        return None
    async with client.db.acquire() as conn:
        # Get all users with at least 1 point
        tx_users = await conn.fetch(
            """SELECT unnest(ARRAY[seller_id, buyer_id]) as user_id, COUNT(*) as cnt
               FROM estate_transactions WHERE status='completed'
               GROUP BY user_id"""
        )
        review_users = await conn.fetch(
            "SELECT user_id, COUNT(*) as cnt FROM reviews WHERE status='approved' GROUP BY user_id"
        )
        # Build points map
        points_map = {}
        for row in tx_users:
            points_map[row["user_id"]] = points_map.get(row["user_id"], 0) + (row["cnt"] * 30)
        for row in review_users:
            points_map[row["user_id"]] = points_map.get(row["user_id"], 0) + (row["cnt"] * 10)

        if not points_map:
            return None

        all_points = sorted(points_map.values(), reverse=True)
        total = len(all_points)
        # Find where user ranks
        rank_pos = sum(1 for p in all_points if p > user_points)
        percentile = (rank_pos / total) * 100

        if percentile <= 1:
            return "🌟 Top 1%"
        elif percentile <= 5:
            return "🏆 Top 5%"
        return None

# ==================== USER PREFERENCES DB ====================
async def db_get_user_region(user_id):
    async with client.db.acquire() as conn:
        row = await conn.fetchrow("SELECT region FROM user_preferences WHERE user_id=$1", str(user_id))
        return row["region"] if row else None

async def db_set_user_region(user_id, region):
    async with client.db.acquire() as conn:
        now = int(datetime.now(timezone.utc).timestamp())
        await conn.execute(
            """INSERT INTO user_preferences (user_id, region, updated_at, created_at)
               VALUES ($1,$2,$3,$3)
               ON CONFLICT (user_id) DO UPDATE SET region=$2, updated_at=$3,
               created_at=COALESCE(NULLIF(user_preferences.created_at, 0), $3)""",
            str(user_id), region, now
        )

async def db_get_user_eras(user_id):
    async with client.db.acquire() as conn:
        row = await conn.fetchrow("SELECT eras FROM user_preferences WHERE user_id=$1", str(user_id))
        if row and row["eras"]:
            return [int(e) for e in row["eras"].split(",")]
        return None

async def db_set_user_eras(user_id, eras):
    async with client.db.acquire() as conn:
        era_str = ",".join(str(e) for e in eras)
        await conn.execute(
            "UPDATE user_preferences SET eras=$1, updated_at=$2 WHERE user_id=$3",
            era_str, int(datetime.now(timezone.utc).timestamp()), str(user_id)
        )

async def db_get_user_countries(user_id):
    async with client.db.acquire() as conn:
        row = await conn.fetchrow("SELECT countries FROM user_preferences WHERE user_id=$1", str(user_id))
        if row and row["countries"]:
            return list(row["countries"].split(","))
        return None

async def db_set_user_countries(user_id, countries):
    async with client.db.acquire() as conn:
        country_str = ",".join(countries)
        await conn.execute(
            "UPDATE user_preferences SET countries=$1, updated_at=$2 WHERE user_id=$3",
            country_str, int(datetime.now(timezone.utc).timestamp()), str(user_id)
        )

# ==================== PENDING ALERTS DB ====================

async def db_add_pending_alert(user_id, dealer_name, dealer_url, dealer_flag):
    async with client.db.acquire() as conn:
        await conn.execute(
            "INSERT INTO pending_alerts (user_id, dealer_name, dealer_url, dealer_flag, created_at) VALUES ($1,$2,$3,$4,$5)",
            str(user_id), dealer_name, dealer_url, dealer_flag, int(datetime.now(timezone.utc).timestamp())
        )

async def db_get_pending_alerts(user_id):
    async with client.db.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM pending_alerts WHERE user_id=$1 ORDER BY created_at ASC",
            str(user_id)
        )
        return [dict(r) for r in rows]

async def db_clear_pending_alerts(user_id):
    async with client.db.acquire() as conn:
        await conn.execute("DELETE FROM pending_alerts WHERE user_id=$1", str(user_id))

async def db_cleanup_old_alerts():
    """Remove alerts older than 24 hours."""
    cutoff = int(datetime.now(timezone.utc).timestamp()) - (24 * 3600)
    async with client.db.acquire() as conn:
        deleted = await conn.fetchval("SELECT COUNT(*) FROM pending_alerts WHERE created_at < $1", cutoff)
        await conn.execute("DELETE FROM pending_alerts WHERE created_at < $1", cutoff)
        if deleted:
            logger.info(f"[Alerts] Cleaned up {deleted} expired pending alerts")

async def db_get_users_for_forum(forum_type):
    """Get user_ids who opted in to a specific forum (waf, usmf, or both)."""
    async with client.db.acquire() as conn:
        rows = await conn.fetch(
            "SELECT user_id FROM user_preferences WHERE forums=$1 OR forums='both'",
            forum_type
        )
        return [r["user_id"] for r in rows]

async def db_get_users_for_dealer(dealer_region, dealer_eras, dealer_countries):
    """Get all user_ids whose full profile matches this dealer."""
    async with client.db.acquire() as conn:
        rows = await conn.fetch(
            "SELECT user_id, region, eras, countries FROM user_preferences WHERE region IS NOT NULL AND eras IS NOT NULL AND eras != '' AND countries IS NOT NULL AND countries != ''"
        )
    matched = []
    for row in rows:
        user_id = row["user_id"]
        user_region = row["region"] or "both"
        user_eras = [int(e) for e in row["eras"].split(",") if e] if row["eras"] else []
        user_countries = list(row["countries"].split(",")) if row["countries"] else []

        # Region check
        if user_region != "both" and user_region != dealer_region:
            continue

        # Era check — pass if user selected "all" (0) or dealer has "all" (0) or any overlap
        if 0 not in user_eras and 0 not in dealer_eras:
            if not set(user_eras) & set(dealer_eras):
                continue

        # Country check — pass if user selected "Z" (all) or dealer has "Z" or any overlap
        if "Z" not in user_countries and "Z" not in dealer_countries:
            if not set(user_countries) & set(dealer_countries):
                continue

        matched.append(user_id)
    return matched

# ==================== SERVER CONFIG HELPERS ====================

async def get_server_channel(guild_id, channel_key, fallback_id=None):
    """Get a channel for a specific server from config, with fallback."""
    config = await db_get_server_config(str(guild_id))
    channel_id = get_config_value(config, channel_key) if config else None
    if channel_id:
        channel = client.get_channel(channel_id)
        if channel:
            return channel
    # Fallback to hardcoded ID
    if fallback_id:
        return client.get_channel(fallback_id)
    return None

async def get_server_role(guild, role_key, fallback_id=None):
    """Get a role for a specific server from config, with fallback."""
    config = await db_get_server_config(str(guild.id))
    role_id = get_config_value(config, role_key) if config else None
    if role_id:
        role = guild.get_role(role_id)
        if role:
            return role
    if fallback_id:
        return guild.get_role(fallback_id)
    return None

async def get_all_server_channels(channel_key, fallback_id=None):
    """Get a specific channel from ALL servers — for broadcasting alerts."""
    servers = await db_get_all_servers()
    channels = []
    for server in servers:
        channel_id = get_config_value(server, channel_key)
        if channel_id:
            channel = client.get_channel(channel_id)
            if channel:
                channels.append(channel)
    # Also include fallback channel if not already included
    if fallback_id:
        fallback = client.get_channel(fallback_id)
        if fallback and fallback not in channels:
            channels.append(fallback)
    return channels

# ==================== RATE LIMITING ====================

COMMAND_COOLDOWNS = {
    "start": 30,      # 30 seconds between /start calls
    "alerts": 10,     # 10 seconds between /alerts calls
    "profile": 10,
    "ratedealer": 60,
    "setup": 60,
}

def check_cooldown(user_id, command):
    """Returns (is_on_cooldown, seconds_remaining)."""
    key = f"{user_id}:{command}"
    now = datetime.now(timezone.utc).timestamp()
    last = bot_state["command_cooldowns"].get(key, 0)
    cooldown = COMMAND_COOLDOWNS.get(command, 0)
    remaining = cooldown - (now - last)
    if remaining > 0:
        return True, int(remaining)
    bot_state["command_cooldowns"][key] = now
    return False, 0

def cleanup_cooldowns():
    """Remove expired cooldown entries to prevent memory leak."""
    now = datetime.now(timezone.utc).timestamp()
    max_cooldown = max(COMMAND_COOLDOWNS.values(), default=60)
    expired = [k for k, v in bot_state["command_cooldowns"].items() if now - v > max_cooldown + 10]
    for k in expired:
        del bot_state["command_cooldowns"][k]
    if expired:
        logger.debug(f"[Cooldown] Cleared {len(expired)} expired cooldown entries")

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
                logger.debug(f"Attempt {attempt+1}/{retries} — status {resp.status} for {url}")
        except Exception as e:
            logger.debug(f"Attempt {attempt+1}/{retries} — error: {e}")
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
        logger.debug(f"Error parsing HTML: {e}")
        return set()

# ==================== ALERTS ====================
async def send_alert(channel, name, url, logo_file, test=False, waf=False):
    # Check cooldown for dealers that have one set
    if not test:
        dealer_info = find_dealer(name)
        cooldown_hours = dealer_info.get("cooldown_hours", 0) if dealer_info else 0
        if cooldown_hours:
            last_alert = bot_state["dealer_cooldowns"].get(name)
            if last_alert:
                elapsed = (datetime.now(timezone.utc) - last_alert).total_seconds() / 3600
                if elapsed < cooldown_hours:
                    remaining = cooldown_hours - elapsed
                    logger.info(f"[Cooldown] Skipping {name} — {remaining:.1f}h remaining on {cooldown_hours}h cooldown.")
                    return
            bot_state["dealer_cooldowns"][name] = datetime.now(timezone.utc)

    warning = await db_get_warning(name)
    dealer_reviews = await db_get_reviews(name)
    rating, review_count = get_dealer_rating_sync(dealer_reviews)

    dealer_info = find_dealer(name)
    logger.debug(f"[Alert] Processing alert for {name} | test={test} | waf={waf}")
    flag = dealer_info.get("flag", "🌐") if dealer_info else "🌐"
    dealer_region = dealer_info.get("region", "both") if dealer_info else "both"
    title = f"🧪 TEST — {name}" if test else f"🆕 {flag} New Items at {name}!"
    description = f"This is a test notification for [{name}]({url})\n\n[**Click here to view items →**]({url})" if test else f"New items have been added to [{name}]({url})\n\n[**Click here to view new items →**]({url})"

    if warning and not test:
        description = f"⚠️ **WARNING: {warning}**\n\n" + description

    color = discord.Color.blurple() if test else (discord.Color.red() if warning else discord.Color.dark_gold())

    embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.now(timezone.utc))
    embed.add_field(name="Rating", value=stars_display(rating), inline=True)
    embed.add_field(name="Total Reviews", value=f"📝 {review_count}", inline=True)
    embed.set_footer(text="Adrian — Dealer Update")

    file = None
    if os.path.exists(logo_file):
        file = discord.File(logo_file, filename="logo.png")
        embed.set_thumbnail(url="attachment://logo.png")

    content_msg = f"<@&{WAF_ROLE_ID}> New WAF Estate listing!" if waf and not test else None

    follow_view = FollowDealerView(name)

    # Post full embed to ALL servers' updates channels
    updates_channels = await get_all_server_channels("updates_channel_id", ADRIAN_UPDATES_CHANNEL_ID)
    for updates_channel in updates_channels:
        try:
            if file and os.path.exists(logo_file):
                await updates_channel.send(content=content_msg, file=discord.File(logo_file, filename="logo.png"), embed=embed, view=follow_view)
            else:
                await updates_channel.send(content=content_msg, embed=embed, view=follow_view)
        except Exception as e:
            logger.error(f"[Alert] Failed to send to {updates_channel.guild.name}: {e}")

    # Log to private mod log channel
    try:
        log_channel = client.get_channel(PRIVATE_LOG_CHANNEL_ID)
        if log_channel:
            if file and os.path.exists(logo_file):
                await log_channel.send(file=discord.File(logo_file, filename="logo.png"), embed=embed)
            else:
                await log_channel.send(embed=embed)
    except Exception as e:
        logger.error(f"[Alert] Failed to log alert for {name}: {e}")

    # Save alert to pending DB and ping matched users across all servers
    if not test:
        try:
            dealer_eras = dealer_info.get("eras", [0]) if dealer_info else [0]
            dealer_countries = dealer_info.get("countries", ["Z"]) if dealer_info else ["Z"]
            matched_users = await db_get_users_for_dealer(dealer_region, dealer_eras, dealer_countries)
            logger.info(f"[Alert] Queuing ping for {len(matched_users)} matched user(s) for {name}")
            for uid in matched_users:
                try:
                    await db_add_pending_alert(uid, name, url, flag)
                    # Add to batch queue instead of pinging immediately
                    if uid not in bot_state["pending_pings"]:
                        bot_state["pending_pings"][uid] = []
                    bot_state["pending_pings"][uid].append({"name": name, "flag": flag, "url": url})
                except Exception as alert_err:
                    logger.debug(f"[Alert] Could not queue ping for {uid}: {alert_err}")
            # Start flush task if not already running
            if bot_state["pending_pings"] and not bot_state["ping_task_running"]:
                asyncio.create_task(flush_pending_pings())
        except Exception as e:
            logger.error(f"[Alert] Failed to send alerts for {name}: {e}")

async def cross_post_listing(thread, seller, starter_message=None):
    """Mirror a listing to all servers that accept cross-posts."""
    try:
        all_servers = await db_get_all_servers()
        already_mirrored = await db_get_mirror_servers(str(thread.id))

        # Get image from starter message if available
        image_url = None
        extra_images = 0
        if starter_message and starter_message.attachments:
            image_url = starter_message.attachments[0].url
            extra_images = len(starter_message.attachments) - 1

        # Get description snippet from starter message
        description_snippet = ""
        if starter_message and starter_message.content:
            description_snippet = starter_message.content[:300]
            if len(starter_message.content) > 300:
                description_snippet += "..."

        # Get seller ratings
        seller_avg, seller_count = await db_get_seller_rating(str(seller.id))
        points = await db_get_user_points(str(seller.id))
        warnings = await db_get_user_warnings(str(seller.id))
        rank = get_rank(points, warnings > 0)


        logger.info(f"[CrossPost] Checking {len(all_servers)} server(s) for mirror destinations")
        mirror_count = 0
        for server in all_servers:
            gid = str(server.get("guild_id", ""))
            cp = str(server.get("accept_cross_posts", "0"))
            eid = get_config_value(server, "estate_channel_id")
            logger.info(f"[CrossPost] Server {server.get('guild_name','?')} ({gid}): cross_posts={cp} estate_channel={eid}")

            # Skip original server
            if gid == str(thread.guild.id):
                logger.info(f"[CrossPost] Skipping — origin server")
                continue
            # Skip servers that don't accept cross-posts
            if cp != "1":
                logger.info(f"[CrossPost] Skipping — cross-posts disabled")
                continue
            # Skip if already mirrored to this server
            if gid in already_mirrored:
                logger.info(f"[CrossPost] Skipping — already mirrored")
                continue
            # Skip if no estate channel configured
            estate_channel_id = eid
            if not estate_channel_id:
                logger.info(f"[CrossPost] Skipping — no estate channel")
                continue

            estate_channel = client.get_channel(int(estate_channel_id))
            if not estate_channel or not isinstance(estate_channel, discord.ForumChannel):
                continue

            # Check if listing tags are blocked by this server
            if await is_listing_blocked_for_guild(thread, gid):
                logger.info(f"[CrossPost] Skipping — listing tags blocked by {server.get('guild_name','?')}")
                continue

            try:
                # Build negotiation view
                _seller_id = str(seller.id)
                _thread_id = str(thread.id)
                _item_title = thread.name
                _guild_name = thread.guild.name

                class ContactSellerView(discord.ui.View):
                    def __init__(self, seller_id, buyer_id, item_title, guild_name, thread_id):
                        super().__init__(timeout=None)
                        self.seller_id = seller_id
                        self.buyer_id = buyer_id  # None at creation, set when buyer clicks
                        self.item_title = item_title
                        self.guild_name = guild_name
                        self.thread_id = thread_id

                    @discord.ui.button(label="📨 Contact Seller", style=discord.ButtonStyle.primary, custom_id=f"contact_seller_{_seller_id}_{_thread_id}")
                    async def contact_seller(self, interaction: discord.Interaction, button: discord.ui.Button):
                        try:
                            # Check if buyer is blocked
                            if await db_is_buyer_blocked(self.seller_id, str(interaction.user.id), self.thread_id):
                                await interaction.response.send_message(
                                    "🚫 The seller has declined contact for this listing.",
                                    ephemeral=True
                                )
                                return

                            seller_user = await client.fetch_user(int(self.seller_id))
                            if not seller_user:
                                await interaction.response.send_message("⚠️ Could not find the seller.", ephemeral=True)
                                return

                            buyer = interaction.user
                            dm_embed = discord.Embed(
                                title="💬 Someone is interested in your listing!",
                                description=(
                                    f"**{buyer.display_name}** from **{interaction.guild.name}** "
                                    f"is interested in:\n\n**{self.item_title}**"
                                ),
                                color=discord.Color.dark_gold(),
                                timestamp=datetime.now(timezone.utc)
                            )
                            dm_embed.set_thumbnail(url=buyer.display_avatar.url)
                            dm_embed.add_field(name="Buyer", value=f"{buyer.mention} ({buyer.display_name})", inline=True)
                            dm_embed.set_footer(text="Adrian — Estand Marketplace")

                            class SellerResponseView(discord.ui.View):
                                def __init__(self):
                                    super().__init__(timeout=86400)  # 24 hours

                                async def _disable(self, interaction):
                                    for child in self.children:
                                        child.disabled = True
                                    await interaction.message.edit(view=self)

                                @discord.ui.button(label="✅ Accept Interest", style=discord.ButtonStyle.success)
                                async def accept(self, interaction2: discord.Interaction, button: discord.ui.Button):
                                    await self._disable(interaction2)
                                    try:
                                        buyer_user = await client.fetch_user(int(buyer.id))
                                        accept_embed = discord.Embed(
                                            title="✅ Seller is interested!",
                                            description=(
                                                f"The seller of **{self.view.item_title if hasattr(self, 'view') else _item_title}** has accepted your interest!\n\n"
                                                f"You can now DM the seller directly to negotiate."
                                            ),
                                            color=discord.Color.green()
                                        )
                                        accept_embed.add_field(name="Seller", value=f"<@{seller_user.id}> ({seller_user.display_name})", inline=True)
                                        accept_embed.set_footer(text="Adrian — Estand Marketplace")
                                        await buyer_user.send(embed=accept_embed)
                                        await interaction2.response.send_message("✅ You accepted their interest. They've been notified and can DM you now!", ephemeral=True)
                                    except discord.Forbidden:
                                        await interaction2.response.send_message("⚠️ Could not DM the buyer — they may have DMs disabled.", ephemeral=True)

                                @discord.ui.button(label="💰 Counter Offer", style=discord.ButtonStyle.primary)
                                async def counter(self, interaction2: discord.Interaction, button: discord.ui.Button):
                                    class CounterModal(discord.ui.Modal, title="Send Counter Offer"):
                                        price = discord.ui.TextInput(label="Your asking price", placeholder="e.g. $350", max_length=50)
                                        message = discord.ui.TextInput(label="Message to buyer (optional)", style=discord.TextStyle.paragraph, placeholder="Any additional details...", required=False, max_length=500)

                                        async def on_submit(self, interaction3: discord.Interaction):
                                            await self._disable_parent(interaction2)
                                            try:
                                                buyer_user = await client.fetch_user(int(buyer.id))
                                                counter_embed = discord.Embed(
                                                    title="💰 Counter Offer Received!",
                                                    description=f"The seller of **{_item_title}** has sent you a counter offer.",
                                                    color=discord.Color.gold(),
                                                    timestamp=datetime.now(timezone.utc)
                                                )
                                                counter_embed.add_field(name="Asking Price", value=self.price.value, inline=True)
                                                if self.message.value:
                                                    counter_embed.add_field(name="Message from Seller", value=self.message.value, inline=False)
                                                counter_embed.add_field(name="Seller", value=f"<@{seller_user.id}>", inline=True)
                                                counter_embed.set_footer(text="Adrian — Estand Marketplace")

                                                class BuyerResponseView(discord.ui.View):
                                                    def __init__(self):
                                                        super().__init__(timeout=86400)

                                                    async def _disable(self, interaction):
                                                        for child in self.children:
                                                            child.disabled = True
                                                        await interaction.message.edit(view=self)

                                                    @discord.ui.button(label="✅ Accept Counter", style=discord.ButtonStyle.success)
                                                    async def accept_counter(self, interaction4: discord.Interaction, button: discord.ui.Button):
                                                        await self._disable(interaction4)
                                                        try:
                                                            seller_notify = discord.Embed(
                                                                title="🎉 Buyer accepted your counter offer!",
                                                                description=f"**{buyer.display_name}** accepted your offer of **{self.price.value if hasattr(self, 'price') else 'your price'}** for **{_item_title}**!\n\nYou can now finalize the sale via DM.",
                                                                color=discord.Color.green()
                                                            )
                                                            seller_notify.add_field(name="Buyer", value=f"<@{buyer.id}> ({buyer.display_name})", inline=True)
                                                            seller_notify.set_footer(text="Adrian — Estand Marketplace")
                                                            await seller_user.send(embed=seller_notify)
                                                            await interaction4.response.send_message("✅ You accepted the counter offer! The seller has been notified.", ephemeral=True)
                                                        except discord.Forbidden:
                                                            await interaction4.response.send_message("⚠️ Could not notify the seller.", ephemeral=True)

                                                    @discord.ui.button(label="💰 Counter Back", style=discord.ButtonStyle.primary)
                                                    async def counter_back(self, interaction4: discord.Interaction, button: discord.ui.Button):
                                                        class BuyerCounterModal(discord.ui.Modal, title="Send Your Counter"):
                                                            price = discord.ui.TextInput(label="Your offer price", placeholder="e.g. $300", max_length=50)
                                                            message = discord.ui.TextInput(label="Message (optional)", style=discord.TextStyle.paragraph, required=False, max_length=500)

                                                            async def on_submit(self, interaction5: discord.Interaction):
                                                                await BuyerResponseView._disable(self, interaction4)
                                                                try:
                                                                    back_embed = discord.Embed(
                                                                        title="💰 Buyer Counter Offer",
                                                                        description=f"**{buyer.display_name}** countered your offer on **{_item_title}**.",
                                                                        color=discord.Color.gold()
                                                                    )
                                                                    back_embed.add_field(name="Their Offer", value=self.price.value, inline=True)
                                                                    if self.message.value:
           