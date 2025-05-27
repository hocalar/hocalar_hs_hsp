import streamlit as st
import pandas as pd
from io import BytesIO

def convert_edit_url_to_csv(url):
    return url.split("/edit")[0] + "/export?format=csv"

def read_public_google_sheet(csv_url):
    try:
        df = pd.read_csv(csv_url)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Veri alınamadı: {e}")
        return pd.DataFrame()

def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

st.set_page_config(layout="wide")
st.title("Hocalar Hisse Analizi")

# Google Sheets CSV linkleri
sheet1_url = convert_edit_url_to_csv("https://docs.google.com/spreadsheets/d/1u9WT-P9dEoXYuCOX1ojkFUySeJVmznc6dEFzhq0Ob8M/edit?usp=drivesdk")
sheet2_url = convert_edit_url_to_csv("https://docs.google.com/spreadsheets/d/1MnhlPTx6aD5a4xuqsVLRw3ktLmf-NwSpXtw_IteXIFs/edit?usp=drivesdk")

# Verileri oku
df1 = read_public_google_sheet(sheet1_url)
df2 = read_public_google_sheet(sheet2_url)

# Hisse adı sütun adlarını normalize et
if "Ticker" in df1.columns:
    df1 = df1.rename(columns={"Ticker": "Hisse Adı"})
if "Ticker" in df2.columns:
    df2 = df2.rename(columns={"Ticker": "Hisse Adı"})

# Eğer her iki tabloda da "Hisse Adı" varsa birleştir
if "Hisse Adı" in df1.columns and "Hisse Adı" in df2.columns:
    df = pd.merge(df2, df1, on="Hisse Adı", how="outer")
else:
    st.error(f"'Hisse Adı' sütunu her iki tabloda da olmalı. Mevcut sütunlar:\n"
             f"Sheet1: {list(df1.columns)}\n"
             f"Sheet2: {list(df2.columns)}")
    st.stop()

df = df.fillna("N/A")

# Sidebar filtreleme
st.sidebar.header("Filtreler")

# Hisse filtresi
hisseler = df["Hisse Adı"].dropna().unique().tolist()
secilen_hisseler = st.sidebar.multiselect("Hisse Adı", options=hisseler, default=hisseler)

# Sektör filtresi (varsa)
if "Sektör" in df.columns:
    sektorler = df["Sektör"].dropna().unique().tolist()
    secilen_sektorler = st.sidebar.multiselect("Sektör", options=sektorler, default=sektorler)
else:
    secilen_sektorler = []

# Sayısal kolon filtreleri
numeric_cols = df.select_dtypes(include='number').columns.tolist()
numeric_filters = {}

for col in numeric_cols:
    min_val = float(df[col].min())
    max_val = float(df[col].max())
    selected_range = st.sidebar.slider(
        label=col,
        min_value=min_val,
        max_value=max_val,
        value=(min_val, max_val),
        step=(max_val - min_val) / 100 if max_val != min_val else 1.0
    )
    numeric_filters[col] = selected_range

# Filtreleme
filtered_df = df[df["Hisse Adı"].isin(secilen_hisseler)]
if secilen_sektorler and "Sektör" in df.columns:
    filtered_df = filtered_df[filtered_df["Sektör"].isin(secilen_sektorler)]

for col, (min_val, max_val) in numeric_filters.items():
    filtered_df = filtered_df[
        pd.to_numeric(filtered_df[col], errors="coerce").between(min_val, max_val)
    ]

# Gösterim
st.subheader("Filtrelenmiş Veri Tablosu")
st.dataframe(filtered_df, use_container_width=True)

st.download_button("Excel olarak indir",
                   convert_df_to_excel(filtered_df),
                   file_name="hisse_analizi_filtered.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
