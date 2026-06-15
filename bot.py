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
    {"name": "Dutch Militaria", "flag": "🇳🇱", "region": "EU", "match": ["dutchmilitaria.com", "dutch militaria"], "logo_file": "dutch_militaria.png", "url": "https://dutchmilitaria.com/", "eras": [2, 3], "countries": ['D']},
    {"name": "Militaria Sales", "flag": "🇺🇸", "region": "NA", "match": ["militariasales.com", "militaria sales"], "logo_file": "militaria_sales.png", "url": "https://www.militariasales.com/new-item/", "eras": [2, 3, 6], "countries": ['A', 'D', 'J', 'G']},
    {"name": "Military Collectibles", "flag": "🇺🇸", "region": "NA", "match": ["info@militarycollectibles.com", "militarycollectibles.com"], "logo_file": "military_collectibles.png", "url": "https://militarycollectibles.com/shop?s=n", "eras": [2, 3], "countries": ['D']},
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
                    msg_id TEXT PRIMARY KEY,
                    seen_at BIGINT DEFAULT 0
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
        try:
            role = guild.get_role(int(role_id))
            if role:
                return role
        except (ValueError, TypeError):
            pass
    if fallback_id:
        return guild.get_role(int(fallback_id))
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
                                                                    await seller_user.send(embed=back_embed)
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
        updates_channels = await get_all_server_channels("updates_channel_id", ADRIAN_UPDATES_CHANNEL_ID)

        for uid, alerts in pings.items():
            try:
                # Build batched message
                if len(alerts) == 1:
                    msg = f"🆕 **{alerts[0]['name']}** has new items!"
                else:
                    dealer_list = "\n".join([f"• {a['flag']} **{a['name']}**" for a in alerts])
                    msg = f"🆕 **{len(alerts)} dealers** have new items!\n{dealer_list}"

                for updates_channel in updates_channels:
                    member = updates_channel.guild.get_member(int(uid))
                    if member:
                        await updates_channel.send(
                            content=f"{member.mention}\n{msg}",
                            delete_after=3
                        )
                        break
            except Exception as e:
                logger.debug(f"[Alert] Batch ping failed for {uid}: {e}")
    finally:
        bot_state["ping_task_running"] = False

async def check_dealer(session, dealer, seen, channel):
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
        await send_alert(channel, name, url, logo_file)
    else:
        logger.debug(f"[{name}] No new items ({len(current_items)} items unchanged).")

def _fetch_gmail_sync():
    """Synchronous Gmail IMAP fetch — run in thread to avoid blocking event loop."""
    raw_emails = []
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", timeout=20)
        mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        mail.select("inbox")
        _, messages = mail.search(None, "UNSEEN")
        email_ids = messages[0].split()
        for eid in email_ids:
            _, msg_data = mail.fetch(eid, "(RFC822)")
            raw_emails.append(msg_data[0][1])
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
    channel = client.get_channel(CHANNEL_ID)
    if not channel:
        logger.warning(f"[DealerChecker] Could not find channel {CHANNEL_ID} — waiting 60s before retry...")
        await asyncio.sleep(60)
        return
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
                await check_dealer(session, dealer, seen, channel)
                await asyncio.sleep(2)
        save_seen(seen)
        logger.info(f"--- Done. Next check in {CHECK_INTERVAL//60} minutes. ---")
        await asyncio.sleep(CHECK_INTERVAL)

# ==================== WAF EMAIL PARSER ====================

BUMP_KEYWORDS = ["up", "bump", "still available", "still for sale", "ttt", "btt", "to the top", "glws", "price reduced", "price drop", "make offer", "reduced"]

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

    logger.debug(f"[USMF] Parsed: title='{item_title}' | category='{category}' | price='{price_str}' | url='{topic_url}'")

    return {
        "item_title": item_title,
        "category": category,
        "price_str": price_str,
        "forum_url": topic_url,
    }

async def send_usmf_alert(channel, parsed):
    """Send a USMF forum alert to the USMF channel."""
    if not channel:
        logger.error("[USMF] Channel not found!")
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
    usmf_updates_channels = await get_all_server_channels("updates_channel_id", ADRIAN_UPDATES_CHANNEL_ID)
    for usmf_updates_channel in usmf_updates_channels:
        try:
            if file and os.path.exists(logo_file):
                await usmf_updates_channel.send(file=discord.File(logo_file, filename="logo.png"), embed=embed)
            else:
                await usmf_updates_channel.send(embed=embed)
            logger.info(f"[USMF] Alert sent to {usmf_updates_channel.guild.name}: {parsed['item_title']}")
        except Exception as e:
            logger.error(f"[USMF] Failed to send to {usmf_updates_channel.guild.name}: {e}")

    # Log to private mod channel
    try:
        log_ch = client.get_channel(PRIVATE_LOG_CHANNEL_ID)
        if log_ch:
            await log_ch.send(embed=embed)
    except Exception as e:
        logger.error(f"[USMF] Failed to log: {e}")

    # Ping matched users
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
    description = f"**{parsed['item_title']}**\n"
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
    embed.set_footer(text="Adrian — Forum Alert | You may need to make a free forum account to see this listing")

    logo_file = os.path.join(SCRIPT_DIR, "logos", "waf.png")
    file = None
    if os.path.exists(logo_file):
        file = discord.File(logo_file, filename="logo.png")
        embed.set_thumbnail(url="attachment://logo.png")

    content_msg = f"<@&{parsed['role_id']}>" if role else None

    watch_view = WatchItemView(parsed["forum_url"], parsed["item_title"], price_str) if parsed["forum_url"] else None

    # Post to #adrian-updates
    waf_updates_channels = await get_all_server_channels("updates_channel_id", ADRIAN_UPDATES_CHANNEL_ID)
    for waf_updates_channel in waf_updates_channels:
        try:
            if file and os.path.exists(logo_file):
                await waf_updates_channel.send(content=content_msg, file=discord.File(logo_file, filename="logo.png"), embed=embed, view=watch_view)
            else:
                await waf_updates_channel.send(content=content_msg, embed=embed, view=watch_view)
            bot_state["alert_count"] += 1
            logger.info(f"[WAF] Alert sent to {waf_updates_channel.guild.name}: {parsed['item_title']}")
        except Exception as e:
            logger.error(f"[WAF] Failed to send to {waf_updates_channel.guild.name}: {e}")

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
    channel = client.get_channel(CHANNEL_ID)
    if not channel:
        logger.warning(f"[EmailChecker] Could not find channel {CHANNEL_ID} — waiting 60s before retry...")
        await asyncio.sleep(60)
        return
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
                    waf_channel = client.get_channel(WAF_CHANNEL_ID)
                    await send_waf_alert(waf_channel, parsed, guild)
                except Exception as e:
                    logger.error(f"[WAF] Error processing email '{subject}': {e}\n{traceback.format_exc()}")
            elif dealer.get("usmf", False):
                try:
                    parsed = parse_usmf_email(subject, body)
                    usmf_channel = client.get_channel(USMF_CHANNEL_ID)
                    await send_usmf_alert(usmf_channel, parsed)
                except Exception as e:
                    logger.error(f"[USMF] Error processing email '{subject}': {e}\n{traceback.format_exc()}")
            else:
                logo_file = os.path.join(SCRIPT_DIR, "logos", dealer["logo_file"])
                await send_alert(channel, dealer["name"], dealer["url"], logo_file)


        await asyncio.sleep(EMAIL_CHECK_INTERVAL)

