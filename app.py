import streamlit as st
import pandas as pd
from datetime import date, timedelta
from supabase import create_client

# The Soap Lab v2.1.4 — Clean navigation, theme refresh, product photo fields
st.set_page_config(page_title="The Soap Lab", layout="wide", initial_sidebar_state="expanded")

THEMES = {
    "Lavender": {"accent": "#7C3AED", "dark": "#5B21B6", "soft": "#EDE9FE", "pale": "#FAF7FF", "sidebar": "#F3E8FF", "border": "#DDD6FE"},
    "Rose": {"accent": "#BE5B7D", "dark": "#8A3551", "soft": "#FCE7F0", "pale": "#FFF7FA", "sidebar": "#FBE7EF", "border": "#F5C2D7"},
    "Ocean": {"accent": "#2563EB", "dark": "#1D4ED8", "soft": "#DBEAFE", "pale": "#F8FBFF", "sidebar": "#EFF6FF", "border": "#BFDBFE"},
    "Forest": {"accent": "#059669", "dark": "#047857", "soft": "#D1FAE5", "pale": "#F7FFFB", "sidebar": "#ECFDF5", "border": "#A7F3D0"},
    "Citrus": {"accent": "#EA580C", "dark": "#C2410C", "soft": "#FFEDD5", "pale": "#FFF7ED", "sidebar": "#FFF1E6", "border": "#FED7AA"},
    "Red": {"accent": "#DC2626", "dark": "#991B1B", "soft": "#FEE2E2", "pale": "#FFF8F8", "sidebar": "#FEF2F2", "border": "#FECACA"},
}

if "app_theme" not in st.session_state:
    st.session_state.app_theme = "Lavender"

_theme = THEMES.get(st.session_state.app_theme, THEMES["Lavender"])
PINK = _theme["accent"]
PINK_DARK = _theme["dark"]
PINK_SOFT = _theme["soft"]
PINK_PALE = _theme["pale"]
SIDEBAR_BG = _theme["sidebar"]
SIDEBAR_BORDER = _theme["border"]
TEXT = "#111827"
MUTED = "#4B5563"
BORDER = "#E5E7EB"
CARD = "#FFFFFF"

st.markdown(f"""
<style>
/* GLOBAL */
html, body, .stApp {{
    background: {PINK_PALE} !important;
    color: {TEXT} !important;
}}

* {{
    color: {TEXT} !important;
}}

h1, h2, h3, h4, h5, h6 {{
    color: {TEXT} !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em;
}}

p, span, label, div {{
    color: {TEXT} !important;
}}

/* SIDEBAR */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {SIDEBAR_BG} 0%, {PINK_PALE} 100%) !important;
    border-right: 1px solid {SIDEBAR_BORDER} !important;
}}

section[data-testid="stSidebar"] * {{
    color: {TEXT} !important;
}}

section[data-testid="stSidebar"] h1 {{
    color: {PINK_DARK} !important;
    font-size: 1.8rem !important;
}}

/* RADIO NAV */
div[role="radiogroup"] label {{
    background: transparent !important;
    border-radius: 12px !important;
    padding: 8px 10px !important;
}}

div[role="radiogroup"] label:hover {{
    background: {PINK_SOFT} !important;
}}

/* FORMS AND INPUTS */
.stTextInput label,
.stNumberInput label,
.stTextArea label,
.stSelectbox label,
.stCheckbox label {{
    color: {TEXT} !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
}}

input, textarea {{
    background-color: #FFFFFF !important;
    color: {TEXT} !important;
    border: 1px solid #D1D5DB !important;
    border-radius: 10px !important;
}}

input::placeholder, textarea::placeholder {{
    color: #6B7280 !important;
}}

[data-baseweb="input"],
[data-baseweb="textarea"],
[data-baseweb="select"] > div {{
    background-color: #FFFFFF !important;
    color: {TEXT} !important;
    border-color: #D1D5DB !important;
    border-radius: 10px !important;
}}

[data-baseweb="input"] *,
[data-baseweb="textarea"] *,
[data-baseweb="select"] * {{
    color: {TEXT} !important;
    background-color: transparent !important;
}}

/* NUMBER INPUT BUTTONS */
button[kind="secondary"] {{
    background-color: #FFFFFF !important;
    color: {TEXT} !important;
    border: 1px solid #D1D5DB !important;
}}

div[data-testid="stNumberInput"] button,
div[data-testid="stNumberInput"] button[kind="secondary"] {{
    background-color: #FFFFFF !important;
    color: #111827 !important;
    border-color: #D1D5DB !important;
}}

div[data-testid="stNumberInput"] button *,
div[data-testid="stNumberInput"] svg {{
    color: #111827 !important;
    fill: #111827 !important;
    stroke: #111827 !important;
}}

/* CLEAN BUTTON SYSTEM */
.stButton button,
.stFormSubmitButton button {{
    background: #FFFFFF !important;
    color: {PINK_DARK} !important;
    border-radius: 10px !important;
    border: 1px solid {SIDEBAR_BORDER} !important;
    font-weight: 700 !important;
    padding: 0.55rem 0.95rem !important;
    box-shadow: 0 2px 8px rgba(17,24,39,0.04) !important;
}}

.stButton button:hover,
.stFormSubmitButton button:hover {{
    background: {PINK_SOFT} !important;
    color: {PINK_DARK} !important;
    border-color: {PINK} !important;
}}

.stFormSubmitButton button {{
    background: {PINK} !important;
    color: #FFFFFF !important;
    border-color: {PINK} !important;
}}

.stFormSubmitButton button:hover {{
    background: {PINK_DARK} !important;
    color: #FFFFFF !important;
}}

/* METRIC CARDS */
div[data-testid="stMetric"] {{
    background: {CARD} !important;
    padding: 20px !important;
    border-radius: 16px !important;
    border: 1px solid {BORDER} !important;
    box-shadow: 0 6px 18px rgba(17,24,39,0.05) !important;
}}

div[data-testid="stMetric"] * {{
    color: {TEXT} !important;
}}

div[data-testid="stMetricValue"] {{
    color: {PINK_DARK} !important;
    font-weight: 800 !important;
}}

/* ALERTS */
div[data-testid="stAlert"] {{
    border-radius: 12px !important;
}}

div[data-testid="stAlert"] * {{
    color: {TEXT} !important;
}}

/* TABLES */
[data-testid="stDataFrame"] {{
    background: #FFFFFF !important;
    border-radius: 14px !important;
    border: 1px solid {BORDER} !important;
    overflow: hidden !important;
}}

/* EXPANDERS / FORM AREAS */
.streamlit-expanderHeader {{
    color: {TEXT} !important;
    font-weight: 700 !important;
}}

/* CAPTIONS AND SMALL TEXT */
small, .caption, [data-testid="stCaptionContainer"] * {{
    color: {MUTED} !important;
}}


/* Lighten number stepper controls so they do not show as black boxes */
[data-testid="stNumberInput"] button,
[data-testid="stNumberInput"] button * {{
    background-color: #FFFFFF !important;
    color: #111827 !important;
    border-color: #D1D5DB !important;
}}

/* V2 TOP NAV + CARDS */
.soap-topbar {{
    background: linear-gradient(90deg, {PINK_DARK} 0%, {PINK} 100%);
    color: white !important;
    padding: 18px 24px;
    border-radius: 18px;
    margin-bottom: 16px;
    box-shadow: 0 12px 30px rgba(17,24,39,0.10);
}}
.soap-topbar * {{ color: white !important; }}
.soap-brand {{
    font-size: 1.6rem;
    font-weight: 900;
    letter-spacing: -0.03em;
}}
.soap-subtle-card {{
    background: #FFFFFF;
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 8px 22px rgba(17,24,39,0.05);
}}
.soap-action-bar {{
    background: #FFFFFF;
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 12px;
    margin: 10px 0 18px 0;
}}
.soap-product-card {{
    background: #FFFFFF;
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 14px;
    min-height: 220px;
    box-shadow: 0 8px 22px rgba(17,24,39,0.05);
}}
.soap-product-photo {{
    width: 100%;
    height: 115px;
    object-fit: cover;
    border-radius: 12px;
    background: {PINK_SOFT};
    border: 1px solid {SIDEBAR_BORDER};
}}
.soap-placeholder-photo {{
    height: 115px;
    border-radius: 12px;
    background: {PINK_SOFT};
    border: 1px dashed {PINK};
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    color: {PINK_DARK} !important;
}}


/* v2.0.7 SIDEBAR SAFETY: keep Streamlit collapse/expand controls usable */
button[title="View fullscreen"],
button[title="Exit fullscreen"] {{ display: flex !important; }}
button[aria-label="Close sidebar"],
button[aria-label="Open sidebar"],
button[title="Close sidebar"],
button[title="Open sidebar"] {{
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 999999 !important;
}}
[data-testid="collapsedControl"] {{
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 999999 !important;
}}

/* v2.0.3 EXACT MOCKUP-STYLE NAVIGATION */
[data-testid="stHeader"] {{ background: transparent !important; }}
.block-container {{ padding-top: 1.15rem !important; max-width: 1600px !important; }}
.soap-app-shell-top {{
    background: linear-gradient(90deg, #A78BFA 0%, #8B5CF6 55%, #A78BFA 100%);
    min-height: 74px;
    border-radius: 0 0 0 0;
    margin: -1.15rem -3.8rem 1.35rem -3.8rem;
    padding: 14px 24px;
    display: flex;
    align-items: center;
    gap: 18px;
    box-shadow: 0 10px 30px rgba(91,33,182,.22);
}}
.soap-app-shell-top * {{ color: #FFFFFF !important; text-decoration: none !important; }}
.soap-brand-block {{ display:flex; align-items:center; gap:10px; min-width:220px; }}
.soap-logo-mark {{ font-size: 2.1rem; line-height:1; filter: drop-shadow(0 2px 8px rgba(0,0,0,.10)); }}
.soap-brand-script {{ font-size: 1.8rem; font-weight: 850; letter-spacing: -.04em; font-family: "Segoe Script", "Brush Script MT", cursive; white-space: nowrap; }}
.soap-main-nav {{ display:flex; align-items:center; gap: 6px; flex: 1; }}
.soap-nav-item {{
    display:inline-flex; align-items:center; gap:7px;
    padding: 11px 14px; border-radius: 10px;
    font-weight: 800; font-size: .92rem;
    opacity: .95; transition: all .15s ease;
}}
.soap-nav-item:hover, .soap-nav-item.active {{ background: rgba(255,255,255,.16); box-shadow: inset 0 0 0 1px rgba(255,255,255,.13); }}
.soap-nav-icon {{ font-size:1.05rem; }}
.soap-chevron {{ font-size:.75rem; opacity:.78; margin-left:2px; }}
.soap-top-search {{
    min-width: 215px; background: rgba(255,255,255,.88);
    color: #6D5B95 !important; border-radius: 9px;
    padding: 12px 14px; font-weight:700; font-size:.88rem;
    display:flex; justify-content:space-between; align-items:center;
}}
.soap-top-search span {{ color:#7C3AED !important; }}
.soap-user-pill {{ width:34px;height:34px;border-radius:999px;background:rgba(255,255,255,.25);display:flex;align-items:center;justify-content:center;font-weight:900; }}
.soap-subnav-wrap {{
    background:#FFFFFF; border:1px solid #E8E1FF; border-radius:14px;
    padding: 8px; margin: -5px 0 18px 0;
    box-shadow: 0 8px 24px rgba(91,33,182,.06);
    display:flex; gap:8px; flex-wrap:wrap;
}}
.soap-subnav-item {{
    padding: 9px 13px; border-radius:10px;
    color:#5B21B6 !important; font-weight:800; text-decoration:none !important;
}}
.soap-subnav-item:hover, .soap-subnav-item.active {{ background:#EDE9FE; }}
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #FFFFFF 0%, #FBF8FF 100%) !important;
    border-right: 1px solid #E8E1FF !important;
    box-shadow: 8px 0 24px rgba(91,33,182,.035);
}}
section[data-testid="stSidebar"] .stButton button {{
    background:#FFFFFF !important; color:#3B2B66 !important;
    border:1px solid #E8E1FF !important; border-radius:10px !important;
    box-shadow: 0 3px 12px rgba(91,33,182,.045) !important;
}}
section[data-testid="stSidebar"] .stButton button:hover {{ background:#F3E8FF !important; border-color:#C4B5FD !important; }}
.stButton button {{ border-radius: 10px !important; }}
div[data-testid="stMetric"] {{ border: 1px solid #E8E1FF !important; box-shadow: 0 10px 28px rgba(91,33,182,.055) !important; }}
.fg-status-badge {{ border-radius: 999px !important; padding: 5px 12px !important; }}
@media (max-width: 1150px) {{
    .soap-app-shell-top {{ flex-wrap: wrap; margin-left:-1rem; margin-right:-1rem; }}
    .soap-main-nav {{ order: 3; flex-basis: 100%; overflow-x:auto; }}
    .soap-top-search {{ flex:1; min-width:160px; }}
}}

</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
/* DROPDOWN / SELECT MENU FIX */
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
ul[role="listbox"],
div[role="listbox"],
[data-baseweb="menu"] {
    background-color: #FFFFFF !important;
    color: #111827 !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 12px !important;
}

li[role="option"],
div[role="option"] {
    background-color: #FFFFFF !important;
    color: #111827 !important;
}

li[role="option"] *,
div[role="option"] *,
[data-baseweb="menu"] * {
    color: #111827 !important;
}

li[role="option"]:hover,
div[role="option"]:hover,
li[aria-selected="true"],
div[aria-selected="true"] {
    background-color: #F3F4F6 !important;
    color: #111827 !important;
}

[data-baseweb="select"],
[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #111827 !important;
}

[data-baseweb="select"] *,
[data-baseweb="select"] input {
    color: #111827 !important;
}
</style>
""", unsafe_allow_html=True)




