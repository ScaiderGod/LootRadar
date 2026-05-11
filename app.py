import html
import math
from datetime import datetime
from typing import Any, Dict, List, Tuple

import pandas as pd
import requests
import streamlit as st

APP_NAME = "LootRadar"
APP_VERSION = "V1.3"
CHEAPSHARK_BASE = "https://www.cheapshark.com/api/1.0"
CHEAPSHARK_REDIRECT = "https://www.cheapshark.com/redirect?dealID="
CHEAPSHARK_STORE_IMG = "https://www.cheapshark.com"

DLC_KEYWORDS = [
    "dlc", "season pass", "battle pass", "soundtrack", "ost", "upgrade",
    "cosmetic", "skin", "pack", "currency", "coins", "points", "addon",
    "add-on", "expansion pass", "starter pack", "bonus content", "character pack",
]

EDITION_KEYWORDS = [
    "bundle", "collection", "complete", "ultimate", "deluxe", "gold edition",
    "game of the year", "goty", "legendary", "anthology", "super deluxe",
]

DEFAULT_SEARCHES = [
    "Borderlands", "Tiny Tina", "Cyberpunk", "Elden Ring", "Baldur's Gate",
    "Doom", "Resident Evil", "Monster Hunter", "Final Fantasy", "Hades",
]

SORT_MAP = {
    "Best deal rating": "Deal Rating",
    "Biggest discount": "Savings",
    "Lowest price": "Price",
    "Best reviews": "Reviews",
    "Metacritic": "Metacritic",
    "Newest release": "Release",
    "Store": "Store",
    "Recently added": "recent",
    "Title": "Title",
}

CURRENCY_PRESETS = {
    "USD": {"label": "USD · US Dollar", "symbol": "$", "rate": 1.0, "decimals": 2},
    "MXN": {"label": "MXN · Mexican Peso", "symbol": "$", "rate": 17.0, "decimals": 2},
    "EUR": {"label": "EUR · Euro", "symbol": "€", "rate": 0.92, "decimals": 2},
    "GBP": {"label": "GBP · Pound Sterling", "symbol": "£", "rate": 0.80, "decimals": 2},
    "CAD": {"label": "CAD · Canadian Dollar", "symbol": "C$", "rate": 1.36, "decimals": 2},
    "BRL": {"label": "BRL · Brazilian Real", "symbol": "R$", "rate": 5.0, "decimals": 2},
    "COP": {"label": "COP · Colombian Peso", "symbol": "$", "rate": 3900.0, "decimals": 0},
    "CLP": {"label": "CLP · Chilean Peso", "symbol": "$", "rate": 900.0, "decimals": 0},
    "ARS": {"label": "ARS · Argentine Peso", "symbol": "$", "rate": 900.0, "decimals": 0},
    "JPY": {"label": "JPY · Japanese Yen", "symbol": "¥", "rate": 155.0, "decimals": 0},
    "Custom": {"label": "Custom currency", "symbol": "$", "rate": 1.0, "decimals": 2},
}


def currency_step(rate: float) -> float:
    if rate >= 1000:
        return 1000.0
    if rate >= 100:
        return 100.0
    if rate >= 10:
        return 10.0
    return 1.0


def make_currency_settings(code: str, symbol: str, rate: float, decimals: int) -> Dict[str, Any]:
    return {
        "code": code.strip().upper() or "CUR",
        "symbol": symbol.strip() or "$",
        "rate": max(float(rate), 0.0001),
        "decimals": max(0, min(int(decimals), 4)),
    }


def convert_price(value: float, currency: Dict[str, Any]) -> float:
    return float(value) * float(currency.get("rate", 1.0))


def convert_to_usd(value: float, currency: Dict[str, Any]) -> float:
    return float(value) / max(float(currency.get("rate", 1.0)), 0.0001)

