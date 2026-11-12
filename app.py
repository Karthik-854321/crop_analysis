import io
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from src.database import init_db, save_records, load_records, get_connection
from src.validation import normalize_columns, validate_records, QUALITY_COLUMNS
from src.analysis import build_summary, yearly_comparison, calculate_yield
from src.charts import production_trend, yield_trend, region_comparison

st.set_page_config(page_title="Crop Production Analysis", page_icon="🌾", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --field-ink: #20362b;
        --field-muted: #68766b;
        --field-green: #315b43;
        --field-green-dark: #244734;
        --field-sage: #e6ecdf;
        --field-paper: #f5f4ed;
        --field-clay: #eee9dc;
        --field-line: #dce2d5;
        --clay-shadow: 7px 7px 18px rgba(63, 75, 58, 0.10),
                       -6px -6px 16px rgba(255, 255, 250, 0.82);
    }

    .stApp {
        background:
            radial-gradient(ellipse at 84% 2%, rgba(221, 231, 207, 0.48), transparent 28rem),
            var(--field-paper);
        color: var(--field-ink);
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stMainBlockContainer"] {
        max-width: 1540px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #edf0e7 0%, #e8ecdf 100%);
        border-right: 1px solid rgba(49, 91, 67, 0.10);
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: var(--field-muted);
    }
    .field-brand {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin: 0.25rem 0 1.8rem;
    }
    .field-brand-mark {
        display: grid;
        place-items: center;
        width: 2.8rem;
        height: 2.8rem;
        border-radius: 1rem;
        background: linear-gradient(145deg, #f8f8ef, #dce5d5);
        box-shadow: var(--clay-shadow);
        color: var(--field-green);
        font-size: 1.3rem;
    }
    .field-brand-name {
        color: var(--field-ink);
        font-size: 1rem;
        font-weight: 750;
        letter-spacing: -0.02em;
    }
    .field-brand-caption {
        margin-top: 0.15rem;
        color: var(--field-muted);
        font-size: 0.72rem;
    }
    .field-hero {
        position: relative;
        overflow: hidden;
        margin: 0 0 1.8rem;
        padding: clamp(1.6rem, 3vw, 2.6rem);
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 1.8rem;
        background: linear-gradient(115deg, #294a37 0%, #3c674b 64%, #68845a 100%);
        box-shadow: 10px 12px 26px rgba(42, 66, 47, 0.17),
                    inset 1px 1px 0 rgba(255, 255, 255, 0.18);
        color: #f8f7ed;
    }
    .field-hero::after {
        position: absolute;
        top: -7rem;
        right: -3rem;
        width: 22rem;
        height: 22rem;
        border: 1px solid rgba(247, 244, 224, 0.17);
        border-radius: 50%;
        box-shadow: 0 0 0 2.5rem rgba(247, 244, 224, 0.035),
                    0 0 0 5rem rgba(247, 244, 224, 0.025);
        content: "";
        pointer-events: none;
    }
    .field-eyebrow {
        margin-bottom: 0.65rem;
        color: #d9e3ca;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
    }
    .field-hero h1 {
        position: relative;
        z-index: 1;
        margin: 0;
        color: #fffdf4;
        font-size: clamp(2rem, 4vw, 3.15rem);
        font-weight: 720;
        letter-spacing: -0.055em;
        line-height: 1.1;
    }
    .field-hero p {
        position: relative;
        z-index: 1;
        max-width: 42rem;
        margin: 0.85rem 0 0;
        color: #e3eadc;
        font-size: 1rem;
        line-height: 1.65;
    }
    h2, h3 { color: var(--field-ink); letter-spacing: -0.025em; }
    [data-testid="stTabs"] [role="tablist"] {
        gap: 0.45rem;
        padding: 0.45rem;
        border: 1px solid rgba(49, 91, 67, 0.08);
        border-radius: 1.1rem;
        background: #e9ece3;
        box-shadow: inset 2px 2px 5px rgba(55, 70, 53, 0.07),
                    inset -2px -2px 5px rgba(255, 255, 255, 0.7);
    }
    [data-testid="stTabs"] [role="tab"] {
        display: flex;
        align-items: center;
        min-height: 2.7rem;
        padding: 0.55rem 1rem;
        border-radius: 0.8rem;
        color: #617064 !important;
        font-weight: 650;
    }
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        background: #f8f8f1;
        box-shadow: 3px 3px 8px rgba(52, 70, 52, 0.11),
                    -2px -2px 6px rgba(255, 255, 255, 0.85);
        color: var(--field-green-dark) !important;
    }
    [data-testid="stMetric"] {
        min-height: 7.1rem;
        padding: 1.15rem 1.25rem;
        border: 1px solid rgba(255, 255, 255, 0.76);
        border-radius: 1.25rem;
        background: linear-gradient(145deg, #f7f7ef, #e9ece2);
        box-shadow: var(--clay-shadow);
    }
    [data-testid="stMetricLabel"] { color: var(--field-muted); }
    [data-testid="stMetricValue"] {
        color: var(--field-green-dark);
        font-weight: 750;
        letter-spacing: -0.04em;
    }
    [data-testid="stFileUploader"] section,
    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        border-radius: 1rem;
    }
    [data-testid="stFileUploader"] section {
        border: 1px dashed #aab9a4;
        background: rgba(235, 239, 228, 0.58);
    }
    [data-testid="stButton"] button,
    [data-testid="stDownloadButton"] button {
        min-height: 2.65rem;
        border: 1px solid #d8dfd3;
        border-radius: 0.85rem;
        background: linear-gradient(145deg, #f8f8f0, #e8ece2);
        box-shadow: 4px 4px 9px rgba(50, 67, 49, 0.09),
                    -3px -3px 7px rgba(255, 255, 255, 0.78);
        color: var(--field-green-dark);
        font-weight: 650;
        transition: transform 140ms ease, box-shadow 140ms ease;
    }
    [data-testid="stButton"] button:hover,
    [data-testid="stDownloadButton"] button:hover {
        transform: translateY(-1px);
        border-color: #9eb29c;
        color: var(--field-green-dark);
        box-shadow: 5px 6px 12px rgba(50, 67, 49, 0.12),
                    -3px -3px 7px rgba(255, 255, 255, 0.82);
    }
    [data-testid="stButton"] button[kind="primary"] {
        border-color: #315b43;
        background: linear-gradient(135deg, #3e704f, #2d563d);
        color: #fffdf4;
        box-shadow: 4px 5px 12px rgba(43, 82, 56, 0.22);
    }
    [data-testid="stButton"] button[kind="primary"]:hover {
        border-color: #294a37;
        color: #fffdf4;
    }
    [data-baseweb="select"] > div,
    [data-baseweb="input"] > div,
    [data-baseweb="textarea"] > div {
        border-radius: 0.8rem;
        background: #f8f8f1;
    }
    [data-testid="stAlert"] { border-radius: 0.9rem; }
    @media (max-width: 700px) {
        [data-testid="stMainBlockContainer"] {
            padding: 1rem 1rem 2rem;
        }
        .field-hero { border-radius: 1.25rem; }
        [data-testid="stTabs"] [role="tab"] {
            padding-right: 0.65rem;
            padding-left: 0.65rem;
            font-size: 0.82rem;
        }
    }
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after { scroll-behavior: auto !important; transition: none !important; }
    }
    </style>
    <div class="field-hero">
        <div class="field-eyebrow">Field intelligence · historical analysis</div>
        <h1>Crop Production<br>Analysis</h1>
        <p>Explore production, cultivated area, rainfall, and yield across crops, regions, and seasons.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown(
        """
        <div class="field-brand">
            <div class="field-brand-mark">✳</div>
            <div>
                <div class="field-brand-name">Fieldwork</div>
                <div class="field-brand-caption">Crop analysis workspace</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.subheader("Database")
    st.write("Configure MySQL in `.env` or environment variables.")
    if st.button("Initialize database"):
        try:
            init_db()
            st.success("Database tables are ready.")
        except Exception as exc:
            st.error(f"Database initialization failed: {exc}")

tab_upload, tab_dashboard, tab_data, tab_about = st.tabs(
    ["Upload data", "Dashboard & reports", "Data explorer", "About"]
)

with tab_upload:
    st.subheader("Upload a historical dataset")
    st.markdown(
        "Upload a CSV or Excel file. Required columns: **crop, region, year, cultivated_area, production**. "
        "`rainfall` is optional. Column names such as `Crop_Name`, `Area`, and `Yield` are not assumed; "
        "use the documented column names or rename them before upload."
    )
    uploaded = st.file_uploader("Choose CSV or Excel file", type=["csv", "xlsx", "xls"])
    if uploaded:
        try:
            raw = pd.read_csv(uploaded) if uploaded.name.lower().endswith(".csv") else pd.read_excel(uploaded)
            st.write("Preview", raw.head(10))
            normalized = normalize_columns(raw)
            checked, issues = validate_records(normalized)
            st.subheader("Validation summary")
            c1, c2, c3 = st.columns(3)
            c1.metric("Rows received", len(raw))
            c2.metric("Valid rows", int(checked["is_valid"].sum()))
            c3.metric("Rows needing review", int((~checked["is_valid"]).sum()))
            if not issues.empty:
                st.dataframe(issues, width="stretch")
                st.download_button(
                    "Download validation issues",
                    issues.to_csv(index=False).encode("utf-8"),
                    "validation_issues.csv",
                    "text/csv",
                )
            st.dataframe(checked, width="stretch")
            valid = checked[checked["is_valid"]].copy()
            if st.button("Save valid rows to MySQL", type="primary", disabled=valid.empty):
                try:
                    init_db()
                    inserted = save_records(valid)
                    st.success(f"Saved {inserted} valid records.")
                except Exception as exc:
                    st.error(f"Could not save records: {exc}")
            st.download_button(
                "Download normalized data",
                checked.drop(columns=["is_valid", "validation_notes"], errors="ignore").to_csv(index=False).encode("utf-8"),
                "normalized_crop_data.csv",
                "text/csv",
            )
        except Exception as exc:
            st.error(f"Could not read this file: {exc}")

with tab_dashboard:
    st.subheader("Historical dashboard")
    source = st.radio("Data source", ["MySQL database", "Upload a file for this session"], horizontal=True)
    df = pd.DataFrame()
    if source == "MySQL database":
        if st.button("Load database records"):
            st.session_state["db_loaded"] = True
        if st.session_state.get("db_loaded"):
            try:
                df = load_records()
            except Exception as exc:
                st.error(f"Could not load database records: {exc}")
    else:
        session_file = st.file_uploader("Choose a CSV or Excel file for analysis", type=["csv", "xlsx", "xls"], key="dashboard_upload")
        if session_file:
            try:
                raw = pd.read_csv(session_file) if session_file.name.lower().endswith(".csv") else pd.read_excel(session_file)
                clean, _ = validate_records(normalize_columns(raw))
                df = clean[clean["is_valid"]].drop(columns=["is_valid", "validation_notes"], errors="ignore")
            except Exception as exc:
                st.error(f"Could not analyze this file: {exc}")

    if not df.empty:
        df = calculate_yield(df)
        crops = sorted(df["crop"].dropna().unique().tolist())
        regions = sorted(df["region"].dropna().unique().tolist())
        years = sorted(df["year"].dropna().astype(int).unique().tolist())
        a, b, c = st.columns(3)
        selected_crops = a.multiselect("Crops", crops, default=crops)
        selected_regions = b.multiselect("Regions", regions, default=regions)
        selected_years = c.multiselect("Years", years, default=years)
        filtered = df[
            df["crop"].isin(selected_crops)
            & df["region"].isin(selected_regions)
            & df["year"].isin(selected_years)
        ].copy()

        if filtered.empty:
            st.warning("No records match the selected filters.")
        else:
            total_prod = filtered["production"].sum(min_count=1)
            total_area = filtered["cultivated_area"].sum(min_count=1)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Records", f"{len(filtered):,}")
            m2.metric("Total production", f"{total_prod:,.2f}" if pd.notna(total_prod) else "N/A")
            m3.metric("Cultivated area", f"{total_area:,.2f}" if pd.notna(total_area) else "N/A")
            valid_yield = filtered["yield"].dropna()
            m4.metric("Mean record yield", f"{valid_yield.mean():,.3f}" if not valid_yield.empty else "N/A")

            st.pyplot(production_trend(filtered), width="stretch")
            left, right = st.columns(2)
            with left:
                st.pyplot(yield_trend(filtered), width="stretch")
            with right:
                st.pyplot(region_comparison(filtered), width="stretch")

            st.subheader("Crop-wise and region-wise report")
            summary = build_summary(filtered)
            st.dataframe(summary, width="stretch")
            st.download_button("Download summary CSV", summary.to_csv(index=False).encode("utf-8"), "crop_region_summary.csv", "text/csv")

            st.subheader("Year comparison")
            comparison = yearly_comparison(filtered)
            st.dataframe(comparison, width="stretch")
            st.download_button("Download year comparison CSV", comparison.to_csv(index=False).encode("utf-8"), "year_comparison.csv", "text/csv")
    else:
        st.info("Load records from MySQL or upload a dataset to view the dashboard.")

with tab_data:
    st.subheader("Data explorer")
    try:
        if st.button("Refresh database table"):
            st.session_state["explorer_loaded"] = True
        if st.session_state.get("explorer_loaded"):
            records = load_records()
            if records.empty:
                st.info("The database has no records yet.")
            else:
                st.dataframe(records, width="stretch")
                st.download_button("Export database records", records.to_csv(index=False).encode("utf-8"), "crop_records.csv", "text/csv")
    except Exception as exc:
        st.info(f"Database is not available yet: {exc}")

with tab_about:
    st.subheader("Project scope")
    st.markdown("""
    - Describes historical production and yield patterns.
    - Yield is calculated as production divided by cultivated area only when area is positive and units are compatible.
    - Missing, zero, negative, and non-numeric values are flagged instead of silently repaired.
    - Rainfall is displayed as an optional historical field; correlation is not treated as causation.
    - Comparisons should use consistent production and area units and comparable time periods.
    """)
    st.code("crop,region,year,cultivated_area,production,rainfall\\nRice,Region A,2022,1200,3600,850")
