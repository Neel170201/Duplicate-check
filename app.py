import streamlit as st
import pandas as pd
import io
from datetime import datetime
import numpy as np


# Configure page
st.set_page_config(
    page_title="BRIGHT TRADING INDIA LLP",
    page_icon="💎",
    layout="wide"
)

# ------------------------------------------------------------
# FIX #1: Remove pandas Styler's cell-limit.
# By default pandas caps styled tables at ~262,144 cells
# (rows x columns). With ~38,000 rows x 12 columns you cross
# that limit (~450,000+ cells) and pandas silently stops
# rendering/styling the rest -> looks like a "limited" table.
# Bumping this option removes that cap.
# ------------------------------------------------------------
pd.set_option("styler.render.max_elements", 5_000_000)

# ============================================================
#  GLOBAL THEME — Navy & Gold, locked to light mode
# ============================================================
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600;700&display=swap');

/* ---------- FORCE LIGHT THEME EVERYWHERE ---------- */
/* Overrides Streamlit's internal theme variables so the app
   always renders light, even if a visitor's OS/browser is
   set to dark mode or they had dark mode selected before. */
:root, .stApp, [data-theme="dark"], .stApp[data-theme="dark"] {
    --background-color: #ffffff !important;
    --secondary-background-color: #f2efe6 !important;
    --text-color: #14171f !important;
    --primary-color: #c9a24b !important;

    --navy-950: #0a1128;
    --navy-900: #0f1c3f;
    --navy-800: #16264f;
    --navy-700: #1e3163;
    --gold-500: #c9a24b;
    --gold-400: #d9b96a;
    --gold-300: #e8cf94;
    --cream-50:  #faf8f3;
    --ink-900:  #14171f;
    --ink-600:  #4a5164;
    --success-bg: #e5f5e8;
    --success-fg: #1e7a34;
    --danger-bg:  #fbe8e8;
    --danger-fg:  #b0292f;
}

html, body, [class*="css"]  {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    color-scheme: light !important;
}

/* Kill any dark-mode surface Streamlit tries to paint */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"],
[data-testid="stSidebar"], [data-testid="stToolbar"], body {
    background-color: #ffffff !important;
}

/* App background — soft warm neutral with faint diamond-facet texture */
.stApp {
    background:
        radial-gradient(circle at 15% 10%, rgba(201,162,75,0.05) 0%, rgba(201,162,75,0) 45%),
        radial-gradient(circle at 85% 85%, rgba(15,28,63,0.04) 0%, rgba(15,28,63,0) 45%),
        linear-gradient(180deg, #ffffff 0%, #f8f6f0 100%) !important;
}

/* Main content card */
.block-container {
    max-width: 1420px;
    margin: 2rem auto;
    padding: 2.6rem 3rem 3rem 3rem;
    background: #ffffff;
    border-radius: 22px;
    box-shadow: 0 16px 50px rgba(15, 28, 63, 0.09);
    border: 1px solid rgba(201, 162, 75, 0.18);
    position: relative;
}

/* Base text color */
html, body, p, label, span, div {
    color: var(--ink-900);
}

h1, h2, h3, h4 {
    font-family: 'Playfair Display', 'Segoe UI', serif;
    color: var(--navy-900);
}

/* ---------- Hero header ---------- */
.hero {
    position: relative;
    background: linear-gradient(120deg, var(--navy-950) 0%, var(--navy-800) 55%, var(--navy-900) 100%);
    border-radius: 20px;
    padding: 2.8rem 2.8rem 2.4rem 2.8rem;
    margin-bottom: 2.2rem;
    overflow: hidden;
    border: 1px solid rgba(201, 162, 75, 0.4);
    box-shadow: 0 16px 40px rgba(10, 17, 40, 0.28);
}

.hero::before {
    content: "";
    position: absolute;
    top: -45%; right: -8%;
    width: 460px; height: 460px;
    background: radial-gradient(circle, rgba(201,162,75,0.22) 0%, rgba(201,162,75,0) 70%);
    pointer-events: none;
}

.hero::after {
    content: "";
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(30deg, rgba(255,255,255,0.035) 1px, transparent 1px),
        linear-gradient(-30deg, rgba(255,255,255,0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
    background-size: 46px 80px, 46px 80px, 46px 80px;
    pointer-events: none;
}

.hero-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    z-index: 1;
}

.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    font-weight: 600;
    color: var(--gold-300);
    text-transform: uppercase;
    border: 1px solid rgba(201, 162, 75, 0.45);
    padding: 5px 14px;
    border-radius: 999px;
    margin-bottom: 1rem;
    background: rgba(201, 162, 75, 0.07);
}

.hero-badge {
    font-size: 0.72rem;
    color: rgba(255,255,255,0.55);
    border: 1px solid rgba(255,255,255,0.18);
    padding: 5px 12px;
    border-radius: 999px;
    letter-spacing: 0.04em;
}

div.hero h1, .hero h1, .hero h1 * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-size: 2.3rem;
    margin: 0 0 0.35rem 0;
    letter-spacing: 0.01em;
    position: relative;
    z-index: 1;
}

