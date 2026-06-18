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
BOT_OWNER_ID = 161988117862023169
NEW_PROFILE_CHANNEL_ID = 1515727882394144908  # Bot owner profile notification channel  # Murphy's Discord user ID
GUILD_ID = 1357352905857826887  # Main server
TEST_GUILD_ID = 1513233559878369422  # Test server
OWNER_GUILD_ID = 1357352905857826887  # Owner commands go here (main server)
IMAGE_HOST_CHANNEL_ID = 1513273241043599530  # #image-host — test server
CHANNEL_ID = 1513271593273655387  # #adrian — test server
WAF_CHANNEL_ID = None  # Deprecated — use get_all_server_channels() instead
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
    {"name": "Dutch Militaria", "flag": "🇳🇱", "region": "EU", "match": ["dutchmilitaria.com", "dutch militaria"], "logo_file": "dutch_militaria.png", "url": "https://dutchmilitaria.com/", "eras": [2, 3], "countries": ['D']},
    {"name": "Militaria Sales", "flag": "🇺🇸", "region": "NA", "match": ["militariasales.com", "militaria sales"], "logo_file": "militaria_sales.png", "url": "https://www.militariasales.com/new-item/", "eras": [2, 3, 6], "countries": ['A', 'D', 'J', 'G']},
    {"name": "Military Collectibles", "flag": "🇺🇸", "region": "NA", "match": ["info@militarycollectibles.com", "militarycollectibles.com"], "logo_file": "military_collectibles.png", "url": "https://militarycollectibles.com/shop?s=n", "eras": [2, 3], "countries": ['D']},
    {"name": "Military Collectors HQ", "flag": "🇺🇸", "region": "NA", "match": ["militarycollectorshq.com", "military collectors hq"], "logo_file": "militarycollectorshq.png", "url": "https://militarycollectorshq.com/store-catalog", "eras": [0], "countries": ['Z']},
    {"name": "Soviet Orders", "flag": "🇳🇱", "region": "NA", "match": ["sovietorders.com", "soviet orders"], "logo_file": "Soviet_Orders.png", "url": "https://sovietorders.com/new-in-store/", "eras": [2, 3], "countries": ['E']},
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
    {"name": "The Collector's Guild", "flag": "🇨🇦", "region": "NA", "match": ["germanmilitaria.com", "collector's guild", "collectors guild"], "logo_file": "germanmilitaria.png", "url": "https://www.germanmilitaria.com/Advanced.html", "eras": [0], "countries": ['Z']},
    {"name": "General Assault Militaria", "flag": "🇩🇪", "region": "NA", "match": ["generalassaultmilitaria.com", "general assault militaria", "gam"], "logo_file": "gam.png", "url": "https://www.generalassaultmilitaria.com/", "eras": [3], "countries": ['D']},
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
    {"name": "Regimentals", "flag": "🇬🇧", "region": "EU", "match": ["regimentals@emailer500.com", "regimentalsmilitaria.co.uk"], "logo_file": "Regimentals.png", "url": "https://regimentalsmilitaria.co.uk/collections/new-in", "eras": [1], "countries": ['Z'], "code": "EU-ABCD-23"},
    {"name": "Military Warehouse", "flag": "🇺🇸", "region": "NA", "match": ["john@militarywarehouse.ccsend.com", "militarywarehouse.com"], "logo_file": "Military_Warehouse.png", "url": "https://www.militarywarehouse.com/", "eras": [2, 3], "countries": ['D'], "code": "NA-D23"},
    {"name": "Virtual Grenadier", "flag": "🇺🇸", "region": "NA", "match": ["unmonitored@virtualgrenadier.com", "virtualgrenadier.com"], "logo_file": "Virutal_Grenadier.png", "url": "https://virtualgrenadier.com/salelist.php", "eras": [2, 3], "countries": ['D'], "code": "NA-23D"},
    {"name": "John Casino Militaria", "flag": "🇺🇸", "region": "NA", "match": ["Ostfront@send.mailchimpapp.com", "johncasino.com"], "logo_file": "John_Casino_Militaria.png", "url": "https://www.johncasino.com/shop.html#!/UPDATES-&-NEWLY-ADDED-ITEMS/c/13894460", "eras": [0], "countries": ["Z"]},
    {"name": "Joe's Military Collectibles", "flag": "🇺🇸", "region": "NA", "match": ["joesmilitary@emailer500.com", "joe's military collectibles", "joesmilitary"], "logo_file": "joes_military_collectibles.png", "url": "https://joesmilitary.com/shop.php", "eras": [2, 3], "countries": ["A"]},
    {"name": "Summer Vacation Militaria", "flag": "🇺🇸", "region": "NA", "match": ["svmilitaria", "summer vacation militaria", "sv militaria", "noreply@svmilitaria.com"], "logo_file": "summer_vacation_militaria.png", "url": "https://www.svmilitaria.com/NewItems.htm", "eras": [2, 3], "countries": ['A', 'H', 'D']},
    {"name": "Clements Militaria", "flag": "🇳🇱", "region": "EU", "match": ["clementsm@emailer500.com", "clements militaria", "clementsmilitaria.com"], "logo_file": "clements_militaria.png", "url": "https://clementsmilitaria.com/shop.php", "eras": [3], "countries": ['B', 'A', 'D']},
]

USMF_CHANNEL_ID = None  # Deprecated — use get_all_server_channels() instead