st.markdown("""
<style>
/* FINISHED GOODS STATUS BADGES / FORM CONTROL FIXES */
.fg-status-badge {
    display:inline-block;
    padding:4px 10px;
    border-radius:8px;
    font-size:0.82rem;
    font-weight:800;
    line-height:1;
    white-space:nowrap;
}
.fg-finished { background:#DCFCE7; color:#166534 !important; border:1px solid #86EFAC; }
.fg-curing { background:#FFEDD5; color:#C2410C !important; border:1px solid #FDBA74; }
.fg-review { background:#F3E8FF; color:#7E22CE !important; border:1px solid #D8B4FE; }
.fg-not-started { background:#E5E7EB; color:#374151 !important; border:1px solid #D1D5DB; }
.fg-plain-cell {
    display:inline-block;
    background:#FFFFFF !important;
    color:#111827 !important;
    border:1px solid #E5E7EB;
    border-radius:8px;
    padding:4px 8px;
    font-weight:700;
}

/* force number/date controls light */
div[data-baseweb="input"] button,
div[data-baseweb="input"] [role="button"] {
    background-color:#FFFFFF !important;
    color:#111827 !important;
    border-color:#D1D5DB !important;
}

/* make cure status radio look cleaner */
div[role="radiogroup"] label p {
    color:#111827 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Number input stepper fix */
div[data-testid="stNumberInput"] button {
    background-color: white !important;
    color: rgb(17, 24, 39) !important;
    border: 1px solid rgb(209, 213, 219) !important;
}
div[data-testid="stNumberInput"] button * {{
    color: rgb(17, 24, 39) !important;
}
</style>
""", unsafe_allow_html=True)