st.set_page_config(
    page_title=f"{APP_NAME} | Game Deal Scanner",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_css() -> None:
    st.markdown(
        """
<style>
:root {
    --space: #050812;
    --ink: #f5f7fb;
    --muted: #9ca8c0;
    --line: rgba(255,255,255,.10);
    --panel: rgba(13, 20, 37, .78);
    --panel2: rgba(20, 29, 51, .72);
    --radar: #45ff9a;
    --radar-soft: rgba(69,255,154,.16);
    --violet: #8d7cff;
    --violet-soft: rgba(141,124,255,.18);
    --amber: #ffd166;
    --danger: #ff5c78;
}

.stApp {
    color: var(--ink);
    background:
        radial-gradient(circle at 12% 3%, rgba(69,255,154,.13), transparent 28%),
        radial-gradient(circle at 90% 0%, rgba(141,124,255,.18), transparent 30%),
        radial-gradient(circle at 50% 100%, rgba(69,255,154,.06), transparent 34%),
        linear-gradient(145deg, #050812 0%, #0b1122 45%, #070917 100%);
}

.block-container {
    max-width: 1520px;
    padding-top: 1.25rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(4,8,17,.98), rgba(7,11,23,.96));
    border-right: 1px solid rgba(255,255,255,.09);
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {
    font-size: .95rem;
}

hr { border-color: rgba(255,255,255,.10); }

div[data-testid="stButton"] > button {
    border-radius: 999px;
    border: 1px solid rgba(255,255,255,.13);
    background: rgba(255,255,255,.055);
    color: #f4f7fb;
    font-weight: 800;
    min-height: 2.55rem;
    transition: transform .14s ease, border-color .14s ease, box-shadow .14s ease, background .14s ease;
}

div[data-testid="stButton"] > button:hover {
    transform: translateY(-1px);
    border-color: rgba(69,255,154,.58);
    background: rgba(69,255,154,.08);
    box-shadow: 0 0 0 1px rgba(69,255,154,.13), 0 16px 34px rgba(0,0,0,.28);
    color: #fff;
}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
    border-radius: 15px !important;
    background: rgba(255,255,255,.055) !important;
    border-color: rgba(255,255,255,.09) !important;
}

.hero-shell {
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 30px;
    padding: 1px;
    background:
      linear-gradient(135deg, rgba(69,255,154,.55), rgba(141,124,255,.35), rgba(255,255,255,.08));
    box-shadow: 0 30px 90px rgba(0,0,0,.32);
    margin-bottom: 1.1rem;
}

.hero {
    border-radius: 29px;
    padding: 30px;
    background:
      linear-gradient(135deg, rgba(12,18,33,.97), rgba(17,24,47,.92)),
      radial-gradient(circle at 8% 20%, rgba(69,255,154,.14), transparent 35%),
      radial-gradient(circle at 92% 7%, rgba(141,124,255,.22), transparent 36%);
    overflow: hidden;
    position: relative;
}

.hero:before {
    content: "";
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(255,255,255,.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,.025) 1px, transparent 1px);
    background-size: 38px 38px;
    mask-image: linear-gradient(90deg, rgba(0,0,0,.85), transparent 75%);
    pointer-events: none;
}

.hero-content { position: relative; z-index: 1; }

.brand-line {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 16px;
}

.radar-logo {
    width: 58px;
    height: 58px;
    border-radius: 50%;
    position: relative;
    border: 1px solid rgba(69,255,154,.55);
    background:
        radial-gradient(circle, rgba(255,255,255,.95) 0 5%, rgba(69,255,154,.90) 6% 9%, transparent 10%),
        repeating-radial-gradient(circle, transparent 0 13px, rgba(255,255,255,.14) 14px, transparent 15px),
        conic-gradient(from 250deg, rgba(69,255,154,.05), rgba(69,255,154,.9), rgba(141,124,255,.30), rgba(69,255,154,.05));
    box-shadow: 0 0 34px rgba(69,255,154,.20), inset 0 0 25px rgba(69,255,154,.10);
}

.radar-logo:after {
    content: "";
    position: absolute;
    left: 28px;
    top: 8px;
    width: 2px;
    height: 22px;
    border-radius: 2px;
    background: rgba(69,255,154,.95);
    transform-origin: bottom center;
    transform: rotate(42deg);
    box-shadow: 0 0 18px rgba(69,255,154,.9);
}

.eyebrow {
    color: var(--radar);
    letter-spacing: .18em;
    font-size: .72rem;
    font-weight: 900;
    text-transform: uppercase;
}

.hero h1 {
    margin: 0;
    font-size: clamp(3.1rem, 7vw, 6.7rem);
    line-height: .86;
    letter-spacing: -.075em;
}

.hero-subtitle {
    color: #c5d0e6;
    font-size: 1.05rem;
    max-width: 900px;
    margin: 18px 0 0;
}

.hero-grid {
    display: grid;
    grid-template-columns: 1.4fr .8fr .8fr .8fr;
    gap: 12px;
    margin-top: 24px;
}

.hero-stat {
    background: rgba(255,255,255,.055);
    border: 1px solid rgba(255,255,255,.095);
    border-radius: 20px;
    padding: 15px 16px;
    min-height: 82px;
}

.hero-stat .k {
    color: var(--muted);
    font-size: .76rem;
    margin-bottom: 6px;
}

.hero-stat .v {
    font-size: 1.35rem;
    line-height: 1.12;
    font-weight: 950;
    word-break: break-word;
}

.section-title {
    font-size: 1.35rem;
    font-weight: 950;
    letter-spacing: -.03em;
    margin: 18px 0 9px;
}

.scan-strip {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 10px;
}

.pick-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
    margin: 12px 0 18px;
}

.pick-card {
    border: 1px solid rgba(255,255,255,.10);
    background: linear-gradient(180deg, rgba(18,27,50,.82), rgba(9,13,25,.83));
    border-radius: 22px;
    padding: 15px;
}

.pick-card .tag {
    color: var(--radar);
    font-size: .70rem;
    letter-spacing: .13em;
    text-transform: uppercase;
    font-weight: 900;
    margin-bottom: 8px;
}

.pick-card .name {
    font-weight: 950;
    line-height: 1.18;
    margin-bottom: 8px;
}

.pick-card .meta {
    color: var(--muted);
    font-size: .82rem;
}

.metric-row {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin: 12px 0 18px;
}

.soft-panel {
    border: 1px solid rgba(255,255,255,.09);
    background: rgba(255,255,255,.045);
    border-radius: 22px;
    padding: 16px;
}

.deal-card {
    min-height: 100%;
    border: 1px solid rgba(255,255,255,.105);
    background:
        radial-gradient(circle at 8% 0%, rgba(69,255,154,.09), transparent 30%),
        linear-gradient(180deg, rgba(17,25,47,.92), rgba(8,12,23,.96));
    border-radius: 24px;
    padding: 15px;
    box-shadow: 0 24px 58px rgba(0,0,0,.24);
    transition: transform .16s ease, border-color .16s ease, box-shadow .16s ease;
}

.deal-card:hover {
    transform: translateY(-3px);
    border-color: rgba(69,255,154,.28);
    box-shadow: 0 30px 75px rgba(0,0,0,.34);
}

.deal-top {
    display: grid;
    grid-template-columns: 92px 1fr;
    gap: 14px;
    align-items: start;
}

.cover-wrap {
    position: relative;
    width: 92px;
    height: 92px;
}

.deal-img {
    width: 92px;
    height: 92px;
    object-fit: cover;
    border-radius: 18px;
    background: rgba(255,255,255,.06);
    border: 1px solid rgba(255,255,255,.10);
}

.store-mini {
    position: absolute;
    right: -7px;
    bottom: -7px;
    width: 30px;
    height: 30px;
    border-radius: 10px;
    background: #101827;
    border: 1px solid rgba(255,255,255,.18);
    padding: 4px;
    object-fit: contain;
}

.deal-title {
    color: #fff;
    font-size: 1rem;
    line-height: 1.18;
    font-weight: 950;
    margin: 2px 0 8px;
}

.store-line {
    color: var(--muted);
    font-size: .82rem;
    margin-bottom: 8px;
}

.badge-row {
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
    margin: 8px 0 10px;
}

.badge {
    display: inline-flex;
    align-items: center;
    padding: 5px 9px;
    border-radius: 999px;
    font-size: .70rem;
    line-height: 1;
    font-weight: 950;
    border: 1px solid rgba(255,255,255,.12);
    background: rgba(255,255,255,.07);
    color: #dfe7f7;
    white-space: nowrap;
}

.badge.green { color: #031109; background: var(--radar); border-color: rgba(69,255,154,.82); }
.badge.violet { color: #fff; background: rgba(141,124,255,.35); border-color: rgba(141,124,255,.55); }
.badge.gold { color: #1f1500; background: var(--amber); border-color: rgba(255,209,102,.78); }
.badge.red { color: #fff; background: rgba(255,92,120,.40); border-color: rgba(255,92,120,.58); }

.price-row {
    display: flex;
    align-items: baseline;
    gap: 8px;
    margin: 12px 0 8px;
}

.sale-price {
    color: var(--radar);
    font-size: 1.8rem;
    font-weight: 1000;
    letter-spacing: -.045em;
}

.normal-price {
    color: var(--muted);
    text-decoration: line-through;
    font-size: .92rem;
}

.detail-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 8px;
    margin-top: 10px;
}

.detail {
    background: rgba(255,255,255,.043);
    border: 1px solid rgba(255,255,255,.075);
    border-radius: 15px;
    padding: 8px;
}

.detail .label {
    color: var(--muted);
    font-size: .66rem;
    margin-bottom: 3px;
}

.detail .value {
    color: #fff;
    font-weight: 900;
    font-size: .88rem;
}

.deal-note {
    color: #dbe5f7;
    background: rgba(69,255,154,.065);
    border: 1px solid rgba(69,255,154,.14);
    border-radius: 16px;
    padding: 10px 12px;
    font-size: .81rem;
    margin-top: 12px;
    min-height: 46px;
}

.deal-actions {
    display: grid;
    grid-template-columns: 1fr;
    gap: 8px;
    margin-top: 12px;
}

a.deal-btn {
    display: inline-flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    padding: 10px 12px;
    color: #031109 !important;
    background: linear-gradient(90deg, var(--radar), #a4ffd0);
    font-weight: 1000;
    text-decoration: none !important;
    border-radius: 16px;
    box-shadow: 0 14px 30px rgba(69,255,154,.16);
}

.empty-box {
    border: 1px solid rgba(255,255,255,.10);
    background: rgba(255,255,255,.045);
    border-radius: 24px;
    padding: 28px;
    color: var(--muted);
}

.tiny-muted {
    color: var(--muted);
    font-size: .82rem;
}

.footer-note {
    color: var(--muted);
    font-size: .80rem;
    margin-top: 24px;
    border-top: 1px solid rgba(255,255,255,.08);
    padding-top: 12px;
}

@media (max-width: 1000px) {
    .hero-grid, .metric-row, .pick-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 700px) {
    .hero { padding: 22px; }
    .hero-grid, .metric-row, .pick-grid { grid-template-columns: 1fr; }
    .deal-top { grid-template-columns: 74px 1fr; }
    .cover-wrap, .deal-img { width: 74px; height: 74px; }
    .detail-grid { grid-template-columns: 1fr; }
}
</style>
        """,
        unsafe_allow_html=True,
    )


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        if value in (None, ""):
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


@st.cache_data(ttl=60 * 45, show_spinner=False)
def api_get(endpoint: str, params: Tuple[Tuple[str, Any], ...] = ()) -> Any:
    response = requests.get(
        f"{CHEAPSHARK_BASE}/{endpoint}",
        params=dict(params),
        timeout=20,
        headers={"User-Agent": f"{APP_NAME}/{APP_VERSION}"},
    )
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=60 * 60 * 12, show_spinner=False)
def get_stores() -> Dict[str, Dict[str, str]]:
    try:
        raw_stores = api_get("stores")
        stores: Dict[str, Dict[str, str]] = {}
        for store in raw_stores:
            if str(store.get("isActive", "1")) == "1":
                store_id = str(store.get("storeID"))
                images = store.get("images") or {}
                icon = images.get("icon") or images.get("logo") or ""
                stores[store_id] = {
                    "name": str(store.get("storeName", f"Store {store_id}")),
                    "icon": f"{CHEAPSHARK_STORE_IMG}{icon}" if str(icon).startswith("/") else str(icon),
                }
        return stores
    except Exception:
        return {}


