# 📊 JP Curation Tool

A **Streamlit-based web application** for Amazon product curation, pricing optimization, and restricted ASIN/brand filtering using IN and marketplace data.

---

## 🚀 Features

* ✅ INR price calculation (product + shipping)
* ✅ Advanced weight calculation (actual vs volumetric)
* ✅ Automated shipping & FBA fee estimation
* ✅ Final selling price optimization
* ✅ Competition percentage (`comp%`) analysis
* ✅ Restricted ASIN filtering
* ✅ Restricted brand filtering
* ✅ Supports JP marketplace (extendable to AU)

---

## 🧠 How It Works

1. Upload **IN (India) product data**
2. Upload **JP marketplace data**
3. Upload **Restricted file (Excel)**
4. Tool calculates:

   * Final weight
   * Shipping cost
   * Total cost
   * Suggested selling price
5. Filters out:

   * Restricted ASINs
   * Restricted brands

---

## 📂 Project Structure

```
.
├── app.py                # Streamlit UI
├── all_curation.py      # Core processing logic
├── requirements.txt     # Dependencies
├── README.md
```

---

## ⚙️ Installation

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the App

```bash
streamlit run app.py
```

---

## 📥 Input Requirements

### 1. IN File (CSV)

Must include:

* `asin`
* `lowest_new_price`
* `lowest_new_shipping`
* weight & dimension columns

---

### 2. JP File (CSV)

Must include:

* `asin`
* `title`
* `brand`
* `lowest_new_price`
* `lowest_new_shipping`
* `fba_pick_pack`

---

### 3. Restricted File (Excel)

Sheets required:

* `Notification Asin`
* `Res Asin`
* `RestrictedKeywords_IGSUS`

---

## 📤 Output

* Final curated dataset with:

  * `Our_Price`
  * `comp%`
  * `Shipping`
  * `FBA_Price`
  * Filtered ASINs & brands

---

## 🛠 Tech Stack

* Python 
* Pandas
* NumPy
* Streamlit

---

## 🔮 Future Improvements

* Add AU marketplace support
* Add UI filters (e.g., comp% > 120%)
* Performance optimization for large datasets
* Deploy to Streamlit Cloud

---

## 👨‍💻 Author

Developed by **Rohit Devaliya**


