import ccxt
import pandas as pd
import numpy as np
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pybit.unified_trading import HTTP
import time
import os
import subprocess
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# ======================== Configuration ========================
# Constants
# Constants (GitHub Actions compatible)

GITHUB_WORKSPACE = os.getenv('GITHUB_WORKSPACE', os.path.dirname(os.path.abspath(__file__)))
TRADE_FILE = os.path.join(GITHUB_WORKSPACE, "active_trade.json")
TRADE_STATE_FILE = os.path.join(GITHUB_WORKSPACE, "trade_state.txt")
ALERT_PATH = os.path.join(GITHUB_WORKSPACE, "alert.mp3") if os.path.exists(os.path.join(GITHUB_WORKSPACE, "alert.mp3")) else None
SCAN_INTERVAL = 600  # 15 minutes in seconds


# Email Configuration
sender = os.getenv('EMAIL_SENDER')
recipients = os.getenv('EMAIL_RECIPIENTS', '').split(',')
password = os.getenv('EMAIL_PASSWORD')

# Bybit API Configuration
session = HTTP(
    api_key=os.getenv('BYBIT_API_KEY'),
    api_secret=os.getenv('BYBIT_API_SECRET'),
    demo=True
)



# Initialize the exchange
exchange = ccxt.bitget()