USMF_CATEGORIES = [
    {"name": "FS Field & Personal Gear", "emoji": "🎒", "keywords": ["field", "personal gear", "gear"]},
    {"name": "FS Knives and Other Weapons & Accessories", "emoji": "🗡️", "keywords": ["knife", "knives", "weapon", "bayonet", "blade"]},
    {"name": "FS Medals, Decorations, Ribbons, & Accessories", "emoji": "🏅", "keywords": ["medal", "decoration", "ribbon", "award"]},
    {"name": "FS Books, Photos, Ephemera, & Research Material", "emoji": "📚", "keywords": ["book", "photo", "ephemera", "research", "document", "paper"]},
    {"name": "FS Miscellaneous", "emoji": "📦", "keywords": ["misc", "miscellaneous"]},
    {"name": "FS Cloth & Metal Insignia", "emoji": "🎖️", "keywords": ["cloth", "metal", "insignia", "patch", "badge", "pin"]},
    {"name": "FS Uniforms", "emoji": "🪖", "keywords": ["uniform", "tunic", "jacket", "trousers", "coat"]},
]


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
                    msg_id TEXT PRIMARY KEY,
                    seen_at BIGINT DEFAULT 0
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS waf_thread_stats (
                    forum_url TEXT PRIMARY KEY,
                    item_title TEXT,
                    notification_count INTEGER DEFAULT 0,
                    bump_count INTEGER DEFAULT 0,
                    last_price TEXT,
                    last_notified BIGINT DEFAULT 0
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS seen_dealer_items (
                    id SERIAL PRIMARY KEY,
                    dealer_name TEXT NOT NULL,
                    item_id TEXT NOT NULL,
                    item_title TEXT,
                    seen_at BIGINT DEFAULT 0,
                    UNIQUE(dealer_name, item_id)
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
            # Safe migrations — IF NOT EXISTS prevents startup noise
            migrations = [
                "ALTER TABLE server_config ADD COLUMN IF NOT EXISTS view_all_channels INTEGER DEFAULT 0",
                "ALTER TABLE server_config ADD COLUMN IF NOT EXISTS welcome_message_id TEXT",
                "ALTER TABLE server_config ADD COLUMN IF NOT EXISTS estand_verified_role_id TEXT",
                "ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS estand_agreed INTEGER DEFAULT 0",
                "ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS created_at BIGINT DEFAULT 0",
                "ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS waf_categories TEXT DEFAULT ''",
                "ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS usmf_categories TEXT DEFAULT ''",
                "ALTER TABLE server_config ADD COLUMN IF NOT EXISTS na_role_id TEXT",
                "ALTER TABLE server_config ADD COLUMN IF NOT EXISTS eu_role_id TEXT",
                "ALTER TABLE server_config ADD COLUMN IF NOT EXISTS waf_role_id TEXT",
                "ALTER TABLE server_config ADD COLUMN IF NOT EXISTS usmf_role_id TEXT",
                "ALTER TABLE server_config ADD COLUMN IF NOT EXISTS na_updates_channel_id TEXT",
                "ALTER TABLE server_config ADD COLUMN IF NOT EXISTS eu_updates_channel_id TEXT",
                "ALTER TABLE server_config ADD COLUMN IF NOT EXISTS waf_channel_id TEXT",
                "ALTER TABLE server_config ADD COLUMN IF NOT EXISTS usmf_channel_id TEXT",
                "ALTER TABLE server_config ADD COLUMN IF NOT EXISTS estand_channel_id TEXT", 
                "ALTER TABLE server_config ADD COLUMN IF NOT EXISTS accept_cross_posts INTEGER DEFAULT 0",
                "ALTER TABLE server_config ADD COLUMN IF NOT EXISTS estate_cross_posts_channel_id TEXT",
                "ALTER TABLE server_config ADD COLUMN IF NOT EXISTS estate_sold_tag_id TEXT",
                "ALTER TABLE server_config ADD COLUMN IF NOT EXISTS estate_name TEXT",
                "ALTER TABLE server_config ADD COLUMN IF NOT EXISTS updates_channel_id TEXT",
                "ALTER TABLE server_config ADD COLUMN IF NOT EXISTS verified_role_id TEXT",
                "ALTER TABLE seen_emails ADD COLUMN IF NOT EXISTS seen_at BIGINT DEFAULT 0",
            ]
            for migration in migrations:
                try:
                    await conn.execute(migration)
                except Exception as _e:
                    logger.debug(f"[Migration] {_e}")

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
                CREATE TABLE IF NOT EXISTS user_bans (
                    user_id TEXT PRIMARY KEY,
                    reason TEXT,
                    banned_by TEXT,
                    banned_at BIGINT DEFAULT 0
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS playwright_seen_items (
                    dealer_name TEXT NOT NULL,
                    item_id TEXT NOT NULL,
                    item_title TEXT,
                    seen_at BIGINT DEFAULT 0,
                    PRIMARY KEY (dealer_name, item_id)
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
                    na_role_id TEXT,
                    eu_role_id TEXT,
                    waf_role_id TEXT,
                    usmf_role_id TEXT,
                    na_updates_channel_id TEXT,
                    eu_updates_channel_id TEXT,
                    waf_channel_id TEXT,
                    usmf_channel_id TEXT,
                    estand_channel_id TEXT,
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

# ==================== PLAYWRIGHT DEALERS ====================
PLAYWRIGHT_DEALERS = [
    {
        "name": "Time Traveler Militaria",
        "flag": "🇺🇸",
        "region": "NA",
        "url": "https://www.ttmilitaria.com/",
        "item_sel": ".product",
        "title_sel": ".woocommerce-loop-product__title",
        "id_sel": ".sku",
        "logo_file": "Time_traveler_militaria.png",
        "eras": [0],
        "countries": ["Z"],
    },
    {
        "name": "Oorlogsspullen",
        "flag": "🇳🇱",
        "region": "EU",
        "url": "https://oorlogsspullen.nl/product-categorie/new/",
        "item_sel": "li.product",
        "title_sel": ".woocommerce-loop-product__title",
        "id_sel": None,
        "logo_file": "Oorlogspullen.png",
        "eras": [3],
        "countries": ["Z"],
    },
    {
        "name": "EA Militaria",
        "flag": "🇳🇱",
        "region": "EU",
        "url": "https://www.ea-militaria.com/new-items?hideSold=1",
        "item_sel": ".product-item",
        "title_sel": ".product-item-name",
        "id_sel": None,
        "logo_file": "eamilitaria.png",
        "eras": [3],
        "countries": ["D"],
    },
    {
        "name": "OD43",
        "flag": "🇺🇸",
        "region": "NA",
        "url": "https://od43.com/product-category/z60/",
        "item_sel": "li.product",
        "title_sel": ".woocommerce-loop-product__title",
        "id_sel": None,
        "logo_file": "OD43.png",
        "eras": [0],
        "countries": ["Z"],
    },

    {
        "name": "Crain's Militaria",
        "flag": "🇧🇪",
        "region": "EU",
        "url": "https://crainsmilitaria.com/index.php?route=common/home",
        "item_sel": ".product-layout",
        "title_sel": ".caption h4 a",
        "id_sel": None,
        "logo_file": "Crains_Militaria.png",
        "eras": [0],
        "countries": ["Z"],
    },

    {
        "name": "Past Glories Militaria",
        "extra_wait_ms": 5000,
        "flag": "🇬🇧",
        "region": "EU",
        "url": "https://www.pastgloriesmilitaria.com/shop.php",
        "item_sel": "div.c500item, div[class*='item'], .shop-item, .product-list-item",
        "title_sel": "a, h3, h4, .title",
        "id_sel": None,
        "logo_file": "Past_Glories_Militaria.png",
        "eras": [0],
        "countries": ["Z"],
    },
    {
        "name": "The Old Brigade",
        "extra_wait_ms": 5000,
        "flag": "🇬🇧",
        "region": "EU",
        "url": "https://www.theoldbrigade.co.uk/shop.php?q=&d=2&c=all&hide=unavailabe",
        "item_sel": "div.c500item, div[class*='item'], .shop-item, .product-list-item",
        "title_sel": "a, h3, h4, .title",
        "id_sel": None,
        "logo_file": "The_Old_Brigade.png",
        "eras": [0],
        "countries": ["Z"],
    },
    {
        "name": "Overlook Militaria Surplus",
        "flag": "🇺🇸",
        "region": "NA",
        "url": "https://wwiigimilitarysurplus.com/shop.php?p=t|hhh||",
        "item_sel": "table tr",
        "title_sel": "td:nth-child(2) a, td a, td b",
        "extra_wait_ms": 4000,
        "id_sel": None,
        "logo_file": "Overlook_Militaria_Surplus.png",
        "eras": [0],
        "countries": ["Z"],
    },
    {
        "name": "Summer Vacation Militaria",
        "flag": "🇺🇸",
        "region": "NA",
        "url": "https://www.svmilitaria.com/NewItems.htm",
        "item_sel": "table tr",
        "title_sel": "td:nth-child(2) b, td b",
        "id_sel": None,
        "logo_file": "summer_vacation_militaria.png",
        "eras": [0],
        "countries": ["Z"],
    },
    {
        "name": "Griffin Militaria",
        "flag": "🇺🇸",
        "region": "NA",
        "url": "https://griffinmilitaria.com/product-category/united-states/",  # primary URL (unused, pages overrides)
        "item_sel": "li.product",
        "title_sel": ".woocommerce-loop-product__title",
        "id_sel": None,
        "logo_file": "Griffin_Militaria.png",
        "eras": [0],
        "countries": ["Z"],
        "pages": [
            # United States
            "https://griffinmilitaria.com/product-category/united-states/civil-war/accoutrements/",
            "https://griffinmilitaria.com/product-category/united-states/civil-war/civil-war-span-am-war-veterans/",
            "https://griffinmilitaria.com/product-category/united-states/civil-war/edged_weapons/",
            "https://griffinmilitaria.com/product-category/united-states/civil-war/miscellaneous-civil-war/",
            "https://griffinmilitaria.com/product-category/united-states/civil-war/photos-paper/",
            "https://griffinmilitaria.com/product-category/united-states/pre-wwi/",
            "https://griffinmilitaria.com/product-category/united-states/world-war-i/us-wwi-chevrons/",
            "https://griffinmilitaria.com/product-category/united-states/world-war-i/collar-disks/",
            "https://griffinmilitaria.com/product-category/united-states/world-war-i/dog-tags/",
            "https://griffinmilitaria.com/product-category/united-states/world-war-i/enlisted-squadron-patches/",
            "https://griffinmilitaria.com/product-category/united-states/world-war-i/us-wwi-field-gear/",
            "https://griffinmilitaria.com/product-category/united-states/world-war-i/us-wwi-headgear/",
            "https://griffinmilitaria.com/product-category/united-states/world-war-i/medals/",
            "https://griffinmilitaria.com/product-category/united-states/world-war-i/us-wwi-metal-insignia/",
            "https://griffinmilitaria.com/product-category/united-states/world-war-i/miscellaneous-wwi-items/",
            "https://griffinmilitaria.com/product-category/united-states/world-war-i/patches/",
            "https://griffinmilitaria.com/product-category/united-states/world-war-i/us-wwi-uniforms/",
            "https://griffinmilitaria.com/product-category/united-states/world-war-ii/us-wwii-chevrons/",
            "https://griffinmilitaria.com/product-category/united-states/world-war-ii/us-wwii-cloth-insignia/",
            "https://griffinmilitaria.com/product-category/united-states/world-war-ii/crest-drop-in/",
            "https://griffinmilitaria.com/product-category/united-states/world-war-ii/us-wwii-field-gear/",
            "https://griffinmilitaria.com/product-category/united-states/world-war-ii/us-wwii-headgear/",
            "https://griffinmilitaria.com/product-category/united-states/world-war-ii/medal-ribbons/",
            "https://griffinmilitaria.com/product-category/united-states/world-war-ii/us-wwii-metal-insignia/",
            "https://griffinmilitaria.com/product-category/united-states/world-war-ii/miscellaneous-wwii-items-world-war-ii/",
            "https://griffinmilitaria.com/product-category/united-states/world-war-ii/navy-rates/",
            "https://griffinmilitaria.com/product-category/united-states/world-war-ii/posters/",
            "https://griffinmilitaria.com/product-category/united-states/world-war-ii/sweetheart-homefront/",
            "https://griffinmilitaria.com/product-category/united-states/world-war-ii/us-wwii-uniforms/",
            "https://griffinmilitaria.com/product-category/united-states/world-war-ii/us-paper/",
            "https://griffinmilitaria.com/product-category/united-states/world-war-ii/wings/",
            "https://griffinmilitaria.com/product-category/united-states/cold-war-steins/",
            # Japan
            "https://griffinmilitaria.com/product-category/japan/japanese-medals/",
            "https://griffinmilitaria.com/product-category/japan/japanese-insignia/",
            "https://griffinmilitaria.com/product-category/japan/japanese-head-gear/",
            "https://griffinmilitaria.com/product-category/japan/japanese-flags-and-banners/",
            "https://griffinmilitaria.com/product-category/japan/Overcoats/",
            "https://griffinmilitaria.com/product-category/japan/japanese-uniforms/shirts/",
            "https://griffinmilitaria.com/product-category/japan/Tunics/",
            "https://griffinmilitaria.com/product-category/japan/japanese-uniforms/trousers/",
            "https://griffinmilitaria.com/product-category/japan/japanese-edged-weapons/",
            "https://griffinmilitaria.com/product-category/japan/japanese-field-gear/",
            "https://griffinmilitaria.com/product-category/japan/japanese-personal-items/",
            "https://griffinmilitaria.com/product-category/japan/japanese-cups/",
            "https://griffinmilitaria.com/product-category/japan/japanese-paper/",
            "https://griffinmilitaria.com/product-category/japan/miscellaneous-japanese-militaria/",
            # Germany WWI
            "https://griffinmilitaria.com/product-category/germany/germany-wwi/edged-weapons-germany-wwi/",
            "https://griffinmilitaria.com/product-category/germany/germany-wwi/headgear/",
            "https://griffinmilitaria.com/product-category/germany/germany-wwi/imperial-german-steins/",
            "https://griffinmilitaria.com/product-category/germany/germany-wwi/medals-decorations/",
            "https://griffinmilitaria.com/product-category/germany/germany-wwi/Miscellaneous-WWI-German-Items/",
            # Germany WWII
            "https://griffinmilitaria.com/product-category/germany/germany-wwii/belts-belt-buckles/",
            "https://griffinmilitaria.com/product-category/germany/germany-wwii/germany-wwii-cloth-insignia/",
            "https://griffinmilitaria.com/product-category/germany/germany-wwii/documents-and-photographs/",
            "https://griffinmilitaria.com/product-category/germany/germany-wwii/edged-weapons/",
            "https://griffinmilitaria.com/product-category/germany/germany-wwii/flags-banners/",
            "https://griffinmilitaria.com/product-category/germany/germany-wwii/germany-wwii-headgear/",
            "https://griffinmilitaria.com/product-category/germany/germany-wwii/medals-badges/",
            "https://griffinmilitaria.com/product-category/germany/germany-wwii/germany-wwii-metal-insignia/",
            "https://griffinmilitaria.com/product-category/germany/germany-wwii/miscellaneous-wwii-items/",
            "https://griffinmilitaria.com/product-category/germany/germany-wwii/ribbon-bars/",
            "https://griffinmilitaria.com/product-category/germany/germany-wwii/stickpins/",
            "https://griffinmilitaria.com/product-category/germany/germany-wwii/tinnies/",
            "https://griffinmilitaria.com/product-category/germany/germany-wwii/third-reich-steins/",
            # Other
            "https://griffinmilitaria.com/product-category/militaria-of-other-countries/",
            # Vietnam
            "https://griffinmilitaria.com/product-category/vietnam-war/beercan-di/",
            "https://griffinmilitaria.com/product-category/vietnam-war/headgear-vietnam-war/",
            "https://griffinmilitaria.com/product-category/vietnam-war/medals-vietnam-war/",
            "https://griffinmilitaria.com/product-category/vietnam-war/miscellaneous/",
            "https://griffinmilitaria.com/product-category/vietnam-war/patches-insignia/",
            "https://griffinmilitaria.com/product-category/vietnam-war/uniforms/",
            # Photos & Books
            "https://griffinmilitaria.com/product-category/military-photographs/american-military-photos/",
            "https://griffinmilitaria.com/product-category/military-photographs/german-military-photos/",
            "https://griffinmilitaria.com/product-category/military-photographs/japanese-military-photos/",
            "https://griffinmilitaria.com/product-category/military-photographs/other-countries-military-photos/",
            "https://griffinmilitaria.com/product-category/reference-books/",
        ],
    },
    {
        "name": "WarEra Militaria",
        "flag": "🇵🇱",
        "region": "EU",
        "url": "https://warera-militaria.com/katalog/filter/icons=3/",
        "item_sel": ".product-item, .catalog-item, li.product",
        "title_sel": ".product-title, .item-title, .woocommerce-loop-product__title, h2, h3",
        "id_sel": None,
        "logo_file": "WarEra_Militaria.png",
        "eras": [0],
        "countries": ["Z"],
    },
    {
        "name": "SMG War Relics",
        "flag": "🇺🇸",
        "region": "NA",
        "url": "https://war-relics.com/shop/",
        "item_sel": "li.product",
        "title_sel": ".woocommerce-loop-product__title",
        "id_sel": None,
        "logo_file": "smg_war_relics.png",
        "eras": [0],
        "countries": ["Z"],
    },
]

PLAYWRIGHT_CHECK_INTERVAL = 600  # 10 minutes

# ==================== DATABASE FUNCTIONS ====================

bot_state = {
    "paused": False,
    "force_rescan": False,
    "last_check": None,
    "startup_time": None,
    "alert_count": 0,
    "error_count": 0,
    "dealer_cooldowns": {},
    "command_cooldowns": {},
    "pending_pings": {},
    "ping_task_running": False,
    "waf_notification_count": 0,
    "usmf_notification_count": 0,
    "griffin_buffer": [],
    "griffin_timer": None,
}

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
        await conn.execute("INSERT INTO seen_emails (msg_id, seen_at) VALUES ($1, $2) ON CONFLICT DO NOTHING", msg_id, int(datetime.now(timezone.utc).timestamp()))

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

# ==================== WAF THREAD STATS ====================

async def db_increment_waf_thread(forum_url, item_title, price_str="", is_bump=False):
    """Track notification and bump counts per WAF thread."""
    now = int(datetime.now(timezone.utc).timestamp())
    async with client.db.acquire() as conn:
        if is_bump:
            await conn.execute(
                """INSERT INTO waf_thread_stats (forum_url, item_title, bump_count, last_price, last_notified)
                   VALUES ($1, $2, 1, $3, $4)
                   ON CONFLICT (forum_url) DO UPDATE SET
                   bump_count = waf_thread_stats.bump_count + 1,
                   last_price = COALESCE(NULLIF($3, \'\'), waf_thread_stats.last_price),
                   last_notified = $4""",
                forum_url, item_title, price_str, now
            )
        else:
            await conn.execute(
                """INSERT INTO waf_thread_stats (forum_url, item_title, notification_count, last_price, last_notified)
                   VALUES ($1, $2, 1, $3, $4)
                   ON CONFLICT (forum_url) DO UPDATE SET
                   notification_count = waf_thread_stats.notification_count + 1,
                   last_price = COALESCE(NULLIF($3, \'\'), waf_thread_stats.last_price),
                   last_notified = $4""",
                forum_url, item_title, price_str, now
            )

async def db_get_waf_thread_stats(forum_url):
    """Get stats for a WAF thread."""
    async with client.db.acquire() as conn:
        return await conn.fetchrow(
            "SELECT notification_count, bump_count, last_price FROM waf_thread_stats WHERE forum_url=$1",
            forum_url
        )

# ==================== SEEN DEALER ITEMS ====================

import re as _re

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
        try:
            role = guild.get_role(int(role_id))
            if role:
                return role
        except (ValueError, TypeError):
            pass
    if fallback_id:
        return guild.get_role(int(fallback_id))
    return None

# Map channel keys to their Discord channel names for fallback lookup
CHANNEL_NAME_MAP = {
    "updates_channel_id": "dealer-updates",
    "na_updates_channel_id": "na-dealer-updates",
    "eu_updates_channel_id": "eu-dealer-updates",
    "waf_channel_id": "waf-updates",
    "usmf_channel_id": "usmf-updates",
    "channel_id": "adrian",
    "estand_channel_id": "estand",
}

async def get_all_server_channels(channel_key, fallback_id=None):
    """Get a specific channel from ALL servers — for broadcasting alerts."""
    servers = await db_get_all_servers()
    channels = []
    channel_name = CHANNEL_NAME_MAP.get(channel_key)

    for server in servers:
        guild_id = get_config_value(server, "guild_id")
        channel_id = get_config_value(server, channel_key)

        # Try by saved ID first
        if channel_id:
            channel = client.get_channel(int(channel_id))
            if channel:
                channels.append(channel)
                continue

        # Fall back to searching by name in the guild
        if channel_name and guild_id:
            guild = client.get_guild(int(guild_id))
            if guild:
                ch = discord.utils.get(guild.text_channels, name=channel_name)
                if not ch:
                    ch = discord.utils.get(guild.forums, name=channel_name)
                if ch:
                    channels.append(ch)
                    # Save it for next time
                    await db_save_server_config(str(guild_id), **{channel_key: str(ch.id)})
                    logger.debug(f"[Channels] Found #{channel_name} by name in {guild.name}")

    # Also search all connected guilds not in DB
    if channel_name:
        for guild in client.guilds:
            already = any(c.guild.id == guild.id for c in channels)
            if not already:
                ch = discord.utils.get(guild.text_channels, name=channel_name)
                if ch and ch not in channels:
                    channels.append(ch)

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
    return DEALERS + EMAIL_DEALERS + PLAYWRIGHT_DEALERS

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
async def send_alert(name, url, logo_file, test=False, waf=False):
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

    content_msg = None  # No pings in channel — DMs only for followers/subscribers

    follow_view = FollowDealerView(name)

    # Route to correct channels based on dealer region
    # Always post to #dealer-updates (all dealers)
    all_channels = await get_all_server_channels("updates_channel_id")
    # Post to #na-dealer-updates if NA dealer
    if dealer_region.upper() in ("NA", "BOTH"):
        na_channels = await get_all_server_channels("na_updates_channel_id")
        all_channels = list({c.id: c for c in all_channels + na_channels}.values())
    # Post to #eu-dealer-updates if EU dealer
    if dealer_region.upper() in ("EU", "BOTH"):
        eu_channels = await get_all_server_channels("eu_updates_channel_id")
        all_channels = list({c.id: c for c in all_channels + eu_channels}.values())

    for updates_channel in all_channels:
        try:
            if file and os.path.exists(logo_file):
                await updates_channel.send(file=discord.File(logo_file, filename="logo.png"), embed=embed, view=follow_view, allowed_mentions=discord.AllowedMentions.none())
            else:
                await updates_channel.send(embed=embed, view=follow_view, allowed_mentions=discord.AllowedMentions.none())
            logger.info(f"[Alert] {name} → #{updates_channel.name} in {updates_channel.guild.name}")
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
        extra_image_urls = []
        extra_images = 0
        if starter_message and starter_message.attachments:
            image_url = starter_message.attachments[0].url
            extra_image_urls = [a.url for a in starter_message.attachments[1:]]
            extra_images = len(extra_image_urls)

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
                                                                        back_embed.add_field(name="Message", value=self.message.value, inline=False)
                                                                    back_embed.set_footer(text="Adrian — Estand Marketplace")

                                                                    # Give seller buttons to continue negotiating
                                                                    class SellerCounterResponseView(discord.ui.View):
                                                                        def __init__(self):
                                                                            super().__init__(timeout=86400)

                                                                        async def _disable(self2, interaction_x):
                                                                            for child in self2.children:
                                                                                child.disabled = True
                                                                            try:
                                                                                await interaction_x.message.edit(view=self2)
                                                                            except Exception: pass

                                                                        @discord.ui.button(label="✅ Accept", style=discord.ButtonStyle.success)
                                                                        async def accept(self2, interaction_x: discord.Interaction, btn: discord.ui.Button):
                                                                            await self2._disable(interaction_x)
                                                                            try:
                                                                                accept_embed = discord.Embed(
                                                                                    title="🎉 Seller accepted your counter offer!",
                                                                                    description=f"**{seller_user.display_name}** accepted your offer of **{self.price.value}** for **{_item_title}**!\n\nThey will be in touch to finalize the sale.",
                                                                                    color=discord.Color.green()
                                                                                )
                                                                                accept_embed.set_footer(text="Adrian — Estand Marketplace")
                                                                                await buyer_user.send(embed=accept_embed)
                                                                                await interaction_x.response.send_message("✅ You accepted the counter! The buyer has been notified.", ephemeral=True)
                                                                            except discord.Forbidden:
                                                                                await interaction_x.response.send_message("⚠️ Could not notify the buyer.", ephemeral=True)

                                                                        @discord.ui.button(label="💰 Counter", style=discord.ButtonStyle.primary)
                                                                        async def counter_again(self2, interaction_x: discord.Interaction, btn: discord.ui.Button):
                                                                            class SellerCounterAgainModal(discord.ui.Modal, title="Send Counter Offer"):
                                                                                price = discord.ui.TextInput(label="Your price", placeholder="e.g. $350", max_length=50)
                                                                                message = discord.ui.TextInput(label="Message (optional)", style=discord.TextStyle.paragraph, required=False, max_length=500)

                                                                                async def on_submit(self3, interaction_y: discord.Interaction):
                                                                                    await self2._disable(interaction_x)
                                                                                    try:
                                                                                        new_counter_embed = discord.Embed(
                                                                                            title="💰 Counter Offer Received!",
                                                                                            description=f"The seller of **{_item_title}** has sent you a counter offer.",
                                                                                            color=discord.Color.gold()
                                                                                        )
                                                                                        new_counter_embed.add_field(name="Asking Price", value=self3.price.value, inline=True)
                                                                                        if self3.message.value:
                                                                                            new_counter_embed.add_field(name="Message", value=self3.message.value, inline=False)
                                                                                        new_counter_embed.add_field(name="Seller", value=f"<@{seller_user.id}>", inline=True)
                                                                                        new_counter_embed.set_footer(text="Adrian — Estand Marketplace")
                                                                                        await buyer_user.send(embed=new_counter_embed, view=BuyerResponseView())
                                                                                        await interaction_y.response.send_message("✅ Counter sent to the buyer!", ephemeral=True)
                                                                                    except discord.Forbidden:
                                                                                        await interaction_y.response.send_message("⚠️ Could not DM the buyer.", ephemeral=True)

                                                                            await interaction_x.response.send_modal(SellerCounterAgainModal())

                                                                        @discord.ui.button(label="❌ Decline", style=discord.ButtonStyle.danger)
                                                                        async def decline(self2, interaction_x: discord.Interaction, btn: discord.ui.Button):
                                                                            await self2._disable(interaction_x)
                                                                            try:
                                                                                dec_embed = discord.Embed(
                                                                                    title="❌ Seller declined your counter offer",
                                                                                    description=f"**{seller_user.display_name}** passed on your counter for **{_item_title}**.",
                                                                                    color=discord.Color.red()
                                                                                )
                                                                                dec_embed.set_footer(text="Adrian — Estand Marketplace")
                                                                                await buyer_user.send(embed=dec_embed)
                                                                                await interaction_x.response.send_message("You declined the counter. The buyer has been notified.", ephemeral=True)
                                                                            except discord.Forbidden:
                                                                                await interaction_x.response.send_message("⚠️ Could not notify the buyer.", ephemeral=True)

                                                                    await seller_user.send(embed=back_embed, view=SellerCounterResponseView())
                                                                    await interaction5.response.send_message("✅ Your counter has been sent to the seller!", ephemeral=True)
                                                                except discord.Forbidden:
                                                                    await interaction5.response.send_message("⚠️ Could not reach the seller.", ephemeral=True)

                                                        await interaction4.response.send_modal(BuyerCounterModal())

                                                    @discord.ui.button(label="❌ Decline", style=discord.ButtonStyle.danger)
                                                    async def decline_counter(self, interaction4: discord.Interaction, button: discord.ui.Button):
                                                        await self._disable(interaction4)
                                                        try:
                                                            decline_embed = discord.Embed(
                                                                title="❌ Buyer declined your counter offer",
                                                                description=f"**{buyer.display_name}** passed on your counter offer for **{_item_title}**.",
                                                                color=discord.Color.red()
                                                            )
                                                            decline_embed.set_footer(text="Adrian — Estand Marketplace")
                                                            await seller_user.send(embed=decline_embed)
                                                            await interaction4.response.send_message("You declined the counter offer. The seller has been notified.", ephemeral=True)
                                                        except discord.Forbidden:
                                                            await interaction4.response.send_message("⚠️ Could not notify the seller.", ephemeral=True)

                                                await buyer_user.send(embed=counter_embed, view=BuyerResponseView())
                                                await interaction3.response.send_message("✅ Your counter offer has been sent!", ephemeral=True)
                                            except discord.Forbidden:
                                                await interaction3.response.send_message("⚠️ Could not DM the buyer.", ephemeral=True)

                                        async def _disable_parent(self, original_interaction):
                                            try:
                                                for child in original_interaction.message.components:
                                                    pass
                                            except Exception:
                                                pass

                                    await interaction2.response.send_modal(CounterModal())

                                @discord.ui.button(label="💬 Send Message", style=discord.ButtonStyle.secondary)
                                async def send_message_btn(self, interaction2: discord.Interaction, button: discord.ui.Button):
                                    class MessageModal(discord.ui.Modal, title="Send Message to Buyer"):
                                        message = discord.ui.TextInput(label="Your message", style=discord.TextStyle.paragraph, placeholder="Type your message to the buyer...", max_length=1000)

                                        async def on_submit(self, interaction3: discord.Interaction):
                                            try:
                                                buyer_user = await client.fetch_user(int(buyer.id))
                                                msg_embed = discord.Embed(
                                                    title=f"💬 Message from the seller of {_item_title}",
                                                    description=self.message.value,
                                                    color=discord.Color.dark_gold(),
                                                    timestamp=datetime.now(timezone.utc)
                                                )
                                                msg_embed.add_field(name="Seller", value=f"<@{seller_user.id}>", inline=True)
                                                msg_embed.set_footer(text="Adrian — Estand Marketplace")
                                                await buyer_user.send(embed=msg_embed)
                                                await interaction3.response.send_message("✅ Message sent to the buyer!", ephemeral=True)
                                            except discord.Forbidden:
                                                await interaction3.response.send_message("⚠️ Could not DM the buyer.", ephemeral=True)

                                    await interaction2.response.send_modal(MessageModal())

                                @discord.ui.button(label="🚫 Block", style=discord.ButtonStyle.danger)
                                async def block_buyer(self, interaction2: discord.Interaction, button: discord.ui.Button):
                                    await self._disable(interaction2)
                                    await db_block_buyer(str(seller_user.id), str(buyer.id), _thread_id)
                                    try:
                                        buyer_user = await client.fetch_user(int(buyer.id))
                                        block_embed = discord.Embed(
                                            title="🚫 Seller declined contact",
                                            description=f"The seller of **{_item_title}** has declined further contact for this listing.",
                                            color=discord.Color.red()
                                        )
                                        block_embed.set_footer(text="Adrian — Estand Marketplace")
                                        await buyer_user.send(embed=block_embed)
                                    except discord.Forbidden:
                                        pass
                                    await interaction2.response.send_message("🚫 Buyer has been blocked from contacting you about this listing.", ephemeral=True)
                                    logger.info(f"[Negotiation] Seller {seller_user.id} blocked buyer {buyer.id} on listing {_thread_id}")

                            await seller_user.send(embed=dm_embed, view=SellerResponseView())
                            await interaction.response.send_message(
                                "✅ The seller has been notified! They'll respond to you via DM.",
                                ephemeral=True
                            )
                            logger.info(f"[Negotiation] Buyer {buyer.id} contacted seller {seller_user.id} about listing {_thread_id}")
                        except discord.Forbidden:
                            await interaction.response.send_message("⚠️ Could not contact the seller — they may have DMs disabled.", ephemeral=True)
                        except Exception as e:
                            logger.error(f"[Negotiation] Contact seller error: {e}\n{traceback.format_exc()}")
                            await interaction.response.send_message("⚠️ Something went wrong.", ephemeral=True)

                # Build mirror embed
                guild_name = thread.guild.name

                # Description
                desc_parts = []
                if description_snippet:
                    desc_parts.append(f"{description_snippet}")
                desc_parts.append(f"")
                desc_parts.append(f"🏪 **{seller.display_name}** — {rank}")
                desc_parts.append(f"{format_stars(seller_avg)}  •  {seller_count} sale(s)")
                desc_parts.append(f"")
                desc_parts.append(f"📍 *Cross-posted from **{guild_name}***")

                mirror_embed = discord.Embed(
                    title=thread.name,
                    description="\n".join(desc_parts),
                    color=discord.Color.from_rgb(180, 140, 60),
                    timestamp=datetime.now(timezone.utc)
                )

                # Image
                if image_url:
                    mirror_embed.set_image(url=image_url)
                # Extra images posted as separate messages below

                mirror_embed.set_footer(
                    text="Adrian Estand  •  Cross-Posted Listing",
                    icon_url="https://cdn.discordapp.com/attachments/1513273241043599530/1513273241043599530/discord_pfp.png"
                )

                # Post to destination forum channel
                tags_to_apply = []
                for tag in estate_channel.available_tags:
                    if tag.name.lower() == "cross-posted":
                        tags_to_apply.append(tag)
                        break

                mirror_thread, _ = await estate_channel.create_thread(
                    name=f"🌐 {thread.name}",
                    content="",
                    embed=mirror_embed,
                    applied_tags=tags_to_apply
                )

                # Post extra images if any
                if extra_image_urls:
                    for img_url in extra_image_urls[:4]:  # Max 4 extra images
                        try:
                            extra_embed = discord.Embed(color=discord.Color.dark_gold())
                            extra_embed.set_image(url=img_url)
                            await mirror_thread.send(embed=extra_embed)
                        except Exception as ie:
                            logger.debug(f"[CrossPost] Could not post extra image: {ie}")

                # Save mirror to DB
                await db_save_cross_post_mirror(
                    str(thread.id), str(thread.guild.id), str(seller.id),
                    str(server["guild_id"]), str(estate_channel.id),
                    thread.name, str(mirror_thread.id)
                )

                # Action buttons — no extra embed needed
                await mirror_thread.send(view=SellerProfileView(str(seller.id)))


                mirror_count += 1
                bot_state["cross_post_count"] += 1
                logger.info(f"[CrossPost] Mirrored \'{thread.name}\' to {estate_channel.guild.name}")

            except Exception as e:
                logger.error(f"[CrossPost] Failed to mirror to {server.get('guild_name', 'unknown')}: {e}")

        if mirror_count > 0:
            logger.info(f"[CrossPost] \'{thread.name}\' mirrored to {mirror_count} server(s)")
        return mirror_count

    except Exception as e:
        logger.error(f"[CrossPost] cross_post_listing error: {e}\n{traceback.format_exc()}")
        return 0

async def flush_pending_pings():
    """Send batched alert pings — groups multiple dealer alerts into one message per user."""
    if bot_state["ping_task_running"]:
        return
    bot_state["ping_task_running"] = True
    try:
        await asyncio.sleep(30)  # Wait 30 seconds to batch alerts
        if not bot_state["pending_pings"]:
            return

        pings = bot_state["pending_pings"].copy()
        bot_state["pending_pings"] = {}

        servers = await db_get_all_servers()
        for uid, alerts in pings.items():
            try:
                # Build DM message
                if len(alerts) == 1:
                    a = alerts[0]
                    embed = discord.Embed(
                        title=f"🆕 {a['flag']} {a['name']} has new items!",
                        description=f"[View listings]({a['url']})" if a.get('url') else "Check the dealer channel for new listings.",
                        color=discord.Color.dark_gold()
                    )
                else:
                    dealer_list = "\n".join([f"{a['flag']} **{a['name']}**" for a in alerts])
                    embed = discord.Embed(
                        title=f"🆕 {len(alerts)} dealers have new items!",
                        description=dealer_list,
                        color=discord.Color.dark_gold()
                    )
                embed.set_footer(text="Adrian — Dealer Alert | Click 🔕 on any alert to unfollow")
                user = await client.fetch_user(int(uid))
                await user.send(embed=embed)
                logger.debug(f"[Alert] DM sent to {uid} for {len(alerts)} dealer(s)")
            except discord.Forbidden:
                logger.debug(f"[Alert] Could not DM {uid} — DMs disabled")
            except Exception as e:
                logger.debug(f"[Alert] Batch ping failed for {uid}: {e}")
    finally:
        bot_state["ping_task_running"] = False

async def check_dealer(session, dealer, seen):
    name = dealer["name"]
    url = dealer["url"]
    logo_file = os.path.join(SCRIPT_DIR, "logos", dealer["logo_file"])
    selector = dealer["item_selector"]
    base_url = dealer["base_url"]

    html_bytes = await fetch_page(session, url)
    if not html_bytes:
        logger.warning(f"[{name}] Could not fetch page.")
        return

    current_items = extract_item_links(html_bytes, selector, base_url)
    items_key = name + "_items"

    if not current_items:
        logger.debug(f"[{name}] No items found with selector '{selector}' — skipping.")
        return

    old_items = set(seen.get(items_key, []))
    if not old_items:
        seen[items_key] = list(current_items)
        logger.info(f"[{name}] First check — saved {len(current_items)} items as baseline.")
        return

    new_items = current_items - old_items
    if new_items:
        logger.info(f"[{name}] {len(new_items)} NEW ITEM(S) DETECTED!")
        seen[items_key] = list(current_items)
        await db_increment_stat(name)
        await send_alert(name, url, logo_file)
    else:
        logger.debug(f"[{name}] No new items ({len(current_items)} items unchanged).")

def _fetch_gmail_sync():
    """Synchronous Gmail IMAP fetch — checks all folders including Promotions, Updates, Social tabs."""
    raw_emails = []
    # All Gmail folders/tabs to check
    folders = [
        "INBOX",
        "[Gmail]/Spam",
        '"[Gmail]/Promotions"',
        '"[Gmail]/Updates"',
        '"[Gmail]/Social"',
        '"[Gmail]/Forums"',
    ]
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", timeout=20)
        mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)

        seen_ids = set()
        for folder in folders:
            try:
                status, _ = mail.select(folder, readonly=False)
                if status != "OK":
                    continue
                _, messages = mail.search(None, "UNSEEN")
                email_ids = messages[0].split()
                new_in_folder = 0
                for eid in email_ids:
                    # Avoid duplicates across folders
                    _, uid_data = mail.fetch(eid, "(UID)")
                    uid = uid_data[0].decode() if uid_data and uid_data[0] else str(eid)
                    if uid in seen_ids:
                        continue
                    seen_ids.add(uid)
                    _, msg_data = mail.fetch(eid, "(RFC822)")
                    if msg_data and msg_data[0] and msg_data[0][1]:
                        raw_emails.append(msg_data[0][1])
                        new_in_folder += 1
                if new_in_folder > 0:
                    logger.info(f"[Gmail] Found {new_in_folder} unread email(s) in {folder}")
            except Exception as fe:
                logger.debug(f"[Gmail] Could not read folder {folder}: {fe}")
                continue

        try:
            mail.logout()
        except Exception:
            pass
    except Exception as e:
        logger.error(f"[Gmail] IMAP error: {e}")
    return raw_emails

async def check_gmail_async():
    triggered = []
    try:
        # Run blocking IMAP in a thread to avoid blocking the event loop
        raw_emails = await asyncio.to_thread(_fetch_gmail_sync)
        logger.info(f"[Gmail] Found {len(raw_emails)} unread email(s).")
        for raw in raw_emails:
            msg = email.message_from_bytes(raw)
            msg_id = msg.get("Message-ID", "")
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
                # Match on sender email address only — no subject/keyword matching needed
                dealer_matched = False
                for keyword in dealer["match"]:
                    if keyword.lower() in sender.lower():
                        dealer_matched = True
                        break
                if dealer_matched:
                    logger.info(f"[Gmail] Matched dealer: {dealer['name']} (sender: {sender})")
                    triggered.append((dealer, subject, body))
                    matched = True
                    break
            if not matched:
                logger.info(f"[Gmail] No dealer matched for sender: {sender} | Subject: {subject}")
    except Exception as e:
        logger.error(f"[Gmail] Error checking email: {e}\n{traceback.format_exc()}")
    return triggered

# ==================== BACKGROUND TASKS ====================
async def health_log_task():
    """Log bot health every 30 minutes so Railway logs stay active."""
    await client.wait_until_ready()
    while not client.is_closed():
        try:
            uptime = ""
            if bot_state.get("startup_time"):
                delta = datetime.now(timezone.utc) - bot_state["startup_time"]
                h, rem = divmod(int(delta.total_seconds()), 3600)
                m, s = divmod(rem, 60)
                uptime = f"{h}h {m}m"
            mem = psutil.Process().memory_info().rss / 1024 / 1024
            guilds = len(client.guilds)
            errors = bot_state.get("error_count", 0)
            alerts = bot_state.get("alert_count", 0)
            logger.info(
                f"[Health] ✅ Online | Uptime: {uptime} | "
                f"Guilds: {guilds} | Mem: {mem:.0f}MB | "
                f"Alerts: {alerts} | Errors: {errors}"
            )
        except Exception as e:
            logger.debug(f"[Health] Health log error: {e}")
        await asyncio.sleep(1800)  # Every 30 minutes

async def onboarding_reminder_task():
    """Every 24 hours, remind users who started /start but never finished."""
    await client.wait_until_ready()
    await asyncio.sleep(3600)  # Wait 1 hour after startup before first check
    while not client.is_closed():
        try:
            logger.info("[Reminder] Running onboarding reminder check")
            async with client.db.acquire() as conn:
                # Find users with a row in user_preferences but no region set
                rows = await conn.fetch(
                    """SELECT user_id FROM user_preferences
                       WHERE region IS NULL
                       AND created_at IS NOT NULL
                       AND created_at < $1""",
                    int((datetime.now(timezone.utc).timestamp())) - 86400  # older than 24 hours
                )

            reminded = 0
            for row in rows:
                try:
                    user = await client.fetch_user(int(row["user_id"]))
                    if user:
                        embed = discord.Embed(
                            title="👋 Hey! You never finished setting up your profile.",
                            description=(
                                "You started creating your Adrian collector profile but didn\'t finish!\n\n"
                                "It only takes 2 minutes and unlocks:\n"
                                "📬 **Personalized dealer alerts** — only items matching your interests\n"
                                "🏪 **Estand marketplace** — buy and sell with verified collectors\n"
                                "⭐ **Global reputation** — build your collector rank across every Adrian server\n\n"
                                "Head back to the **#adrian** channel on any server and click **👋 Get Started** to finish!"
                            ),
                            color=discord.Color.dark_gold()
                        )
                        embed.set_footer(text="Adrian — Discord\'s #1 Militaria Bot")
                        await user.send(embed=embed)
                        reminded += 1
                        await asyncio.sleep(1)  # Rate limit
                except discord.Forbidden:
                    pass
                except Exception as e:
                    logger.debug(f"[Reminder] Could not remind user {row['user_id']}: {e}")

            if reminded > 0:
                logger.info(f"[Reminder] Sent onboarding reminders to {reminded} user(s)")

        except Exception as e:
            logger.error(f"[Reminder] Onboarding reminder error: {e}\n{traceback.format_exc()}")

        await asyncio.sleep(86400)  # Run every 24 hours

async def check_all_dealers():
    await client.wait_until_ready()
    while not client.is_closed():
        try:
            await _check_all_dealers_inner()
        except asyncio.CancelledError:
            logger.info("[DealerChecker] Task cancelled — shutting down.")
            break
        except Exception as e:
            logger.error(f"[DealerChecker] CRASHED: {e}\n{traceback.format_exc()}")
            logger.info("[DealerChecker] Restarting in 60 seconds...")
            await asyncio.sleep(60)

async def _check_all_dealers_inner():
    logger.info(f"Bot ready! Monitoring {len(DEALERS)} web dealers + {len(EMAIL_DEALERS)} email dealers.")
    while not client.is_closed():
        if bot_state["paused"] and not bot_state["force_rescan"]:
            await asyncio.sleep(30)
            continue
        bot_state["force_rescan"] = False
        logger.info(f"--- Checking dealers at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
        logger.debug(f"[Dealer Check] Paused={bot_state['paused']} | Force={bot_state['force_rescan']} | Dealers={len(DEALERS)+len(EMAIL_DEALERS)}")
        bot_state["last_check"] = datetime.now(timezone.utc)
        seen = load_seen()
        async with aiohttp.ClientSession() as session:
            for dealer in DEALERS:
                await check_dealer(session, dealer, seen)
                await asyncio.sleep(2)
        save_seen(seen)
        logger.info(f"--- Done. Next check in {CHECK_INTERVAL//60} minutes. ---")
        await asyncio.sleep(CHECK_INTERVAL)

# ==================== PLAYWRIGHT SCRAPER ====================

async def db_get_seen_items(dealer_name):
    """Get all seen item IDs for a Playwright dealer."""
    try:
        async with client.db.acquire() as conn:
            rows = await conn.fetch(
                "SELECT item_id FROM playwright_seen_items WHERE dealer_name=$1",
                dealer_name
            )
            return {row["item_id"] for row in rows}
    except Exception as e:
        logger.error(f"[DB] db_get_seen_items error: {e}")
        return set()


async def db_save_seen_items(dealer_name, item_ids, item_titles=None):
    """Save new seen item IDs for a Playwright dealer."""
    if not item_ids:
        return
    try:
        now = int(datetime.now(timezone.utc).timestamp())
        async with client.db.acquire() as conn:
            for item_id in item_ids:
                title = (item_titles or {}).get(item_id, "")
                await conn.execute(
                    """INSERT INTO playwright_seen_items (dealer_name, item_id, item_title, seen_at)
                       VALUES ($1, $2, $3, $4)
                       ON CONFLICT (dealer_name, item_id) DO NOTHING""",
                    dealer_name, str(item_id), str(title), now
                )
    except Exception as e:
        logger.error(f"[DB] db_save_seen_items error: {e}")



async def get_playwright_browser():
    """Launch a shared Playwright browser instance."""
    try:
        from playwright.async_api import async_playwright
        pw = await async_playwright().start()
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--no-first-run",
                "--no-zygote",
            ]
        )
        return pw, browser
    except Exception as e:
        logger.error(f"[Playwright] Failed to launch browser: {e}")
        return None, None


async def scrape_dealer_items(browser, dealer):
    """Scrape a dealer page and return list of (item_id, item_title) tuples."""
    name = dealer["name"]
    url = dealer["url"]
    item_sel = dealer["item_sel"]
    title_sel = dealer["title_sel"]
    id_sel = dealer.get("id_sel")

    items = []
    context = None
    page = None
    try:
        # Use isolated browser context per dealer so failures don\'t bleed across
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-US",
            viewport={"width": 1920, "height": 1080},
            java_script_enabled=True,
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Cache-Control": "max-age=0",
                "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            }
        )
        page = await context.new_page()

        # Hide webdriver fingerprint
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            window.chrome = {runtime: {}};
        """)

        logger.debug(f"[Playwright] Loading {name}...")
        for attempt in range(3):
            try:
                await page.goto(url, wait_until="networkidle", timeout=45000)
                # Check if page loaded properly (not a 39-char empty response)
                html_check = await page.content()
                if len(html_check) > 500:
                    break
                logger.debug(f"[Playwright] {name} got short response ({len(html_check)} chars), retrying...")
                await asyncio.sleep(5)
            except Exception:
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    break
                except Exception:
                    if attempt == 2:
                        raise
                    await asyncio.sleep(5)

        # Accept cookie consent banners if present
        for cookie_sel in ["#accept-cookies", ".cookie-accept", "button[id*='accept']", "button[class*='accept']", "a[class*='accept']", ".got-it", "a[class*='borderoff']"]:
            try:
                btn = await page.query_selector(cookie_sel)
                if btn:
                    await btn.click()
                    await asyncio.sleep(1)
                    logger.debug(f"[Playwright] Accepted cookie consent on {name}")
                    break
            except Exception:
                pass
        # Try text-based click for sites like Overlook with "Got it!" text
        try:
            await page.get_by_text("Got it!").click(timeout=3000)
            await asyncio.sleep(1)
            logger.debug(f"[Playwright] Clicked 'Got it!' on {name}")
        except Exception:
            pass
        try:
            await page.get_by_text("Got It!").click(timeout=2000)
            await asyncio.sleep(1)
        except Exception:
            pass

        # Extra wait for AJAX-heavy sites
        extra_wait = dealer.get("extra_wait_ms", 0)
        await asyncio.sleep(2 + extra_wait / 1000)

        # Wait for products to appear — try multiple common selectors
        selectors_to_try = [item_sel, "li.product", ".product", ".product-item", "article.product"]
        found_sel = None
        for sel in selectors_to_try:
            try:
                await page.wait_for_selector(sel, timeout=8000)
                found_sel = sel
                logger.debug(f"[Playwright] Found products with selector \'{sel}\' on {name}")
                break
            except Exception:
                continue

        if not found_sel:
            try:
                title = await page.title()
                current_url = page.url
                html = await page.content()
                html_len = len(html)
                logger.warning(f"[Playwright] No product selector found on {name}")
                logger.warning(f"[Playwright]   Title: \'{title}\' | URL: {current_url} | HTML: {html_len} chars")
                # Dump first 2000 chars of body to help find the right selector
                import re as _re3
                body_match = _re3.search(r'<body[^>]*>(.*)', html, _re3.DOTALL | _re3.IGNORECASE)
                if body_match:
                    body_snippet = body_match.group(1)[:2000]
                    # Strip tags for readability
                    clean = _re3.sub(r'<[^>]+>', ' ', body_snippet)
                    clean = _re3.sub(r'\s+', ' ', clean).strip()
                    logger.debug(f"[Playwright] {name} body snippet: {clean[:500]}")
            except Exception:
                logger.warning(f"[Playwright] No product selector found on {name} — could not get debug info")
            return items

        product_elements = await page.query_selector_all(found_sel)
        logger.debug(f"[Playwright] Found {len(product_elements)} product elements on {name}")

        for el in product_elements:
            try:
                # Get title — try multiple selectors
                title_text = ""
                for t_sel in [title_sel, "h2", "h3", ".product-title", ".name", "a"]:
                    title_el = await el.query_selector(t_sel)
                    if title_el:
                        title_text = (await title_el.inner_text()).strip()
                        if title_text:
                            break

                # Get ID (SKU/item code) or fall back to title
                if id_sel:
                    id_el = await el.query_selector(id_sel)
                    item_id = (await id_el.inner_text()).strip() if id_el else title_text
                else:
                    item_id = title_text

                if item_id and title_text:
                    # Skip category counters like "AMERICAN (1497)"
                    import re as _re2
                    if _re2.match(r'^[A-Z\\s&]+\\s*\\(\\d+\\)$', item_id.strip()):
                        continue
                    items.append((item_id[:200], title_text[:200]))
            except Exception as ie:
                logger.debug(f"[Playwright] Error parsing item on {name}: {ie}")
                continue

        logger.debug(f"[Playwright] Extracted {len(items)} items from {name}")

    except Exception as e:
        logger.error(f"[Playwright] Error scraping {name}: {e}")
    finally:
        try:
            if page: await page.close()
            if context: await context.close()
        except Exception:
            pass

    return items


async def install_playwright_browsers():
    """Install Playwright browsers if not already installed."""
    try:
        import subprocess
        logger.info("[Playwright] Installing Chromium browser...")
        result = subprocess.run(
            ["playwright", "install", "chromium", "--with-deps"],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            logger.info("[Playwright] Chromium installed successfully")
        else:
            logger.warning(f"[Playwright] Install output: {result.stdout} {result.stderr}")
    except Exception as e:
        logger.error(f"[Playwright] Could not install Chromium: {e}")


async def check_playwright_dealers():
    """Background task — checks all Playwright dealers every 10 minutes."""
    # Install browsers first
    await install_playwright_browsers()
    # Wait for bot to be fully ready
    await asyncio.sleep(15)
    logger.info(f"[Playwright] Scraper starting — monitoring {len(PLAYWRIGHT_DEALERS)} dealers")

    pw = None
    browser = None

    while not client.is_closed():
        try:
            logger.info(f"[Playwright] --- Checking {len(PLAYWRIGHT_DEALERS)} dealers at {datetime.now().strftime('%H:%M:%S')} ---")

            # Launch browser
            try:
                from playwright.async_api import async_playwright
                pw = await async_playwright().start()
                # Try system chromium first (Railway), fall back to Playwright's own
                import shutil
                chromium_path = shutil.which("chromium") or shutil.which("chromium-browser") or None
                launch_kwargs = dict(
                    headless=True,
                    args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--single-process"]
                )
                if chromium_path:
                    launch_kwargs["executable_path"] = chromium_path
                    logger.debug(f"[Playwright] Using system Chromium at {chromium_path}")
                browser = await pw.chromium.launch(**launch_kwargs)
                logger.debug("[Playwright] Browser launched")
            except Exception as be:
                logger.error(f"[Playwright] Could not launch browser: {be}")
                await asyncio.sleep(PLAYWRIGHT_CHECK_INTERVAL)
                continue

            for dealer in PLAYWRIGHT_DEALERS:
                name = dealer["name"]
                # Create fresh browser for each dealer to prevent crashes bleeding across
                dealer_browser = None
                try:
                    dealer_browser = await pw.chromium.launch(
                        headless=True,
                        args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--single-process"]
                    )
                    # Handle multi-page dealers (like Griffin)
                    pages = dealer.get("pages")
                    if pages:
                        items = []
                        for page_url in pages:
                            page_browser = None
                            try:
                                page_browser = await pw.chromium.launch(
                                    headless=True,
                                    args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--single-process"]
                                )
                                page_dealer = dict(dealer)
                                page_dealer["url"] = page_url
                                page_items = await scrape_dealer_items(page_browser, page_dealer)
                                items.extend(page_items)
                                if page_items:
                                    logger.debug(f"[Playwright] {name} — {page_url.rstrip('/').split('/')[-1]}: {len(page_items)} items")
                            except Exception as pe:
                                logger.debug(f"[Playwright] {name} — error on {page_url}: {pe}")
                            finally:
                                if page_browser:
                                    try:
                                        await page_browser.close()
                                    except Exception:
                                        pass
                        logger.debug(f"[Playwright] {name} — total {len(items)} items across {len(pages)} pages")
                    else:
                        items = await scrape_dealer_items(dealer_browser, dealer)

                    if not items:
                        logger.debug(f"[Playwright] {name} — no items found, skipping")
                        continue

                    # Check against seen items
                    seen = await db_get_seen_items(name)

                    if not seen:
                        # First run — save baseline, no alert
                        item_ids = [i[0] for i in items]
                        item_titles = {i[0]: i[1] for i in items}
                        await db_save_seen_items(name, item_ids, item_titles)
                        logger.info(f"[Playwright] {name} — first check, saved {len(items)} items as baseline")
                        continue

                    # Find new items
                    new_items = [(iid, title) for iid, title in items if iid not in seen]

                    if new_items:
                        logger.info(f"[Playwright] {name} — {len(new_items)} NEW item(s) detected!")
                        for iid, title in new_items:
                            logger.info(f"[Playwright]   → {title} ({iid})")

                        # Save new items as seen
                        new_ids = [i[0] for i in new_items]
                        new_titles = {i[0]: i[1] for i in new_items}
                        await db_save_seen_items(name, new_ids, new_titles)

                        # Fire alert
                        logo_file = os.path.join(SCRIPT_DIR, "logos", dealer["logo_file"])
                        await send_alert(name, dealer["url"], logo_file)
                        bot_state["alert_count"] += 1
                    else:
                        logger.debug(f"[Playwright] {name} — no new items ({len(items)} seen)")

                    await asyncio.sleep(3)  # Small delay between dealers

                except Exception as de:
                    logger.error(f"[Playwright] Error checking {name}: {de}\n{traceback.format_exc()}")
                    bot_state["error_count"] += 1
                finally:
                    if dealer_browser:
                        try:
                            await dealer_browser.close()
                        except Exception:
                            pass

        except Exception as e:
            logger.error(f"[Playwright] Scraper loop error: {e}\n{traceback.format_exc()}")
            bot_state["error_count"] += 1

        finally:
            # Always close browser after each check cycle
            try:
                if browser:
                    await browser.close()
                if pw:
                    await pw.stop()
            except Exception:
                pass
            browser = None
            pw = None

        logger.info(f"[Playwright] --- Done. Next check in {PLAYWRIGHT_CHECK_INTERVAL//60} minutes ---")
        await asyncio.sleep(PLAYWRIGHT_CHECK_INTERVAL)


# ==================== WAF EMAIL PARSER ====================

BUMP_KEYWORDS = ["up", "bump", "still available", "still for sale", "ttt", "btt", "to the top", "glws", "price reduced", "price drop", "make offer", "reduced", "price drop", "lowered", "will consider", "open to offers", "bump it up", "bringing to top", "back to top", "anyone interested", "still here", "available", "taking offers"]

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
        # Exact match on short messages
        exact_match = any(keyword == msg_lower for keyword in BUMP_KEYWORDS)
        # Short message (under 60 chars) containing a bump keyword
        short_bump = len(msg_lower) < 60 and any(keyword in msg_lower for keyword in BUMP_KEYWORDS)
        # Message starts with a bump keyword
        starts_with_bump = any(msg_lower.startswith(keyword) for keyword in BUMP_KEYWORDS)
        # Message is ONLY bump content — no price mentioned
        has_price = bool(re.search(r"[\$€£]\s*\d{2,}", msg_lower))
        is_bump = (exact_match or short_bump or starts_with_bump) and not has_price

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
    subject_category = subject_cat_match.group(1).strip() if subject_cat_match else ""
    subject_category_lower = subject_category.lower()

    # Use subject category directly as display name — Gmail is already correct
    # Just need to find the matching role for pinging
    matched_role_id = None
    category_name = subject_category if subject_category else "All WAF Updates"

    # Try exact match first (case insensitive)
    for cat in WAF_CATEGORIES:
        if cat["name"] == "All WAF Updates":
            continue
        if cat["name"].lower() == subject_category_lower:
            matched_role_id = cat["role_id"]
            break

    # Try partial match — subject contains category name or vice versa
    if not matched_role_id:
        for cat in WAF_CATEGORIES:
            if cat["name"] == "All WAF Updates":
                continue
            cat_lower = cat["name"].lower()
            if cat_lower in subject_category_lower or subject_category_lower in cat_lower:
                matched_role_id = cat["role_id"]
                break

    # Fall back to keyword matching
    if not matched_role_id:
        for cat in WAF_CATEGORIES:
            if cat["name"] == "All WAF Updates":
                continue
            for keyword in cat["keywords"]:
                if keyword.lower() in subject_category_lower:
                    matched_role_id = cat["role_id"]
                    break
            if matched_role_id:
                break

    # Default to All WAF Updates
    if not matched_role_id:
        matched_role_id = WAF_CATEGORIES[0]["role_id"]
        logger.debug(f"[WAF] Could not match category '{subject_category}' — defaulting to All WAF Updates")
    else:
        logger.debug(f"[WAF] Matched '{subject_category}' to role {matched_role_id}")

    # Detect sold items — check title and message body for sold indicators
    sold_keywords = ["sold", "[sold]", "(sold)", "- sold", "sold out", "sold!", "sold pending"]
    title_lower = item_title.lower()
    msg_lower_check = msg_body_clean.lower()
    is_sold = (
        any(kw in title_lower for kw in sold_keywords) or
        any(kw in msg_lower_check[:100] for kw in sold_keywords)  # Check start of message only
    )

    logger.debug(f"[WAF] Parsed: title='{item_title}' | category='{category_name}' | poster='{poster}' | url='{forum_url}' | prices={clean_prices} | bump={is_bump} | sold={is_sold}")

    return {
        "item_title": item_title,
        "category": category_name,
        "poster": poster,
        "forum_url": forum_url,
        "is_bump": is_bump,
        "prices": clean_prices,
        "role_id": matched_role_id,
        "msg_body": msg_body_clean,
        "is_sold": is_sold,
    }

# ==================== USMF EMAIL PARSER ====================
def parse_usmf_email(subject, body):
    """Parse a USMF forum notification email."""
    import re

    # Title comes from the subject line directly
    item_title = subject.strip()

    # Extract forum/category — "Posted in CATEGORY"
    category_match = re.search(r"Posted in (.+)", body, re.IGNORECASE)
    category = category_match.group(1).strip() if category_match else ""

    # Extract price from body
    price_pattern = r"(?:[\$€£]\s*\d{2,6}(?:[.,]\d{2})?|\d{2,6}(?:[.,]\d{2})?\s*(?:EUR|USD|GBP))"
    raw_prices = re.findall(price_pattern, body, re.IGNORECASE)
    clean_prices = []
    seen_prices = set()
    for p in raw_prices:
        p = p.strip().upper()
        if p not in seen_prices:
            seen_prices.add(p)
            clean_prices.append(p)
    clean_prices = clean_prices[:3]
    price_str = " | ".join(clean_prices) if clean_prices else ""

    # Extract the actual topic URL from inside the redirect URL
    # Format: ...&url=https://www.usmilitariaforum.com/forums/index.php?/topic/XXXXX/...
    topic_url = ""
    url_match = re.search(r'https?://www\.usmilitariaforum\.com/forums/index\.php\?/topic/[^\s&"]+', body)
    if url_match:
        topic_url = url_match.group(0).strip()
    else:
        # Fallback: grab any USMF URL
        fallback = re.search(r"https?://www\.usmilitariaforum\.com/\S+", body)
        topic_url = fallback.group(0).strip() if fallback else ""

    # Match category to USMF_CATEGORIES
    matched_category = category  # Use raw category from email by default
    for cat in USMF_CATEGORIES:
        if cat["name"].lower() in category.lower() or category.lower() in cat["name"].lower():
            matched_category = cat["name"]
            break
        for keyword in cat["keywords"]:
            if keyword.lower() in category.lower():
                matched_category = cat["name"]
                break

    # Detect sold items
    sold_keywords = ["sold", "[sold]", "(sold)", "- sold", "sold out", "sold!", "sold pending"]
    is_sold = any(kw in item_title.lower() for kw in sold_keywords)

    logger.debug(f"[USMF] Parsed: title='{item_title}' | category='{matched_category}' | price='{price_str}' | url='{topic_url}' | sold={is_sold}")

    return {
        "item_title": item_title,
        "category": matched_category,
        "price_str": price_str,
        "forum_url": topic_url,
        "is_sold": is_sold,
    }

async def send_usmf_alert(parsed):
    """Send a USMF forum alert to the USMF channel."""

    # Skip sold items entirely
    if parsed.get("is_sold"):
        logger.info(f"[USMF] Skipping sold item: {parsed.get('item_title', 'Unknown')}")
        return

    # Build description
    description = f"**{parsed['item_title']}**\n"
    if parsed.get("category"):
        description += f"\n📂 {parsed['category']}\n"
    if parsed.get("price_str"):
        description += f"\n💰 **{parsed['price_str']}**\n"
    if parsed.get("forum_url"):
        description += f"\n[**View Thread →**]({parsed['forum_url']})"

    embed = discord.Embed(
        title="🇺🇸 New USMF Listing",
        description=description,
        color=discord.Color.dark_blue(),
        timestamp=datetime.now(timezone.utc)
    )
    embed.set_footer(text="Adrian — Forum Alert | You may need to make a free forum account to see this listing")

    logo_file = os.path.join(SCRIPT_DIR, "logos", "usmf.png")
    file = None
    if os.path.exists(logo_file):
        file = discord.File(logo_file, filename="logo.png")
        embed.set_thumbnail(url="attachment://logo.png")

    # Post to #adrian-updates
    usmf_updates_channels = await get_all_server_channels("usmf_channel_id")
    for usmf_updates_channel in usmf_updates_channels:
        try:
            if file and os.path.exists(logo_file):
                await usmf_updates_channel.send(file=discord.File(logo_file, filename="logo.png"), embed=embed, allowed_mentions=discord.AllowedMentions.none())
            else:
                await usmf_updates_channel.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())
            logger.info(f"[USMF] Alert sent to #{usmf_updates_channel.name} in {usmf_updates_channel.guild.name}: {parsed['item_title']}")
        except Exception as e:
            logger.error(f"[USMF] Failed to send to {usmf_updates_channel.guild.name}: {e}")

    # Log to private mod channel
    try:
        log_ch = client.get_channel(PRIVATE_LOG_CHANNEL_ID)
        if log_ch:
            await log_ch.send(embed=embed)
    except Exception as e:
        logger.error(f"[USMF] Failed to log: {e}")

    # Ping subscribed users in channel then immediately delete
    try:
        category_name = parsed.get("category", "")
        if category_name:
            async with client.db.acquire() as conn:
                rows = await conn.fetch(
                    "SELECT user_id FROM user_preferences WHERE usmf_categories LIKE $1",
                    f"%{category_name}%"
                )
            if rows:
                mentions = " ".join([f"<@{row['user_id']}>" for row in rows])
                for usmf_updates_channel in usmf_updates_channels:
                    try:
                        ping_msg = await usmf_updates_channel.send(mentions)
                        await ping_msg.delete()
                    except Exception as pe:
                        logger.debug(f"[USMF] Ping error: {pe}")
                logger.info(f"[USMF] Pinged {len(rows)} user(s) for category: {category_name}")
    except Exception as e:
        logger.error(f"[USMF] Ping error: {e}")

    # Legacy pending pings (keep for backwards compatibility)
    try:
        usmf_users = await db_get_users_for_forum("usmf")
        for uid in usmf_users:
            try:
                await db_add_pending_alert(uid, f"USMF: {parsed['item_title']}", parsed.get('forum_url', ''), "🇺🇸")
                if uid not in bot_state["pending_pings"]:
                    bot_state["pending_pings"][uid] = []
                bot_state["pending_pings"][uid].append({"name": "USMF Forum", "flag": "🇺🇸", "url": ""})
                if not bot_state["ping_task_running"]:
                    asyncio.create_task(flush_pending_pings())
            except Exception as ping_err:
                logger.debug(f"[USMF Alert] Could not ping {uid}: {ping_err}")
    except Exception as e:
        logger.error(f"[USMF Alert] Failed: {e}")

    # Keyword watchlist DMs
    try:
        item_title = parsed.get("item_title", "")
        keyword_users = await db_get_users_for_keyword(item_title)
        for uid in keyword_users:
            try:
                user = await client.fetch_user(int(uid))
                kw_embed = discord.Embed(
                    title="🔔 Keyword Alert — USMF",
                    description=(
                        f"A USMF listing matched one of your keywords!\n\n"
                        f"**{item_title}**\n"
                        f"Posted by: **{parsed.get('poster', 'Unknown')}**"
                    ),
                    color=discord.Color.dark_gold(),
                    timestamp=datetime.now(timezone.utc)
                )
                forum_url = parsed.get("forum_url", "")
                if forum_url:
                    kw_embed.add_field(name="🔗 View Listing", value=f"[Click here]({forum_url})", inline=False)
                kw_embed.set_footer(text="Adrian — Keyword Watchlist | You may need a free forum account to view this listing")
                await user.send(embed=kw_embed)
                logger.info(f"[Watchlist] Keyword DM sent to {uid} for USMF: {item_title}")
            except discord.Forbidden:
                pass
            except Exception as kw_err:
                logger.debug(f"[Watchlist] Could not DM {uid}: {kw_err}")
    except Exception as e:
        logger.error(f"[Watchlist] USMF keyword matching failed: {e}")

async def send_waf_alert(parsed, guild=None):
    """Send a formatted WAF Estate alert to members with the correct role."""
    forum_url = parsed.get("forum_url", "")
    item_title = parsed.get("item_title", "Unknown")
    price_str_raw = " | ".join(parsed["prices"]) if parsed["prices"] else ""

    # Skip sold items entirely — no alert, no DM
    if parsed.get("is_sold"):
        logger.info(f"[WAF] Skipping sold item: {item_title}")
        return

    if parsed["is_bump"]:
        # Track bump but check for price drop first
        if forum_url:
            await db_increment_waf_thread(forum_url, item_title, price_str_raw, is_bump=True)
            stats = await db_get_waf_thread_stats(forum_url)
            last_price = stats["last_price"] if stats else None
            bump_count = stats["bump_count"] if stats else 1
            notif_count = stats["notification_count"] if stats else 0

            # Only alert if there is a new lower price
            if price_str_raw and last_price and price_str_raw != last_price:
                logger.info(f"[WAF] Price drop detected for: {item_title} — {last_price} → {price_str_raw}")
                # Fall through to send a price drop alert below
                parsed["is_bump"] = False
                parsed["price_drop"] = True
                parsed["old_price"] = last_price
            else:
                logger.info(f"[WAF] Bump silently ignored for: {item_title} (bump #{bump_count})")
                return
        else:
            logger.info(f"[WAF] Bump silently ignored for: {item_title}")
            return

    role = guild.get_role(parsed["role_id"]) if guild else None

    price_str = " | ".join(parsed["prices"]) if parsed["prices"] else ""

    # Track notification count
    if forum_url:
        await db_increment_waf_thread(forum_url, item_title, price_str, is_bump=False)
        stats = await db_get_waf_thread_stats(forum_url)
        notif_count = stats["notification_count"] if stats else 1
        bump_count = stats["bump_count"] if stats else 0
    else:
        notif_count = 1
        bump_count = 0

    # Look up emoji for this category
    cat_emoji = "🎖️"
    for cat in WAF_CATEGORIES:
        if cat["role_id"] == parsed["role_id"]:
            cat_emoji = cat.get("emoji", "🎖️")
            break

    # Embed: category as title, item name in description
    description = f"**{parsed['item_title']}**\n"
    if parsed.get("price_drop") and parsed.get("old_price"):
        description += f"\n💰 ~~{parsed['old_price']}~~ → **{price_str}** 📉\n"
    elif price_str:
        description += f"\n💰 **{price_str}**\n"
    if parsed["forum_url"]:
        description += f"\n[**View Listing →**]({parsed['forum_url']})"

    embed_color = discord.Color.green() if parsed.get("price_drop") else discord.Color.dark_gold()
    embed_title = f"📉 Price Drop — {parsed['category']}" if parsed.get("price_drop") else f"{cat_emoji} {parsed['category']}"
    embed = discord.Embed(
        title=embed_title,
        description=description,
        color=embed_color,
        timestamp=datetime.now(timezone.utc)
    )
    embed.set_footer(text="Adrian — Forum Alert | You may need to make a free forum account to see this listing")

    logo_file = os.path.join(SCRIPT_DIR, "logos", "waf.png")
    file = None
    if os.path.exists(logo_file):
        file = discord.File(logo_file, filename="logo.png")
        embed.set_thumbnail(url="attachment://logo.png")

    watch_view = WatchItemView(parsed["forum_url"], parsed["item_title"], price_str) if parsed["forum_url"] else None

    # Post to #adrian-updates (no role ping — users get DMs based on their profile)
    waf_updates_channels = await get_all_server_channels("waf_channel_id")
    for waf_updates_channel in waf_updates_channels:
        try:
            if file and os.path.exists(logo_file):
                await waf_updates_channel.send(file=discord.File(logo_file, filename="logo.png"), embed=embed, view=watch_view, allowed_mentions=discord.AllowedMentions.none())
            else:
                await waf_updates_channel.send(embed=embed, view=watch_view, allowed_mentions=discord.AllowedMentions.none())
            bot_state["alert_count"] += 1
            logger.info(f"[WAF] Alert sent to #{waf_updates_channel.name} in {waf_updates_channel.guild.name}: {parsed['item_title']}")
        except Exception as e:
            logger.error(f"[WAF] Failed to send to {waf_updates_channel.guild.name}: {e}")

    # Ping subscribed users in channel then immediately delete
    try:
        role_id_str = str(parsed["role_id"])
        async with client.db.acquire() as conn:
            # Use comma-bounded search to prevent partial ID matches
            rows = await conn.fetch(
                """SELECT user_id FROM user_preferences WHERE
                   waf_categories = $1 OR
                   waf_categories LIKE $2 OR
                   waf_categories LIKE $3 OR
                   waf_categories LIKE $4""",
                role_id_str,
                f"{role_id_str},%",
                f"%,{role_id_str},%",
                f"%,{role_id_str}"
            )
        if rows:
            mentions = " ".join([f"<@{row['user_id']}>" for row in rows])
            for waf_updates_channel in waf_updates_channels:
                try:
                    ping_msg = await waf_updates_channel.send(mentions)
                    await ping_msg.delete()
                except Exception as pe:
                    logger.debug(f"[WAF] Ping error: {pe}")
            logger.info(f"[WAF] Pinged {len(rows)} user(s) for category: {parsed['category']}")
    except Exception as e:
        logger.error(f"[WAF] Ping error: {e}")

    # Log to private mod channel
    try:
        log_ch = client.get_channel(PRIVATE_LOG_CHANNEL_ID)
        if log_ch:
            await log_ch.send(embed=embed)
    except Exception as e:
        logger.error(f"[WAF] Failed to log: {e}")

    # Ping matched users
    try:
        waf_users = await db_get_users_for_forum("waf")
        for uid in waf_users:
            try:
                await db_add_pending_alert(uid, f"WAF: {parsed['item_title']}", parsed.get('forum_url', ''), "🎖️")
                if uid not in bot_state["pending_pings"]:
                    bot_state["pending_pings"][uid] = []
                bot_state["pending_pings"][uid].append({"name": "WAF Forum", "flag": "🎖️", "url": ""})
                if not bot_state["ping_task_running"]:
                    asyncio.create_task(flush_pending_pings())
            except Exception as ping_err:
                logger.debug(f"[WAF Alert] Could not ping {uid}: {ping_err}")
    except Exception as e:
        logger.error(f"[WAF Alert] Failed: {e}")

    # Keyword watchlist DMs
    try:
        item_title = parsed.get("item_title", "")
        keyword_users = await db_get_users_for_keyword(item_title)
        for uid in keyword_users:
            try:
                user = await client.fetch_user(int(uid))
                kw_embed = discord.Embed(
                    title="🔔 Keyword Alert — WAF Forum",
                    description=(
                        f"A WAF listing matched one of your keywords!\n\n"
                        f"**{item_title}**\n"
                        f"Posted by: **{parsed.get('poster', 'Unknown')}**"
                    ),
                    color=discord.Color.dark_gold(),
                    timestamp=datetime.now(timezone.utc)
                )
                forum_url = parsed.get("forum_url", "")
                if forum_url:
                    kw_embed.add_field(name="🔗 View Listing", value=f"[Click here]({forum_url})", inline=False)
                kw_embed.set_footer(text="Adrian — Keyword Watchlist | You may need a free forum account to view this listing")
                await user.send(embed=kw_embed)
                logger.info(f"[Watchlist] Keyword DM sent to {uid} for WAF: {item_title}")
            except discord.Forbidden:
                pass
            except Exception as kw_err:
                logger.debug(f"[Watchlist] Could not DM {uid}: {kw_err}")
    except Exception as e:
        logger.error(f"[Watchlist] WAF keyword matching failed: {e}")

    try:
        # Every 25 WAF notifications, send a Militaria Alert ad
        bot_state["waf_notification_count"] += 1
        if bot_state["waf_notification_count"] % 25 == 0:
            try:
                ad_embed = discord.Embed(
                    title="🔍 Looking for something specific?",
                    description="**Want custom alerts for items you're looking for?**\n\nSign up for **Militaria Alert** and get notified the moment your target item hits the market.\n\n💰 Only **$1/month**",
                    color=discord.Color.green(),
                    timestamp=datetime.now(timezone.utc)
                )
                ad_embed.set_footer(text="Adrian — Sponsored")
                buy_view = MilitariaAlertAdView()
                await channel.send(embed=ad_embed, view=buy_view)
                logger.info("[WAF] Militaria Alert ad sent.")
            except Exception as ad_err:
                logger.error(f"[WAF] Failed to send ad: {ad_err}")
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
                    dm_embed.set_footer(text="Adrian — Watchlist")
                    await user.send(embed=dm_embed)
                    await db_update_watch_price(uid, parsed["forum_url"], new_price)
                except Exception as e:
                    logger.error(f"[Watchlist] Failed to DM watcher {uid}: {e}")

async def check_email_dealers():
    await client.wait_until_ready()
    while not client.is_closed():
        try:
            await _check_email_dealers_inner()
        except asyncio.CancelledError:
            logger.info("[EmailChecker] Task cancelled — shutting down.")
            break
        except Exception as e:
            logger.error(f"[EmailChecker] CRASHED: {e}\n{traceback.format_exc()}")
            logger.info("[EmailChecker] Restarting in 60 seconds...")
            await asyncio.sleep(60)

async def _check_email_dealers_inner():
    # Email checker runs regardless of channel availability
    logger.info(f"Email checker ready! Checking every {EMAIL_CHECK_INTERVAL} seconds.")
    while not client.is_closed():
        if bot_state["paused"]:
            await asyncio.sleep(30)
            continue
        bot_state["last_email_check"] = datetime.now(timezone.utc)
        logger.debug(f"[Email Check] Running email check at {datetime.now().strftime('%H:%M:%S')}")

        # Check Gmail
        triggered = await check_gmail_async()
        for dealer, subject, body in triggered:
            await db_increment_stat(dealer["name"])
            is_waf = dealer.get("waf", False)
            if is_waf:
                try:
                    parsed = parse_waf_email(subject, body)
                    guild = client.guilds[0] if client.guilds else None
                    await send_waf_alert(parsed, guild)
                except Exception as e:
                    logger.error(f"[WAF] Error processing email '{subject}': {e}\n{traceback.format_exc()}")
            elif dealer.get("usmf", False):
                try:
                    parsed = parse_usmf_email(subject, body)
                    await send_usmf_alert(parsed)
                except Exception as e:
                    logger.error(f"[USMF] Error processing email '{subject}': {e}\n{traceback.format_exc()}")
            else:
                logo_file = os.path.join(SCRIPT_DIR, "logos", dealer["logo_file"])
                await send_alert(dealer["name"], dealer["url"], logo_file)


        await asyncio.sleep(EMAIL_CHECK_INTERVAL)

# ==================== SELLER PROFILE VIEW ====================

class SellerProfileView(discord.ui.View):
    def __init__(self, seller_id):
        super().__init__(timeout=None)
        self.seller_id = seller_id

    def _get_seller_id(self, interaction: discord.Interaction):
        """Get seller ID from self or fall back to DB lookup."""
        if self.seller_id and self.seller_id != "placeholder":
            return self.seller_id
        return None

    async def _get_seller_id_async(self, interaction: discord.Interaction):
        """Get seller ID — checks DB for cross-posted mirrors."""
        if self.seller_id and self.seller_id != "placeholder":
            return self.seller_id
        # Check DB for cross-post mirror
        if isinstance(interaction.channel, discord.Thread):
            try:
                async with client.db.acquire() as conn:
                    row = await conn.fetchrow(
                        "SELECT seller_id FROM cross_post_mirrors WHERE mirror_thread_id=$1",
                        str(interaction.channel.id)
                    )
                    if row:
                        return str(row["seller_id"])
            except Exception as e:
                logger.debug(f"[SellerProfile] DB lookup error: {e}")
        return None

    @discord.ui.button(label="Check Seller Profile", emoji="🔍", style=discord.ButtonStyle.primary, custom_id="estate_check_seller")
    async def check_seller(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            seller_id = await self._get_seller_id_async(interaction)
            if not seller_id:
                await interaction.response.send_message("⚠️ Could not find seller.", ephemeral=True)
                return
            seller = interaction.guild.get_member(int(seller_id)) if interaction.guild else None
            if not seller:
                seller = await client.fetch_user(int(seller_id))
            self.seller_id = seller_id
            if not seller:
                await interaction.response.send_message("⚠️ Could not find seller profile.", ephemeral=True)
                return
            seller_avg, seller_count = await db_get_seller_rating(self.seller_id)
            points = await db_get_user_points(self.seller_id)
            warnings = await db_get_user_warnings(self.seller_id)
            rank = get_rank(points, warnings > 0)
            account_ts = int(seller.created_at.timestamp())
            joined = getattr(seller, "joined_at", None)
            join_ts = int(joined.timestamp()) if joined else 0

            embed = discord.Embed(
                title=f"🎖️ {seller.display_name}'s Seller Profile",
                color=discord.Color.dark_gold(),
                timestamp=datetime.now(timezone.utc)
            )
            embed.set_thumbnail(url=seller.display_avatar.url)
            embed.add_field(name="🎗️ Rank", value=f"{rank}\n{points:,} pts", inline=True)
            embed.add_field(name="🏪 Seller Rating", value=f"{format_stars(seller_avg)}\n{seller_count} sale(s)", inline=True)
            if join_ts:
                embed.add_field(name="📅 Member Since", value=f"<t:{join_ts}:R>", inline=True)
            embed.add_field(name="🗓️ Account Age", value=f"<t:{account_ts}:R>", inline=True)
            if warnings > 0:
                embed.add_field(name="⚠️ Warnings", value=f"{warnings} active warning(s)", inline=True)
            embed.set_footer(text="Adrian — Estand Marketplace")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"[Estate] CheckSeller error: {e}\n{traceback.format_exc()}")
            try:
                await interaction.response.send_message("⚠️ Something went wrong.", ephemeral=True)
            except Exception:
                pass

    @discord.ui.button(label="I'll Take It!", emoji="💰", style=discord.ButtonStyle.success, custom_id="estate_ill_take_it")
    async def ill_take_it(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            self.seller_id = await self._get_seller_id_async(interaction) or self.seller_id
            if str(interaction.user.id) == str(self.seller_id):
                await interaction.response.send_message("🚫 You can't buy your own listing!", ephemeral=True)
                return
            seller_user = await client.fetch_user(int(self.seller_id))
            if not seller_user:
                await interaction.response.send_message("⚠️ Could not find the seller.", ephemeral=True)
                return
            buyer = interaction.user
            listing_name = interaction.channel.name if interaction.channel else "your item"
            dm_embed = discord.Embed(
                title="💰 You have a buyer!",
                description=(
                    f"**{buyer.display_name}** wants to buy your listing:\n\n"
                    f"**{listing_name}**\n\n"
                    f"Reach out to them via DM to finalize the sale!"
                ),
                color=discord.Color.green(),
                timestamp=datetime.now(timezone.utc)
            )
            dm_embed.set_thumbnail(url=buyer.display_avatar.url)
            dm_embed.add_field(name="Buyer", value=f"{buyer.mention} ({buyer.display_name})", inline=True)
            dm_embed.set_footer(text="Adrian — Estand Marketplace")
            await seller_user.send(embed=dm_embed)
            await interaction.response.send_message(
                "✅ The seller has been notified! They'll reach out via DM to finalize.",
                ephemeral=True
            )
            logger.info(f"[Estate] I'll Take It clicked by {buyer.id} on listing by {self.seller_id}")
        except discord.Forbidden:
            await interaction.response.send_message("⚠️ Could not DM the seller — they may have DMs disabled.", ephemeral=True)
        except Exception as e:
            logger.error(f"[Estate] IllTakeIt error: {e}\n{traceback.format_exc()}")
            await interaction.response.send_message("⚠️ Something went wrong.", ephemeral=True)

    @discord.ui.button(label="Make an Offer", emoji="🤝", style=discord.ButtonStyle.success, custom_id="estate_make_offer")
    async def make_offer(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            self.seller_id = await self._get_seller_id_async(interaction) or self.seller_id
            if str(interaction.user.id) == str(self.seller_id):
                await interaction.response.send_message("🚫 You can't make an offer on your own listing!", ephemeral=True)
                return
            if await db_is_buyer_blocked(self.seller_id, str(interaction.user.id), str(interaction.channel_id)):
                await interaction.response.send_message("🚫 The seller has declined contact for this listing.", ephemeral=True)
                return

            seller_user = await client.fetch_user(int(self.seller_id))
            if not seller_user:
                await interaction.response.send_message("⚠️ Could not find the seller.", ephemeral=True)
                return
            buyer = interaction.user
            listing_name = interaction.channel.name if interaction.channel else "your item"
            _seller_id = self.seller_id
            _thread_id = str(interaction.channel_id)

            class OfferModal(discord.ui.Modal, title="Make an Offer"):
                price = discord.ui.TextInput(label="Your offer price", placeholder="e.g. $350", max_length=50)
                message = discord.ui.TextInput(
                    label="Message to seller (optional)",
                    style=discord.TextStyle.paragraph,
                    placeholder="Any questions or details about your offer...",
                    required=False,
                    max_length=500
                )

                async def on_submit(self2, interaction2: discord.Interaction):
                    try:
                        offer_embed = discord.Embed(
                            title="🤝 New Offer on Your Listing!",
                            description=f"**{buyer.display_name}** made an offer on **{listing_name}**",
                            color=discord.Color.gold(),
                            timestamp=datetime.now(timezone.utc)
                        )
                        offer_embed.set_thumbnail(url=buyer.display_avatar.url)
                        offer_embed.add_field(name="💰 Offer Price", value=self2.price.value, inline=True)
                        offer_embed.add_field(name="From", value=f"{buyer.mention}", inline=True)
                        if self2.message.value:
                            offer_embed.add_field(name="Message", value=self2.message.value, inline=False)
                        offer_embed.set_footer(text="Adrian — Estand Marketplace")

                        class SellerOfferResponseView(discord.ui.View):
                            def __init__(self):
                                super().__init__(timeout=86400)

                            async def _disable(self, inter):
                                for child in self.children:
                                    child.disabled = True
                                await inter.message.edit(view=self)

                            @discord.ui.button(label="✅ Accept Offer", style=discord.ButtonStyle.success)
                            async def accept(self3, interaction3: discord.Interaction, button3: discord.ui.Button):
                                await self3._disable(interaction3)
                                try:
                                    accept_embed = discord.Embed(
                                        title="✅ Your offer was accepted!",
                                        description=f"The seller accepted your offer of **{self2.price.value}** for **{listing_name}**!\n\nReach out to the seller to finalize.",
                                        color=discord.Color.green()
                                    )
                                    accept_embed.add_field(name="Seller", value=f"<@{_seller_id}>", inline=True)
                                    accept_embed.set_footer(text="Adrian — Estand Marketplace")
                                    await buyer.send(embed=accept_embed)
                                    await interaction3.response.send_message("✅ You accepted the offer! The buyer has been notified.", ephemeral=True)
                                except discord.Forbidden:
                                    await interaction3.response.send_message("⚠️ Could not DM the buyer.", ephemeral=True)

                            @discord.ui.button(label="💰 Counter Offer", style=discord.ButtonStyle.primary)
                            async def counter(self3, interaction3: discord.Interaction, button3: discord.ui.Button):
                                class CounterModal(discord.ui.Modal, title="Send Counter Offer"):
                                    counter_price = discord.ui.TextInput(label="Your asking price", placeholder="e.g. $400", max_length=50)
                                    counter_msg = discord.ui.TextInput(label="Message (optional)", style=discord.TextStyle.paragraph, required=False, max_length=500)

                                    async def on_submit(self4, interaction4: discord.Interaction):
                                        await self3._disable(interaction3)
                                        try:
                                            counter_embed = discord.Embed(
                                                title="💰 Counter Offer from Seller",
                                                description=f"The seller countered your offer on **{listing_name}**",
                                                color=discord.Color.gold(),
                                                timestamp=datetime.now(timezone.utc)
                                            )
                                            counter_embed.add_field(name="Counter Price", value=self4.counter_price.value, inline=True)
                                            if self4.counter_msg.value:
                                                counter_embed.add_field(name="Message", value=self4.counter_msg.value, inline=False)
                                            counter_embed.add_field(name="Seller", value=f"<@{_seller_id}>", inline=True)
                                            counter_embed.set_footer(text="Adrian — Estand Marketplace")

                                            class BuyerCounterView(discord.ui.View):
                                                def __init__(self):
                                                    super().__init__(timeout=86400)

                                                async def _disable(self, inter):
                                                    for child in self.children:
                                                        child.disabled = True
                                                    await inter.message.edit(view=self)

                                                @discord.ui.button(label="✅ Accept", style=discord.ButtonStyle.success)
                                                async def accept_counter(self5, interaction5: discord.Interaction, b: discord.ui.Button):
                                                    await self5._disable(interaction5)
                                                    try:
                                                        notify = discord.Embed(title="🎉 Counter accepted!", description=f"**{buyer.display_name}** accepted your counter of **{self4.counter_price.value}** for **{listing_name}**!", color=discord.Color.green())
                                                        notify.set_footer(text="Adrian — Estand Marketplace")
                                                        await seller_user.send(embed=notify)
                                                        await interaction5.response.send_message("✅ Accepted! The seller has been notified.", ephemeral=True)
                                                    except discord.Forbidden:
                                                        await interaction5.response.send_message("⚠️ Could not notify the seller.", ephemeral=True)

                                                @discord.ui.button(label="💰 Counter Back", style=discord.ButtonStyle.primary)
                                                async def counter_back(self5, interaction5: discord.Interaction, b: discord.ui.Button):
                                                    class BuyerCounterModal(discord.ui.Modal, title="Your Counter Offer"):
                                                        bc_price = discord.ui.TextInput(label="Your offer price", placeholder="e.g. $375", max_length=50)
                                                        bc_msg = discord.ui.TextInput(label="Message (optional)", style=discord.TextStyle.paragraph, required=False, max_length=500)
                                                        async def on_submit(self6, interaction6: discord.Interaction):
                                                            await self5._disable(interaction5)
                                                            try:
                                                                bc_embed = discord.Embed(title="💰 Buyer Counter Offer", description=f"**{buyer.display_name}** countered back on **{listing_name}**", color=discord.Color.gold())
                                                                bc_embed.add_field(name="Their Offer", value=self6.bc_price.value, inline=True)
                                                                if self6.bc_msg.value:
                                                                    bc_embed.add_field(name="Message", value=self6.bc_msg.value, inline=False)
                                                                bc_embed.set_footer(text="Adrian — Estand Marketplace")
                                                                await seller_user.send(embed=bc_embed)
                                                                await interaction6.response.send_message("✅ Your counter was sent!", ephemeral=True)
                                                            except discord.Forbidden:
                                                                await interaction6.response.send_message("⚠️ Could not reach the seller.", ephemeral=True)
                                                    await interaction5.response.send_modal(BuyerCounterModal())

                                                @discord.ui.button(label="❌ Decline", style=discord.ButtonStyle.danger)
                                                async def decline(self5, interaction5: discord.Interaction, b: discord.ui.Button):
                                                    await self5._disable(interaction5)
                                                    try:
                                                        dec_embed = discord.Embed(title="❌ Counter declined", description=f"**{buyer.display_name}** declined your counter offer for **{listing_name}**.", color=discord.Color.red())
                                                        dec_embed.set_footer(text="Adrian — Estand Marketplace")
                                                        await seller_user.send(embed=dec_embed)
                                                        await interaction5.response.send_message("You declined the counter offer. The seller has been notified.", ephemeral=True)
                                                    except discord.Forbidden:
                                                        await interaction5.response.send_message("⚠️ Could not notify the seller.", ephemeral=True)

                                            await buyer.send(embed=counter_embed, view=BuyerCounterView())
                                            await interaction4.response.send_message("✅ Counter offer sent!", ephemeral=True)
                                        except discord.Forbidden:
                                            await interaction4.response.send_message("⚠️ Could not DM the buyer.", ephemeral=True)
                                await interaction3.response.send_modal(CounterModal())

                            @discord.ui.button(label="❌ Decline Offer", style=discord.ButtonStyle.danger)
                            async def decline(self3, interaction3: discord.Interaction, button3: discord.ui.Button):
                                await self3._disable(interaction3)
                                try:
                                    dec_embed = discord.Embed(
                                        title="❌ Offer Declined",
                                        description=f"The seller declined your offer of **{self2.price.value}** for **{listing_name}**.",
                                        color=discord.Color.red()
                                    )
                                    dec_embed.set_footer(text="Adrian — Estand Marketplace")
                                    await buyer.send(embed=dec_embed)
                                    await interaction3.response.send_message("You declined the offer. The buyer has been notified.", ephemeral=True)
                                except discord.Forbidden:
                                    await interaction3.response.send_message("⚠️ Could not notify the buyer.", ephemeral=True)

                            @discord.ui.button(label="🚫 Block Buyer", style=discord.ButtonStyle.secondary)
                            async def block(self3, interaction3: discord.Interaction, button3: discord.ui.Button):
                                await self3._disable(interaction3)
                                await db_block_buyer(_seller_id, str(buyer.id), _thread_id)
                                try:
                                    block_embed = discord.Embed(title="🚫 Seller declined contact", description="The seller has declined further contact for this listing.", color=discord.Color.red())
                                    block_embed.set_footer(text="Adrian — Estand Marketplace")
                                    await buyer.send(embed=block_embed)
                                except discord.Forbidden:
                                    pass
                                await interaction3.response.send_message("🚫 Buyer blocked from this listing.", ephemeral=True)

                        await seller_user.send(embed=offer_embed, view=SellerOfferResponseView())
                        await interaction2.response.send_message("✅ Your offer has been sent to the seller!", ephemeral=True)
                        logger.info(f"[Estate] Offer sent by {buyer.id} to seller {_seller_id}: {self2.price.value}")
                    except discord.Forbidden:
                        await interaction2.response.send_message("⚠️ Could not DM the seller — they may have DMs disabled.", ephemeral=True)

            await interaction.response.send_modal(OfferModal())
        except Exception as e:
            logger.error(f"[Estate] MakeOffer error: {e}\n{traceback.format_exc()}")

    @discord.ui.button(label="Contact Seller", emoji="✉️", style=discord.ButtonStyle.secondary, custom_id="estate_contact_seller_direct")
    async def contact_seller_direct(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            self.seller_id = self._get_seller_id(interaction) or self.seller_id
            if str(interaction.user.id) == str(self.seller_id):
                await interaction.response.send_message("🚫 You can't contact yourself!", ephemeral=True)
                return
            if await db_is_buyer_blocked(self.seller_id, str(interaction.user.id), str(interaction.channel_id)):
                await interaction.response.send_message("🚫 The seller has declined contact for this listing.", ephemeral=True)
                return
            seller_user = await client.fetch_user(int(self.seller_id))
            if not seller_user:
                await interaction.response.send_message("⚠️ Could not find the seller.", ephemeral=True)
                return
            buyer = interaction.user
            listing_name = interaction.channel.name if interaction.channel else "your item"
            _seller_id = self.seller_id
            _thread_id = str(interaction.channel_id)

            class ContactModal(discord.ui.Modal, title="Message to Seller"):
                message = discord.ui.TextInput(
                    label="Your message",
                    style=discord.TextStyle.paragraph,
                    placeholder="Ask a question or send a message to the seller...",
                    max_length=1000
                )

                async def on_submit(self2, interaction2: discord.Interaction):
                    try:
                        msg_embed = discord.Embed(
                            title="✉️ Message about your listing",
                            description=self2.message.value,
                            color=discord.Color.dark_gold(),
                            timestamp=datetime.now(timezone.utc)
                        )
                        msg_embed.set_thumbnail(url=buyer.display_avatar.url)
                        msg_embed.add_field(name="From", value=f"{buyer.mention} ({buyer.display_name})", inline=True)
                        msg_embed.add_field(name="Listing", value=listing_name, inline=True)
                        msg_embed.set_footer(text="Adrian — Estand Marketplace")

                        class SellerReplyView(discord.ui.View):
                            def __init__(self):
                                super().__init__(timeout=86400)

                            async def _disable(self, inter):
                                for child in self.children:
                                    child.disabled = True
                                await inter.message.edit(view=self)

                            @discord.ui.button(label="💬 Reply", style=discord.ButtonStyle.primary)
                            async def reply(self3, interaction3: discord.Interaction, b: discord.ui.Button):
                                class ReplyModal(discord.ui.Modal, title="Reply to Buyer"):
                                    reply_msg = discord.ui.TextInput(label="Your reply", style=discord.TextStyle.paragraph, max_length=1000)
                                    async def on_submit(self4, interaction4: discord.Interaction):
                                        try:
                                            re_embed = discord.Embed(title="💬 Reply from seller", description=self4.reply_msg.value, color=discord.Color.dark_gold(), timestamp=datetime.now(timezone.utc))
                                            re_embed.add_field(name="From", value=f"<@{_seller_id}>", inline=True)
                                            re_embed.set_footer(text="Adrian — Estand Marketplace")
                                            await buyer.send(embed=re_embed)
                                            await interaction4.response.send_message("✅ Reply sent!", ephemeral=True)
                                        except discord.Forbidden:
                                            await interaction4.response.send_message("⚠️ Could not DM the buyer.", ephemeral=True)
                                await interaction3.response.send_modal(ReplyModal())

                            @discord.ui.button(label="🚫 Block", style=discord.ButtonStyle.danger)
                            async def block(self3, interaction3: discord.Interaction, b: discord.ui.Button):
                                await self3._disable(interaction3)
                                await db_block_buyer(_seller_id, str(buyer.id), _thread_id)
                                try:
                                    block_embed = discord.Embed(title="🚫 Seller declined contact", description="The seller has declined further contact for this listing.", color=discord.Color.red())
                                    block_embed.set_footer(text="Adrian — Estand Marketplace")
                                    await buyer.send(embed=block_embed)
                                except discord.Forbidden:
                                    pass
                                await interaction3.response.send_message("🚫 Buyer blocked.", ephemeral=True)

                        await seller_user.send(embed=msg_embed, view=SellerReplyView())
                        await interaction2.response.send_message("✅ Your message has been sent to the seller!", ephemeral=True)
                        logger.info(f"[Estate] Contact message sent by {buyer.id} to seller {_seller_id}")
                    except discord.Forbidden:
                        await interaction2.response.send_message("⚠️ Could not DM the seller — they may have DMs disabled.", ephemeral=True)

            await interaction.response.send_modal(ContactModal())
        except Exception as e:
            logger.error(f"[Estate] ContactSeller error: {e}\n{traceback.format_exc()}")

    @discord.ui.button(label="Report", emoji="🚩", style=discord.ButtonStyle.danger, custom_id="estate_report_listing")
    async def report_listing(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            listing_name = interaction.channel.name if interaction.channel else "Unknown listing"
            reporter = interaction.user
            _seller_id = self.seller_id

            class ReportModal(discord.ui.Modal, title="Report This Listing"):
                reason = discord.ui.TextInput(
                    label="Reason for report",
                    style=discord.TextStyle.paragraph,
                    placeholder="Describe the issue (scam, fake item, misleading description, etc.)",
                    max_length=1000
                )

                async def on_submit(self2, interaction2: discord.Interaction):
                    try:
                        guild = interaction2.guild
                        report_embed = discord.Embed(
                            title="🚩 Listing Report",
                            description=self2.reason.value,
                            color=discord.Color.red(),
                            timestamp=datetime.now(timezone.utc)
                        )
                        report_embed.add_field(name="Reporter", value=f"{reporter.mention} ({reporter.display_name})", inline=True)
                        report_embed.add_field(name="Seller", value=f"<@{_seller_id}>", inline=True)
                        report_embed.add_field(name="Listing", value=listing_name, inline=True)
                        report_embed.add_field(name="Server", value=guild.name if guild else "Unknown", inline=True)
                        report_embed.set_footer(text="Adrian — Estand Marketplace")

                        class OwnerReportView(discord.ui.View):
                            def __init__(self):
                                super().__init__(timeout=None)

                            @discord.ui.button(label="⚠️ Warn Reporter", style=discord.ButtonStyle.secondary)
                            async def warn_reporter(self3, interaction3: discord.Interaction, b: discord.ui.Button):
                                class WarnModal(discord.ui.Modal, title="Send Warning to Reporter"):
                                    custom_msg = discord.ui.TextInput(
                                        label="Custom message (optional)",
                                        style=discord.TextStyle.paragraph,
                                        placeholder="Add a custom note or leave blank for default message...",
                                        required=False,
                                        max_length=500
                                    )
                                    async def on_submit(self4, interaction4: discord.Interaction):
                                        try:
                                            default_msg = "We have reviewed your report. At this time, no action will be taken because the server guidelines have not been violated."
                                            final_msg = self4.custom_msg.value if self4.custom_msg.value else default_msg
                                            warn_embed = discord.Embed(
                                                title="⚠️ Report Review",
                                                description=final_msg,
                                                color=discord.Color.orange(),
                                                timestamp=datetime.now(timezone.utc)
                                            )
                                            warn_embed.add_field(name="Server", value=guild.name if guild else "Unknown", inline=True)
                                            warn_embed.set_footer(text="Adrian — Estand Marketplace")
                                            await reporter.send(embed=warn_embed)
                                            # Log warning on reporter's profile
                                            await db_add_user_warning(
                                                str(reporter.id),
                                                f"False/invalid report: {listing_name}. {final_msg}",
                                                warning_type="report_abuse",
                                                issued_by=str(interaction4.user.id),
                                                guild_id=str(guild.id) if guild else None
                                            )
                                            await interaction4.response.send_message("✅ Warning sent to reporter and logged on their profile.", ephemeral=True)
                                            logger.info(f"[Report] Warning issued to reporter {reporter.id} by {interaction4.user.id}")
                                        except discord.Forbidden:
                                            await interaction4.response.send_message("⚠️ Could not DM the reporter.", ephemeral=True)
                                await interaction3.response.send_modal(WarnModal())

                            @discord.ui.button(label="🗑️ Delete from my Estand", style=discord.ButtonStyle.danger)
                            async def delete_listing(self3, interaction3: discord.Interaction, b: discord.ui.Button):
                                try:
                                    thread = guild.get_thread(interaction2.channel_id) if guild else None
                                    if thread:
                                        await thread.delete()
                                        await interaction3.response.send_message("✅ Listing deleted from your Estand.", ephemeral=True)
                                        logger.info(f"[Report] Server owner deleted listing {interaction2.channel_id} from {guild.name if guild else 'unknown'}")
                                    else:
                                        await interaction3.response.send_message("⚠️ Could not find the listing — it may have already been deleted.", ephemeral=True)
                                except discord.Forbidden:
                                    await interaction3.response.send_message("⚠️ Missing permissions to delete the thread.", ephemeral=True)

                            @discord.ui.button(label="🚨 Report Member", style=discord.ButtonStyle.danger)
                            async def report_member(self3, interaction3: discord.Interaction, b: discord.ui.Button):
                                class ReportMemberView(discord.ui.View):
                                    def __init__(self):
                                        super().__init__(timeout=300)

                                    @discord.ui.select(
                                        placeholder="Select report type...",
                                        options=[
                                            discord.SelectOption(label="Scammer", value="scammer", emoji="🚨", description="This user is attempting to scam buyers or sellers"),
                                            discord.SelectOption(label="Other", value="other", emoji="📋", description="Other rule violation or concern"),
                                        ]
                                    )
                                    async def select_type(self4, interaction4: discord.Interaction, select: discord.ui.Select):
                                        report_type = select.values[0]

                                        class BotOwnerReportModal(discord.ui.Modal, title=f"Report Member — {report_type.title()}"):
                                            details = discord.ui.TextInput(
                                                label="Details",
                                                style=discord.TextStyle.paragraph,
                                                placeholder="Provide any additional details...",
                                                max_length=1000
                                            )

                                            async def on_submit(self5, interaction5: discord.Interaction):
                                                try:
                                                    owner_channel = client.get_channel(1513670729194016778)
                                                    if owner_channel:
                                                        owner_embed = discord.Embed(
                                                            title=f"🚨 Member Report — {report_type.title()}",
                                                            description=self5.details.value,
                                                            color=discord.Color.red(),
                                                            timestamp=datetime.now(timezone.utc)
                                                        )
                                                        owner_embed.add_field(name="Reported By (Server Owner)", value=f"{interaction3.user.mention} ({interaction3.user.display_name})", inline=True)
                                                        owner_embed.add_field(name="Reported User (Seller)", value=f"<@{_seller_id}>", inline=True)
                                                        owner_embed.add_field(name="Listing", value=listing_name, inline=True)
                                                        owner_embed.add_field(name="Server", value=guild.name if guild else "Unknown", inline=True)
                                                        owner_embed.add_field(name="Report Type", value=report_type.title(), inline=True)
                                                        owner_embed.set_footer(text="Adrian — Admin Report")
                                                        await owner_channel.send(embed=owner_embed)
                                                    await interaction5.response.send_message("✅ Report submitted to Adrian admin.", ephemeral=True)
                                                    logger.info(f"[Report] Member report submitted: seller={_seller_id} type={report_type} by={interaction3.user.id}")
                                                except Exception as e:
                                                    logger.error(f"[Report] Owner report error: {e}")
                                                    await interaction5.response.send_message("⚠️ Something went wrong submitting the report.", ephemeral=True)

                                        await interaction4.response.send_modal(BotOwnerReportModal())

                                await interaction3.response.send_message(
                                    "Select the report type:",
                                    view=ReportMemberView(),
                                    ephemeral=True
                                )

                        # Try to get listing image from thread starter message
                        try:
                            if isinstance(interaction2.channel, discord.Thread):
                                starter = await interaction2.channel.fetch_message(interaction2.channel.id)
                                if starter and starter.attachments:
                                    report_embed.set_thumbnail(url=starter.attachments[0].url)
                                elif starter and starter.embeds and starter.embeds[0].image:
                                    report_embed.set_thumbnail(url=starter.embeds[0].image.url)
                        except Exception:
                            pass

                        # Build owner action view with full controls
                        class BotOwnerReportActionView(discord.ui.View):
                            def __init__(self):
                                super().__init__(timeout=None)

                            @discord.ui.button(label="⚠️ Warn Reporter", style=discord.ButtonStyle.secondary, row=0)
                            async def warn_reporter_btn(self3, interaction3: discord.Interaction, b: discord.ui.Button):
                                class WarnReporterModal(discord.ui.Modal, title="Warn Reporter"):
                                    custom_msg = discord.ui.TextInput(
                                        label="Warning message",
                                        style=discord.TextStyle.paragraph,
                                        placeholder="Leave blank for default message...",
                                        required=False,
                                        max_length=500
                                    )
                                    async def on_submit(self4, interaction4: discord.Interaction):
                                        try:
                                            default_msg = "We have reviewed your report. At this time, no action will be taken as no guidelines were violated."
                                            final_msg = self4.custom_msg.value if self4.custom_msg.value else default_msg
                                            warn_embed = discord.Embed(
                                                title="⚠️ Report Review",
                                                description=final_msg,
                                                color=discord.Color.orange(),
                                                timestamp=datetime.now(timezone.utc)
                                            )
                                            warn_embed.set_footer(text="Adrian — Estand Marketplace")
                                            await reporter.send(embed=warn_embed)
                                            await db_add_user_warning(
                                                str(reporter.id),
                                                f"False/invalid report on listing: {listing_name}. {final_msg}",
                                                warning_type="report_abuse",
                                                issued_by=str(interaction4.user.id),
                                                guild_id=str(guild.id) if guild else None
                                            )
                                            # Log action to report channel
                                            action_embed = discord.Embed(
                                                title="📋 Action Taken — Warning Sent",
                                                description=f"**{interaction4.user.display_name}** warned reporter {reporter.mention}",
                                                color=discord.Color.orange(),
                                                timestamp=datetime.now(timezone.utc)
                                            )
                                            action_embed.add_field(name="Warning Message", value=final_msg, inline=False)
                                            action_embed.add_field(name="Listing", value=listing_name, inline=True)
                                            action_embed.set_footer(text="Adrian — Report Log")
                                            report_log = client.get_channel(1515954657975992401)
                                            if report_log:
                                                await report_log.send(embed=action_embed)
                                            await interaction4.response.send_message(f"✅ Warning sent to {reporter.display_name} and logged.", ephemeral=True)
                                        except discord.Forbidden:
                                            await interaction4.response.send_message("⚠️ Could not DM the reporter.", ephemeral=True)
                                await interaction3.response.send_modal(WarnReporterModal())

                            @discord.ui.button(label="🗑️ Delete Listing", style=discord.ButtonStyle.danger, row=0)
                            async def delete_listing_btn(self3, interaction3: discord.Interaction, b: discord.ui.Button):
                                try:
                                    thread = None
                                    if guild:
                                        thread = guild.get_thread(interaction2.channel_id)
                                    if thread:
                                        await thread.delete()
                                        action_embed = discord.Embed(
                                            title="📋 Action Taken — Listing Deleted",
                                            description=f"**{interaction3.user.display_name}** deleted listing **{listing_name}**",
                                            color=discord.Color.red(),
                                            timestamp=datetime.now(timezone.utc)
                                        )
                                        action_embed.add_field(name="Server", value=guild.name if guild else "Unknown", inline=True)
                                        action_embed.add_field(name="Seller", value=f"<@{_seller_id}>", inline=True)
                                        action_embed.set_footer(text="Adrian — Report Log")
                                        report_log = client.get_channel(1515954657975992401)
                                        if report_log:
                                            await report_log.send(embed=action_embed)
                                        await interaction3.response.send_message("✅ Listing deleted and logged.", ephemeral=True)
                                    else:
                                        await interaction3.response.send_message("⚠️ Could not find the listing — it may already be deleted.", ephemeral=True)
                                except discord.Forbidden:
                                    await interaction3.response.send_message("⚠️ Missing permissions to delete.", ephemeral=True)

                            @discord.ui.button(label="🚨 Warn Seller", style=discord.ButtonStyle.danger, row=0)
                            async def warn_seller_btn(self3, interaction3: discord.Interaction, b: discord.ui.Button):
                                class WarnSellerModal(discord.ui.Modal, title="Warn Seller"):
                                    custom_msg = discord.ui.TextInput(
                                        label="Warning message",
                                        style=discord.TextStyle.paragraph,
                                        placeholder="Describe the violation...",
                                        max_length=500
                                    )
                                    async def on_submit(self4, interaction4: discord.Interaction):
                                        try:
                                            seller_user = await client.fetch_user(int(_seller_id))
                                            warn_embed = discord.Embed(
                                                title="⚠️ Listing Warning",
                                                description=self4.custom_msg.value,
                                                color=discord.Color.red(),
                                                timestamp=datetime.now(timezone.utc)
                                            )
                                            warn_embed.add_field(name="Listing", value=listing_name, inline=True)
                                            warn_embed.set_footer(text="Adrian — Estand Marketplace")
                                            await seller_user.send(embed=warn_embed)
                                            await db_add_user_warning(
                                                str(_seller_id),
                                                f"Listing warning: {listing_name}. {self4.custom_msg.value}",
                                                warning_type="listing_violation",
                                                issued_by=str(interaction4.user.id),
                                                guild_id=str(guild.id) if guild else None
                                            )
                                            action_embed = discord.Embed(
                                                title="📋 Action Taken — Seller Warned",
                                                description=f"**{interaction4.user.display_name}** warned seller <@{_seller_id}>",
                                                color=discord.Color.red(),
                                                timestamp=datetime.now(timezone.utc)
                                            )
                                            action_embed.add_field(name="Warning", value=self4.custom_msg.value, inline=False)
                                            action_embed.add_field(name="Listing", value=listing_name, inline=True)
                                            action_embed.set_footer(text="Adrian — Report Log")
                                            report_log = client.get_channel(1515954657975992401)
                                            if report_log:
                                                await report_log.send(embed=action_embed)
                                            await interaction4.response.send_message(f"✅ Warning sent to seller and logged.", ephemeral=True)
                                        except discord.Forbidden:
                                            await interaction4.response.send_message("⚠️ Could not DM the seller.", ephemeral=True)
                                await interaction3.response.send_modal(WarnSellerModal())

                            @discord.ui.button(label="✅ No Action", style=discord.ButtonStyle.secondary, row=1)
                            async def no_action_btn(self3, interaction3: discord.Interaction, b: discord.ui.Button):
                                action_embed = discord.Embed(
                                    title="📋 No Action Taken",
                                    description=f"**{interaction3.user.display_name}** reviewed and dismissed report on **{listing_name}**",
                                    color=discord.Color.greyple(),
                                    timestamp=datetime.now(timezone.utc)
                                )
                                action_embed.set_footer(text="Adrian — Report Log")
                                report_log = client.get_channel(1515954657975992401)
                                if report_log:
                                    await report_log.send(embed=action_embed)
                                for child in self3.children:
                                    child.disabled = True
                                await interaction3.message.edit(view=self3)
                                await interaction3.response.send_message("✅ Report dismissed and logged.", ephemeral=True)

                        # Post to bot report log channel with full action buttons
                        report_log_channel = client.get_channel(1515954657975992401)
                        if report_log_channel:
                            await report_log_channel.send(embed=report_embed, view=BotOwnerReportActionView())
                            logger.info(f"[Estate] Report logged to report channel")

                        # DM server owner with same controls
                        if guild and guild.owner:
                            try:
                                await guild.owner.send(embed=report_embed, view=BotOwnerReportActionView())
                            except discord.Forbidden:
                                logger.warning(f"[Estate] Could not DM server owner for report")

                        # Post to mod log if configured
                        config = await db_get_server_config(str(guild.id)) if guild else None
                        mod_log_id = get_config_value(config, "mod_log_channel_id") if config else None
                        if mod_log_id:
                            mod_channel = guild.get_channel(int(mod_log_id)) if guild else None
                            if mod_channel:
                                await mod_channel.send(embed=report_embed, view=BotOwnerReportActionView())

                        await interaction2.response.send_message("✅ Your report has been submitted.", ephemeral=True)
                        logger.info(f"[Estate] Report submitted by {reporter.id} on listing by {_seller_id}")
                    except discord.Forbidden:
                        await interaction2.response.send_message("⚠️ Could not reach the server owner.", ephemeral=True)

            await interaction.response.send_modal(ReportModal())
        except Exception as e:
            logger.error(f"[Estate] Report error: {e}\n{traceback.format_exc()}")

# ==================== ESTATE BUYER ID VIEW ====================

class BuyerIdentifyView(discord.ui.View):
    def __init__(self, thread_id, seller_id):
        super().__init__(timeout=None)
        self.thread_id = thread_id
        self.seller_id = seller_id

    @discord.ui.button(label="I'm the Buyer", emoji="🙋", style=discord.ButtonStyle.primary, custom_id="estate_buyer_claim")
    async def claim_buyer(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            user_id = str(interaction.user.id)
            # Block seller from claiming they are the buyer
            if user_id == str(self.seller_id):
                await interaction.response.send_message("🚫 You cannot identify yourself as the buyer of your own listing.", ephemeral=True)
                return
            # Save buyer to transaction
            await db_set_transaction_buyer(self.thread_id, user_id)
            await interaction.response.send_message(f"✅ Got it! The seller will now be prompted to rate you.", ephemeral=True)
            # Disable the button on the message
            for item in self.children:
                item.disabled = True
            await interaction.message.edit(view=self)
            # Now prompt the seller to rate the buyer
            try:
                seller = await client.fetch_user(int(self.seller_id))
                if seller:
                    rating_embed = discord.Embed(
                        title="⭐ Rate Your Buyer",
                        description=f"How was your experience selling to **{interaction.user.display_name}**?\n\nClick a star rating below:",
                        color=discord.Color.dark_gold(),
                        timestamp=datetime.now(timezone.utc)
                    )
                    rating_embed.set_footer(text="Adrian — Forum Alert | You may need to make a free forum account to see this listing")
                    await seller.send(embed=rating_embed, view=EstateRatingView(self.thread_id, str(interaction.user.id), self.seller_id))
            except Exception as e:
                logger.error(f"[Estate] Could not DM seller: {e}")
        except Exception as e:
            logger.error(f"[Estate] BuyerIdentify error: {e}\n{traceback.format_exc()}")
            try:
                await interaction.response.send_message("⚠️ Something went wrong. Please try again.", ephemeral=True)
            except Exception: pass

class EstateRatingView(discord.ui.View):
    def __init__(self, thread_id, buyer_id, seller_id):
        super().__init__(timeout=None)
        self.thread_id = thread_id
        self.buyer_id = buyer_id
        self.seller_id = seller_id

    async def _rate(self, interaction, stars):
        try:
            await db_add_estate_rating(self.buyer_id, self.seller_id, self.thread_id, stars)
            await db_complete_transaction(self.thread_id, stars)
            for item in self.children:
                item.disabled = True
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="✅ Rating Submitted!",
                    description=f"You rated this buyer **{'⭐' * stars}**. Thank you!",
                    color=discord.Color.green()
                ),
                view=self
            )
            logger.info(f"[Estate] Rating {stars}★ submitted for buyer {self.buyer_id}")
        except Exception as e:
            logger.error(f"[Estate] Rating error: {e}")
            try:
                await interaction.response.send_message("⚠️ Something went wrong.", ephemeral=True)
            except Exception: pass

    @discord.ui.button(emoji="⭐", label="1", style=discord.ButtonStyle.secondary, custom_id="estate_rate_1")
    async def rate_1(self, i, b): await self._rate(i, 1)
    @discord.ui.button(emoji="⭐", label="2", style=discord.ButtonStyle.secondary, custom_id="estate_rate_2")
    async def rate_2(self, i, b): await self._rate(i, 2)
    @discord.ui.button(emoji="⭐", label="3", style=discord.ButtonStyle.secondary, custom_id="estate_rate_3")
    async def rate_3(self, i, b): await self._rate(i, 3)
    @discord.ui.button(emoji="⭐", label="4", style=discord.ButtonStyle.secondary, custom_id="estate_rate_4")
    async def rate_4(self, i, b): await self._rate(i, 4)
    @discord.ui.button(emoji="⭐", label="5", style=discord.ButtonStyle.secondary, custom_id="estate_rate_5")
    async def rate_5(self, i, b): await self._rate(i, 5)

# ==================== MILITARIA ALERT AD BUTTON ====================

class MilitariaAlertAdView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(
            label="Buy Now — $1/month",
            emoji="🛒",
            style=discord.ButtonStyle.link,
            url="https://www.militariaalert.com"
        ))

# ==================== WAF WATCH ITEM BUTTONS ====================

class WatchItemView(discord.ui.View):
    def __init__(self, forum_url, item_title, price=""):
        super().__init__(timeout=None)
        self.forum_url = forum_url
        self.item_title = item_title
        self.price = price

    @discord.ui.button(emoji="🔔", style=discord.ButtonStyle.secondary, custom_id="watch_item")
    async def watch(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            user_id = str(interaction.user.id)
            if await db_is_watching(user_id, self.forum_url):
                await interaction.response.send_message(f"⚠️ You are already watching **{self.item_title}**!", ephemeral=True)
                return
            await db_watch_item(user_id, self.forum_url, self.item_title, self.price)
            await interaction.response.send_message(f"🔔 You are now watching **{self.item_title}**! You will be notified of any price changes or updates.", ephemeral=True)
        except Exception as e:
            logger.error(f"[WatchItem] Watch button error: {e}\n{traceback.format_exc()}")
            try:
                await interaction.response.send_message("⚠️ Something went wrong. Please try again.", ephemeral=True)
            except Exception: pass

    @discord.ui.button(emoji="🔕", style=discord.ButtonStyle.secondary, custom_id="unwatch_item")
    async def unwatch(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            user_id = str(interaction.user.id)
            if not await db_is_watching(user_id, self.forum_url):
                await interaction.response.send_message(f"⚠️ You are not watching **{self.item_title}**.", ephemeral=True)
                return
            await db_unwatch_item(user_id, self.forum_url)
            await interaction.response.send_message(f"🔕 You have stopped watching **{self.item_title}**.", ephemeral=True)
        except Exception as e:
            logger.error(f"[WatchItem] Unwatch button error: {e}\n{traceback.format_exc()}")
            try:
                await interaction.response.send_message("⚠️ Something went wrong. Please try again.", ephemeral=True)
            except Exception: pass

    @discord.ui.button(emoji="📬", style=discord.ButtonStyle.secondary, custom_id="send_to_dm")
    async def send_to_dm(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            price_line = f"\n💰 **{self.price}**" if self.price else ""
            dm_embed = discord.Embed(
                title=f"📌 Bookmarked: {self.item_title}",
                description=f"You saved this listing for later.{price_line}\n\n[**View Listing →**]({self.forum_url})",
                color=discord.Color.dark_gold(),
                timestamp=datetime.now(timezone.utc)
            )
            dm_embed.set_footer(text="Adrian — Bookmark")
            await interaction.user.send(embed=dm_embed)
            await interaction.response.send_message(f"📬 **{self.item_title}** has been sent to your DMs!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("⚠️ I couldn't DM you — please enable DMs from server members in Discord privacy settings.", ephemeral=True)
        except Exception as e:
            logger.error(f"[WatchItem] DM bookmark failed: {e}\n{traceback.format_exc()}")
            try:
                await interaction.response.send_message("⚠️ Something went wrong sending the DM.", ephemeral=True)
            except Exception: pass

# ==================== FOLLOW DEALER BUTTONS ====================

class FollowDealerView(discord.ui.View):
    def __init__(self, dealer_name):
        super().__init__(timeout=None)
        self.dealer_name = dealer_name

    @discord.ui.button(emoji="🔔", style=discord.ButtonStyle.secondary, custom_id="follow_dealer")
    async def follow(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Get dealer name from embed if self.dealer_name is placeholder
        dealer_name = self.dealer_name
        if dealer_name == "placeholder" and interaction.message and interaction.message.embeds:
            dealer_name = interaction.message.embeds[0].author.name or dealer_name
        user_id = str(interaction.user.id)
        can_follow, reason = await db_can_follow_dealer(user_id)
        if not can_follow:
            await interaction.response.send_message(f"⚠️ {reason}", ephemeral=True)
            return
        if await db_is_following(user_id, dealer_name):
            await interaction.response.send_message(f"⚠️ You are already following **{dealer_name}**!", ephemeral=True)
            return
        await db_follow_dealer(user_id, dealer_name)
        await interaction.response.send_message(f"🔔 Now following **{dealer_name}**! You'll get a DM whenever they post new items.", ephemeral=True)

    @discord.ui.button(emoji="🔕", style=discord.ButtonStyle.secondary, custom_id="unfollow_dealer")
    async def unfollow(self, interaction: discord.Interaction, button: discord.ui.Button):
        dealer_name = self.dealer_name
        if dealer_name == "placeholder" and interaction.message and interaction.message.embeds:
            dealer_name = interaction.message.embeds[0].author.name or dealer_name
        user_id = str(interaction.user.id)
        if not await db_is_following(user_id, dealer_name):
            await interaction.response.send_message(f"⚠️ You are not following **{dealer_name}**.", ephemeral=True)
            return
        await db_unfollow_dealer(user_id, dealer_name)
        await interaction.response.send_message(f"🔕 Unfollowed **{dealer_name}**.", ephemeral=True)

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
        except Exception:
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

# ==================== COUNTRY FLAGS ====================
COUNTRY_FLAGS = {
    "Z": "0️⃣", "A": "🇺🇸", "B": "🇬🇧", "C": "🇨🇦", "M": "🇨🇳",
    "D": "🇩🇪", "E": "🇷🇺", "F": "🇫🇷", "G": "🇯🇵",
    "H": "🇮🇹", "I": "🇦🇹", "J": "🏳️", "K": "🌍", "L": "🌐",
}

COUNTRY_NAMES = {
    "Z": "All Countries", "A": "American", "B": "British/Commonwealth",
    "C": "Canadian", "M": "Chinese/KMT", "D": "German", "E": "Soviet/Russian",
    "F": "French", "G": "Japanese", "H": "Italian",
    "I": "Austro-Hungarian", "J": "Other Axis", "K": "Other Allied", "L": "Multi-country",
}

class CountrySelectView(discord.ui.View):
    def __init__(self, selected_countries=None):
        super().__init__(timeout=None)
        self.selected = set(selected_countries or [])

    async def _toggle(self, interaction, code):
        try:
            if code in self.selected:
                self.selected.discard(code)
            else:
                self.selected.add(code)
            selected_list = sorted(self.selected)
            country_display = " ".join([COUNTRY_FLAGS.get(c, c) for c in selected_list]) if selected_list else "None selected"

            embeds = []
            if bot_state.get("question3_img_url"):
                img_embed = discord.Embed(color=discord.Color.dark_gold())
                img_embed.set_image(url=bot_state["question3_img_url"])
                embeds.append(img_embed)

            description = (
                "0️⃣ All Countries\n"
                "🇺🇸 American\n"
                "🇬🇧 British / Commonwealth\n"
                "🇨🇦 Canadian\n"
                "🇩🇪 German\n"
                "🇷🇺 Soviet / Russian\n"
                "🇫🇷 French\n"
                "🇯🇵 Japanese\n"
                "🇮🇹 Italian\n"
                "🇦🇹 Austro-Hungarian\n"
                "🏳️ Other Axis\n"
                "🌍 Other Allied\n"
                "🌐 Multi-country / General\n"
                "🇨🇳 Chinese / KMT\n\n"
                f"**Selected:** {country_display}\n"
                "**Click Done when finished.**"
            )
            text_embed = discord.Embed(description=description, color=discord.Color.dark_gold())
            text_embed.set_footer(text="Adrian — Discord's #1 Militaria Bot")
            embeds.append(text_embed)

            if interaction.response.is_done():
                await interaction.edit_original_response(embeds=embeds, view=CountrySelectView(list(self.selected)))
            else:
                await interaction.response.edit_message(embeds=embeds, view=CountrySelectView(list(self.selected)))
        except Exception as e:
            logger.error(f"[CountrySelect] Toggle error: {e}\n{traceback.format_exc()}")
            try:
                await interaction.response.send_message("⚠️ Something went wrong. Please try again.", ephemeral=True)
            except Exception: pass

    @discord.ui.button(emoji="0️⃣", style=discord.ButtonStyle.secondary, custom_id="country_Z")
    async def c_all(self, i, b): await self._toggle(i, "Z")
    @discord.ui.button(emoji="🇺🇸", style=discord.ButtonStyle.secondary, custom_id="country_A")
    async def c_a(self, i, b): await self._toggle(i, "A")
    @discord.ui.button(emoji="🇬🇧", style=discord.ButtonStyle.secondary, custom_id="country_B")
    async def c_b(self, i, b): await self._toggle(i, "B")
    @discord.ui.button(emoji="🇨🇦", style=discord.ButtonStyle.secondary, custom_id="country_C")
    async def c_c(self, i, b): await self._toggle(i, "C")
    @discord.ui.button(emoji="🇨🇳", style=discord.ButtonStyle.secondary, custom_id="country_M")
    async def c_m(self, i, b): await self._toggle(i, "M")
    @discord.ui.button(emoji="🇩🇪", style=discord.ButtonStyle.secondary, custom_id="country_D")
    async def c_d(self, i, b): await self._toggle(i, "D")
    @discord.ui.button(emoji="🇷🇺", style=discord.ButtonStyle.secondary, custom_id="country_E")
    async def c_e(self, i, b): await self._toggle(i, "E")
    @discord.ui.button(emoji="🇫🇷", style=discord.ButtonStyle.secondary, custom_id="country_F")
    async def c_f(self, i, b): await self._toggle(i, "F")
    @discord.ui.button(emoji="🇯🇵", style=discord.ButtonStyle.secondary, custom_id="country_G")
    async def c_g(self, i, b): await self._toggle(i, "G")
    @discord.ui.button(emoji="🇮🇹", style=discord.ButtonStyle.secondary, custom_id="country_H")
    async def c_h(self, i, b): await self._toggle(i, "H")
    @discord.ui.button(emoji="🇦🇹", style=discord.ButtonStyle.secondary, custom_id="country_I")
    async def c_i(self, i, b): await self._toggle(i, "I")
    @discord.ui.button(emoji="🏳️", style=discord.ButtonStyle.secondary, custom_id="country_J")
    async def c_j(self, i, b): await self._toggle(i, "J")
    @discord.ui.button(emoji="🌍", style=discord.ButtonStyle.secondary, custom_id="country_K")
    async def c_k(self, i, b): await self._toggle(i, "K")
    @discord.ui.button(emoji="🌐", style=discord.ButtonStyle.secondary, custom_id="country_L")
    async def c_l(self, i, b): await self._toggle(i, "L")
    @discord.ui.button(label="✅ Done", style=discord.ButtonStyle.success, custom_id="country_done")
    async def c_done(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.selected:
            await interaction.response.send_message("⚠️ Please select at least one country.", ephemeral=True)
            return
        await db_set_user_countries(str(interaction.user.id), list(self.selected))
        await show_question4(interaction, edit=True)

# ==================== ERA SELECT VIEW ====================

ERA_EMOJIS = {
    0: "⚪",  # All eras
    1: "🟤",  # Pre-1914
    2: "🟡",  # WWI
    3: "🔴",  # WWII
    4: "🔵",  # Korean War
    5: "🟢",  # Vietnam
    6: "🟣",  # Cold War
    7: "🟠",  # GWOT
}

ERA_NAMES = {
    0: "All Eras",
    1: "Pre-1914",
    2: "WWI (1914–1918)",
    3: "WWII (1939–1945)",
    4: "Korean War (1950–1953)",
    5: "Vietnam War (1955–1975)",
    6: "Cold War (1947–1991)",
    7: "GWOT / Modern (2001–present)",
}

async def db_get_user_forums(user_id):
    async with client.db.acquire() as conn:
        row = await conn.fetchrow("SELECT forums FROM user_preferences WHERE user_id=$1", str(user_id))
        return row["forums"] if row else None

async def db_set_user_forums(user_id, forums_choice):
    async with client.db.acquire() as conn:
        await conn.execute(
            "UPDATE user_preferences SET forums=$1, updated_at=$2 WHERE user_id=$3",
            forums_choice, int(datetime.now(timezone.utc).timestamp()), str(user_id)
        )

# ==================== /START ONBOARDING ====================

async def db_get_users_for_keyword(keyword):
    """Get users who have keyword alerts for this term (Premium feature — stub)."""
    return []


async def db_save_user_waf_categories(user_id, category_names):
    """Save user WAF category subscriptions."""
    cats_str = ",".join(category_names)
    now = int(datetime.now(timezone.utc).timestamp())
    async with client.db.acquire() as conn:
        await conn.execute(
            """INSERT INTO user_preferences (user_id, waf_categories, created_at, updated_at)
               VALUES ($1, $2, $3, $3)
               ON CONFLICT (user_id) DO UPDATE SET waf_categories=$2, updated_at=$3""",
            str(user_id), cats_str, now
        )
    logger.info(f"[DB] WAF categories saved for {user_id}: {cats_str}")

async def db_save_user_usmf_categories(user_id, category_names):
    """Save user USMF category subscriptions."""
    cats_str = ",".join(category_names)
    now = int(datetime.now(timezone.utc).timestamp())
    async with client.db.acquire() as conn:
        await conn.execute(
            """INSERT INTO user_preferences (user_id, usmf_categories, created_at, updated_at)
               VALUES ($1, $2, $3, $3)
               ON CONFLICT (user_id) DO UPDATE SET usmf_categories=$2, updated_at=$3""",
            str(user_id), cats_str, now
        )
    logger.info(f"[DB] USMF categories saved for {user_id}: {cats_str}")



BOT_RULES_TEXT = (
    "**1.** Be respectful — no harassment, hate speech or discrimination\n"
    "**2.** One account only — ban evasion results in a permanent ban\n"
    "**3.** No spam or command abuse\n"
    "**4.** Follow Discord\'s Terms of Service"
)

ESTAND_RULES_TEXT = (
    "**1.** All items must be accurately described and honestly represented\n"
    "**2.** No fakes or reproductions listed as originals\n"
    "**3.** No stolen or looted artifacts\n"
    "**4.** No scamming — fraud results in a permanent ban from all Adrian servers\n"
    "**5.** Honor your deals — if you agree to a sale, complete it\n"
    "**6.** No price gouging\n"
    "**7.** Disputes must be handled through Adrian\'s dispute system"
)


async def start_step1_bot_rules(interaction):
    """Step 1 — Bot rules agreement."""
    embed = discord.Embed(
        title="📋 Adrian Bot Rules",
        description=(
            "Before getting started, please read and agree to the following rules:\n\n"
            + BOT_RULES_TEXT +
            "\n\nBy clicking **I Agree** you confirm you have read and will follow these rules."
        ),
        color=discord.Color.dark_gold()
    )
    embed.set_footer(text="Adrian — Step 1 of 8")

    class BotRulesView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)

        @discord.ui.button(label="✅ I Agree", style=discord.ButtonStyle.success)
        async def agree(self2, interaction2: discord.Interaction, button: discord.ui.Button):
            await interaction2.response.defer(ephemeral=True)
            # Assign Adrian Verified role
            try:
                config = await db_get_server_config(str(interaction2.guild.id))
                role_id = get_config_value(config, "verified_role_id") if config else None
                role = interaction2.guild.get_role(int(role_id)) if role_id else None
                if not role:
                    role = discord.utils.get(interaction2.guild.roles, name="Adrian Verified")
                if role:
                    member = interaction2.guild.get_member(interaction2.user.id)
                    if member and role not in member.roles:
                        await member.add_roles(role, reason="Agreed to bot rules via /start")
                        logger.info(f"[Start] Adrian Verified assigned to {interaction2.user} in {interaction2.guild.name}")
            except Exception as e:
                logger.error(f"[Start] Could not assign Adrian Verified: {e}")
            await start_step2_estand_rules(interaction2)

        @discord.ui.button(label="❌ Decline", style=discord.ButtonStyle.danger)
        async def decline(self2, interaction2: discord.Interaction, button: discord.ui.Button):
            await interaction2.response.edit_message(
                embed=discord.Embed(
                    title="❌ Rules Declined",
                    description=(
                        "You need to agree to the bot rules to use Adrian.\n\n"
                        "Run `/start` again when you\'re ready to agree."
                    ),
                    color=discord.Color.red()
                ),
                view=None
            )

    await interaction.edit_original_response(embed=embed, view=BotRulesView())


async def start_step2_estand_rules(interaction):
    """Step 2 — Estand rules agreement."""
    embed = discord.Embed(
        title="🏪 Estand Marketplace Rules",
        description=(
            "The Estand is Adrian\'s buy & sell marketplace for militaria collectors.\n\n"
            + ESTAND_RULES_TEXT +
            "\n\nAgree to access the Estand. You can skip and come back to this anytime by running `/start` again."
        ),
        color=discord.Color.dark_gold()
    )
    embed.set_footer(text="Adrian — Step 2 of 8")

    class EstartRulesView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)

        @discord.ui.button(label="✅ I Agree", style=discord.ButtonStyle.success)
        async def agree(self2, interaction2: discord.Interaction, button: discord.ui.Button):
            await interaction2.response.defer(ephemeral=True)
            # Save estand agreement and assign role
            try:
                now = int(datetime.now(timezone.utc).timestamp())
                async with client.db.acquire() as conn:
                    await conn.execute(
                        "INSERT INTO user_preferences (user_id, estand_agreed, created_at, updated_at) VALUES ($1, 1, $2, $2) ON CONFLICT (user_id) DO UPDATE SET estand_agreed=1, updated_at=$2",
                        str(interaction2.user.id), now
                    )
                config = await db_get_server_config(str(interaction2.guild.id))
                role_id = get_config_value(config, "estand_verified_role_id") if config else None
                role = interaction2.guild.get_role(int(role_id)) if role_id else None
                if not role:
                    role = discord.utils.get(interaction2.guild.roles, name="Estand Verified")
                if role:
                    member = interaction2.guild.get_member(interaction2.user.id)
                    if member and role not in member.roles:
                        await member.add_roles(role, reason="Agreed to Estand rules via /start")
                        logger.info(f"[Start] Estand Verified assigned to {interaction2.user} in {interaction2.guild.name}")
            except Exception as e:
                logger.error(f"[Start] Estand agreement error: {e}")
            await start_step3_dealer_region(interaction2)

        @discord.ui.button(label="⏭️ Skip for Now", style=discord.ButtonStyle.secondary)
        async def skip(self2, interaction2: discord.Interaction, button: discord.ui.Button):
            await interaction2.response.defer(ephemeral=True)
            await start_step3_dealer_region(interaction2)

    await interaction.edit_original_response(embed=embed, view=EstartRulesView())


async def start_step3_dealer_region(interaction):
    """Step 3 — Dealer region selection."""
    embed = discord.Embed(
        title="🌍 Dealer Updates",
        description=(
            "Where do you want to see dealer updates from?\n\n"
            "🇺🇸 **NA** — North American dealers only\n"
            "🇪🇺 **EU** — European dealers only\n"
            "🌍 **Both** — All dealers\n\n"
            "You can change this anytime by running `/start` again."
        ),
        color=discord.Color.dark_gold()
    )
    embed.set_footer(text="Adrian — Step 3 of 8")

    class DealerRegionView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)

        async def _save(self2, interaction2, region):
            await interaction2.response.defer(ephemeral=True)
            try:
                # Save region preference
                await db_set_user_region(str(interaction2.user.id), region)
                # Assign NA and/or EU roles
                config = await db_get_server_config(str(interaction2.guild.id))
                na_role_id = get_config_value(config, "na_role_id") if config else None
                eu_role_id = get_config_value(config, "eu_role_id") if config else None
                na_role = interaction2.guild.get_role(int(na_role_id)) if na_role_id else discord.utils.get(interaction2.guild.roles, name="NA")
                eu_role = interaction2.guild.get_role(int(eu_role_id)) if eu_role_id else discord.utils.get(interaction2.guild.roles, name="EU")
                member = interaction2.guild.get_member(interaction2.user.id)
                if member:
                    if na_role and region in ("NA", "both"):
                        if na_role not in member.roles:
                            await member.add_roles(na_role, reason="/start dealer region")
                    elif na_role and region == "EU":
                        if na_role in member.roles:
                            await member.remove_roles(na_role, reason="/start dealer region")
                    if eu_role and region in ("EU", "both"):
                        if eu_role not in member.roles:
                            await member.add_roles(eu_role, reason="/start dealer region")
                    elif eu_role and region == "NA":
                        if eu_role in member.roles:
                            await member.remove_roles(eu_role, reason="/start dealer region")
                logger.info(f"[Start] {interaction2.user} selected dealer region: {region}")
            except Exception as e:
                logger.error(f"[Start] Dealer region error: {e}")
            await start_step4_forums(interaction2)

        @discord.ui.button(emoji="🇺🇸", style=discord.ButtonStyle.secondary)
        async def na(self2, interaction2, button):
            await self2._save(interaction2, "NA")

        @discord.ui.button(emoji="🇪🇺", style=discord.ButtonStyle.secondary)
        async def eu(self2, interaction2, button):
            await self2._save(interaction2, "EU")

        @discord.ui.button(label="🌍 Both", style=discord.ButtonStyle.secondary)
        async def both(self2, interaction2, button):
            await self2._save(interaction2, "both")

    await interaction.edit_original_response(embed=embed, view=DealerRegionView())


async def start_step4_forums(interaction):
    """Step 4 — Forum selection."""
    embed = discord.Embed(
        title="🎖️ Forum Alerts",
        description=(
            "Which militaria forums would you like to follow?\n\n"
            "🟥 **WAF** — Wehrmacht Awards Forum\n"
            "🟩 **USMF** — US Militaria Forum\n"
            "✅ **Both** — WAF & USMF\n"
            "❌ **None** — Skip forum alerts\n\n"
            "You\'ll only see forum alerts for the forums you select."
        ),
        color=discord.Color.dark_gold()
    )
    embed.set_footer(text="Adrian — Step 4 of 8")

    class ForumSelectView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)

        async def _save(self2, interaction2, choice):
            await interaction2.response.defer(ephemeral=True)
            try:
                await db_set_user_forums(str(interaction2.user.id), choice)
                config = await db_get_server_config(str(interaction2.guild.id))
                waf_role_id = get_config_value(config, "waf_role_id") if config else None
                usmf_role_id = get_config_value(config, "usmf_role_id") if config else None
                waf_role = interaction2.guild.get_role(int(waf_role_id)) if waf_role_id else discord.utils.get(interaction2.guild.roles, name="WAF")
                usmf_role = interaction2.guild.get_role(int(usmf_role_id)) if usmf_role_id else discord.utils.get(interaction2.guild.roles, name="USMF")
                member = interaction2.guild.get_member(interaction2.user.id)
                if member:
                    if waf_role and choice in ("waf", "both"):
                        if waf_role not in member.roles:
                            await member.add_roles(waf_role, reason="/start forum selection")
                    elif waf_role and choice == "usmf":
                        if waf_role in member.roles:
                            await member.remove_roles(waf_role)
                    if usmf_role and choice in ("usmf", "both"):
                        if usmf_role not in member.roles:
                            await member.add_roles(usmf_role, reason="/start forum selection")
                    elif usmf_role and choice == "waf":
                        if usmf_role in member.roles:
                            await member.remove_roles(usmf_role)
                logger.info(f"[Start] {interaction2.user} selected forums: {choice}")
            except Exception as e:
                logger.error(f"[Start] Forum selection error: {e}")

            if choice == "waf":
                await start_step5_waf_categories(interaction2)
            elif choice == "usmf":
                await start_step6_usmf_categories(interaction2)
            elif choice == "both":
                await start_step5_waf_categories(interaction2, then_usmf=True)
            else:
                await start_step7_dealer_follows(interaction2)

        @discord.ui.button(emoji="🟥", style=discord.ButtonStyle.secondary)
        async def waf(self2, i, b): await self2._save(i, "waf")

        @discord.ui.button(emoji="🟩", style=discord.ButtonStyle.secondary)
        async def usmf(self2, i, b): await self2._save(i, "usmf")

        @discord.ui.button(emoji="✅", style=discord.ButtonStyle.secondary)
        async def both(self2, i, b): await self2._save(i, "both")

        @discord.ui.button(emoji="❌", style=discord.ButtonStyle.secondary)
        async def none(self2, i, b): await self2._save(i, "none")

    await interaction.edit_original_response(embed=embed, view=ForumSelectView())


async def start_step5_waf_categories(interaction, then_usmf=False):
    """Step 5 — WAF category selection."""
    options = [
        discord.SelectOption(label=cat["name"][:100], value=cat["name"], emoji=cat.get("emoji", "🎖️"))
        for cat in WAF_CATEGORIES if cat["name"] != "All WAF Updates"
    ]
    embed = discord.Embed(
        title="🎖️ WAF Categories",
        description=(
            "Which **Wehrmacht Awards Forum** categories do you want to follow?\n\n"
            "You\'ll get notified when new listings appear in your selected categories.\n"
            "Select as many as you like."
        ),
        color=discord.Color.dark_gold()
    )
    embed.set_footer(text="Adrian — Step 5 of 8")

    view = discord.ui.View(timeout=300)
    view._selected = []
    view._then_usmf = then_usmf

    select_menu = discord.ui.Select(
        placeholder="Select WAF categories...",
        options=options,
        min_values=1,
        max_values=len(options)
    )

    async def on_select(interaction2: discord.Interaction):
        view._selected = list(select_menu.values)
        await interaction2.response.defer(ephemeral=True)

    select_menu.callback = on_select
    view.add_item(select_menu)

    save_btn = discord.ui.Button(label="✅ Save", style=discord.ButtonStyle.success, row=1)
    async def on_save(interaction2: discord.Interaction):
        await interaction2.response.defer(ephemeral=True)
        # Read values directly from select at save time as fallback
        selected = view._selected or list(select_menu.values) if select_menu.values else view._selected
        if not selected:
            await interaction2.followup.send("Please select at least one category first.", ephemeral=True)
            return
        await db_save_user_waf_categories(str(interaction2.user.id), selected)
        logger.info(f"[Start] {interaction2.user} subscribed to {len(selected)} WAF categories")
        if view._then_usmf:
            await start_step6_usmf_categories(interaction2)
        else:
            await start_step7_dealer_follows(interaction2)
    save_btn.callback = on_save
    view.add_item(save_btn)

    all_btn = discord.ui.Button(label="⏭️ All Categories", style=discord.ButtonStyle.secondary, row=1)
    async def on_all(interaction2: discord.Interaction):
        await interaction2.response.defer(ephemeral=True)
        all_names = [cat["name"] for cat in WAF_CATEGORIES if cat["name"] != "All WAF Updates"]
        await db_save_user_waf_categories(str(interaction2.user.id), all_names)
        logger.info(f"[Start] {interaction2.user} subscribed to ALL WAF categories")
        if view._then_usmf:
            await start_step6_usmf_categories(interaction2)
        else:
            await start_step7_dealer_follows(interaction2)
    all_btn.callback = on_all
    view.add_item(all_btn)

    skip_btn = discord.ui.Button(label="⏭️ Skip", style=discord.ButtonStyle.secondary, row=1)
    async def on_skip(interaction2: discord.Interaction):
        await interaction2.response.defer(ephemeral=True)
        logger.info(f"[Start] {interaction2.user} skipped WAF categories")
        if view._then_usmf:
            await start_step6_usmf_categories(interaction2)
        else:
            await start_step7_dealer_follows(interaction2)
    skip_btn.callback = on_skip
    view.add_item(skip_btn)

    await interaction.edit_original_response(embed=embed, view=view)


async def start_step6_usmf_categories(interaction):
    """Step 6 — USMF category selection."""
    options = [
        discord.SelectOption(label=cat["name"][:100], value=cat["name"], emoji=cat.get("emoji", "📦"))
        for cat in USMF_CATEGORIES
    ]
    embed = discord.Embed(
        title="🦅 USMF Categories",
        description=(
            "Which **US Militaria Forum** categories do you want to follow?\n\n"
            "Select as many as you like."
        ),
        color=discord.Color.dark_gold()
    )
    embed.set_footer(text="Adrian — Step 6 of 8")

    view = discord.ui.View(timeout=300)
    view._selected = []

    select_menu = discord.ui.Select(
        placeholder="Select USMF categories...",
        options=options,
        min_values=1,
        max_values=len(options)
    )

    async def on_select(interaction2: discord.Interaction):
        view._selected = list(select_menu.values)
        await interaction2.response.defer(ephemeral=True)

    select_menu.callback = on_select
    view.add_item(select_menu)

    save_btn = discord.ui.Button(label="✅ Save", style=discord.ButtonStyle.success, row=1)
    async def on_save(interaction2: discord.Interaction):
        await interaction2.response.defer(ephemeral=True)
        if not view._selected:
            await interaction2.followup.send("Please select at least one category first.", ephemeral=True)
            return
        await db_save_user_usmf_categories(str(interaction2.user.id), view._selected)
        logger.info(f"[Start] {interaction2.user} subscribed to {len(view._selected)} USMF categories")
        await start_step7_dealer_follows(interaction2)
    save_btn.callback = on_save
    view.add_item(save_btn)

    all_btn = discord.ui.Button(label="⏭️ All Categories", style=discord.ButtonStyle.secondary, row=1)
    async def on_all(interaction2: discord.Interaction):
        await interaction2.response.defer(ephemeral=True)
        all_names = [cat["name"] for cat in USMF_CATEGORIES]
        await db_save_user_usmf_categories(str(interaction2.user.id), all_names)
        logger.info(f"[Start] {interaction2.user} subscribed to ALL USMF categories")
        await start_step7_dealer_follows(interaction2)
    all_btn.callback = on_all
    view.add_item(all_btn)

    skip_btn = discord.ui.Button(label="⏭️ Skip", style=discord.ButtonStyle.secondary, row=1)
    async def on_skip(interaction2: discord.Interaction):
        await interaction2.response.defer(ephemeral=True)
        logger.info(f"[Start] {interaction2.user} skipped USMF categories")
        await start_step7_dealer_follows(interaction2)
    skip_btn.callback = on_skip
    view.add_item(skip_btn)

    await interaction.edit_original_response(embed=embed, view=view)


async def start_step7_dealer_follows(interaction):
    """Step 7 — Explain dealer follow system."""
    embed = discord.Embed(
        title="🔔 Dealer Alerts",
        description=(
            "Here\'s how dealer alerts work:\n\n"
            "📬 **#dealer-updates** shows all new listings from dealers — no pings, just a clean feed\n\n"
            "🔔 **Follow dealers you love** — click the 🔔 button on any dealer alert to follow them\n\n"
            "📩 **Get a DM** every time a dealer you follow posts something new\n\n"
            "🔕 **Unfollow anytime** — click the 🔕 button to stop getting DMs from that dealer\n\n"
            f"✅ **Free members** can follow up to **{FREE_DEALER_FOLLOW_LIMIT} dealers**\n"
            "❤️ **Premium members** get **unlimited** dealer follows"
        ),
        color=discord.Color.dark_gold()
    )
    embed.set_footer(text="Adrian — Step 7 of 8")

    class DealerFollowView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)

        @discord.ui.button(label="Got it! →", style=discord.ButtonStyle.success)
        async def next(self2, interaction2, button):
            await interaction2.response.defer(ephemeral=True)
            await start_step8_premium(interaction2)

    await interaction.edit_original_response(embed=embed, view=DealerFollowView())


async def start_step8_premium(interaction):
    """Step 8 — Offer Adrian Premium."""
    embed = discord.Embed(
        title="❤️ Adrian Premium",
        description=(
            "Upgrade to **Adrian Premium** and unlock the full experience:\n\n"
            "🔔 **Unlimited dealer follows** — free members get 20\n"
            "📩 **Keyword alerts** — get a DM when any WAF/USMF post contains your keywords\n"
            "🏪 **Estand Premium** — listing boost, analytics, unlimited photos, price drop alerts and more\n\n"
            "Premium is coming soon. We\'ll let you know when it\'s available!"
        ),
        color=discord.Color.gold()
    )
    embed.set_footer(text="Adrian — Step 8 of 8")

    class PremiumView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)

        @discord.ui.button(label="✅ Finish Setup", style=discord.ButtonStyle.success)
        async def finish(self2, interaction2, button):
            await interaction2.response.defer(ephemeral=True)
            await start_final_screen(interaction2)

        @discord.ui.button(label="Buy Premium", emoji="❤️", style=discord.ButtonStyle.danger)
        async def buy_premium(self2, interaction2, button):
            await interaction2.response.send_message(
                "❤️ Adrian Premium is coming soon! We\'ll announce it in the server when it\'s available.",
                ephemeral=True
            )

        @discord.ui.button(label="Beta Tester", emoji="🤖", style=discord.ButtonStyle.primary)
        async def beta_tester(self2, interaction2: discord.Interaction, button):
            await interaction2.response.defer(ephemeral=True)
            if interaction2.user.id != BOT_OWNER_ID:
                await interaction2.followup.send("⚠️ This button is for authorized beta testers only.", ephemeral=True)
                return
            try:
                premium_role = discord.utils.get(interaction2.guild.roles, name="Adrian Premium")
                if not premium_role:
                    config = await db_get_server_config(str(interaction2.guild.id))
                    premium_role_id = get_config_value(config, "premium_role_id") if config else None
                    if premium_role_id:
                        premium_role = interaction2.guild.get_role(int(premium_role_id))
                if premium_role:
                    member = interaction2.guild.get_member(interaction2.user.id)
                    if member:
                        if premium_role not in member.roles:
                            await member.add_roles(premium_role, reason="Beta tester — assigned via /start")
                            await interaction2.followup.send("🤖 Beta tester status granted! You now have Adrian Premium.", ephemeral=True)
                            logger.info(f"[Start] Beta tester premium assigned to {interaction2.user} in {interaction2.guild.name}")
                        else:
                            await interaction2.followup.send("🤖 You already have the Premium role!", ephemeral=True)
                    else:
                        await interaction2.followup.send("⚠️ Could not find your membership in this server.", ephemeral=True)
                else:
                    await interaction2.followup.send("⚠️ Could not find the Adrian Premium role. Make sure `/setup` has been run on this server.", ephemeral=True)
            except Exception as e:
                logger.error(f"[Start] Beta tester error: {e}\n{traceback.format_exc()}")
                await interaction2.followup.send(f"⚠️ Something went wrong: {e}", ephemeral=True)

    await interaction.edit_original_response(embed=embed, view=PremiumView())


async def start_final_screen(interaction):
    """Final screen — welcome to Adrian."""
    embed = discord.Embed(
        title="🎖️ You\'re All Set!",
        description=(
            f"Welcome to Adrian, **{interaction.user.display_name}**!\n\n"
            "Here\'s a quick summary of what\'s available to you:\n\n"
            "📬 Check **#dealer-updates** for the latest listings\n"
            "🎖️ Check **#waf-updates** and **#usmf-updates** for forum alerts\n"
            "🏪 Visit **#estand** to buy and sell with trusted collectors\n"
            "🔔 Click 🔔 on any dealer alert to follow that dealer\n\n"
            "Run `/start` anytime to update your preferences."
        ),
        color=discord.Color.green()
    )
    embed.set_footer(text="Adrian — Discord's #1 Militaria Bot")

    # Send profile notification to owner channel
    try:
        notif_channel = client.get_channel(NEW_PROFILE_CHANNEL_ID)
        if notif_channel:
            points = await db_get_user_points(str(interaction.user.id))
            notif_embed = discord.Embed(
                title="👤 New Profile Created",
                description=f"**{interaction.user.display_name}** just completed `/start` in **{interaction.guild.name}**",
                color=discord.Color.dark_gold(),
                timestamp=datetime.now(timezone.utc)
            )
            notif_embed.set_thumbnail(url=interaction.user.display_avatar.url if interaction.user.display_avatar else None)
            notif_embed.add_field(name="User ID", value=str(interaction.user.id), inline=True)
            notif_embed.add_field(name="Points", value=str(points), inline=True)
            await notif_channel.send(embed=notif_embed)
            logger.info(f"[Profile] New profile notification sent for {interaction.user} in {interaction.guild.name}")
    except Exception as e:
        logger.debug(f"[Profile] Could not send profile notification: {e}")

    await interaction.edit_original_response(embed=embed, view=None)


async def _show_start_onboarding(interaction):
    """Entry point for /start — checks if already verified and goes to right step."""
    logger.debug(f"[Start] Showing onboarding to {interaction.user} ({interaction.user.id})")
    # Check if already agreed to bot rules (has Adrian Verified role)
    member = interaction.guild.get_member(interaction.user.id)
    config = await db_get_server_config(str(interaction.guild.id))
    role_id = get_config_value(config, "verified_role_id") if config else None
    verified_role = interaction.guild.get_role(int(role_id)) if role_id else discord.utils.get(interaction.guild.roles, name="Adrian Verified")
    already_verified = verified_role and member and verified_role in member.roles

    if already_verified:
        # Already agreed to bot rules — go straight to step 2
        await start_step2_estand_rules(interaction)
    else:
        await start_step1_bot_rules(interaction)



@client.tree.command(name="setup", description="Set up Adrian on your server — creates all channels, roles and permissions")
async def setup_cmd(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("🚫 Only server administrators can run `/setup`.", ephemeral=True)
        return
    await interaction.response.send_message("👋 Loading...", ephemeral=True)
    logger.info(f"[Setup] /setup started by {interaction.user} in {interaction.guild.name}")
    await db_save_server_config(str(interaction.guild_id), guild_name=interaction.guild.name, owner_id=str(interaction.guild.owner_id))
    await _show_setup_rules(interaction)


async def _show_setup_rules(interaction):
    embed = discord.Embed(
        title="📋 Server Owner Agreement",
        description=(
            "Before setting up Adrian, please read and agree to the following:\n\n"
            "**1.** Moderate your server — remove fraudulent or rule-breaking listings promptly\n"
            "**2.** No prohibited items — illegal items or items prohibited by Discord's ToS\n"
            "**3.** Protect your members — act on reports of scammers or bad actors\n"
            "**4.** Do not manipulate ratings or reviews\n"
            "**5.** Do not restrict the bot's permissions in ways that break its features\n\n"
            "By clicking **I Agree** you confirm you have read and will abide by these rules."
        ),
        color=discord.Color.dark_gold()
    )
    embed.set_footer(text="Adrian — Server Setup")

    class SetupRulesView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)

        @discord.ui.button(label="✅ I Agree", style=discord.ButtonStyle.success)
        async def agree(self2, interaction2: discord.Interaction, button: discord.ui.Button):
            await interaction2.response.defer(ephemeral=True)
            await _run_auto_setup(interaction2)

        @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.danger)
        async def cancel(self2, interaction2: discord.Interaction, button: discord.ui.Button):
            await interaction2.response.edit_message(
                embed=discord.Embed(title="Setup Cancelled", description="Run `/setup` again whenever you're ready.", color=discord.Color.red()),
                view=None
            )

    await interaction.edit_original_response(embed=embed, view=SetupRulesView())


async def _run_auto_setup(interaction):
    guild = interaction.guild
    results = []

    await interaction.edit_original_response(
        embed=discord.Embed(title="⚙️ Setting up Adrian...", description="Creating channels, roles and permissions. This will take a few seconds.", color=discord.Color.dark_gold()),
        view=None
    )

    try:
        # ── ROLES ──────────────────────────────────────────────
        async def get_or_create_role(name, color, save_key=None):
            role = discord.utils.get(guild.roles, name=name)
            if not role:
                role = await guild.create_role(name=name, color=color, reason="Adrian setup")
                results.append(f"✅ Created **@{name}** role")
            else:
                results.append(f"✅ Found **@{name}** role")
            if save_key and role:
                await db_save_server_config(str(guild.id), **{save_key: str(role.id)})
            return role

        verified_role  = await get_or_create_role("Adrian Verified", discord.Color.blue(),   "verified_role_id")
        estand_role    = await get_or_create_role("Estand Verified",  discord.Color.green(),  "estand_verified_role_id")
        na_role        = await get_or_create_role("NA",               discord.Color.from_rgb(0, 120, 215), "na_role_id")
        eu_role        = await get_or_create_role("EU",               discord.Color.from_rgb(0, 70, 160),  "eu_role_id")
        waf_role       = await get_or_create_role("WAF",              discord.Color.from_rgb(180, 0, 0),   "waf_role_id")
        usmf_role      = await get_or_create_role("USMF",             discord.Color.from_rgb(0, 100, 0),   "usmf_role_id")
        premium_role   = await get_or_create_role("Adrian Premium",   discord.Color.gold(),   "premium_role_id")

        # ── FIX ROLE HIERARCHY ─────────────────────────────────
        try:
            bot_role = guild.me.top_role
            # Find the highest role the bot can move to
            # Bot cannot move roles above its current position, so we find the
            # highest non-managed role below @everyone that isn't the bot's own role
            # In practice: move to just below the server owner / highest admin role
            all_roles = sorted(guild.roles, key=lambda r: r.position, reverse=True)
            target_position = None
            for role in all_roles:
                # Skip @everyone, managed roles (other bots), and roles above or equal to bot's current position
                if role.is_default():
                    continue
                if role.managed and role.id != bot_role.id:
                    continue
                if role.id == bot_role.id:
                    continue
                if role.position >= bot_role.position:
                    # This is a role we can't go above — set target just below it
                    target_position = role.position
                    break
            
            if target_position and bot_role.position < target_position - 1:
                await bot_role.edit(position=target_position - 1, reason="Adrian setup — maximizing role position")
                results.append(f"✅ Bot role moved to highest possible position")
                logger.info(f"[Setup] Bot role moved to position {target_position - 1} in {guild.name}")
            else:
                results.append("✅ Bot role already at optimal position")
        except Exception as e:
            results.append(f"⚠️ Could not auto-fix role hierarchy: {e}")
            logger.warning(f"[Setup] Role hierarchy fix failed: {e}")

        # ── CHANNELS ───────────────────────────────────────────
        everyone   = guild.default_role
        bot_member = guild.me

        # Create Adrian category
        category = discord.utils.get(guild.categories, name="Adrian")
        if not category:
            category = await guild.create_category(
                name="Adrian",
                overwrites={everyone: discord.PermissionOverwrite(view_channel=False), bot_member: discord.PermissionOverwrite(view_channel=True)},
                reason="Adrian setup"
            )
            results.append("✅ Created **Adrian** category")
        else:
            results.append("✅ Found **Adrian** category")

        async def get_or_create_channel(name, topic, overwrites, save_key=None):
            channel = discord.utils.get(guild.text_channels, name=name)
            if not channel:
                channel = await guild.create_text_channel(name=name, topic=topic, category=category, overwrites=overwrites, reason="Adrian setup")
                results.append(f"✅ Created **#{name}**")
            else:
                if channel.category != category:
                    await channel.edit(category=category)
                for target, perms in overwrites.items():
                    await channel.set_permissions(target, overwrite=perms)
                results.append(f"✅ Found **#{name}**")
            if save_key and channel:
                await db_save_server_config(str(guild.id), **{save_key: str(channel.id)})
            return channel

        adrian_ch  = await get_or_create_channel("adrian",           "Welcome to Adrian! Type /start to set up your profile.",
            {everyone: discord.PermissionOverwrite(view_channel=True, send_messages=False), bot_member: discord.PermissionOverwrite(view_channel=True, send_messages=True), guild.owner: discord.PermissionOverwrite(view_channel=True, send_messages=True)}, "channel_id")
        dealer_ch  = await get_or_create_channel("dealer-updates",   "New item alerts from militaria dealers.",
            {everyone: discord.PermissionOverwrite(view_channel=False), verified_role: discord.PermissionOverwrite(view_channel=True, send_messages=False), bot_member: discord.PermissionOverwrite(view_channel=True, send_messages=True)}, "updates_channel_id")
        na_ch      = await get_or_create_channel("na-dealer-updates","New item alerts from North American dealers.",
            {everyone: discord.PermissionOverwrite(view_channel=False), na_role: discord.PermissionOverwrite(view_channel=True, send_messages=False), bot_member: discord.PermissionOverwrite(view_channel=True, send_messages=True)}, "na_updates_channel_id")
        eu_ch      = await get_or_create_channel("eu-dealer-updates","New item alerts from European dealers.",
            {everyone: discord.PermissionOverwrite(view_channel=False), eu_role: discord.PermissionOverwrite(view_channel=True, send_messages=False), bot_member: discord.PermissionOverwrite(view_channel=True, send_messages=True)}, "eu_updates_channel_id")
        waf_ch     = await get_or_create_channel("waf-updates",      "Wehrmacht Awards Forum new listing alerts.",
            {everyone: discord.PermissionOverwrite(view_channel=False), waf_role: discord.PermissionOverwrite(view_channel=True, send_messages=False), bot_member: discord.PermissionOverwrite(view_channel=True, send_messages=True)}, "waf_channel_id")
        usmf_ch    = await get_or_create_channel("usmf-updates",     "US Militaria Forum new listing alerts.",
            {everyone: discord.PermissionOverwrite(view_channel=False), usmf_role: discord.PermissionOverwrite(view_channel=True, send_messages=False), bot_member: discord.PermissionOverwrite(view_channel=True, send_messages=True)}, "usmf_channel_id")

        # Estand forum channel
        estand_ch = discord.utils.get(guild.forums, name="estand") or discord.utils.get(guild.text_channels, name="estand")
        if not estand_ch:
            try:
                estand_ch = await guild.create_forum(
                    name="estand", topic="Buy and sell militaria with trusted collectors.", category=category,
                    overwrites={everyone: discord.PermissionOverwrite(view_channel=False), estand_role: discord.PermissionOverwrite(view_channel=True, send_messages=True), bot_member: discord.PermissionOverwrite(view_channel=True, send_messages=True)},
                    reason="Adrian setup"
                )
                results.append("✅ Created **#estand** forum")
            except Exception as e:
                results.append(f"⚠️ Could not create Estand forum: {e}")
        else:
            results.append("✅ Found **#estand** forum")
        if estand_ch:
            await db_save_server_config(str(guild.id), estand_channel_id=str(estand_ch.id))

        await db_save_server_config(str(guild.id), setup_complete="1")
        logger.info(f"[Setup] Setup complete for {guild.name}")

        # Post welcome message
        try:
            welcome_file = os.path.join(SCRIPT_DIR, "logos", "adrian", "Adrian_welcome.png")
            if os.path.exists(welcome_file):
                welcome_msg = await adrian_ch.send(file=discord.File(welcome_file, filename="Adrian_welcome.png"), view=WelcomeView())
                await db_save_server_config(str(guild.id), welcome_message_id=str(welcome_msg.id))
        except Exception as e:
            logger.error(f"[Setup] Could not post welcome: {e}")

        results_text = "\n".join(results)
        embed = discord.Embed(
            title="🎖️ Adrian is Ready!",
            description=f"Setup complete for **{guild.name}**!\n\n{results_text}\n\n**Members can now type `/start` in {adrian_ch.mention} to get started!**",
            color=discord.Color.green()
        )
        embed.set_footer(text="Adrian — Discord's #1 Militaria Bot")
        await interaction.edit_original_response(embed=embed, view=None)

    except discord.Forbidden:
        await interaction.edit_original_response(
            embed=discord.Embed(title="⚠️ Missing Permissions", description="I need **Administrator** permissions to complete setup. Please grant this and run `/setup` again.", color=discord.Color.red()),
            view=None
        )
    except Exception as e:
        logger.error(f"[Setup] Error: {e}\n{traceback.format_exc()}")
        await interaction.edit_original_response(
            embed=discord.Embed(title="⚠️ Setup Error", description=f"Something went wrong. Please try again.\n\n`{e}`", color=discord.Color.red()),
            view=None
        )


@client.tree.command(name="start", description="Set up your Adrian profile and preferences")
async def start_cmd(interaction: discord.Interaction):
    on_cd, remaining = check_cooldown(str(interaction.user.id), "start")
    if on_cd:
        await interaction.response.send_message(f"⏳ Please wait {remaining}s before trying again.", ephemeral=True)
        return
    await interaction.response.send_message("👋 Loading...", ephemeral=True)
    await _show_start_onboarding(interaction)


@client.tree.command(name="settings", description="Update your notification preferences")
async def settings_cmd(interaction: discord.Interaction):
    existing = await db_get_user_region(str(interaction.user.id))
    region_str = {"NA": "🇺🇸 North America Only", "EU": "🇪🇺 Europe Only", "both": "🌍 All Dealers"}.get(existing, "Not set yet")

    embeds = []
    if bot_state.get("question1_img_url"):
        img_embed = discord.Embed(color=discord.Color.dark_gold())
        img_embed.set_image(url=bot_state["question1_img_url"])
        embeds.append(img_embed)
    text_embed = discord.Embed(
        description=f"🇺🇸 North America Only\n🇪🇺 Europe Only\n🌍 All Dealers\n\n**Current Setting:** {region_str}",
        color=discord.Color.dark_gold()
    )
    text_embed.set_footer(text="Adrian — Discord's #1 Militaria Bot")
    embeds.append(text_embed)
    await interaction.response.send_message("Use `/start` to update your preferences.", ephemeral=True)

@client.tree.command(name="help", description="Shows all available bot commands")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="🎖️ Adrian — Commands", color=discord.Color.dark_gold())
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

@client.tree.command(name="dealerprofile", description="View a dealer's full profile including ratings and reviews")
@app_commands.describe(dealer_name="Name of the dealer")
@app_commands.autocomplete(dealer_name=dealer_autocomplete)
async def dealerprofile_cmd(interaction: discord.Interaction, dealer_name: str):
    dealer = find_dealer(dealer_name)
    if not dealer:
        await interaction.response.send_message(f"⚠️ Dealer '{dealer_name}' not found.", ephemeral=True)
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

    embed.set_footer(text="Adrian — Dealer Update")

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
        await interaction.followup.send("🚫 You have been restricted from leaving reviews. If you believe this is an error please contact a moderator.", ephemeral=True)
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

    embed = discord.Embed(title="🏆 Adrian — Leaderboard", color=discord.Color.gold(), timestamp=datetime.now(timezone.utc))

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

    embed.set_footer(text="Adrian — Dealer Update")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ==================== MOD COMMANDS ====================

@client.tree.command(name="testalert", description="🔒 Test the alert ping and /alerts system for yourself")
async def testalert_cmd(interaction: discord.Interaction):
    if not is_mod(interaction.user):
        await interaction.response.send_message("🚫 You need Moderator permissions.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    channel = client.get_channel(CHANNEL_ID)
    user_id = str(interaction.user.id)

    # Save a test alert to pending
    await db_add_pending_alert(user_id, "TEST — Weitze Militaria", "https://www.weitze.com/neuheiten.html", "🇩🇪")

    # Ping in #adrian-updates
    updates_channel = channel
    if updates_channel:
        member = updates_channel.guild.get_member(interaction.user.id)
        if member:
            await updates_channel.send(
                content=f"{member.mention} 🆕 **TEST** — Weitze Militaria has new items! Type `/alerts` to see your updates.",
                delete_after=3
            )
    await interaction.followup.send("✅ Test alert sent! Check #Adrian for the ping, then type `/alerts` to verify.", ephemeral=True)

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
        await send_alert(dealer["name"], dealer["url"], logo_file, test=True)
        await asyncio.sleep(1)
    await interaction.followup.send("✅ Test complete!", ephemeral=True)

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
    embed.set_footer(text="Adrian — Dealer Update")
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
    embed.set_footer(text="Adrian — Dealer Update")
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
    embed.set_footer(text="Watchlist entries expire after 90 days — Adrian")
    await interaction.followup.send(embed=embed, ephemeral=True)

@client.tree.command(name="scamflag", description="Flag a user as a suspected scammer")
@app_commands.describe(
    user="The user to flag",
    reason="Why you believe this user is a scammer"
)
async def scamflag_cmd(interaction: discord.Interaction, user: discord.Member, reason: str):
    # Must be mod or server owner
    config = await db_get_server_config(str(interaction.guild_id))
    mod_role_id = get_config_value(config, "mod_role_id") if config else None
    is_mod = (
        interaction.user.guild_permissions.manage_messages or
        interaction.user.id == interaction.guild.owner_id or
        is_bot_owner(interaction.user) or
        (mod_role_id and any(r.id == int(mod_role_id) for r in interaction.user.roles))
    )
    if not is_mod:
        await interaction.response.send_message("⚠️ You don't have permission to flag users.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    if user.id == interaction.user.id:
        await interaction.followup.send("⚠️ You can't flag yourself.", ephemeral=True)
        return
    if user.id == client.user.id:
        await interaction.followup.send("⚠️ You can't flag the bot.", ephemeral=True)
        return

    total_flags, newly_added = await db_add_scam_flag(
        str(user.id), str(interaction.user.id),
        str(interaction.guild_id), reason
    )

    if not newly_added:
        await interaction.followup.send(
            f"⚠️ You have already flagged **{user.display_name}**. Another mod needs to confirm.",
            ephemeral=True
        )
        return

    logger.info(f"[ScamFlag] {interaction.user} flagged {user} ({user.id}) — total flags: {total_flags}")

    # Log to mod channel
    try:
        mod_log_id = get_config_value(config, "mod_log_channel_id") if config else None
        if mod_log_id:
            mod_channel = interaction.guild.get_channel(int(mod_log_id))
            if mod_channel:
                log_embed = discord.Embed(
                    title="🚨 Scam Flag Added",
                    color=discord.Color.red(),
                    timestamp=datetime.now(timezone.utc)
                )
                log_embed.add_field(name="Flagged User", value=f"{user.mention} ({user.display_name})", inline=True)
                log_embed.add_field(name="Flagged By", value=f"{interaction.user.mention}", inline=True)
                log_embed.add_field(name="Total Flags", value=f"{total_flags} / {SCAM_FLAG_THRESHOLD}", inline=True)
                log_embed.add_field(name="Reason", value=reason, inline=False)
                log_embed.set_footer(text="Adrian — Scam Protection")
                await mod_channel.send(embed=log_embed)
    except Exception as e:
        logger.debug(f"[ScamFlag] Could not log: {e}")

    # Check if threshold reached
    if total_flags >= SCAM_FLAG_THRESHOLD:
        # Add global scammer warning
        await db_add_user_warning(
            str(user.id),
            f"Flagged as scammer by {total_flags} mods across the Adrian network. Reason: {reason}",
            warning_type="scammer",
            issued_by="system",
            guild_id=str(interaction.guild_id)
        )

        # Notify bot owner channel
        try:
            owner_channel = client.get_channel(1513670729194016778)
            if owner_channel:
                alert_embed = discord.Embed(
                    title="🚨 Global Scammer Flag Triggered!",
                    description=f"**{user.display_name}** (`{user.id}`) has been flagged by **{total_flags} mods** and is now globally marked as a scammer.",
                    color=discord.Color.red(),
                    timestamp=datetime.now(timezone.utc)
                )
                alert_embed.add_field(name="Last Reason", value=reason, inline=False)
                alert_embed.add_field(name="Server", value=interaction.guild.name, inline=True)
                alert_embed.set_footer(text="Adrian — Scam Protection System")
                await owner_channel.send(embed=alert_embed)
        except Exception as e:
            logger.debug(f"[ScamFlag] Could not notify owner channel: {e}")

        # Try to DM the flagged user
        try:
            dm_embed = discord.Embed(
                title="🚨 Your account has been flagged",
                description=(
                    "Your account has been flagged as a suspected scammer by multiple moderators "
                    "across the Adrian network.\n\n"
                    "Your access to the Estand Marketplace has been restricted pending review.\n\n"
                    "If you believe this is an error, please contact a server administrator."
                ),
                color=discord.Color.red()
            )
            dm_embed.set_footer(text="Adrian — Scam Protection")
            await user.send(embed=dm_embed)
        except discord.Forbidden:
            pass

        await interaction.followup.send(
            embed=discord.Embed(
                title="🚨 Global Scammer Flag Triggered",
                description=(
                    f"**{user.display_name}** has been flagged by **{total_flags} mods** "
                    f"and is now **globally marked as a scammer** across all Adrian servers.\n\n"
                    f"Their Estand access has been restricted and the bot owner has been notified."
                ),
                color=discord.Color.red()
            ),
            ephemeral=True
        )
    else:
        remaining = SCAM_FLAG_THRESHOLD - total_flags
        await interaction.followup.send(
            embed=discord.Embed(
                title="🚩 Scam Flag Added",
                description=(
                    f"**{user.display_name}** has been flagged.\n\n"
                    f"**Total flags:** {total_flags} / {SCAM_FLAG_THRESHOLD}\n"
                    f"**{remaining} more mod flag(s) needed** from different servers to trigger global action."
                ),
                color=discord.Color.orange()
            ),
            ephemeral=True
        )


@client.tree.command(name="clearscamflag", description="[Owner] Clear all scam flags for a user")
@app_commands.describe(user="The user to clear flags for")
async def clearscamflag_cmd(interaction: discord.Interaction, user: discord.Member):
    if not is_bot_owner(interaction.user):
        await interaction.response.send_message("❓ Unknown command.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    await db_remove_scam_flag(str(user.id))
    await interaction.followup.send(
        embed=discord.Embed(
            title="✅ Scam Flags Cleared",
            description=f"All scam flags and scammer warnings have been cleared for **{user.display_name}**.",
            color=discord.Color.green()
        ),
        ephemeral=True
    )
    logger.info(f"[ScamFlag] Flags cleared for {user} ({user.id}) by {interaction.user}")


@client.tree.command(name="warn", description="Issue a warning to a user")
@app_commands.describe(
    user="The user to warn",
    reason="Reason for the warning"
)
async def warn_cmd(interaction: discord.Interaction, user: discord.Member, reason: str):
    # Must be server owner or have mod role
    config = await db_get_server_config(str(interaction.guild_id))
    mod_role_id = get_config_value(config, "mod_role_id") if config else None
    is_mod = (
        interaction.user.guild_permissions.manage_messages or
        interaction.user.id == interaction.guild.owner_id or
        is_bot_owner(interaction.user) or
        (mod_role_id and any(r.id == int(mod_role_id) for r in interaction.user.roles))
    )
    if not is_mod:
        await interaction.response.send_message("⚠️ You don't have permission to warn users.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    # Can't warn yourself or the bot
    if user.id == interaction.user.id:
        await interaction.followup.send("⚠️ You can't warn yourself.", ephemeral=True)
        return
    if user.id == client.user.id:
        await interaction.followup.send("⚠️ You can't warn the bot.", ephemeral=True)
        return

    # Add warning to DB
    await db_add_user_warning(
        str(user.id),
        reason,
        warning_type="warning",
        issued_by=str(interaction.user.id),
        guild_id=str(interaction.guild_id)
    )

    warning_count = await db_get_user_warnings(str(user.id))

    # DM the warned user
    try:
        warn_embed = discord.Embed(
            title="⚠️ You have received a warning",
            description=(
                f"You have been warned in **{interaction.guild.name}**\n\n"
                f"**Reason:** {reason}\n\n"
                f"**Total warnings:** {warning_count}\n\n"
                f"Please review the server rules to avoid further action."
            ),
            color=discord.Color.orange(),
            timestamp=datetime.now(timezone.utc)
        )
        warn_embed.set_footer(text="Adrian — Estand Marketplace")
        await user.send(embed=warn_embed)
        dm_status = "✅ User was notified via DM"
    except discord.Forbidden:
        dm_status = "⚠️ Could not DM user — they may have DMs disabled"

    # Log to mod log channel
    try:
        mod_log_id = get_config_value(config, "mod_log_channel_id") if config else None
        if mod_log_id:
            mod_channel = interaction.guild.get_channel(int(mod_log_id))
            if mod_channel:
                log_embed = discord.Embed(
                    title="⚠️ User Warning Issued",
                    color=discord.Color.orange(),
                    timestamp=datetime.now(timezone.utc)
                )
                log_embed.add_field(name="User", value=f"{user.mention} ({user.display_name})", inline=True)
                log_embed.add_field(name="Warned by", value=f"{interaction.user.mention}", inline=True)
                log_embed.add_field(name="Reason", value=reason, inline=False)
                log_embed.add_field(name="Total Warnings", value=str(warning_count), inline=True)
                log_embed.set_footer(text="Adrian — Mod Log")
                await mod_channel.send(embed=log_embed)
    except Exception as e:
        logger.debug(f"[Warn] Could not log to mod channel: {e}")

    await interaction.followup.send(
        embed=discord.Embed(
            title="⚠️ Warning Issued",
            description=(
                f"**{user.display_name}** has been warned.\n\n"
                f"**Reason:** {reason}\n"
                f"**Total warnings:** {warning_count}\n"
                f"{dm_status}"
            ),
            color=discord.Color.orange()
        ),
        ephemeral=True
    )
    logger.info(f"[Warn] {interaction.user} warned {user} ({user.id}) in {interaction.guild.name}: {reason}")


@client.tree.command(name="watchlist", description="Manage your keyword watchlist for forum alerts")
async def watchlist_cmd(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    uid = str(interaction.user.id)
    is_premium = await db_is_premium(uid)
    keywords = await db_get_user_keywords(uid)
    limit = "Unlimited" if is_premium else f"{FREE_KEYWORD_LIMIT}"

    embed = discord.Embed(
        title="🔔 Your Keyword Watchlist",
        description=(
            f"Get a DM when any forum alert (WAF/USMF) contains your keywords.\n"
            f"**Keywords used:** {len(keywords)} / {limit}\n\n"
        ) + (
            "\n".join([f"• `{k['keyword']}`" for k in keywords]) if keywords else "*No keywords saved yet.*"
        ),
        color=discord.Color.dark_gold()
    )
    embed.set_footer(text="Adrian — Keyword Watchlist")

    class WatchlistView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)

        @discord.ui.button(label="➕ Add Keyword", style=discord.ButtonStyle.success)
        async def add_keyword(self2, interaction2: discord.Interaction, button: discord.ui.Button):
            class AddKeywordModal(discord.ui.Modal, title="Add Keyword"):
                keyword = discord.ui.TextInput(
                    label="Keyword to watch",
                    placeholder="e.g. iron cross, M35 helmet, purple heart",
                    max_length=50
                )
                async def on_submit(self3, interaction3: discord.Interaction):
                    is_prem = await db_is_premium(str(interaction3.user.id))
                    success, msg = await db_add_keyword(str(interaction3.user.id), self3.keyword.value, is_prem)
                    color = discord.Color.green() if success else discord.Color.orange()
                    await interaction3.response.send_message(
                        embed=discord.Embed(description=msg, color=color),
                        ephemeral=True
                    )
                    logger.info(f"[Watchlist] {interaction3.user} added keyword: {self3.keyword.value} success={success}")
            await interaction2.response.send_modal(AddKeywordModal())

        @discord.ui.button(label="➖ Remove Keyword", style=discord.ButtonStyle.danger)
        async def remove_keyword(self2, interaction2: discord.Interaction, button: discord.ui.Button):
            if not keywords:
                await interaction2.response.send_message("You have no keywords to remove.", ephemeral=True)
                return
            options = [
                discord.SelectOption(label=k["keyword"], value=k["keyword"])
                for k in keywords
            ][:25]

            class RemoveSelect(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=120)

                @discord.ui.select(placeholder="Select keyword to remove...", options=options)
                async def select_keyword(self3, interaction3: discord.Interaction, select: discord.ui.Select):
                    removed = await db_remove_keyword(str(interaction3.user.id), select.values[0])
                    if removed:
                        await interaction3.response.send_message(
                            embed=discord.Embed(description=f"✅ Removed keyword **{select.values[0]}** from your watchlist.", color=discord.Color.green()),
                            ephemeral=True
                        )
                    else:
                        await interaction3.response.send_message("⚠️ Could not find that keyword.", ephemeral=True)

            await interaction2.response.send_message(
                "Select a keyword to remove:",
                view=RemoveSelect(),
                ephemeral=True
            )

    await interaction.followup.send(embed=embed, view=WatchlistView(), ephemeral=True)

@client.tree.command(name="profile", description="View your profile or another member's public profile")
@app_commands.describe(user="Leave blank for your own profile, or mention a member for their public profile")
async def profile_cmd(interaction: discord.Interaction, user: discord.Member = None):
    await interaction.response.defer(ephemeral=True)
    if user is None or user.id == interaction.user.id:
        await show_private_profile(interaction)
    else:
        await show_public_profile(interaction, user)


@client.tree.command(name="lookup", description="🔒 Admin — look up any Adrian profile by user ID or mention")
@app_commands.describe(user_id="Discord user ID or mention (@user)")
async def lookup_cmd(interaction: discord.Interaction, user_id: str):
    is_owner = interaction.user.id == BOT_OWNER_ID
    is_admin = interaction.user.guild_permissions.administrator if interaction.guild else False
    if not is_owner and not is_admin:
        await interaction.response.send_message("❓ Unknown command.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)

    # Clean up the user_id — strip mention formatting
    clean_id = user_id.strip().lstrip("<@!").rstrip(">")
    try:
        uid = int(clean_id)
    except ValueError:
        await interaction.followup.send("⚠️ Please provide a valid user ID or @mention.", ephemeral=True)
        return

    # Try to fetch the user
    try:
        user = await client.fetch_user(uid)
    except discord.NotFound:
        await interaction.followup.send(f"⚠️ Could not find Discord user with ID `{uid}`.", ephemeral=True)
        return
    except Exception as e:
        await interaction.followup.send(f"⚠️ Error fetching user: {e}", ephemeral=True)
        return

    # Check they have an Adrian profile
    async with client.db.acquire() as conn:
        row = await conn.fetchrow("SELECT user_id FROM user_preferences WHERE user_id=$1", str(uid))
    if not row:
        await interaction.followup.send(
            embed=discord.Embed(
                title="👤 No Profile Found",
                description=f"**{user.display_name}** (`{uid}`) has no Adrian profile in the database.",
                color=discord.Color.orange()
            ),
            ephemeral=True
        )
        return

    # Get member object if available (for role info)
    member = None
    for guild in client.guilds:
        member = guild.get_member(uid)
        if member:
            break

    await show_admin_profile(interaction, user, member)


async def show_public_profile(interaction, user: discord.Member):
    """Public profile — visible to anyone via /profile @user."""
    uid = str(user.id)

    async with client.db.acquire() as conn:
        row = await conn.fetchrow("SELECT user_id FROM user_preferences WHERE user_id=$1", uid)
    if not row:
        await interaction.followup.send(
            embed=discord.Embed(
                title="👤 Profile Not Found",
                description=f"**{user.display_name}** hasn\'t set up their Adrian profile yet.",
                color=discord.Color.orange()
            ),
            ephemeral=True
        )
        return

    seller_avg, seller_count = await db_get_seller_rating(uid)
    buyer_avg, buyer_count = await db_get_buyer_rating(uid)
    seller_sales, buyer_purchases = await db_get_completed_transactions(uid)
    points = await db_get_user_points(uid)
    warnings = await db_get_user_warnings(uid)

    # Check badges
    is_premium = await db_is_premium(uid)
    is_beta = await db_is_beta_tester(uid)

    # Member since
    member_since = f"<t:{int(user.created_at.timestamp())}:D>"

    # Build embed
    name_line = user.display_name
    badges = ""
    if user.id == BOT_OWNER_ID: badges += " 🛠️"
    if is_beta: badges += " 🤖"
    if is_premium: badges += " ❤️"

    embed = discord.Embed(
        title=f"👤 {name_line}{badges}",
        color=discord.Color.dark_gold(),
        timestamp=datetime.now(timezone.utc)
    )
    embed.set_thumbnail(url=user.display_avatar.url if user.display_avatar else None)
    embed.add_field(name="📅 Member Since", value=member_since, inline=True)
    embed.add_field(name="⭐ Seller", value=f"{format_stars(seller_avg)}\n{seller_sales} sale(s)", inline=True)
    embed.add_field(name="🛒 Buyer", value=f"{format_stars(buyer_avg)}\n{buyer_purchases} purchase(s)", inline=True)

    # Active listings
    try:
        async with client.db.acquire() as conn:
            listings = await conn.fetch(
                "SELECT title FROM estate_listings WHERE seller_id=$1 AND status='active' LIMIT 5",
                uid
            )
        if listings:
            listing_text = "\n".join([f"• {l['title']}" for l in listings])
            embed.add_field(name="🏪 Active Listings", value=listing_text, inline=False)
    except Exception:
        pass

    if warnings > 0:
        embed.add_field(name="⚠️ Warnings", value=f"{warnings} active warning(s)", inline=False)

    embed.set_footer(text="Adrian — Collector Profile")

    # Public profile action buttons
    pub_view = discord.ui.View(timeout=300)

    # Button 1 — Send Message
    msg_btn = discord.ui.Button(label="Send Message", emoji="📩", style=discord.ButtonStyle.primary, row=0)
    async def on_send_message(interaction2: discord.Interaction):
        class MessageModal(discord.ui.Modal, title="Send a Message"):
            message = discord.ui.TextInput(
                label="Your message",
                style=discord.TextStyle.paragraph,
                placeholder="Write your message here...",
                max_length=1000
            )
            async def on_submit(self2, interaction3: discord.Interaction):
                try:
                    dm_embed = discord.Embed(
                        title="📩 New Message via Adrian",
                        description=self2.message.value,
                        color=discord.Color.dark_gold(),
                        timestamp=datetime.now(timezone.utc)
                    )
                    dm_embed.add_field(name="From", value=f"{interaction3.user.display_name} (`{interaction3.user.id}`)", inline=True)
                    dm_embed.set_footer(text="Reply to this user directly in Discord")
                    target_user = await client.fetch_user(int(uid))
                    await target_user.send(embed=dm_embed)
                    await interaction3.response.send_message("✅ Message sent!", ephemeral=True)
                    logger.info(f"[Profile] {interaction3.user} sent message to {uid}")
                except discord.Forbidden:
                    await interaction3.response.send_message("⚠️ This user has DMs disabled.", ephemeral=True)
                except Exception as e:
                    await interaction3.response.send_message(f"⚠️ Could not send message: {e}", ephemeral=True)
        await interaction2.response.send_modal(MessageModal())
    msg_btn.callback = on_send_message
    pub_view.add_item(msg_btn)

    # Button 2 — Report User
    report_btn = discord.ui.Button(label="Report User", emoji="🚩", style=discord.ButtonStyle.danger, row=0)
    async def on_report(interaction2: discord.Interaction):
        class ReportModal(discord.ui.Modal, title="Report User"):
            reason = discord.ui.TextInput(
                label="Reason for report",
                style=discord.TextStyle.paragraph,
                placeholder="Describe why you are reporting this user...",
                max_length=500
            )
            async def on_submit(self2, interaction3: discord.Interaction):
                await interaction3.response.defer(ephemeral=True)
                try:
                    report_channel = client.get_channel(1516868724479492107)
                    if not report_channel:
                        await interaction3.followup.send("⚠️ Could not submit report. Please try again later.", ephemeral=True)
                        return

                    reported_user = await client.fetch_user(int(uid))
                    reporter = interaction3.user

                    report_embed = discord.Embed(
                        title="🚩 User Report",
                        color=discord.Color.red(),
                        timestamp=datetime.now(timezone.utc)
                    )
                    report_embed.add_field(name="Reported User", value=f"{reported_user.display_name} (`{uid}`)", inline=True)
                    report_embed.add_field(name="Reporter", value=f"{reporter.display_name} (`{reporter.id}`)", inline=True)
                    report_embed.add_field(name="Server", value=interaction3.guild.name if interaction3.guild else "Unknown", inline=True)
                    report_embed.add_field(name="Reason", value=self2.reason.value, inline=False)
                    report_embed.set_thumbnail(url=reported_user.display_avatar.url if reported_user.display_avatar else None)
                    report_embed.set_footer(text="Adrian — Report System")

                    # Action buttons on report
                    report_action_view = discord.ui.View(timeout=None)

                    do_nothing_btn = discord.ui.Button(label="✅ Do Nothing", style=discord.ButtonStyle.secondary, row=0)
                    async def on_do_nothing(interaction4: discord.Interaction):
                        for child in report_action_view.children:
                            child.disabled = True
                        await interaction4.message.edit(view=report_action_view)
                        await interaction4.response.send_message("Report dismissed.", ephemeral=True)
                        logger.info(f"[Report] {interaction4.user} dismissed report on {uid}")
                    do_nothing_btn.callback = on_do_nothing
                    report_action_view.add_item(do_nothing_btn)

                    warn_reporter_btn = discord.ui.Button(label="⚠️ Warn Reporter", style=discord.ButtonStyle.secondary, row=0)
                    async def on_warn_reporter(interaction4: discord.Interaction):
                        class WarnReporterModal(discord.ui.Modal, title="Warn Reporter"):
                            msg = discord.ui.TextInput(label="Warning message", style=discord.TextStyle.paragraph, max_length=500, required=False, placeholder="Leave blank for default message")
                            async def on_submit(self3, interaction5: discord.Interaction):
                                try:
                                    default = "Please do not abuse the report system. False reports may result in a ban."
                                    final_msg = self3.msg.value if self3.msg.value else default
                                    warn_embed = discord.Embed(title="⚠️ Warning", description=final_msg, color=discord.Color.orange(), timestamp=datetime.now(timezone.utc))
                                    warn_embed.set_footer(text="Adrian — Report System")
                                    await reporter.send(embed=warn_embed)
                                    await interaction5.response.send_message(f"✅ Warning sent to {reporter.display_name}.", ephemeral=True)
                                    logger.info(f"[Report] {interaction5.user} warned reporter {reporter.id}")
                                except discord.Forbidden:
                                    await interaction5.response.send_message("⚠️ Could not DM the reporter.", ephemeral=True)
                        await interaction4.response.send_modal(WarnReporterModal())
                    warn_reporter_btn.callback = on_warn_reporter
                    report_action_view.add_item(warn_reporter_btn)

                    warn_user_btn = discord.ui.Button(label="⚠️ Warn User", style=discord.ButtonStyle.danger, row=0)
                    async def on_warn_user(interaction4: discord.Interaction):
                        class WarnUserModal(discord.ui.Modal, title="Warn Reported User"):
                            msg = discord.ui.TextInput(label="Warning message", style=discord.TextStyle.paragraph, max_length=500)
                            async def on_submit(self3, interaction5: discord.Interaction):
                                try:
                                    warn_embed = discord.Embed(title="⚠️ Warning from Adrian", description=self3.msg.value, color=discord.Color.red(), timestamp=datetime.now(timezone.utc))
                                    warn_embed.set_footer(text="Adrian — Report System")
                                    await reported_user.send(embed=warn_embed)
                                    await db_add_user_warning(str(uid), self3.msg.value, warning_type="report", issued_by=str(interaction5.user.id), guild_id=str(interaction5.guild.id) if interaction5.guild else None)
                                    await interaction5.response.send_message(f"✅ Warning sent to {reported_user.display_name}.", ephemeral=True)
                                    logger.info(f"[Report] {interaction5.user} warned reported user {uid}")
                                except discord.Forbidden:
                                    await interaction5.response.send_message("⚠️ Could not DM the reported user.", ephemeral=True)
                        await interaction4.response.send_modal(WarnUserModal())
                    warn_user_btn.callback = on_warn_user
                    report_action_view.add_item(warn_user_btn)

                    ban_btn = discord.ui.Button(label="🔨 Ban", style=discord.ButtonStyle.danger, row=1)
                    async def on_ban(interaction4: discord.Interaction):
                        ban_view = discord.ui.View(timeout=60)
                        ban_select = discord.ui.Select(
                            placeholder="Who do you want to ban?",
                            options=[
                                discord.SelectOption(label=f"Ban Reporter — {reporter.display_name}", value="reporter", emoji="🚩"),
                                discord.SelectOption(label=f"Ban Reported User — {reported_user.display_name}", value="reported", emoji="🔨"),
                            ]
                        )
                        async def on_ban_select(interaction5: discord.Interaction):
                            target = ban_select.values[0]
                            target_id = str(reporter.id) if target == "reporter" else str(uid)
                            target_name = reporter.display_name if target == "reporter" else reported_user.display_name
                            async with client.db.acquire() as conn:
                                await conn.execute(
                                    "INSERT INTO user_bans (user_id, reason, banned_by, banned_at) VALUES ($1, $2, $3, $4) ON CONFLICT (user_id) DO UPDATE SET reason=$2, banned_by=$3, banned_at=$4",
                                    target_id, f"Banned via report system by {interaction5.user.display_name}", str(interaction5.user.id), int(datetime.now(timezone.utc).timestamp())
                                )
                            await interaction5.response.send_message(f"🔨 **{target_name}** has been banned from Adrian.", ephemeral=True)
                            logger.info(f"[Report] {interaction5.user} banned {target_id} via report system")
                        ban_select.callback = on_ban_select
                        ban_view.add_item(ban_select)
                        await interaction4.response.send_message("Who do you want to ban?", view=ban_view, ephemeral=True)
                    ban_btn.callback = on_ban
                    report_action_view.add_item(ban_btn)

                    await report_channel.send(embed=report_embed, view=report_action_view)
                    await interaction3.followup.send("✅ Your report has been submitted. Thank you.", ephemeral=True)
                    logger.info(f"[Report] {reporter.id} reported {uid}: {self2.reason.value[:50]}")

                except Exception as e:
                    logger.error(f"[Report] Error submitting report: {e}\n{traceback.format_exc()}")
                    await interaction3.followup.send("⚠️ Something went wrong submitting your report.", ephemeral=True)

        await interaction2.response.send_modal(ReportModal())
    report_btn.callback = on_report
    pub_view.add_item(report_btn)

    await interaction.followup.send(embed=embed, view=pub_view, ephemeral=True)


async def show_private_profile(interaction):
    """Private profile — only the user sees this via /profile."""
    uid = str(interaction.user.id)
    user = interaction.user

    async with client.db.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM user_preferences WHERE user_id=$1", uid
        )

    if not row:
        await interaction.followup.send(
            embed=discord.Embed(
                title="👤 No Profile Yet",
                description="You haven\'t set up your Adrian profile yet. Click **Get Started** in #adrian or run `/start`.",
                color=discord.Color.orange()
            ),
            ephemeral=True
        )
        return

    seller_avg, seller_count = await db_get_seller_rating(uid)
    buyer_avg, buyer_count = await db_get_buyer_rating(uid)
    seller_sales, buyer_purchases = await db_get_completed_transactions(uid)
    points = await db_get_user_points(uid)
    warnings = await db_get_user_warnings(uid)
    follows = await db_get_follows(uid)
    is_premium = await db_is_premium(uid)
    is_beta = await db_is_beta_tester(uid)

    badges = ""
    if interaction.user.id == BOT_OWNER_ID: badges += " 🛠️"
    if is_beta: badges += " 🤖"
    if is_premium: badges += " ❤️"

    member_since = f"<t:{int(user.created_at.timestamp())}:D>"

    embed = discord.Embed(
        title=f"👤 {user.display_name}{badges}",
        description="Your private profile — only you can see this.",
        color=discord.Color.dark_gold(),
        timestamp=datetime.now(timezone.utc)
    )
    embed.set_thumbnail(url=user.display_avatar.url if user.display_avatar else None)
    embed.add_field(name="📅 Member Since", value=member_since, inline=True)
    embed.add_field(name="⭐ Seller", value=f"{format_stars(seller_avg)}\n{seller_sales} sale(s)", inline=True)
    embed.add_field(name="🛒 Buyer", value=f"{format_stars(buyer_avg)}\n{buyer_purchases} purchase(s)", inline=True)

    # Followed dealers dropdown
    if follows:
        dealer_options = [
            discord.SelectOption(label=f["dealer_name"][:100], value=f["dealer_name"])
            for f in follows[:25]
        ]
    else:
        dealer_options = [discord.SelectOption(label="No dealers followed yet", value="none")]

    # WAF/USMF subscriptions
    waf_cats = row.get("waf_categories", "") or ""
    usmf_cats = row.get("usmf_categories", "") or ""
    waf_list = [c for c in waf_cats.split(",") if c] if waf_cats else []
    usmf_list = [c for c in usmf_cats.split(",") if c] if usmf_cats else []

    forum_text = ""
    if waf_list:
        forum_text += f"**WAF:** {', '.join(waf_list[:3])}{'...' if len(waf_list) > 3 else ''}\n"
    if usmf_list:
        forum_text += f"**USMF:** {', '.join(usmf_list[:3])}{'...' if len(usmf_list) > 3 else ''}"
    if not forum_text:
        forum_text = "No forum subscriptions"

    embed.add_field(name="🔔 Following", value=f"{len(follows)} dealer(s)", inline=True)
    embed.add_field(name="🎖️ Forum Subscriptions", value=forum_text, inline=False)

    # Transaction history
    try:
        async with client.db.acquire() as conn:
            txs = await conn.fetch(
                """SELECT item_title, status, seller_id, buyer_id FROM estate_transactions
                   WHERE seller_id=$1 OR buyer_id=$1
                   ORDER BY created_at DESC LIMIT 5""",
                uid
            )
        if txs:
            tx_text = "\n".join([
                f"{'sold' if t['seller_id'] == uid else 'bought'} — {t['item_title'][:40]}"
                for t in txs
            ])
            embed.add_field(name="📋 Recent Transactions", value=tx_text, inline=False)
    except Exception:
        pass

    if warnings > 0:
        embed.add_field(name="⚠️ Warnings", value=f"{warnings} active warning(s)", inline=False)

    embed.set_footer(text="Adrian — Your Private Profile | Run /start to update preferences")

    # 4 action buttons
    view = discord.ui.View(timeout=300)

    # Button 1 — Manage followed dealers
    dealers_btn = discord.ui.Button(label="🔔 Dealers", style=discord.ButtonStyle.secondary, row=0)
    async def on_dealers(interaction2: discord.Interaction):
        await interaction2.response.defer(ephemeral=True)
        current_follows = await db_get_follows(uid)
        if not current_follows:
            await interaction2.followup.send("You\'re not following any dealers yet. Click 🔔 on any dealer alert to follow them.", ephemeral=True)
            return
        dealer_options = [
            discord.SelectOption(label=f["dealer_name"][:100], value=f["dealer_name"])
            for f in current_follows[:25]
        ]
        unfollow_view = discord.ui.View(timeout=120)
        unfollow_select = discord.ui.Select(
            placeholder="🔕 Select a dealer to unfollow...",
            options=dealer_options,
            min_values=1,
            max_values=1
        )
        async def on_unfollow(interaction3: discord.Interaction):
            dealer = unfollow_select.values[0]
            async with client.db.acquire() as conn:
                await conn.execute("DELETE FROM dealer_follows WHERE user_id=$1 AND dealer_name=$2", uid, dealer)
            await interaction3.response.send_message(f"🔕 Unfollowed **{dealer}**.", ephemeral=True)
            logger.info(f"[Profile] {interaction3.user} unfollowed {dealer}")
        unfollow_select.callback = on_unfollow
        unfollow_view.add_item(unfollow_select)
        follow_embed = discord.Embed(
            title="🔔 Your Followed Dealers",
            description="\n".join([f"• {f['dealer_name']}" for f in current_follows]),
            color=discord.Color.dark_gold()
        )
        follow_embed.set_footer(text=f"{len(current_follows)}/{FREE_DEALER_FOLLOW_LIMIT} dealer follows used")
        await interaction2.followup.send(embed=follow_embed, view=unfollow_view, ephemeral=True)
    dealers_btn.callback = on_dealers
    view.add_item(dealers_btn)

    # Button 2 — Manage forum categories
    forums_btn = discord.ui.Button(label="🎖️ Forum Categories", style=discord.ButtonStyle.secondary, row=0)
    async def on_forums(interaction2: discord.Interaction):
        await interaction2.response.defer(ephemeral=True)
        async with client.db.acquire() as conn:
            pref_row = await conn.fetchrow("SELECT waf_categories, usmf_categories FROM user_preferences WHERE user_id=$1", uid)
        waf_cats = (pref_row["waf_categories"] or "") if pref_row else ""
        usmf_cats = (pref_row["usmf_categories"] or "") if pref_row else ""
        waf_list = [c for c in waf_cats.split(",") if c]
        usmf_list = [c for c in usmf_cats.split(",") if c]

        # Show current subscriptions
        cats_embed = discord.Embed(title="🎖️ Your Forum Subscriptions", color=discord.Color.dark_gold())
        cats_embed.add_field(
            name="WAF Categories",
            value="\n".join([f"• {c}" for c in waf_list]) if waf_list else "None selected",
            inline=False
        )
        cats_embed.add_field(
            name="USMF Categories",
            value="\n".join([f"• {c}" for c in usmf_list]) if usmf_list else "None selected",
            inline=False
        )
        cats_embed.set_footer(text="Select a forum below to update your categories")

        # Forum picker view
        forum_pick_view = discord.ui.View(timeout=120)
        forum_select = discord.ui.Select(
            placeholder="Which forum do you want to update?",
            options=[
                discord.SelectOption(label="WAF — Wehrmacht Awards Forum", value="waf", emoji="🟥"),
                discord.SelectOption(label="USMF — US Militaria Forum", value="usmf", emoji="🟩"),
            ],
            min_values=1,
            max_values=1
        )

        async def on_forum_pick(interaction3: discord.Interaction):
            chosen = forum_select.values[0]
            await interaction3.response.defer(ephemeral=True)

            if chosen == "waf":
                options = [
                    discord.SelectOption(
                        label=cat["name"][:100],
                        value=cat["name"],
                        emoji=cat.get("emoji", "🎖️"),
                        default=cat["name"] in waf_list
                    )
                    for cat in WAF_CATEGORIES if cat["name"] != "All WAF Updates"
                ]
                title = "🟥 WAF Categories"
                save_key = "waf"
            else:
                options = [
                    discord.SelectOption(
                        label=cat["name"][:100],
                        value=cat["name"],
                        emoji=cat.get("emoji", "📦"),
                        default=cat["name"] in usmf_list
                    )
                    for cat in USMF_CATEGORIES
                ]
                title = "🟩 USMF Categories"
                save_key = "usmf"

            cat_view = discord.ui.View(timeout=120)
            cat_selected = []

            cat_select = discord.ui.Select(
                placeholder=f"Select {title} categories...",
                options=options,
                min_values=1,
                max_values=len(options)
            )

            async def on_cat_select(interaction4: discord.Interaction):
                nonlocal cat_selected
                cat_selected = list(cat_select.values)
                await interaction4.response.defer(ephemeral=True)
            cat_select.callback = on_cat_select
            cat_view.add_item(cat_select)

            save_btn2 = discord.ui.Button(label="✅ Save", style=discord.ButtonStyle.success, row=1)
            async def on_save(interaction4: discord.Interaction):
                await interaction4.response.defer(ephemeral=True)
                selected = cat_selected or list(cat_select.values) if cat_select.values else cat_selected
                if not selected:
                    await interaction4.followup.send("Please select at least one category first.", ephemeral=True)
                    return
                if save_key == "waf":
                    await db_save_user_waf_categories(str(uid), selected)
                else:
                    await db_save_user_usmf_categories(str(uid), selected)
                await interaction4.followup.send(
                    embed=discord.Embed(
                        title="✅ Categories Saved",
                        description=f"Updated **{title}** subscriptions:\n" + "\n".join([f"• {c}" for c in selected]),
                        color=discord.Color.green()
                    ),
                    ephemeral=True
                )
                logger.info(f"[Profile] {interaction4.user} updated {save_key} categories: {selected}")
            save_btn2.callback = on_save
            cat_view.add_item(save_btn2)

            cat_embed = discord.Embed(
                title=title,
                description="Select the categories you want to follow then click **Save**.",
                color=discord.Color.dark_gold()
            )
            await interaction3.followup.send(embed=cat_embed, view=cat_view, ephemeral=True)

        forum_select.callback = on_forum_pick
        forum_pick_view.add_item(forum_select)
        await interaction2.followup.send(embed=cats_embed, view=forum_pick_view, ephemeral=True)
    forums_btn.callback = on_forums
    view.add_item(forums_btn)

    # Button 3 — Buy Premium
    premium_btn = discord.ui.Button(label="Buy Premium", emoji="❤️", style=discord.ButtonStyle.danger, row=0)
    async def on_premium(interaction2: discord.Interaction):
        await interaction2.response.send_message(
            "❤️ Adrian Premium is coming soon! We\'ll announce it when it\'s available.",
            ephemeral=True
        )
    premium_btn.callback = on_premium
    view.add_item(premium_btn)

    # Button 4 — Clear profile
    clear_btn = discord.ui.Button(label="🗑️ Clear Profile", style=discord.ButtonStyle.danger, row=0)
    async def on_clear(interaction2: discord.Interaction):
        confirm_view = discord.ui.View(timeout=60)
        yes_btn = discord.ui.Button(label="Yes, clear my profile", style=discord.ButtonStyle.danger)
        no_btn = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.secondary)
        async def on_yes(interaction3: discord.Interaction):
            async with client.db.acquire() as conn:
                await conn.execute("DELETE FROM user_preferences WHERE user_id=$1", uid)
                await conn.execute("DELETE FROM dealer_follows WHERE user_id=$1", uid)
            if interaction3.guild:
                member = interaction3.guild.get_member(int(uid))
                if member:
                    roles_to_remove = [r for r in member.roles if r.name in ("Adrian Verified", "Estand Verified", "NA", "EU", "WAF", "USMF", "Adrian Premium")]
                    if roles_to_remove:
                        try:
                            await member.remove_roles(*roles_to_remove, reason="Profile cleared")
                        except Exception:
                            pass
            await interaction3.response.edit_message(
                embed=discord.Embed(title="🗑️ Profile Cleared", description="Your Adrian profile has been reset. Run `/start` to set up again.", color=discord.Color.red()),
                view=None
            )
            logger.info(f"[Profile] {interaction3.user} cleared their profile")
        async def on_no(interaction3: discord.Interaction):
            await interaction3.response.edit_message(
                embed=discord.Embed(description="Cancelled.", color=discord.Color.green()),
                view=None
            )
        yes_btn.callback = on_yes
        no_btn.callback = on_no
        confirm_view.add_item(yes_btn)
        confirm_view.add_item(no_btn)
        await interaction2.response.send_message(
            embed=discord.Embed(
                title="⚠️ Clear Profile?",
                description="This will delete all your preferences, dealer follows and remove your Adrian roles.\n\nAre you sure?",
                color=discord.Color.red()
            ),
            view=confirm_view,
            ephemeral=True
        )
    clear_btn.callback = on_clear
    view.add_item(clear_btn)

    await interaction.followup.send(embed=embed, view=view, ephemeral=True)


async def show_admin_profile(interaction, user, member=None):
    """Admin profile — mods and bot owner only via /lookup."""
    uid = str(user.id)

    seller_avg, seller_count = await db_get_seller_rating(uid)
    buyer_avg, buyer_count = await db_get_buyer_rating(uid)
    seller_sales, buyer_purchases = await db_get_completed_transactions(uid)
    points = await db_get_user_points(uid)
    warnings = await db_get_user_warnings(uid)
    is_premium = await db_is_premium(uid)
    is_beta = await db_is_beta_tester(uid)

    badges = ""
    if is_beta: badges += " 🤖"
    if is_premium: badges += " ❤️"

    # Ban status
    try:
        async with client.db.acquire() as conn:
            ban_row = await conn.fetchrow(
                "SELECT reason FROM user_bans WHERE user_id=$1", uid
            )
        ban_status = f"🚫 Banned: {ban_row['reason']}" if ban_row else "✅ Not banned"
    except Exception:
        ban_status = "Unknown"

    # Warning history
    try:
        async with client.db.acquire() as conn:
            warn_rows = await conn.fetch(
                "SELECT reason, issued_at FROM user_warnings WHERE user_id=$1 ORDER BY issued_at DESC LIMIT 5",
                uid
            )
        warn_text = "\n".join([
            f"• {w['reason'][:60]} — <t:{w['issued_at']}:D>"
            for w in warn_rows
        ]) if warn_rows else "No warnings"
    except Exception:
        warn_text = "Could not load"

    # Report history
    try:
        async with client.db.acquire() as conn:
            report_count = await conn.fetchval(
                "SELECT COUNT(*) FROM estate_reports WHERE seller_id=$1", uid
            ) or 0
        report_text = f"{report_count} report(s)"
    except Exception:
        report_text = "Unknown"

    # All transactions
    try:
        async with client.db.acquire() as conn:
            txs = await conn.fetch(
                """SELECT item_title, status, seller_id, buyer_id, guild_id FROM estate_transactions
                   WHERE seller_id=$1 OR buyer_id=$1
                   ORDER BY created_at DESC LIMIT 10""",
                uid
            )
        tx_text = "\n".join([
            f"{'sold' if t['seller_id'] == uid else 'bought'} — {t['item_title'][:40]}"
            for t in txs
        ]) if txs else "No transactions"
    except Exception:
        tx_text = "Could not load"

    embed = discord.Embed(
        title=f"🔒 Admin Lookup — {user.display_name}{badges}",
        color=discord.Color.red(),
        timestamp=datetime.now(timezone.utc)
    )
    embed.set_thumbnail(url=user.display_avatar.url if user.display_avatar else None)
    embed.add_field(name="User ID", value=uid, inline=True)
    embed.add_field(name="Account Created", value=f"<t:{int(user.created_at.timestamp())}:D>", inline=True)
    embed.add_field(name="Ban Status", value=ban_status, inline=False)
    embed.add_field(name="⭐ Seller", value=f"{format_stars(seller_avg)} · {seller_sales} sale(s)", inline=True)
    embed.add_field(name="🛒 Buyer", value=f"{format_stars(buyer_avg)} · {buyer_purchases} purchase(s)", inline=True)
    embed.add_field(name="⚠️ Active Warnings", value=str(warnings), inline=True)
    embed.add_field(name="📋 Warning History", value=warn_text, inline=False)
    embed.add_field(name="🚨 Reports Against", value=report_text, inline=True)
    embed.add_field(name="🏪 Transactions", value=tx_text, inline=False)
    embed.set_footer(text="Adrian — Admin Profile | 🔒 Confidential")

    await interaction.followup.send(embed=embed, ephemeral=True)


async def db_is_beta_tester(user_id):
    """Check if user has Adrian Premium role on any connected guild."""
    try:
        for guild in client.guilds:
            member = guild.get_member(int(user_id))
            if member:
                premium_role = discord.utils.get(guild.roles, name="Adrian Premium")
                if premium_role and premium_role in member.roles:
                    return True
    except Exception:
        pass
    return False


@client.tree.command(name="alerts", description="See your pending dealer and forum alerts")
async def alerts_cmd(interaction: discord.Interaction):
    on_cd, remaining = check_cooldown(str(interaction.user.id), "alerts")
    if on_cd:
        await interaction.response.send_message(f"⏳ Please wait {remaining}s before checking alerts again.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    user_id = str(interaction.user.id)
    alerts = await db_get_pending_alerts(user_id)

    if not alerts:
        await interaction.followup.send(
            "✅ You have no pending alerts. New items matching your profile will appear here!\n\nMake sure you've completed `/start` to set up your preferences.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title=f"🔔 You have {len(alerts)} pending alert(s)!",
        color=discord.Color.dark_gold(),
        timestamp=datetime.now(timezone.utc)
    )

    for alert in alerts[:20]:  # Cap at 20 to avoid embed limits
        ts = f"<t:{alert['created_at']}:R>"
        url_text = f"[View →]({alert['dealer_url']})" if alert['dealer_url'] else "No link"
        embed.add_field(
            name=f"{alert['dealer_flag']} {alert['dealer_name']}",
            value=f"{url_text} · {ts}",
            inline=False
        )

    if len(alerts) > 20:
        embed.set_footer(text=f"Showing 20 of {len(alerts)} alerts · Alerts expire after 24 hours")
    else:
        embed.set_footer(text="Alerts expire after 24 hours · Adrian — Discord's #1 Militaria Bot")

    # Clear alerts after showing them
    await db_clear_pending_alerts(user_id)
    await interaction.followup.send(embed=embed, ephemeral=True)

@client.tree.command(name="reputation", description="Check a member's buyer reputation in the estate")
@app_commands.describe(member="The member to look up")
async def reputation_cmd(interaction: discord.Interaction, member: discord.Member):
    rating, count = await db_get_buyer_rating(str(member.id))
    embed = discord.Embed(
        title=f"🏅 Buyer Reputation — {member.display_name}",
        color=discord.Color.dark_gold(),
        timestamp=datetime.now(timezone.utc)
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    if rating is None:
        embed.description = "No ratings yet — this member has not completed any estate purchases."
    else:
        stars = "⭐" * int(rating) + ("✨" if rating % 1 >= 0.5 else "")
        embed.add_field(name="Rating", value=f"{stars} {rating}/5", inline=True)
        embed.add_field(name="Transactions", value=f"📦 {count}", inline=True)
    embed.set_footer(text="Adrian — Forum Alert | You may need to make a free forum account to see this listing")
    await interaction.response.send_message(embed=embed, ephemeral=True)

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

# ==================== WELCOME VIEW ====================

class WelcomeView(discord.ui.View):
    """Persistent buttons on the static welcome message in #adrian."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="👋 Get Started", style=discord.ButtonStyle.success, custom_id="welcome_create_profile")
    async def create_profile(self, interaction: discord.Interaction, button: discord.ui.Button):
        logger.info(f"[Welcome] Get Started clicked by {interaction.user} ({interaction.user.id}) in {interaction.guild.name}")
        on_cd, remaining = check_cooldown(str(interaction.user.id), "start")
        if on_cd:
            await interaction.response.send_message(f"⏳ Please wait {remaining}s before trying again.", ephemeral=True)
            return
        await interaction.response.send_message("👋 Loading...", ephemeral=True)
        await _show_start_onboarding(interaction)

    @discord.ui.button(label="👤 View My Profile", style=discord.ButtonStyle.primary, custom_id="welcome_view_profile")
    async def view_profile(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        # Check if user exists in DB at all (not just if region is set)
        async with client.db.acquire() as conn:
            row = await conn.fetchrow("SELECT user_id FROM user_preferences WHERE user_id=$1", str(interaction.user.id))
        if not row:
            await interaction.followup.send(
                "You don't have a profile yet! Click **👋 Get Started** to create one.",
                ephemeral=True
            )
            return
        await _send_profile(interaction, interaction.user)

    @discord.ui.button(label="🗑️ Clear My Profile", style=discord.ButtonStyle.danger, custom_id="welcome_clear_profile")
    async def clear_profile(self, interaction: discord.Interaction, button: discord.ui.Button):
        logger.info(f"[Welcome] Clear Profile clicked by {interaction.user} ({interaction.user.id})")
        await interaction.response.defer(ephemeral=True)
        region = await db_get_user_region(str(interaction.user.id))
        if not region:
            await interaction.followup.send("You don't have a profile yet — nothing to clear!", ephemeral=True)
            return
        async with client.db.acquire() as conn:
            await conn.execute(
                "UPDATE user_preferences SET region=NULL, eras=NULL, countries=NULL, forums=NULL WHERE user_id=$1",
                str(interaction.user.id)
            )
        await interaction.followup.send(
            embed=discord.Embed(
                title="🗑️ Profile Preferences Cleared",
                description=(
                    "Your alert preferences have been reset.\n\n"
                    "**Your reputation, ratings and transaction history are untouched.**\n\n"
                    "Click **👋 Get Started** to set up new preferences."
                ),
                color=discord.Color.red()
            ),
            ephemeral=True
        )


async def _send_profile(interaction, user):
    """Build and send a user profile embed with action buttons."""
    logger.info(f"[Profile] Building profile for {user} ({user.id})")
    uid = str(user.id)

    # Preferences
    region = await db_get_user_region(uid)
    eras_raw = await db_get_user_eras(uid)
    countries_raw = await db_get_user_countries(uid)
    forums_raw = await db_get_user_forums(uid)

    era_names = {0: "All Eras", 1: "Pre-1914", 2: "WWI", 3: "WWII", 4: "Korean War", 5: "Vietnam", 6: "Cold War", 7: "GWOT"}
    country_names = {
        "Z": "🌍 All Countries", "A": "🇺🇸 US", "B": "🇬🇧 British",
        "C": "🇨🇦 Canadian", "D": "🇩🇪 German", "E": "🇷🇺 Soviet",
        "F": "🇫🇷 French", "G": "🇯🇵 Japanese", "H": "🇮🇹 Italian",
        "I": "🇦🇹 Austro-Hungarian", "J": "Other Axis", "K": "Other Allied",
        "L": "🌐 Multi", "M": "🇨🇳 Chinese/KMT"
    }

    region_display = {"na": "NA", "eu": "EU", "both": "NA / EU"}.get((region or "").lower(), region or "Not set")
    forums_raw_lower = (forums_raw or "").lower()
    forums_display = {"waf": "WAF", "usmf": "USMF", "both": "WAF / USMF", "none": "None"}.get(forums_raw_lower, forums_raw or "Not set")

    eras_list = [int(e) for e in (eras_raw or [0])] if eras_raw else [0]
    eras_str = "🌍 All Eras" if 0 in eras_list else ", ".join([era_names.get(e, str(e)) for e in sorted(eras_list)])

    countries_list = countries_raw or ["Z"]
    if "Z" in countries_list:
        countries_str = "🌍 All Countries"
    else:
        known = [country_names[c] for c in countries_list if c in country_names]
        countries_str = ", ".join(known) if known else "Not set"

    # Reputation
    seller_avg, seller_count = await db_get_seller_rating(uid)
    buyer_avg, buyer_count = await db_get_buyer_rating(uid)
    seller_sales, buyer_purchases = await db_get_completed_transactions(uid)

    # Rank
    points = await db_get_user_points(uid)
    warnings = await db_get_user_warnings(uid)
    rank = get_rank(points, warnings > 0)
    top_percent = await db_get_top_percent(uid)


    title = f"🎖️ {user.display_name}'s Collector Profile"
    if top_percent:
        title += f"  {top_percent}"

    embed = discord.Embed(title=title, color=discord.Color.dark_gold(), timestamp=datetime.now(timezone.utc))
    embed.set_thumbnail(url=user.display_avatar.url)

    # Rank row
    embed.add_field(name="🎗️ Rank", value=f"{rank}\n{points:,} pts", inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)

    # Preferences
    embed.add_field(name="📍 Region", value=region_display, inline=True)
    embed.add_field(name="📋 Forums", value=forums_display, inline=True)
    embed.add_field(name="⏳ Eras", value=eras_str, inline=False)
    embed.add_field(name="🌐 Countries", value=countries_str, inline=False)

    # Reputation
    embed.add_field(name="\u200b", value="**— Reputation —**", inline=False)
    embed.add_field(name="🏪 Seller", value=f"{format_stars(seller_avg)}\n{seller_sales} sale(s)", inline=True)
    embed.add_field(name="🛒 Buyer", value=f"{format_stars(buyer_avg)}\n{buyer_purchases} purchase(s)", inline=True)

    embed.set_footer(text="Adrian — Collector Profile")

    # Profile action buttons
    class ProfileActionsView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)

        @discord.ui.button(label="📦 My Followed Dealers", style=discord.ButtonStyle.secondary)
        async def show_follows(self, interaction2: discord.Interaction, button: discord.ui.Button):
            logger.info(f"[Profile] My Followed Dealers clicked by {interaction2.user} ({interaction2.user.id})")
            await interaction2.response.defer(ephemeral=True)
            async with client.db.acquire() as conn:
                rows = await conn.fetch("SELECT dealer_name FROM dealer_follows WHERE user_id=$1 ORDER BY timestamp ASC", uid)
            if not rows:
                await interaction2.followup.send("You aren't following any dealers yet.", ephemeral=True)
                return
            dealer_list = [r["dealer_name"] for r in rows]

            class ClearFollowsView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=120)

                @discord.ui.button(label="🗑️ Clear All Follows", style=discord.ButtonStyle.danger)
                async def clear_follows(self, interaction3: discord.Interaction, button: discord.ui.Button):
                    async with client.db.acquire() as conn:
                        await conn.execute("DELETE FROM dealer_follows WHERE user_id=$1", uid)
                    await interaction3.response.send_message("✅ All dealer follows cleared.", ephemeral=True)

            follows_text = "\n".join([f"• {d}" for d in dealer_list])
            await interaction2.followup.send(
                embed=discord.Embed(
                    title=f"📦 Followed Dealers ({len(dealer_list)})",
                    description=follows_text,
                    color=discord.Color.dark_gold()
                ),
                view=ClearFollowsView(),
                ephemeral=True
            )

        @discord.ui.button(label="💬 My Transaction Reviews", style=discord.ButtonStyle.secondary)
        async def show_reviews(self, interaction2: discord.Interaction, button: discord.ui.Button):
            logger.info(f"[Profile] My Transaction Reviews clicked by {interaction2.user} ({interaction2.user.id})")
            await interaction2.response.defer(ephemeral=True)
            reviews = await db_get_user_reviews(uid)
            if not reviews:
                await interaction2.followup.send("No transaction reviews yet — complete a sale or purchase to get started!", ephemeral=True)
                return
            review_text = ""
            for r in reviews[:10]:
                role = "Seller" if str(r["seller_id"]) == uid else "Buyer"
                comment = f'*"{r["review"]}"*' if r.get("review") else "*No comment*"
                review_text += f"⭐ {r['rating']}/5 as **{role}** — {comment}\n"
            await interaction2.followup.send(
                embed=discord.Embed(
                    title="💬 Transaction Reviews",
                    description=review_text.strip(),
                    color=discord.Color.dark_gold()
                ),
                ephemeral=True
            )

        @discord.ui.button(label="🗑️ Clear My Profile", style=discord.ButtonStyle.danger)
        async def clear_profile_action(self, interaction2: discord.Interaction, button: discord.ui.Button):
            await interaction2.response.defer(ephemeral=True)
            async with client.db.acquire() as conn:
                await conn.execute(
                    "UPDATE user_preferences SET region=NULL, eras=NULL, countries=NULL, forums=NULL WHERE user_id=$1",
                    uid
                )
            await interaction2.followup.send(
                embed=discord.Embed(
                    title="🗑️ Profile Preferences Cleared",
                    description=(
                        "Your alert preferences have been reset.\n\n"
                        "**Your reputation, ratings and transaction history are untouched.**\n\n"
                        "Click **👋 Get Started** in the #adrian channel to set up new preferences."
                    ),
                    color=discord.Color.red()
                ),
                ephemeral=True
            )


    await interaction.followup.send(embed=embed, view=ProfileActionsView(), ephemeral=True)