@st.cache_data(ttl=60 * 20, show_spinner=False)
def search_deals(
    title: str,
    page_size: int,
    sort_by: str,
    desc: bool,
    on_sale_only: bool,
    steamworks_only: bool,
    lower_price: float,
    upper_price: float,
) -> List[Dict[str, Any]]:
    params: Dict[str, Any] = {
        "title": title,
        "pageSize": page_size,
        "pageNumber": 0,
        "sortBy": sort_by,
        "desc": 1 if desc else 0,
        "lowerPrice": lower_price,
        "upperPrice": upper_price,
    }
    if on_sale_only:
        params["onSale"] = 1
    if steamworks_only:
        params["steamworks"] = 1
    normalized_params = tuple(sorted(params.items()))
    return api_get("deals", normalized_params)


def classify_item(title: str) -> str:
    lower_title = title.lower()
    if any(word in lower_title for word in ["season pass", "expansion pass"]):
        return "Season Pass"
    if any(word in lower_title for word in EDITION_KEYWORDS):
        return "Bundle / Edition"
    if any(word in lower_title for word in DLC_KEYWORDS):
        return "DLC / Add on"
    return "Base Game"


def deal_score(savings: float, deal_rating: float, sale_price: float, steam_rating: float, category: str) -> int:
    discount_points = min(max(savings, 0), 100) * 0.52
    deal_rating_points = min(max(deal_rating, 0), 10) * 3.1
    player_points = min(max(steam_rating, 0), 100) * 0.12
    price_points = max(0, 100 - min(sale_price, 70) / 70 * 100) * 0.05
    category_penalty = 4 if category in {"DLC / Add on", "Season Pass"} else 0
    return max(0, min(100, int(round(discount_points + deal_rating_points + player_points + price_points - category_penalty))))