div.hero p, .hero p {
    color: rgba(255,255,255,0.72) !important;
    -webkit-text-fill-color: rgba(255,255,255,0.72) !important;
    font-size: 1rem;
    margin: 0;
    font-family: 'Inter', sans-serif;
    position: relative;
    z-index: 1;
}

.hero-divider {
    height: 1px;
    margin: 1.4rem 0 1.1rem 0;
    background: linear-gradient(90deg, rgba(201,162,75,0.55), rgba(201,162,75,0.05));
    position: relative;
    z-index: 1;
}

.hero-stats {
    display: flex;
    gap: 2.2rem;
    position: relative;
    z-index: 1;
}
.hero-stats .item { display:flex; flex-direction:column; gap:2px; }
.hero-stats .item .k { color: var(--gold-300); font-size: 0.68rem; letter-spacing: 0.08em; text-transform: uppercase; }
.hero-stats .item .v { color: #fff; font-family: 'Playfair Display', serif; font-size: 1.05rem; }

.hero-signature {
    position: absolute;
    bottom: 14px;
    right: 22px;
    font-size: 0.75rem;
    font-style: italic;
    color: rgba(232, 207, 148, 0.6);
    z-index: 1;
}

/* ---------- Section labels ---------- */
.section-label {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
    color: var(--navy-900);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin: 1.8rem 0 1rem 0;
}
.section-label::after {
    content: "";
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(201,162,75,0.5), rgba(201,162,75,0));
}