# ==================== EVENTS ====================
@client.event
async def on_error(event, *args, **kwargs):
    logger.error(f"Discord error in event '{event}': {traceback.format_exc()}")

@client.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    command_name = interaction.command.name if interaction.command else "unknown"
    logger.error(f"[Error] Slash command '{command_name}' failed: {error}")
    logger.error(traceback.format_exc())

    # Log to private mod channel
    try:
        log_channel = client.get_channel(PRIVATE_LOG_CHANNEL_ID)
        if log_channel:
            error_embed = discord.Embed(
                title="⚠️ Command Error",
                color=discord.Color.red(),
                timestamp=datetime.now(timezone.utc)
            )
            error_embed.add_field(name="Command", value=f"`/{command_name}`", inline=True)
            error_embed.add_field(name="User", value=f"{interaction.user} ({interaction.user.id})", inline=True)
            error_embed.add_field(name="Server", value=f"{interaction.guild.name if interaction.guild else 'DM'}", inline=True)
            error_embed.add_field(name="Error", value=f"```{str(error)[:500]}```", inline=False)
            await log_channel.send(embed=error_embed)
    except Exception as _e:

        logger.debug(f"[Silent] {_e}")

    # Friendly message to user based on error type
    if isinstance(error, app_commands.CommandOnCooldown):
        msg = f"⏳ This command is on cooldown. Try again in **{error.retry_after:.0f} seconds**."
    elif isinstance(error, app_commands.MissingPermissions):
        msg = "🚫 You don\'t have permission to use this command."
    elif isinstance(error, app_commands.BotMissingPermissions):
        msg = "🚫 I\'m missing permissions to do that. Please make sure I have the right roles."
    elif isinstance(error, app_commands.CommandNotFound):
        msg = "❓ Unknown command."
    elif isinstance(error, app_commands.CheckFailure):
        msg = "🚫 You don\'t have access to this command."
    else:
        msg = (
            "The error has been logged and will be looked into. "
            "Please try again in a moment or contact a mod if it keeps happening."
        )
        # Show 404 image for unknown errors
        try:
            embeds = []
            if bot_state.get("error_404_img_url"):
                err_embed = discord.Embed(color=discord.Color.red())
                err_embed.set_image(url=bot_state["error_404_img_url"])
                embeds.append(err_embed)
            text_embed = discord.Embed(
                description=msg,
                color=discord.Color.red()
            )
            embeds.append(text_embed)
            if not interaction.response.is_done():
                await interaction.response.send_message(embeds=embeds, ephemeral=True)
            else:
                await interaction.followup.send(embeds=embeds, ephemeral=True)
        except Exception as _e:

            logger.debug(f"[Silent] {_e}")
        return

    try:
        if not interaction.response.is_done():
            await interaction.response.send_message(msg, ephemeral=True)
        else:
            await interaction.followup.send(msg, ephemeral=True)
    except Exception as _e:

        logger.debug(f"[Silent] {_e}")