# Symbol mapping
symbol_mapping = {
    '1000000MOG/USDT:USDT': '1000000MOGUSDT',
    '10000ELON/USDT:USDT': '10000ELONUSDT',
    '10000WHY/USDT:USDT': '10000WHYUSDT',
    '1000BONK/USDC:USDC': '1000BONKUSDC:USDC',
    '1000BONK/USDT:USDT': '1000BONKUSDT',
    '1000CAT/USDT:USDT': '1000CATUSDT',
    '1000RATS/USDT:USDT': '1000RATSUSDT',
    '1000SATS/USDT:USDT': '1000SATSUSDT',
    '1000XEC/USDT:USDT': '1000XECUSDT',
    '1INCH/USDT:USDT': '1INCHUSDT',
    '1MBABYDOGE/USDT:USDT': '1MBABYDOGEUSDT',
    '1MCHEEMS/USDT:USDT': '1MCHEEMSUSDT',
    'AAVE/USDC:USDC': 'AAVEUSDC:USDC',
    'AAVE/USDT:USDT': 'AAVEUSDT',
    'ACE/USDT:USDT': 'ACEUSDT',
    'ACH/USDT:USDT': 'ACHUSDT',
    'ACT/USDC:USDC': 'ACTUSDC:USDC',
    'ACT/USDT:USDT': 'ACTUSDT',
    'ACX/USDT:USDT': 'ACXUSDT',
    'ADA/USD:ADA': 'ADAUSD:ADA',
    'ADA/USDC:USDC': 'ADAUSDC:USDC',
    'ADA/USDT:USDT': 'ADAUSDT',
    'AERO/USDT:USDT': 'AEROUSDT',
    'AEVO/USDC:USDC': 'AEVOUSDC:USDC',
    'AEVO/USDT:USDT': 'AEVOUSDT',
    'AGI/USDT:USDT': 'AGIUSDT',
    'AGLD/USDT:USDT': 'AGLDUSDT',
    'AI/USDT:USDT': 'AIUSDT',
    'AI16Z/USDT:USDT': 'AI16ZUSDT',
    'AIOZ/USDT:USDT': 'AIOZUSDT',
    'AIXBT/USDT:USDT': 'AIXBTUSDT',
    'AKT/USDT:USDT': 'AKTUSDT',
    'ALCH/USDT:USDT': 'ALCHUSDT',
    'ALGO/USDC:USDC': 'ALGOUSDC:USDC',
    'ALGO/USDT:USDT': 'ALGOUSDT',
    'ALICE/USDT:USDT': 'ALICEUSDT',
    'ALPACA/USDT:USDT': 'ALPACAUSDT',
    'ALPHA/USDT:USDT': 'ALPHAUSDT',
    'ALT/USDT:USDT': 'ALTUSDT',
    'AMP/USDT:USDT': 'AMPUSDT',
    'ANIME/USDT:USDT': 'ANIMEUSDT',
    'ANKR/USDT:USDT': 'ANKRUSDT',
    'APE/USDT:USDT': 'APEUSDT',
    'API3/USDT:USDT': 'API3USDT',
    'APT/USDC:USDC': 'APTUSDC:USDC',
    'APT/USDT:USDT': 'APTUSDT',
    'AR/USDT:USDT': 'ARUSDT',
    'ARB/USDC:USDC': 'ARBUSDC:USDC',
    'ARB/USDT:USDT': 'ARBUSDT',
    'ARC/USDT:USDT': 'ARCUSDT',
    'ARK/USDT:USDT': 'ARKUSDT',
    'ARKM/USDT:USDT': 'ARKMUSDT',
    'ARPA/USDT:USDT': 'ARPAUSDT',
    'ASTR/USDT:USDT': 'ASTRUSDT',
    'ATA/USDT:USDT': 'ATAUSDT',
    'ATH/USDT:USDT': 'ATHUSDT',
    'ATOM/USDT:USDT': 'ATOMUSDT',
    'AUCTION/USDT:USDT': 'AUCTIONUSDT',
    'AUDIO/USDT:USDT': 'AUDIOUSDT',
    'AVA/USDT:USDT': 'AVAUSDT',
    'AVAAI/USDT:USDT': 'AVAAIUSDT',
    'AVAIL/USDT:USDT': 'AVAILUSDT',
    'AVAX/USDC:USDC': 'AVAXUSDC:USDC',
    'AVAX/USDT:USDT': 'AVAXUSDT',
    'AVL/USDT:USDT': 'AVLUSDT',
    'AXL/USDT:USDT': 'AXLUSDT',
    'AXS/USDT:USDT': 'AXSUSDT',
    'B3/USDT:USDT': 'B3USDT',
    'BAKE/USDT:USDT': 'BAKEUSDT',
    'BAN/USDT:USDT': 'BANUSDT',
    'BANANA/USDT:USDT': 'BANANAUSDT',
    'BANANAS31/USDT:USDT': 'BANANAS31USDT',
    'BAND/USDT:USDT': 'BANDUSDT',
    'BAT/USDT:USDT': 'BATUSDT',
    'BB/USDT:USDT': 'BBUSDT',
    'BCH/USDC:USDC': 'BCHUSDC:USDC',
    'BCH/USDT:USDT': 'BCHUSDT',
    'BEAM/USDT:USDT': 'BEAMUSDT',
    'BEL/USDT:USDT': 'BELUSDT',
    'BERA/USDC:USDC': 'BERAUSDC:USDC',
    'BERA/USDT:USDT': 'BERAUSDT',
    'BGB/USDT:USDT': 'BGBUSDT',
    'BGSC/USDT:USDT': 'BGSCUSDT',
    'BICO/USDT:USDT': 'BICOUSDT',
    'BID/USDT:USDT': 'BIDUSDT',
    'BIGTIME/USDT:USDT': 'BIGTIMEUSDT',
    'BIO/USDT:USDT': 'BIOUSDT',
    'BLAST/USDT:USDT': 'BLASTUSDT',
    'BLUR/USDT:USDT': 'BLURUSDT',
    'BMT/USDT:USDT': 'BMTUSDT',
    'BNB/USDC:USDC': 'BNBUSDC:USDC',
    'BNB/USDT:USDT': 'BNBUSDT',
    'BNT/USDT:USDT': 'BNTUSDT',
    'BOME/USDC:USDC': 'BOMEUSDC:USDC',
    'BOME/USDT:USDT': 'BOMEUSDT',
    'BR/USDT:USDT': 'BRUSDT',
    'BRETT/USDT:USDT': 'BRETTUSDT',
    'BROCCOLI/USDT:USDT': 'BROCCOLIUSDT',
    'BROCCOLIF3B/USDT:USDT': 'BROCCOLIF3BUSDT',
    'BSV/USDT:USDT': 'BSVUSDT',
    'BSW/USDT:USDT': 'BSWUSDT',
    'BTC/USD:BTC': 'BTCUSD:BTC',
    'BTC/USDC:USDC': 'BTCUSDC:USDC',
    'BTC/USDT:USDT': 'BTCUSDT',
    'C98/USDT:USDT': 'C98USDT',
    'CAKE/USDT:USDT': 'CAKEUSDT',
    'CARV/USDT:USDT': 'CARVUSDT',
    'CATI/USDC:USDC': 'CATIUSDC:USDC',
    'CATI/USDT:USDT': 'CATIUSDT',
    'CELO/USDT:USDT': 'CELOUSDT',
    'CELR/USDT:USDT': 'CELRUSDT',
    'CETUS/USDT:USDT': 'CETUSUSDT',
    'CFX/USDT:USDT': 'CFXUSDT',
    'CGPT/USDT:USDT': 'CGPTUSDT',
    'CHESS/USDT:USDT': 'CHESSUSDT',
    'CHILLGUY/USDT:USDT': 'CHILLGUYUSDT',
    'CHR/USDT:USDT': 'CHRUSDT',
    'CHZ/USDT:USDT': 'CHZUSDT',
    'CKB/USDT:USDT': 'CKBUSDT',
    'CLOUD/USDT:USDT': 'CLOUDUSDT',
    'COMP/USDT:USDT': 'COMPUSDT',
    'COOKIE/USDT:USDT': 'COOKIEUSDT',
    'CORE/USDT:USDT': 'COREUSDT',
    'COS/USDT:USDT': 'COSUSDT',
    'COTI/USDT:USDT': 'COTIUSDT',
    'COW/USDT:USDT': 'COWUSDT',
    'CRO/USDT:USDT': 'CROUSDT',
    'CRV/USDC:USDC': 'CRVUSDC:USDC',
    'CRV/USDT:USDT': 'CRVUSDT',
    'CTC/USDT:USDT': 'CTCUSDT',
    'CTSI/USDT:USDT': 'CTSIUSDT',
    'CVC/USDT:USDT': 'CVCUSDT',
    'CVX/USDT:USDT': 'CVXUSDT',
    'CYBER/USDT:USDT': 'CYBERUSDT',
    'DBR/USDT:USDT': 'DBRUSDT',
    'DEEP/USDT:USDT': 'DEEPUSDT',
    'DENT/USDT:USDT': 'DENTUSDT',
    'DEXE/USDT:USDT': 'DEXEUSDT',
    'DF/USDT:USDT': 'DFUSDT',
    'DIA/USDT:USDT': 'DIAUSDT',
    'DOG/USDT:USDT': 'DOGUSDT',
    'DOGE/USD:DOGE': 'DOGEUSD:DOGE',
    'DOGE/USDC:USDC': 'DOGEUSDC:USDC',
    'DOGE/USDT:USDT': 'DOGEUSDT',
    'DOGS/USDT:USDT': 'DOGSUSDT',
    'DOT/USD:DOT': 'DOTUSD:DOT',
    'DOT/USDC:USDC': 'DOTUSDC:USDC',
    'DOT/USDT:USDT': 'DOTUSDT',
    'DRIFT/USDT:USDT': 'DRIFTUSDT',
    'DUCK/USDT:USDT': 'DUCKUSDT',
    'DYDX/USDT:USDT': 'DYDXUSDT',
    'DYM/USDT:USDT': 'DYMUSDT',
    'DegenReborn/USDT:USDT': 'DegenRebornUSDT',
    'EGLD/USDT:USDT': 'EGLDUSDT',
    'EIGEN/USDC:USDC': 'EIGENUSDC:USDC',
    'EIGEN/USDT:USDT': 'EIGENUSDT',
    'ELX/USDT:USDT': 'ELXUSDT',
    'ENA/USDC:USDC': 'ENAUSDC:USDC',
    'ENA/USDT:USDT': 'ENAUSDT',
    'ENJ/USDT:USDT': 'ENJUSDT',
    'ENS/USDC:USDC': 'ENSUSDC:USDC',
    'ENS/USDT:USDT': 'ENSUSDT',
    'EOS/USD:EOS': 'EOSUSD:EOS',
    'EOS/USDT:USDT': 'EOSUSDT',
    'EPIC/USDT:USDT': 'EPICUSDT',
    'ETC/USDC:USDC': 'ETCUSDC:USDC',
    'ETC/USDT:USDT': 'ETCUSDT',
    'ETH/USD:ETH': 'ETHUSD:ETH',
    'ETH/USDC:USDC': 'ETHUSDC:USDC',
    'ETH/USDT:USDT': 'ETHUSDT',
    'ETHFI/USDC:USDC': 'ETHFIUSDC:USDC',
    'ETHFI/USDT:USDT': 'ETHFIUSDT',
    'ETHW/USDT:USDT': 'ETHWUSDT',
    'FARTCOIN/USDC:USDC': 'FARTCOINUSDC:USDC',
    'FARTCOIN/USDT:USDT': 'FARTCOINUSDT',
    'FET/USDT:USDT': 'FETUSDT',
    'FIDA/USDT:USDT': 'FIDAUSDT',
    'FIL/USDC:USDC': 'FILUSDC:USDC',
    'FIL/USDT:USDT': 'FILUSDT',
    'FIO/USDT:USDT': 'FIOUSDT',
    'FLM/USDT:USDT': 'FLMUSDT',
    'FLOKI/USDT:USDT': 'FLOKIUSDT',
    'FLOW/USDT:USDT': 'FLOWUSDT',
    'FLUX/USDT:USDT': 'FLUXUSDT',
    'FORM/USDT:USDT': 'FORMUSDT',
    'FORTH/USDT:USDT': 'FORTHUSDT',
    'FOXY/USDT:USDT': 'FOXYUSDT',
    'FTN/USDT:USDT': 'FTNUSDT',
    'FUEL/USDT:USDT': 'FUELUSDT',
    'FUN/USDT:USDT': 'FUNUSDT',
    'FWOG/USDT:USDT': 'FWOGUSDT',
    'FXS/USDT:USDT': 'FXSUSDT',
    'G/USDT:USDT': 'GUSDT',
    'GALA/USDC:USDC': 'GALAUSDC:USDC',
    'GALA/USDT:USDT': 'GALAUSDT',
    'GAS/USDT:USDT': 'GASUSDT',
    'GHST/USDT:USDT': 'GHSTUSDT',
    'GIGA/USDT:USDT': 'GIGAUSDT',
    'GLM/USDT:USDT': 'GLMUSDT',
    'GMT/USDT:USDT': 'GMTUSDT',
    'GMX/USDT:USDT': 'GMXUSDT',
    'GNO/USDT:USDT': 'GNOUSDT',
    'GOAT/USDT:USDT': 'GOATUSDT',
    'GODS/USDT:USDT': 'GODSUSDT',
    'GPS/USDT:USDT': 'GPSUSDT',
    'GRASS/USDT:USDT': 'GRASSUSDT',
    'GRIFFAIN/USDT:USDT': 'GRIFFAINUSDT',
    'GRT/USDT:USDT': 'GRTUSDT',
    'GTC/USDT:USDT': 'GTCUSDT',
    'GUN/USDT:USDT': 'GUNUSDT',
    'HBAR/USDC:USDC': 'HBARUSDC:USDC',
    'HBAR/USDT:USDT': 'HBARUSDT',
    'HEI/USDT:USDT': 'HEIUSDT',
    'HIFI/USDT:USDT': 'HIFIUSDT',
    'HIPPO/USDT:USDT': 'HIPPOUSDT',
    'HIVE/USDT:USDT': 'HIVEUSDT',
    'HMSTR/USDT:USDT': 'HMSTRUSDT',
    'HNT/USDT:USDT': 'HNTUSDT',
    'HOOK/USDT:USDT': 'HOOKUSDT',
    'HOT/USDT:USDT': 'HOTUSDT',
    'HYPE/USDT:USDT': 'HYPEUSDT',
    'ICP/USDT:USDT': 'ICPUSDT',
    'ICX/USDT:USDT': 'ICXUSDT',
    'ID/USDT:USDT': 'IDUSDT',
    'IMX/USDT:USDT': 'IMXUSDT',
    'INJ/USDT:USDT': 'INJUSDT',
    'IO/USDT:USDT': 'IOUSDT',
    'IOST/USDT:USDT': 'IOSTUSDT',
    'IOTA/USDT:USDT': 'IOTAUSDT',
    'IOTX/USDT:USDT': 'IOTXUSDT',
    'IP/USDC:USDC': 'IPUSDC:USDC',
    'IP/USDT:USDT': 'IPUSDT',
    'J/USDT:USDT': 'JUSDT',
    'JAILSTOOL/USDT:USDT': 'JAILSTOOLUSDT',
    'JASMY/USDT:USDT': 'JASMYUSDT',
    'JOE/USDT:USDT': 'JOEUSDT',
    'JTO/USDT:USDT': 'JTOUSDT',
    'JUP/USDT:USDT': 'JUPUSDT',
    'KAIA/USDT:USDT': 'KAIAUSDT',
    'KAITO/USDC:USDC': 'KAITOUSDC:USDC',
    'KAITO/USDT:USDT': 'KAITOUSDT',
    'KAS/USDT:USDT': 'KASUSDT',
    'KAVA/USDT:USDT': 'KAVAUSDT',
    'KDA/USDT:USDT': 'KDAUSDT',
    'KILO/USDT:USDT': 'KILOUSDT',
    'KMNO/USDT:USDT': 'KMNOUSDT',
    'KNC/USDT:USDT': 'KNCUSDT',
    'KOMA/USDT:USDT': 'KOMAUSDT',
    'KSM/USDT:USDT': 'KSMUSDT',
    'LAYER/USDT:USDT': 'LAYERUSDT',
    'LDO/USDT:USDT': 'LDOUSDT',
    'LEVER/USDT:USDT': 'LEVERUSDT',
    'LINK/USD:LINK': 'LINKUSD:LINK',
    'LINK/USDC:USDC': 'LINKUSDC:USDC',
    'LINK/USDT:USDT': 'LINKUSDT',
    'LISTA/USDT:USDT': 'LISTAUSDT',
    'LOKA/USDT:USDT': 'LOKAUSDT',
    'LOOKS/USDT:USDT': 'LOOKSUSDT',
    'LPT/USDT:USDT': 'LPTUSDT',
    'LQTY/USDT:USDT': 'LQTYUSDT',
    'LRC/USDT:USDT': 'LRCUSDT',
    'LSK/USDT:USDT': 'LSKUSDT',
    'LTC/USD:LTC': 'LTCUSD:LTC',
    'LTC/USDC:USDC': 'LTCUSDC:USDC',
    'LTC/USDT:USDT': 'LTCUSDT',
    'LUCE/USDT:USDT': 'LUCEUSDT',
    'LUMIA/USDT:USDT': 'LUMIAUSDT',
    'LUNA/USDT:USDT': 'LUNAUSDT',
    'LUNC/USDT:USDT': 'LUNCUSDT',
    'MAGIC/USDT:USDT': 'MAGICUSDT',
    'MAJOR/USDT:USDT': 'MAJORUSDT',
    'MANA/USDT:USDT': 'MANAUSDT',
    'MANTA/USDT:USDT': 'MANTAUSDT',
    'MASK/USDT:USDT': 'MASKUSDT',
    'MAV/USDT:USDT': 'MAVUSDT',
    'MAX/USDT:USDT': 'MAXUSDT',
    'MBOX/USDT:USDT': 'MBOXUSDT',
    'ME/USDC:USDC': 'MEUSDC:USDC',
    'ME/USDT:USDT': 'MEUSDT',
    'MELANIA/USDT:USDT': 'MELANIAUSDT',
    'MEME/USDT:USDT': 'MEMEUSDT',
    'MEMEFI/USDT:USDT': 'MEMEFIUSDT',
    'MERL/USDT:USDT': 'MERLUSDT',
    'METIS/USDT:USDT': 'METISUSDT',
    'MEW/USDT:USDT': 'MEWUSDT',
    'MINA/USDT:USDT': 'MINAUSDT',
    'MKR/USDT:USDT': 'MKRUSDT',
    'MLN/USDT:USDT': 'MLNUSDT',
    'MOCA/USDT:USDT': 'MOCAUSDT',
    'MOODENG/USDT:USDT': 'MOODENGUSDT',
    'MORPHO/USDT:USDT': 'MORPHOUSDT',
    'MOVE/USDT:USDT': 'MOVEUSDT',
    'MOVR/USDT:USDT': 'MOVRUSDT',
    'MTL/USDT:USDT': 'MTLUSDT',
    'MUBARAK/USDT:USDT': 'MUBARAKUSDT',
    'MYRO/USDT:USDT': 'MYROUSDT',
    'NAVX/USDT:USDT': 'NAVXUSDT',
    'NC/USDT:USDT': 'NCUSDT',
    'NEAR/USDC:USDC': 'NEARUSDC:USDC',
    'NEAR/USDT:USDT': 'NEARUSDT',
    'NEIROCTO/USDT:USDT': 'NEIROCTOUSDT',
    'NEIROETH/USDT:USDT': 'NEIROETHUSDT',
    'NEO/USDC:USDC': 'NEOUSDC:USDC',
    'NEO/USDT:USDT': 'NEOUSDT',
    'NFP/USDT:USDT': 'NFPUSDT',
    'NIL/USDT:USDT': 'NILUSDT',
    'NKN/USDT:USDT': 'NKNUSDT',
    'NMR/USDT:USDT': 'NMRUSDT',
    'NOT/USDC:USDC': 'NOTUSDC:USDC',
    'NOT/USDT:USDT': 'NOTUSDT',
    'NS/USDT:USDT': 'NSUSDT',
    'NTRN/USDT:USDT': 'NTRNUSDT',
    'NULS/USDT:USDT': 'NULSUSDT',
    'OBT/USDT:USDT': 'OBTUSDT',
    'OG/USDT:USDT': 'OGUSDT',
    'OGN/USDT:USDT': 'OGNUSDT',
    'OIK/USDT:USDT': 'OIKUSDT',
    'OL/USDT:USDT': 'OLUSDT',
    'OM/USDT:USDT': 'OMUSDT',
    'OMNI1/USDT:USDT': 'OMNI1USDT',
    'ONDO/USDC:USDC': 'ONDOUSDC:USDC',
    'ONDO/USDT:USDT': 'ONDOUSDT',
    'ONE/USDT:USDT': 'ONEUSDT',
    'ONG/USDT:USDT': 'ONGUSDT',
    'ONT/USDT:USDT': 'ONTUSDT',
    'OP/USDC:USDC': 'OPUSDC:USDC',
    'OP/USDT:USDT': 'OPUSDT',
    'ORCA/USDT:USDT': 'ORCAUSDT',
    'ORDER/USDT:USDT': 'ORDERUSDT',
    'ORDI/USDC:USDC': 'ORDIUSDC:USDC',
    'ORDI/USDT:USDT': 'ORDIUSDT',
    'OXT/USDT:USDT': 'OXTUSDT',
    'PARTI/USDT:USDT': 'PARTIUSDT',
    'PAXG/USDT:USDT': 'PAXGUSDT',
    'PEAQ/USDT:USDT': 'PEAQUSDT',
    'PENDLE/USDT:USDT': 'PENDLEUSDT',
    'PENGU/USDT:USDT': 'PENGUUSDT',
    'PEOPLE/USDT:USDT': 'PEOPLEUSDT',
    'PEPE/USDC:USDC': 'PEPEUSDC:USDC',
    'PEPE/USDT:USDT': 'PEPEUSDT',
    'PHA/USDT:USDT': 'PHAUSDT',
    'PHB/USDT:USDT': 'PHBUSDT',
    'PI/USDC:USDC': 'PIUSDC:USDC',
    'PI/USDT:USDT': 'PIUSDT',
    'PIPPIN/USDT:USDT': 'PIPPINUSDT',
    'PIXEL/USDT:USDT': 'PIXELUSDT',
    'PLUME/USDT:USDT': 'PLUMEUSDT',
    'PNUT/USDC:USDC': 'PNUTUSDC:USDC',
    'PNUT/USDT:USDT': 'PNUTUSDT',
    'POL/USDC:USDC': 'POLUSDC:USDC',
    'POL/USDT:USDT': 'POLUSDT',
    'POLYX/USDT:USDT': 'POLYXUSDT',
    'PONKE/USDT:USDT': 'PONKEUSDT',
    'POPCAT/USDC:USDC': 'POPCATUSDC:USDC',
    'POPCAT/USDT:USDT': 'POPCATUSDT',
    'PORTAL/USDT:USDT': 'PORTALUSDT',
    'POWR/USDT:USDT': 'POWRUSDT',
    'PRCL/USDT:USDT': 'PRCLUSDT',
    'PROM/USDT:USDT': 'PROMUSDT',
    'PROS/USDT:USDT': 'PROSUSDT',
    'PUFFER/USDT:USDT': 'PUFFERUSDT',
    'PUMP/USDT:USDT': 'PUMPUSDT',
    'PYR/USDT:USDT': 'PYRUSDT',
    'PYTH/USDT:USDT': 'PYTHUSDT',
    'QKC/USDT:USDT': 'QKCUSDT',
    'QNT/USDT:USDT': 'QNTUSDT',
    'QTUM/USDT:USDT': 'QTUMUSDT',
    'QUICK/USDT:USDT': 'QUICKUSDT',
    'RAD/USDT:USDT': 'RADUSDT',
    'RARE/USDT:USDT': 'RAREUSDT',
    'RAY/USDT:USDT': 'RAYUSDT',
    'RDNT/USDT:USDT': 'RDNTUSDT',
    'RED/USDT:USDT': 'REDUSDT',
    'REI/USDT:USDT': 'REIUSDT',
    'RENDER/USDT:USDT': 'RENDERUSDT',
    'REZ/USDT:USDT': 'REZUSDT',
    'ROAM/USDT:USDT': 'ROAMUSDT',
    'RON/USDT:USDT': 'RONUSDT',
    'ROSE/USDT:USDT': 'ROSEUSDT',
    'RPL/USDT:USDT': 'RPLUSDT',
    'RSR/USDT:USDT': 'RSRUSDT',
    'RSS3/USDT:USDT': 'RSS3USDT',
    'RUNE/USDT:USDT': 'RUNEUSDT',
    'RVN/USDT:USDT': 'RVNUSDT',
    'S/USDT:USDT': 'SUSDT',
    'SAFE/USDT:USDT': 'SAFEUSDT',
    'SAGA/USDT:USDT': 'SAGAUSDT',
    'SAND/USDT:USDT': 'SANDUSDT',
    'SANTOS/USDT:USDT': 'SANTOSUSDT',
    'SCR/USDT:USDT': 'SCRUSDT',
    'SCRT/USDT:USDT': 'SCRTUSDT',
    'SEI/USDT:USDT': 'SEIUSDT',
    'SERAPH/USDT:USDT': 'SERAPHUSDT',
    'SFP/USDT:USDT': 'SFPUSDT',
    'SHELL/USDT:USDT': 'SHELLUSDT',
    'SHIB/USDC:USDC': 'SHIBUSDC:USDC',
    'SHIB/USDT:USDT': 'SHIBUSDT',
    'SIREN/USDT:USDT': 'SIRENUSDT',
    'SKL/USDT:USDT': 'SKLUSDT',
    'SLERF/USDT:USDT': 'SLERFUSDT',
    'SNT/USDT:USDT': 'SNTUSDT',
    'SNX/USDT:USDT': 'SNXUSDT',
    'SOL/USD:SOL': 'SOLUSD:SOL',
    'SOL/USDC:USDC': 'SOLUSDC:USDC',
    'SOL/USDT:USDT': 'SOLUSDT',
    'SOLV/USDT:USDT': 'SOLVUSDT',
    'SONIC/USDT:USDT': 'SONICUSDT',
    'SPELL/USDT:USDT': 'SPELLUSDT',
    'SPX/USDT:USDT': 'SPXUSDT',
    'SSV/USDT:USDT': 'SSVUSDT',
    'STEEM/USDT:USDT': 'STEEMUSDT',
    'STG/USDT:USDT': 'STGUSDT',
    'STO/USDT:USDT': 'STOUSDT',
    'STORJ/USDT:USDT': 'STORJUSDT',
    'STPT/USDT:USDT': 'STPTUSDT',
    'STRK/USDC:USDC': 'STRKUSDC:USDC',
    'STRK/USDT:USDT': 'STRKUSDT',
    'STX/USDC:USDC': 'STXUSDC:USDC',
    'STX/USDT:USDT': 'STXUSDT',
    'SUI/USDC:USDC': 'SUIUSDC:USDC',
    'SUI/USDT:USDT': 'SUIUSDT',
    'SUN/USDT:USDT': 'SUNUSDT',
    'SUNDOG/USDT:USDT': 'SUNDOGUSDT',
    'SUPER/USDT:USDT': 'SUPERUSDT',
    'SUSHI/USDT:USDT': 'SUSHIUSDT',
    'SWARMS/USDT:USDT': 'SWARMSUSDT',
    'SWEAT/USDT:USDT': 'SWEATUSDT',
    'SWELL/USDT:USDT': 'SWELLUSDT',
    'SXP/USDT:USDT': 'SXPUSDT',
    'SYN/USDT:USDT': 'SYNUSDT',
    'SYS/USDT:USDT': 'SYSUSDT',
    'T/USDT:USDT': 'TUSDT',
    'TAIKO/USDT:USDT': 'TAIKOUSDT',
    'TAO/USDT:USDT': 'TAOUSDT',
    'THE/USDT:USDT': 'THEUSDT',
    'THETA/USDT:USDT': 'THETAUSDT',
    'TIA/USDC:USDC': 'TIAUSDC:USDC',
    'TIA/USDT:USDT': 'TIAUSDT',
    'TLM/USDT:USDT': 'TLMUSDT',
    'TNSR/USDT:USDT': 'TNSRUSDT',
    'TON/USDC:USDC': 'TONUSDC:USDC',
    'TON/USDT:USDT': 'TONUSDT',
    'TOSHI/USDT:USDT': 'TOSHIUSDT',
    'TRB/USDT:USDT': 'TRBUSDT',
    'TROY/USDT:USDT': 'TROYUSDT',
    'TRU/USDT:USDT': 'TRUUSDT',
    'TRUMP/USDC:USDC': 'TRUMPUSDC:USDC',
    'TRUMP/USDT:USDT': 'TRUMPUSDT',
    'TRX/USD:TRX': 'TRXUSD:TRX',
    'TRX/USDC:USDC': 'TRXUSDC:USDC',
    'TRX/USDT:USDT': 'TRXUSDT',
    'TSTBSC/USDC:USDC': 'TSTBSCUSDC:USDC',
    'TSTBSC/USDT:USDT': 'TSTBSCUSDT',
    'TURBO/USDT:USDT': 'TURBOUSDT',
    'TUT/USDT:USDT': 'TUTUSDT',
    'UMA/USDT:USDT': 'UMAUSDT',
    'UNI/USDC:USDC': 'UNIUSDC:USDC',
    'UNI/USDT:USDT': 'UNIUSDT',
    'USDC/USDT:USDT': 'USDCUSDT',
    'USTC/USDT:USDT': 'USTCUSDT',
    'USUAL/USDT:USDT': 'USUALUSDT',
    'UXLINK/USDT:USDT': 'UXLINKUSDT',
    'VANA/USDC:USDC': 'VANAUSDC:USDC',
    'VANA/USDT:USDT': 'VANAUSDT',
    'VANRY/USDT:USDT': 'VANRYUSDT',
    'VELO/USDT:USDT': 'VELOUSDT',
    'VELODROME/USDT:USDT': 'VELODROMEUSDT',
    'VET/USDT:USDT': 'VETUSDT',
    'VIC/USDT:USDT': 'VICUSDT',
    'VIDT/USDT:USDT': 'VIDTUSDT',
    'VINE/USDT:USDT': 'VINEUSDT',
    'VIRTUAL/USDT:USDT': 'VIRTUALUSDT',
    'VOXEL/USDT:USDT': 'VOXELUSDT',
    'VTHO/USDT:USDT': 'VTHOUSDT',
    'VVV/USDT:USDT': 'VVVUSDT',
    'W/USDT:USDT': 'WUSDT',
    'WAL/USDT:USDT': 'WALUSDT',
    'WAVES/USDT:USDT': 'WAVESUSDT',
    'WAXP/USDT:USDT': 'WAXPUSDT',
    'WIF/USDC:USDC': 'WIFUSDC:USDC',
    'WIF/USDT:USDT': 'WIFUSDT',
    'WLD/USDC:USDC': 'WLDUSDC:USDC',
    'WLD/USDT:USDT': 'WLDUSDT',
    'WOO/USDT:USDT': 'WOOUSDT',
    'X/USDT:USDT': 'XUSDT',
    'XAI/USDT:USDT': 'XAIUSDT',
    'XAUT/USDT:USDT': 'XAUTUSDT',
    'XCN/USDT:USDT': 'XCNUSDT',
    'XDC/USDT:USDT': 'XDCUSDT',
    'XION/USDT:USDT': 'XIONUSDT',
    'XLM/USDC:USDC': 'XLMUSDC:USDC',
    'XLM/USDT:USDT': 'XLMUSDT',
    'XRP/USD:XRP': 'XRPUSD:XRP',
    'XRP/USDC:USDC': 'XRPUSDC:USDC',
    'XRP/USDT:USDT': 'XRPUSDT',
    'XTZ/USDT:USDT': 'XTZUSDT',
    'XVG/USDT:USDT': 'XVGUSDT',
    'XVS/USDT:USDT': 'XVSUSDT',
    'YGG/USDT:USDT': 'YGGUSDT',
    'ZEN/USDT:USDT': 'ZENUSDT',
    'ZEREBRO/USDT:USDT': 'ZEREBROUSDT',
    'ZETA/USDT:USDT': 'ZETAUSDT',
    'ZIL/USDT:USDT': 'ZILUSDT',
    'ZK/USDT:USDT': 'ZKUSDT',
    'ZKJ/USDT:USDT': 'ZKJUSDT',
    'ZRC/USDT:USDT': 'ZRCUSDT',
    'ZRO/USDT:USDT': 'ZROUSDT',
    'ZRX/USDT:USDT': 'ZRXUSDT'
}
symbols = list(symbol_mapping.keys())
symbol_mapping_inv = {v: k for k, v in symbol_mapping.items()}  # <-- ADD THIS LINE