def deal_verdict(score: int, savings: float, sale_price: float, category: str) -> Tuple[str, str]:
    if sale_price <= 0.01:
        return "Claim now", "Free or almost free. Grab it before it disappears."
    if category in {"DLC / Add on", "Season Pass"}:
        return "Check edition", "Extra content detected. Compare it against complete editions before buying."
    if score >= 85 and savings >= 75:
        return "Buy now", "Strong score, deep discount and good value for a base game or edition."
    if score >= 72:
        return "Strong deal", "Looks worth checking now, especially if it was already on your wishlist."
    if savings >= 50:
        return "Good discount", "The discount is solid, but compare stores and editions first."
    return "Watch it", "Not bad, but probably worth waiting for a stronger sale."


def money(value: float, currency: Dict[str, Any] | None = None) -> str:
    if value <= 0.01:
        return "Free"
    currency = currency or make_currency_settings("USD", "$", 1.0, 2)
    converted = convert_price(float(value), currency)
    decimals = int(currency.get("decimals", 2))
    symbol = str(currency.get("symbol", "$"))
    code = str(currency.get("code", "USD"))
    formatted = f"{symbol}{converted:,.{decimals}f}"
    return f"{formatted} {code}"


def add_currency_columns(df: pd.DataFrame, currency: Dict[str, Any]) -> pd.DataFrame:
    if df.empty:
        return df
    enriched = df.copy()
    enriched["sale_price_display"] = enriched["sale_price"].apply(lambda value: money(float(value), currency))
    enriched["normal_price_display"] = enriched["normal_price"].apply(lambda value: money(float(value), currency))
    enriched["sale_price_converted"] = enriched["sale_price"].apply(lambda value: convert_price(float(value), currency))
    enriched["normal_price_converted"] = enriched["normal_price"].apply(lambda value: convert_price(float(value), currency))
    enriched["currency"] = str(currency.get("code", "USD"))
    return enriched