@client.event
async def on_guild_join(guild):
    """When bot joins a new server, DM the owner to run /setup."""
    try:
        logger.info(f"[Guild] ==============================")
        logger.info(f"[Guild] Joined new server: {guild.name} ({guild.id})")
        logger.info(f"[Guild] Owner ID: {guild.owner_id}")
        logger.info(f"[Guild] Member count: {guild.member_count}")
        logger.info(f"[Guild] ==============================")
        # Save basic info
        await db_save_server_config(
            str(guild.id),
            guild_name=guild.name,
            owner_id=str(guild.owner_id)
        )
        # DM the server owner
        try:
            owner = await client.fetch_user(guild.owner_id)
            if owner:
                embed = discord.Embed(
                    title="👋 Hey! I'm Adrian — Thanks for the invite!",
                    description=(
                        f"I'm now on **{guild.name}** and ready to get to work!\n\n"
                        "Here's what I can do for your community:\n\n"
                        "📬 **New Item Alerts** — I monitor 100+ militaria dealer websites for new items\n"
                        "🗞️ **Forum Alerts** — I monitor all the major collector forums for new items for sale\n"
                        "🎖️ **Collector Profiles** — Members build a personalized feed based on their era, country, and region\n"
                        "🏪 **Estand Marketplace** — A trusted buy/sell system with global seller ratings and scam protection\n"
                        "⭐ **Cross-Server Reputation** — Buyer & seller ratings and reviews follow members across every Adrian server\n"
                        "🌐 **Cross-Server Listings** — Sellers reach buyers on every server running Adrian\n\n"
                        "**To get started, run `/setup` in your server.**\n"
                        "It only takes 2 minutes and I'll handle everything automatically — channels, permissions, roles, all of it."
                    ),
                    color=discord.Color.dark_gold()
                )
                if bot_state.get("setup_q1_img_url"):
                    embed.set_thumbnail(url=bot_state["setup_q1_img_url"])
                embed.set_footer(text="Adrian — Discord's #1 Militaria Bot")
                await owner.send(embed=embed)
                logger.info(f"[Guild] DM sent to owner of {guild.name}")
        except Exception as e:
            logger.warning(f"[Guild] Could not DM owner of {guild.name}: {e}")
    except Exception as e:
        logger.error(f"[Guild] on_guild_join error: {e}\n{traceback.format_exc()}")