async def send_promo():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    if not channel:
        return
    bot_state["last_promo"] = datetime.now(timezone.utc)  # Set at startup so /nextpromo works
    while not client.is_closed():
        await asyncio.sleep(48 * 3600)
        if bot_state["promo_paused"]:
            continue
        banner_file = os.path.join(SCRIPT_DIR, "logos", "Server_Banner.png")
        embed = discord.Embed(
            title="🎖️ Adrian Militaria Community",
            description="Looking for the best militaria collecting community on Discord?\n\n**Adrian** connects collectors across multiple servers with dealer alerts, an estate marketplace, and global reputation.\n\n📬 Dealer alerts from 100+ websites\n🏪 Estate marketplace with verified ratings\n\n[**Click here to join →**](https://discord.gg/yourserver)",
            color=discord.Color.dark_red(),
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_footer(text="Adrian — Dealer Update")
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
            logger.info("Promo message sent!")
        except Exception as e:
            logger.error(f"Failed to send promo: {e}")

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

                        # DM server owner
                        if guild and guild.owner:
                            await guild.owner.send(embed=report_embed, view=OwnerReportView())

                        # Post to mod log if configured
                        config = await db_get_server_config(str(guild.id)) if guild else None
                        mod_log_id = get_config_value(config, "mod_log_channel_id") if config else None
                        if mod_log_id:
                            mod_channel = guild.get_channel(int(mod_log_id)) if guild else None
                            if mod_channel:
                                await mod_channel.send(embed=report_embed)

                        await interaction2.response.send_message("✅ Your report has been sent to the server owner.", ephemeral=True)
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

    @discord.ui.button(label="Watch Item", emoji="🔔", style=discord.ButtonStyle.secondary, custom_id="watch_item")
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

    @discord.ui.button(label="Unwatch", emoji="🔕", style=discord.ButtonStyle.secondary, custom_id="unwatch_item")
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

    @discord.ui.button(label="Send to DM", emoji="📬", style=discord.ButtonStyle.secondary, custom_id="send_to_dm")
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

    @discord.ui.button(label="Follow Dealer", emoji="🔔", style=discord.ButtonStyle.secondary, custom_id="follow_dealer")
    async def follow(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        if await db_is_following(user_id, self.dealer_name):
            await interaction.response.send_message(f"⚠️ You are already following **{self.dealer_name}**!", ephemeral=True)
            return
        await db_follow_dealer(user_id, self.dealer_name)
        await interaction.response.send_message(f"🔔 You are now following **{self.dealer_name}**! You'll receive a DM whenever they have new items.", ephemeral=True)

    @discord.ui.button(label="Unfollow Dealer", emoji="🔕", style=discord.ButtonStyle.secondary, custom_id="unfollow_dealer")
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

async def show_question4(interaction: discord.Interaction, edit=True):
    """Show question 4 — community forums opt-in."""
    embeds = []
    if bot_state.get("question4_img_url"):
        img_embed = discord.Embed(color=discord.Color.dark_gold())
        img_embed.set_image(url=bot_state["question4_img_url"])
        embeds.append(img_embed)

    text_embed = discord.Embed(
        description="🟥 **WAF** — Wehrmacht Awards Forum only\n🟩 **USMF** — US Militaria Forum only\n✅ **Both** — WAF & USMF\n❌ **None** — Skip forum notifications",
        color=discord.Color.dark_gold()
    )
    text_embed.set_footer(text="Adrian — Discord's #1 Militaria Bot")
    embeds.append(text_embed)

    try:
        if interaction.response.is_done():
            await interaction.edit_original_response(embeds=embeds, view=ForumSelectView())
        else:
            await interaction.response.edit_message(embeds=embeds, view=ForumSelectView())
    except Exception as e:
        logger.error(f"[Q4] Error showing forum question: {e}")
        try:
            await interaction.followup.send(embeds=embeds, view=ForumSelectView(), ephemeral=True)
        except Exception: pass

class ForumSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def _save(self, interaction, choice):
        try:
            await interaction.response.defer(ephemeral=True)
            await db_set_user_forums(str(interaction.user.id), choice)
            await show_all_done(interaction, edit=True)
        except Exception as e:
            logger.error(f"[ForumSelect] Error: {e}\n{traceback.format_exc()}")
            try:
                await interaction.followup.send("⚠️ Something went wrong. Please try again.", ephemeral=True)
            except Exception: pass

    @discord.ui.button(emoji="🟥", style=discord.ButtonStyle.secondary, custom_id="forum_waf")
    async def forum_waf(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._save(interaction, "waf")

    @discord.ui.button(emoji="🟩", style=discord.ButtonStyle.secondary, custom_id="forum_usmf")
    async def forum_usmf(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._save(interaction, "usmf")

    @discord.ui.button(emoji="✅", style=discord.ButtonStyle.secondary, custom_id="forum_both")
    async def forum_both(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._save(interaction, "both")

    @discord.ui.button(emoji="❌", style=discord.ButtonStyle.secondary, custom_id="forum_none")
    async def forum_none(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._save(interaction, "none")

async def show_all_done(interaction: discord.Interaction, edit=True):
    """Show final screen after all questions answered."""
    # Assign Adrian Verified role — use server config ID first, fallback to hardcoded
    try:
        if interaction.guild:
            verified_role = await get_server_role(interaction.guild, "verified_role_id", ADRIAN_VERIFIED_ROLE_ID)
            if verified_role and verified_role not in interaction.user.roles:
                await interaction.user.add_roles(verified_role, reason="Completed /start onboarding")
                logger.info(f"[Adrian] Verified role assigned to {interaction.user} in {interaction.guild.name}")
    except Exception as e:
        logger.error(f"[Adrian] Could not assign verified role: {e}")

    embeds = []
    # Show adrain_5th image first, then the thank you image
    if bot_state.get("question5_img_url"):
        img_embed = discord.Embed(color=discord.Color.dark_gold())
        img_embed.set_image(url=bot_state["question5_img_url"])
        embeds.append(img_embed)
    if bot_state.get("thankyou_img_url"):
        ty_embed = discord.Embed(color=discord.Color.dark_gold())
        ty_embed.set_image(url=bot_state["thankyou_img_url"])
        embeds.append(ty_embed)

    # Always use edit_original_response to keep it in the ephemeral flow
    # Never edit the public welcome message in #adrian
    try:
        if interaction.response.is_done():
            await interaction.edit_original_response(embeds=embeds, view=FinalScreenView())
        else:
            await interaction.response.send_message(embeds=embeds, view=FinalScreenView(), ephemeral=True)
    except Exception as e:
        logger.error(f"[Final] Error showing final screen: {e}")

    # Notify owner channel of new profile
    try:
        notify_channel = client.get_channel(1515727882394144908)
        if notify_channel and interaction.guild:
            user = interaction.user
            region = await db_get_user_region(str(user.id))
            points, _ = await db_get_user_points(str(user.id))
            rank = get_rank(points, False)
            region_str = {"NA": "🇺🇸 North America", "EU": "🇪🇺 Europe", "both": "🌍 All"}.get(region, "Not set")
            notify_embed = discord.Embed(
                title="🆕 New Collector Profile",
                color=discord.Color.dark_gold(),
                timestamp=datetime.now(timezone.utc)
            )
            notify_embed.set_thumbnail(url=user.display_avatar.url if user.display_avatar else None)
            notify_embed.add_field(name="User", value=f"{user.mention} ({user.display_name})", inline=True)
            notify_embed.add_field(name="Server", value=interaction.guild.name, inline=True)
            notify_embed.add_field(name="Region", value=region_str, inline=True)
            notify_embed.add_field(name="Rank", value=rank, inline=True)
            notify_embed.set_footer(text="Adrian — New Member")
            await notify_channel.send(embed=notify_embed)
            logger.info(f"[Profile] New profile notification sent for {user} in {interaction.guild.name}")
    except Exception as e:
        logger.debug(f"[Profile] Could not send profile notification: {e}")

class FinalScreenView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="⭐ Rate the Bot", style=discord.ButtonStyle.primary, custom_id="final_rate")
    async def rate_bot(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "⭐ Thanks for rating! Use `/ratedealer` to rate any dealer, or share your thoughts about the bot with the mods.",
            ephemeral=True
        )

    @discord.ui.button(label="💬 Leave Feedback", style=discord.ButtonStyle.secondary, custom_id="final_feedback")
    async def leave_feedback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(FeedbackModal())

    @discord.ui.button(label="💗 Buy Premium", style=discord.ButtonStyle.danger, custom_id="final_premium")
    async def buy_premium(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "💗 **Buy Premium** — Coming soon! Stay tuned.",
            ephemeral=True
        )

class FeedbackModal(discord.ui.Modal, title="Leave Feedback for the Developer"):
    feedback = discord.ui.TextInput(
        label="Your Feedback",
        placeholder="Tell us what you think about Adrian...",
        style=discord.TextStyle.paragraph,
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            feedback_text = str(self.feedback).lower()
            server_name = interaction.guild.name if interaction.guild else "DM"
            server_id = interaction.guild.id if interaction.guild else "N/A"

            # Basic hate speech / slur filter
            banned_words = [
                "nigger", "nigga", "faggot", "chink", "spic", "kike", "raghead",
                "towelhead", "wetback", "tranny", "retard", "cunt"
            ]
            triggered = [w for w in banned_words if w in feedback_text]
            flagged = len(triggered) > 0

            # Always post to feedback channel with full user log
            feedback_channel = client.get_channel(BOT_FEEDBACK_CHANNEL_ID)
            if feedback_channel:
                color = discord.Color.red() if flagged else discord.Color.blurple()
                embed = discord.Embed(
                    title="⚠️ FLAGGED Feedback" if flagged else "💬 Bot Feedback",
                    description=f"||{str(self.feedback)[:1000]}||" if flagged else str(self.feedback)[:1000],
                    color=color,
                    timestamp=datetime.now(timezone.utc)
                )
                embed.add_field(name="User", value=f"{interaction.user.mention} ({interaction.user})", inline=True)
                embed.add_field(name="User ID", value=str(interaction.user.id), inline=True)
                embed.add_field(name="Server", value=f"{server_name} ({server_id})", inline=True)
                embed.add_field(name="Account Created", value=f"<t:{int(interaction.user.created_at.timestamp())}:R>", inline=True)
                if flagged:
                    embed.add_field(name="Triggered Words", value=", ".join(triggered), inline=False)
                    embed.set_footer(text="⚠️ Content hidden — click to reveal spoiler")
                else:
                    embed.set_footer(text="Adrian Feedback System")
                await feedback_channel.send(embed=embed)

            # If flagged — DM the user the Guerrilla Warfare warning
            if flagged:
                await interaction.response.send_message(
                    "⚠️ Your feedback has been logged and flagged for review.",
                    ephemeral=True
                )
                try:
                    img_path = os.path.join(SCRIPT_DIR, "logos", "adrian", "guerrilla_warfare.png")
                    audio_path = os.path.join(SCRIPT_DIR, "logos", "adrian", "guerrilla_warfare_call.mp3")
                    if os.path.exists(img_path):
                        await interaction.user.send(file=discord.File(img_path, filename="guerrilla_warfare.png"))
                    if os.path.exists(audio_path):
                        await interaction.user.send(file=discord.File(audio_path, filename="guerrilla_warfare_call.mp3"))
                    logger.info(f"[Feedback] Guerrilla Warfare warning sent to {interaction.user}")
                except discord.Forbidden:
                    logger.warning(f"[Feedback] Could not DM {interaction.user} — DMs closed")
                except Exception as dm_err:
                    logger.error(f"[Feedback] DM error: {dm_err}")
                # Assign the Guerrilla Warfare role
                try:
                    if interaction.guild:
                        gw_role = await get_server_role(interaction.guild, "guerrilla_role_id", GUERRILLA_WARFARE_ROLE_ID)
                        if gw_role:
                            await interaction.user.add_roles(gw_role, reason="Triggered feedback filter")
                            logger.info(f"[Feedback] Guerrilla Warfare role assigned to {interaction.user} in {interaction.guild.name}")
                except Exception as role_err:
                    logger.error(f"[Feedback] Could not assign role: {role_err}")
            else:
                await interaction.response.send_message("💬 Thanks for your feedback! The developer will review it.", ephemeral=True)

        except Exception as e:
            logger.error(f"[Feedback] Error: {e}\n{traceback.format_exc()}")
            try:
                await interaction.response.send_message("⚠️ Something went wrong. Please try again.", ephemeral=True)
            except Exception: pass

async def show_question3(interaction: discord.Interaction, edit=True):
    """Show question 3 — country selection."""
    existing_countries = await db_get_user_countries(str(interaction.user.id))
    country_display = " ".join([COUNTRY_FLAGS.get(c, c) for c in existing_countries]) if existing_countries else "Not set yet"

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
        "🇨🇳 Chinese / KMT\n"
        "🇩🇪 German\n"
        "🇷🇺 Soviet / Russian\n"
        "🇫🇷 French\n"
        "🇯🇵 Japanese\n"
        "🇮🇹 Italian\n"
        "🇦🇹 Austro-Hungarian\n"
        "🏳️ Other Axis\n"
        "🌍 Other Allied\n"
        "🌐 Multi-country / General\n"
        "**Select all that apply. Click Done when finished.**"
    )
    if existing_countries:
        description += f"\n\n**Current Selection:** {country_display}"

    text_embed = discord.Embed(description=description, color=discord.Color.dark_gold())
    text_embed.set_footer(text="Adrian — Discord's #1 Militaria Bot")
    embeds.append(text_embed)

    if edit:
        await interaction.response.edit_message(embeds=embeds, view=CountrySelectView(existing_countries or []))
    else:
        await interaction.response.send_message(embeds=embeds, view=CountrySelectView(existing_countries or []), ephemeral=True)

async def show_question2(interaction: discord.Interaction, edit=True):
    """Show question 2 — era selection."""
    existing_eras = await db_get_user_eras(str(interaction.user.id))
    era_display = ", ".join([f"{ERA_EMOJIS[e]} {ERA_NAMES[e]}" for e in existing_eras]) if existing_eras else "Not set yet"

    embeds = []
    if bot_state.get("question2_img_url"):
        img_embed = discord.Embed(color=discord.Color.dark_gold())
        img_embed.set_image(url=bot_state["question2_img_url"])
        embeds.append(img_embed)

    description = (
        "⚪ All Eras\n"
        "🟤 Pre-1914\n"
        "🟡 WWI (1914\u20131918)\n"
        "🔴 WWII (1939\u20131945)\n"
        "🔵 Korean War (1950\u20131953)\n"
        "🟢 Vietnam War (1955\u20131975)\n"
        "🟣 Cold War (1947\u20131991)\n"
        "🟠 GWOT / Modern (2001\u2013present)\n\n"
        "**Select all that apply. Click Done when finished.**"
    )
    if existing_eras:
        description += f"\n\n**Current Selection:** {era_display}"

    text_embed = discord.Embed(description=description, color=discord.Color.dark_gold())
    text_embed.set_footer(text="Adrian — Discord's #1 Militaria Bot")
    embeds.append(text_embed)

    if edit:
        await interaction.response.edit_message(embeds=embeds, view=EraSelectView(existing_eras or []))
    else:
        await interaction.response.send_message(embeds=embeds, view=EraSelectView(existing_eras or []), ephemeral=True)

class EraSelectView(discord.ui.View):
    def __init__(self, selected_eras=None):
        super().__init__(timeout=None)
        self.selected = set(selected_eras or [])

    @discord.ui.button(emoji="⚪", style=discord.ButtonStyle.secondary, custom_id="era_0")
    async def era_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle(interaction, 0)

    @discord.ui.button(emoji="🟤", style=discord.ButtonStyle.secondary, custom_id="era_1")
    async def era_pre14(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle(interaction, 1)

    @discord.ui.button(emoji="🟡", style=discord.ButtonStyle.secondary, custom_id="era_2")
    async def era_wwi(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle(interaction, 2)

    @discord.ui.button(emoji="🔴", style=discord.ButtonStyle.secondary, custom_id="era_3")
    async def era_wwii(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle(interaction, 3)

    @discord.ui.button(emoji="🔵", style=discord.ButtonStyle.secondary, custom_id="era_4")
    async def era_korea(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle(interaction, 4)

    @discord.ui.button(emoji="🟢", style=discord.ButtonStyle.secondary, custom_id="era_5")
    async def era_vietnam(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle(interaction, 5)

    @discord.ui.button(emoji="🟣", style=discord.ButtonStyle.secondary, custom_id="era_6")
    async def era_coldwar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle(interaction, 6)

    @discord.ui.button(emoji="🟠", style=discord.ButtonStyle.secondary, custom_id="era_7")
    async def era_gwot(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle(interaction, 7)

    @discord.ui.button(label="✅ Done", style=discord.ButtonStyle.success, custom_id="era_done")
    async def era_done(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.selected:
            await interaction.response.send_message("⚠️ Please select at least one era.", ephemeral=True)
            return
        await db_set_user_eras(str(interaction.user.id), list(self.selected))
        # Move to question 3
        await show_question3(interaction, edit=True)

    async def _toggle(self, interaction: discord.Interaction, era: int):
        try:
            if era in self.selected:
                self.selected.discard(era)
            else:
                self.selected.add(era)
            selected_list = sorted(self.selected)
            era_display = " ".join([ERA_EMOJIS[e] for e in selected_list]) if selected_list else "None selected"

            embeds = []
            if bot_state.get("question2_img_url"):
                img_embed = discord.Embed(color=discord.Color.dark_gold())
                img_embed.set_image(url=bot_state["question2_img_url"])
                embeds.append(img_embed)

            description = (
                "⚪ All Eras\n"
                "🟤 Pre-1914\n"
                "🟡 WWI (1914–1918)\n"
                "🔴 WWII (1939–1945)\n"
                "🔵 Korean War (1950–1953)\n"
                "🟢 Vietnam War (1955–1975)\n"
                "🟣 Cold War (1947–1991)\n"
                "🟠 GWOT / Modern (2001–present)\n\n"
                f"**Selected:** {era_display}\n"
                "**Click Done when finished.**"
            )
            text_embed = discord.Embed(description=description, color=discord.Color.dark_gold())
            text_embed.set_footer(text="Adrian — Discord's #1 Militaria Bot")
            embeds.append(text_embed)

            await interaction.response.edit_message(embeds=embeds, view=EraSelectView(list(self.selected)))
        except Exception as e:
            logger.error(f"[EraSelect] Toggle error: {e}\n{traceback.format_exc()}")
            try:
                await interaction.response.send_message("⚠️ Something went wrong. Please try again.", ephemeral=True)
            except Exception: pass

# ==================== REGION SELECT VIEW ====================

async def _show_estand_rules(interaction, edit=False):
    """Show Estand rules agreement — called from both /start and skip path."""
    rules_embed = discord.Embed(
        title="📋 Estand Marketplace Rules",
        description=(
            "Before accessing the Estand, please read and agree to the **Estand Marketplace Rules**:\n\n"
            "🤝 **Honest listings** — Accurately describe items including condition, provenance and any known issues.\n\n"
            "🚫 **No prohibited items** — Illegal items, stolen goods, or items banned by Discord\'s ToS are strictly prohibited.\n\n"
            "💬 **Respectful communication** — Treat all buyers and sellers with respect. Harassment will not be tolerated.\n\n"
            "⭐ **Complete your transactions** — If you agree to a sale, follow through. Backing out repeatedly will affect your reputation.\n\n"
            "🛡️ **No scamming** — Fraud, fake items, or misrepresentation will result in a permanent ban from the Adrian network.\n\n"
            "📊 **Honest reviews** — Only leave reviews for transactions you actually completed. Fake reviews are prohibited.\n\n"
            "By clicking **I Agree**, you confirm you have read and will follow these rules."
        ),
        color=discord.Color.dark_gold()
    )
    rules_embed.set_footer(text="Adrian — Estand Marketplace Rules")

    class EstandRulesView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)

        @discord.ui.button(label="✅ I Agree", style=discord.ButtonStyle.success, custom_id="estand_rules_agree")
        async def agree(self2, interaction2: discord.Interaction, button: discord.ui.Button):
            await interaction2.response.defer(ephemeral=True)
            try:
                async with client.db.acquire() as conn:
                    await conn.execute(
                        "INSERT INTO user_preferences (user_id, estand_agreed, created_at) VALUES ($1, 1, $2) ON CONFLICT (user_id) DO UPDATE SET estand_agreed=1",
                        str(interaction2.user.id), int(datetime.now(timezone.utc).timestamp())
                    )
                # Grant Estand Verified role if available
                if interaction2.guild:
                    config = await db_get_server_config(str(interaction2.guild.id))
                    estand_role_id = get_config_value(config, "estand_verified_role_id") if config else None
                    if estand_role_id:
                        estand_role = interaction2.guild.get_role(int(estand_role_id)) if estand_role_id else None
                        if estand_role:
                            member = interaction2.guild.get_member(interaction2.user.id)
                            if member and estand_role not in member.roles:
                                await member.add_roles(estand_role, reason="Agreed to Estand rules")
                                logger.info(f"[Estand] Granted Estand Verified to {interaction2.user} in {interaction2.guild.name}")
            except Exception as e:
                logger.error(f"[Estand] Rules agree error: {e}")

            done_embed = discord.Embed(
                title="✅ Welcome to the Estand!",
                description=(
                    "You now have access to the **Estand Marketplace**!\n\n"
                    "🏪 Browse listings in the Estand channel\n"
                    "📦 Post your own items for sale\n"
                    "⭐ Build your buyer and seller reputation\n\n"
                    "If you\'d like to also receive **dealer alerts**, run `/start` and complete your collector profile."
                ),
                color=discord.Color.green()
            )
            done_embed.set_footer(text="Adrian — Estand Marketplace")
            await interaction2.edit_original_response(embed=done_embed, view=None)
            logger.info(f"[Estand] {interaction2.user} agreed to Estand rules")

        @discord.ui.button(label="❌ Decline", style=discord.ButtonStyle.danger, custom_id="estand_rules_decline")
        async def decline(self2, interaction2: discord.Interaction, button: discord.ui.Button):
            await interaction2.response.defer(ephemeral=True)
            await interaction2.edit_original_response(
                embed=discord.Embed(
                    title="No problem!",
                    description="You can run `/start` again whenever you\'re ready to join the Estand marketplace.",
                    color=discord.Color.red()
                ),
                view=None
            )

    # Always keep in ephemeral flow
    await interaction.edit_original_response(embed=rules_embed, view=EstandRulesView())


class RegionSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(emoji="🇺🇸", style=discord.ButtonStyle.secondary, custom_id="region_select_na")
    async def region_na(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await db_set_user_region(str(interaction.user.id), "NA")
            await show_question2(interaction, edit=True)
        except Exception as e:
            logger.error(f"[RegionSelect] NA error: {e}\n{traceback.format_exc()}")
            try:
                await interaction.response.send_message("⚠️ Something went wrong. Please try again.", ephemeral=True)
            except Exception: pass

    @discord.ui.button(emoji="🇪🇺", style=discord.ButtonStyle.secondary, custom_id="region_select_eu")
    async def region_eu(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await db_set_user_region(str(interaction.user.id), "EU")
            await show_question2(interaction, edit=True)
        except Exception as e:
            logger.error(f"[RegionSelect] EU error: {e}\n{traceback.format_exc()}")
            try:
                await interaction.response.send_message("⚠️ Something went wrong. Please try again.", ephemeral=True)
            except Exception: pass

    @discord.ui.button(emoji="🌍", style=discord.ButtonStyle.secondary, custom_id="region_select_both")
    async def region_both(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await db_set_user_region(str(interaction.user.id), "both")
            await show_question2(interaction, edit=True)
        except Exception as e:
            logger.error(f"[RegionSelect] Both error: {e}\n{traceback.format_exc()}")
            try:
                await interaction.response.send_message("⚠️ Something went wrong. Please try again.", ephemeral=True)
            except Exception: pass

    @discord.ui.button(label="⏭️ Skip — Just the Estand", style=discord.ButtonStyle.secondary, custom_id="region_select_skip")
    async def skip_to_estand(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            logger.info(f"[Start] {interaction.user} skipped alerts, going straight to Estand rules")
            await _show_estand_rules(interaction, edit=True)
        except Exception as e:
            logger.error(f"[RegionSelect] Skip error: {e}\n{traceback.format_exc()}")
            try:
                await interaction.response.send_message("⚠️ Something went wrong. Please try again.", ephemeral=True)
            except Exception: pass

# ==================== SLASH COMMANDS ====================

# ==================== SETUP FLOW VIEWS ====================

class SetupEstateConfirmView(discord.ui.View):
    """Confirmation when server owner says No to estate."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ Yes — Add the Estand", style=discord.ButtonStyle.success, custom_id="setup_estate_confirm_yes")
    async def confirm_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        forum_channels = [c for c in interaction.guild.channels if isinstance(c, discord.ForumChannel)]
        if not forum_channels:
            embed = discord.Embed(
                title="⚠️ Forum Channel Required",
                description=(
                    "The Estand marketplace only works with **Forum Channels** — not regular text channels.\n\n"
                    "**Here\'s how to create one:**\n"
                    "1. Go to your server settings\n"
                    "2. Click **Channels** → **New Channel**\n"
                    "3. Select **Forum** as the channel type\n"
                    "4. Name it something like `#estand` or `#marketplace`\n"
                    "5. Click the button below once it\'s created"
                ),
                color=discord.Color.orange()
            )
            await interaction.response.edit_message(embed=embed, view=SetupNoForumView())
            return
        forum_options = [
            discord.SelectOption(label=f"#{c.name}"[:100], value=str(c.id))
            for c in sorted(forum_channels, key=lambda x: x.position)
        ][:25]
        embed = discord.Embed(
            title="🏪 Estand Marketplace — Buy & Sell Militaria",
            description=(
                "Which **forum channel** should be your Estand marketplace?\n\n"
                "🚀 **Let me create one** — I\'ll set up the channel with the right tags automatically\n"
                "📋 **Pick an existing one** — select from the dropdown below"
            ),
            color=discord.Color.dark_gold()
        )
        if bot_state.get("setup_estand_img_url"):
            embed.set_thumbnail(url=bot_state["setup_estand_img_url"])
        view = _build_estate_forum_select(forum_options)
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label="❌ No, skip for now", style=discord.ButtonStyle.secondary, custom_id="setup_estate_confirm_no")
    async def confirm_no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await db_save_server_config(str(interaction.guild_id), setup_complete=0)
        await _show_permissions_step(interaction)


def _build_estate_forum_select(forum_options):
    """Build the forum channel select view for estate setup."""
    class EstateForumSelect(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)

        @discord.ui.button(label="🚀 Auto-create Estand channel for me", style=discord.ButtonStyle.success, row=0)
        async def auto_create(self, interaction2: discord.Interaction, button: discord.ui.Button):
            try:
                await interaction2.response.defer(ephemeral=True)
                guild = interaction2.guild
                estate_channel = discord.utils.get(guild.forums, name="estand")
                if not estate_channel:
                    estate_channel = await guild.create_forum(
                        name="estand",
                        topic="Buy and sell militaria with verified members. Use /start to create your profile.",
                        available_tags=ESTAND_STANDARD_TAGS[:20],
                        reason="Created by Adrian setup"
                    )
                    result = "✅ Created **#estand** with standard country, era, and status tags"
                else:
                    added = await add_standard_tags_to_forum(estate_channel)
                    if added:
                        result = f"✅ Found existing **#estand** — added {len(added)} missing tags"
                    else:
                        result = "✅ Found existing **#estand** — all standard tags already present"
                sold_tag = next((t for t in estate_channel.available_tags if t.name.lower() == "sold"), None)
                await db_save_server_config(
                    str(interaction2.guild_id),
                    estate_channel_id=str(estate_channel.id),
                    estate_sold_tag_id=str(sold_tag.id) if sold_tag else None,
                    estate_name="Estand"
                )
                embed = discord.Embed(
                    title="🏪 Estand Marketplace — Buy & Sell Militaria",
                    description=(
                        result + "\n\n"
                        "Do you want to **accept cross-posted listings** from other Adrian servers?\n\n"
                        "📈 **More listings** — your members see a wider selection\n"
                        "🤝 **Community growth** — builds connections between servers\n"
                        "🆓 **Completely free**"
                    ),
                    color=discord.Color.dark_gold()
                )
                if bot_state.get("setup_crosspost_img_url"):
                    embed.set_thumbnail(url=bot_state["setup_crosspost_img_url"])
                await interaction2.edit_original_response(embed=embed, view=SetupCrossPostView())
            except discord.Forbidden:
                await interaction2.edit_original_response(embed=discord.Embed(
                    title="⚠️ Missing Permissions",
                    description="I don\'t have permission to create channels.",
                    color=discord.Color.red()
                ))
            except Exception as e:
                logger.error(f"[Setup] Auto-create estand error: {e}\n{traceback.format_exc()}")

        @discord.ui.select(placeholder="Or pick an existing forum channel...", options=forum_options, row=1)
        async def select_forum(self, interaction2: discord.Interaction, select: discord.ui.Select):
            await interaction2.response.defer(ephemeral=True)
            estate_channel_id = int(select.values[0])
            estate_channel = interaction2.guild.get_channel(estate_channel_id)
            # Add any missing standard tags
            if hasattr(estate_channel, "available_tags"):
                try:
                    added = await add_standard_tags_to_forum(estate_channel)
                    tag_note = f" Added {len(added)} standard tags." if added else " Standard tags already present."
                except Exception as te:
                    tag_note = ""
                    logger.debug(f"[Setup] Could not add tags: {te}")
            else:
                tag_note = ""
            sold_tag = next((t for t in estate_channel.available_tags if t.name.lower() == "sold"), None) if hasattr(estate_channel, "available_tags") else None
            await db_save_server_config(
                str(interaction2.guild_id),
                estate_channel_id=str(estate_channel_id),
                estate_sold_tag_id=str(sold_tag.id) if sold_tag else None,
                estate_name=estate_channel.name
            )
            embed = discord.Embed(
                title="🏪 Estand Marketplace — Buy & Sell Militaria",
                description=(
                    f"✅ Estand channel set to {estate_channel.mention}{tag_note}\n\n"
                    "Do you want to **accept cross-posted listings** from other Adrian servers?\n\n"
                    "📈 **More listings** — your members see a wider selection\n"
                    "🤝 **Community growth** — builds connections between servers\n"
                    "🆓 **Completely free**"
                ),
                color=discord.Color.dark_gold()
            )
            if bot_state.get("setup_crosspost_img_url"):
                embed.set_thumbnail(url=bot_state["setup_crosspost_img_url"])
            await interaction2.response.edit_message(embed=embed, view=SetupCrossPostView())

    return EstateForumSelect()


class SetupStep3EstateView(discord.ui.View):
    """Step 3 — Estate marketplace pitch."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ Yes — Add the Estand", style=discord.ButtonStyle.success, custom_id="setup_s3_yes")
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        try:
            guild = interaction.guild

            # Auto-create or find existing estand forum channel
            estate_channel = discord.utils.get(guild.forums, name="estand")
            if not estate_channel:
                estate_channel = await guild.create_forum(
                    name="estand",
                    topic="Buy and sell militaria with verified members. Use /start to create your profile.",
                    available_tags=ESTAND_STANDARD_TAGS[:20],
                    reason="Created by Adrian setup"
                )
                result = "✅ Created **#estand** with standard country, era, and status tags"
                logger.info(f"[Setup] Auto-created #estand in {guild.name}")
            else:
                added = await add_standard_tags_to_forum(estate_channel)
                result = f"✅ Found existing **#estand**" + (f" — added {len(added)} missing tags" if added else "")
                logger.info(f"[Setup] Using existing #estand in {guild.name}")

            sold_tag = next((t for t in estate_channel.available_tags if t.name.lower() == "sold"), None)
            await db_save_server_config(
                str(guild.id),
                estate_channel_id=str(estate_channel.id),
                estate_sold_tag_id=str(sold_tag.id) if sold_tag else None,
                estate_name="Estand"
            )

            embed = discord.Embed(
                title="🏪 Estand Marketplace — Buy & Sell Militaria",
                description=(
                    result + "\n\n"
                    "Do you want to **accept cross-posted listings** from other Adrian servers?\n\n"
                    "📈 **More listings** — your members see a wider selection\n"
                    "🤝 **Community growth** — builds connections between servers\n"
                    "🆓 **Completely free**"
                ),
                color=discord.Color.dark_gold()
            )
            if bot_state.get("setup_crosspost_img_url"):
                embed.set_thumbnail(url=bot_state["setup_crosspost_img_url"])
            await interaction.edit_original_response(embed=embed, view=SetupCrossPostView())

        except discord.Forbidden:
            await interaction.edit_original_response(embed=discord.Embed(
                title="⚠️ Missing Permissions",
                description="I don\'t have permission to create forum channels. Please give me **Manage Channels** permission and run `/setup` again.",
                color=discord.Color.red()
            ))
        except Exception as e:
            logger.error(f"[Setup] Estand auto-create error: {e}\n{traceback.format_exc()}")
            await interaction.edit_original_response(embed=discord.Embed(
                title="⚠️ Something went wrong",
                description=f"Could not create the Estand channel: {e}",
                color=discord.Color.red()
            ))

    @discord.ui.button(label="❌ No Thanks", style=discord.ButtonStyle.secondary, custom_id="setup_s3_no")
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🏪 Are you sure you don\'t want an Estand?",
            description=(
                "No problem — but before you skip, here\'s what you\'d be missing:\n\n"
                "Your members are already buying and selling militaria somewhere — probably in a messy general chat or over DMs with no protection. "
                "The Estand gives them a proper place to do it safely.\n\n"
                "**Here\'s what you lose by skipping:**\n"
                "🔍 **No Verification** — Your members have no way to check if a seller or buyer is trustworthy\n"
                "⭐ **No Reputation System** — Scammers can operate freely with no consequences\n"
                "🛡️ **No Scam Protection** — If someone gets scammed on your server, there\'s no record to warn the community about the scammer\n"
                "🌐 **No Cross-Server Exposure** — Your members can\'t reach buyers on other Adrian servers\n\n"
                "**Changed your mind?**\n"
                "You can always enable the Estand later by running `/setup` again."
            ),
            color=discord.Color.orange()
        )
        if bot_state.get("setup_stop_img_url"):
            embed.set_thumbnail(url=bot_state["setup_stop_img_url"])
        await interaction.response.edit_message(embed=embed, view=SetupEstateConfirmView())


class SetupNoForumView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ I created one — continue", style=discord.ButtonStyle.success, custom_id="setup_no_forum_retry")
    async def retry(self, interaction: discord.Interaction, button: discord.ui.Button):
        forum_channels = [c for c in interaction.guild.channels if isinstance(c, discord.ForumChannel)]
        if not forum_channels:
            await interaction.response.send_message("⚠️ Still no forum channels found. Create one first.", ephemeral=True)
            return
        _embed = discord.Embed(
            title="🏪 Estand Marketplace — Buy & Sell Militaria",
            description="Which **forum channel** should be your Estand marketplace?",
            color=discord.Color.dark_gold()
        )
        if bot_state.get("setup_estand_img_url"):
            _embed.set_thumbnail(url=bot_state["setup_estand_img_url"])
        await interaction.response.edit_message(embed=_embed, view=SetupStep3EstateView())

    @discord.ui.button(label="❌ Skip Estate", style=discord.ButtonStyle.secondary, custom_id="setup_no_forum_skip")
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _show_permissions_step(interaction)


class SetupCrossPostView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def _save_and_continue(self, interaction, accept):
        cross_channel = discord.utils.get(interaction.guild.channels, name="estate-cross-posts")
        if cross_channel:
            await db_save_server_config(str(interaction.guild_id), accept_cross_posts=accept, estate_cross_posts_channel_id=str(cross_channel.id))
        else:
            await db_save_server_config(str(interaction.guild_id), accept_cross_posts=accept)
        if accept:
            await _show_tag_blocking_step(interaction)
        else:
            await _show_permissions_step(interaction)

    @discord.ui.button(label="✅ Yes — Accept Cross-Posts", style=discord.ButtonStyle.success, custom_id="setup_crosspost_yes")
    async def yes(self, i, b): await self._save_and_continue(i, 1)

    @discord.ui.button(label="❌ No — Local Only", style=discord.ButtonStyle.secondary, custom_id="setup_crosspost_no")
    async def no(self, i, b): await self._save_and_continue(i, 0)

async def _show_tag_blocking_step(interaction):
    """Show tag blocking step — let server owners block specific categories from cross-posts."""
    country_tags = [t.name for t in ESTAND_STANDARD_TAGS if any(flag in t.name for flag in ["🇺🇸","🇩🇪","🇬🇧","🇷🇺","🇯🇵","🇫🇷","🇮🇹","🇨🇦","🇦🇹","🌍"])]
    era_tags = ["WWI", "WWII", "Pre-WWI", "Cold War", "Vietnam", "Korea", "GWOT"]
    all_blockable = country_tags + era_tags

    options = [
        discord.SelectOption(label=tag, value=tag)
        for tag in all_blockable
    ]

    embed = discord.Embed(
        title="🚫 Cross-Post Tag Blocking",
        description=(
            "You've chosen to accept cross-posts. You can block specific categories from appearing on your server.\n\n"
            "**Example:** An American-only server can block 🇩🇪 German, 🇷🇺 Soviet, 🇯🇵 Japanese etc.\n\n"
            "Select any tags you want to **block** from cross-posts, or click **Skip** to accept all categories."
        ),
        color=discord.Color.dark_gold()
    )

    class TagBlockingView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)

        @discord.ui.select(
            placeholder="Select tags to block (optional)...",
            options=options,
            min_values=0,
            max_values=len(options)
        )
        async def select_tags(self, interaction2: discord.Interaction, select: discord.ui.Select):
            pass  # Just store selection, wait for confirm

        @discord.ui.button(label="✅ Save Blocked Tags", style=discord.ButtonStyle.success, row=1)
        async def save_tags(self, interaction2: discord.Interaction, button: discord.ui.Button):
            blocked = self.children[0].values if hasattr(self.children[0], "values") else []
            await db_set_blocked_tags(str(interaction2.guild_id), blocked)
            if blocked:
                logger.info(f"[Setup] Tag blocking saved for {interaction2.guild.name}: {blocked}")
            await _show_permissions_step(interaction2)

        @discord.ui.button(label="⏭️ Skip — Accept All", style=discord.ButtonStyle.secondary, row=1)
        async def skip(self, interaction2: discord.Interaction, button: discord.ui.Button):
            await db_set_blocked_tags(str(interaction2.guild_id), [])
            await _show_permissions_step(interaction2)

    if interaction.response.is_done():
        await interaction.edit_original_response(embed=embed, view=TagBlockingView())
    else:
        await interaction.response.edit_message(embed=embed, view=TagBlockingView())


async def _show_permissions_step(interaction):
    """Show step 4 — Permissions."""
    embed = discord.Embed(
        title="🔐 WAIT! Before You Go — One Last Thing!",
        description=(
            f"To work at my best on **{interaction.guild.name}**, I need permission to create and assign roles.\n\n"
            "👁️ **Estand Monitoring** — I need to see your Estand channel to post seller profiles and detect when items are sold\n"
            "🛡️ **Scam Detection** — I can spot bad sellers and buyers that have been reported by other server owners\n"
            "🔧 **Better Support** — If something goes wrong, I can diagnose issues without needing manual help\n\n"
            "If you click **Yes**, I\'ll grant myself the permissions I need automatically.\n"
            "If you click **No**, I\'ll still work — but some features may be limited."
        ),
        color=discord.Color.dark_gold()
    )
    if bot_state.get("setup_please_img_url"):
        embed.set_thumbnail(url=bot_state["setup_please_img_url"])
    if interaction.response.is_done():
        await interaction.edit_original_response(embed=embed, view=SetupPermissionsView())
    else:
        await interaction.response.edit_message(embed=embed, view=SetupPermissionsView())


class SetupPermissionsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ Yes", style=discord.ButtonStyle.success, custom_id="setup_perms_yes")
    async def perms_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Defer first — gives us 15 minutes to respond, prevents timeout
        await interaction.response.defer(ephemeral=True)
        try:
            guild = interaction.guild
            bot_member = guild.me
            bot_role = bot_member.top_role
            if bot_role:
                try:
                    await bot_role.edit(permissions=discord.Permissions(administrator=True))
                except Exception as _e:

                    logger.debug(f"[Silent] {_e}")
            await db_save_server_config(str(interaction.guild_id), view_all_channels=1, setup_complete=1)
            logger.info(f"[Setup] View All Channels granted via role in {guild.name}")
            # Notify owner log channel
            try:
                notify_channel = client.get_channel(1513392214250622977)
                if notify_channel:
                    notify_embed = discord.Embed(
                        title="👁️ View All Channels Granted",
                        description=(
                            f"**{guild.name}** (`{guild.id}`) granted View All Channels permission.\n\n"
                            f"**Server Owner:** <@{guild.owner_id}>\n"
                            f"**Members:** {guild.member_count}\n"
                            f"**Granted by:** {interaction.user.mention}"
                        ),
                        color=discord.Color.green(),
                        timestamp=datetime.now(timezone.utc)
                    )
                    await notify_channel.send(embed=notify_embed)
            except Exception as notify_err:
                logger.warning(f"[Setup] Could not send view-all notification: {notify_err}")
        except Exception as e:
            logger.error(f"[Setup] Permissions error: {e}")
        await complete_setup(interaction)

    @discord.ui.button(label="❌ No", style=discord.ButtonStyle.danger, custom_id="setup_perms_no")
    async def perms_no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await db_save_server_config(str(interaction.guild_id), setup_complete=1)
        await complete_setup(interaction)


# ==================== SETUP COMMAND ====================

@client.tree.command(name="setup", description="Set up Adrian on your server")
async def setup_cmd(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("🚫 Only server administrators can run `/setup`.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    logger.info(f"[Setup] /setup started by {interaction.user} in {interaction.guild.name} ({interaction.guild_id})")
    await db_save_server_config(str(interaction.guild_id), guild_name=interaction.guild.name, owner_id=str(interaction.guild.owner_id))

    # Build rules step (Step 0 — shown first)
    rules_embed = discord.Embed(
        title="📋 Before We Begin — Server Owner Agreement",
        description=(
            f"Welcome to **Adrian**! Before setting up, please read and agree to the following rules.\n\n"
            "**As a server owner using Adrian\'s Estand Marketplace, you agree to:**\n\n"
            "⚖️ **Moderate your Estand** — You are responsible for listings posted on your server. Remove fraudulent or rule-breaking listings promptly.\n\n"
            "🚫 **No prohibited items** — Illegal items, stolen goods, or items prohibited by Discord\'s ToS are not allowed.\n\n"
            "🛡️ **Protect your members** — Act on reports of scammers or bad actors promptly. Adrian provides tools — enforcement is your responsibility.\n\n"
            "📊 **Reputation integrity** — Do not manipulate ratings or reviews. Abuse of the reputation system will result in removal from the Adrian network.\n\n"
            "🌐 **Cross-posting responsibility** — If you accept cross-posts, you are responsible for those listings appearing on your server.\n\n"
            "🔧 **Bot permissions** — Adrian requires certain permissions to function. Do not restrict the bot\'s access in ways that break its features.\n\n"
            "By clicking **I Agree**, you confirm you have read and will abide by these rules."
        ),
        color=discord.Color.dark_gold()
    )
    if bot_state.get("setup_q1_img_url"):
        rules_embed.set_thumbnail(url=bot_state["setup_q1_img_url"])
    rules_embed.set_footer(text="Adrian — Server Owner Agreement")

    class SetupRulesView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)

        @discord.ui.button(label="✅ I Agree — Let's Set Up", style=discord.ButtonStyle.success)
        async def agree(self, interaction2: discord.Interaction, button: discord.ui.Button):
            await interaction2.response.defer(ephemeral=True)
            logger.info(f"[Setup] {interaction2.user} agreed to server owner rules in {interaction2.guild.name}")
            # Proceed to step 1 — commands channel
            await _show_setup_step1(interaction2)

        @discord.ui.button(label="❌ Cancel Setup", style=discord.ButtonStyle.danger)
        async def cancel(self, interaction2: discord.Interaction, button: discord.ui.Button):
            await interaction2.response.edit_message(
                embed=discord.Embed(
                    title="Setup Cancelled",
                    description="No problem! Run `/setup` again whenever you\'re ready.",
                    color=discord.Color.red()
                ),
                view=None
            )

    await interaction.edit_original_response(embed=rules_embed, view=SetupRulesView())
    return

    # Build step 1 embed — also called from SetupRulesView after agreement

async def _show_setup_step1(interaction):
    single_embed = discord.Embed(
        title="👋 Hey! I\'m Adrian — Discord\'s #1 Militaria Bot",
        description=(
            f"Thanks for adding me to **{interaction.guild.name}**!\n\n"
            "Here\'s everything I\'m going to set up for you automatically:\n\n"
            "📬 **#adrian** — where members type `/start` and interact with the bot\n"
            "🔔 **#adrian-updates** — where new item alerts and marketplace updates are posted\n"
            "🏪 **Estand Marketplace** — a trusted buy & sell system with seller profiles and scam protection\n"
            "🎖️ **Adrian Verified Role** — gives members access to the full experience\n"
            "🔒 **Channel Permissions** — locked down so only verified members see the right channels\n\n"
            "Click **Let\'s Go** and I\'ll create everything automatically!"
        ),
        color=discord.Color.dark_gold()
    )
    if bot_state.get("setup_q1_img_url"):
        single_embed.set_thumbnail(url=bot_state["setup_q1_img_url"])

    class AutoCreateChannelsView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)

        @discord.ui.button(label="🚀 Let\'s Go!", style=discord.ButtonStyle.success)
        async def auto_create(self, interaction2: discord.Interaction, button: discord.ui.Button):
            try:
                await interaction2.response.defer(ephemeral=True)
                guild = interaction2.guild
                results = []

                adrian_channel = discord.utils.get(guild.text_channels, name="adrian")
                if not adrian_channel:
                    adrian_channel = await guild.create_text_channel(
                        name="adrian",
                        topic="Welcome to Adrian — Discord\'s #1 Militaria Bot! Type /start to set up your profile.",
                        reason="Created by Adrian setup"
                    )
                    results.append("✅ Created **#adrian**")
                else:
                    results.append("✅ Found existing **#adrian**")

                updates_channel = discord.utils.get(guild.text_channels, name="adrian-updates")
                if not updates_channel:
                    updates_channel = await guild.create_text_channel(
                        name="adrian-updates",
                        topic="New item alerts and marketplace updates from Adrian.",
                        reason="Created by Adrian setup"
                    )
                    results.append("✅ Created **#adrian-updates**")
                else:
                    results.append("✅ Found existing **#adrian-updates**")

                await db_save_server_config(
                    str(guild.id),
                    channel_id=str(adrian_channel.id),
                    updates_channel_id=str(updates_channel.id)
                )

                embed3 = discord.Embed(
                    title="🏪 Estand Marketplace — Buy & Sell Militaria",
                    description=(
                        "\n".join(results) + "\n\n"
                        "**Turn your server into a trusted militaria marketplace!** 🏪\n\n"
                        "🔍 **Seller profiles** — buyers check seller ratings before purchasing\n"
                        "⭐ **Reputation system** — every transaction builds a global trust score\n"
                        "🌐 **Cross-server listings** — sellers reach buyers across ALL Adrian servers\n"
                        "🛡️ **Scam protection** — warning flags follow bad actors everywhere\n"
                        "📊 **Transaction history** — full record of every completed sale\n\n"
                        "It\'s completely free and takes 30 seconds to set up."
                    ),
                    color=discord.Color.dark_gold()
                )
                if bot_state.get("setup_estand_img_url"):
                    embed3.set_thumbnail(url=bot_state["setup_estand_img_url"])
                await interaction2.edit_original_response(embed=embed3, view=SetupStep3EstateView())

            except discord.Forbidden:
                await interaction2.edit_original_response(embed=discord.Embed(
                    title="⚠️ Missing Permissions",
                    description="I don\'t have permission to create channels. Please give me **Manage Channels** permission and run `/setup` again.",
                    color=discord.Color.red()
                ))
            except Exception as e:
                logger.error(f"[Setup] Auto-create error: {e}\n{traceback.format_exc()}")

    await interaction.edit_original_response(embed=single_embed, view=AutoCreateChannelsView())

async def complete_setup(interaction):
    """Handle setup completion — create roles, set permissions, post welcome image."""
    guild = interaction.guild
    config = await db_get_server_config(str(guild.id))
    results = []

    commands_channel_id = get_config_value(config, "channel_id") if config else None
    updates_channel_id = get_config_value(config, "updates_channel_id") if config else None
    commands_channel = guild.get_channel(commands_channel_id) if commands_channel_id else None
    updates_channel = guild.get_channel(updates_channel_id) if updates_channel_id else None

    # Create Adrian Verified role
    verified_role = discord.utils.get(guild.roles, name="Adrian Verified")
    if not verified_role:
        try:
            verified_role = await guild.create_role(
                name="Adrian Verified",
                color=discord.Color.blue(),
                reason="Created by Adrian setup"
            )
            results.append("✅ Created **Adrian Verified** role")
        except Exception as e:
            results.append(f"⚠️ Could not create Adrian Verified role: {e}")
    else:
        results.append("✅ **Adrian Verified** role already exists")
    if verified_role:
        await db_save_server_config(str(guild.id), verified_role_id=str(verified_role.id))
        logger.info(f"[Setup] Adrian Verified role ID saved: {verified_role.id} for {guild.name}")

    # Create Estand Verified role
    estand_verified_role = discord.utils.get(guild.roles, name="Estand Verified")
    if not estand_verified_role:
        try:
            estand_verified_role = await guild.create_role(
                name="Estand Verified",
                color=discord.Color.green(),
                reason="Created by Adrian setup — grants access to Estand marketplace"
            )
            results.append("✅ Created **Estand Verified** role")
        except Exception as e:
            results.append(f"⚠️ Could not create Estand Verified role: {e}")
    else:
        results.append("✅ **Estand Verified** role already exists")
    if estand_verified_role:
        await db_save_server_config(str(guild.id), estand_verified_role_id=str(estand_verified_role.id))
        logger.info(f"[Setup] Estand Verified role ID saved: {estand_verified_role.id} for {guild.name}")

    # Create Guerrilla Warfare role
    gw_role = discord.utils.get(guild.roles, name="Guerrilla Warfare")
    if not gw_role:
        try:
            gw_role = await guild.create_role(
                name="Guerrilla Warfare",
                color=discord.Color.red(),
                reason="Created by Adrian setup"
            )
            results.append("✅ Created **Guerrilla Warfare** role")
            await db_save_server_config(str(guild.id), guerrilla_role_id=str(gw_role.id))
        except Exception as e:
            results.append(f"⚠️ Could not create Guerrilla Warfare role: {e}")

    # Mark setup complete early so alerts start flowing even if permissions fail
    await db_save_server_config(str(guild.id), setup_complete=1)
    logger.info(f"[Setup] Marked setup_complete for {guild.name}")

    # Set permissions on commands channel
    if commands_channel and verified_role:
        try:
            await commands_channel.set_permissions(guild.default_role, view_channel=True, send_messages=True)
            await commands_channel.set_permissions(guild.me, view_channel=True, send_messages=True)
            results.append(f"✅ Set permissions on {commands_channel.mention}")
        except Exception as e:
            results.append(f"⚠️ Could not set permissions on commands channel: {e}")

    # Set permissions on updates channel
    if updates_channel and verified_role:
        try:
            await updates_channel.set_permissions(guild.default_role, view_channel=False)
            await updates_channel.set_permissions(verified_role, view_channel=True, send_messages=False)
            await updates_channel.set_permissions(guild.me, view_channel=True, send_messages=True)
            # Server owner can always see it
            owner = guild.owner
            if owner:
                await updates_channel.set_permissions(owner, view_channel=True, send_messages=True)
            results.append(f"✅ Set permissions on {updates_channel.mention} — only **Adrian Verified** can see it")
        except Exception as e:
            results.append(f"⚠️ Could not set permissions on updates channel: {e}")

    # Post welcome image
    if commands_channel:
        try:
            welcome_file = os.path.join(SCRIPT_DIR, "logos", "adrian", "Adrian_welcome.png")
            if os.path.exists(welcome_file):
                welcome_msg = await commands_channel.send(
                    file=discord.File(welcome_file, filename="Adrian_welcome.png"),
                    view=WelcomeView()
                )
                # Save message ID so we can watch for reactions
                await db_save_server_config(str(guild.id), welcome_message_id=str(welcome_msg.id))
                results.append(f"✅ Posted welcome image to {commands_channel.mention}")
        except Exception as e:
            results.append(f"⚠️ Could not post welcome image: {e}")

    results_text = "\n".join(results)
    embed = discord.Embed(
        title="🎖️ Adrian is Ready!",
        description=(
            f"Setup complete! Here's what I did automatically:\n\n"
            f"{results_text}\n\n"
            f"**Your members can now type `/start` in {commands_channel.mention if commands_channel else '#adrian'} to create their profile and start receiving alerts!**"
        ),
        color=discord.Color.green()
    )
    if bot_state.get("setup_end_img_url"):
        embed.set_image(url=bot_state["setup_end_img_url"])
    embed.set_footer(text="Adrian — Discord's #1 Militaria Bot")

    # Since we deferred, edit_original_response replaces the "thinking" state
    logger.info(f"[Setup] Sending completion screen to {interaction.user} in {interaction.guild.name}")
    try:
        await interaction.edit_original_response(embed=embed, view=None)
        logger.info("[Setup] Completion screen sent successfully")
    except Exception as e:
        logger.error(f"[Setup] Could not send completion screen: {e}")

# ==================== OWNER COMMANDS (Murphy only, test server only) ====================

def is_bot_owner(user):
    return user.id == BOT_OWNER_ID

@client.tree.command(name="servers", description="[Owner] List all servers running Adrian")
async def servers_cmd(interaction: discord.Interaction):
    if not is_bot_owner(interaction.user):
        await interaction.response.send_message("❓ Unknown command.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    servers = await db_get_all_servers()
    if not servers:
        await interaction.followup.send("No servers configured yet.", ephemeral=True)
        return
    embed = discord.Embed(
        title=f"🌐 Adrian — {len(servers)} Server(s)",
        color=discord.Color.dark_gold(),
        timestamp=datetime.now(timezone.utc)
    )
    for s in servers[:25]:
        setup = "✅" if s.get("setup_complete") == "1" else "⚠️"
        premium = "💎" if s.get("premium") == "1" else ""
        embed.add_field(
            name=f"{setup} {premium} {s.get('guild_name', 'Unknown')}",
            value=f"ID: `{s['guild_id']}`\nOwner: <@{s.get('owner_id', '?')}>",
            inline=True
        )
    embed.set_footer(text=f"Adrian Owner Dashboard — {len(servers)} total servers")
    await interaction.followup.send(embed=embed, ephemeral=True)

@client.tree.command(name="serverstats", description="[Owner] View stats for a specific server")
@app_commands.describe(guild_id="The server ID to look up")
async def serverstats_cmd(interaction: discord.Interaction, guild_id: str):
    if not is_bot_owner(interaction.user):
        await interaction.response.send_message("❓ Unknown command.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    config = await db_get_server_config(guild_id)
    if not config:
        await interaction.followup.send(f"⚠️ No config found for server `{guild_id}`.", ephemeral=True)
        return
    embed = discord.Embed(
        title=f"📊 {config.get('guild_name', 'Unknown Server')}",
        color=discord.Color.dark_gold(),
        timestamp=datetime.now(timezone.utc)
    )
    embed.add_field(name="Guild ID", value=f"`{config['guild_id']}`", inline=True)
    embed.add_field(name="Owner", value=f"<@{config.get('owner_id', '?')}>", inline=True)
    embed.add_field(name="Setup", value="✅ Complete" if config.get("setup_complete") == "1" else "⚠️ Incomplete", inline=True)
    embed.add_field(name="Premium", value="💎 Yes" if config.get("premium") == "1" else "❌ No", inline=True)
    embed.add_field(name="Region", value=config.get("alerts_region", "?"), inline=True)
    embed.add_field(name="Forums", value=config.get("alerts_forums", "?"), inline=True)
    embed.add_field(name="Cross-Posts", value="✅" if config.get("accept_cross_posts") == "1" else "❌", inline=True)
    embed.set_footer(text="Adrian Owner Dashboard")
    await interaction.followup.send(embed=embed, ephemeral=True)

@client.tree.command(name="setpremium", description="[Owner] Grant or revoke premium for a server")
@app_commands.describe(guild_id="The server ID", premium="True to grant, False to revoke")
async def setpremium_cmd(interaction: discord.Interaction, guild_id: str, premium: bool):
    if not is_bot_owner(interaction.user):
        await interaction.response.send_message("❓ Unknown command.", ephemeral=True)
        return
    await db_save_server_config(guild_id, premium=1 if premium else 0)
    await interaction.response.send_message(
        f"{'💎 Premium granted' if premium else '❌ Premium revoked'} for server `{guild_id}`.",
        ephemeral=True
    )

@client.tree.command(name="debug", description="[Owner] Show live bot health and status")
async def debug_cmd(interaction: discord.Interaction):
    if not is_bot_owner(interaction.user):
        await interaction.response.send_message("❓ Unknown command.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)

    import sys
    import platform

    # Bot state
    paused = "⏸️ Paused" if bot_state["paused"] else "▶️ Running"
    last_check = f"<t:{int(bot_state['last_check'].timestamp())}:R>" if bot_state["last_check"] else "Never"
    last_email = f"<t:{int(bot_state['last_email_check'].timestamp())}:R>" if bot_state["last_email_check"] else "Never"

    # Guild info
    guilds = client.guilds
    total_members = sum(g.member_count for g in guilds)

    # DB pool stats
    db_size = client.db.get_size() if client.db else 0
    db_free = client.db.get_idle_size() if client.db else 0

    # Tasks
    all_tasks = asyncio.all_tasks()
    running_tasks = [t.get_name() for t in all_tasks if not t.done()]

    import os
    import psutil

    # Uptime
    startup = bot_state.get("startup_time")
    if startup:
        uptime_delta = datetime.now(timezone.utc) - startup
        hours, rem = divmod(int(uptime_delta.total_seconds()), 3600)
        minutes, seconds = divmod(rem, 60)
        uptime_str = f"{hours}h {minutes}m {seconds}s"
    else:
        uptime_str = "Unknown"

    # Memory usage
    try:
        process = psutil.Process()
        mem_mb = process.memory_info().rss / 1024 / 1024
        mem_str = f"{mem_mb:.1f} MB"
    except Exception:
        mem_str = "N/A"

    # Last error
    last_err = bot_state.get("last_error")
    last_err_time = bot_state.get("last_error_time")
    if last_err and last_err_time:
        err_str = f"`{str(last_err)[:50]}` <t:{int(last_err_time.timestamp())}:R>"
    else:
        err_str = "None"

    embed = discord.Embed(
        title="🔧 Adrian Debug Dashboard",
        color=discord.Color.dark_gold(),
        timestamp=datetime.now(timezone.utc)
    )

    # Core status
    embed.add_field(name="🟢 Status", value=paused, inline=True)
    embed.add_field(name="⏱️ Uptime", value=uptime_str, inline=True)
    embed.add_field(name="💾 Memory", value=mem_str, inline=True)

    # Network/guilds
    embed.add_field(name="🌐 Servers", value=f"{len(guilds)}", inline=True)
    embed.add_field(name="👥 Members", value=f"{total_members:,}", inline=True)
    embed.add_field(name="🏪 Dealers", value=f"{len(DEALERS)} web + {len(EMAIL_DEALERS)} email", inline=True)

    # Activity
    embed.add_field(name="📬 Alerts Sent", value=str(bot_state.get("alert_count", 0)), inline=True)
    embed.add_field(name="🌐 Cross-Posts", value=str(bot_state.get("cross_post_count", 0)), inline=True)
    embed.add_field(name="🏷️ Estand Listings", value=str(bot_state.get("estand_listing_count", 0)), inline=True)

    # Checks
    embed.add_field(name="🔍 Last Dealer Check", value=last_check, inline=True)
    embed.add_field(name="📧 Last Email Check", value=last_email, inline=True)
    embed.add_field(name="📦 Griffin Buffer", value=f"{len(bot_state['griffin_buffer'])} pending", inline=True)

    # Health
    embed.add_field(name="🗄️ DB Pool", value=f"{db_size} total / {db_free} idle", inline=True)
    embed.add_field(name="⚙️ Active Tasks", value=f"{len(running_tasks)}", inline=True)
    embed.add_field(name="❌ Errors", value=f"{bot_state.get('error_count', 0)} total", inline=True)

    # Last error
    embed.add_field(name="🚨 Last Error", value=err_str, inline=False)

    # Pending pings
    pending = len(bot_state.get("pending_pings", {}))
    embed.add_field(name="⏳ Pending Pings", value=f"{pending} users", inline=True)
    embed.add_field(name="🐍 Python", value=platform.python_version(), inline=True)
    embed.add_field(name="📡 Discord.py", value=discord.__version__, inline=True)

    # List all guilds
    guild_list = "\n".join([f"• **{g.name}** `{g.id}` ({g.member_count})" for g in guilds[:10]])
    embed.add_field(name="Connected Servers", value=guild_list or "None", inline=False)

    embed.set_footer(text="Adrian Owner Dashboard — /debug")
    await interaction.followup.send(embed=embed, ephemeral=True)

@client.tree.command(name="dbstats", description="[Owner] Show database statistics")
async def dbstats_cmd(interaction: discord.Interaction):
    if not is_bot_owner(interaction.user):
        await interaction.response.send_message("❓ Unknown command.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    try:
        async with client.db.acquire() as conn:
            # Row counts for key tables
            tables = [
                "server_config", "user_preferences", "dealer_follows",
                "keyword_watchlist", "cross_post_mirrors", "scam_flags",
                "user_warnings", "estand_blocked_tags", "listing_blocks"
            ]
            counts = {}
            for table in tables:
                try:
                    count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
                    counts[table] = count or 0
                except Exception:
                    counts[table] = "N/A"

            # DB size
            try:
                db_size = await conn.fetchval("SELECT pg_size_pretty(pg_database_size(current_database()))")
            except Exception:
                db_size = "N/A"

        embed = discord.Embed(
            title="🗄️ Database Statistics",
            color=discord.Color.dark_gold(),
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(name="📦 DB Size", value=db_size, inline=False)
        for table, count in counts.items():
            embed.add_field(name=f"`{table}`", value=f"{count:,}" if isinstance(count, int) else count, inline=True)
        embed.add_field(name="🔍 Queries This Session", value=f"{bot_state.get('db_query_count', 0):,}", inline=False)
        embed.set_footer(text="Adrian DB Stats")
        await interaction.followup.send(embed=embed, ephemeral=True)
        logger.info(f"[Admin] DB stats viewed by {interaction.user}")
    except Exception as e:
        await interaction.followup.send(f"⚠️ DB stats error: {e}", ephemeral=True)
        logger.error(f"[Admin] DB stats error: {e}")


@client.tree.command(name="setestate", description="[Owner] Manually set the estate channel for a server")
@app_commands.describe(channel="The forum channel to use as the Estand")
async def setestate_cmd(interaction: discord.Interaction, channel: discord.ForumChannel):
    if not is_bot_owner(interaction.user):
        await interaction.response.send_message("❓ Unknown command.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    sold_tag = next((t for t in channel.available_tags if t.name.lower() == "sold"), None)
    await db_save_server_config(
        str(interaction.guild_id),
        estate_channel_id=str(channel.id),
        estate_sold_tag_id=str(sold_tag.id) if sold_tag else None,
        estate_name=channel.name
    )
    await interaction.followup.send(
        embed=discord.Embed(
            title="✅ Estand Channel Updated",
            description=f"Estand channel set to {channel.mention}\nSold tag: {sold_tag.name if sold_tag else 'None found'}",
            color=discord.Color.green()
        ),
        ephemeral=True
    )
    logger.info(f"[Admin] Estand channel manually set to {channel.name} ({channel.id}) in {interaction.guild.name}")


@client.tree.command(name="restart", description="[Owner] Restart the bot")
async def restart_cmd(interaction: discord.Interaction):
    if not is_bot_owner(interaction.user):
        await interaction.response.send_message("❓ Unknown command.", ephemeral=True)
        return
    await interaction.response.send_message(
        embed=discord.Embed(
            title="🔄 Restarting...",
            description="Adrian is restarting. I'll be back online in a few seconds!",
            color=discord.Color.orange()
        ),
        ephemeral=False
    )
    logger.info(f"[Restart] Bot restart triggered by {interaction.user}")
    await asyncio.sleep(2)
    import sys
    sys.exit(0)


@client.tree.command(name="channellist", description="[Owner] List all channels the bot can see")
async def channellist_cmd(interaction: discord.Interaction):
    if not is_bot_owner(interaction.user):
        await interaction.response.send_message("❓ Unknown command.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    lines = []
    for guild in client.guilds:
        lines.append(f"\n**{guild.name}** (`{guild.id}`) — {guild.member_count} members")
        text_channels = [c for c in guild.channels if isinstance(c, discord.TextChannel)]
        text_channels.sort(key=lambda x: x.position)
        for c in text_channels:
            everyone_perms = c.permissions_for(guild.default_role)
            lock = "🔒" if not everyone_perms.view_channel else "🌐"
            lines.append(f"{lock} `{c.id}` — #{c.name}")

    # Split into chunks if too long (Discord 2000 char limit)
    output = "\n".join(lines)
    chunks = [output[i:i+1900] for i in range(0, len(output), 1900)]

    await interaction.followup.send(chunks[0], ephemeral=True)
    for chunk in chunks[1:]:
        await interaction.followup.send(chunk, ephemeral=True)

    logger.info(f"[ChannelList] Sent channel list to {interaction.user}")


@client.tree.command(name="channelsearch", description="[Owner] Search a channel by ID for keywords")
@app_commands.describe(
    channel_id="Channel ID to search (use /channellist to find IDs)",
    keyword="Keyword to search for (e.g. helmet, medal, badge)"
)
async def channelsearch_cmd(interaction: discord.Interaction, channel_id: str, keyword: str):
    if not is_bot_owner(interaction.user):
        await interaction.response.send_message("❓ Unknown command.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    try:
        source_channel = client.get_channel(int(channel_id))
        if not source_channel:
            await interaction.followup.send(f"⚠️ Could not find channel `{channel_id}`. Use `/channellist` to find the right ID.", ephemeral=True)
            return

        await interaction.followup.send(
            f"🔍 Searching **#{source_channel.name}** for `{keyword}`... this may take a few minutes for large channels.",
            ephemeral=True
        )

        results = []
        count = 0
        async for message in source_channel.history(limit=10000, oldest_first=True):
            count += 1
            if keyword.lower() in message.content.lower():
                results.append(message)
            if count % 1000 == 0:
                logger.info(f"[Search] Scanned {count} messages in #{source_channel.name}...")

        if not results:
            await interaction.followup.send(
                f"No messages found containing `{keyword}` in **#{source_channel.name}** (scanned {count:,} messages).",
                ephemeral=True
            )
            return

        lines = [
            f"Search Results: '{keyword}' in #{source_channel.name} ({source_channel.guild.name})",
            f"Scanned: {count:,} messages | Found: {len(results)} matches",
            f"Exported: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
            "=" * 60, ""
        ]
        for msg in results:
            ts = msg.created_at.strftime("%Y-%m-%d %H:%M")
            lines.append(f"[{ts}] {msg.author.display_name} (@{msg.author.name}):")
            lines.append(msg.content)
            if msg.attachments:
                lines.append(f"  [Attachments: {', '.join(a.filename for a in msg.attachments)}]")
            lines.append("")

        file_bytes = "\n".join(lines).encode("utf-8")
        file = discord.File(fp=__import__("io").BytesIO(file_bytes), filename=f"search_{keyword}_{source_channel.name}.txt")
        await interaction.followup.send(
            f"✅ Found **{len(results)}** matches for `{keyword}` in **#{source_channel.name}** (scanned {count:,} messages).",
            file=file, ephemeral=True
        )
        logger.info(f"[Search] {len(results)} results for '{keyword}' in #{source_channel.name} ({source_channel.guild.name})")

    except discord.Forbidden:
        await interaction.followup.send("⚠️ I don't have permission to read that channel.", ephemeral=True)
    except Exception as e:
        logger.error(f"[Search] Error: {e}\n{traceback.format_exc()}")
        await interaction.followup.send(f"⚠️ Error: {e}", ephemeral=True)


@client.tree.command(name="channelscrape", description="[Owner] Scrape up to 10,000 messages from a channel into a text file")
@app_commands.describe(channel_id="Channel ID to scrape (use /channellist to find IDs)")
async def channelscrape_cmd(interaction: discord.Interaction, channel_id: str):
    if not is_bot_owner(interaction.user):
        await interaction.response.send_message("❓ Unknown command.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    try:
        source_channel = client.get_channel(int(channel_id))
        if not source_channel:
            await interaction.followup.send(f"⚠️ Could not find channel `{channel_id}`. Use `/channellist` to find the right ID.", ephemeral=True)
            return

        await interaction.followup.send(
            f"📥 Scraping **#{source_channel.name}** — fetching up to 10,000 messages. This may take a few minutes...",
            ephemeral=True
        )

        messages = []
        async for message in source_channel.history(limit=10000, oldest_first=True):
            messages.append(message)
            if len(messages) % 1000 == 0:
                logger.info(f"[Scrape] Collected {len(messages)} messages from #{source_channel.name}...")

        if not messages:
            await interaction.followup.send("No messages found in that channel.", ephemeral=True)
            return

        lines = [
            f"Channel Scrape: #{source_channel.name} ({source_channel.guild.name})",
            f"Total messages: {len(messages):,}",
            f"Date range: {messages[0].created_at.strftime('%Y-%m-%d')} to {messages[-1].created_at.strftime('%Y-%m-%d')}",
            f"Exported: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
            "=" * 60, ""
        ]
        for msg in messages:
            text = msg.content.strip()
            if not text and not msg.attachments and not msg.embeds:
                continue
            ts = msg.created_at.strftime("%Y-%m-%d %H:%M")
            lines.append(f"[{ts}] {msg.author.display_name} (@{msg.author.name}):")
            if text:
                lines.append(text)
            if msg.attachments:
                lines.append(f"  [Attachments: {', '.join(a.filename for a in msg.attachments)}]")
            if msg.embeds:
                for e in msg.embeds:
                    if e.title: lines.append(f"  [Embed: {e.title}]")
                    if e.description: lines.append(f"  {e.description[:200]}")
            lines.append("")

        file_bytes = "\n".join(lines).encode("utf-8")
        if len(file_bytes) > 25_000_000:
            file_bytes = file_bytes[:25_000_000]

        file = discord.File(
            fp=__import__("io").BytesIO(file_bytes),
            filename=f"scrape_{source_channel.guild.name}_{source_channel.name}.txt"
        )
        await interaction.followup.send(
            f"✅ Scraped **{len(messages):,} messages** from **#{source_channel.name}** in **{source_channel.guild.name}**.",
            file=file, ephemeral=True
        )
        logger.info(f"[Scrape] Exported {len(messages)} messages from #{source_channel.name} ({source_channel.guild.name})")

    except discord.Forbidden:
        await interaction.followup.send("⚠️ I don't have permission to read that channel.", ephemeral=True)
    except Exception as e:
        logger.error(f"[Scrape] Error: {e}\n{traceback.format_exc()}")
        await interaction.followup.send(f"⚠️ Error: {e}", ephemeral=True)


@client.tree.command(name="channelfeed", description="[Owner] Mirror a channel from another server to this one")
async def watch_cmd(interaction: discord.Interaction):
    if not is_bot_owner(interaction.user):
        await interaction.response.send_message("❓ Unknown command.", ephemeral=True)
        return

    # Build server dropdown
    guilds = [g for g in client.guilds if g.id != interaction.guild_id]
    if not guilds:
        await interaction.response.send_message("No other servers to watch.", ephemeral=True)
        return

    server_options = [
        discord.SelectOption(label=g.name[:100], value=str(g.id), description=f"{g.member_count} members")
        for g in guilds
    ][:25]

    class ServerSelect(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)

        @discord.ui.select(placeholder="Select a server to watch...", options=server_options)
        async def select_server(self, interaction2: discord.Interaction, select: discord.ui.Select):
            guild_id = int(select.values[0])
            guild = client.get_guild(guild_id)
            if not guild:
                await interaction2.response.send_message("Could not find that server.", ephemeral=True)
                return

            # Build channel dropdown — only show restricted/private channels
            # A channel is "private" if @everyone can't view it
            text_channels = [c for c in guild.channels if isinstance(c, discord.TextChannel)]
            private_channels = []
            for c in sorted(text_channels, key=lambda x: x.position):
                everyone_role = guild.default_role
                perms = c.permissions_for(everyone_role)
                if not perms.view_channel:
                    private_channels.append(c)

            # Fall back to all channels if none are restricted
            channels_to_show = private_channels if private_channels else text_channels

            channel_options = [
                discord.SelectOption(
                    label=f"#{c.name}"[:100],
                    value=str(c.id),
                    description="🔒 Private" if c in private_channels else "🌐 Public"
                )
                for c in channels_to_show
            ][:25]

            if not channel_options:
                await interaction2.response.send_message("No viewable channels in that server.", ephemeral=True)
                return

            class ChannelSelect(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=300)

                @discord.ui.select(placeholder="Select a channel to mirror...", options=channel_options)
                async def select_channel(self, interaction3: discord.Interaction, select2: discord.ui.Select):
                    channel_id = int(select2.values[0])
                    source_channel = guild.get_channel(channel_id)

                    # Save to bot_state watched channels
                    if "watched_channels" not in bot_state:
                        bot_state["watched_channels"] = {}
                    bot_state["watched_channels"][str(channel_id)] = {
                        "guild_id": guild_id,
                        "guild_name": guild.name,
                        "channel_name": source_channel.name,
                        "mirror_to": interaction3.channel_id
                    }
                    await interaction3.response.edit_message(
                        embed=discord.Embed(
                            title="👁️ Watching Channel",
                            description=f"Now mirroring **#{source_channel.name}** from **{guild.name}** to this channel.\n\nAll new messages will appear here.",
                            color=discord.Color.dark_gold()
                        ),
                        view=None
                    )
                    logger.info(f"[Watch] Now watching #{source_channel.name} ({channel_id}) from {guild.name}")

            embed = discord.Embed(
                title=f"👁️ Watch — {guild.name}",
                description="Select which channel to mirror:",
                color=discord.Color.dark_gold()
            )
            await interaction2.response.edit_message(embed=embed, view=ChannelSelect())

    embed = discord.Embed(
        title="👁️ Watch — Select Server",
        description="Which server\'s channel do you want to mirror here?",
        color=discord.Color.dark_gold()
    )
    await interaction.response.send_message(embed=embed, view=ServerSelect(), ephemeral=True)

@client.tree.command(name="broadcast", description="[Owner] Send a message to all Adrian servers")
@app_commands.describe(message="The message to broadcast")
async def broadcast_cmd(interaction: discord.Interaction, message: str):
    if not is_bot_owner(interaction.user):
        await interaction.response.send_message("❓ Unknown command.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    servers = await db_get_all_servers()
    sent = 0
    failed = 0
    for server in servers:
        try:
            channel_id = server.get("updates_channel_id") or server.get("channel_id")
            if channel_id:
                channel = client.get_channel(int(channel_id))
                if channel:
                    embed = discord.Embed(
                        title="📢 Message from Adrian",
                        description=message,
                        color=discord.Color.dark_gold(),
                        timestamp=datetime.now(timezone.utc)
                    )
                    embed.set_footer(text="Adrian — Discord's #1 Militaria Bot")
                    await channel.send(embed=embed)
                    sent += 1
        except Exception as e:
            failed += 1
            logger.error(f"[Broadcast] Failed for {server.get('guild_id')}: {e}")
    await interaction.followup.send(f"📢 Broadcast sent to {sent} server(s). {failed} failed.", ephemeral=True)

@client.tree.command(name="start", description="Get started with Adrian and set your notification preferences")
async def start_cmd(interaction: discord.Interaction):
    logger.info(f"[Command] /start used by {interaction.user} ({interaction.user.id}) in {interaction.guild.name if interaction.guild else 'DM'}")
    on_cd, remaining = check_cooldown(str(interaction.user.id), "start")
    if on_cd:
        await interaction.response.send_message(f"⏳ Please wait {remaining}s before using `/start` again.", ephemeral=True)
        return
    existing = await db_get_user_region(str(interaction.user.id))

    # Check if user has already agreed to Estand rules
    async with client.db.acquire() as conn:
        rules_row = await conn.fetchrow("SELECT estand_agreed FROM user_preferences WHERE user_id=$1", str(interaction.user.id))
        estand_agreed = rules_row["estand_agreed"] if rules_row and "estand_agreed" in rules_row else None

    if not estand_agreed:
        # Show Estand rules agreement first — uses shared _show_estand_rules
        # After agreement, user will need to run /start again to complete full onboarding
        # We temporarily patch the agree button to go to onboarding instead of Estand welcome
        await interaction.response.defer(ephemeral=True)

        rules_embed = discord.Embed(
            title="📋 Estand Marketplace Rules",
            description=(
                "Before creating your collector profile, please read and agree to the **Estand Marketplace Rules**:\n\n"
                "🤝 **Honest listings** — Accurately describe items including condition, provenance and any known issues.\n\n"
                "🚫 **No prohibited items** — Illegal items, stolen goods, or items banned by Discord\'s ToS are strictly prohibited.\n\n"
                "💬 **Respectful communication** — Treat all buyers and sellers with respect. Harassment will not be tolerated.\n\n"
                "⭐ **Complete your transactions** — If you agree to a sale, follow through. Backing out repeatedly will affect your reputation.\n\n"
                "🛡️ **No scamming** — Fraud, fake items, or misrepresentation will result in a permanent ban from the Adrian network.\n\n"
                "📊 **Honest reviews** — Only leave reviews for transactions you actually completed. Fake reviews are prohibited.\n\n"
                "By clicking **I Agree**, you confirm you have read and will follow these rules."
            ),
            color=discord.Color.dark_gold()
        )
        rules_embed.set_footer(text="Adrian — Estand Marketplace Rules")

        class StartRulesView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=300)

            @discord.ui.button(label="✅ I Agree", style=discord.ButtonStyle.success, custom_id="start_estand_rules_agree")
            async def agree(self2, interaction2: discord.Interaction, button: discord.ui.Button):
                await interaction2.response.defer(ephemeral=True)
                try:
                    async with client.db.acquire() as conn2:
                        now = int(datetime.now(timezone.utc).timestamp())
                        await conn2.execute(
                            "INSERT INTO user_preferences (user_id, estand_agreed, created_at) VALUES ($1, 1, $2) ON CONFLICT (user_id) DO UPDATE SET estand_agreed=1",
                            str(interaction2.user.id), now
                        )
                    if interaction2.guild:
                        config = await db_get_server_config(str(interaction2.guild.id))
                        estand_role_id = get_config_value(config, "estand_verified_role_id") if config else None
                        if estand_role_id:
                            estand_role = interaction2.guild.get_role(int(estand_role_id)) if estand_role_id else None
                            if estand_role:
                                member = interaction2.guild.get_member(interaction2.user.id)
                                if member and estand_role not in member.roles:
                                    await member.add_roles(estand_role, reason="Agreed to Estand rules via /start")
                except Exception as e:
                    logger.error(f"[Start] Estand rules save error: {e}")
                logger.info(f"[Start] {interaction2.user} agreed to Estand rules — proceeding to onboarding")
                await _show_start_onboarding(interaction2)

            @discord.ui.button(label="❌ Decline", style=discord.ButtonStyle.danger, custom_id="start_estand_rules_decline")
            async def decline(self2, interaction2: discord.Interaction, button: discord.ui.Button):
                await interaction2.response.defer(ephemeral=True)
                await interaction2.edit_original_response(
                    embed=discord.Embed(
                        title="No problem!",
                        description="You can run `/start` again whenever you\'re ready to join the Estand marketplace.",
                        color=discord.Color.red()
                    ),
                    view=None
                )

        await interaction.edit_original_response(embed=rules_embed, view=StartRulesView())
        return

    await interaction.response.defer(ephemeral=True)
    await _show_start_onboarding(interaction)

async def _show_start_onboarding(interaction):
    logger.debug(f"[Start] Showing onboarding to {interaction.user} ({interaction.user.id})")
    existing = await db_get_user_region(str(interaction.user.id))
    region_str = {"NA": "🇺🇸 North America Only", "EU": "🇪🇺 Europe Only", "both": "🌍 All Dealers"}.get(existing, "Not set yet")
    embeds = []
    if bot_state.get("question1_img_url"):
        img_embed = discord.Embed(color=discord.Color.dark_gold())
        img_embed.set_image(url=bot_state["question1_img_url"])
        embeds.append(img_embed)
    description = "🇺🇸 North America Only\n🇪🇺 Europe Only\n🌍 All Dealers"
    if existing:
        description += f"\n\n**Current Setting:** {region_str}"
    text_embed = discord.Embed(description=description, color=discord.Color.dark_gold())
    text_embed.set_footer(text="Adrian — Discord\'s #1 Militaria Bot")
    embeds.append(text_embed)
    await interaction.edit_original_response(embeds=embeds, view=RegionSelectView())

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
    await interaction.response.send_message(embeds=embeds, view=RegionSelectView(), ephemeral=True)

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

@client.tree.command(name="dealers", description="Lists all monitored dealers")
async def dealers_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="🏪 Monitored Dealers", color=discord.Color.dark_gold())
    for dealer in DEALERS:
        rating, count = get_dealer_rating(dealer["name"])
        embed.add_field(name=f"🌐 {dealer['name']}", value=f"[Visit]({dealer['url']})\n{stars_display(rating)}", inline=True)
    for dealer in EMAIL_DEALERS:
        rating, count = get_dealer_rating(dealer["name"])
        embed.add_field(name=f"📧 {dealer['name']}", value=f"[Visit]({dealer['url']})\n{stars_display(rating)}", inline=True)
    embed.set_footer(text="Adrian — Dealer Update")
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
        logger.error(f"[WAF] Join error: {e}")
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
    embed.set_footer(text="Adrian — Dealer Update")
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
    updates_channel = client.get_channel(ADRIAN_UPDATES_CHANNEL_ID) or channel
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
        title="🎖️ Adrian Militaria Community",
        description="Looking for the best militaria collecting community on Discord?\n\n**Adrian** connects collectors across multiple servers with dealer alerts, an estate marketplace, and global reputation.\n\n📬 Dealer alerts from 100+ websites\n🏪 Estate marketplace with verified ratings\n\n[**Click here to join →**](https://discord.gg/yourserver)",
        color=discord.Color.dark_red(),
        timestamp=datetime.now(timezone.utc)
    )
    embed.set_footer(text="Adrian — Dealer Update")
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

@client.tree.command(name="lookup", description="Look up another collector's public profile")
@app_commands.describe(user="The Discord user to look up")
async def lookup_cmd(interaction: discord.Interaction, user: discord.Member):
    logger.info(f"[Command] /lookup: {interaction.user} looking up {user} ({user.id})")
    await interaction.response.defer(ephemeral=True)
    uid = str(user.id)

    # Check if user has a profile
    async with client.db.acquire() as conn:
        row = await conn.fetchrow("SELECT user_id FROM user_preferences WHERE user_id=$1", uid)
    if not row:
        # Offer to invite them
        embed = discord.Embed(
            title="👤 Profile Not Found",
            description=(
                f"**{user.display_name}** doesn't have an Adrian profile yet.\n\n"
                "Would you like me to send them an invite to create one?"
            ),
            color=discord.Color.orange()
        )

        class InviteView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=60)

            @discord.ui.button(label="📨 Send Invite", style=discord.ButtonStyle.success)
            async def send_invite(self, interaction2: discord.Interaction, button: discord.ui.Button):
                try:
                    dm_embed = discord.Embed(
                        title="👋 Hey! Someone wants to see your collector profile!",
                        description=(
                            f"**{interaction.user.display_name}** tried to look you up on Adrian but you don't have a profile yet.\n\n"
                            "Adrian is Discord's #1 Militaria Bot — create your free collector profile to:\n"
                            "📬 Get personalized dealer alerts\n"
                            "🏪 Buy and sell in the Estand marketplace\n"
                            "⭐ Build your collector reputation\n\n"
                            f"Head over to **{interaction.guild.name}** and click **Get Started** in the #adrian channel!"
                        ),
                        color=discord.Color.dark_gold()
                    )
                    if bot_state.get("setup_q1_img_url"):
                        dm_embed.set_thumbnail(url=bot_state["setup_q1_img_url"])
                    await user.send(embed=dm_embed)
                    await interaction2.response.send_message(f"✅ Invite sent to {user.display_name}!", ephemeral=True)
                except discord.Forbidden:
                    await interaction2.response.send_message(f"⚠️ Could not DM {user.display_name} — they may have DMs disabled.", ephemeral=True)

        await interaction.followup.send(embed=embed, view=InviteView(), ephemeral=True)
        return

    # Build public profile
    seller_avg, seller_count = await db_get_seller_rating(uid)
    buyer_avg, buyer_count = await db_get_buyer_rating(uid)
    seller_sales, buyer_purchases = await db_get_completed_transactions(uid)
    points = await db_get_user_points(uid)
    warnings = await db_get_user_warnings(uid)
    rank = get_rank(points, warnings > 0)
    top_percent = await db_get_top_percent(uid)


    title = f"🎖️ {user.display_name}'s Public Profile"
    if top_percent:
        title += f"  {top_percent}"
    if warnings > 0:
        title += "  ⚠️"

    embed = discord.Embed(title=title, color=discord.Color.dark_gold(), timestamp=datetime.now(timezone.utc))
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="🎗️ Rank", value=f"{rank}\n{points:,} pts", inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)
    embed.add_field(name="🏪 Seller", value=f"{format_stars(seller_avg)}\n{seller_sales} sale(s)", inline=True)
    embed.add_field(name="🛒 Buyer", value=f"{format_stars(buyer_avg)}\n{buyer_purchases} purchase(s)", inline=True)
    if warnings > 0:
        embed.add_field(name="⚠️ Warnings", value=f"{warnings} active warning(s)", inline=False)
    embed.set_footer(text="Adrian — Collector Profile")
    await interaction.followup.send(embed=embed, ephemeral=True)

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

@client.tree.command(name="profile", description="View your Adrian notification profile")
async def profile_cmd(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    user_id = str(interaction.user.id)

    # Fetch all preferences
    region = await db_get_user_region(user_id)
    eras = await db_get_user_eras(user_id)
    countries = await db_get_user_countries(user_id)
    forums = await db_get_user_forums(user_id)
    buyer_rating, buyer_count = await db_get_buyer_rating(user_id)
    follows = await db_get_follows(user_id)
    watchlist = await db_get_watchlist(user_id)

    # Check profile completeness
    complete = all([region, eras, countries, forums])
    status = "✅ Complete" if complete else "⚠️ Incomplete — type `/start` to finish setup"

    # Format region
    region_display = {
        "NA": "🇺🇸 North America",
        "EU": "🇪🇺 Europe",
        "both": "🌍 All Dealers"
    }.get(region, "Not set")

    # Format eras — emoji row only
    if eras:
        era_display = " ".join([ERA_EMOJIS.get(e, str(e)) for e in sorted(eras)])
    else:
        era_display = "Not set"

    # Format countries — flag row only
    if countries:
        country_display = " ".join([COUNTRY_FLAGS.get(c, c) for c in countries])
    else:
        country_display = "Not set"

    # Format forums
    forum_display = {
        "waf": "🟥 WAF",
        "usmf": "🟩 USMF",
        "both": "🟥 WAF + 🟩 USMF",
        "none": "❌ None"
    }.get(forums, "Not set")

    # Format buyer rep
    if buyer_rating:
        stars = "⭐" * int(buyer_rating) + ("✨" if buyer_rating % 1 >= 0.5 else "")
        rep_display = f"{stars} {buyer_rating}/5 · {buyer_count} sale(s)"
    else:
        rep_display = "No transactions yet"

    # Build profile code
    region_code = {"NA": "NA", "EU": "EU", "both": "ALL"}.get(region, "?")
    era_code = "".join([str(e) for e in sorted(eras)]) if eras else "?"
    country_code = "".join(sorted(countries)) if countries else "?"
    forum_code = {"waf": "W", "usmf": "U", "both": "WU", "none": "N"}.get(forums, "?")
    profile_code = f"`{region_code}-{era_code}-{country_code}-{forum_code}`"

    embed = discord.Embed(
        title=f"🎖️ {interaction.user.display_name}",
        description=f"{status}\n\n**Profile Code:** {profile_code}",
        color=discord.Color.green() if complete else discord.Color.orange(),
        timestamp=datetime.now(timezone.utc)
    )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)

    # Notification preferences section
    embed.add_field(name="📍 Region", value=region_display, inline=True)
    embed.add_field(name="📬 Forums", value=forum_display, inline=True)
    embed.add_field(name="​", value="​", inline=True)  # spacer
    embed.add_field(name="🕰️ Eras", value=era_display, inline=False)
    embed.add_field(name="🌐 Countries", value=country_display, inline=False)

    # Activity section
    embed.add_field(name="🔔 Following", value=f"{len(follows)} dealer(s)", inline=True)
    embed.add_field(name="👁️ Watchlist", value=f"{len(watchlist)} item(s)", inline=True)
    embed.add_field(name="🏅 Buyer Rep", value=rep_display, inline=True)

    embed.set_footer(text="Use /settings to update • Adrian — Discord's #1 Militaria Bot")

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

        await interaction.response.defer(ephemeral=True)

        # Check if user has agreed to Estand rules
        try:
            async with client.db.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT estand_agreed FROM user_preferences WHERE user_id=$1",
                    str(interaction.user.id)
                )
                estand_agreed = row["estand_agreed"] if row and row["estand_agreed"] else 0
        except Exception:
            estand_agreed = 0

        if not estand_agreed:
            # Show Estand rules first
            rules_embed = discord.Embed(
                title="📋 Estand Marketplace Rules",
                description=(
                    "Before creating your collector profile, please read and agree to the **Estand Marketplace Rules**:\n\n"
                    "🤝 **Honest listings** — Accurately describe items including condition and provenance.\n\n"
                    "🚫 **No prohibited items** — Illegal items or items banned by Discord\'s ToS are prohibited.\n\n"
                    "💬 **Respectful communication** — Treat all buyers and sellers with respect.\n\n"
                    "⭐ **Complete your transactions** — If you agree to a sale, follow through.\n\n"
                    "🛡️ **No scamming** — Fraud or misrepresentation will result in a permanent ban.\n\n"
                    "📊 **Honest reviews** — Only leave reviews for transactions you actually completed."
                ),
                color=discord.Color.dark_gold()
            )
            rules_embed.set_footer(text="Adrian — Estand Marketplace Rules")

            class WelcomeRulesView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=300)

                @discord.ui.button(label="✅ I Agree", style=discord.ButtonStyle.success)
                async def agree(self2, interaction2: discord.Interaction, button2: discord.ui.Button):
                    await interaction2.response.defer(ephemeral=True)
                    try:
                        async with client.db.acquire() as conn2:
                            now = int(datetime.now(timezone.utc).timestamp())
                            await conn2.execute(
                                "INSERT INTO user_preferences (user_id, estand_agreed, created_at) VALUES ($1, 1, $2) ON CONFLICT (user_id) DO UPDATE SET estand_agreed=1",
                                str(interaction2.user.id), now
                            )
                        # Grant Estand Verified role if available
                        if interaction2.guild:
                            config = await db_get_server_config(str(interaction2.guild.id))
                            estand_role_id = get_config_value(config, "estand_verified_role_id") if config else None
                            if estand_role_id:
                                estand_role = interaction2.guild.get_role(int(estand_role_id)) if estand_role_id else None
                                if estand_role:
                                    member = interaction2.guild.get_member(interaction2.user.id)
                                    if member and estand_role not in member.roles:
                                        await member.add_roles(estand_role, reason="Agreed to Estand rules via Get Started")
                    except Exception as e:
                        logger.error(f"[Welcome] Estand rules save error: {e}")
                    # Now show onboarding
                    await _show_start_onboarding(interaction2)

                @discord.ui.button(label="❌ Decline", style=discord.ButtonStyle.danger)
                async def decline(self2, interaction2: discord.Interaction, button2: discord.ui.Button):
                    await interaction2.response.defer(ephemeral=True)
                    await interaction2.edit_original_response(
                        embed=discord.Embed(
                            title="No problem!",
                            description="You can click **Get Started** again whenever you\'re ready.",
                            color=discord.Color.red()
                        ),
                        view=None
                    )

            await interaction.edit_original_response(embed=rules_embed, view=WelcomeRulesView())
        else:
            # Already agreed — go straight to onboarding
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
            await dm.send(embed=embed, view=RegionSelectView())
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
        await asyncio.sleep(3)

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
    client.add_view(RegionSelectView())
    client.add_view(EraSelectView())
    client.add_view(CountrySelectView())
    client.add_view(ForumSelectView())
    client.add_view(FinalScreenView())
    client.add_view(SellerProfileView("placeholder"))
    client.add_view(EstateRatingView("placeholder", "placeholder", "placeholder"))
    client.add_view(SetupEstateConfirmView())
    client.add_view(SetupStep3EstateView())
    client.add_view(SetupNoForumView())
    client.add_view(SetupCrossPostView())
    client.add_view(SetupPermissionsView())
    client.add_view(WelcomeView())
    logger.info("Persistent views registered.")

    # Post welcome image to all configured #adrian channels on startup
    try:
        welcome_file = os.path.join(SCRIPT_DIR, "logos", "adrian", "Adrian_welcome.png")
        if not os.path.exists(welcome_file):
            logger.warning("[Startup] Adrian_welcome.png not found — skipping welcome post")
        else:
            # Build list of all channels to refresh — deduplicated by channel ID
            channels_to_refresh = {}

            # Always include hardcoded main server channel
            main_channel = client.get_channel(CHANNEL_ID)
            if main_channel:
                channels_to_refresh[CHANNEL_ID] = (main_channel, str(main_channel.guild.id))

            # Add all configured servers
            try:
                all_servers = await db_get_all_servers()
                for server in all_servers:
                    srv_channel_id = get_config_value(server, "channel_id")
                    guild_id = get_config_value(server, "guild_id")
                    if not srv_channel_id:
                        continue
                    srv_channel_id = int(srv_channel_id)
                    srv_channel = client.get_channel(srv_channel_id)
                    if srv_channel:
                        channels_to_refresh[srv_channel_id] = (srv_channel, str(guild_id))
            except Exception as e:
                logger.warning(f"[Startup] Could not load server list: {e}")

            # Refresh each channel
            for channel_id, (channel, guild_id) in channels_to_refresh.items():
                try:
                    # Bulk delete up to 100 messages (must be under 14 days old)
                    try:
                        deleted = await channel.purge(limit=100, reason="Adrian startup cleanup")
                        logger.info(f"[Startup] Cleared {len(deleted)} messages from #{channel.name} in {channel.guild.name}")
                    except discord.Forbidden:
                        logger.warning(f"[Startup] No permission to purge #{channel.name} in {channel.guild.name}")
                    except Exception as pe:
                        logger.warning(f"[Startup] Purge failed for #{channel.name}: {pe}")

                    # Post fresh welcome message
                    welcome_msg = await channel.send(
                        file=discord.File(welcome_file, filename="Adrian_welcome.png"),
                        view=WelcomeView()
                    )
                    await db_save_server_config(guild_id, welcome_message_id=str(welcome_msg.id))
                    logger.info(f"[Startup] Welcome posted to #{channel.name} in {channel.guild.name}")

                    await asyncio.sleep(0.5)  # Small delay between servers

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
    embed.set_footer(text="Adrian — Dealer Update")

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
                logger.info("[Griffin] Buffer started — waiting 5 minutes for more changes...")
            return web.Response(text="OK", status=200)

        dealer = find_dealer(dealer_name)
        if not dealer:
            logger.warning(f"[Webhook] Unknown dealer: {dealer_name}")
            return web.Response(text="Unknown dealer", status=404)

        # Post to ALL servers' updates channels
        updates_channels = await get_all_server_channels("updates_channel_id", ADRIAN_UPDATES_CHANNEL_ID)
        if not updates_channels:
            updates_channels = [client.get_channel(CHANNEL_ID)]
        for channel in updates_channels:
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
            embed.set_footer(text="Adrian — Dealer Update")

            file = None
            if os.path.exists(logo_file):
                file = discord.File(logo_file, filename="logo.png")
                embed.set_thumbnail(url="attachment://logo.png")

            if file:
                await channel.send(file=file, embed=embed)
            else:
                await channel.send(embed=embed)
        logger.info(f"[Webhook] Alert sent for {dealer_name} to {len(updates_channels)} server(s)!")

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
    app.router.add_get("/alert", handle_webhook)
    app.router.add_post("/alert", handle_webhook)
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
            tasks.append(asyncio.create_task(onboarding_reminder_task()))
            tasks.append(asyncio.create_task(health_log_task()))
            tasks.append(asyncio.create_task(check_email_dealers()))
            tasks.append(asyncio.create_task(send_promo()))
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
