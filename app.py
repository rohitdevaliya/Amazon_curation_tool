import streamlit as st
import pandas as pd
from All_Curation import process_data1

st.title("📊 JP Curation Tool")

# Upload main files
in_file = st.file_uploader("Upload IN file", type=["csv"])
jp_file = st.file_uploader("Upload JP file", type=["csv"])

# ✅ Add restricted file upload
restricted_file = st.file_uploader("Upload Restricted File", type=["xlsx"])

if in_file and jp_file and restricted_file:

    IN_data = pd.read_csv(in_file, encoding='latin1')
    JP_data = pd.read_csv(jp_file, encoding='latin1')

    if st.button("🚀 Run Processing"):

        # ✅ Pass restricted file also
        result = process_data1(IN_data, JP_data, restricted_file)

        st.dataframe(result)

        st.download_button(
            "Download Output",
            result.to_csv(index=False),
            "output.csv"
        )