@client.event
async def on_member_update(before: discord.Member, after: discord.Member):
    """Watch for Estand Verified role being manually assigned."""
    try:
        # Check if Estand Verified role was just added
        before_roles = {r.id for r in before.roles}
        after_roles = {r.id for r in after.roles}
        added_roles = after_roles - before_roles
        if not added_roles:
            return

        config = await db_get_server_config(str(after.guild.id))
        estand_role_id = get_config_value(config, "estand_verified_role_id") if config else None
        if not estand_role_id:
            return

        if not estand_role_id or int(estand_role_id) not in added_roles:
            return

        logger.info(f"[Estand] Estand Verified role added to {after} ({after.id}) in {after.guild.name}")

        estand_role = after.guild.get_role(int(estand_role_id))
        if not estand_role:
            return

        # Check 1 — has user agreed to Estand rules in DB?
        async with client.db.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT estand_agreed FROM user_preferences WHERE user_id=$1",
                str(after.id)
            )
        estand_agreed = row["estand_agreed"] if row else 0

        if not estand_agreed:
            await after.remove_roles(estand_role, reason="Estand rules not agreed to via /start")
            try:
                embed = discord.Embed(
                    title="⚠️ Estand Verified Role Removed",
                    description=(
                        f"You were given the **Estand Verified** role on **{after.guild.name}** "
                        f"but you haven\'t agreed to the Estand Marketplace Rules yet.\n\n"
                        f"Run `/start` in the **#adrian** channel to agree to the rules and get proper access."
                    ),
                    color=discord.Color.orange()
                )
                embed.set_footer(text="Adrian — Estand Marketplace")
                await after.send(embed=embed)
            except discord.Forbidden:
                pass
            logger.info(f"[Estand] Removed Estand Verified from {after} — no DB agreement")
            return

        # Check 2 — has user been globally banned?
        async with client.db.acquire() as conn:
            ban_row = await conn.fetchrow(
                "SELECT id FROM user_warnings WHERE user_id=$1 AND warning_type IN ('ban', 'scammer')",
                str(after.id)
            )

        if ban_row:
            await after.remove_roles(estand_role, reason="User is globally banned from Estand")
            try:
                embed = discord.Embed(
                    title="🚫 Estand Access Denied",
                    description=(
                        "Your account has been flagged in the Adrian network and you are not permitted "
                        "to access the Estand Marketplace.\n\n"
                        "If you believe this is an error, please contact the server owner."
                    ),
                    color=discord.Color.red()
                )
                embed.set_footer(text="Adrian — Estand Marketplace")
                await after.send(embed=embed)
            except discord.Forbidden:
                pass
            logger.info(f"[Estand] Removed Estand Verified from {after} — globally banned/flagged")
            return

        logger.info(f"[Estand] Estand Verified confirmed for {after} — agreement and ban check passed")

    except Exception as e:
        logger.error(f"[Estand] on_member_update error: {e}\n{traceback.format_exc()}")