st.markdown("""
<style>
/* v1.4.0: keep number stepper buttons and small controls light/readable */
[data-testid="stNumberInput"] button,
[data-testid="stNumberInput"] button * {{
    background-color: #FFFFFF !important;
    color: #111827 !important;
    border-color: #D1D5DB !important;
}
[data-testid="stNumberInput"] input {
    background-color: #FFFFFF !important;
    color: #111827 !important;
}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

try:
    supabase = db()
except Exception:
    st.error("Add SUPABASE_URL and SUPABASE_KEY in Streamlit secrets first.")
    st.stop()

def df(table):
    try:
        return pd.DataFrame(supabase.table(table).select("*").execute().data)
    except Exception as e:
        st.error(f"Could not load {table}: {e}")
        return pd.DataFrame()

def insert(table, data):
    return supabase.table(table).insert(data).execute()

# Compatibility helpers for newer Inventory Manager code
def table_df(table):
    return df(table)

def safe_table_df(table):
    try:
        return table_df(table)
    except Exception:
        return pd.DataFrame()

def cost_per_unit(row):
    return cpu(row)

def insert_row(table, data):
    return insert(table, data)

def update_row(table, row_id, data):
    return supabase.table(table).update(data).eq("id", row_id).execute()

def delete_row(table, row_id):
    return supabase.table(table).delete().eq("id", row_id).execute()

def normalize_cure_status(value):
    allowed = ["Not Started", "Curing", "Cured", "Needs Review"]
    value = str(value or "").strip()
    v = value.lower().replace("_", " ").strip()
    if v in ["not started", "notstarted"]:
        return "Not Started"
    if v == "curing":
        return "Curing"
    if v in ["cured", "finished", "complete", "completed", "ready"]:
        return "Cured"
    if v in ["needs review", "review"]:
        return "Needs Review"
    return "Curing"

def update_finished_good_status(row_id, status, batch_id=None, batch_number=None):
    """Update the finished goods cure status without deleting or hiding inventory.

    For current installs, cure_status is the official field. For older / partially
    migrated installs, status is used as a fallback so the app can keep working.
    A sold version should run database migrations automatically during deployment.
    """
    status = normalize_cure_status(status)
    row_id = int(row_id)
    last_error = None

    # Try the current column first.
    try:
        supabase.table("finished_goods").update({"cure_status": status}).eq("id", row_id).execute()
    except Exception as e:
        last_error = e

    # Try fallback display/legacy column. This is also useful if cure_status exists
    # but the current app is reading status from a prior version.
    try:
        supabase.table("finished_goods").update({"status": status}).eq("id", row_id).execute()
    except Exception as e:
        if last_error is None:
            last_error = e

    # Optional helper flag. Missing column should not block a status update.
    try:
        supabase.table("finished_goods").update({"hide_from_cure_tracking": False}).eq("id", row_id).execute()
    except Exception:
        pass

    # Verify using whichever columns exist.
    try:
        verify = supabase.table("finished_goods").select("*").eq("id", row_id).execute()
    except Exception as e:
        st.error("The app could not re-read this finished goods line after saving.")
        st.code(str(e))
        return False, None

    verified_status = None
    if verify.data:
        record = verify.data[0]
        # Prefer status as a fallback because some partial installs can update it
        # even when cure_status remains stuck at an older value.
        verified_status = normalize_cure_status(record.get("status") or record.get("cure_status"))

    if verified_status != status:
        st.error("The status did not persist in Supabase.")
        st.caption("This is a database schema/RLS issue, not a button issue. For a production/sellable app, migrations should run automatically during setup/deployment instead of asking the user to paste SQL.")
        if last_error is not None:
            st.code(str(last_error))
        return False, verify

    # Best-effort batch sync. Finished Goods is the source of truth.
    if batch_id not in [None, "", "nan"]:
        try:
            supabase.table("batches").update({"cure_status": status}).eq("id", int(float(batch_id))).execute()
        except Exception:
            pass
    if batch_number not in [None, "", "nan"]:
        try:
            supabase.table("batches").update({"cure_status": status}).eq("batch_number", str(batch_number)).execute()
        except Exception:
            pass

    return True, verify

def cpu(row):
    q = float(row.get("quantity_purchased") or 0)
    t = float(row.get("total_cost") or 0)
    return t / q if q else 0

def recipe_lines(recipe_id):
    inv = df("inventory"); lines = df("recipe_lines")
    if inv.empty or lines.empty: return pd.DataFrame()
    lines = lines[lines["recipe_id"] == recipe_id]
    if lines.empty: return pd.DataFrame()
    m = lines.merge(inv, left_on="inventory_id", right_on="id", suffixes=("_line","_inv"))
    m["cost_per_unit"] = m.apply(cpu, axis=1)
    m["line_cost"] = m["amount_used"].astype(float) * m["cost_per_unit"]
    m["enough_inventory"] = m["current_quantity"].astype(float) >= m["amount_used"].astype(float)
    return m

def recipe_row(recipe_id):
    r = df("recipes")
    if r.empty: return None
    r = r[r["id"] == recipe_id]
    return r.iloc[0] if not r.empty else None

def cure_status_badge(status):
    status = str(status or "Curing")
    css_class = {
        "Cured": "fg-finished",
        "Finished": "fg-finished",
        "Curing": "fg-curing",
        "Needs Review": "fg-review",
        "Not Started": "fg-not-started",
    }.get(status, "fg-not-started")
    return f'<span class="fg-status-badge {css_class}">{status}</span>'


st.markdown("""
<style>

/* v2.0.5 native Streamlit top navigation */
.soap-real-nav-shell { margin-bottom: .65rem !important; }
.soap-subnav-label { font-size:.82rem; font-weight:900; color:#7C3AED !important; margin:.45rem 0 .25rem 0; text-transform:uppercase; letter-spacing:.04em; }
div[data-testid="stPopover"] button,
div[data-testid="stPopover"] button * { color:#3B2B66 !important; }

</style>
""", unsafe_allow_html=True)

NAV = {
    "Dashboard": ["Dashboard"],
    "Production": ["Batch Production", "Cure Tracking", "Finished Goods"],
    "Inventory": ["Inventory", "Fragrance Library", "Suppliers", "Categories", "Units"],
    "Products": ["Recipes", "Product Gallery", "Ingredient Label Generator", "Product Type View", "Can I Make This?", "Recipe Cost Summary"],
    "Sales": ["POS / Sales"],
    "Reports": ["Reports"],
    "Settings": ["My Settings"],
}

# v2.0.7: NO-LINK navigation. Every menu and quick action is a real Streamlit button/selectbox.
# There are no HTML anchors, hrefs, page_links, or link_buttons, so nothing can open a new browser tab.
if "active_section" not in st.session_state:
    st.session_state.active_section = "Dashboard"
if st.session_state.active_section not in NAV:
    st.session_state.active_section = "Dashboard"
if "active_subpage" not in st.session_state:
    st.session_state.active_subpage = NAV[st.session_state.active_section][0]
if st.session_state.active_subpage not in NAV[st.session_state.active_section]:
    st.session_state.active_subpage = NAV[st.session_state.active_section][0]

def go_to(section, subpage=None):
    st.session_state.active_section = section
    st.session_state.active_subpage = subpage or NAV[section][0]
    st.rerun()

st.markdown(f"""
<div class="soap-app-shell-top soap-real-nav-shell">
  <div class="soap-brand-block">
    <div class="soap-logo-mark">⚗</div>
    <div class="soap-brand-script">The Soap Lab</div>
  </div>
  <div class="soap-top-search">Search everything... <span>⌕</span></div>
  <div class="soap-user-pill">TS</div>
</div>
""", unsafe_allow_html=True)

# Functional top menu row
nav_cols = st.columns([1, 1, 1, 1, .9, .9, .9])
for col, section in zip(nav_cols, NAV.keys()):
    active_marker = "✓ " if st.session_state.active_section == section else ""
    label = f"{active_marker}{section}"
    if col.button(label, key=f"top_nav_btn_{section}", use_container_width=True):
        go_to(section, NAV[section][0])

subpages = NAV[st.session_state.active_section]
if len(subpages) > 1:
    st.markdown(f'<div class="soap-subnav-label">{st.session_state.active_section} Menu</div>', unsafe_allow_html=True)
    sub_cols = st.columns(min(len(subpages), 6))
    for i, sub in enumerate(subpages):
        col = sub_cols[i % len(sub_cols)]
        active_marker = "✓ " if st.session_state.active_subpage == sub else ""
        if col.button(f"{active_marker}{sub}", key=f"sub_nav_btn_{st.session_state.active_section}_{sub}", use_container_width=True):
            st.session_state.active_subpage = sub
            st.rerun()

page = st.session_state.active_subpage

st.sidebar.title("The Soap Lab")
st.sidebar.caption("v2.1.4")
st.sidebar.markdown("### Quick Actions")
if st.sidebar.button("+ New Recipe", key="quick_new_recipe", use_container_width=True):
    st.session_state.recipe_mode = "add"
    go_to("Products", "Recipes")
if st.sidebar.button("+ New Batch", key="quick_new_batch", use_container_width=True):
    go_to("Production", "Batch Production")
if st.sidebar.button("+ Add Inventory", key="quick_add_inventory", use_container_width=True):
    st.session_state.inventory_mode = "add"
    go_to("Inventory", "Inventory")
if st.sidebar.button("+ Record Sale", key="quick_record_sale", use_container_width=True):
    go_to("Sales", "POS / Sales")
st.sidebar.divider()
st.sidebar.markdown("### Main Menu")
for section, pages in NAV.items():
    if st.sidebar.button(section, key=f"side_nav_{section}", use_container_width=True):
        go_to(section, pages[0])
st.sidebar.divider()
st.sidebar.markdown("### Current Theme")
st.sidebar.write(st.session_state.get("app_theme", "Lavender"))

if page == "Dashboard":
    st.title("Dashboard")
    st.caption("Welcome back! Here is what is happening in your soap lab today.")
    inv, recipes, batches, goods, sales = df("inventory"), df("recipes"), df("batches"), df("finished_goods"), df("sales")
    raw_value = 0; finished_value = 0; retail_value = 0; ready_for_sale = 0; curing_count = 0; low_count = 0
    if not inv.empty:
        inv["cost_per_unit"] = inv.apply(cpu, axis=1)
        raw_value = (pd.to_numeric(inv.get("current_quantity", 0), errors="coerce").fillna(0) * pd.to_numeric(inv["cost_per_unit"], errors="coerce").fillna(0)).sum()
        if "reorder_point" in inv.columns:
            low_count = int((pd.to_numeric(inv["current_quantity"], errors="coerce").fillna(0) <= pd.to_numeric(inv["reorder_point"], errors="coerce").fillna(0)).sum())
    if not goods.empty:
        for col in ["quantity_on_hand", "cost_per_item", "retail_price", "cure_status", "status"]:
            if col not in goods.columns:
                goods[col] = 0 if col in ["quantity_on_hand", "cost_per_item", "retail_price"] else ""
        goods["display_status"] = goods["cure_status"].fillna("").astype(str)
        if "status" in goods.columns:
            goods["display_status"] = goods["display_status"].where(goods["display_status"].str.strip() != "", goods["status"].fillna(""))
        goods["display_status"] = goods["display_status"].apply(normalize_cure_status)
        qty_series = pd.to_numeric(goods["quantity_on_hand"], errors="coerce").fillna(0)
        finished_value = (qty_series * pd.to_numeric(goods["cost_per_item"], errors="coerce").fillna(0)).sum()
        retail_value = (qty_series * pd.to_numeric(goods["retail_price"], errors="coerce").fillna(0)).sum()
        ready_for_sale = int(qty_series[goods["display_status"] == "Cured"].sum())
        curing_count = int(qty_series[goods["display_status"] == "Curing"].sum())

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("Raw Inventory Value", f"${raw_value:,.2f}")
    c2.metric("Finished Goods Value", f"${finished_value:,.2f}")
    c3.metric("Retail Value", f"${retail_value:,.2f}")
    c4.metric("Ready for Sale", ready_for_sale)
    c5.metric("Currently Curing", curing_count)
    c6.metric("Low Stock", low_count)

    left, right = st.columns([1.05, 1])
    with left:
        st.markdown("### Recent Finished Goods")
        if goods.empty:
            st.info("No finished goods yet.")
        else:
            show = goods.copy()
            if "product_name" not in show.columns: show["product_name"] = ""
            if "batch_number" not in show.columns: show["batch_number"] = show.get("batch_id", "")
            for _, row in show.tail(6).iterrows():
                c = st.columns([1.6, .9, .9, .8])
                c[0].markdown(f"**{row.get('product_name') or 'Product'}**")
                c[1].write(row.get("batch_number") or "—")
                c[2].markdown(cure_status_badge(row.get("display_status") or row.get("cure_status") or "Curing"), unsafe_allow_html=True)
                c[3].write(int(row.get("quantity_on_hand") or 0))
                st.markdown("<hr style='margin:0.25rem 0;border:none;border-top:1px solid #eee;'>", unsafe_allow_html=True)
    with right:
        st.markdown("### Product Snapshot")
        if goods.empty:
            st.info("Product photos will appear here once you add finished goods.")
        else:
            cards = goods.drop_duplicates(subset=["product_name"]).head(4)
            cols = st.columns(2)
            for i, (_, row) in enumerate(cards.iterrows()):
                with cols[i % 2]:
                    photo = str(row.get("photo_url") or "").strip() if "photo_url" in row.index else ""
                    if photo:
                        st.markdown(f'<div class="soap-product-card"><img class="soap-product-photo" src="{photo}"><h4>{row.get("product_name") or "Product"}</h4><p>{int(row.get("quantity_on_hand") or 0)} available</p></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="soap-product-card"><div class="soap-placeholder-photo">Product Photo</div><h4>{row.get("product_name") or "Product"}</h4><p>{int(row.get("quantity_on_hand") or 0)} available</p></div>', unsafe_allow_html=True)

elif page == "Inventory":
    st.title("Inventory Manager")
    st.caption("Search, view, add, edit, delete, and report on your inventory.")

    df = table_df("inventory")
    inventory_categories = safe_table_df("inventory_categories")

    default_inventory_categories = [
        "Base Oils", "Butters", "Waxes", "Lye / Alkali", "Liquids",
        "Fragrance Oils", "Essential Oils", "Clays", "Colorants", "Additives",
        "Exfoliants", "Preservatives", "Emulsifiers", "Packaging", "Shipping",
        "Equipment", "Other"
    ]

    custom_inventory_categories = []
    if not inventory_categories.empty and "category_name" in inventory_categories.columns:
        custom_inventory_categories = inventory_categories["category_name"].dropna().astype(str).tolist()

    existing_inventory_categories = []
    if not df.empty and "category" in df.columns:
        existing_inventory_categories = df["category"].dropna().astype(str).unique().tolist()

    inventory_category_options = []
    for cat in default_inventory_categories + custom_inventory_categories + existing_inventory_categories:
        if cat and cat not in inventory_category_options:
            inventory_category_options.append(cat)

    if "active_inventory_category" not in st.session_state:
        st.session_state.active_inventory_category = "All"

    if "inventory_mode" not in st.session_state:
        st.session_state.inventory_mode = "list"
    if "selected_inventory_id" not in st.session_state:
        st.session_state.selected_inventory_id = None

    if not df.empty:
        for col in ["item_name", "category", "subcategory", "supplier", "label_display_name", "notes", "unit"]:
            if col not in df.columns:
                df[col] = ""
        for col in ["quantity_purchased", "total_cost", "current_quantity", "reorder_point"]:
            if col not in df.columns:
                df[col] = 0

        df["cost_per_unit"] = df.apply(cost_per_unit, axis=1)
        df["inventory_value"] = df["current_quantity"].astype(float) * df["cost_per_unit"].astype(float)
        df["stock_status"] = df.apply(
            lambda r: "LOW" if float(r.get("current_quantity") or 0) <= float(r.get("reorder_point") or 0) else "OK",
            axis=1
        )

    top1, top2, top3, top4 = st.columns([1.7, 1.7, 1, 2.6])
    if top1.button("➕ Create New Inventory Item", use_container_width=True):
        st.session_state.inventory_mode = "add"
        st.session_state.selected_inventory_id = None
        st.rerun()
    if top2.button("➕ Create New Category", use_container_width=True):
        st.session_state.inventory_mode = "add_category"
        st.session_state.selected_inventory_id = None
        st.rerun()
    if top3.button("📊 Reports", use_container_width=True):
        st.session_state.inventory_mode = "reports"
        st.session_state.selected_inventory_id = None
        st.rerun()

    if st.session_state.inventory_mode in ["add", "add_category", "edit", "delete", "reports"]:
        if st.button("← Back to Inventory List"):
            st.session_state.inventory_mode = "list"
            st.session_state.selected_inventory_id = None
            st.rerun()

    st.divider()

    if st.session_state.inventory_mode == "list":
        st.subheader("Inventory Categories")
        category_tabs = ["All"] + inventory_category_options
        category_filter = st.radio(
            "Choose an inventory category",
            category_tabs,
            horizontal=True,
            index=category_tabs.index(st.session_state.active_inventory_category) if st.session_state.active_inventory_category in category_tabs else 0
        )
        st.session_state.active_inventory_category = category_filter

        st.subheader("Current Inventory")

        c_search, c_hint = st.columns([2, 1])
        search_term = c_search.text_input("Search inventory", placeholder="Search item, supplier, category, INCI name, or notes...")
        c_hint.info("Create custom categories like Baking Soda, Botanicals, Labels, or Specialty Additives.")

        display_df = df.copy()

        if not display_df.empty:
            if search_term:
                term = search_term.lower()
                display_df = display_df[
                    display_df["item_name"].fillna("").str.lower().str.contains(term) |
                    display_df["category"].fillna("").str.lower().str.contains(term) |
                    display_df["subcategory"].fillna("").str.lower().str.contains(term) |
                    display_df["supplier"].fillna("").str.lower().str.contains(term) |
                    display_df["label_display_name"].fillna("").str.lower().str.contains(term) |
                    display_df["notes"].fillna("").str.lower().str.contains(term)
                ]

            if category_filter != "All":
                display_df = display_df[display_df["category"] == category_filter]

        if display_df.empty:
            st.info("No inventory items found in this category/search.")
        else:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Items Shown", len(display_df))
            c2.metric("Inventory Value", f"${display_df['inventory_value'].sum():.2f}")
            c3.metric("Low Stock Items", int((display_df["stock_status"] == "LOW").sum()))
            c4.metric("All Items", len(df))

            st.markdown("### Inventory Items")

            header_cols = st.columns([2.2, 1.2, 1.2, 1.1, 1, 1, 0.8, 0.8])
            header_cols[0].markdown("**Item**")
            header_cols[1].markdown("**Category**")
            header_cols[2].markdown("**Supplier**")
            header_cols[3].markdown("**Qty Left**")
            header_cols[4].markdown("**Cost/Unit**")
            header_cols[5].markdown("**Value**")
            header_cols[6].markdown("**Edit**")
            header_cols[7].markdown("**Delete**")

            for _, row in display_df.sort_values(["stock_status", "category", "item_name"]).iterrows():
                row_id = int(row["id"])
                status_icon = "⚠️" if row["stock_status"] == "LOW" else "✅"
                qty_text = f"{float(row.get('current_quantity') or 0):.2f} {row.get('unit') or ''}"
                cost_text = f"${float(row.get('cost_per_unit') or 0):.4f}"
                value_text = f"${float(row.get('inventory_value') or 0):.2f}"

                cols = st.columns([2.2, 1.2, 1.2, 1.1, 1, 1, 0.8, 0.8])
                cols[0].markdown(f"**{status_icon} {row.get('item_name') or ''}**")
                cols[1].write(row.get("category") or "")
                cols[2].write(row.get("supplier") or "—")
                cols[3].write(qty_text)
                cols[4].write(cost_text)
                cols[5].write(value_text)

                if cols[6].button("Edit", key=f"edit_{row_id}"):
                    st.session_state.selected_inventory_id = row_id
                    st.session_state.inventory_mode = "edit"
                    st.rerun()

                if cols[7].button("Delete", key=f"delete_{row_id}"):
                    st.session_state.selected_inventory_id = row_id
                    st.session_state.inventory_mode = "delete"
                    st.rerun()

                st.markdown("<hr style='margin: 0.35rem 0; border: none; border-top: 1px solid #eee;'>", unsafe_allow_html=True)

    elif st.session_state.inventory_mode == "add_category":
        st.subheader("Create New Inventory Category")
        st.write("Examples: Baking Soda, Botanicals, Labels, Shrink Wrap, Micas, Milks, Salts, Specialty Additives.")

        with st.form("create_inventory_category"):
            category_name = st.text_input("Category Name")
            description = st.text_area("Description, optional")
            submitted = st.form_submit_button("Create Category")

            if submitted:
                if not category_name.strip():
                    st.error("Category name is required.")
                else:
                    try:
                        insert_row("inventory_categories", {
                            "category_name": category_name.strip(),
                            "description": description.strip()
                        })
                        st.success(f"Created inventory category: {category_name}")
                        st.session_state.active_inventory_category = category_name.strip()
                        st.session_state.inventory_mode = "list"
                        st.rerun()
                    except Exception as e:
                        st.warning("Custom inventory categories require the inventory_categories table. Run supabase_inventory_categories.sql when Supabase is working.")
                        st.code(str(e))

        st.markdown("#### Available Categories Right Now")
        st.write(", ".join(inventory_category_options))

    elif st.session_state.inventory_mode == "add":
        st.subheader("Add New Inventory Item")

        with st.form("add_inventory", clear_on_submit=False):
            c1, c2, c3 = st.columns(3)
            item_name = c1.text_input("Item Name")
            default_index = inventory_category_options.index(st.session_state.active_inventory_category) if st.session_state.active_inventory_category in inventory_category_options else 0
            category = c2.selectbox("Inventory Category", inventory_category_options, index=default_index)
            subcategory = c3.text_input("Subcategory")

            c4, c5, c6 = st.columns(3)
            supplier = c4.text_input("Supplier")
            quantity = c5.number_input("Quantity Purchased", min_value=0.0, step=0.01)
            unit = c6.selectbox("Unit", ["oz", "lb", "g", "kg", "fl oz", "each"])

            c7, c8, c9 = st.columns(3)
            total_cost = c7.number_input("Total Cost Paid", min_value=0.0, step=0.01)
            current_quantity = c8.number_input("Current Quantity Left", min_value=0.0, step=0.01)
            reorder_point = c9.number_input("Reorder Point", min_value=0.0, step=0.01)

            label_display_name = st.text_input("Label Display / INCI Name")
            notes = st.text_area("Notes")
            submitted = st.form_submit_button("Save New Item")

            if submitted:
                if not item_name.strip():
                    st.error("Item Name is required.")
                else:
                    insert_row("inventory", {
                        "item_name": item_name.strip(),
                        "category": category,
                        "subcategory": subcategory.strip(),
                        "supplier": supplier.strip(),
                        "quantity_purchased": quantity,
                        "unit": unit,
                        "total_cost": total_cost,
                        "current_quantity": current_quantity,
                        "reorder_point": reorder_point,
                        "label_display_name": label_display_name.strip(),
                        "notes": notes.strip()
                    })
                    st.success(f"Added {item_name}")
                    st.session_state.active_inventory_category = category
                    st.session_state.inventory_mode = "list"
                    st.rerun()

    elif st.session_state.inventory_mode == "edit":
        selected_id = st.session_state.selected_inventory_id

        if df.empty or selected_id is None or df[df["id"] == selected_id].empty:
            st.error("Inventory item not found.")
        else:
            selected = df[df["id"] == selected_id].iloc[0]
            st.subheader(f"Edit: {selected.get('item_name')}")

            cost_unit = cost_per_unit(selected)
            inv_value = float(selected.get("current_quantity") or 0) * cost_unit
            status = "LOW STOCK" if float(selected.get("current_quantity") or 0) <= float(selected.get("reorder_point") or 0) else "OK"

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Status", status)
            m2.metric("Cost Per Unit", f"${cost_unit:.4f}")
            m3.metric("Quantity Left", f"{float(selected.get('current_quantity') or 0):.2f} {selected.get('unit') or ''}")
            m4.metric("Inventory Value", f"${inv_value:.2f}")

            st.markdown("#### Quick Quantity Update")
            with st.form("quick_quantity_inline"):
                q1, q2 = st.columns([1, 2])
                new_qty = q1.number_input(
                    "Current Quantity Left",
                    min_value=0.0,
                    step=0.01,
                    value=float(selected.get("current_quantity") or 0)
                )
                quick_note = q2.text_input("Quantity note, optional", placeholder="Example: used 12 oz in batch")
                quick_save = st.form_submit_button("Update Quantity Only")
                if quick_save:
                    existing_notes = str(selected.get("notes") or "")
                    updated_notes = existing_notes + (f"\nQuantity adjustment: {quick_note.strip()}" if quick_note.strip() else "")
                    update_row("inventory", selected_id, {"current_quantity": new_qty, "notes": updated_notes})
                    st.success("Quantity updated.")
                    st.rerun()

            st.markdown("#### Full Item Details")
            with st.form("edit_inventory"):
                c1, c2, c3 = st.columns(3)
                edit_item_name = c1.text_input("Item Name", value=str(selected.get("item_name") or ""))
                units = ["oz", "lb", "g", "kg", "fl oz", "each"]

                edit_category = c2.selectbox(
                    "Inventory Category",
                    inventory_category_options,
                    index=inventory_category_options.index(selected.get("category")) if selected.get("category") in inventory_category_options else 0
                )
                edit_subcategory = c3.text_input("Subcategory", value=str(selected.get("subcategory") or ""))

                c4, c5, c6 = st.columns(3)
                edit_supplier = c4.text_input("Supplier", value=str(selected.get("supplier") or ""))
                edit_quantity = c5.number_input("Original Quantity Purchased", min_value=0.0, step=0.01, value=float(selected.get("quantity_purchased") or 0))
                edit_unit = c6.selectbox(
                    "Unit",
                    units,
                    index=units.index(selected.get("unit")) if selected.get("unit") in units else 0
                )

                c7, c8, c9 = st.columns(3)
                edit_total_cost = c7.number_input("Total Cost Paid", min_value=0.0, step=0.01, value=float(selected.get("total_cost") or 0))
                edit_current_quantity = c8.number_input("Current Quantity Left", min_value=0.0, step=0.01, value=float(selected.get("current_quantity") or 0))
                edit_reorder_point = c9.number_input("Reorder Point", min_value=0.0, step=0.01, value=float(selected.get("reorder_point") or 0))

                edit_label = st.text_input("Label Display / INCI Name", value=str(selected.get("label_display_name") or ""))
                edit_notes = st.text_area("Notes", value=str(selected.get("notes") or ""))

                save_edit = st.form_submit_button("Save Changes")

                if save_edit:
                    update_row("inventory", selected_id, {
                        "item_name": edit_item_name.strip(),
                        "category": edit_category,
                        "subcategory": edit_subcategory.strip(),
                        "supplier": edit_supplier.strip(),
                        "quantity_purchased": edit_quantity,
                        "unit": edit_unit,
                        "total_cost": edit_total_cost,
                        "current_quantity": edit_current_quantity,
                        "reorder_point": edit_reorder_point,
                        "label_display_name": edit_label.strip(),
                        "notes": edit_notes.strip()
                    })
                    st.success(f"Updated {edit_item_name}")
                    st.session_state.active_inventory_category = edit_category
                    st.session_state.inventory_mode = "list"
                    st.rerun()

    elif st.session_state.inventory_mode == "delete":
        selected_id = st.session_state.selected_inventory_id

        if df.empty or selected_id is None or df[df["id"] == selected_id].empty:
            st.error("Inventory item not found.")
        else:
            selected = df[df["id"] == selected_id].iloc[0]
            st.subheader("Delete Inventory Item")

            st.warning("Once you delete this item, it is permanent and cannot be undone.")
            st.markdown(f"### {selected.get('item_name')}")
            st.write(f"**Category:** {selected.get('category') or '—'}")
            st.write(f"**Supplier:** {selected.get('supplier') or '—'}")
            st.write(f"**Quantity Left:** {float(selected.get('current_quantity') or 0):.2f} {selected.get('unit') or ''}")

            d1, d2, d3 = st.columns([1, 1, 3])

            if d1.button("Delete Item", type="primary", use_container_width=True):
                try:
                    delete_row("inventory", selected_id)
                    st.success("Inventory item deleted.")
                    st.session_state.inventory_mode = "list"
                    st.session_state.selected_inventory_id = None
                    st.rerun()
                except Exception as e:
                    st.error("The item could not be deleted. It may be used in a recipe, or Supabase may still need the delete policy added.")
                    st.code(str(e))

            if d2.button("Cancel", use_container_width=True):
                st.session_state.inventory_mode = "list"
                st.session_state.selected_inventory_id = None
                st.rerun()

    elif st.session_state.inventory_mode == "reports":
        st.subheader("Inventory Reports")

        if df.empty:
            st.info("No inventory available for reports yet.")
        else:
            report_type = st.selectbox(
                "Choose report",
                [
                    "Low Stock / Reorder Needed",
                    "Lowest Stock First",
                    "Highest Stock First",
                    "Highest Inventory Value",
                    "Lowest Inventory Value",
                    "By Category Summary",
                    "By Supplier Summary"
                ]
            )

            if report_type == "Low Stock / Reorder Needed":
                report = df[df["current_quantity"].astype(float) <= df["reorder_point"].astype(float)].copy()
                st.write("Items where current quantity is at or below reorder point.")
                if report.empty:
                    st.success("Nothing needs reordering right now.")
                else:
                    st.dataframe(report[["item_name", "category", "supplier", "current_quantity", "unit", "reorder_point"]], use_container_width=True, hide_index=True)

            elif report_type == "Lowest Stock First":
                report = df.sort_values("current_quantity", ascending=True)
                st.dataframe(report[["item_name", "category", "supplier", "current_quantity", "unit", "reorder_point"]], use_container_width=True, hide_index=True)

            elif report_type == "Highest Stock First":
                report = df.sort_values("current_quantity", ascending=False)
                st.dataframe(report[["item_name", "category", "supplier", "current_quantity", "unit", "reorder_point"]], use_container_width=True, hide_index=True)

            elif report_type == "Highest Inventory Value":
                report = df.sort_values("inventory_value", ascending=False)
                st.dataframe(report[["item_name", "category", "supplier", "current_quantity", "unit", "cost_per_unit", "inventory_value"]], use_container_width=True, hide_index=True)

            elif report_type == "Lowest Inventory Value":
                report = df.sort_values("inventory_value", ascending=True)
                st.dataframe(report[["item_name", "category", "supplier", "current_quantity", "unit", "cost_per_unit", "inventory_value"]], use_container_width=True, hide_index=True)

            elif report_type == "By Category Summary":
                report = df.groupby("category", dropna=False).agg(
                    item_count=("id", "count"),
                    total_inventory_value=("inventory_value", "sum"),
                    low_stock_items=("stock_status", lambda x: int((x == "LOW").sum()))
                ).reset_index()
                st.dataframe(report, use_container_width=True, hide_index=True)

            elif report_type == "By Supplier Summary":
                report = df.groupby("supplier", dropna=False).agg(
                    item_count=("id", "count"),
                    total_inventory_value=("inventory_value", "sum")
                ).reset_index().sort_values("total_inventory_value", ascending=False)
                st.dataframe(report, use_container_width=True, hide_index=True)

elif page == "Fragrance Library":
    st.title("Fragrance Library")
    st.caption("Organize fragrance oils by scent family, season, dupes, notes, performance, and ratings.")

    fragrances = table_df("fragrances")
    fragrance_categories = safe_table_df("fragrance_categories")

    if "fragrance_mode" not in st.session_state:
        st.session_state.fragrance_mode = "list"
    if "selected_fragrance_id" not in st.session_state:
        st.session_state.selected_fragrance_id = None
    if "active_fragrance_category" not in st.session_state:
        st.session_state.active_fragrance_category = "All"

    default_fragrance_categories = [
        "Men's",
        "Women's",
        "Dupes",
        "Christmas",
        "Fall",
        "Fruit",
        "Bakery",
        "Floral",
        "Fresh / Clean",
        "Spa",
        "Herbal",
        "Citrus",
        "Vanilla / Sweet",
        "Seasonal",
        "Nature / Outdoors",
        "Other"
    ]

    custom_fragrance_categories = []
    if not fragrance_categories.empty and "category_name" in fragrance_categories.columns:
        custom_fragrance_categories = fragrance_categories["category_name"].dropna().astype(str).tolist()

    existing_fragrance_categories = []
    if not fragrances.empty and "category" in fragrances.columns:
        existing_fragrance_categories = fragrances["category"].dropna().astype(str).unique().tolist()

    fragrance_category_options = []
    for cat in default_fragrance_categories + custom_fragrance_categories + existing_fragrance_categories:
        if cat and cat not in fragrance_category_options:
            fragrance_category_options.append(cat)

    if not fragrances.empty:
        for col in ["fragrance_name", "supplier", "vanillin", "ifra_notes", "cp_notes", "notes"]:
            if col not in fragrances.columns:
                fragrances[col] = ""
        if "category" not in fragrances.columns:
            fragrances["category"] = "Other"
        for col in ["quantity_oz", "total_cost", "strength_rating", "overall_rating"]:
            if col not in fragrances.columns:
                fragrances[col] = 0

        fragrances["cost_per_oz"] = fragrances.apply(
            lambda r: float(r.get("total_cost") or 0) / float(r.get("quantity_oz") or 1) if float(r.get("quantity_oz") or 0) else 0,
            axis=1
        )

    c1, c2, c3 = st.columns([1.7, 1.8, 3])
    if c1.button("➕ Create New Fragrance", use_container_width=True):
        st.session_state.fragrance_mode = "add"
        st.session_state.selected_fragrance_id = None
        st.rerun()

    if c2.button("➕ Create New Fragrance Category", use_container_width=True):
        st.session_state.fragrance_mode = "add_category"
        st.session_state.selected_fragrance_id = None
        st.rerun()

    if st.session_state.fragrance_mode != "list":
        if st.button("← Back to Fragrance List"):
            st.session_state.fragrance_mode = "list"
            st.session_state.selected_fragrance_id = None
            st.rerun()

    st.divider()

    if st.session_state.fragrance_mode == "list":
        st.subheader("Fragrance Categories")
        tab_options = ["All"] + fragrance_category_options

        selected_category = st.radio(
            "Choose a fragrance category",
            tab_options,
            horizontal=True,
            index=tab_options.index(st.session_state.active_fragrance_category) if st.session_state.active_fragrance_category in tab_options else 0
        )
        st.session_state.active_fragrance_category = selected_category

        st.subheader("Fragrance List")

        c_search, c_hint = st.columns([2, 1])
        search_term = c_search.text_input("Search fragrances", placeholder="Search fragrance, supplier, category, notes, vanillin, IFRA...")
        c_hint.info("Default categories show even before the Supabase category table is created.")

        display_df = fragrances.copy()

        if not display_df.empty:
            if selected_category != "All":
                display_df = display_df[display_df["category"] == selected_category]

            if search_term:
                term = search_term.lower()
                display_df = display_df[
                    display_df["fragrance_name"].fillna("").str.lower().str.contains(term) |
                    display_df["supplier"].fillna("").str.lower().str.contains(term) |
                    display_df["category"].fillna("").str.lower().str.contains(term) |
                    display_df["vanillin"].fillna("").str.lower().str.contains(term) |
                    display_df["ifra_notes"].fillna("").str.lower().str.contains(term) |
                    display_df["cp_notes"].fillna("").str.lower().str.contains(term) |
                    display_df["notes"].fillna("").str.lower().str.contains(term)
                ]

        if display_df.empty:
            st.info("No fragrances found in this category/search.")
        else:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Fragrances Shown", len(display_df))
            m2.metric("All Fragrances", len(fragrances))
            m3.metric("Avg Strength", f"{display_df['strength_rating'].astype(float).mean():.1f} ⭐")
            m4.metric("Avg Rating", f"{display_df['overall_rating'].astype(float).mean():.1f} ⭐")

            header_cols = st.columns([2.1, 1.1, 1.1, 0.8, 0.8, 0.8, 0.75, 0.75])
            header_cols[0].markdown("**Fragrance**")
            header_cols[1].markdown("**Category**")
            header_cols[2].markdown("**Supplier**")
            header_cols[3].markdown("**Qty**")
            header_cols[4].markdown("**Strength**")
            header_cols[5].markdown("**Rating**")
            header_cols[6].markdown("**Edit**")
            header_cols[7].markdown("**Delete**")

            for _, row in display_df.sort_values(["category", "fragrance_name"]).iterrows():
                row_id = int(row["id"])
                cols = st.columns([2.1, 1.1, 1.1, 0.8, 0.8, 0.8, 0.75, 0.75])
                cols[0].markdown(f"**{row.get('fragrance_name') or ''}**")
                cols[1].write(row.get("category") or "Other")
                cols[2].write(row.get("supplier") or "—")
                cols[3].write(f"{float(row.get('quantity_oz') or 0):.2f} oz")
                cols[4].write(f"{int(row.get('strength_rating') or 0)} ⭐")
                cols[5].write(f"{int(row.get('overall_rating') or 0)} ⭐")

                if cols[6].button("Edit", key=f"edit_fragrance_{row_id}"):
                    st.session_state.selected_fragrance_id = row_id
                    st.session_state.fragrance_mode = "edit"
                    st.rerun()

                if cols[7].button("Delete", key=f"delete_fragrance_{row_id}"):
                    st.session_state.selected_fragrance_id = row_id
                    st.session_state.fragrance_mode = "delete"
                    st.rerun()

                st.markdown("<hr style='margin: 0.35rem 0; border: none; border-top: 1px solid #eee;'>", unsafe_allow_html=True)

    elif st.session_state.fragrance_mode == "add_category":
        st.subheader("Create New Fragrance Category")
        st.write("Examples: Summer, Spring, Candy, Masculine, Dupes, Christmas, Fall, Fruit, Bakery, Spa.")

        with st.form("create_fragrance_category"):
            category_name = st.text_input("Category Name")
            description = st.text_area("Description, optional")
            submitted = st.form_submit_button("Create Category")

            if submitted:
                if not category_name.strip():
                    st.error("Category name is required.")
                else:
                    try:
                        insert_row("fragrance_categories", {
                            "category_name": category_name.strip(),
                            "description": description.strip()
                        })
                        st.success(f"Created fragrance category: {category_name}")
                        st.session_state.active_fragrance_category = category_name.strip()
                        st.session_state.fragrance_mode = "list"
                        st.rerun()
                    except Exception as e:
                        st.warning("Custom fragrance categories require the fragrance_categories table. Run supabase_fragrance_categories.sql when Supabase is working.")
                        st.code(str(e))

        st.markdown("#### Available Categories Right Now")
        st.write(", ".join(fragrance_category_options))

    elif st.session_state.fragrance_mode == "add":
        st.subheader("Create New Fragrance")

        with st.form("add_fragrance"):
            c1, c2, c3 = st.columns(3)
            fragrance_name = c1.text_input("Fragrance Name")
            default_index = fragrance_category_options.index(st.session_state.active_fragrance_category) if st.session_state.active_fragrance_category in fragrance_category_options else 0
            category = c2.selectbox("Fragrance Category", fragrance_category_options, index=default_index)
            supplier = c3.text_input("Supplier")

            c4, c5, c6 = st.columns(3)
            quantity_oz = c4.number_input("Quantity oz", min_value=0.0, step=0.01)
            total_cost = c5.number_input("Total Cost", min_value=0.0, step=0.01)
            vanillin = c6.text_input("Vanillin %")

            ifra_notes = st.text_input("IFRA Notes")
            cp_notes = st.text_area("Cold Process / Cure Notes")

            c7, c8 = st.columns(2)
            strength_rating = c7.slider("Strength Rating", 1, 5, 3)
            overall_rating = c8.slider("Overall Rating", 1, 5, 3)
            notes = st.text_area("Other Notes")

            submitted = st.form_submit_button("Save Fragrance")
            if submitted:
                if not fragrance_name.strip():
                    st.error("Fragrance name is required.")
                else:
                    data = {
                        "fragrance_name": fragrance_name.strip(),
                        "supplier": supplier.strip(),
                        "quantity_oz": quantity_oz,
                        "total_cost": total_cost,
                        "vanillin": vanillin.strip(),
                        "ifra_notes": ifra_notes.strip(),
                        "cp_notes": cp_notes.strip(),
                        "strength_rating": strength_rating,
                        "overall_rating": overall_rating,
                        "notes": notes.strip(),
                        "category": category
                    }
                    try:
                        insert_row("fragrances", data)
                    except Exception:
                        data.pop("category", None)
                        insert_row("fragrances", data)
                    st.success(f"Saved {fragrance_name}")
                    st.session_state.active_fragrance_category = category
                    st.session_state.fragrance_mode = "list"
                    st.rerun()

    elif st.session_state.fragrance_mode == "edit":
        selected_id = st.session_state.selected_fragrance_id

        if fragrances.empty or selected_id is None or fragrances[fragrances["id"] == selected_id].empty:
            st.error("Fragrance not found.")
        else:
            selected = fragrances[fragrances["id"] == selected_id].iloc[0]
            st.subheader(f"Edit: {selected.get('fragrance_name')}")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Quantity", f"{float(selected.get('quantity_oz') or 0):.2f} oz")
            m2.metric("Cost / oz", f"${float(selected.get('cost_per_oz') or 0):.4f}")
            m3.metric("Strength", f"{int(selected.get('strength_rating') or 0)} ⭐")
            m4.metric("Rating", f"{int(selected.get('overall_rating') or 0)} ⭐")

            with st.form("edit_fragrance_form"):
                c1, c2, c3 = st.columns(3)
                fragrance_name = c1.text_input("Fragrance Name", value=str(selected.get("fragrance_name") or ""))
                current_cat = selected.get("category") if selected.get("category") else "Other"
                category = c2.selectbox(
                    "Fragrance Category",
                    fragrance_category_options,
                    index=fragrance_category_options.index(current_cat) if current_cat in fragrance_category_options else 0
                )
                supplier = c3.text_input("Supplier", value=str(selected.get("supplier") or ""))

                c4, c5, c6 = st.columns(3)
                quantity_oz = c4.number_input("Quantity oz", min_value=0.0, step=0.01, value=float(selected.get("quantity_oz") or 0))
                total_cost = c5.number_input("Total Cost", min_value=0.0, step=0.01, value=float(selected.get("total_cost") or 0))
                vanillin = c6.text_input("Vanillin %", value=str(selected.get("vanillin") or ""))

                ifra_notes = st.text_input("IFRA Notes", value=str(selected.get("ifra_notes") or ""))
                cp_notes = st.text_area("Cold Process / Cure Notes", value=str(selected.get("cp_notes") or ""))

                c7, c8 = st.columns(2)
                strength_rating = c7.slider("Strength Rating", 1, 5, int(selected.get("strength_rating") or 3))
                overall_rating = c8.slider("Overall Rating", 1, 5, int(selected.get("overall_rating") or 3))
                notes = st.text_area("Other Notes", value=str(selected.get("notes") or ""))

                submitted = st.form_submit_button("Save Changes")
                if submitted:
                    data = {
                        "fragrance_name": fragrance_name.strip(),
                        "supplier": supplier.strip(),
                        "quantity_oz": quantity_oz,
                        "total_cost": total_cost,
                        "vanillin": vanillin.strip(),
                        "ifra_notes": ifra_notes.strip(),
                        "cp_notes": cp_notes.strip(),
                        "strength_rating": strength_rating,
                        "overall_rating": overall_rating,
                        "notes": notes.strip(),
                        "category": category
                    }
                    try:
                        update_row("fragrances", selected_id, data)
                    except Exception:
                        data.pop("category", None)
                        update_row("fragrances", selected_id, data)
                    st.success("Fragrance updated.")
                    st.session_state.active_fragrance_category = category
                    st.session_state.fragrance_mode = "list"
                    st.rerun()

    elif st.session_state.fragrance_mode == "delete":
        selected_id = st.session_state.selected_fragrance_id

        if fragrances.empty or selected_id is None or fragrances[fragrances["id"] == selected_id].empty:
            st.error("Fragrance not found.")
        else:
            selected = fragrances[fragrances["id"] == selected_id].iloc[0]
            st.subheader("Delete Fragrance")
            st.warning("Once you delete this fragrance, it is permanent and cannot be undone.")
            st.markdown(f"### {selected.get('fragrance_name')}")
            st.write(f"**Category:** {selected.get('category') or 'Other'}")
            st.write(f"**Supplier:** {selected.get('supplier') or '—'}")

            d1, d2, d3 = st.columns([1, 1, 3])
            if d1.button("Delete Fragrance", type="primary", use_container_width=True):
                try:
                    delete_row("fragrances", selected_id)
                    st.success("Fragrance deleted.")
                    st.session_state.fragrance_mode = "list"
                    st.session_state.selected_fragrance_id = None
                    st.rerun()
                except Exception as e:
                    st.error("The fragrance could not be deleted. Supabase may need the delete policy added.")
                    st.code(str(e))

            if d2.button("Cancel", use_container_width=True):
                st.session_state.fragrance_mode = "list"
                st.session_state.selected_fragrance_id = None
                st.rerun()

elif page == "Recipes":
    st.title("Recipe Manager")
    st.caption("Manage recipes, recipe tabs/categories, ingredients, costs, and production details.")

    if "recipe_mode" not in st.session_state:
        st.session_state.recipe_mode = "list"
    if "selected_recipe_id" not in st.session_state:
        st.session_state.selected_recipe_id = None
    if "selected_recipe_line_id" not in st.session_state:
        st.session_state.selected_recipe_line_id = None
    if "active_recipe_tab" not in st.session_state:
        st.session_state.active_recipe_tab = "All"

    recipes = table_df("recipes")
    inv = table_df("inventory")
    recipe_categories = safe_table_df("recipe_categories")

    default_tabs = ["Soap", "Melt & Pour", "Lotion", "Body Butter", "Body Oil", "Cuticle Oil", "Bath Bomb", "Shower Steamer"]

    custom_tabs = []
    if not recipe_categories.empty and "category_name" in recipe_categories.columns:
        custom_tabs = recipe_categories["category_name"].dropna().astype(str).tolist()

    existing_tabs = []
    if not recipes.empty and "product_type" in recipes.columns:
        existing_tabs = recipes["product_type"].dropna().astype(str).unique().tolist()

    recipe_tabs = []
    for tab in default_tabs + custom_tabs + existing_tabs:
        if tab and tab not in recipe_tabs:
            recipe_tabs.append(tab)

    c1, c2, c3 = st.columns([1.5, 1.8, 3])
    if c1.button("➕ Create New Recipe", use_container_width=True):
        st.session_state.recipe_mode = "add"
        st.session_state.selected_recipe_id = None
        st.session_state.selected_recipe_line_id = None
        st.rerun()

    if c2.button("➕ Create New Tab / Category", use_container_width=True):
        st.session_state.recipe_mode = "add_tab"
        st.session_state.selected_recipe_id = None
        st.session_state.selected_recipe_line_id = None
        st.rerun()

    if st.session_state.recipe_mode != "list":
        if st.button("← Back to Recipe List"):
            st.session_state.recipe_mode = "list"
            st.session_state.selected_recipe_id = None
            st.session_state.selected_recipe_line_id = None
            st.rerun()

    st.divider()

    if st.session_state.recipe_mode == "list":
        st.subheader("Recipe Tabs / Categories")
        tab_options = ["All"] + recipe_tabs
        active_tab = st.radio("Choose a recipe tab", tab_options, horizontal=True)
        st.session_state.active_recipe_tab = active_tab

        st.subheader("Recipe List")
        search_term = st.text_input("Search recipes", placeholder="Search by recipe name, tab/category, or notes...")

        display_recipes = recipes.copy()

        if not display_recipes.empty:
            for col in ["recipe_name", "product_type", "notes"]:
                if col not in display_recipes.columns:
                    display_recipes[col] = ""

            if active_tab != "All":
                display_recipes = display_recipes[display_recipes["product_type"] == active_tab]

            if search_term:
                term = search_term.lower()
                display_recipes = display_recipes[
                    display_recipes["recipe_name"].fillna("").str.lower().str.contains(term) |
                    display_recipes["product_type"].fillna("").str.lower().str.contains(term) |
                    display_recipes["notes"].fillna("").str.lower().str.contains(term)
                ]

        if display_recipes.empty:
            st.info("No recipes found in this tab/search.")
        else:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Recipes Shown", len(display_recipes))
            m2.metric("All Recipes", len(recipes))
            m3.metric("Average Yield", f"{display_recipes['bars_made'].astype(float).mean():.1f}" if "bars_made" in display_recipes else "0")
            m4.metric("Avg Retail", f"${display_recipes['retail_price'].astype(float).mean():.2f}" if "retail_price" in display_recipes else "$0.00")

            header = st.columns([2.2, 1.3, 0.8, 0.9, 0.8, 0.8, 0.8])
            header[0].markdown("**Recipe**")
            header[1].markdown("**Tab / Category**")
            header[2].markdown("**Yield**")
            header[3].markdown("**Retail**")
            header[4].markdown("**Open**")
            header[5].markdown("**Edit**")
            header[6].markdown("**Delete**")

            for _, row in display_recipes.sort_values(["product_type", "recipe_name"]).iterrows():
                rid = int(row["id"])
                cols = st.columns([2.2, 1.3, 0.8, 0.9, 0.8, 0.8, 0.8])
                cols[0].markdown(f"**{row.get('recipe_name') or ''}**")
                cols[1].write(row.get("product_type") or "")
                cols[2].write(int(row.get("bars_made") or 0))
                cols[3].write(f"${float(row.get('retail_price') or 0):.2f}")

                if cols[4].button("Open", key=f"open_recipe_{rid}"):
                    st.session_state.selected_recipe_id = rid
                    st.session_state.recipe_mode = "details"
                    st.rerun()

                if cols[5].button("Edit", key=f"edit_recipe_{rid}"):
                    st.session_state.selected_recipe_id = rid
                    st.session_state.recipe_mode = "edit_recipe"
                    st.rerun()

                if cols[6].button("Delete", key=f"delete_recipe_{rid}"):
                    st.session_state.selected_recipe_id = rid
                    st.session_state.recipe_mode = "delete_recipe"
                    st.rerun()

                st.markdown("<hr style='margin: 0.35rem 0; border: none; border-top: 1px solid #eee;'>", unsafe_allow_html=True)

    elif st.session_state.recipe_mode == "add_tab":
        st.subheader("Create New Recipe Tab / Category")
        st.write("Examples: Cold Process Soap, Lotions, Body Butters, Scrubs, Wax Melts, Candles, Pet Products.")

        with st.form("create_recipe_tab"):
            tab_name = st.text_input("Tab / Category Name")
            description = st.text_area("Description, optional")
            submitted = st.form_submit_button("Create Tab")

            if submitted:
                if not tab_name.strip():
                    st.error("Tab/category name is required.")
                else:
                    try:
                        insert_row("recipe_categories", {
                            "category_name": tab_name.strip(),
                            "description": description.strip()
                        })
                        st.success(f"Created tab: {tab_name}")
                        st.session_state.active_recipe_tab = tab_name.strip()
                        st.session_state.recipe_mode = "list"
                        st.rerun()
                    except Exception as e:
                        st.warning("Custom tabs require the recipe_categories table. Run supabase_recipe_tabs_categories.sql when Supabase is working.")
                        st.code(str(e))

        st.markdown("#### Available Tabs Right Now")
        st.write(", ".join(recipe_tabs))

    elif st.session_state.recipe_mode == "add":
        st.subheader("Create New Recipe")

        with st.form("create_recipe"):
            recipe_name = st.text_input("Recipe Name")
            product_type = st.selectbox("Recipe Tab / Category", recipe_tabs)
            bars_made = st.number_input("Number Made / Batch Yield", min_value=1, step=1)
            retail_price = st.number_input("Retail Price Per Item", min_value=0.0, step=0.01)
            cure_days = st.number_input("Cure / Ready Days", min_value=0, value=42, step=1)
            notes = st.text_area("Recipe Notes")
            submitted = st.form_submit_button("Create Recipe")

            if submitted:
                if not recipe_name.strip():
                    st.error("Recipe name is required.")
                else:
                    res = insert_row("recipes", {
                        "recipe_name": recipe_name.strip(),
                        "product_type": product_type,
                        "bars_made": bars_made,
                        "retail_price": retail_price,
                        "cure_days": cure_days,
                        "notes": notes.strip()
                    })
                    new_recipe_id = None
                    try:
                        if res.data:
                            new_recipe_id = res.data[0].get("id")
                    except Exception:
                        new_recipe_id = None
                    if new_recipe_id is None:
                        try:
                            latest = supabase.table("recipes").select("id").eq("recipe_name", recipe_name.strip()).order("id", desc=True).limit(1).execute()
                            if latest.data:
                                new_recipe_id = latest.data[0].get("id")
                        except Exception:
                            pass
                    st.success(f"Created recipe {recipe_name}")
                    st.session_state.active_recipe_tab = product_type
                    st.session_state.selected_recipe_id = int(new_recipe_id) if new_recipe_id is not None else None
                    st.session_state.recipe_mode = "details" if new_recipe_id is not None else "list"
                    st.rerun()

    elif st.session_state.recipe_mode == "edit_recipe":
        rid = st.session_state.selected_recipe_id

        if recipes.empty or rid is None or recipes[recipes["id"] == rid].empty:
            st.error("Recipe not found.")
        else:
            recipe = recipes[recipes["id"] == rid].iloc[0]
            st.subheader(f"Edit Recipe: {recipe.get('recipe_name')}")

            current_category = recipe.get("product_type")

            with st.form("edit_recipe_form"):
                recipe_name = st.text_input("Recipe Name", value=str(recipe.get("recipe_name") or ""))
                product_type = st.selectbox(
                    "Recipe Tab / Category",
                    recipe_tabs,
                    index=recipe_tabs.index(current_category) if current_category in recipe_tabs else 0
                )
                bars_made = st.number_input("Number Made / Batch Yield", min_value=1, step=1, value=int(recipe.get("bars_made") or 1))
                retail_price = st.number_input("Retail Price Per Item", min_value=0.0, step=0.01, value=float(recipe.get("retail_price") or 0))
                cure_days = st.number_input("Cure / Ready Days", min_value=0, step=1, value=int(recipe.get("cure_days") or 0))
                notes = st.text_area("Recipe Notes", value=str(recipe.get("notes") or ""))
                save = st.form_submit_button("Save Recipe Changes")

                if save:
                    update_row("recipes", rid, {
                        "recipe_name": recipe_name.strip(),
                        "product_type": product_type,
                        "bars_made": bars_made,
                        "retail_price": retail_price,
                        "cure_days": cure_days,
                        "notes": notes.strip()
                    })
                    st.success("Recipe updated.")
                    st.session_state.active_recipe_tab = product_type
                    st.session_state.recipe_mode = "details"
                    st.rerun()

    elif st.session_state.recipe_mode == "delete_recipe":
        rid = st.session_state.selected_recipe_id

        if recipes.empty or rid is None or recipes[recipes["id"] == rid].empty:
            st.error("Recipe not found.")
        else:
            recipe = recipes[recipes["id"] == rid].iloc[0]
            st.subheader("Delete Recipe")
            st.warning("Deleting this recipe will also delete its recipe line items. This cannot be undone.")
            st.markdown(f"### {recipe.get('recipe_name')}")
            st.write(f"**Tab / Category:** {recipe.get('product_type') or '—'}")
            d1, d2, d3 = st.columns([1, 1, 3])
            if d1.button("Delete Recipe", type="primary", use_container_width=True):
                try:
                    delete_row("recipes", rid)
                    st.success("Recipe deleted.")
                    st.session_state.recipe_mode = "list"
                    st.session_state.selected_recipe_id = None
                    st.rerun()
                except Exception as e:
                    st.error("Could not delete recipe. Supabase may need delete policies.")
                    st.code(str(e))

            if d2.button("Cancel", use_container_width=True):
                st.session_state.recipe_mode = "list"
                st.session_state.selected_recipe_id = None
                st.rerun()

    elif st.session_state.recipe_mode == "details":
        rid = st.session_state.selected_recipe_id

        if recipes.empty or rid is None or recipes[recipes["id"] == rid].empty:
            st.error("Recipe not found.")
        else:
            recipe = recipes[recipes["id"] == rid].iloc[0]
            st.subheader(f"Recipe Details: {recipe.get('recipe_name')}")
            st.caption(f"Tab / Category: {recipe.get('product_type') or 'Uncategorized'}")

            action1, action2, action3 = st.columns([1, 1, 4])
            if action1.button("Edit Recipe", use_container_width=True):
                st.session_state.recipe_mode = "edit_recipe"
                st.rerun()
            if action2.button("Delete Recipe", use_container_width=True):
                st.session_state.recipe_mode = "delete_recipe"
                st.rerun()

            lines = recipe_lines(rid)

            total_cost = float(lines["line_cost"].sum()) if not lines.empty else 0
            made = int(recipe.get("bars_made") or 1)
            cost_per_item = total_cost / made if made else 0
            retail_price = float(recipe.get("retail_price") or 0)
            profit_per_item = retail_price - cost_per_item
            margin = (profit_per_item / retail_price * 100) if retail_price else 0

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Batch Cost", f"${total_cost:.2f}")
            m2.metric("Cost Per Item", f"${cost_per_item:.2f}")
            m3.metric("Profit Per Item", f"${profit_per_item:.2f}")
            m4.metric("Margin", f"{margin:.1f}%")

            st.markdown("#### Add Ingredient / Inventory Line")

            if inv.empty:
                st.warning("Add inventory items first before building a recipe.")
            else:
                with st.form("add_recipe_line"):
                    inv_sorted = inv.sort_values("item_name")
                    item_choice = st.selectbox("Inventory Item", inv_sorted["id"].astype(str) + " - " + inv_sorted["item_name"])
                    inventory_id = int(item_choice.split(" - ")[0])
                    amount_used = st.number_input("Amount Used", min_value=0.0, step=0.01)
                    unit = st.selectbox("Unit Used", ["oz", "g", "each"])
                    include_on_label = st.checkbox("Include on ingredient label", value=True)
                    label_override = st.text_input("Label Name Override, optional")
                    add_line = st.form_submit_button("Add Line")

                    if add_line:
                        insert_row("recipe_lines", {
                            "recipe_id": rid,
                            "inventory_id": inventory_id,
                            "amount_used": amount_used,
                            "unit": unit,
                            "include_on_label": include_on_label,
                            "label_name_override": label_override
                        })
                        st.success("Added ingredient to recipe.")
                        st.rerun()

            st.markdown("#### Recipe Lines")

            if lines.empty:
                st.info("No ingredients added to this recipe yet.")
            else:
                header = st.columns([2.2, 1.1, 0.9, 0.9, 1, 0.8, 0.8])
                header[0].markdown("**Item**")
                header[1].markdown("**Category**")
                header[2].markdown("**Amount**")
                header[3].markdown("**Unit**")
                header[4].markdown("**Line Cost**")
                header[5].markdown("**Edit**")
                header[6].markdown("**Delete**")

                for _, line in lines.iterrows():
                    lid = int(line["id_line"]) if "id_line" in lines.columns else int(line["id"])
                    cols = st.columns([2.2, 1.1, 0.9, 0.9, 1, 0.8, 0.8])
                    cols[0].markdown(f"**{line.get('item_name') or ''}**")
                    cols[1].write(line.get("category") or "")
                    cols[2].write(float(line.get("amount_used") or 0))
                    cols[3].write(line.get("unit_line") or line.get("unit") or "")
                    cols[4].write(f"${float(line.get('line_cost') or 0):.2f}")

                    if cols[5].button("Edit", key=f"edit_line_{lid}"):
                        st.session_state.selected_recipe_line_id = lid
                        st.session_state.recipe_mode = "edit_line"
                        st.rerun()

                    if cols[6].button("Delete", key=f"delete_line_{lid}"):
                        st.session_state.selected_recipe_line_id = lid
                        st.session_state.recipe_mode = "delete_line"
                        st.rerun()

                    st.markdown("<hr style='margin: 0.35rem 0; border: none; border-top: 1px solid #eee;'>", unsafe_allow_html=True)

    elif st.session_state.recipe_mode == "edit_line":
        rid = st.session_state.selected_recipe_id
        lid = st.session_state.selected_recipe_line_id
        lines = recipe_lines(rid)

        if lines.empty:
            st.error("Recipe line not found.")
        else:
            id_col = "id_line" if "id_line" in lines.columns else "id"
            match = lines[lines[id_col] == lid]

            if match.empty:
                st.error("Recipe line not found.")
            else:
                line = match.iloc[0]
                st.subheader(f"Edit Recipe Line: {line.get('item_name')}")

                with st.form("edit_recipe_line_form"):
                    amount_used = st.number_input("Amount Used", min_value=0.0, step=0.01, value=float(line.get("amount_used") or 0))
                    current_unit = line.get("unit_line") if "unit_line" in line.index else line.get("unit")
                    units = ["oz", "g", "each"]
                    unit = st.selectbox("Unit Used", units, index=units.index(current_unit) if current_unit in units else 0)
                    include_on_label = st.checkbox("Include on ingredient label", value=bool(line.get("include_on_label")))
                    label_override = st.text_input("Label Name Override, optional", value=str(line.get("label_name_override") or ""))
                    save_line = st.form_submit_button("Save Line Changes")

                    if save_line:
                        update_row("recipe_lines", lid, {
                            "amount_used": amount_used,
                            "unit": unit,
                            "include_on_label": include_on_label,
                            "label_name_override": label_override.strip()
                        })
                        st.success("Recipe line updated.")
                        st.session_state.recipe_mode = "details"
                        st.session_state.selected_recipe_line_id = None
                        st.rerun()

    elif st.session_state.recipe_mode == "delete_line":
        rid = st.session_state.selected_recipe_id
        lid = st.session_state.selected_recipe_line_id
        lines = recipe_lines(rid)

        if lines.empty:
            st.error("Recipe line not found.")
        else:
            id_col = "id_line" if "id_line" in lines.columns else "id"
            match = lines[lines[id_col] == lid]

            if match.empty:
                st.error("Recipe line not found.")
            else:
                line = match.iloc[0]
                st.subheader("Delete Recipe Line")
                st.warning("This will remove this item from the recipe. It cannot be undone.")
                st.markdown(f"### {line.get('item_name')}")
                d1, d2, d3 = st.columns([1, 1, 3])
                if d1.button("Delete Line", type="primary", use_container_width=True):
                    try:
                        delete_row("recipe_lines", lid)
                        st.success("Recipe line deleted.")
                        st.session_state.recipe_mode = "details"
                        st.session_state.selected_recipe_line_id = None
                        st.rerun()
                    except Exception as e:
                        st.error("Could not delete recipe line. Supabase may need delete policies.")
                        st.code(str(e))

                if d2.button("Cancel", use_container_width=True):
                    st.session_state.recipe_mode = "details"
                    st.session_state.selected_recipe_line_id = None
                    st.rerun()

elif page == "Recipe Cost Summary":
    st.title("Recipe Cost Summary")
    recipes = df("recipes")
    if recipes.empty: st.warning("Create a recipe first.")
    else:
        choice = st.selectbox("Choose Recipe", recipes["id"].astype(str)+" - "+recipes["recipe_name"]); rid = int(choice.split(" - ")[0]); r = recipe_row(rid); lines = recipe_lines(rid)
        if lines.empty: st.info("No ingredients added yet.")
        else:
            total = lines["line_cost"].sum(); made = int(r["bars_made"] or 1); cpi = total/made; retail = float(r["retail_price"] or 0); profit = retail-cpi; margin = profit/retail*100 if retail else 0
            c1,c2,c3,c4 = st.columns(4); c1.metric("Total Batch Cost", f"${total:.2f}"); c2.metric("Cost Per Item", f"${cpi:.2f}"); c3.metric("Profit Per Item", f"${profit:.2f}"); c4.metric("Margin", f"{margin:.1f}%")
            st.dataframe(lines[["item_name","category","amount_used","unit_line","line_cost"]], use_container_width=True)

elif page == "Can I Make This?":
    st.title("Can I Make This?")
    recipes = df("recipes")
    if recipes.empty: st.warning("Create a recipe first.")
    else:
        choice = st.selectbox("Choose Recipe", recipes["id"].astype(str)+" - "+recipes["recipe_name"]); rid = int(choice.split(" - ")[0]); lines = recipe_lines(rid)
        if lines.empty: st.info("No ingredients added yet.")
        else:
            batches = [(float(x.current_quantity)//float(x.amount_used)) if float(x.amount_used or 0) else 0 for x in lines.itertuples()]
            st.success(f"Yes — maximum full batches possible: {int(min(batches))}") if all(lines["enough_inventory"]) else st.error("Not enough inventory for this recipe.")
            st.dataframe(lines[["item_name","amount_used","unit_line","current_quantity","enough_inventory"]], use_container_width=True)

elif page == "Batch Production":
    st.title("Batch Production")
    recipes = df("recipes")
    cure_status_options = ["Not Started", "Curing", "Cured", "Needs Review"]

    if recipes.empty:
        st.warning("Create a recipe first.")
    else:
        choice = st.selectbox("Choose Recipe", recipes["id"].astype(str) + " - " + recipes["recipe_name"])
        rid = int(choice.split(" - ")[0])
        r = recipe_row(rid)
        lines = recipe_lines(rid)

        c1, c2, c3 = st.columns(3)
        batch = c1.text_input("Batch Number", value=f"{str(r['product_type'])[:2].upper()}-{date.today().strftime('%Y%m%d')}")
        made_date = c2.date_input("Date Made", value=date.today())
        cure_days = c3.number_input("Cure Days", min_value=0, step=1, value=int(r.get("cure_days") or 0))

        c4, c5 = st.columns(2)
        default_status = "Cured" if int(cure_days or 0) == 0 else "Curing"
        cure_status = c4.selectbox("Manual Cure Status", cure_status_options, index=cure_status_options.index(default_status))
        qty = c5.number_input("Quantity Made", min_value=1, value=int(r["bars_made"] or 1))

        cure_date = made_date + timedelta(days=int(cure_days or 0))
        notes = st.text_area("Batch Notes")

        total = float(lines["line_cost"].sum()) if not lines.empty else 0
        cpi = total / qty if qty else 0

        m1, m2, m3 = st.columns(3)
        m1.metric("Batch Cost", f"${total:.2f}")
        m2.metric("Cost Per Item", f"${cpi:.2f}")
        m3.metric("Manual Status", cure_status)
        st.write(f"Ready/Cure Date: **{cure_date}**")

        if st.button("Save Batch and Add to Finished Goods"):
            batch_data = {
                "batch_number": batch,
                "recipe_id": rid,
                "date_made": str(made_date),
                "cure_date": str(cure_date),
                "cure_days": int(cure_days or 0),
                "quantity_made": qty,
                "batch_cost": total,
                "cost_per_item": cpi,
                "notes": notes,
                "cure_status": cure_status
            }
            try:
                res = insert("batches", batch_data)
            except Exception:
                batch_data.pop("cure_status", None)
                res = insert("batches", batch_data)

            bid = res.data[0]["id"] if res.data else None
            goods_data = {
                "product_name": r["recipe_name"],
                "product_type": r["product_type"],
                "recipe_id": rid,
                "batch_id": bid,
                "quantity_on_hand": qty,
                "cure_start_date": str(made_date),
                "cure_days": int(cure_days or 0),
                "cure_date": str(cure_date),
                "cost_per_item": cpi,
                "retail_price": float(r["retail_price"] or 0),
                "notes": notes,
                "cure_status": cure_status
            }
            try:
                insert("finished_goods", goods_data)
            except Exception:
                # Older Supabase tables may not have the new cure columns yet.
                for optional_col in ["cure_status", "cure_start_date", "cure_days", "cure_date"]:
                    goods_data.pop(optional_col, None)
                insert("finished_goods", goods_data)
            st.rerun()

        ingredients = "\n".join([f"- {x.item_name}: {x.amount_used} {x.unit_line}" for x in lines.itertuples()]) if not lines.empty else ""
        st.text_area("Printable Batch Card", value=f"THE SOAP LAB BATCH CARD\n\nBatch: {batch}\nRecipe: {r['recipe_name']}\nDate Made: {made_date}\nReady Date: {cure_date}\nManual Cure Status: {cure_status}\nQuantity: {qty}\nBatch Cost: ${total:.2f}\nCost Per Item: ${cpi:.2f}\n\nIngredients:\n{ingredients}\n\nNotes:\n{notes}", height=350)

elif page == "Finished Goods":
    st.title("Finished Goods Inventory")
    st.caption("Track finished products, cure status, cure days, quantities, pricing, and batch notes.")

    goods = df("finished_goods")
    batches = df("batches")
    recipes = df("recipes")
    cure_status_options = ["Not Started", "Curing", "Cured", "Needs Review"]

    if "finished_goods_mode" not in st.session_state:
        st.session_state.finished_goods_mode = "list"
    if "selected_finished_good_id" not in st.session_state:
        st.session_state.selected_finished_good_id = None

    if st.session_state.finished_goods_mode != "list":
        if st.button("← Back to Finished Goods List"):
            st.session_state.finished_goods_mode = "list"
            st.session_state.selected_finished_good_id = None
            st.rerun()

    def normalize_finished_goods(gdf):
        if gdf.empty:
            return gdf
        defaults = {
            "product_name": "",
            "product_type": "",
            "batch_id": None,
            "recipe_id": None,
            "quantity_on_hand": 0,
            "cost_per_item": 0,
            "retail_price": 0,
            "notes": "",
            "cure_status": "Curing",
            "cure_days": 0,
            "cure_start_date": None,
            "cure_date": None,
            "photo_url": "",
            "description": "",
            "sku": "",
        }
        for col, default in defaults.items():
            if col not in gdf.columns:
                gdf[col] = default

        # Pull cure dates from batches for older records when finished_goods does not have them yet.
        if not batches.empty and "batch_id" in gdf.columns:
            batch_cols = [c for c in ["id", "batch_number", "date_made", "cure_date", "cure_days"] if c in batches.columns]
            if batch_cols:
                gdf = gdf.merge(batches[batch_cols], left_on="batch_id", right_on="id", how="left", suffixes=("", "_batch"))
                if "batch_number" not in gdf.columns:
                    gdf["batch_number"] = ""
                gdf["cure_start_date"] = gdf["cure_start_date"].fillna(gdf.get("date_made", pd.Series([None] * len(gdf))))
                gdf["cure_date"] = gdf["cure_date"].fillna(gdf.get("cure_date_batch", pd.Series([None] * len(gdf))))
                if "cure_days_batch" in gdf.columns:
                    gdf["cure_days"] = gdf["cure_days"].fillna(gdf["cure_days_batch"])
        if "batch_number" not in gdf.columns:
            gdf["batch_number"] = ""
        if "status" in gdf.columns:
            # Prefer manual status fallback when present, because older installs may save there.
            status_text = gdf["status"].fillna("").astype(str).str.strip()
            gdf["cure_status"] = gdf["cure_status"].where(status_text == "", gdf["status"])
        gdf["cure_status"] = gdf["cure_status"].apply(normalize_cure_status)
        gdf["cure_days"] = pd.to_numeric(gdf["cure_days"], errors="coerce").fillna(0).astype(int)
        gdf["quantity_on_hand"] = pd.to_numeric(gdf["quantity_on_hand"], errors="coerce").fillna(0)
        gdf["cost_per_item"] = pd.to_numeric(gdf["cost_per_item"], errors="coerce").fillna(0)
        gdf["retail_price"] = pd.to_numeric(gdf["retail_price"], errors="coerce").fillna(0)
        gdf["total_value"] = gdf["quantity_on_hand"] * gdf["cost_per_item"]
        return gdf

    goods = normalize_finished_goods(goods)

    if goods.empty:
        st.info("No finished goods yet. Save a batch from Batch Production to create finished goods inventory.")
    elif st.session_state.finished_goods_mode == "list":
        ctop1, ctop2 = st.columns([1.4, 4])
        if ctop1.button("➕ Create Manual Finished Good", use_container_width=True):
            st.session_state.finished_goods_mode = "add"
            st.session_state.selected_finished_good_id = None
            st.rerun()

        search_term = st.text_input("Search finished goods", placeholder="Search product, type, batch, status, or notes...")

        if "active_finished_goods_status" not in st.session_state:
            st.session_state.active_finished_goods_status = "All"

        st.subheader("View Finished Goods by Cure Status")
        status_tabs = ["All"] + cure_status_options
        status_filter = st.radio(
            "This filters the list only. To change a product status, use Quick Status or Edit.",
            status_tabs,
            horizontal=True,
            index=status_tabs.index(st.session_state.active_finished_goods_status) if st.session_state.active_finished_goods_status in status_tabs else 0
        )
        st.session_state.active_finished_goods_status = status_filter

        display_goods = goods.copy()
        if status_filter != "All":
            display_goods = display_goods[display_goods["cure_status"] == status_filter]
        if search_term:
            term = search_term.lower()
            searchable_cols = ["product_name", "product_type", "batch_number", "cure_status", "notes"]
            mask = pd.Series(False, index=display_goods.index)
            for col in searchable_cols:
                if col in display_goods.columns:
                    mask = mask | display_goods[col].fillna("").astype(str).str.lower().str.contains(term)
            display_goods = display_goods[mask]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Items Shown", len(display_goods))
        c2.metric("Cured", int((display_goods["cure_status"] == "Cured").sum()))
        c3.metric("Curing", int((display_goods["cure_status"] == "Curing").sum()))
        c4.metric("Inventory Value", f"${display_goods['total_value'].sum():.2f}")

        if display_goods.empty:
            st.info("No finished goods found for that search/filter.")
        else:
            st.markdown("### Finished Goods Lines")
            header = st.columns([1.65, 0.95, 0.65, 0.8, 0.9, 1, 0.8, 1.2, 0.7, 0.7])
            header[0].markdown("**Product**")
            header[1].markdown("**Batch**")
            header[2].markdown("**Qty Available**")
            header[3].markdown("**Cure Days**")
            header[4].markdown("**Ready Date**")
            header[5].markdown("**Status**")
            header[6].markdown("**Value**")
            header[7].markdown("**Quick Status**")
            header[8].markdown("**Edit**")
            header[9].markdown("**Delete**")

            for _, row in display_goods.sort_values(["product_name"]).iterrows():
                gid = int(row["id"])
                current_status = row.get("cure_status") if row.get("cure_status") in cure_status_options else "Curing"
                cols = st.columns([1.65, 0.95, 0.65, 0.8, 0.9, 1, 0.8, 1.2, 0.7, 0.7])
                cols[0].markdown(f"**{row.get('product_name') or ''}**")
                cols[1].markdown(f'<span class="fg-plain-cell">{row.get("batch_number") or row.get("batch_id") or "—"}</span>', unsafe_allow_html=True)
                cols[2].markdown(str(int(row.get("quantity_on_hand") or 0)))
                cols[3].markdown(str(int(row.get("cure_days") or 0)))
                cols[4].markdown(str(row.get("cure_date") or "—"))
                cols[5].markdown(cure_status_badge(current_status), unsafe_allow_html=True)
                cols[6].markdown(f"${float(row.get('total_value') or 0):.2f}")

                # Reliable quick status save. Select the status, then click Update.
                quick_status = cols[7].selectbox(
                    "Quick Status",
                    cure_status_options,
                    index=cure_status_options.index(current_status),
                    key=f"quick_status_{gid}",
                    label_visibility="collapsed"
                )
                if cols[7].button("Update", key=f"quick_status_update_{gid}", use_container_width=True):
                    ok, _ = update_finished_good_status(gid, quick_status, row.get("batch_id"), row.get("batch_number"))
                    if ok:
                        st.session_state.active_finished_goods_status = "All"
                        st.toast(f"Updated {row.get('product_name') or 'finished good'} to {quick_status}")
                        st.rerun()

                if cols[8].button("Edit", key=f"edit_finished_good_{gid}"):
                    st.session_state.selected_finished_good_id = gid
                    st.session_state.finished_goods_mode = "edit"
                    st.rerun()

                if cols[9].button("Delete", key=f"delete_finished_good_{gid}"):
                    st.session_state.selected_finished_good_id = gid
                    st.session_state.finished_goods_mode = "delete"
                    st.rerun()

                st.markdown("<hr style='margin: 0.55rem 0; border: none; border-top: 1px solid #eee;'>", unsafe_allow_html=True)

    elif st.session_state.finished_goods_mode in ["add", "edit"]:
        selected_id = st.session_state.selected_finished_good_id
        is_edit = st.session_state.finished_goods_mode == "edit"
        selected = None
        if is_edit:
            if goods.empty or selected_id is None or goods[goods["id"] == selected_id].empty:
                st.error("Finished goods line not found.")
            else:
                selected = goods[goods["id"] == selected_id].iloc[0]

        if (not is_edit) or selected is not None:
            st.subheader("Edit Finished Goods Line" if is_edit else "Create Manual Finished Good")

            if is_edit:
                current_quick_status = selected.get("cure_status") if selected.get("cure_status") in cure_status_options else "Curing"
                st.markdown(f"**Current Cure Status:** {cure_status_badge(current_quick_status)}", unsafe_allow_html=True)
                st.caption("Change the cure status below and click Save Finished Goods Line.")

            def as_date(value, fallback=date.today()):
                try:
                    if pd.isna(value) or value in [None, ""]:
                        return fallback
                    return pd.to_datetime(value).date()
                except Exception:
                    return fallback

            def parse_date_text(value, fallback):
                try:
                    if value is None or str(value).strip() == "":
                        return fallback
                    return pd.to_datetime(str(value).strip()).date()
                except Exception:
                    return fallback

            with st.form("finished_goods_edit_form"):
                c1, c2, c3 = st.columns(3)
                product_name = c1.text_input("Product Name", value=str(selected.get("product_name") or "") if is_edit else "")
                product_type = c2.text_input("Product Type", value=str(selected.get("product_type") or "") if is_edit else "")
                batch_id_value = selected.get("batch_id") if is_edit else None
                batch_label = str(selected.get("batch_number") or batch_id_value or "Manual") if is_edit else "Manual"
                c3.text_input("Batch", value=batch_label, disabled=True)

                photo_url = st.text_input("Product Photo URL", value=str(selected.get("photo_url") or "") if is_edit else "", help="Paste an image URL for now. Later we can add Supabase image upload.")
                description = st.text_area("Product Description", value=str(selected.get("description") or "") if is_edit else "", height=80)

                c4, c5, c6 = st.columns(3)
                qty = c4.number_input("Quantity On Hand", min_value=0, step=1, value=int(selected.get("quantity_on_hand") or 0) if is_edit else 0)
                cost_per_item = c5.number_input("Cost Per Item", min_value=0.0, step=0.01, value=float(selected.get("cost_per_item") or 0) if is_edit else 0.0)
                retail_price = c6.number_input("Retail Price", min_value=0.0, step=0.01, value=float(selected.get("retail_price") or 0) if is_edit else 0.0)

                current_status = selected.get("cure_status") if is_edit and selected.get("cure_status") in cure_status_options else "Curing"
                cure_status = st.radio(
                    "Cure Status",
                    cure_status_options,
                    index=cure_status_options.index(current_status),
                    horizontal=True
                )

                c7, c8, c9 = st.columns(3)
                cure_days = c7.number_input("Cure Days", min_value=0, step=1, value=int(selected.get("cure_days") or 0) if is_edit else 0)
                default_start = as_date(selected.get("cure_start_date") if is_edit else None)
                cure_start_text = c8.text_input("Cure Start Date", value=str(default_start), help="Use YYYY-MM-DD. This avoids the dark calendar popup.")
                start_for_calc = parse_date_text(cure_start_text, default_start)
                calculated_cure_date = start_for_calc + timedelta(days=int(cure_days or 0))
                default_ready = as_date(selected.get("cure_date") if is_edit else calculated_cure_date, calculated_cure_date)
                cure_date_text = c9.text_input("Ready / Cure Date", value=str(default_ready), help="Use YYYY-MM-DD, or match the calculated date.")

                cure_start_date = parse_date_text(cure_start_text, default_start)
                cure_date = parse_date_text(cure_date_text, calculated_cure_date)

                c10, c11 = st.columns(2)
                c10.metric("Calculated From Cure Days", str(calculated_cure_date))
                c11.markdown(f"**Selected Status:** {cure_status_badge(cure_status)}", unsafe_allow_html=True)

                notes = st.text_area("Notes", value=str(selected.get("notes") or "") if is_edit else "")
                save = st.form_submit_button("Save Finished Goods Line")

                if save:
                    data = {
                        "product_name": product_name.strip(),
                        "product_type": product_type.strip(),
                        "quantity_on_hand": qty,
                        "cost_per_item": cost_per_item,
                        "retail_price": retail_price,
                        "cure_status": cure_status,
                        "status": cure_status,
                        "hide_from_cure_tracking": False,
                        "cure_days": int(cure_days or 0),
                        "cure_start_date": str(cure_start_date),
                        "cure_date": str(cure_date),
                        "notes": notes.strip(),
                        "photo_url": photo_url.strip(),
                        "description": description.strip(),
                    }
                    try:
                        if is_edit:
                            try:
                                update_row("finished_goods", int(selected_id), data)
                            except Exception:
                                # Fallback for older Supabase tables that do not have every optional column yet.
                                minimal_data = {
                                    "product_name": product_name.strip(),
                                    "product_type": product_type.strip(),
                                    "quantity_on_hand": qty,
                                    "cost_per_item": cost_per_item,
                                    "retail_price": retail_price,
                                    "cure_status": cure_status,
                                    "cure_days": int(cure_days or 0),
                                    "cure_start_date": str(cure_start_date),
                                    "cure_date": str(cure_date),
                                    "notes": notes.strip(),
                                }
                                update_row("finished_goods", int(selected_id), minimal_data)
                            # Force status persistence and sync after the full save.
                            update_finished_good_status(int(selected_id), cure_status, batch_id_value, selected.get("batch_number"))
                        else:
                            try:
                                insert_row("finished_goods", data)
                            except Exception:
                                minimal_data = {
                                    "product_name": product_name.strip(),
                                    "product_type": product_type.strip(),
                                    "quantity_on_hand": qty,
                                    "cost_per_item": cost_per_item,
                                    "retail_price": retail_price,
                                    "cure_status": cure_status,
                                    "cure_days": int(cure_days or 0),
                                    "cure_start_date": str(cure_start_date),
                                    "cure_date": str(cure_date),
                                    "notes": notes.strip(),
                                }
                                insert_row("finished_goods", minimal_data)
                        st.session_state.active_finished_goods_status = "All"
                        st.session_state.finished_goods_mode = "list"
                        st.session_state.selected_finished_good_id = None
                        st.rerun()
                    except Exception as e:
                        st.error("This save did not persist. The app needs its database migration/permissions to be applied automatically in deployment.")
                        st.code(str(e))

    elif st.session_state.finished_goods_mode == "delete":
        selected_id = st.session_state.selected_finished_good_id
        if goods.empty or selected_id is None or goods[goods["id"] == selected_id].empty:
            st.error("Finished goods line not found.")
        else:
            selected = goods[goods["id"] == selected_id].iloc[0]
            st.subheader("Delete Finished Goods Line")
            st.warning("This removes this finished goods inventory line. It cannot be undone.")
            st.markdown(f"### {selected.get('product_name')}")
            d1, d2, d3 = st.columns([1, 1, 3])
            if d1.button("Delete Line", type="primary", use_container_width=True):
                try:
                    delete_row("finished_goods", selected_id)
                    st.session_state.finished_goods_mode = "list"
                    st.session_state.selected_finished_good_id = None
                    st.rerun()
                except Exception as e:
                    st.error("Could not delete this line. Supabase may need delete policies.")
                    st.code(str(e))
            if d2.button("Cancel", use_container_width=True):
                st.session_state.finished_goods_mode = "list"
                st.session_state.selected_finished_good_id = None
                st.rerun()

elif page == "Product Gallery":
    st.title("Product Gallery")
    st.caption("A clean product view with photos, inventory, cure status, and pricing.")
    goods = df("finished_goods")
    if goods.empty:
        st.info("No products yet. Add products from Finished Goods, then add a photo URL in Edit.")
    else:
        for col, default in {"product_name":"", "product_type":"", "quantity_on_hand":0, "retail_price":0, "cost_per_item":0, "cure_status":"Curing", "photo_url":"", "description":""}.items():
            if col not in goods.columns:
                goods[col] = default
        goods["quantity_on_hand"] = pd.to_numeric(goods["quantity_on_hand"], errors="coerce").fillna(0)
        goods["retail_price"] = pd.to_numeric(goods["retail_price"], errors="coerce").fillna(0)
        goods["cost_per_item"] = pd.to_numeric(goods["cost_per_item"], errors="coerce").fillna(0)
        search = st.text_input("Search products", placeholder="Search by product name, type, status...")
        display = goods.copy()
        if search:
            term = search.lower()
            display = display[
                display["product_name"].fillna("").astype(str).str.lower().str.contains(term) |
                display["product_type"].fillna("").astype(str).str.lower().str.contains(term) |
                display["cure_status"].fillna("").astype(str).str.lower().str.contains(term)
            ]
        if display.empty:
            st.info("No products match that search.")
        else:
            rows = display.drop_duplicates(subset=["product_name", "product_type"]).reset_index(drop=True)
            for start_idx in range(0, len(rows), 4):
                cols = st.columns(4)
                for col, (_, row) in zip(cols, rows.iloc[start_idx:start_idx+4].iterrows()):
                    with col:
                        photo = str(row.get("photo_url") or "").strip()
                        status = normalize_cure_status(row.get("cure_status") or "Curing")
                        if photo:
                            st.markdown(f'<div class="soap-product-card"><img class="soap-product-photo" src="{photo}"><h4>{row.get("product_name") or "Product"}</h4><p>{row.get("product_type") or ""}</p><p>{cure_status_badge(status)}</p><p><b>{int(row.get("quantity_on_hand") or 0)}</b> available</p><p>Retail: <b>${float(row.get("retail_price") or 0):.2f}</b></p></div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="soap-product-card"><div class="soap-placeholder-photo">Add Photo</div><h4>{row.get("product_name") or "Product"}</h4><p>{row.get("product_type") or ""}</p><p>{cure_status_badge(status)}</p><p><b>{int(row.get("quantity_on_hand") or 0)}</b> available</p><p>Retail: <b>${float(row.get("retail_price") or 0):.2f}</b></p></div>', unsafe_allow_html=True)

elif page == "Ingredient Label Generator":
    st.title("Ingredient Label Generator")
    recipes = df("recipes")
    if recipes.empty: st.warning("Create a recipe first.")
    else:
        choice = st.selectbox("Choose Recipe", recipes["id"].astype(str)+" - "+recipes["recipe_name"]); rid = int(choice.split(" - ")[0]); r = recipe_row(rid); lines = recipe_lines(rid)
        if lines.empty: st.info("No ingredients added yet.")
        else:
            label_lines = lines[lines["include_on_label"] == True].sort_values("amount_used", ascending=False)
            names=[]
            for _, row in label_lines.iterrows():
                names.append(row.get("label_name_override") or row.get("label_display_name") or row.get("item_name"))
            unique=[]
            for n in names:
                if n and n not in unique: unique.append(n)
            statement = "Ingredients: " + ", ".join(unique) + "."
            st.text_area("Generated Ingredient Statement", value=statement, height=120)
            st.text_area("Simple Label Template", value=f"{r['recipe_name']}\n\n{statement}\n\nNet Wt: ______\nMade by The Soap Lab / Fizzebath", height=250)

elif page == "Product Type View":
    st.title("Product Type View")
    ptype = st.selectbox("Product Type", ["Soap","Bath Bomb","Shower Steamer","Body Butter","Body Oil","Lotion","Cuticle Oil","Melt & Pour"])
    recipes, goods = df("recipes"), df("finished_goods")
    if not recipes.empty: st.dataframe(recipes[recipes["product_type"] == ptype], use_container_width=True)
    if not goods.empty: st.dataframe(goods[goods["product_type"] == ptype], use_container_width=True)

elif page == "Cure Tracking":
    st.title("Cure Tracking")
    goods = df("finished_goods")
    if goods.empty:
        st.info("No batches are in cure tracking yet.")
    else:
        for col in ["product_name", "cure_status", "cure_days", "cure_start_date", "cure_date", "quantity_on_hand", "notes", "hide_from_cure_tracking"]:
            if col not in goods.columns:
                goods[col] = "" if col in ["product_name", "cure_status", "cure_start_date", "cure_date", "notes"] else False if col == "hide_from_cure_tracking" else 0
        if "status" in goods.columns:
            # Prefer manual status fallback when present, because older installs may save there.
            status_text = goods["status"].fillna("").astype(str).str.strip()
            goods["cure_status"] = goods["cure_status"].where(status_text == "", goods["status"])
        goods["cure_status"] = goods["cure_status"].apply(normalize_cure_status)
        goods["cure_days"] = pd.to_numeric(goods["cure_days"], errors="coerce").fillna(0).astype(int)
        goods["quantity_on_hand"] = pd.to_numeric(goods["quantity_on_hand"], errors="coerce").fillna(0).astype(int)
        goods["hide_from_cure_tracking"] = goods["hide_from_cure_tracking"].fillna(False).astype(bool)
        show_hidden = st.checkbox("Show removed items", value=False)
        if not show_hidden:
            goods = goods[goods["hide_from_cure_tracking"] == False]
        status = st.radio("Show Status", ["All", "Not Started", "Curing", "Cured", "Needs Review"], horizontal=True)
        show = goods.copy()
        if status != "All":
            show = show[show["cure_status"] == status]
        if show.empty:
            st.info("No cure tracking items found for that status.")
        else:
            header = st.columns([2, 0.9, 1.1, 0.8, 1, 1, 1.2, 0.9])
            header[0].markdown("**Product**")
            header[1].markdown("**Qty Available**")
            header[2].markdown("**Status**")
            header[3].markdown("**Cure Days**")
            header[4].markdown("**Start Date**")
            header[5].markdown("**Ready Date**")
            header[6].markdown("**Notes**")
            header[7].markdown("**Remove**")
            for _, row in show.sort_values(["cure_status", "product_name"]).iterrows():
                cols = st.columns([2, 0.9, 1.1, 0.8, 1, 1, 1.2, 0.9])
                cols[0].markdown(f"**{row.get('product_name') or ''}**")
                cols[1].markdown(str(int(row.get("quantity_on_hand") or 0)))
                cols[2].markdown(cure_status_badge(row.get("cure_status") or "Curing"), unsafe_allow_html=True)
                cols[3].markdown(str(int(row.get("cure_days") or 0)))
                cols[4].markdown(str(row.get("cure_start_date") or "—"))
                cols[5].markdown(str(row.get("cure_date") or "—"))
                cols[6].markdown(str(row.get("notes") or ""))
                if cols[7].button("Remove", key=f"remove_from_cure_{int(row.get("id"))}"):
                    try:
                        update_row("finished_goods", int(row.get("id")), {"hide_from_cure_tracking": True})
                        st.rerun()
                    except Exception as e:
                        st.error("Could not remove from Cure Tracking. Run the v1.4.4 SQL first.")
                        st.code(str(e))
                st.markdown("<hr style='margin: 0.35rem 0; border: none; border-top: 1px solid #eee;'>", unsafe_allow_html=True)

elif page == "Reports":
    st.title("Reports")
    inv, recipes, batches, goods, sales = df("inventory"), df("recipes"), df("batches"), df("finished_goods"), df("sales")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Inventory Items", len(inv))
    c2.metric("Recipes", len(recipes))
    c3.metric("Batches", len(batches))
    c4.metric("Finished Goods", len(goods))
    if not goods.empty:
        if "quantity_on_hand" in goods.columns and "cost_per_item" in goods.columns:
            goods["total_value"] = pd.to_numeric(goods["quantity_on_hand"], errors="coerce").fillna(0) * pd.to_numeric(goods["cost_per_item"], errors="coerce").fillna(0)
            st.subheader("Finished Goods Value")
            st.metric("Total Finished Goods Value", f"${goods['total_value'].sum():.2f}")
            st.dataframe(goods.sort_values("product_name"), use_container_width=True, hide_index=True)

elif page == "Suppliers":
    st.title("Suppliers")
    inv = df("inventory")
    if inv.empty or "supplier" not in inv.columns:
        st.info("Suppliers will appear here once they are used in inventory.")
    else:
        suppliers = inv.groupby("supplier", dropna=False).agg(item_count=("id", "count")).reset_index().sort_values("supplier")
        st.dataframe(suppliers, use_container_width=True, hide_index=True)

elif page == "Categories":
    st.title("Categories")
    st.write("Recipe, inventory, and fragrance categories are managed inside their matching modules.")
    for label, table in [("Recipe Categories", "recipe_categories"), ("Inventory Categories", "inventory_categories"), ("Fragrance Categories", "fragrance_categories")]:
        st.subheader(label)
        data = safe_table_df(table)
        if data.empty:
            st.info(f"No custom {label.lower()} yet.")
        else:
            st.dataframe(data, use_container_width=True, hide_index=True)

elif page == "Units":
    st.title("Units")
    st.info("Default units currently supported: oz, lb, g, kg, fl oz, and each. Custom unit management can be added in a future build.")

elif page == "My Settings":
    st.title("My Settings")
    st.caption("Choose the color theme for The Soap Lab interface.")

    theme_names = list(THEMES.keys())
    current_theme = st.session_state.get("app_theme", "Lavender")
    selected_theme = st.radio(
        "App Color Theme",
        theme_names,
        horizontal=True,
        index=theme_names.index(current_theme) if current_theme in theme_names else 0,
    )

    if selected_theme != current_theme:
        st.session_state.app_theme = selected_theme
        st.toast(f"Theme changed to {selected_theme}")
        st.rerun()

    palette = THEMES[selected_theme]
    st.markdown("### Theme Preview")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div style="background:{palette["accent"]};color:white;padding:16px;border-radius:12px;font-weight:800;text-align:center;">Main Button</div>', unsafe_allow_html=True)
    c2.markdown(f'<div style="background:{palette["soft"]};color:#111827;padding:16px;border-radius:12px;font-weight:800;text-align:center;border:1px solid {palette["border"]};">Soft Accent</div>', unsafe_allow_html=True)
    c3.markdown(f'<div style="background:{palette["pale"]};color:#111827;padding:16px;border-radius:12px;font-weight:800;text-align:center;border:1px solid #E5E7EB;">Page Background</div>', unsafe_allow_html=True)
    c4.markdown(f'<div style="background:{palette["dark"]};color:white;padding:16px;border-radius:12px;font-weight:800;text-align:center;">Dark Accent</div>', unsafe_allow_html=True)

    st.info("For now, themes save for the current browser session. Later we can store each user's theme in Supabase so it follows their login.")

elif page in ["Sales Tracker", "POS / Sales"]:
    st.title("Sales Tracker")
    with st.form("sale"):
        c1,c2,c3 = st.columns(3); sale_date = c1.date_input("Sale Date", value=date.today()); channel = c2.selectbox("Channel", ["Etsy","Shopify","Craft Show","Facebook","Direct","Other"]); product = c3.text_input("Product Name")
        c4,c5,c6 = st.columns(3); qty = c4.number_input("Quantity Sold", min_value=1, step=1); price = c5.number_input("Sale Price Each", min_value=0.0, step=.01); fees = c6.number_input("Fees", min_value=0.0, step=.01)
        ship = st.number_input("Shipping / Packing Material Cost", min_value=0.0, step=.01); cname = st.text_input("Customer Name"); email = st.text_input("Customer Email"); notes = st.text_area("Notes")
        if st.form_submit_button("Save Sale"):
            insert("sales", {"sale_date":str(sale_date),"channel":channel,"product_name":product,"quantity_sold":qty,"sale_price_each":price,"fees":fees,"shipping_material_cost":ship,"customer_name":cname,"customer_email":email,"notes":notes}); st.rerun()
    sales = df("sales")
    if not sales.empty: st.dataframe(sales.sort_values("sale_date", ascending=False), use_container_width=True)
