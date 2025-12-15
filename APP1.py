# ============================================================
# PART 1 — HEADER + LOAD MODELS 
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import joblib, pickle
from pathlib import Path

st.set_page_config(page_title="H&M Recommender", layout="wide")

BASE = Path(".")
MODELS_DIR = BASE / "models"
DATA_DIR = BASE / "data" / "h-and-m-personalized-fashion-recommendations"
IMAGES_DIR = DATA_DIR / "images"

# Use your logo from models/
LOGO_PATH = MODELS_DIR / "hm_logo.png"

ARTICLES_CSV = DATA_DIR / "articles.csv"
USER_ENCODER_PATH = MODELS_DIR / "user_encoder.joblib"
ITEM_ENCODER_PATH = MODELS_DIR / "item_encoder.joblib"
ALS_MODEL_PATH = MODELS_DIR / "als_model.pkl"
CO_PURCHASE_PATH = MODELS_DIR / "co_purchase.joblib"
CANDIDATES_PATH = MODELS_DIR / "candidates.joblib"
USER_SUMMARY_PATH = MODELS_DIR / "user_summary.parquet"

N_RECS = 12
N_ALSO_BOUGHT = 5


# ------------------ HELPERS ------------------
def pad10(x):
    try:
        return str(int(x)).zfill(10)
    except:
        return str(x).zfill(10)

def safe_joblib(path):
    try:
        return joblib.load(path) if path.exists() else None
    except:
        return None

def safe_pickle(path):
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except:
        return None

def image_path(article_id):
    article_id = pad10(article_id)
    folder = article_id[:3]
    p1 = IMAGES_DIR / folder / f"{article_id}.jpg"
    p2 = IMAGES_DIR / folder / f"{article_id}.png"
    if p1.exists(): return str(p1)
    if p2.exists(): return str(p2)
    return None


# ------------------ LOAD ALL ARTIFACTS ------------------
@st.cache_resource
def load_artifacts():
    art = {}

    # articles.csv
    if ARTICLES_CSV.exists():
        df = pd.read_csv(ARTICLES_CSV, dtype=str)

        # FIXED: must use .str.zfill instead of .zfill
        df["article_id"] = df["article_id"].astype(str).str.zfill(10)

        df["price_numeric"] = pd.to_numeric(df.get("price", np.nan), errors="coerce")

        text_cols = [
            "product_name", "prod_name", "product_type_name", "product_group_name",
            "perceived_colour_master_name", "colour", "detail_desc", "garment_group_name"
        ]
        for c in text_cols:
            if c not in df.columns:
                df[c] = ""

        df["_search_text"] = df[text_cols].fillna("").agg(" ".join, axis=1).str.lower()
        art["articles_df"] = df
    else:
        art["articles_df"] = pd.DataFrame()

    # models
    art["user_encoder"] = safe_joblib(USER_ENCODER_PATH)
    art["item_encoder"] = safe_joblib(ITEM_ENCODER_PATH)
    art["als_model"] = safe_pickle(ALS_MODEL_PATH)
    art["co_purchase"] = safe_joblib(CO_PURCHASE_PATH) or {}
    art["candidates"] = safe_joblib(CANDIDATES_PATH) or {}

    # user summary
    if USER_SUMMARY_PATH.exists():
        us = pd.read_parquet(USER_SUMMARY_PATH)
        us.index = us.index.astype(str)
        if "last_5_items" in us.columns:
            us["last_5_items"] = us["last_5_items"].apply(
                lambda lst: [pad10(x) for x in lst] if isinstance(lst, list) else []
            )
        art["user_summary"] = us
    else:
        art["user_summary"] = pd.DataFrame()

    return art


# Load all artifacts
loaded = load_artifacts()
articles_df = loaded["articles_df"]
user_encoder = loaded["user_encoder"]
item_encoder = loaded["item_encoder"]
als_model = loaded["als_model"]
co_purchase = loaded["co_purchase"]
candidates = loaded["candidates"]
user_summary = loaded["user_summary"]

item_factors = getattr(als_model, "item_factors", None)
user_factors = getattr(als_model, "user_factors", None)
# ============================================================
# SUPER PREMIUM H&M THEME — PRIYANK SIGNATURE EDITION
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif !important;
    letter-spacing: 0.3px !important;
}

