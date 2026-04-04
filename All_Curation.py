import pandas as pd
import numpy as np


def process_data1(IN_data, JP_data, restricted_file):

    # ---------------- IN DATA ----------------
    IN_data["lowest_new_price"] = pd.to_numeric(
        IN_data["lowest_new_price"].astype(str).str.replace(",", ""),
        errors="coerce"
    )

    IN_data["lowest_new_shipping"] = pd.to_numeric(
        IN_data["lowest_new_shipping"].astype(str).str.replace(",", ""),
        errors="coerce"
    )

    IN_data["INR_Price"] = IN_data["lowest_new_price"] + IN_data["lowest_new_shipping"]

    # Weight calculations
    IN_data["Gram3"] = IN_data["item_dimensions_weight"] * 453.6
    IN_data["Gram2"] = IN_data["package_dimensions_weight"] * 453.6

    IN_data["CM1"] = IN_data["package_dimensions_height"] * 2.54
    IN_data["CM2"] = IN_data["package_dimensions_length"] * 2.54
    IN_data["CM3"] = IN_data["package_dimensions_width"] * 2.54

    IN_data["Cubic CM"] = IN_data["CM1"] * IN_data["CM2"] * IN_data["CM3"]

    IN_data["Volumetric_Weight_(KG)"] = IN_data["Cubic CM"] / 5000
    IN_data["Gram1"] = IN_data["Volumetric_Weight_(KG)"] * 1000

    IN_data["Max"] = np.ceil(IN_data[["Gram1","Gram2","Gram3"]].max(axis=1))

    IN_data["Median"] = np.ceil(np.where(
        IN_data["Max"] > 10000,
        IN_data[["Gram1","Gram2","Gram3"]].median(axis=1),
        IN_data["Max"]
    ))

    IN_data["Similarity"] = np.where(
        (IN_data["Max"] == 0),
        0,
        IN_data["Median"] / IN_data["Max"]
    )

    IN_data["Final_Weight"] = np.where(
        IN_data["Similarity"] >= 0.90,
        IN_data["Median"],
        IN_data["Max"]
    )

    New_IN_data = IN_data[["asin","INR_Price","Final_Weight"]].copy()

    # Weight adjustment
    New_IN_data["Final_Weight"] = np.where(
        (New_IN_data["Final_Weight"] >= 1) & (New_IN_data["Final_Weight"] <= 300),
        New_IN_data["Final_Weight"] + 50,
        np.where(
            (New_IN_data["Final_Weight"] <= 1000),
            New_IN_data["Final_Weight"] + 100,
            np.where(
                (New_IN_data["Final_Weight"] < 2000),
                New_IN_data["Final_Weight"] + 150,
                New_IN_data["Final_Weight"]
            )
        )
    )

    # ---------------- MARKET DATA ----------------
    JP_data["FBA FEE"] = JP_data["fba_pick_pack"]

    JP_data["lowest_new_price"] = pd.to_numeric(
        JP_data["lowest_new_price"].astype(str).str.replace(",", ""),
        errors="coerce"
    )

    JP_data["lowest_new_shipping"] = pd.to_numeric(
        JP_data["lowest_new_shipping"].astype(str).str.replace(",", ""),
        errors="coerce"
    )

    JP_data["JP_Price"] = JP_data["lowest_new_price"] + JP_data["lowest_new_shipping"]

    new_JP_data = JP_data[["asin","title","brand","FBA FEE","JP_Price"]]

    # ---------------- MERGE ----------------
    All_data = new_JP_data.merge(New_IN_data, on="asin", how="left")

    file_name = "AU"   # safer

    # ---------------- MARKET LOGIC ----------------
    if "JP" in file_name:
        rate = 0.59
        shipping_rate = 0.568
        margin = 0.61
        final_margin = 0.57

    elif "AU" in file_name:
        rate = 64.23
        shipping_rate = 0.478
        margin = 0.53
        final_margin = 62.72

    else:
        raise ValueError("Unknown marketplace file")

    All_data["FBA_Price"] = (
        pd.to_numeric(All_data["FBA FEE"], errors="coerce") * rate
    ).round()

    All_data = All_data.dropna(subset=["INR_Price","Final_Weight"])

    All_data["Shipping"] = (All_data["Final_Weight"] * shipping_rate).round()

    All_data["Total_INR"] = (
        (All_data["Shipping"] + All_data["FBA_Price"] + All_data["INR_Price"] + 20)
        / margin
    ).round()

    All_data["Our_Price"] = (All_data["Total_INR"] / final_margin).round()

    All_data = All_data[All_data["INR_Price"] != 0]

    # ---------------- COMP % ----------------
    comp = (All_data["Our_Price"] / All_data["JP_Price"]) * 100
    comp = comp.replace([np.inf, -np.inf], np.nan)

    All_data["comp%"] = comp.round().fillna(0).astype(int).astype(str) + "%"

    All_data["Min_Value"] = All_data["Our_Price"] - 0.95
    All_data["Max_Value"] = All_data["Our_Price"] + 1.20

    # ---------------- RESTRICTED ----------------
    excel_file = pd.ExcelFile(restricted_file)

    sheets = ["Notification Asin", "Res Asin"]
    available_sheets = excel_file.sheet_names

    valid_sheets = [s for s in sheets if s in available_sheets]

    restricted_data = pd.read_excel(excel_file, sheet_name=valid_sheets)

    restricted_set = set()

    for df in restricted_data.values():
        df.columns = df.columns.str.strip().str.lower()
        asin_col = [c for c in df.columns if "asin" in c]
        if asin_col:
            restricted_set.update(df[asin_col[0]].dropna())

    All_data.columns = All_data.columns.str.lower()
    All_data = All_data[~All_data["asin"].isin(restricted_set)]

    # -------- Restricted Brand --------
    if "RestrictedKeywords_IGSUS" in available_sheets:

        Restricted_brand = pd.read_excel(
            excel_file, sheet_name="RestrictedKeywords_IGSUS"
        )

        Restricted_brand.columns = Restricted_brand.columns.str.lower()
        Restricted_brand.rename(columns={"keyword": "brand"}, inplace=True)

        Restricted_brand_set = set(
            Restricted_brand["brand"].dropna().str.lower()
        )

        All_data = All_data[
            ~All_data["brand"].str.lower().isin(Restricted_brand_set)
        ]

    return All_data