import html
import math
from datetime import datetime
from typing import Any, Dict, List, Tuple
import pandas as pd
import requests
import streamlit as st

APP_NAME = "LootRadar"
CHEAPSHARK_BASE = "https://www.cheapshark.com/api/1.0"
CHEAPSHARK_REDIRECT = "https://www.cheapshark.com/redirect?dealID="

DLC_KEYWORDS = [
    "dlc", "season pass", "battle pass", "soundtrack", "ost", "upgrade",
    "cosmetic", "skin", "pack", "currency", "coins", "points", "addon",
    "add-on", "expansion pass", "starter pack", "bonus content"
]

DEFAULT_SEARCHES = [
    "Borderlands", "Tiny Tina", "Cyberpunk", "Elden Ring", "Baldur's Gate",
    "Doom", "Resident Evil", "Monster Hunter", "Final Fantasy", "Hades"
]

st.set_page_config(
    page_title=f"{APP_NAME} | Game Deal Finder",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #070a12;
            --panel: rgba(16, 22, 38, 0.82);
            --panel-strong: rgba(20, 29, 51, 0.96);
            --text: #f4f7fb;
            --muted: #a8b3c7;
            --green: #4dff9a;
            --purple: #9d7cff;
            --gold: #ffd166;
            --red: #ff5d73;
            --line: rgba(255,255,255,0.10);
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(77,255,154,.16), transparent 32%),
                radial-gradient(circle at top right, rgba(157,124,255,.16), transparent 34%),
                linear-gradient(135deg, #070a12 0%, #101629 55%, #080b14 100%);
            color: var(--text);
        }

        [data-testid="stSidebar"] {
            background: rgba(6, 10, 20, 0.92);
            border-right: 1px solid var(--line);
        }

        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 3rem;
            max-width: 1500px;
        }

        .hero {
            border: 1px solid rgba(255,255,255,.12);
            background:
                linear-gradient(135deg, rgba(16,22,38,.96), rgba(18,25,48,.86)),
                radial-gradient(circle at 12% 0%, rgba(77,255,154,.18), transparent 30%),
                radial-gradient(circle at 92% 10%, rgba(157,124,255,.20), transparent 32%);
            border-radius: 28px;
            padding: 28px 30px;
            box-shadow: 0 28px 80px rgba(0,0,0,.35);
            margin-bottom: 18px;
        }

        .brand-row {
            display: flex;
            align-items: center;
            gap: 14px;
            margin-bottom: 18px;
        }

        .radar-mark {
            width: 48px;
            height: 48px;
            border-radius: 999px;
            background:
                radial-gradient(circle, rgba(77,255,154,.90) 0 7%, transparent 8% 100%),
                conic-gradient(from 30deg, rgba(77,255,154,.12), rgba(77,255,154,.70), rgba(157,124,255,.18), rgba(77,255,154,.12));
            border: 1px solid rgba(77,255,154,.55);
            box-shadow: 0 0 30px rgba(77,255,154,.24);
            position: relative;
        }

        .radar-mark:before, .radar-mark:after {
            content: "";
            position: absolute;
            inset: 10px;
            border: 1px solid rgba(255,255,255,.28);
            border-radius: 999px;
        }

        .radar-mark:after {
            inset: 19px;
            border-color: rgba(255,255,255,.34);
        }

        .eyebrow {
            color: var(--green);
            font-weight: 800;
            letter-spacing: .14em;
            font-size: .75rem;
            text-transform: uppercase;
        }

        .hero h1 {
            font-size: clamp(2.3rem, 6vw, 5.2rem);
            line-height: .94;
            margin: 0;
            letter-spacing: -0.06em;
        }

        .hero p {
            max-width: 880px;
            color: var(--muted);
            font-size: 1.05rem;
            margin: 14px 0 0;
        }

        .hero-stats {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 12px;
            margin-top: 22px;
        }

        .stat-card {
            background: rgba(255,255,255,.055);
            border: 1px solid rgba(255,255,255,.09);
            border-radius: 18px;
            padding: 14px 15px;
        }

        .stat-card .label {
            color: var(--muted);
            font-size: .76rem;
            margin-bottom: 5px;
        }

        .stat-card .value {
            font-size: 1.25rem;
            font-weight: 900;
        }

        .quick-chip {
            display: inline-flex;
            align-items: center;
            border: 1px solid rgba(255,255,255,.12);
            background: rgba(255,255,255,.06);
            color: var(--text);
            border-radius: 999px;
            padding: 8px 13px;
            margin: 5px 6px 5px 0;
            font-size: .84rem;
        }

        .section-title {
            font-size: 1.18rem;
            font-weight: 900;
            margin: 8px 0 8px;
        }

        .deal-card {
            border: 1px solid rgba(255,255,255,.11);
            background: linear-gradient(180deg, rgba(17,25,45,.94), rgba(9,13,24,.94));
            border-radius: 24px;
            padding: 16px;
            box-shadow: 0 22px 50px rgba(0,0,0,.26);
            min-height: 100%;
        }

        .deal-top {
            display: grid;
            grid-template-columns: 96px 1fr;
            gap: 14px;
            align-items: start;
        }

        .deal-img {
            width: 96px;
            height: 96px;
            object-fit: cover;
            border-radius: 18px;
            background: rgba(255,255,255,.06);
            border: 1px solid rgba(255,255,255,.09);
        }

        .deal-title {
            font-size: 1.02rem;
            line-height: 1.17;
            font-weight: 900;
            margin: 1px 0 8px;
            color: #ffffff;
        }

        .store-line {
            color: var(--muted);
            font-size: .82rem;
            margin-bottom: 10px;
        }

        .badge-row {
            display: flex;
            flex-wrap: wrap;
            gap: 7px;
            margin: 9px 0 12px;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            padding: 5px 9px;
            border-radius: 999px;
            font-size: .72rem;
            font-weight: 800;
            border: 1px solid rgba(255,255,255,.12);
            background: rgba(255,255,255,.07);
            color: #dfe7f7;
        }

        .badge.green { color: #05130b; background: var(--green); border-color: rgba(77,255,154,.9); }
        .badge.purple { color: #fff; background: rgba(157,124,255,.35); border-color: rgba(157,124,255,.52); }
        .badge.gold { color: #211600; background: var(--gold); border-color: rgba(255,209,102,.82); }
        .badge.red { color: #fff; background: rgba(255,93,115,.35); border-color: rgba(255,93,115,.52); }

        .price-row {
            display: flex;
            align-items: baseline;
            gap: 9px;
            margin: 8px 0 5px;
        }

        .sale-price {
            color: var(--green);
            font-size: 1.65rem;
            font-weight: 950;
            letter-spacing: -0.04em;
        }

        .normal-price {
            color: var(--muted);
            text-decoration: line-through;
            font-size: .92rem;
        }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 8px;
            margin-top: 12px;
        }

        .metric {
            background: rgba(255,255,255,.045);
            border: 1px solid rgba(255,255,255,.08);
            border-radius: 15px;
            padding: 9px;
        }

        .metric .m-label {
            color: var(--muted);
            font-size: .68rem;
            margin-bottom: 3px;
        }

        .metric .m-value {
            font-weight: 900;
            font-size: .93rem;
        }

        .deal-note {
            color: #d8e0ef;
            background: rgba(77,255,154,.07);
            border: 1px solid rgba(77,255,154,.14);
            border-radius: 16px;
            padding: 10px 12px;
            font-size: .82rem;
            margin-top: 12px;
            min-height: 42px;
        }

        a.deal-btn {
            display: inline-flex;
            justify-content: center;
            width: 100%;
            margin-top: 13px;
            padding: 10px 12px;
            color: #06110a !important;
            background: linear-gradient(90deg, var(--green), #9cffcb);
            font-weight: 950;
            text-decoration: none !important;
            border-radius: 15px;
            box-shadow: 0 12px 28px rgba(77,255,154,.17);
        }

        .empty-box {
            border: 1px solid rgba(255,255,255,.10);
            background: rgba(255,255,255,.05);
            border-radius: 24px;
            padding: 28px;
            color: var(--muted);
        }

        .small-muted {
            color: var(--muted);
            font-size: .84rem;
        }

        div[data-testid="stMetricValue"] {
            color: #ffffff;
        }

        @media (max-width: 900px) {
            .hero-stats { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .deal-top { grid-template-columns: 74px 1fr; }
            .deal-img { width: 74px; height: 74px; }
            .metric-grid { grid-template-columns: 1fr; }
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


@st.cache_data(ttl=60 * 60, show_spinner=False)
def api_get(endpoint: str, params: Tuple[Tuple[str, Any], ...] = ()) -> Any:
    response = requests.get(
        f"{CHEAPSHARK_BASE}/{endpoint}",
        params=dict(params),
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=60 * 60 * 12, show_spinner=False)
def get_stores() -> Dict[str, str]:
    try:
        raw_stores = api_get("stores")
        stores = {}
        for store in raw_stores:
            if str(store.get("isActive", "1")) == "1":
                stores[str(store.get("storeID"))] = store.get("storeName", f"Store {store.get('storeID')}")
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
) -> List[Dict[str, Any]]:
    params = {
        "title": title,
        "pageSize": page_size,
        "pageNumber": 0,
        "sortBy": sort_by,
        "desc": 1 if desc else 0,
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
    if any(word in lower_title for word in ["bundle", "collection", "complete", "ultimate", "deluxe", "gold edition", "goty"]):
        return "Bundle / Edition"
    if any(word in lower_title for word in DLC_KEYWORDS):
        return "DLC / Add on"
    return "Base Game"


def deal_score(savings: float, deal_rating: float, sale_price: float, steam_rating: float) -> int:
    discount_points = min(max(savings, 0), 100) * 0.50
    rating_points = min(max(deal_rating, 0), 10) * 5 * 0.24
    player_points = min(max(steam_rating, 0), 100) * 0.16
    price_points = max(0, 100 - min(sale_price, 60) / 60 * 100) * 0.10
    return int(round(discount_points + rating_points + player_points + price_points))


def deal_verdict(score: int, savings: float, sale_price: float, category: str) -> Tuple[str, str]:
    if sale_price <= 0.01:
        return "Claim now", "Free or almost free. Grab it before it disappears."
    if score >= 85 and savings >= 75:
        return "Buy now", "Excellent discount and strong deal score."
    if score >= 75:
        return "Strong deal", "Good value right now, especially if this is on your wishlist."
    if category in {"DLC / Add on", "Season Pass"}:
        return "Check edition", "This looks like extra content. Compare it against complete editions first."
    if savings >= 50:
        return "Good discount", "Worth checking, but compare against other editions."
    return "Watch it", "Not bad, but this may be worth waiting for a deeper sale."


def normalize_deals(raw_deals: List[Dict[str, Any]], stores: Dict[str, str]) -> pd.DataFrame:
    rows = []
    for deal in raw_deals:
        title = str(deal.get("title", "Unknown game"))
        sale_price = safe_float(deal.get("salePrice"))
        normal_price = safe_float(deal.get("normalPrice"))
        savings = safe_float(deal.get("savings"))
        deal_rating = safe_float(deal.get("dealRating"))
        steam_rating = safe_float(deal.get("steamRatingPercent"))
        metacritic = safe_float(deal.get("metacriticScore"))
        store_id = str(deal.get("storeID", ""))
        category = classify_item(title)
        score = deal_score(savings, deal_rating, sale_price, steam_rating)
        verdict, note = deal_verdict(score, savings, sale_price, category)
        deal_id = str(deal.get("dealID", ""))
        rows.append(
            {
                "title": title,
                "store_id": store_id,
                "store": stores.get(store_id, f"Store {store_id}"),
                "sale_price": sale_price,
                "normal_price": normal_price,
                "savings": savings,
                "deal_rating": deal_rating,
                "steam_rating": steam_rating,
                "steam_rating_count": safe_float(deal.get("steamRatingCount")),
                "metacritic": metacritic,
                "thumb": deal.get("thumb", ""),
                "deal_id": deal_id,
                "game_id": str(deal.get("gameID", "")),
                "steam_app_id": str(deal.get("steamAppID", "")),
                "url": f"{CHEAPSHARK_REDIRECT}{deal_id}",
                "category": category,
                "deal_score": score,
                "verdict": verdict,
                "note": note,
            }
        )
    return pd.DataFrame(rows)


def money(value: float) -> str:
    if value <= 0.01:
        return "Free"
    return f"${value:,.2f}"


def render_hero(df: pd.DataFrame, query: str) -> None:
    if df.empty:
        total_deals = "0"
        best_discount = "0%"
        best_price = "—"
        best_store = "—"
    else:
        total_deals = str(len(df))
        best_discount = f"{df['savings'].max():.0f}%"
        best_row = df.sort_values(["sale_price", "deal_score"], ascending=[True, False]).iloc[0]
        best_price = money(float(best_row["sale_price"]))
        best_store = html.escape(str(best_row["store"]))

    st.markdown(
        f"""
        <div class="hero">
            <div class="brand-row">
                <div class="radar-mark"></div>
                <div>
                    <div class="eyebrow">Game deal scanner</div>
                    <h1>{APP_NAME}</h1>
                </div>
            </div>
            <p>Search PC game deals across tracked stores, compare discounts, filter by platform style and spot the best value before the sale disappears.</p>
            <div class="hero-stats">
                <div class="stat-card"><div class="label">Search</div><div class="value">{html.escape(query or 'Explore')}</div></div>
                <div class="stat-card"><div class="label">Deals found</div><div class="value">{total_deals}</div></div>
                <div class="stat-card"><div class="label">Best discount</div><div class="value">{best_discount}</div></div>
                <div class="stat-card"><div class="label">Lowest price</div><div class="value">{best_price} · {best_store}</div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_deal_card(row: pd.Series) -> None:
    title = html.escape(str(row["title"]))
    store = html.escape(str(row["store"]))
    category = html.escape(str(row["category"]))
    thumb = html.escape(str(row.get("thumb") or ""))
    url = html.escape(str(row["url"]))
    savings = float(row["savings"])
    score = int(row["deal_score"])
    deal_rating = float(row["deal_rating"])
    steam_rating = float(row["steam_rating"])
    metacritic = float(row["metacritic"])
    sale_price = float(row["sale_price"])
    normal_price = float(row["normal_price"])
    verdict = html.escape(str(row["verdict"]))
    note = html.escape(str(row["note"]))

    score_class = "green" if score >= 80 else "purple" if score >= 65 else "gold" if score >= 50 else "red"
    discount_class = "green" if savings >= 75 else "purple" if savings >= 50 else "gold"
    category_class = "purple" if category != "Base Game" else "green"

    image_html = (
        f'<img class="deal-img" src="{thumb}" alt="{title}">' if thumb else '<div class="deal-img"></div>'
    )

    st.markdown(
        f"""
        <div class="deal-card">
            <div class="deal-top">
                {image_html}
                <div>
                    <div class="deal-title">{title}</div>
                    <div class="store-line">{store} · PC deal</div>
                    <div class="badge-row">
                        <span class="badge {discount_class}">{savings:.0f}% OFF</span>
                        <span class="badge {score_class}">Score {score}/100</span>
                        <span class="badge {category_class}">{category}</span>
                    </div>
                </div>
            </div>

            <div class="price-row">
                <div class="sale-price">{money(sale_price)}</div>
                <div class="normal-price">{money(normal_price)}</div>
            </div>

            <div class="metric-grid">
                <div class="metric"><div class="m-label">Deal rating</div><div class="m-value">{deal_rating:.1f}/10</div></div>
                <div class="metric"><div class="m-label">Steam rating</div><div class="m-value">{steam_rating:.0f}%</div></div>
                <div class="metric"><div class="m-label">Metacritic</div><div class="m-value">{metacritic:.0f}</div></div>
            </div>

            <div class="deal-note"><strong>{verdict}:</strong> {note}</div>
            <a class="deal-btn" href="{url}" target="_blank" rel="noopener noreferrer">View deal</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_quick_searches() -> None:
    st.markdown('<div class="section-title">Quick scans</div>', unsafe_allow_html=True)
    chip_html = "".join([f'<span class="quick-chip">{html.escape(item)}</span>' for item in DEFAULT_SEARCHES])
    st.markdown(chip_html, unsafe_allow_html=True)


def apply_filters(
    df: pd.DataFrame,
    selected_stores: List[str],
    selected_categories: List[str],
    min_discount: int,
    max_price: float,
    min_score: int,
    clean_mode: bool,
) -> pd.DataFrame:
    filtered = df.copy()
    if selected_stores:
        filtered = filtered[filtered["store"].isin(selected_stores)]
    if selected_categories:
        filtered = filtered[filtered["category"].isin(selected_categories)]
    filtered = filtered[filtered["savings"] >= min_discount]
    filtered = filtered[filtered["sale_price"] <= max_price]
    filtered = filtered[filtered["deal_score"] >= min_score]
    if clean_mode:
        filtered = filtered[filtered["category"].isin(["Base Game", "Bundle / Edition"])]
    return filtered


def favorites_panel(df: pd.DataFrame) -> None:
    if "favorites" not in st.session_state:
        st.session_state.favorites = []

    st.markdown("### Vault")
    st.caption("Temporary favorites saved only during this session.")

    if df.empty:
        st.info("Search first to add deals to your vault.")
        return

    options = {
        f"{row.title} · {row.store} · {money(row.sale_price)}": row.deal_id
        for row in df.itertuples()
    }
    pick = st.selectbox("Add deal", [""] + list(options.keys()))
    if st.button("Add to Vault", use_container_width=True, disabled=not pick):
        deal_id = options[pick]
        if deal_id not in st.session_state.favorites:
            st.session_state.favorites.append(deal_id)
            st.success("Added to Vault.")
        else:
            st.info("Already in Vault.")

    favorite_df = df[df["deal_id"].isin(st.session_state.favorites)]
    if favorite_df.empty:
        st.caption("Your Vault is empty.")
    else:
        st.dataframe(
            favorite_df[["title", "store", "sale_price", "savings", "deal_score", "url"]],
            use_container_width=True,
            hide_index=True,
        )
        if st.button("Clear Vault", use_container_width=True):
            st.session_state.favorites = []
            st.rerun()


def main() -> None:
    inject_css()

    stores = get_stores()

    with st.sidebar:
        st.markdown("## LootRadar Controls")
        query = st.text_input("Search game", value="Borderlands", placeholder="Borderlands, Doom, Hades...")
        st.caption("V1 uses CheapShark data, focused on PC game deals.")

        sort_by = st.selectbox(
            "Sort from API",
            ["Deal Rating", "Savings", "Price", "Title", "Metacritic", "Reviews", "Release", "Store", "recent"],
            index=0,
        )
        desc = st.toggle("Descending order", value=True)
        on_sale_only = st.toggle("Only active sales", value=True)
        steamworks_only = st.toggle("Steam redeemable only", value=False)
        page_size = st.slider("Max results", 12, 60, 36, step=12)

        st.divider()
        st.markdown("### Filters")
        min_discount = st.slider("Minimum discount", 0, 95, 0, step=5)
        max_price = st.slider("Maximum price", 0.0, 100.0, 60.0, step=1.0)
        min_score = st.slider("Minimum deal score", 0, 100, 0, step=5)
        clean_mode = st.toggle("Clean Mode: hide most DLC and extras", value=True)

    raw_deals: List[Dict[str, Any]] = []
    error_message = None
    if query.strip():
        try:
            with st.spinner("Scanning deals..."):
                raw_deals = search_deals(query.strip(), page_size, sort_by, desc, on_sale_only, steamworks_only)
        except Exception as exc:
            error_message = str(exc)

    df = normalize_deals(raw_deals, stores) if raw_deals else pd.DataFrame()
    render_hero(df, query.strip())

    if error_message:
        st.error(f"Could not load deals right now: {error_message}")
        st.stop()

    render_quick_searches()

    if df.empty:
        st.markdown(
            """
            <div class="empty-box">
                No deals found yet. Try another title or turn off some filters.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.stop()

    categories = sorted(df["category"].dropna().unique().tolist())
    store_names = sorted(df["store"].dropna().unique().tolist())

    filter_col_1, filter_col_2, filter_col_3 = st.columns([1.2, 1.2, 1])
    with filter_col_1:
        selected_stores = st.multiselect("Store", store_names)
    with filter_col_2:
        selected_categories = st.multiselect("Content type", categories)
    with filter_col_3:
        local_sort = st.selectbox("Final sort", ["Deal Score", "Lowest Price", "Biggest Discount", "Store", "Title"])

    filtered_df = apply_filters(
        df,
        selected_stores,
        selected_categories,
        min_discount,
        max_price,
        min_score,
        clean_mode,
    )

    if local_sort == "Deal Score":
        filtered_df = filtered_df.sort_values(["deal_score", "savings"], ascending=[False, False])
    elif local_sort == "Lowest Price":
        filtered_df = filtered_df.sort_values(["sale_price", "deal_score"], ascending=[True, False])
    elif local_sort == "Biggest Discount":
        filtered_df = filtered_df.sort_values(["savings", "deal_score"], ascending=[False, False])
    elif local_sort == "Store":
        filtered_df = filtered_df.sort_values(["store", "title"], ascending=[True, True])
    else:
        filtered_df = filtered_df.sort_values(["title", "deal_score"], ascending=[True, False])

    metric_1, metric_2, metric_3, metric_4 = st.columns(4)
    metric_1.metric("Visible deals", len(filtered_df))
    metric_2.metric("Stores", filtered_df["store"].nunique() if not filtered_df.empty else 0)
    metric_3.metric("Top discount", f"{filtered_df['savings'].max():.0f}%" if not filtered_df.empty else "0%")
    metric_4.metric("Best score", f"{filtered_df['deal_score'].max():.0f}/100" if not filtered_df.empty else "0/100")

    tab_deals, tab_compare, tab_vault, tab_data = st.tabs(["Radar", "Compare", "Vault", "Data"])

    with tab_deals:
        if filtered_df.empty:
            st.markdown(
                """
                <div class="empty-box">
                    No deals match your filters. Lower the discount, price or score filters.
                </div>
                """,
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
                            render_deal_card(filtered_df.iloc[deal_index])

    with tab_compare:
        st.markdown("### Compare current results")
        st.caption("Useful for franchises with base games, bundles, season passes and DLCs mixed together.")
        compare_cols = ["title", "category", "store", "sale_price", "normal_price", "savings", "deal_score", "deal_rating", "steam_rating", "metacritic", "url"]
        st.dataframe(
            filtered_df[compare_cols],
            use_container_width=True,
            hide_index=True,
            column_config={
                "sale_price": st.column_config.NumberColumn("Sale price", format="$%.2f"),
                "normal_price": st.column_config.NumberColumn("Normal price", format="$%.2f"),
                "savings": st.column_config.NumberColumn("Discount", format="%.0f%%"),
                "deal_score": st.column_config.ProgressColumn("Deal Score", min_value=0, max_value=100),
                "url": st.column_config.LinkColumn("Deal link"),
            },
        )

    with tab_vault:
        favorites_panel(filtered_df)

    with tab_data:
        st.markdown("### Export")
        st.caption("Download the filtered result set as CSV.")
        csv = filtered_df.to_csv(index=False).encode("utf-8")
        file_name = f"lootrader_{query.strip().replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        st.download_button("Download CSV", csv, file_name=file_name, mime="text/csv", use_container_width=True)
        st.caption("Raw data displayed below.")
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    st.markdown(
        """
        <div class="small-muted" style="margin-top: 24px;">
            LootRadar V1. Prices and availability depend on the provider response. Always verify the final price in the store before buying.
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