/* -----------------------------------------------------------
   FLOATING GLASS HEADER
----------------------------------------------------------- */
.hm-title {
    font-weight:900;
    color:#D90429;
    font-size:56px;
    text-align:center;
    margin-top:10px;
    text-transform:uppercase;
    letter-spacing:3px;
    backdrop-filter: blur(6px);
}

.hm-sub {
    text-align:center;
    color:#333;
    font-size:17px;
    margin-top:-18px;
    text-transform:uppercase;
    letter-spacing:2px;
}

/* -----------------------------------------------------------
   BASE BODY LOOK — clean white + subtle fade-in
----------------------------------------------------------- */
body {
    background-color: #ffffff !important;
}
.reportview-container {
    animation: fadein 0.7s ease-in-out;
}
@keyframes fadein {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; }
}

/* -----------------------------------------------------------
   PREMIUM PRODUCT CARD — GLASS, HOVER, SHADOW, ANIMATION
----------------------------------------------------------- */
div[data-testid="column"] {
    background: rgba(255,255,255,0.7);
    border-radius: 22px !important;
    padding: 18px !important;
    box-shadow: 0px 8px 28px rgba(0,0,0,0.08) !important;
    backdrop-filter: blur(10px);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

div[data-testid="column"]:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0px 14px 40px rgba(0,0,0,0.15) !important;
}

/* -----------------------------------------------------------
   IMAGE PREMIUM MASK + SOFT SHADOW
----------------------------------------------------------- */
img {
    border-radius: 16px !important;
    box-shadow: 0px 4px 18px rgba(0,0,0,0.12);
    transition: transform 0.25s ease;
}

img:hover {
    transform: scale(1.03);
}

/* -----------------------------------------------------------
   BUTTONS — H&M SUPREME RED + ANIMATION
----------------------------------------------------------- */
.stButton>button {
    background: linear-gradient(135deg, #D90429, #b10321) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 26px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stButton>button:hover {
    transform: scale(1.07);
    box-shadow: 0px 8px 20px rgba(217, 4, 41, 0.4);
}

/* Add-to-cart pulse */
.stButton>button:active {
    transform: scale(0.92);
    box-shadow: 0px 0px 0px rgba(0,0,0,0);
}

/* -----------------------------------------------------------
   INPUT BOXES — PREMIUM DESIGN
----------------------------------------------------------- */
input {
    border-radius: 12px !important;
    border: 2px solid #E2E2E2 !important;
    padding: 12px !important;
    font-size: 16px !important;
    transition: box-shadow 0.2s ease, border 0.2s ease;
}

input:focus {
    border: 2px solid #D90429 !important;
    box-shadow: 0 0 0 4px rgba(217,4,41,0.2) !important;
}

/* -----------------------------------------------------------
   EXPANDER STYLING
----------------------------------------------------------- */
.streamlit-expanderHeader {
    font-weight:600 !important;
    font-size:16px !important;
    color:#333 !important;
}

/* -----------------------------------------------------------
   SIDEBAR — GLASS, SHADOW, PREMIUM LOOK
----------------------------------------------------------- */
section[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.65) !important;
    backdrop-filter: blur(14px);
    border-right: 1px solid #eee !important;
}

section[data-testid="stSidebar"] .stMarkdown p {
    font-size: 15px !important;
    font-weight: 500 !important;
}

/* -----------------------------------------------------------
   CART BADGE ICON STYLE (SUPER PREMIUM)
----------------------------------------------------------- */
.sidebar-content::after {
    content: "";
    position: absolute;
    top: 12px;
    right: 18px;
    width: 12px;
    height: 12px;
    background: #D90429;
    border-radius: 50%;
}

/* -----------------------------------------------------------
   SECTION TITLES — PREMIUM LETTER-SPACING
----------------------------------------------------------- */
h3, .stMarkdown h3 {
    letter-spacing: 2px !important;
    font-weight: 700 !important;
    color: #111 !important;
}

/* -----------------------------------------------------------
   SMOOTH FADE-IN FOR RESULT CARDS
----------------------------------------------------------- */
div[data-testid="column"] {
    animation: fadeUp 0.5s ease;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}