# Trading Parameters
TRADE_AMOUNT_USDT = 50
STOP_LOSS_PERCENT = 2
TAKE_PROFIT_PERCENT = 20

# Indicator Parameters
timeframe_15m = '15m'
timeframe_1h = '1h'
limit = 500
ema_fast_length = 38
ema_slow_length = 62
ema_trend_length = 200
H_BANDWIDTH = 8.0
MULTIPLIER = 3.0
REPAINT = True

# ======================== Core Functions ========================

def calculate_atr(df, length=14):
    """Calculate ATR for a given dataframe"""
    df['prev_close'] = df['close'].shift(1)
    df['hl'] = df['high'] - df['low']
    df['hc'] = abs(df['high'] - df['prev_close'])
    df['lc'] = abs(df['low'] - df['prev_close'])
    df['tr'] = df[['hl', 'hc', 'lc']].max(axis=1)
    df['atr'] = df['tr'].rolling(window=length).mean()
    return df

def get_atr_levels(symbol, timeframe='15m', length=14):
    """Get current ATR and projected levels"""
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=length+1)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df = calculate_atr(df, length)
    
    last_close = df['close'].iloc[-2]  # Last fully closed candle
    last_atr = df['atr'].iloc[-2]      # Last fully closed ATR
    
    return {
        'upper': last_close + (2 * last_atr),
        'lower': last_close - (2 * last_atr),
        'atr': last_atr
    }