@client.event
async def on_guild_remove(guild):
    logger.info(f"[Guild] Bot removed from: {guild.name} ({guild.id})")
    """When bot is removed from a server, log it."""
    logger.info(f"[Guild] Removed from server: {guild.name} ({guild.id})")

@client.event
@client.event
async def on_message(message: discord.Message):
    """Handle incoming messages — mirror watched channels and redirect webhooks."""
    try:
        # ---- Watched channel mirroring (channelfeed feature) ----
        if not message.author.bot:
            watched = bot_state.get("watched_channels", {})
            if str(message.channel.id) in watched:
                watch_info = watched[str(message.channel.id)]
                mirror_channel = client.get_channel(watch_info["mirror_to"])
                if mirror_channel:
                    embed = discord.Embed(
                        description=message.content or "*[no text]*",
                        color=discord.Color.dark_gold(),
                        timestamp=message.created_at
                    )
                    embed.set_author(
                        name=message.author.display_name,
                        icon_url=message.author.display_avatar.url if message.author.display_avatar else None
                    )
                    embed.set_footer(text=f"#{message.channel.name} • {message.guild.name if message.guild else 'DM'}")
                    if message.attachments:
                        embed.set_image(url=message.attachments[0].url)
                    await mirror_channel.send(embed=embed)

        # ---- Webhook redirect — send to #adrian-updates if lands in #adrian ----
        if message.webhook_id and message.guild:
            config = await db_get_server_config(str(message.guild.id))
            if config:
                commands_channel_id = get_config_value(config, "channel_id")
                updates_channel_id = get_config_value(config, "updates_channel_id")
                if commands_channel_id and updates_channel_id:
                    if str(message.channel.id) == str(commands_channel_id):
                        updates_channel = message.guild.get_channel(int(updates_channel_id))
                        if updates_channel:
                            if message.embeds:
                                fwd_embed = message.embeds[0]
                            else:
                                fwd_embed = discord.Embed(
                                    description=message.content or "",
                                    color=discord.Color.dark_gold()
                                )
                            fwd_embed.set_footer(text=f"Forwarded from #{message.channel.name} — Adrian")
                            await updates_channel.send(embed=fwd_embed)
                            try:
                                await message.delete()
                            except discord.Forbidden:
                                pass
                            logger.info(f"[Message] Redirected webhook from #adrian to #adrian-updates in {message.guild.name}")

    except Exception as e:
        logger.debug(f"[Message] on_message error: {e}")