/* ---------- Info / helper card ---------- */
.info-card {
    display: flex;
    align-items: flex-start;
    gap: 0.9rem;
    background: linear-gradient(135deg, #fbf9f4 0%, #f5f0e4 100%);
    border: 1px solid rgba(201, 162, 75, 0.3);
    border-radius: 14px;
    padding: 1rem 1.2rem;
    margin-bottom: 1.4rem;
}
.info-card .icon { font-size: 1.4rem; line-height: 1; }
.info-card .txt-title { font-weight: 700; color: var(--navy-900); font-size: 0.92rem; margin-bottom: 2px; }
.info-card .txt-sub { color: var(--ink-600); font-size: 0.82rem; }

/* ---------- File uploader ---------- */
[data-testid="stFileUploaderDropzone"] {
    background: var(--cream-50) !important;
    border: 1.5px dashed rgba(201, 162, 75, 0.55) !important;
    border-radius: 14px !important;
    transition: all 0.2s ease;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: var(--gold-500) !important;
    background: #fbf7ec !important;
}

/* ---------- Buttons ---------- */
.stButton > button, .stDownloadButton > button {
    background: linear-gradient(135deg, var(--navy-900), var(--navy-700));
    color: #ffffff !important;
    border: 1px solid var(--gold-500);
    border-radius: 10px;
    padding: 0.65rem 1.7rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    transition: all 0.2s ease;
    box-shadow: 0 4px 14px rgba(15, 28, 63, 0.18);
}
.stButton > button:hover, .stDownloadButton > button:hover {
    background: linear-gradient(135deg, var(--navy-700), var(--navy-900));
    border-color: var(--gold-400);
    box-shadow: 0 8px 24px rgba(15, 28, 63, 0.3);
    transform: translateY(-1px);
    color: #ffffff !important;
}
.stButton > button p, .stDownloadButton > button p { color: #ffffff !important; }

/* ---------- Metric cards ---------- */
[data-testid="stMetric"] {
    background: linear-gradient(180deg, #ffffff 0%, var(--cream-50) 100%);
    border: 1px solid rgba(201, 162, 75, 0.28);
    border-radius: 16px;
    padding: 1.1rem 1.3rem 0.9rem 1.3rem;
    box-shadow: 0 6px 18px rgba(15, 28, 63, 0.06);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 26px rgba(15, 28, 63, 0.1);
    border-color: rgba(201, 162, 75, 0.5);
}
[data-testid="stMetricLabel"] {
    color: var(--ink-600) !important;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 0.72rem;
    letter-spacing: 0.05em;
}
[data-testid="stMetricValue"] {
    color: var(--navy-900) !important;
    font-family: 'Playfair Display', serif;
}

/* ---------- Alerts ---------- */
[data-testid="stAlert"] {
    border-radius: 12px;
    border: 1px solid rgba(201, 162, 75, 0.25);
}

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    border-bottom: 1px solid rgba(201,162,75,0.25);
}
.stTabs [data-baseweb="tab"] {
    font-weight: 600;
    color: var(--ink-600);
}
.stTabs [aria-selected="true"] {
    color: var(--navy-900) !important;
    border-bottom-color: var(--gold-500) !important;
}

/* ---------- Multiselect / Select boxes ---------- */
[data-baseweb="select"] > div {
    border-radius: 10px !important;
    border-color: rgba(201, 162, 75, 0.35) !important;
}
[data-baseweb="tag"] {
    background-color: var(--navy-900) !important;
}

/* ---------- Dataframe ---------- */
[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid rgba(201, 162, 75, 0.25);
    box-shadow: 0 6px 18px rgba(15, 28, 63, 0.05);
}

/* ---------- Legend chips ---------- */
.legend-row { display: flex; gap: 0.8rem; margin: 0.6rem 0 1.2rem 0; }
.legend-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.78rem;
    font-weight: 600;
    padding: 5px 12px;
    border-radius: 999px;
}
.legend-chip.sel { background: var(--success-bg); color: var(--success-fg); }
.legend-chip.rej { background: var(--danger-bg); color: var(--danger-fg); }
.legend-dot { width: 8px; height: 8px; border-radius: 50%; display:inline-block; }
.legend-chip.sel .legend-dot { background: var(--success-fg); }
.legend-chip.rej .legend-dot { background: var(--danger-fg); }

/* ---------- Divider ---------- */
hr {
    border-top: 1px solid rgba(201, 162, 75, 0.3) !important;
}

/* ---------- Footer ---------- */
.app-footer {
    text-align: center;
    margin-top: 2.6rem;
    padding-top: 1.3rem;
    border-top: 1px solid rgba(201, 162, 75, 0.25);
    color: var(--ink-600);
    font-size: 0.8rem;
    letter-spacing: 0.02em;
}
.app-footer .dot { color: var(--gold-500); margin: 0 8px; }

</style>
""", unsafe_allow_html=True)


def validate_master_file(df):
    """Validate master file has required columns"""
    required_columns = ['Shape', 'From Size', 'To Size', 'Color', 'Clarity', 'Grid', 'Available', 'On Memo', '1.5 MONTH SOLD PCS']
    missing_columns = [col for col in required_columns if col not in df.columns]
    return len(missing_columns) == 0, missing_columns

def validate_pool_file(df):
    """Validate pool file has required columns"""
    required_columns = ['STOCKID', 'Shape', 'Size', 'Color', 'Clarity']
    missing_columns = [col for col in required_columns if col not in df.columns]
    return len(missing_columns) == 0, missing_columns


def process_stones_selection(master_df, pool_df):
    """
    Process stone selection based on the provided algorithm.

    OPTIMIZED VERSION — same logic/output as before, but:
      1. Pre-computes lower/upper-cased match columns ONCE instead of
         re-running .str.lower()/.str.upper() on every master row.
      2. Works with raw numpy arrays instead of repeated pandas .loc
         assignments + .replace('', 0) over the FULL pool on every
         iteration (that .replace() call over ~38k rows, run once per
         master row, was the single biggest cost — O(master_rows x pool_rows)
         of expensive string replace operations).
      3. Picks the "smallest N eligible sizes" using argsort on just the
         eligible subset instead of sort_values().head() on a larger slice.
      4. Vectorizes the 'Group' label instead of a per-row .apply().
    """

    pool = pool_df.copy()
    n = len(pool)

    # ---- Precompute match keys ONCE (vectorized, not per master row) ----
    pool_shape_lower = pool['Shape'].astype(str).str.lower().to_numpy()
    pool_color_upper = pool['Color'].astype(str).str.upper().to_numpy()
    pool_clarity_upper = pool['Clarity'].astype(str).str.upper().to_numpy()
    pool_size = pd.to_numeric(pool['Size'], errors='coerce').to_numpy()

    # ---- Output arrays, initialized once (no repeated full-frame resets) ----
    from_size_arr = np.full(n, np.nan)
    to_size_arr = np.full(n, np.nan)
    grid_arr = np.zeros(n)
    available_arr = np.zeros(n)
    memo_arr = np.zeros(n)
    sold_arr = np.zeros(n)
    remark_arr = np.full(n, '', dtype=object)

    for _, row in master_df.iterrows():
        shape = str(row['Shape']).lower()
        from_size = row['From Size']
        to_size = row['To Size']
        color = str(row['Color']).upper()
        clarity = str(row['Clarity']).upper()
        required = row['Grid']
        available = row['Available']
        memo = row['On Memo']
        sold = row['1.5 MONTH SOLD PCS']

        remaining = required - available

        match_mask = (
            (pool_shape_lower == shape) &
            (pool_size >= from_size) &
            (pool_size <= to_size) &
            (pool_color_upper == color) &
            (pool_clarity_upper == clarity)
        )

        if not match_mask.any():
            continue

        match_idx = np.where(match_mask)[0]

        # Tag all matching pool rows with this requirement's info
        from_size_arr[match_idx] = from_size
        to_size_arr[match_idx] = to_size
        grid_arr[match_idx] = required
        available_arr[match_idx] = available
        memo_arr[match_idx] = memo
        sold_arr[match_idx] = sold

        if remaining <= 0:
            continue

        # Eligible = matched AND not already picked by an earlier requirement
        eligible_idx = match_idx[remark_arr[match_idx] == '']
        if eligible_idx.size == 0:
            continue

        k = int(remaining)
        if k >= eligible_idx.size:
            selected_idx = eligible_idx
        else:
            # Only sort within the (small) eligible subset, not the whole pool
            order = np.argsort(pool_size[eligible_idx], kind='mergesort')[:k]
            selected_idx = eligible_idx[order]

        remark_arr[selected_idx] = 'SELECTION'

    # Anything never matched/selected -> Rejection
    remark_arr[remark_arr == ''] = 'REJECTION'

    pool['From Size'] = from_size_arr
    pool['To Size'] = to_size_arr
    pool['Grid'] = grid_arr
    pool['Available'] = available_arr
    pool['On Memo'] = memo_arr
    pool['1.5 MONTH SOLD PCS'] = sold_arr
    pool['Remark'] = remark_arr

    # Add 'Same' column with count of identical Shape + From Size + To Size + Color + Clarity combinations
    pool['Same'] = pool.groupby(
        ['Shape', 'From Size', 'To Size', 'Color', 'Clarity']
    )['Shape'].transform('count')

    # Add 'Group' column with 'From Size' and 'To Size' in 0.00 format (vectorized, no per-row apply)
    valid_mask = pool['From Size'].notna() & pool['To Size'].notna()
    group_col = np.full(n, '-', dtype=object)
    if valid_mask.any():
        formatted = (
            pool.loc[valid_mask, 'From Size'].map('{:.2f}'.format)
            + ' - '
            + pool.loc[valid_mask, 'To Size'].map('{:.2f}'.format)
        )
        group_col[valid_mask.to_numpy()] = formatted.to_numpy()
    pool['Group'] = group_col

    # Drop 'From Size' and 'To Size' columns
    pool.drop(columns=['From Size', 'To Size'], inplace=True)

    # Reorder columns as per desired output
    final_columns = [
        'STOCKID', 'Shape', 'Size', 'Color', 'Clarity',
        'Group', 'Grid', 'Available', 'On Memo', '1.5 MONTH SOLD PCS',
        'Same', 'Remark'
    ]
    pool = pool[final_columns]

    return pool

def calculate_statistics(processed_df):
    """Calculate summary statistics from processed dataframe safely."""
    if processed_df.empty:
        return {
            'total_stones': 0,
            'selections': 0,
            'rejections': 0,
            'selection_rate': 0.0,
            'avg_fulfillment': 0.0,
            'unique_requirements': 0
        }

    total_stones = len(processed_df)
    selections = (processed_df['Remark'] == 'SELECTION').sum()
    rejections = (processed_df['Remark'] == 'REJECTION').sum()

    # ✅ Safe groupby with numeric conversion
    grouped = processed_df.groupby(['Shape', 'Group', 'Color', 'Clarity']).agg({
        'Grid': 'first',
        'Available': 'first',
        'Remark': lambda x: (x == 'SELECTION').sum()
    }).reset_index()

    # Ensure numeric types
    grouped['Grid'] = pd.to_numeric(grouped['Grid'], errors='coerce').fillna(0)
    grouped['Available'] = pd.to_numeric(grouped['Available'], errors='coerce').fillna(0)

    # ✅ Required stones (never negative)
    grouped['Required'] = (grouped['Grid'] - grouped['Available']).clip(lower=0)

    # ✅ Fulfillment calculation
    grouped['Fulfillment_Rate'] = np.where(
        grouped['Required'] > 0,
        (grouped['Remark'] / grouped['Required'] * 100).clip(upper=100),
        100.0  # If nothing required → assume 100% fulfilled
    )

    avg_fulfillment = grouped['Fulfillment_Rate'].mean() if not grouped.empty else 0.0

    return {
        'total_stones': int(total_stones),
        'selections': int(selections),
        'rejections': int(rejections),
        'selection_rate': round((selections / total_stones * 100), 2) if total_stones > 0 else 0.0,
        'avg_fulfillment': round(avg_fulfillment, 2),
        'unique_requirements': len(grouped)
    }


def main():

    # ---------- Hero header ----------
    now_str = datetime.now().strftime("%d %b %Y")
    st.markdown(f"""
    <div class="hero">
        <div class="hero-top">
            <div>
                <span class="hero-eyebrow">💎 Diamond &amp; Gemstone Trading</span>
                <h1 style="color:#ffffff !important;-webkit-text-fill-color:#ffffff !important;">BRIGHT TRADING INDIA LLP</h1>
                <p style="color:rgba(255,255,255,0.72) !important;-webkit-text-fill-color:rgba(255,255,255,0.72) !important;">Automated stone selection and inventory processing</p>
            </div>
            <span class="hero-badge">{now_str}</span>
        </div>
        <div class="hero-divider"></div>
        <div class="hero-stats">
            <div class="item"><span class="k">Engine</span><span class="v">Auto-Match &amp; Grid Fulfillment</span></div>
            <div class="item"><span class="k">Output</span><span class="v">Excel Export Ready</span></div>
            <div class="item"><span class="k">Mode</span><span class="v">Real-time Filtering</span></div>
        </div>
        <div class="hero-signature">Designed by Neel Limbachiya</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">📁 Upload Files</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-card">
        <div class="icon">🗂️</div>
        <div>
            <div class="txt-title">Two files required to run a match</div>
            <div class="txt-sub">Master Refile File defines what's needed per Shape/Size/Color/Clarity — the Pool File is your live inventory to select from.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    upload_col1, upload_col2 = st.columns(2)

    with upload_col1:
        master_file = st.file_uploader(
            "Upload Master Refile File",
            type=['xlsx', 'xls'],
            help="Excel file containing master stone requirement"
        )

    with upload_col2:
        pool_file = st.file_uploader(
            "Upload File For Selections",
            type=['xlsx', 'xls'],
            help="Excel file containing available stone inventory"
        )

    # Validation
    if master_file is None or pool_file is None:
        st.info("👆 Please upload both Master and Party Excel files to begin processing")
        st.stop()

    try:
        # Load files
        with st.spinner("Loading files..."):
            master_df = pd.read_excel(master_file)
            pool_df = pd.read_excel(pool_file)

        # Validate structure
        master_valid, master_missing = validate_master_file(master_df)
        pool_valid, pool_missing = validate_pool_file(pool_df)

        if not master_valid:
            st.error(f"❌ Master file is missing required columns: {', '.join(master_missing)}")
            st.stop()

        if not pool_valid:
            st.error(f"❌ Pool file is missing required columns: {', '.join(pool_missing)}")
            st.stop()

        # ✅ Unique shapes from Party file
        party_shapes = pool_df['Shape'].dropna().unique()

        # ✅ Filter Master File based on Party Shapes
        filtered_master_df = master_df[master_df['Shape'].isin(party_shapes)]

        # ✅ Check if any shapes are missing in Master File
        missing_shapes = set(party_shapes) - set(master_df['Shape'].unique())
        if missing_shapes:
            st.warning(f"⚠️ These shapes are in Party File but missing in Master File: {', '.join(missing_shapes)}")

        st.success("✅ Files loaded successfully!")

        tab1 = st.tabs(["📊 Stone Selection"])[0]

        with tab1:
            st.markdown('<div class="section-label">📦 Overview</div>', unsafe_allow_html=True)
            col1 = st.columns(1)[0]  # Only one column now
            with col1:
                st.metric("Available Stones", f"{len(pool_df)} stones")

            # Process button
            if st.button("🔄 Process Stone Selection", type="primary"):
                with st.spinner("Processing stone selection..."):
                    try:
                        start_time = datetime.now()

                        # ✅ Use filtered master file
                        processed_df = process_stones_selection(filtered_master_df, pool_df)

                        # Store in session state
                        st.session_state.processed_df = processed_df
                        st.session_state.statistics = calculate_statistics(processed_df)

                        elapsed = (datetime.now() - start_time).total_seconds()
                        st.success(f"✅ Processing completed in {elapsed:.1f} seconds!")
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error during processing: {str(e)}")

            # Display results if available
            if 'processed_df' in st.session_state:
                st.markdown('<div class="section-label">📊 Results Summary</div>', unsafe_allow_html=True)

                # Statistics
                stats = st.session_state.statistics
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Total Stones", stats['total_stones'])
                with col2:
                    st.metric("Selections", stats['selections'], f"{stats['selection_rate']:.1f}%")
                with col3:
                    st.metric("Rejections", stats['rejections'])
                with col4:
                    st.metric("Avg Fulfillment", f"{stats['avg_fulfillment']:.1f}%")

                # Results table
                st.markdown('<div class="section-label">🔍 Detailed Results</div>', unsafe_allow_html=True)

                st.markdown("""
                <div class="legend-row">
                    <span class="legend-chip sel"><span class="legend-dot"></span>Selection — matched &amp; picked</span>
                    <span class="legend-chip rej"><span class="legend-dot"></span>Rejection — not selected</span>
                </div>
                """, unsafe_allow_html=True)

                df = st.session_state.processed_df.copy()

                # Create 5 columns in one row
                col1, col2, col3, col4, col5 = st.columns(5)

                # Shape Filter
                with col1:
                    shape_options = sorted(df['Shape'].dropna().unique().tolist())
                    shape_filter = st.multiselect("Shape", options=shape_options)

                df_shape = df[df['Shape'].isin(shape_filter)] if shape_filter else df

                # Color Filter
                with col2:
                    color_options = sorted(df_shape['Color'].dropna().unique().tolist())
                    color_filter = st.multiselect("Color", options=color_options)

                df_color = df_shape[df_shape['Color'].isin(color_filter)] if color_filter else df_shape

                # Clarity Filter
                with col3:
                    clarity_options = sorted(df_color['Clarity'].dropna().unique().tolist())
                    clarity_filter = st.multiselect("Clarity", options=clarity_options)

                df_clarity = df_color[df_color['Clarity'].isin(clarity_filter)] if clarity_filter else df_color

                # Group Filter
                with col4:
                    group_options = sorted(df_clarity['Group'].dropna().unique().tolist())
                    group_filter = st.multiselect("Group", options=group_options)

                df_group = df_clarity[df_clarity['Group'].isin(group_filter)] if group_filter else df_clarity

                # Status Filter
                with col5:
                    remark_options = sorted(df_group['Remark'].dropna().unique().tolist())
                    remark_filter = st.multiselect("Status", options=remark_options)

                # Final filter
                filtered_df = df_group[df_group['Remark'].isin(remark_filter)] if remark_filter else df_group

                # Color code the dataframe for better visualization
                def highlight_remark(val):
                    if val == 'SELECTION':
                        return 'background-color: #e5f5e8; color: #1e7a34; font-weight: 600;'
                    elif val == 'REJECTION':
                        return 'background-color: #fbe8e8; color: #b0292f; font-weight: 600;'
                    return ''

                styled_df = filtered_df.style.applymap(highlight_remark, subset=['Remark'])

                st.dataframe(
                    styled_df,
                    use_container_width=True,
                    height=600
                )

                st.info(f"Showing {len(filtered_df)} of {len(st.session_state.processed_df)} total stones")

                # Download button
                st.markdown('<div class="section-label">📥 Export Results</div>', unsafe_allow_html=True)

                # Create Excel file in memory
                output_buffer = io.BytesIO()
                with pd.ExcelWriter(output_buffer, engine='openpyxl') as writer:
                    st.session_state.processed_df.to_excel(writer, sheet_name='Stone Selection Results', index=False)

                    # Add summary sheet
                    summary_df = pd.DataFrame([stats])
                    summary_df.to_excel(writer, sheet_name='Summary Statistics', index=False)

                output_buffer.seek(0)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"stones_selected_output_{timestamp}.xlsx"

                st.download_button(
                    label="Download Excel",
                    data=output_buffer.getvalue(),
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        st.markdown("""
        <div class="app-footer">
            BRIGHT TRADING INDIA LLP <span class="dot">•</span> Internal Stone Selection Tool <span class="dot">•</span> Designed by Neel Limbachiya
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error loading files: {str(e)}")
        st.info("Please ensure your Excel files are properly formatted and not corrupted.")

if __name__ == "__main__":
    main()