def play_alert():
    """Play alert sound for network issues"""
    if os.path.exists(ALERT_PATH):
        subprocess.Popen(["mpv", "--no-video", ALERT_PATH])
        print("Alert played")
    else:
        print(f"Alert file not found at {ALERT_PATH}")





def save_active_trade(symbol, entry_price, sl_price, tp_price, side):
    """Save trade details to file with error handling"""
    trade_data = {
        'symbol': symbol,
        'entry_price': entry_price,
        'sl_price': sl_price,
        'tp_price': tp_price,
        'side': side,
        'opened_at': pd.Timestamp.now().isoformat()
    }
    try:
        with open(TRADE_FILE, 'w') as f:
            json.dump(trade_data, f)
        print(f"Trade saved to {TRADE_FILE}")
    except Exception as e:
        print(f"Error saving trade: {e}")
        raise
        
        
        

def clear_active_trade():
    """Remove trade file with confirmation"""
    try:
        if os.path.exists(TRADE_FILE):
            os.remove(TRADE_FILE)
            print(f"Cleared {TRADE_FILE}")
    except Exception as e:
        print(f"Error clearing trade: {e}")
        raise





def initialize_trade_state():
    """Create file with 'ENTRY' if it doesn't exist"""
    if not os.path.exists(TRADE_STATE_FILE):
        with open(TRADE_STATE_FILE, 'w') as f:
            f.write("ENTRY")

