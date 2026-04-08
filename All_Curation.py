import pandas as pd
import numpy as np
import requests


def process_data1(IN_data, Market_Place_Data, market):

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
    Market_Place_Data["FBA FEE"] = Market_Place_Data["fba_pick_pack"]

    Market_Place_Data["lowest_new_price"] = pd.to_numeric(
        Market_Place_Data["lowest_new_price"].astype(str).str.replace(",", ""),
        errors="coerce"
    )

    Market_Place_Data["lowest_new_shipping"] = pd.to_numeric(
        Market_Place_Data["lowest_new_shipping"].astype(str).str.replace(",", ""),
        errors="coerce"
    )

    Market_Place_Data["Price"] = Market_Place_Data["lowest_new_price"] + Market_Place_Data["lowest_new_shipping"]

    new_Market_Place_Data = Market_Place_Data[["asin","title","brand","FBA FEE","Price"]]

    # ---------------- MERGE ----------------
    All_data = new_Market_Place_Data.merge(New_IN_data, on="asin", how="left")

    def get_rate(from_currency, to_currency="INR"):
        url = f"https://open.er-api.com/v6/latest/{from_currency}"
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            return None

        data = response.json()
        return data.get("rates", {}).get(to_currency, None)

        
        return None
    


    # ---------------- MARKET LOGIC ----------------
    if market == "JP":
        rate = get_rate("JPY","INR")
        shipping_rate = 0.568
        margin = 0.61
        final_margin = 0.57


    elif market == "AU":
        rate = get_rate("AUD","INR")
        shipping_rate = 0.478
        margin = 0.53
        final_margin = 62.72

    elif market == "CA":
        rate = get_rate("CAD","INR")
        shipping_rate = 0.745
        margin = 0.60
        final_margin = 65.19

    elif market == "SG":
        rate = get_rate("SGD","INR")
        shipping_rate = 0.314
        margin = 0.56
        final_margin = 70.62

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

    All_data["Our_Price"] = (All_data["Total_INR"] / final_margin).round(2)

    All_data = All_data[All_data["INR_Price"] != 0]

    # ---------------- COMP % ----------------
    comp = (All_data["Our_Price"] / All_data["Price"]) * 100
    comp = comp.replace([np.inf, -np.inf], np.nan)

    All_data["comp%"] = comp.round().fillna(0).astype(int).astype(str) + "%"

    All_data["Min_Value"] = All_data["Our_Price"] - 0.95
    All_data["Max_Value"] = All_data["Our_Price"] + 1.20

    #----------------Restricted asin 1-------------------------
    
    Restricted_asin1 = "https://docs.google.com/spreadsheets/d/1dTNmewiO4Lz1Ook2r7VaydaLFZ-T1P4QA4Dbv7nwG1Y/export?format=csv&gid=2146593195"
    restricted_data1 = pd.read_csv(Restricted_asin1)
    restricted_data1.columns = restricted_data1.columns.str.strip().str.lower()
    restricted_data1.rename(columns={"Asin":"asin"}, inplace=True)

    restricted_set1 = set(
            restricted_data1["asin"].dropna().str.lower()
        )
    

    restricted_asin_file = All_data.copy()
    restricted_asin_file = restricted_asin_file[restricted_asin_file["asin"].str.lower().str.strip().isin(restricted_set1)]

    All_data = All_data[~All_data["asin"].fillna("").str.lower().isin(restricted_set1)]




    #--------------------Restricted asin 2 --------------------
    Restricted_asin2 = "https://docs.google.com/spreadsheets/d/1dTNmewiO4Lz1Ook2r7VaydaLFZ-T1P4QA4Dbv7nwG1Y/export?format=csv&gid=91590025"
    restricted_data2 = pd.read_csv(Restricted_asin2)
    restricted_data2.columns = restricted_data2.columns.str.strip().str.lower()
    restricted_data2.rename(columns={"Asin": "asin"}, inplace=True)

    restricted_set2 = set(
            restricted_data2["asin"].dropna().str.lower()
        )
    

    restricted_asin_file2 = All_data.copy()
    restricted_asin_file2 = restricted_asin_file2[restricted_asin_file2["asin"].str.lower().str.strip().isin(restricted_set2)]

    All_data = All_data[~All_data["asin"].fillna("").str.lower().isin(restricted_set2)]

    All_restricted_asin = pd.concat([restricted_asin_file,restricted_asin_file2])


    # -------- Restricted Brand --------
    Restricted_brand = "https://docs.google.com/spreadsheets/d/1dTNmewiO4Lz1Ook2r7VaydaLFZ-T1P4QA4Dbv7nwG1Y/export?format=csv&gid=516675691"
    Restricted_data3 = pd.read_csv(Restricted_brand)
    Restricted_data3.columns = Restricted_data3.columns.str.strip().str.lower()
    Restricted_data3.rename(columns = {"keyword": "brand"},inplace = True)
    Restricted_brand_set = set(
            Restricted_data3["brand"].dropna().str.lower()
        )
    Restricted_brand_File = All_data.copy()
    Restricted_brand_File = Restricted_brand_File[Restricted_brand_File["brand"].fillna("").str.lower().isin(Restricted_brand_set)]

    All_data = All_data[
            ~All_data["brand"].fillna("").str.lower().isin(Restricted_brand_set)
        ]    
   

        
    All_data["asin"] = All_data["asin"].str.upper()

    return All_data,All_restricted_asin,Restricted_brand_File