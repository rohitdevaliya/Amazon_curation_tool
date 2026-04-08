import streamlit as st
import pandas as pd
from All_Curation import process_data1

st.set_page_config(page_title="Amazon Curation Tool", layout="wide")

st.title("📊 Amazon Curation Tool")

# ---------------- Sidebar ----------------
st.sidebar.header("⚙️ Settings")

market = st.sidebar.selectbox("🌍 Select Marketplace", ["JP", "AU", "CA", "SG"])
run_btn = st.sidebar.button("🚀 Run Processing")

# ---------------- File Upload (2 columns) ----------------
col1, col2 = st.columns(2)

with col1:
    in_file = st.file_uploader("📂 Upload IN File", type=["csv", "xlsx"])

with col2:
    market_place = st.file_uploader("🌍 Upload Market File", type=["csv", "xlsx"])


# ---------------- File Reader ----------------
def read_file(file):
    if file is not None:
        if file.name.endswith(".csv"):
            return pd.read_csv(file, encoding="latin1")
        elif file.name.endswith(".xlsx"):
            return pd.read_excel(file)
    return None


# ---------------- Session State ----------------
if "result" not in st.session_state:
    st.session_state.result = None
    st.session_state.restricted_asin_df = None
    st.session_state.restricted_brand_df = None


# ---------------- Processing ----------------
if run_btn:
    if in_file and market_place:
        IN_data = read_file(in_file)
        Market_Place_Data = read_file(market_place)

        with st.spinner("⏳ Processing data..."):
            result, restricted_asin_df, restricted_brand_df = process_data1(
                IN_data,
                Market_Place_Data,
                market
            )

            # Save in session (prevents disappearing UI)
            st.session_state.result = result
            st.session_state.restricted_asin_df = restricted_asin_df
            st.session_state.restricted_brand_df = restricted_brand_df
    else:
        st.warning("⚠️ Please upload both files before processing.")


# ---------------- Display Results ----------------
if st.session_state.result is not None:

    result = st.session_state.result
    restricted_asin_df = st.session_state.restricted_asin_df
    restricted_brand_df = st.session_state.restricted_brand_df

    # -------- Metrics --------
    col1, col2, col3 = st.columns(3)
    col1.metric("✅ Total Products", len(result))
    col2.metric("🚫 Restricted ASIN", len(restricted_asin_df))
    col3.metric("🏷️ Restricted Brands", len(restricted_brand_df))

    # -------- Search --------
    search = st.text_input("🔍 Search ASIN")
    if search:
        result = result[result["asin"].str.contains(search, case=False, na=False)]

    # -------- Tabs --------
    tab1, tab2, tab3 = st.tabs([
        "✅ Final Output",
        "🚫 Restricted ASIN",
        "🏷️ Restricted Brand"
    ])

    with tab1:
        st.dataframe(result, use_container_width=True)
        st.download_button(
            "⬇️ Download Output",
            result.to_csv(index=False),
            "output.csv"
        )

    with tab2:
        st.dataframe(restricted_asin_df, use_container_width=True)
        st.download_button(
            "⬇️ Download Restricted ASIN",
            restricted_asin_df.to_csv(index=False),
            "restricted_asin.csv"
        )

    with tab3:
        st.dataframe(restricted_brand_df, use_container_width=True)
        st.download_button(
            "⬇️ Download Restricted Brand",
            restricted_brand_df.to_csv(index=False),
            "restricted_brand.csv"
        )