def get_trade_state():
    """Read the current trade state"""
    try:
        with open(TRADE_STATE_FILE, 'r') as f:
            return f.read().strip().upper()
    except:
        return "ENTRY"  # Default to ENTRY if error occurs

def set_trade_state(state):

    """Enhanced with email notifications"""
    old_state = get_trade_state()
    if old_state != state:
        send_email(
            subject=f"🔄 Trade State Changed to {state}",
            body=f"Trading is now {'PAUSED' if state == 'MANAGE' else 'ACTIVE'}"
        )
    """Update the trade state (ENTRY/MANAGE)"""
    valid_states = ["ENTRY", "MANAGE"]
    if state.upper() in valid_states:
        with open(TRADE_STATE_FILE, 'w') as f:
            f.write(state.upper())
    else:
        print(f"Invalid state: {state}. Must be 'ENTRY' or 'MANAGE'")





def get_active_trade():
    """Check for existing active trade"""
    if os.path.exists(TRADE_FILE):
        try:
            with open(TRADE_FILE, 'r') as f:
                trade_data = json.load(f)
            
            # Verify the trade still exists
            position = get_open_position(symbol_mapping.get(trade_data['symbol']))
            if position:
                return trade_data
            else:
                clear_active_trade()
        except Exception as e:
            print(f"Error loading trade data: {e}")
            clear_active_trade()
    return None