def normalize_deals(raw_deals: List[Dict[str, Any]], stores: Dict[str, Dict[str, str]]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for deal in raw_deals:
        title = str(deal.get("title", "Unknown game"))
        sale_price = safe_float(deal.get("salePrice"))
        normal_price = safe_float(deal.get("normalPrice"))
        savings = safe_float(deal.get("savings"))
        deal_rating = safe_float(deal.get("dealRating"))
        steam_rating = safe_float(deal.get("steamRatingPercent"))
        steam_rating_count = safe_int(deal.get("steamRatingCount"))
        metacritic = safe_float(deal.get("metacriticScore"))
        store_id = str(deal.get("storeID", ""))
        store_info = stores.get(store_id, {"name": f"Store {store_id}", "icon": ""})
        category = classify_item(title)
        score = deal_score(savings, deal_rating, sale_price, steam_rating, category)
        verdict, note = deal_verdict(score, savings, sale_price, category)
        deal_id = str(deal.get("dealID", ""))
        steam_app_id = str(deal.get("steamAppID") or "")
        rows.append(
            {
                "title": title,
                "store_id": store_id,
                "store": store_info.get("name", f"Store {store_id}"),
                "store_icon": store_info.get("icon", ""),
                "sale_price": sale_price,
                "normal_price": normal_price,
                "savings": savings,
                "deal_rating": deal_rating,
                "steam_rating": steam_rating,
                "steam_rating_count": steam_rating_count,
                "metacritic": metacritic,
                "thumb": str(deal.get("thumb") or ""),
                "deal_id": deal_id,
                "game_id": str(deal.get("gameID", "")),
                "steam_app_id": steam_app_id,
                "url": f"{CHEAPSHARK_REDIRECT}{deal_id}",
                "steam_url": f"https://store.steampowered.com/app/{steam_app_id}" if steam_app_id else "",
                "category": category,
                "deal_score": score,
                "verdict": verdict,
                "note": note,
            }
        )
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def html_attr(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def render_hero(df: pd.DataFrame, query: str, currency: Dict[str, Any]) -> None:
    if df.empty:
        total_deals = "0"
        best_discount = "0%"
        lowest_price = "—"
        best_store = "No store yet"
    else:
        total_deals = str(len(df))
        best_discount = f"{df['savings'].max():.0f}%"
        best_row = df.sort_values(["sale_price", "deal_score"], ascending=[True, False]).iloc[0]
        lowest_price = money(float(best_row["sale_price"]), currency)
        best_store = str(best_row["store"])

    hero_html = (
        '<div class="hero-shell"><div class="hero"><div class="hero-content">'
        '<div class="brand-line"><div class="radar-logo"></div><div>'
        '<div class="eyebrow">Game deal scanner</div>'
        f'<h1>{APP_NAME}</h1>'
        '</div></div>'
        '<div class="hero-subtitle">Scan PC game deals across tracked stores, compare editions, avoid weak discounts and find the best value before the sale disappears.</div>'
        '<div class="hero-grid">'
        f'<div class="hero-stat"><div class="k">Current scan</div><div class="v">{html.escape(query or "Explore")}</div></div>'
        f'<div class="hero-stat"><div class="k">Deals found</div><div class="v">{total_deals}</div></div>'
        f'<div class="hero-stat"><div class="k">Best discount</div><div class="v">{best_discount}</div></div>'
        f'<div class="hero-stat"><div class="k">Lowest price</div><div class="v">{lowest_price}<br><span style="font-size:.78rem;color:#9ca8c0;">{html.escape(best_store)}</span></div></div>'
        '</div></div></div></div>'
    )
    st.markdown(hero_html, unsafe_allow_html=True)


def render_radar_picks(df: pd.DataFrame, currency: Dict[str, Any]) -> None:
    if df.empty:
        return
    best_score = df.sort_values(["deal_score", "savings"], ascending=[False, False]).iloc[0]
    cheapest = df.sort_values(["sale_price", "deal_score"], ascending=[True, False]).iloc[0]
    biggest_discount = df.sort_values(["savings", "deal_score"], ascending=[False, False]).iloc[0]
    picks = [
        ("Radar pick", best_score),
        ("Cheapest hit", cheapest),
        ("Biggest drop", biggest_discount),
    ]
    cards = []
    seen = set()
    for label, row in picks:
        key = f"{row['title']}::{row['store']}::{label}"
        if key in seen:
            continue
        seen.add(key)
        cards.append(
            '<div class="pick-card">'
            f'<div class="tag">{html.escape(label)}</div>'
            f'<div class="name">{html.escape(str(row["title"]))}</div>'
            f'<div class="meta">{money(float(row["sale_price"]), currency)} · {float(row["savings"]):.0f}% off · {html.escape(str(row["store"]))}</div>'
            '</div>'
        )
    if cards:
        st.markdown('<div class="pick-grid">' + ''.join(cards) + '</div>', unsafe_allow_html=True)


def render_deal_card(row: pd.Series, currency: Dict[str, Any]) -> None:
    title = html.escape(str(row["title"]))
    store = html.escape(str(row["store"]))
    category = html.escape(str(row["category"]))
    thumb = html_attr(row.get("thumb"))
    store_icon = html_attr(row.get("store_icon"))
    url = html_attr(row["url"])
    savings = float(row["savings"])
    score = int(row["deal_score"])
    deal_rating = float(row["deal_rating"])
    steam_rating = float(row["steam_rating"])
    metacritic = float(row["metacritic"])
    sale_price = float(row["sale_price"])
    normal_price = float(row["normal_price"])
    verdict = html.escape(str(row["verdict"]))
    note = html.escape(str(row["note"]))

    score_class = "green" if score >= 80 else "violet" if score >= 65 else "gold" if score >= 45 else "red"
    discount_class = "green" if savings >= 75 else "violet" if savings >= 50 else "gold"
    category_class = "violet" if category != "Base Game" else "green"
    metacritic_value = "—" if metacritic <= 0 else f"{metacritic:.0f}"
    steam_value = "—" if steam_rating <= 0 else f"{steam_rating:.0f}%"

    image_html = (
        f'<img class="deal-img" src="{thumb}" alt="{title}" loading="lazy">'
        if thumb
        else '<div class="deal-img"></div>'
    )
    store_icon_html = (
        f'<img class="store-mini" src="{store_icon}" alt="{store}" loading="lazy">'
        if store_icon
        else ''
    )

    card_html = (
        '<div class="deal-card">'
        '<div class="deal-top">'
        f'<div class="cover-wrap">{image_html}{store_icon_html}</div>'
        '<div>'
        f'<div class="deal-title">{title}</div>'
        f'<div class="store-line">{store} · PC deal</div>'
        '<div class="badge-row">'
        f'<span class="badge {discount_class}">{savings:.0f}% OFF</span>'
        f'<span class="badge {score_class}">Score {score}/100</span>'
        f'<span class="badge {category_class}">{category}</span>'
        '</div>'
        '</div>'
        '</div>'
        '<div class="price-row">'
        f'<div class="sale-price">{money(sale_price, currency)}</div>'
        f'<div class="normal-price">{money(normal_price, currency)}</div>'
        '</div>'
        '<div class="detail-grid">'
        f'<div class="detail"><div class="label">Deal rating</div><div class="value">{deal_rating:.1f}/10</div></div>'
        f'<div class="detail"><div class="label">Steam rating</div><div class="value">{steam_value}</div></div>'
        f'<div class="detail"><div class="label">Metacritic</div><div class="value">{metacritic_value}</div></div>'
        '</div>'
        f'<div class="deal-note"><strong>{verdict}:</strong> {note}</div>'
        '<div class="deal-actions">'
        f'<a class="deal-btn" href="{url}" target="_blank" rel="noopener noreferrer">Open deal</a>'
        '</div>'
        '</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)


def render_quick_searches() -> None:
    st.markdown('<div class="section-title">Quick scans</div>', unsafe_allow_html=True)
    cols = st.columns(5)
    for index, item in enumerate(DEFAULT_SEARCHES):
        with cols[index % 5]:
            if st.button(item, key=f"quick_scan_{index}", use_container_width=True):
                st.session_state.search_query = item
                st.rerun()


def apply_filters(
    df: pd.DataFrame,
    selected_stores: List[str],
    selected_categories: List[str],
    min_discount: int,
    max_price: float,
    min_score: int,
    clean_mode: bool,
    best_per_title: bool,
    currency: Dict[str, Any],
) -> pd.DataFrame:
    filtered = df.copy()
    if filtered.empty:
        return filtered
    if selected_stores:
        filtered = filtered[filtered["store"].isin(selected_stores)]
    if selected_categories:
        filtered = filtered[filtered["category"].isin(selected_categories)]
    filtered = filtered[filtered["savings"] >= min_discount]
    filtered = filtered[filtered["sale_price"].apply(lambda value: convert_price(float(value), currency)) <= max_price]
    filtered = filtered[filtered["deal_score"] >= min_score]
    if clean_mode:
        filtered = filtered[filtered["category"].isin(["Base Game", "Bundle / Edition"])]
    if best_per_title and not filtered.empty:
        filtered = (
            filtered.sort_values(["title", "sale_price", "deal_score"], ascending=[True, True, False])
            .drop_duplicates(subset=["title"], keep="first")
        )
    return filtered


def sort_df(df: pd.DataFrame, sort_label: str) -> pd.DataFrame:
    if df.empty:
        return df
    if sort_label == "Deal Score":
        return df.sort_values(["deal_score", "savings"], ascending=[False, False])
    if sort_label == "Lowest Price":
        return df.sort_values(["sale_price", "deal_score"], ascending=[True, False])
    if sort_label == "Biggest Discount":
        return df.sort_values(["savings", "deal_score"], ascending=[False, False])
    if sort_label == "Base Games First":
        category_order = {"Base Game": 0, "Bundle / Edition": 1, "Season Pass": 2, "DLC / Add on": 3}
        temp = df.assign(_category_rank=df["category"].map(category_order).fillna(9))
        return temp.sort_values(["_category_rank", "deal_score"], ascending=[True, False]).drop(columns=["_category_rank"])
    if sort_label == "Store":
        return df.sort_values(["store", "title"], ascending=[True, True])
    return df.sort_values(["title", "deal_score"], ascending=[True, False])


def favorites_panel(df: pd.DataFrame, currency: Dict[str, Any]) -> None:
    if "favorites" not in st.session_state:
        st.session_state.favorites = []

    st.markdown("### Vault")
    st.caption("Session favorites. Good for comparing deals before opening store links.")

    if df.empty:
        st.info("Search first to add deals to your Vault.")
        return

    options = {
        f"{row.title} · {row.store} · {money(row.sale_price, currency)} · {row.savings:.0f}% off": row.deal_id
        for row in df.itertuples()
    }
    pick = st.selectbox("Add deal", [""] + list(options.keys()))
    add_col, clear_col = st.columns([1, 1])
    with add_col:
        if st.button("Add to Vault", use_container_width=True, disabled=not pick):
            deal_id = options[pick]
            if deal_id not in st.session_state.favorites:
                st.session_state.favorites.append(deal_id)
                st.success("Added to Vault.")
            else:
                st.info("Already in Vault.")
    with clear_col:
        if st.button("Clear Vault", use_container_width=True):
            st.session_state.favorites = []
            st.rerun()

    favorite_df = df[df["deal_id"].isin(st.session_state.favorites)]
    if favorite_df.empty:
        st.caption("Your Vault is empty.")
        return

    favorite_view = add_currency_columns(favorite_df, currency)
    st.dataframe(
        favorite_view[["title", "category", "store", "sale_price_display", "normal_price_display", "sale_price", "normal_price", "savings", "deal_score", "url"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "sale_price_display": st.column_config.TextColumn(f"Sale ({currency['code']})"),
            "normal_price_display": st.column_config.TextColumn(f"Normal ({currency['code']})"),
            "sale_price": st.column_config.NumberColumn("Sale USD", format="$%.2f"),
            "normal_price": st.column_config.NumberColumn("Normal USD", format="$%.2f"),
            "savings": st.column_config.NumberColumn("Discount", format="%.0f%%"),
            "deal_score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100),
            "url": st.column_config.LinkColumn("Deal"),
        },
    )


def render_metrics(filtered_df: pd.DataFrame) -> None:
    if filtered_df.empty:
        visible = 0
        stores_count = 0
        top_discount = "0%"
        best_score = "0/100"
    else:
        visible = len(filtered_df)
        stores_count = filtered_df["store"].nunique()
        top_discount = f"{filtered_df['savings'].max():.0f}%"
        best_score = f"{filtered_df['deal_score'].max():.0f}/100"
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Visible deals", visible)
    c2.metric("Stores", stores_count)
    c3.metric("Top discount", top_discount)
    c4.metric("Best score", best_score)


def main() -> None:
    inject_css()

    if "search_query" not in st.session_state:
        st.session_state.search_query = "Borderlands"

    stores = get_stores()

    with st.sidebar:
        st.markdown("## LootRadar Controls")
        query = st.text_input("Search game", key="search_query", placeholder="Borderlands, Doom, Hades...")
        st.caption("V1.3 is focused on PC game deals.")

        st.divider()
        st.markdown("### Scan settings")
        sort_label = st.selectbox("API scan order", list(SORT_MAP.keys()), index=0)
        sort_by = SORT_MAP[sort_label]
        desc = st.toggle("Descending order", value=True)
        on_sale_only = st.toggle("Only active sales", value=True)
        steamworks_only = st.toggle("Steam redeemable only", value=False)
        page_size = st.slider("Max results", 12, 60, 36, step=12)

        st.divider()
        st.markdown("### Currency")
        currency_choice = st.selectbox(
            "Display currency",
            list(CURRENCY_PRESETS.keys()),
            format_func=lambda key: CURRENCY_PRESETS[key]["label"],
            index=0,
        )
        preset = CURRENCY_PRESETS[currency_choice]
        if currency_choice == "Custom":
            custom_code = st.text_input("Currency code", value="MXN", max_chars=6)
            custom_symbol = st.text_input("Currency symbol", value="$", max_chars=5)
            custom_decimals = st.selectbox("Decimals", [0, 2, 3, 4], index=1)
            currency_code = custom_code
            currency_symbol = custom_symbol
            currency_decimals = custom_decimals
        else:
            currency_code = currency_choice
            currency_symbol = str(preset["symbol"])
            currency_decimals = int(preset["decimals"])
        exchange_rate = st.number_input(
            f"Exchange rate: 1 USD = ? {currency_code.upper()}",
            min_value=0.0001,
            value=float(preset["rate"]),
            step=0.01 if float(preset["rate"]) < 20 else 1.0,
            format="%.4f",
        )
        currency = make_currency_settings(currency_code, currency_symbol, exchange_rate, currency_decimals)
        st.caption("CheapShark returns USD prices. LootRadar converts them using this manual rate.")

        price_step = currency_step(exchange_rate)
        slider_max = max(100.0 * exchange_rate, price_step)
        api_default = min(80.0 * exchange_rate, slider_max)
        visible_default = min(60.0 * exchange_rate, slider_max)
        api_max_price_display = st.slider(
            f"API max price ({currency['code']})",
            0.0,
            float(slider_max),
            float(api_default),
            step=float(price_step),
        )
        api_max_price = convert_to_usd(api_max_price_display, currency)

        st.divider()
        st.markdown("### Filters")
        min_discount = st.slider("Minimum discount", 0, 95, 0, step=5)
        max_price = st.slider(
            f"Visible max price ({currency['code']})",
            0.0,
            float(slider_max),
            float(visible_default),
            step=float(price_step),
        )
        min_score = st.slider("Minimum deal score", 0, 100, 0, step=5)
        clean_mode = st.toggle("Clean Mode: hide most DLC and extras", value=True)
        best_per_title = st.toggle("Best deal per title", value=False)

    raw_deals: List[Dict[str, Any]] = []
    error_message = None
    if query.strip():
        try:
            with st.spinner("Scanning deals..."):
                raw_deals = search_deals(
                    query.strip(),
                    page_size,
                    sort_by,
                    desc,
                    on_sale_only,
                    steamworks_only,
                    0,
                    api_max_price,
                )
        except Exception as exc:
            error_message = str(exc)

    df = normalize_deals(raw_deals, stores) if raw_deals else pd.DataFrame()
    render_hero(df, query.strip(), currency)

    if error_message:
        st.error(f"Could not load deals right now: {error_message}")
        st.stop()

    render_quick_searches()

    if df.empty:
        st.markdown(
            '<div class="empty-box"><strong>No deals found.</strong><br>Try another title, increase the max price or turn off active sales only.</div>',
            unsafe_allow_html=True,
        )
        st.stop()

    render_radar_picks(df, currency)

    categories = sorted(df["category"].dropna().unique().tolist())
    store_names = sorted(df["store"].dropna().unique().tolist())

    filter_col_1, filter_col_2, filter_col_3 = st.columns([1.2, 1.2, 1])
    with filter_col_1:
        selected_stores = st.multiselect("Store", store_names)
    with filter_col_2:
        selected_categories = st.multiselect("Content type", categories)
    with filter_col_3:
        local_sort = st.selectbox(
            "Final sort",
            ["Deal Score", "Lowest Price", "Biggest Discount", "Base Games First", "Store", "Title"],
        )

    filtered_df = apply_filters(
        df,
        selected_stores,
        selected_categories,
        min_discount,
        max_price,
        min_score,
        clean_mode,
        best_per_title,
        currency,
    )
    filtered_df = sort_df(filtered_df, local_sort)

    render_metrics(filtered_df)

    tab_deals, tab_compare, tab_vault, tab_data, tab_about = st.tabs(["Radar", "Compare", "Vault", "Data", "About"])

    with tab_deals:
        if filtered_df.empty:
            st.markdown(
                '<div class="empty-box"><strong>No visible deals match your filters.</strong><br>Lower the discount, score or max price filters.</div>',
                unsafe_allow_html=True,
            )
        else:
            cols_per_row = 3
            rows = math.ceil(len(filtered_df) / cols_per_row)
            for row_index in range(rows):
                cols = st.columns(cols_per_row)
                for col_index in range(cols_per_row):
                    deal_index = row_index * cols_per_row + col_index
                    if deal_index < len(filtered_df):
                        with cols[col_index]:
                            render_deal_card(filtered_df.iloc[deal_index], currency)

    with tab_compare:
        st.markdown("### Compare current results")
        st.caption("Useful for franchises with base games, bundles, season passes and DLCs mixed together.")
        compare_view = add_currency_columns(filtered_df, currency)
        compare_cols = [
            "title", "category", "store", "sale_price_display", "normal_price_display",
            "sale_price", "normal_price", "savings", "deal_score", "deal_rating",
            "steam_rating", "metacritic", "url", "steam_url",
        ]
        st.dataframe(
            compare_view[compare_cols],
            use_container_width=True,
            hide_index=True,
            column_config={
                "sale_price_display": st.column_config.TextColumn(f"Sale ({currency['code']})"),
                "normal_price_display": st.column_config.TextColumn(f"Normal ({currency['code']})"),
                "sale_price": st.column_config.NumberColumn("Sale USD", format="$%.2f"),
                "normal_price": st.column_config.NumberColumn("Normal USD", format="$%.2f"),
                "savings": st.column_config.NumberColumn("Discount", format="%.0f%%"),
                "deal_score": st.column_config.ProgressColumn("Deal Score", min_value=0, max_value=100),
                "deal_rating": st.column_config.NumberColumn("Deal rating", format="%.1f"),
                "steam_rating": st.column_config.NumberColumn("Steam rating", format="%.0f%%"),
                "metacritic": st.column_config.NumberColumn("Metacritic", format="%.0f"),
                "url": st.column_config.LinkColumn("Deal link"),
                "steam_url": st.column_config.LinkColumn("Steam page"),
            },
        )

    with tab_vault:
        favorites_panel(filtered_df, currency)

    with tab_data:
        st.markdown("### Export")
        st.caption("Download the filtered result set as CSV.")
        export_df = add_currency_columns(filtered_df, currency)
        csv = export_df.to_csv(index=False).encode("utf-8")
        safe_query = query.strip().replace(" ", "_").replace("/", "_").lower() or "scan"
        file_name = f"lootrader_{safe_query}_{currency['code'].lower()}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        st.download_button("Download CSV", csv, file_name=file_name, mime="text/csv", use_container_width=True)
        st.caption("Raw filtered data displayed below. USD columns are kept for reference and converted columns use your manual exchange rate.")
        st.dataframe(export_df, use_container_width=True, hide_index=True)

    with tab_about:
        st.markdown("### LootRadar identity")
        st.markdown(
            """
LootRadar scans current PC deals and turns them into a cleaner buying view.

This version adds a stronger visual identity, working quick scans, store icons, radar picks, cleaner cards, best deal per title, Steam links when available, manual currency conversion, and better comparison/export tools.
            """.strip()
        )
        st.info("Always verify the final price in the store before buying. Prices can change quickly.")

    st.markdown(
        f'<div class="footer-note">{APP_NAME} {APP_VERSION}. Prices and availability depend on provider response. Always verify the final store price before buying.</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