@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    """When someone reacts to the welcome image, trigger /start for them."""
    try:
        logger.debug(f"[Reaction] Reaction from {payload.user_id} in guild {payload.guild_id} on msg {payload.message_id}")
        # Ignore bot reactions
        if payload.user_id == client.user.id:
            return

        # Check if this reaction is on a welcome message for any server
        config = await db_get_server_config(str(payload.guild_id))
        if not config:
            return

        welcome_msg_id = get_config_value(config, "welcome_message_id")
        if not welcome_msg_id or payload.message_id != welcome_msg_id:
            return

        logger.info(f"[Welcome] Reaction from {payload.user_id} on welcome message in guild {payload.guild_id}")

        guild = client.get_guild(payload.guild_id)
        if not guild:
            return

        member = guild.get_member(payload.user_id)
        if not member:
            return

        channel = client.get_channel(payload.channel_id)
        if not channel:
            return

        # Remove the reaction after 5 seconds
        async def remove_reactions():
            await asyncio.sleep(5)
            try:
                message = await channel.fetch_message(payload.message_id)
                await message.clear_reactions()
                logger.info(f"[Welcome] Cleared all reactions on welcome message")
            except Exception as e:
                logger.warning(f"[Welcome] Could not clear reactions: {e}")

        asyncio.create_task(remove_reactions())

        # Trigger /start flow for the user
        region = await db_get_user_region(str(payload.user_id))
        if region:
            # Already has profile — send quick ephemeral notice
            try:
                dm = await member.create_dm()
                await dm.send(
                    embed=discord.Embed(
                        description="You already have an Adrian profile! Use `/start` to update your preferences or `/alerts` to see your pending alerts.",
                        color=discord.Color.dark_gold()
                    )
                )
            except discord.Forbidden:
                pass
            return

        # No profile — send onboarding via DM
        try:
            img_url = bot_state.get("question1_img_url")
            embed = discord.Embed(
                title="🌍 Question 1 of 5 — Your Region",
                description="Hey! I saw you reacted to the welcome post. Let\'s set up your collector profile!\n\nWhere are you based? This helps me show you the most relevant dealer alerts.",
                color=discord.Color.dark_gold()
            )
            if img_url:
                embed.set_image(url=img_url)
            dm = await member.create_dm()
            await dm.send(embed=embed)
            logger.info(f"[Welcome] Sent /start onboarding to {member} via DM")
        except discord.Forbidden:
            logger.warning(f"[Welcome] Could not DM {member} — DMs disabled")

    except Exception as e:
        logger.error(f"[Welcome] on_raw_reaction_add error: {e}\n{traceback.format_exc()}")