</style>
""", unsafe_allow_html=True)


# ------------------ HEADER UI (CENTERED & BIGGER) ------------------

st.markdown("""
<style>
.hm-title {
    font-weight:900;
    color:#D90429;
    font-size:48px;       /* Bigger title */
    text-align:center;    /* Perfect center */
}
.hm-sub {
    text-align:center;
    color:#666;
    margin-top:-12px;
}
</style>
""", unsafe_allow_html=True)

# 3 equal columns to center the title perfectly
header_left, header_center, header_right = st.columns([3,6,3])

with header_left:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=120, use_container_width=False)
    else:
        st.markdown("<h2 style='color:#D90429;'>H&M</h2>", unsafe_allow_html=True)

with header_center:
    st.markdown("<div class='hm-title'>H&M RECOMMENDER</div>", unsafe_allow_html=True)
    st.markdown("<div class='hm-sub'>Personalized fashion picks</div>", unsafe_allow_html=True)

with header_right:
    st.write("")  # keeps middle column perfectly centered
# ============================================================
# PART 2 — SEARCH + CUSTOMER INPUT (Perfect Alignment)
# ============================================================

# ---------- CSS to ensure exact alignment ----------
st.markdown("""
<style>
.input-row {
    display: flex;
    gap: 12px;
    width: 100%;
    align-items: center;
}
.input-row input {
    height: 48px !important;
    font-size: 16px;
}
.stButton>button {
    height: 48px !important;
    margin-top: 0px !important;
    
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# SEARCH BAR ROW (Input + Search Button on SAME LINE)
# ============================================================
with st.container():
    st.markdown("<div class='input-row'>", unsafe_allow_html=True)

    search_query = st.text_input(
        " ", 
        placeholder="Search trousers, jeans, red, dress...",
        key="search_box"
    )

    search_clicked = st.button("Search", key="search_btn")

    st.markdown("</div>", unsafe_allow_html=True)


st.markdown("---")


# ============================================================
# CUSTOMER ID ROW (Input + Get Recommendations Button SAME LINE)
# ============================================================
st.markdown("### Customer ID")

with st.container():
    st.markdown("<div class='input-row'>", unsafe_allow_html=True)

    customer_id = st.text_input(
        " ",
        placeholder="Enter customer ID here...",
        key="customer_id_box"
    )

    get_recs_clicked = st.button("Get Recommendations", key="get_recs_btn")

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# SESSION VARIABLES
# ============================================================
if "cart" not in st.session_state:
    st.session_state["cart"] = []

if "last_recs" not in st.session_state:
    st.session_state["last_recs"] = []

if "last_also" not in st.session_state:
    st.session_state["last_also"] = []


# ============================================================
# SEARCH FUNCTION
# ============================================================
def do_search(q, top_k=12):
    if articles_df.empty:
        return []
    q = q.strip().lower()
    if q == "":
        return []
    mask = articles_df["_search_text"].str.contains(q, na=False)
    res = articles_df[mask]
    return [pad10(a) for a in res["article_id"].head(top_k)]


search_results = []
if search_clicked and search_query:
    search_results = do_search(search_query)
# ============================================================
# PART 3 — RECOMMENDATIONS + USERS ALSO BOUGHT + PRODUCT CARDS
# ============================================================


# ============================================================
# ALS RECOMMEND FUNCTION
# ============================================================
def recommend_als_for_user(cid, top_k=12):
    if user_encoder is None or item_encoder is None:
        return []

    try:
        enc_u = user_encoder.transform([cid])[0]
    except:
        return []

    if enc_u < 0 or enc_u >= user_factors.shape[0]:
        return []

    u_vec = user_factors[enc_u]
    scores = item_factors.dot(u_vec)

    # mask last bought items
    if cid in user_summary.index:
        last = user_summary.loc[cid, "last_5_items"]
        for item in last:
            try:
                enc_i = item_encoder.transform([item])[0]
                scores[enc_i] = -999999
            except:
                pass

    idx = np.argsort(-scores)[:top_k]
    dec = item_encoder.inverse_transform(idx)
    return [pad10(x) for x in dec]


# ============================================================
# BUILD MAIN RECOMMENDATIONS
# ============================================================
def get_recommendations(cid, N=12):
    # 1 — Precomputed Candidates
    if cid in candidates:
        raw = candidates[cid][:N]
        return [pad10(x) for x in raw]

    # 2 — ALS
    als_out = recommend_als_for_user(cid, N)
    if als_out:
        return als_out

    # 3 — Popular fallback
    if not articles_df.empty:
        return list(articles_df["article_id"].head(N))

    return []


# ============================================================
# USERS ALSO BOUGHT — OPTION B LOGIC
# Customer → if empty → rec-based → if empty → popular
# ============================================================
def users_also_bought(cid, k=5):

    # STEP 1 — Customer last_5_items → co_purchase
    if cid in user_summary.index:
        last = user_summary.loc[cid, "last_5_items"]
        out = []
        for item in last:
            if item in co_purchase:
                for r in co_purchase[item][:k]:
                    if isinstance(r, tuple):
                        out.append(pad10(r[0]))
                    else:
                        out.append(pad10(r))
        out = list(dict.fromkeys(out))   # unique
        if len(out) >= k:
            return out[:k]

    # STEP 2 — If empty → use recommendations
    recs = get_recommendations(cid, N_RECS)
    out = []
    for r in recs:
        if r in co_purchase:
            for x in co_purchase[r][:k]:
                out.append(pad10(x[0] if isinstance(x, tuple) else x))
    out = list(dict.fromkeys(out))
    if len(out) >= k:
        return out[:k]

    # STEP 3 — Fallback popular items
    return list(articles_df["article_id"].head(k))


# ============================================================
# SHOW PRODUCT CARD
# ============================================================
def show_product_card(aid):
    col = st.container()

    # image
    img = image_path(aid)
    if img:
        col.image(img, use_container_width=True)

    # details
    row = None
    if not articles_df.empty:
        try:
            row = articles_df[articles_df["article_id"] == aid].iloc[0]
        except:
            row = None

    if row is not None:
        name = row.get("product_name") or row.get("prod_name") or f"Article {aid}"
        color = row.get("perceived_colour_master_name") or ""
        price = row.get("price_numeric")
    else:
        name = f"Article {aid}"
        color = ""
        price = None

    col.markdown(f"**{name}**")
    if color:
        col.markdown(f"*{color}*")

    if price is not None and not np.isnan(price):
        col.markdown(f"**₹ {price:.2f}**")
    else:
        col.markdown("Price not available")

    # Add to cart
    if col.button(f"Add to cart {aid}", key=f"add_{aid}"):
        if aid not in st.session_state["cart"]:
            st.session_state["cart"].append(aid)
            st.success("Added to cart")

    # View details
    with col.expander("View details"):
        if row is not None:
            for key in ["product_name", "product_type_name", "product_group_name",
                        "garment_group_name", "detail_desc", "colour",
                        "perceived_colour_master_name"]:
                if key in row and isinstance(row[key], str) and row[key].strip():
                    st.write(f"**{key.replace('_',' ').title()}:** {row[key]}")
        else:
            st.write("No details available.")


# ============================================================
# GET RECOMMENDATIONS TRIGGER
# ============================================================
recs = []
also_bought = []

if get_recs_clicked and customer_id:
    with st.spinner("Generating recommendations..."):
        recs = get_recommendations(customer_id, N_RECS)
        also_bought = users_also_bought(customer_id, N_ALSO_BOUGHT)
        st.session_state["last_recs"] = recs
        st.session_state["last_also"] = also_bought


# ============================================================
# DISPLAY SEARCH RESULTS
# ============================================================
if search_results:
    st.subheader(f"Search results for '{search_query}'")
    cols = st.columns(4)
    for i, aid in enumerate(search_results):
        with cols[i % 4]:
            show_product_card(aid)

else:
    # ============================================================
    # DISPLAY RECOMMENDATIONS
    # ============================================================
    st.subheader("Recommendations")
    recs = st.session_state.get("last_recs", [])

    if not recs:
        st.info("Enter Customer ID and click Get Recommendations")
    else:
        cols = st.columns(4)
        for i, aid in enumerate(recs):
            with cols[i % 4]:
                show_product_card(aid)

    # ============================================================
    # DISPLAY USERS ALSO BOUGHT
    # ============================================================
    also_list = st.session_state.get("last_also", [])
    if also_list:
        st.markdown("---")
        st.subheader("Users also bought")
        cols2 = st.columns(5)
        for i, aid in enumerate(also_list):
            with cols2[i % 5]:
                show_product_card(aid)


# ============================================================
# SIDEBAR CART
# ============================================================
st.sidebar.header("🛒 Cart")

cart = st.session_state["cart"]

if cart:
    for a in cart:
        st.sidebar.write(f"- {a}")
    if st.sidebar.button("Clear cart"):
        st.session_state["cart"] = []
        st.sidebar.success("Cart cleared")
else:
    st.sidebar.write("Cart is empty")


# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.caption("H&M Personalized Recommendations — Streamlit")