def send_email(subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipients, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

def gauss(x, h):
    """Gaussian window function for band calculation"""
    return np.exp(-(x ** 2) / (h ** 2 * 2))

def calculate_nwe(src, h, mult, repaint):
    """Calculate Nadaraya-Watson Envelope"""
    n = len(src)
    out = np.zeros(n)
    mae = np.zeros(n)
    upper = np.zeros(n)
    lower = np.zeros(n)
    
    if not repaint:
        coefs = np.array([gauss(i, h) for i in range(n)])
        den = np.sum(coefs)
        
        for i in range(n):
            out[i] = np.sum(src * coefs) / den
        
        mae = pd.Series(np.abs(src - out)).rolling(499).mean().values * mult
        upper = out + mae
        lower = out - mae
    else:
        nwe = []
        sae = 0.0
        
        for i in range(n):
            sum_val = 0.0
            sumw = 0.0
            for j in range(n):
                w = gauss(i - j, h)
                sum_val += src[j] * w
                sumw += w
            y2 = sum_val / sumw
            nwe.append(y2)
            sae += np.abs(src[i] - y2)
        
        sae = (sae / n) * mult
        
        for i in range(n):
            upper[i] = nwe[i] + sae
            lower[i] = nwe[i] - sae
            out[i] = nwe[i]
    
    return out, upper, lower

def get_market_price(symbol):
    """Fetch current market price from Bybit"""
    try:
        ticker = session.get_tickers(category="linear", symbol=symbol)
        if ticker["retCode"] == 0 and ticker["result"]["list"]:
            return float(ticker["result"]["list"][0]["lastPrice"])
        raise Exception("No price data returned")
    except Exception as e:
        raise Exception(f"Failed to fetch market price: {str(e)}")

def get_lot_size_rules(symbol):
    """Get trading rules for symbol"""
    try:
        instrument_info = session.get_instruments_info(category="linear", symbol=symbol)
        if instrument_info["retCode"] == 0 and instrument_info["result"]["list"]:
            return instrument_info["result"]["list"][0]["lotSizeFilter"]
        raise Exception("No instrument info returned")
    except Exception as e:
        raise Exception(f"Failed to fetch lot size rules: {str(e)}")

def adjust_quantity_to_lot_size(quantity, lot_size_rules):
    """Adjust quantity to comply with exchange rules"""
    try:
        min_order_qty = float(lot_size_rules["minOrderQty"])
        max_order_qty = float(lot_size_rules["maxOrderQty"])
        qty_step = float(lot_size_rules["qtyStep"])

        quantity = max(min_order_qty, min(quantity, max_order_qty))
        quantity = round(quantity / qty_step) * qty_step
        return max(quantity, min_order_qty)
    except Exception as e:
        raise Exception(f"Failed to adjust quantity: {str(e)}")

def get_open_position(symbol):
    """Check for existing position"""
    try:
        positions = session.get_positions(category="linear", symbol=symbol)
        if positions["retCode"] == 0 and positions["result"]["list"]:
            for position in positions["result"]["list"]:
                if position["symbol"] == symbol and float(position["size"]) > 0:
                    return position
        return None
    except Exception as e:
        raise Exception(f"Failed to check positions: {str(e)}")

def update_stop_loss(symbol, new_sl_price):
    """Update stop-loss for open position"""
    try:
        response = session.set_trading_stop(
            category="linear",
            symbol=symbol,
            stopLoss=str(new_sl_price)
        )
        if response["retCode"] == 0:
            print(f"Stop-loss updated to {new_sl_price} USDT")
            return True
        print(f"Failed to update stop-loss: {response['retMsg']}")
        return False
    except Exception as e:
        print(f"Failed to update stop-loss: {e}")
        return False

def close_position(symbol, side):
    """Close position and place limit re-entry order"""
    try:
        position = get_open_position(symbol)
        if not position:
            print("No open position to close")
            return False

        close_side = "Sell" if side == "Buy" else "Buy"
        response = session.place_order(
            category="linear",
            symbol=symbol,
            side=close_side,
            orderType="Market",
            qty=position["size"],
            reduceOnly=True
        )

        if response["retCode"] == 0:
            print(f"Position closed successfully")
            set_trade_state("MANAGE")
            
            # Get current price and ATR levels
            current_price = get_market_price(symbol)
            ccxt_symbol = symbol_mapping_inv[symbol]
            atr_levels = get_atr_levels(ccxt_symbol)
            
            # Place limit re-entry order
            if side == "Buy":
                limit_price = round(atr_levels['upper'], 4)
                limit_side = "Buy"
                print(f"Placing limit buy at {limit_price:.4f} (2xATR above exit)")
            else:
                limit_price = round(atr_levels['lower'], 4)
                limit_side = "Sell"
                print(f"Placing limit sell at {limit_price:.4f} (2xATR below exit)")
            
            # Calculate quantity (same as original trade)
            raw_quantity = TRADE_AMOUNT_USDT / current_price
            lot_size_rules = get_lot_size_rules(symbol)
            adjusted_quantity = adjust_quantity_to_lot_size(raw_quantity, lot_size_rules)
            
            # Place limit order
            limit_response = session.place_order(
                category="linear",
                symbol=symbol,
                side=limit_side,
                orderType="Limit",
                qty=str(adjusted_quantity),
                price=str(limit_price),
                timeInForce="GTC"  # Good Till Cancelled
            )
            
            if limit_response["retCode"] == 0:
                send_email(
                    subject=f"♻️ {symbol} Limit Order Placed",
                    body=f"Placed {limit_side} limit at {limit_price:.4f}\n"
                         f"ATR: {atr_levels['atr']:.4f}\n"
                         f"Qty: {adjusted_quantity:.4f}\n"
                         f"Original Exit: {current_price:.4f}"
                )
            else:
                print(f"Failed to place limit order: {limit_response['retMsg']}")
            
            return True
            
        print(f"Failed to close position: {response['retMsg']}")
        return False
    except Exception as e:
        print(f"Error closing position: {e}")
        return False

def execute_trade(signal_symbol, signal_type):

    """Execute trade based on signal"""
    if get_trade_state() == "MANAGE":
        print(f"Trade blocked - Currently in MANAGE state for {signal_symbol}")
        return
    bybit_symbol = symbol_mapping.get(signal_symbol)
    if not bybit_symbol:
        print(f"No Bybit symbol mapping for {signal_symbol}")
        return

    try:
        side = "Buy" if signal_type == "BUY" else "Sell"
        market_price = get_market_price(bybit_symbol)
        print(f"{bybit_symbol} price: {market_price} USDT")

        # Calculate position size
        raw_quantity = TRADE_AMOUNT_USDT / market_price
        lot_size_rules = get_lot_size_rules(bybit_symbol)
        adjusted_quantity = adjust_quantity_to_lot_size(raw_quantity, lot_size_rules)

        # Calculate SL/TP prices
        if side == "Buy":
            sl_price = round(market_price * (1 - STOP_LOSS_PERCENT / 100), 4)
            tp_price = round(market_price * (1 + TAKE_PROFIT_PERCENT / 100), 4)
        else:
            sl_price = round(market_price * (1 + STOP_LOSS_PERCENT / 100), 4)
            tp_price = round(market_price * (1 - TAKE_PROFIT_PERCENT / 100), 4)

        print(f"Placing {side} order: {adjusted_quantity} contracts")
        print(f"SL: {sl_price} | TP: {tp_price}")

        # Place order
        response = session.place_order(
            category="linear",
            symbol=bybit_symbol,
            side=side,
            orderType="Market",
            qty=str(adjusted_quantity),
            takeProfit=str(tp_price),
            stopLoss=str(sl_price)
        )

        if response["retCode"] == 0:
            print(f"Order executed successfully")
            save_active_trade(signal_symbol, market_price, sl_price, tp_price, side)
            send_email(
                subject=f"✅ {side} {bybit_symbol} Executed",
                body=f"{side} {bybit_symbol} at {market_price}\n"
                     f"Quantity: {adjusted_quantity}\n"
                     f"SL: {sl_price} | TP: {tp_price}"
            )
            monitor_trade(signal_symbol, market_price, sl_price, tp_price, side)
        else:
            print(f"Order failed: {response['retMsg']}")
            send_email(
                subject=f"❌ {side} {bybit_symbol} Failed",
                body=f"Failed to execute {side} order\n"
                     f"Error: {response['retMsg']}"
            )

    except Exception as e:
        print(f"Trade execution error: {str(e)}")
        send_email(
            subject=f"⚠️ {bybit_symbol} Trade Error",
            body=f"Error executing {side} order\n"
                 f"Error: {str(e)}"
        )










def monitor_trade(symbol, entry_price, sl_price, tp_price, side):
    """Monitor open trade with all fixes including proper variable definitions"""
    max_retries = 25
    retry_delay = 10
    bybit_symbol = symbol_mapping.get(symbol)
    
    while True:
        try:
            # ===== 1. Verify Position Exists =====
            position = None
            for attempt in range(max_retries):
                try:
                    position = get_open_position(bybit_symbol)
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    print(f"Position check error (attempt {attempt+1}): {e}")
                    play_alert()
                    time.sleep(retry_delay)
            
            if not position:
                print(f"\nPosition no longer exists")
                clear_active_trade()
                set_trade_state("MANAGE")
                send_email(
                    subject=f"🏁 {symbol} Closed",
                    body=f"Position closed externally\nState set to MANAGE"
                )
                return

            # ===== 2. Get Market Data =====
            current_price = None
            for attempt in range(max_retries):
                try:
                    current_price = get_market_price(bybit_symbol)
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    print(f"Price fetch error (attempt {attempt+1}): {e}")
                    play_alert()
                    time.sleep(retry_delay)

            # ===== 3. Fetch and Prepare OHLCV Data =====
            df = None
            for attempt in range(max_retries):
                try:
                    ohlcv = exchange.fetch_ohlcv(symbol, timeframe_15m, limit=limit)
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    print(f"OHLCV fetch error (attempt {attempt+1}): {e}")
                    play_alert()
                    time.sleep(retry_delay)

            # ===== 4. Calculate Indicators =====
            src = df['close'].values
            out, upper, lower = calculate_nwe(src, H_BANDWIDTH, MULTIPLIER, REPAINT)
            df['upper'] = upper  # Store as DataFrame columns
            df['lower'] = lower
            
            # Get last COMPLETED candle (iloc[-2]) with ALL values
            last_candle = df.iloc[-2]
            last_close = last_candle['close']
            last_open = last_candle['open']
            last_high = last_candle['high']
            last_low = last_candle['low']
            last_upper = last_candle['upper']
            last_lower = last_candle['lower']

            # ===== 5. Calculate PnL and Print to Console =====
            pnl_percent = ((current_price - entry_price)/entry_price)*100 if side == "Buy" \
                         else ((entry_price - current_price)/entry_price)*100
            
            # Enhanced PnL printing
            print(f"\n{symbol} {side.upper()} | PnL: {pnl_percent:+.2f}% | "
                  f"Price: {current_price:.4f} | "
                  f"SL: {sl_price:.4f} | TP: {tp_price:.4f}")

            # ===== 6. Check Exit Conditions =====
            if side == "Buy":
                touched_band = ((last_close >= last_upper) or (last_high >= last_upper)) and \
                              not ((last_close > last_upper) and (last_open > last_upper))
                crossover_occurred = (df['close'].shift(1).iloc[-2] < df['upper'].shift(1).iloc[-2]) and \
                                   (last_close > last_upper)
            else:  # Sell
                touched_band = ((last_close <= last_lower) or (last_low <= last_lower)) and \
                              not ((last_close < last_lower) and (last_open < last_lower))
                crossunder_occurred = (df['close'].shift(1).iloc[-2] > df['lower'].shift(1).iloc[-2]) and \
                                    (last_close < last_lower)

            # ===== 7. Determine Exit Reason =====
            exit_reason = None
            if (side == "Buy" and crossover_occurred) or (side == "Sell" and crossunder_occurred):
                exit_reason = f"Force close ({'crossover' if side == 'Buy' else 'crossunder'})"
            elif pnl_percent >= 5 and touched_band:
                exit_reason = "Take profit (≥5% + band touch)"
            elif touched_band and pnl_percent < 5:
                if pnl_percent > 0:
                    new_sl = entry_price * 1.001 if side == "Buy" else entry_price * 0.999
                    if update_stop_loss(bybit_symbol, new_sl):
                        print(f"\nTrailing SL to 0.1% profit")
                        send_email(
                            subject=f"🔄 {symbol} Trailing SL",
                            body=f"Adjusted SL to {new_sl:.4f}\nCurrent PnL: {pnl_percent:.2f}%"
                        )
                    continue
                else:
                    exit_reason = "Closed at loss (band touch)"
            elif (side == "Buy" and current_price <= sl_price) or (side == "Sell" and current_price >= sl_price):
                exit_reason = "Stop-loss triggered"
            elif (side == "Buy" and current_price >= tp_price) or (side == "Sell" and current_price <= tp_price):
                exit_reason = "Take-profit triggered"

            # ===== 8. Handle Exit =====
            if exit_reason:
                print(f"\n{exit_reason} at {current_price:.4f}")
                
                if close_position(bybit_symbol, side):
                    # Calculate ATR levels for limit order
                    atr_levels = get_atr_levels(symbol)
                    
                    # Determine limit order parameters
                    if side == "Buy":
                        limit_price = atr_levels['upper']  # 2xATR above
                        limit_side = "Buy"
                    else:
                        limit_price = atr_levels['lower']  # 2xATR below
                        limit_side = "Sell"
                    
                    # Place limit order
                    try:
                        session.place_order(
                            category="linear",
                            symbol=bybit_symbol,
                            side=limit_side,
                            orderType="Limit",
                            qty=position["size"],
                            price=str(limit_price),
                            timeInForce="GTC"
                        )
                        print(f"Placed {limit_side} limit at {limit_price:.4f} (2xATR)")
                    except Exception as e:
                        print(f"Failed to place limit order: {e}")
                        play_alert()
                    
                    # Update state and notify
                    clear_active_trade()
                    set_trade_state("MANAGE")
                    send_email(
                        subject=f"🏁 {symbol} Closed → Limit Set",
                        body=f"Exit Reason: {exit_reason}\n"
                             f"Entry: {entry_price:.4f}\n"
                             f"Exit: {current_price:.4f}\n"
                             f"PnL: {pnl_percent:.2f}%\n"
                             f"Placed {limit_side} limit at {limit_price:.4f}\n"
                             f"State: MANAGE"
                    )
                    return

            time.sleep(0)  # Normal monitoring interval

        except Exception as e:
            print(f"\nCritical error: {str(e)}")
            play_alert()
            send_email(
                subject=f"🛑 {symbol} Monitoring Error",
                body=f"Error: {str(e)}\nLast Price: {current_price or 'Unknown'}\nStill managing position."
            )
            time.sleep(0)  # Wait longer after errors




















def check_conservative_entry(symbol):
    """Check for trading signals"""
    try:
        print(f"\nChecking {symbol}...")
        
        # Fetch OHLCV data
        ohlcv_15m = exchange.fetch_ohlcv(symbol, timeframe_15m, limit=limit)
        df_15m = pd.DataFrame(ohlcv_15m, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df_15m['timestamp'] = pd.to_datetime(df_15m['timestamp'], unit='ms')
        df_15m.set_index('timestamp', inplace=True)

        ohlcv_1h = exchange.fetch_ohlcv(symbol, timeframe_1h, limit=limit)
        df_1h = pd.DataFrame(ohlcv_1h, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df_1h['timestamp'] = pd.to_datetime(df_1h['timestamp'], unit='ms')
        df_1h.set_index('timestamp', inplace=True)

        # Calculate EMAs
        df_15m['EMA_Fast'] = df_15m['close'].ewm(span=ema_fast_length, adjust=False).mean()
        df_15m['EMA_Slow'] = df_15m['close'].ewm(span=ema_slow_length, adjust=False).mean()
        df_15m['EMA_Trend'] = df_15m['close'].ewm(span=ema_trend_length, adjust=False).mean()
        df_1h['EMA_Trend'] = df_1h['close'].ewm(span=ema_trend_length, adjust=False).mean()
        df_15m['EMA_Trend_1h'] = df_1h['EMA_Trend'].resample('15min').ffill()

        # Generate signals
        df_15m['Signal'] = 0
        df_15m.loc[
            (df_15m['EMA_Fast'] > df_15m['EMA_Slow']) &
            (df_15m['EMA_Fast'].shift(1) <= df_15m['EMA_Slow'].shift(1)) &
            (df_15m['close'] > df_15m['EMA_Trend']) &
            (df_15m['close'] > df_15m['EMA_Trend_1h']),
            'Signal'] = 1  # Buy signal
        
        df_15m.loc[
            (df_15m['EMA_Fast'] < df_15m['EMA_Slow']) &
            (df_15m['EMA_Fast'].shift(1) >= df_15m['EMA_Slow'].shift(1)) &
            (df_15m['close'] < df_15m['EMA_Trend']) &
            (df_15m['close'] < df_15m['EMA_Trend_1h']),
            'Signal'] = -1  # Sell signal

        # Conservative entry conditions
        df_15m['Entry_Up'] = (
            (df_15m['EMA_Fast'] > df_15m['EMA_Slow']) & 
            (df_15m['close'].shift(1) < df_15m['EMA_Fast'].shift(1)) & 
            (df_15m['close'] > df_15m['EMA_Fast'])
        )
        
        df_15m['Entry_Down'] = (
            (df_15m['EMA_Fast'] < df_15m['EMA_Slow']) & 
            (df_15m['close'].shift(1) > df_15m['EMA_Fast'].shift(1)) & 
            (df_15m['close'] < df_15m['EMA_Fast'])
        )
        
        df_15m['Entry_Up_Filtered'] = df_15m['Entry_Up'] & (
            (df_15m['close'] > df_15m['EMA_Trend']) & 
            (df_15m['close'] > df_15m['EMA_Trend_1h'])
        )
        
        df_15m['Entry_Down_Filtered'] = df_15m['Entry_Down'] & (
            (df_15m['close'] < df_15m['EMA_Trend']) & 
            (df_15m['close'] < df_15m['EMA_Trend_1h'])
        )

        # Track first conservative entry after signal
        df_15m['First_Up_Arrow'] = False
        df_15m['First_Down_Arrow'] = False
        last_signal = 0
        
        for i in range(1, len(df_15m)):
            if df_15m['Signal'].iloc[i] == 1:
                last_signal = 1
            elif df_15m['Signal'].iloc[i] == -1:
                last_signal = -1

            if last_signal == 1 and df_15m['Entry_Up_Filtered'].iloc[i]:
                df_15m.at[df_15m.index[i], 'First_Up_Arrow'] = True
                last_signal = 0
            elif last_signal == -1 and df_15m['Entry_Down_Filtered'].iloc[i]:
                df_15m.at[df_15m.index[i], 'First_Down_Arrow'] = True
                last_signal = 0

        # Check most recent closed candle
        last_candle = df_15m.iloc[-2]
        
        if last_candle['First_Up_Arrow']:
            print(f"{symbol}: ✅ BUY Signal")
            send_email(
                subject=f"🚀 BUY {symbol}",
                body=f"BUY signal detected for {symbol}\n"
                     f"Price: {last_candle['close']}\n"
                     f"Fast EMA: {last_candle['EMA_Fast']:.2f}\n"
                     f"Slow EMA: {last_candle['EMA_Slow']:.2f}"
            )
            execute_trade(symbol, "BUY")
            
        elif last_candle['First_Down_Arrow']:
            print(f"{symbol}: ❌ SELL Signal")
            send_email(
                subject=f"🔻 SELL {symbol}",
                body=f"SELL signal detected for {symbol}\n"
                     f"Price: {last_candle['close']}\n"
                     f"Fast EMA: {last_candle['EMA_Fast']:.2f}\n"
                     f"Slow EMA: {last_candle['EMA_Slow']:.2f}"
            )
            execute_trade(symbol, "SELL")
            
        else:
            print(f"{symbol}: No signal")

    except Exception as e:
        print(f"Error checking {symbol}: {str(e)}")
        send_email(
            subject=f"⚠️ {symbol} Signal Error",
            body=f"Error checking signals for {symbol}\nError: {str(e)}"
        )








# ======================== Main Execution ========================
if __name__ == "__main__":
    print("Starting Trading Bot")
    print(f"Workspace: {GITHUB_WORKSPACE}")
    
    # Check for existing trade
    active_trade = get_active_trade()
    if active_trade:
        print(f"Resuming trade: {active_trade['symbol']}")
        monitor_trade(
            symbol=active_trade['symbol'],
            entry_price=active_trade['entry_price'],
            sl_price=active_trade['sl_price'],
            tp_price=active_trade['tp_price'],
            side=active_trade['side']
        )
    
    # Main trading loop
    try:
        while True:
            scan_start = time.time()
            print(f"\n=== New Scan at {pd.Timestamp.now()} ===")
            current_state = get_trade_state()
            print(f"Current Trade State: {current_state}")


            if current_state == "ENTRY":  # <-- MODIFIED THIS LINE
                for symbol in symbols:
                    check_conservative_entry(symbol)
            else:
                print("Skipping signal checks - MANAGE state active")
            elapsed = time.time() - scan_start
            sleep_time = max(0, SCAN_INTERVAL - elapsed)
            time.sleep(sleep_time)  # <-- Add this critical line
    # ... rest of existing loop ...
            
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        send_email("🛑 Bot Crashed", f"Error:\n{str(e)}")