@client.event
async def on_thread_create(thread):
    """When a new listing is posted in the estate channel, post check before you buy."""
    try:
        logger.info(f"[Estate] on_thread_create fired: {thread.name} | parent_type={type(thread.parent).__name__} | parent_id={thread.parent_id}")

        if not isinstance(thread.parent, discord.ForumChannel):
            logger.info(f"[Estate] Skipping — not a forum channel")
            return

        # Skip mirror threads created by the bot — prevents infinite cross-post loop
        if thread.owner_id == client.user.id:
            logger.info(f"[Estate] Skipping — thread created by bot (mirror)")
            return
        if thread.name.startswith("🌐"):
            logger.info(f"[Estate] Skipping — mirror thread (starts with 🌐)")
            return

        # Check if this thread belongs to any server's estate channel
        config = await db_get_server_config(str(thread.guild.id))
        estate_channel_id = get_config_value(config, "estate_channel_id") if config else None

        # Fall back to hardcoded ID if not in DB
        if not estate_channel_id:
            estate_channel_id = ESTATE_CHANNEL_ID

        # Last resort — check if parent is ANY forum channel on this server
        # (handles case where /setup estate step was skipped but forum exists)
        if thread.parent_id != estate_channel_id:
            logger.info(f"[Estate] Channel mismatch — config={estate_channel_id} actual={thread.parent_id}")
            # Check all servers' estate channels
            all_servers = await db_get_all_servers()
            matched = any(
                get_config_value(s, "estate_channel_id") == thread.parent_id
                for s in all_servers
            )
            if not matched and thread.parent_id != ESTATE_CHANNEL_ID:
                logger.info(f"[Estate] Skipping — not a registered estate channel")
                return
            logger.info(f"[Estate] Matched via server list lookup")

        seller_id = thread.owner_id
        logger.info(f"[Estate] New listing: {thread.name} by {seller_id}")

        # Wait for Discord to create the starter message
        await asyncio.sleep(5)

        # Fetch the starter message
        starter = None
        try:
            starter = await thread.fetch_message(thread.id)
            logger.info(f"[Estate] Starter message found: {starter.content[:50] if starter.content else 'no text'}")
        except Exception as e:
            logger.warning(f"[Estate] Could not fetch starter message: {e} — posting anyway")

        # Post seller action buttons
        view = SellerProfileView(str(seller_id))
        await thread.send(view=view)
        bot_state["estand_listing_count"] += 1
        logger.info(f"[Estate] Buttons posted in {thread.name}")


        # Handle cross-posting (Option B and C)
        # Re-fetch config in case it was loaded via server list fallback
        if not config:
            config = await db_get_server_config(str(thread.guild.id))
        cross_post_enabled = False
        if config:
            cp_val = config.get("accept_cross_posts") or get_config_value(config, "accept_cross_posts")
            cross_post_enabled = str(cp_val) == "1"
        logger.info(f"[CrossPost] Server cross-post setting: {cross_post_enabled}")

        if cross_post_enabled:
            seller = await client.fetch_user(seller_id)
            if seller:
                # Option C — seller already applied Cross-Posted tag
                applied_tag_names = [t.name.lower() for t in (thread.applied_tags or [])]
                if "cross-posted" in applied_tag_names:
                    logger.info(f"[CrossPost] Auto-mirroring \'{thread.name}\' — seller applied Cross-Posted tag")
                    asyncio.create_task(cross_post_listing(thread, seller, starter if starter else None))
                else:
                    # Option B — DM seller asking if they want to cross-post
                    try:
                        class CrossPostOfferView(discord.ui.View):
                            def __init__(self):
                                super().__init__(timeout=3600)  # 1 hour

                            @discord.ui.button(label="🌐 Yes — Cross-post my listing", style=discord.ButtonStyle.success)
                            async def yes_crosspost(self, interaction: discord.Interaction, button: discord.ui.Button):
                                for child in self.children:
                                    child.disabled = True
                                await interaction.response.edit_message(
                                    embed=discord.Embed(
                                        title="🌐 Cross-posting your listing...",
                                        description="Hang tight — I\'m mirroring your listing to other Adrian servers now!",
                                        color=discord.Color.dark_gold()
                                    ),
                                    view=self
                                )
                                count = await cross_post_listing(thread, seller, starter if starter else None)
                                await interaction.edit_original_response(
                                    embed=discord.Embed(
                                        title="✅ Listing Cross-Posted!",
                                        description=f"Your listing **{thread.name}** has been mirrored to **{count}** other Adrian server(s)!\n\nInterested buyers can contact you directly via DM.",
                                        color=discord.Color.green()
                                    )
                                )

                            @discord.ui.button(label="❌ No thanks", style=discord.ButtonStyle.secondary)
                            async def no_crosspost(self, interaction: discord.Interaction, button: discord.ui.Button):
                                for child in self.children:
                                    child.disabled = True
                                await interaction.response.edit_message(
                                    embed=discord.Embed(
                                        description="No problem! Your listing stays local.",
                                        color=discord.Color.dark_gold()
                                    ),
                                    view=self
                                )

                        dm_embed = discord.Embed(
                            title="🌐 Cross-post your listing?",
                            description=(
                                f"Your listing **{thread.name}** was just posted in **{thread.guild.name}**!\n\n"
                                "Would you like to cross-post it to other Adrian servers so more buyers can see it?\n\n"
                                "✅ More exposure across multiple servers\n"
                                "💬 Interested buyers will contact you via DM\n"
                                "🆓 Completely free"
                            ),
                            color=discord.Color.dark_gold()
                        )
                        await seller.send(embed=dm_embed, view=CrossPostOfferView())
                        logger.info(f"[CrossPost] DM sent to seller {seller_id} about cross-posting")
                    except discord.Forbidden:
                        logger.warning(f"[CrossPost] Could not DM seller {seller_id} — DMs disabled")
                    except Exception as e:
                        logger.error(f"[CrossPost] DM error: {e}")

    except discord.Forbidden as e:
        logger.warning(f"[Estate] Forbidden — starter message not ready yet: {e}")
        # Try one more time after longer wait
        try:
            await asyncio.sleep(15)
            view = SellerProfileView(str(thread.owner_id))
            await thread.send(view=view)
            logger.info(f"[Estate] Buttons posted on retry in {thread.name}")

            # Still trigger cross-posting even on retry
            try:
                config = await db_get_server_config(str(thread.guild.id))
                cp_val = config.get("accept_cross_posts") or get_config_value(config, "accept_cross_posts") if config else None
                if str(cp_val) == "1":
                    seller = await client.fetch_user(thread.owner_id)
                    if seller:
                        applied_tag_names = [t.name.lower() for t in (thread.applied_tags or [])]
                        if "cross-posted" in applied_tag_names:
                            logger.info(f"[CrossPost] Auto-mirroring on retry: {thread.name}")
                            asyncio.create_task(cross_post_listing(thread, seller, None))
                        else:
                            dm_embed = discord.Embed(
                                title="🌐 Cross-post your listing?",
                                description=(
                                    f"Your listing **{thread.name}** was just posted in **{thread.guild.name}**!\n\n"
                                    "Would you like to cross-post it to other Adrian servers so more buyers can see it?\n\n"
                                    "✅ More exposure across multiple servers\n"
                                    "💬 Interested buyers will contact you via DM\n"
                                    "🆓 Completely free"
                                ),
                                color=discord.Color.dark_gold()
                            )

                            class CrossPostOfferViewRetry(discord.ui.View):
                                def __init__(self):
                                    super().__init__(timeout=3600)

                                @discord.ui.button(label="🌐 Yes — Cross-post my listing", style=discord.ButtonStyle.success)
                                async def yes_crosspost(self2, interaction: discord.Interaction, button: discord.ui.Button):
                                    for child in self2.children:
                                        child.disabled = True
                                    await interaction.response.edit_message(
                                        embed=discord.Embed(title="🌐 Cross-posting...", color=discord.Color.dark_gold()),
                                        view=self2
                                    )
                                    count = await cross_post_listing(thread, seller, None)
                                    await interaction.edit_original_response(
                                        embed=discord.Embed(
                                            title="✅ Listing Cross-Posted!",
                                            description=f"Mirrored to **{count}** other Adrian server(s)!",
                                            color=discord.Color.green()
                                        )
                                    )

                                @discord.ui.button(label="❌ No thanks", style=discord.ButtonStyle.secondary)
                                async def no_crosspost(self2, interaction: discord.Interaction, button: discord.ui.Button):
                                    for child in self2.children:
                                        child.disabled = True
                                    await interaction.response.edit_message(
                                        embed=discord.Embed(description="No problem! Your listing stays local.", color=discord.Color.dark_gold()),
                                        view=self2
                                    )

                            await seller.send(embed=dm_embed, view=CrossPostOfferViewRetry())
                            logger.info(f"[CrossPost] DM sent to seller on retry for {thread.name}")
            except Exception as cp_err:
                logger.error(f"[CrossPost] Retry cross-post error: {cp_err}")

        except Exception as retry_err:
            logger.error(f"[Estate] Retry also failed: {retry_err}")
    except Exception as e:
        logger.error(f"[Estate] on_thread_create error: {e}\n{traceback.format_exc()}")

@client.event
async def on_thread_update(before, after):
    """Detect when the Sold tag is applied to an estate listing."""
    try:
        # Only watch the estate channel
        # Check if this thread belongs to any server's estate channel
        config = await db_get_server_config(str(after.guild.id))
        estate_channel_id = get_config_value(config, "estate_channel_id") if config else None
        if not estate_channel_id:
            estate_channel_id = ESTATE_CHANNEL_ID
        sold_tag_id = get_config_value(config, "estate_sold_tag_id") if config else None
        if not sold_tag_id:
            sold_tag_id = ESTATE_SOLD_TAG_ID

        # Check all servers if this server's config is missing
        if after.parent_id != estate_channel_id:
            all_servers = await db_get_all_servers()
            matched_server = next(
                (s for s in all_servers if get_config_value(s, "estate_channel_id") == after.parent_id),
                None
            )
            if matched_server:
                estate_channel_id = after.parent_id
                sold_tag_id = get_config_value(matched_server, "estate_sold_tag_id") or ESTATE_SOLD_TAG_ID
            elif after.parent_id != ESTATE_CHANNEL_ID:
                return

        before_tag_ids = {t.id for t in before.applied_tags} if before.applied_tags else set()
        after_tag_ids = {t.id for t in after.applied_tags} if after.applied_tags else set()

        # Convert sold_tag_id to int for comparison
        sold_tag_id_int = int(sold_tag_id) if sold_tag_id else ESTATE_SOLD_TAG_ID
        logger.info(f"[Estate] Thread update — tags before={before_tag_ids} after={after_tag_ids} sold_tag={sold_tag_id_int}")

        # Check if Sold tag was just added
        logger.debug(f"[Estate] on_thread_update: before_tags={before_tag_ids} after_tags={after_tag_ids} sold_tag={sold_tag_id_int}")
        if sold_tag_id_int in after_tag_ids and sold_tag_id_int not in before_tag_ids:
            logger.info(f"[Estate] Sold tag detected on thread: {after.name} ({after.id})")

            # Get the thread owner (seller) from the starter message
            try:
                starter = await after.fetch_message(after.id)
                seller_id = starter.author.id
            except Exception:
                # Fallback — use thread owner
                seller_id = after.owner_id

            # Create transaction record
            logger.info(f"[Estate] Creating transaction record for thread {after.id} seller {seller_id}")
            await db_create_transaction(str(after.id), after.name, str(seller_id))

            # Mark all cross-post mirrors as sold
            try:
                mirrors = await db_mark_mirror_sold(str(after.id))
                for mirror in mirrors:
                    try:
                        mirror_channel = client.get_channel(int(mirror["mirror_channel_id"]))
                        if mirror_channel and mirror["mirror_thread_id"]:
                            mirror_thread = mirror_channel.guild.get_thread(int(mirror["mirror_thread_id"]))
                            if mirror_thread:
                                # Apply sold tag if available
                                mirror_config = await db_get_server_config(str(mirror_channel.guild.id))
                                mirror_sold_tag_id = get_config_value(mirror_config, "estate_sold_tag_id") if mirror_config else None
                                if mirror_sold_tag_id:
                                    sold_tag = discord.utils.get(mirror_thread.parent.available_tags, id=int(mirror_sold_tag_id))
                                    if sold_tag:
                                        current_tags = list(mirror_thread.applied_tags or [])
                                        if sold_tag not in current_tags:
                                            current_tags.append(sold_tag)
                                            await mirror_thread.edit(applied_tags=current_tags[:5])
                                await mirror_thread.send(
                                    embed=discord.Embed(
                                        title="🔴 This item has been sold!",
                                        description=f"The original listing in **{after.guild.name}** has been marked as sold.",
                                        color=discord.Color.red()
                                    )
                                )
                                logger.info(f"[CrossPost] Mirror marked as sold in {mirror_channel.guild.name}")
                    except Exception as me:
                        logger.debug(f"[CrossPost] Could not update mirror: {me}")
            except Exception as e:
                logger.error(f"[CrossPost] Error marking mirrors sold: {e}")

            # Post sold notification in the thread
            embed = discord.Embed(
                title="🔴 Item Sold!",
                description="This listing has been marked as sold. Thank you for using the Estand Marketplace! 🎉",
                color=discord.Color.red(),
                timestamp=datetime.now(timezone.utc)
            )
            embed.set_footer(text="Adrian — Estand Marketplace")
            await after.send(embed=embed)
            logger.info(f"[Estate] Sold notification posted in thread {after.name}")

            # DM the seller with a post-sale message tool
            try:
                seller_user = await client.fetch_user(int(seller_id))
                if seller_user:
                    default_message = (
                        f"Hi! Thanks for your purchase of **{after.name}**. "
                        f"I\'ll be in touch shortly to arrange payment and shipping details. "
                        f"Please feel free to message me here if you have any questions!"
                    )

                    class PostSaleMessageView(discord.ui.View):
                        def __init__(self):
                            super().__init__(timeout=86400)  # 24 hours

                        @discord.ui.button(label="✉️ Contact Buyer", style=discord.ButtonStyle.success)
                        async def send_message(self2, interaction2: discord.Interaction, button: discord.ui.Button):
                            class PostSaleModal(discord.ui.Modal, title="Contact Your Buyer"):
                                buyer_username = discord.ui.TextInput(
                                    label="Buyer\'s Discord username",
                                    placeholder="e.g. username or username#1234",
                                    max_length=100
                                )
                                message_text = discord.ui.TextInput(
                                    label="Your message",
                                    style=discord.TextStyle.paragraph,
                                    default=default_message,
                                    max_length=1000
                                )
                                async def on_submit(self3, interaction3: discord.Interaction):
                                    try:
                                        await interaction3.response.defer(ephemeral=True)
                                        # Try to find buyer by username in the guild
                                        username_input = self3.buyer_username.value.strip()
                                        buyer_user = None

                                        if interaction3.guild:
                                            # Search guild members by name
                                            for member in interaction3.guild.members:
                                                if (member.name.lower() == username_input.lower() or
                                                    member.display_name.lower() == username_input.lower() or
                                                    str(member).lower() == username_input.lower()):
                                                    buyer_user = member
                                                    break

                                        if not buyer_user:
                                            await interaction3.followup.send(
                                                f"⚠️ Could not find **{username_input}** on this server. Make sure you typed their exact Discord username.",
                                                ephemeral=True
                                            )
                                            return

                                        # Save buyer to transaction
                                        await db_set_transaction_buyer(str(after.id), str(buyer_user.id))

                                        buyer_embed = discord.Embed(
                                            title="📦 Message from your seller",
                                            description=self3.message_text.value,
                                            color=discord.Color.dark_gold(),
                                            timestamp=datetime.now(timezone.utc)
                                        )
                                        buyer_embed.add_field(name="Listing", value=after.name, inline=True)
                                        buyer_embed.add_field(name="Seller", value=seller_user.display_name, inline=True)
                                        buyer_embed.set_footer(text="Adrian — Estand Marketplace")
                                        await buyer_user.send(embed=buyer_embed)

                                        await interaction3.followup.send(
                                            f"✅ Message sent to **{buyer_user.display_name}**! They\'ll also be prompted to rate you as a seller.",
                                            ephemeral=True
                                        )

                                        # Now prompt buyer to rate the seller
                                        try:
                                            rating_embed = discord.Embed(
                                                title="⭐ Rate Your Seller",
                                                description=f"How was your experience buying from **{seller_user.display_name}**?\n\nClick a star rating below:",
                                                color=discord.Color.dark_gold(),
                                                timestamp=datetime.now(timezone.utc)
                                            )
                                            rating_embed.set_footer(text="Adrian — Estand Marketplace")
                                            await buyer_user.send(embed=rating_embed, view=EstateRatingView(str(after.id), str(buyer_user.id), str(seller_id)))
                                        except Exception:
                                            pass

                                        # Disable button after sending
                                        for child in self2.children:
                                            child.disabled = True
                                        await interaction2.message.edit(view=self2)

                                        logger.info(f"[Estate] Post-sale message sent from seller {seller_id} to buyer {buyer_user.id}")

                                    except discord.Forbidden:
                                        await interaction3.followup.send(
                                            "⚠️ Could not DM the buyer — they may have DMs disabled.",
                                            ephemeral=True
                                        )
                                    except Exception as e:
                                        logger.error(f"[Estate] Post-sale message error: {e}")
                                        await interaction3.followup.send("⚠️ Something went wrong.", ephemeral=True)

                            await interaction2.response.send_modal(PostSaleModal())

                        @discord.ui.button(label="⏭️ Skip", style=discord.ButtonStyle.secondary)
                        async def skip(self2, interaction2: discord.Interaction, button: discord.ui.Button):
                            for child in self2.children:
                                child.disabled = True
                            await interaction2.response.edit_message(
                                embed=discord.Embed(
                                    description="No problem — you can always message the buyer directly once they identify themselves.",
                                    color=discord.Color.dark_gold()
                                ),
                                view=self2
                            )

                    seller_embed = discord.Embed(
                        title="🎉 Your item sold!",
                        description=(
                            f"Congratulations on selling **{after.name}**!\n\n"
                            "Click **Contact Buyer** to enter the buyer\'s Discord username and send them a message. "
                            "I\'ve pre-written one for you that you can customize.\n\n"
                            "The buyer will also be prompted to rate you as a seller once you contact them."
                        ),
                        color=discord.Color.green(),
                        timestamp=datetime.now(timezone.utc)
                    )
                    seller_embed.add_field(name="Listing", value=after.name, inline=True)
                    seller_embed.add_field(name="Server", value=after.guild.name, inline=True)
                    seller_embed.set_footer(text="Adrian — Estand Marketplace")
                    await seller_user.send(embed=seller_embed, view=PostSaleMessageView())
                    logger.info(f"[Estate] Post-sale DM sent to seller {seller_id}")
            except discord.Forbidden:
                logger.warning(f"[Estate] Could not DM seller {seller_id} — DMs disabled")
            except Exception as e:
                logger.error(f"[Estate] Post-sale seller DM error: {e}")

    except Exception as e:
        logger.error(f"[Estate] on_thread_update error: {e}\n{traceback.format_exc()}")


@client.event
async def on_thread_delete(thread):
    """When a listing thread is deleted, DM the seller asking if it was sold."""
    try:
        if not isinstance(thread.parent, discord.ForumChannel):
            return

        config = await db_get_server_config(str(thread.guild.id))
        estate_channel_id = get_config_value(config, "estate_channel_id") if config else None
        if not estate_channel_id:
            estate_channel_id = ESTATE_CHANNEL_ID

        if thread.parent_id != estate_channel_id:
            all_servers = await db_get_all_servers()
            matched = any(get_config_value(s, "estate_channel_id") == thread.parent_id for s in all_servers)
            if not matched and thread.parent_id != ESTATE_CHANNEL_ID:
                return

        seller_id = thread.owner_id
        logger.info(f"[Estate] Thread deleted: {thread.name} by {seller_id}")

        try:
            seller = await client.fetch_user(seller_id)
            if not seller:
                return

            embed = discord.Embed(
                title="👋 Hey! I noticed your listing was removed.",
                description=(
                    f"Your listing **{thread.name}** is no longer available.\n\n"
                    "**Did this item sell on the server?**\n\n"
                    "If so, please take 30 seconds to rate your buyer. Here\'s why it matters:\n\n"
                    "🎖️ **Ratings build rank** — both you and your buyer earn rank progress from completed, rated transactions\n"
                    "🛡️ **Ratings protect the community** — good ratings reward trustworthy buyers, bad ratings warn others\n"
                    "🌐 **Ratings follow members everywhere** — your buyer\'s reputation carries across every Adrian server\n"
                    "📈 **Ratings grow the community** — the more trusted transactions we track, the stronger this marketplace becomes\n\n"
                    "A community is only as strong as the trust between its members. Your rating takes 10 seconds and makes a real difference."
                ),
                color=discord.Color.dark_gold(),
                timestamp=datetime.now(timezone.utc)
            )
            embed.set_footer(text="Adrian — Estate Marketplace")

            class DeletedListingView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=172800)  # 48 hours

                @discord.ui.button(label="⭐ Yes — Rate my Buyer", style=discord.ButtonStyle.success)
                async def rate_buyer(self, interaction: discord.Interaction, button: discord.ui.Button):
                    modal = discord.ui.Modal(title="Who was your buyer?")
                    buyer_input = discord.ui.TextInput(
                        label="Buyer Discord username or user ID",
                        placeholder="e.g. Murphy#1234 or 161988117862023169",
                        required=True
                    )
                    modal.add_item(buyer_input)

                    async def on_submit(modal_interaction: discord.Interaction):
                        buyer_name = buyer_input.value.strip()
                        buyer = None
                        try:
                            buyer = await client.fetch_user(int(buyer_name))
                        except Exception: pass
                        if buyer:
                            try:
                                buyer_embed = discord.Embed(
                                    title="⭐ Rate Your Seller!",
                                    description=(
                                        f"**{seller.display_name}** just completed a sale with you and wanted to say thanks!\n\n"
                                        f"Item: **{thread.name}**\n\n"
                                        "**Please take a moment to rate your experience as a buyer.** Here\'s why it matters:\n\n"
                                        "🎖️ **Ratings build your rank** — every rated transaction moves you up the ranks from Private to Maréchal d\'Empire\n"
                                        "🛡️ **Ratings protect others** — your honest review helps the next buyer know what to expect\n"
                                        "🌐 **Your reputation travels with you** — your rating is visible on every Adrian server you visit\n"
                                        "📈 **Ratings grow the community** — a trusted marketplace attracts more serious collectors\n\n"
                                        "It takes 10 seconds and means a lot to the community. How was your experience?"
                                    ),
                                    color=discord.Color.dark_gold()
                                )
                                await buyer.send(embed=buyer_embed, view=EstateRatingView(str(thread.id), str(seller_id), str(buyer.id)))
                                await modal_interaction.response.send_message(f"✅ Rating request sent to {buyer.display_name}!", ephemeral=True)
                            except discord.Forbidden:
                                await modal_interaction.response.send_message(f"⚠️ Could not DM that user — they may have DMs disabled.", ephemeral=True)
                        else:
                            await modal_interaction.response.send_message("⚠️ Could not find that user. Please use their exact user ID.", ephemeral=True)

                    modal.on_submit = on_submit
                    await interaction.response.send_modal(modal)

                @discord.ui.button(label="❌ Item wasn't sold", style=discord.ButtonStyle.secondary)
                async def not_sold(self, interaction: discord.Interaction, button: discord.ui.Button):
                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            description="No problem! Let me know if you relist it. 👍",
                            color=discord.Color.dark_gold()
                        ),
                        view=None
                    )

            await seller.send(embed=embed, view=DeletedListingView())
            logger.info(f"[Estate] DM sent to seller {seller_id} about deleted listing")

        except discord.Forbidden:
            logger.warning(f"[Estate] Could not DM seller {seller_id} — DMs disabled")
        except Exception as e:
            logger.error(f"[Estate] Could not DM seller: {e}")

        # Clean up cross-post mirrors
        try:
            mirrors = await db_mark_mirror_sold(str(thread.id))
            for mirror in mirrors:
                try:
                    mirror_channel = client.get_channel(int(mirror["mirror_channel_id"]))
                    if mirror_channel and mirror["mirror_thread_id"]:
                        mirror_thread = mirror_channel.guild.get_thread(int(mirror["mirror_thread_id"]))
                        if mirror_thread:
                            await mirror_thread.send(
                                embed=discord.Embed(
                                    title="🔴 This listing has been removed",
                                    description=f"The original listing in **{thread.guild.name}** is no longer available.",
                                    color=discord.Color.red()
                                )
                            )
                            await mirror_thread.edit(archived=True, locked=True)
                            logger.info(f"[CrossPost] Mirror archived in {mirror_channel.guild.name} after deletion")
                except Exception as me:
                    logger.debug(f"[CrossPost] Could not clean up mirror: {me}")
        except Exception as e:
            logger.error(f"[CrossPost] Mirror cleanup error on delete: {e}")

    except Exception as e:
        logger.error(f"[Estate] on_thread_delete error: {e}\n{traceback.format_exc()}")

@client.event
async def on_ready():
    bot_state["startup_time"] = datetime.now(timezone.utc)
    bot_state["health_status"] = "ready"
    bot_state["startup_time"] = datetime.now(timezone.utc)
    logger.info(f"[Startup] ============================")
    logger.info(f"[Startup] Adrian Bot Starting Up")
    logger.info(f"[Startup] Logged in as {client.user}")
    logger.info(f"[Startup] Discord.py version: {discord.__version__}")
    logger.info(f"[Startup] Guild count: {len(client.guilds)}")
    for g in client.guilds:
        logger.info(f"[Startup] Connected to guild: {g.name} ({g.id})")
    logger.info(f"[Startup] ============================")
    logger.info(f"SCRIPT_DIR: {SCRIPT_DIR}")
    logos_path = os.path.join(SCRIPT_DIR, "logos")
    adrian_path = os.path.join(SCRIPT_DIR, "logos", "adrian")
    if os.path.exists(logos_path):
        logger.info(f"Adrian images: {os.listdir(adrian_path) if os.path.exists(adrian_path) else 'MISSING'}")
        logger.info(f"Dealer logos: {os.listdir(logos_path)}")
    else:
        logger.warning(f"Logos folder NOT found at {logos_path}!")
    # Re-register persistent views so buttons work after bot restarts
    client.add_view(SellerProfileView("placeholder"))
    client.add_view(WatchItemView("placeholder", "placeholder", ""))
    client.add_view(FollowDealerView("placeholder"))
    client.add_view(MilitariaAlertAdView())
    client.add_view(SellerProfileView("placeholder"))
    client.add_view(EstateRatingView("placeholder", "placeholder", "placeholder"))
    client.add_view(WelcomeView())
    logger.info("Persistent views registered.")

    # Post welcome image to all #adrian channels on startup
    try:
        welcome_file = os.path.join(SCRIPT_DIR, "logos", "adrian", "Adrian_welcome.png")
        if not os.path.exists(welcome_file):
            logger.warning("[Startup] Adrian_welcome.png not found — skipping welcome post")
        else:
            channels_to_refresh = {}

            # Find #adrian channel in every connected guild
            for guild in client.guilds:
                # Try DB first
                try:
                    config = await db_get_server_config(str(guild.id))
                    channel_id_str = get_config_value(config, "channel_id") if config else None
                    if channel_id_str:
                        ch = guild.get_channel(int(channel_id_str))
                        if ch:
                            channels_to_refresh[ch.id] = (ch, str(guild.id))
                            continue
                except Exception:
                    pass
                # Fall back to searching by name
                ch = discord.utils.get(guild.text_channels, name="adrian")
                if ch:
                    channels_to_refresh[ch.id] = (ch, str(guild.id))
                    logger.info(f"[Startup] Found #adrian by name in {guild.name}")

            logger.info(f"[Startup] Refreshing welcome in {len(channels_to_refresh)} server(s)")

            for ch_id, (channel, guild_id) in channels_to_refresh.items():
                try:
                    # Clear old messages
                    try:
                        deleted = await channel.purge(limit=100, reason="Adrian startup cleanup")
                        logger.info(f"[Startup] Cleared {len(deleted)} messages from #{channel.name} in {channel.guild.name}")
                    except discord.Forbidden:
                        logger.warning(f"[Startup] No permission to purge #{channel.name} in {channel.guild.name}")
                    except Exception as pe:
                        logger.warning(f"[Startup] Purge failed: {pe}")

                    # Post fresh welcome
                    welcome_msg = await channel.send(
                        file=discord.File(welcome_file, filename="Adrian_welcome.png"),
                        view=WelcomeView()
                    )
                    await db_save_server_config(guild_id, welcome_message_id=str(welcome_msg.id), channel_id=str(channel.id))
                    logger.info(f"[Startup] Welcome posted to #{channel.name} in {channel.guild.name}")
                    await asyncio.sleep(0.5)
                except Exception as se:
                    logger.warning(f"[Startup] Could not refresh #{channel.name}: {se}")

    except Exception as e:
        logger.error(f"[Startup] Welcome post error: {e}\n{traceback.format_exc()}")

        # Upload question images — use DB cache to avoid re-uploading every restart
    try:
        img_host_channel = client.get_channel(IMAGE_HOST_CHANNEL_ID)
        if img_host_channel:
            # Load cached URLs from DB
            cached_urls = {}
            try:
                async with client.db.acquire() as conn:
                    rows = await conn.fetch("SELECT key, url FROM image_url_cache")
                    cached_urls = {r["key"]: r["url"] for r in rows}
                    logger.info(f"[Startup] Loaded {len(cached_urls)} cached image URLs")
            except Exception:
                pass

            images = [("adrian/adrain_1st_question.png", "question1_img_url"), ("adrian/adrain_2nd_question.png", "question2_img_url"), ("adrian/adrain_3rd_question.png", "question3_img_url"), ("adrian/adrain_4th_question.png", "question4_img_url"), ("adrian/adrain_5th_question.png", "question5_img_url"), ("adrian/thank_you_please_buy.png", "thankyou_img_url"), ("adrian/adrain_check_before_buy.png", "check_before_buy_img_url"), ("adrian/setup_1.png", "setup_img_url"), ("adrian/step_1_thumbnails.png", "setup_q1_img_url"), ("adrian/setup_2.png", "setup_q2_img_url"), ("adrian/setup_end.png", "setup_end_img_url"), ("adrian/adrain_stop.png", "setup_stop_img_url"), ("adrian/adrain_estand.png", "setup_estand_img_url"), ("adrian/adrain_cross_platform.png", "setup_crosspost_img_url"), ("adrian/adrain_please.png", "setup_please_img_url"), ("adrian/404.png", "error_404_img_url")]
            uploaded = 0
            for q_file, key in images:
                path = os.path.join(SCRIPT_DIR, "logos", q_file)
                if os.path.exists(path):
                    if key in cached_urls:
                        bot_state[key] = cached_urls[key]
                        logger.debug(f"[Startup] {key} loaded from cache")
                        continue
                    try:
                        msg = await img_host_channel.send(file=discord.File(path, filename=q_file.replace("/", "_")))
                        url = msg.attachments[0].url
                        bot_state[key] = url
                        try:
                            async with client.db.acquire() as conn:
                                await conn.execute(
                                    "INSERT INTO image_url_cache (key, url) VALUES ($1,$2) ON CONFLICT (key) DO UPDATE SET url=$2",
                                    key, url
                                )
                        except Exception as _e:
                            logger.debug(f"[Startup] Could not cache URL: {_e}")
                        uploaded += 1
                        logger.info(f"[Startup] {q_file} uploaded. URL: {url}")
                    except Exception as e:
                        logger.warning(f"[Startup] Failed to upload {q_file}: {e}")
                else:
                    logger.warning(f"[Startup] {q_file} not found in logos folder.")
            logger.info(f"[Startup] Images: {uploaded} uploaded, {len(images)-uploaded} from cache")
        else:
            logger.warning("[Startup] Could not find image host channel.")
    except Exception as e:
        logger.error(f"[Startup] Failed to upload question images: {e}")

async def send_griffin_combined():
    """Sends a combined Griffin Militaria alert after 5 minute buffer."""
    await asyncio.sleep(300)  # Wait 5 minutes to collect all changes
    if not bot_state["griffin_buffer"]:
        return
    pages = bot_state["griffin_buffer"].copy()
    bot_state["griffin_buffer"] = []
    bot_state["griffin_timer"] = None

    channels = await get_all_server_channels("updates_channel_id")
    na_channels = await get_all_server_channels("na_updates_channel_id")
    all_channels = list({c.id: c for c in channels + na_channels}.values())
    if not all_channels:
        return

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
    embed.set_footer(text="Adrian — Dealer Update")

    file = None
    if os.path.exists(logo_file):
        file = discord.File(logo_file, filename="logo.png")
        embed.set_thumbnail(url="attachment://logo.png")

    try:
        for channel in all_channels:
            if file:
                await channel.send(file=discord.File(logo_file, filename="logo.png"), embed=embed, view=FollowDealerView("Griffin Militaria"), allowed_mentions=discord.AllowedMentions.none())
            else:
                await channel.send(embed=embed, view=FollowDealerView("Griffin Militaria"), allowed_mentions=discord.AllowedMentions.none())
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
                    dm_embed.set_footer(text="You are following Griffin Militaria — Adrian")
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


async def handle_guide(request):
    guide_path = os.path.join(SCRIPT_DIR, "guide.html")
    if os.path.exists(guide_path):
        with open(guide_path, "r") as f:
            return web.Response(text=f.read(), content_type="text/html")
    return web.Response(text="Guide not found", status=404)

async def handle_404(request):
    """404 page for web server."""
    img_path = os.path.join(SCRIPT_DIR, "logos", "adrian", "404.png")
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            return web.Response(body=f.read(), content_type="image/png", status=404)
    return web.Response(text="404 Not Found", status=404)

async def handle_health(request):
    """Health check endpoint for Railway and monitoring."""
    uptime = ""
    if bot_state.get("startup_time"):
        seconds = int((datetime.now(timezone.utc) - bot_state["startup_time"]).total_seconds())
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        uptime = f"{hours}h {minutes}m"
    health = {
        "status": bot_state.get("health_status", "unknown"),
        "uptime": uptime,
        "guilds": len(client.guilds),
        "paused": bot_state["paused"],
        "last_check": bot_state["last_check"].isoformat() if bot_state["last_check"] else None,
        "last_email": bot_state["last_email_check"].isoformat() if bot_state["last_email_check"] else None,
        "waf_count": bot_state["waf_notification_count"],
    }
    import json as json_module
    return web.Response(
        text=json_module.dumps(health, indent=2),
        content_type="application/json",
        status=200
    )

async def start_web_server():
    await client.wait_until_ready()
    app = web.Application()
    app.router.add_get("/", handle_guide)
    app.router.add_get("/guide", handle_guide)
    app.router.add_get("/health", handle_health)
    app.router.add_route("*", "/{path_info:.*}", handle_404)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    logger.info("Webhook server running on port 8080!")

async def daily_cleanup():
    await client.wait_until_ready()
    while not client.is_closed():
        await asyncio.sleep(3600)  # Every hour
        try:
            # Clean DB alerts
            await db_cleanup_old_alerts()

            # Clean command cooldowns
            cleanup_cooldowns()

            # Clean dealer_cooldowns — remove entries older than 2 hours
            now = datetime.now(timezone.utc)
            expired_dealers = [
                k for k, v in list(bot_state["dealer_cooldowns"].items())
                if (now - v).total_seconds() > 7200
            ]
            for k in expired_dealers:
                del bot_state["dealer_cooldowns"][k]
            if expired_dealers:
                logger.debug(f"[Cleanup] Cleared {len(expired_dealers)} dealer cooldown entries")

            # Clear any stuck pending_pings older than 1 hour
            stuck = [uid for uid, pings in list(bot_state["pending_pings"].items()) if not pings]
            for uid in stuck:
                del bot_state["pending_pings"][uid]

            # Clear griffin buffer if it's been sitting too long (>2 hours)
            if bot_state.get("griffin_timer"):
                buf_age = (now - bot_state["griffin_timer"]).total_seconds() if isinstance(bot_state.get("griffin_timer"), datetime) else 0
                if buf_age > 7200:
                    bot_state["griffin_buffer"] = []
                    bot_state["griffin_timer"] = None
                    logger.warning("[Cleanup] Cleared stale Griffin buffer")

            # Log memory usage
            try:
                mem_mb = psutil.Process().memory_info().rss / 1024 / 1024
                logger.info(f"[Cleanup] Hourly cleanup complete | Mem: {mem_mb:.0f}MB | "
                           f"Pending pings: {len(bot_state['pending_pings'])} | "
                           f"Dealer cooldowns: {len(bot_state['dealer_cooldowns'])}")
            except Exception:
                logger.info("[Cleanup] Hourly cleanup complete")

        except Exception as e:
            logger.error(f"[Cleanup] Error: {e}")

        # Run full cleanup once per day at 3am UTC
        if datetime.now(timezone.utc).hour == 3:
            try:
                await db_cleanup_watchlist()
                await db_cleanup_seen_items()
                # Clean seen_emails table — keep only last 7 days
                async with client.db.acquire() as conn:
                    deleted = await conn.execute(
                        "DELETE FROM seen_emails WHERE seen_at < $1",
                        int((datetime.now(timezone.utc).timestamp()) - 604800)
                    )
                logger.info(f"[Cleanup] Daily cleanup complete")
            except Exception as e:
                logger.error(f"[Cleanup] Daily cleanup error: {e}")

async def main():
    loop = asyncio.get_event_loop()

    # Track all background tasks for clean shutdown
    tasks = []

    async def shutdown(signal_name=None):
        if signal_name:
            logger.info(f"[Shutdown] Received {signal_name} — shutting down gracefully...")
        else:
            logger.info("[Shutdown] Shutting down gracefully...")

        # Cancel all background tasks
        for task in tasks:
            if not task.done():
                task.cancel()
                try:
                    await asyncio.wait_for(task, timeout=3.0)
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    pass

        # Close Discord connection
        if not client.is_closed():
            await client.close()
            logger.info("[Shutdown] Discord connection closed.")

        # Close DB pool
        if client.db:
            await client.db.close()
            logger.info("[Shutdown] Database pool closed.")

        logger.info("[Shutdown] Clean shutdown complete.")

    try:
        async with client:
            tasks.append(asyncio.create_task(check_all_dealers()))
            tasks.append(asyncio.create_task(check_playwright_dealers()))
            logger.info(f"[Playwright] Scraper task started for {len(PLAYWRIGHT_DEALERS)} dealers")
            tasks.append(asyncio.create_task(onboarding_reminder_task()))
            tasks.append(asyncio.create_task(health_log_task()))
            tasks.append(asyncio.create_task(check_email_dealers()))
            tasks.append(asyncio.create_task(start_web_server()))
            tasks.append(asyncio.create_task(daily_cleanup()))

            # Handle SIGTERM and SIGINT for Railway
            import signal as signal_module
            for sig in (signal_module.SIGTERM, signal_module.SIGINT):
                loop.add_signal_handler(
                    sig,
                    lambda s=sig: asyncio.create_task(shutdown(s.name))
                )

            await client.start(BOT_TOKEN)

    except asyncio.CancelledError:
        logger.info("[Shutdown] Main task cancelled.")
    except Exception as e:
        logger.error(f"[Main] Fatal error: {e}\n{traceback.format_exc()}")
    finally:
        await shutdown()

asyncio.run(main())
