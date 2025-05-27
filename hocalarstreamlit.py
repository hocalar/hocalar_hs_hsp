import streamlit as st
import pandas as pd
from io import BytesIO

# === Google Sheets edit linklerini CSV linke dönüştür ===
def convert_edit_url_to_csv(url):
    return url.split("/edit")[0] + "/export?format=csv"

# === Google Sheets'ten veri çek ===
def read_public_google_sheet(csv_url):
    return pd.read_csv(csv_url)

# === Excel çıktısı oluştur ===
def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# === Uygulama ayarları ===
st.set_page_config(layout="wide")
st.title("Hocalar Hisse Analizi")

# === Google Sheets bağlantıları ===
sheet1_url = convert_edit_url_to_csv("https://docs.google.com/spreadsheets/d/1MnhlPTx6aD5a4xuqsVLRw3ktLmf-NwSpXtw_IteXIFs/edit?usp=drivesdk")
sheet2_url = convert_edit_url_to_csv("https://docs.google.com/spreadsheets/d/1u9WT-P9dEoXYuCOX1ojkFUySeJVmznc6dEFzhq0Ob8M/edit?usp=drivesdk")

# === Verileri oku ===
df1 = read_public_google_sheet(sheet1_url)
df2 = read_public_google_sheet(sheet2_url)

# === Eksik sütunlar için doldurma ===
combined_columns = list(set(df1.columns) | set(df2.columns))
df1 = df1.reindex(columns=combined_columns, fill_value="N/A")
df2 = df2.reindex(columns=combined_columns, fill_value="N/A")

# === Tüm verileri birleştir ===
df = pd.concat([df2, df1], ignore_index=True)

# === Sidebar filtreler ===
st.sidebar.header("Filtreler")

# Hisse adı filtreleme
if "Hisse Adı" in df.columns:
    hisseler = df["Hisse Adı"].dropna().unique().tolist()
    secilen_hisseler = st.sidebar.multiselect("Hisse Adı", hisseler, default=hisseler)
    df = df[df["Hisse Adı"].isin(secilen_hisseler)]

# Sektör filtreleme
if "Sektör" in df.columns:
    sektorler = df["Sektör"].dropna().unique().tolist()
    secilen_sektorler = st.sidebar.multiselect("Sektör", sektorler, default=sektorler)
    df = df[df["Sektör"].isin(secilen_sektorler)]

# Sayısal filtreler (koşullu)
st.sidebar.subheader("Sayısal Filtreler")
numeric_columns = df.select_dtypes(include="number").columns.tolist()
numeric_filters = {}

for col in numeric_columns:
    filter_type = st.sidebar.selectbox(
        f"{col} için filtre tipi",
        ["Yok", ">", "<", "=", "Arasında"],
        key=col
    )

    if filter_type == ">":
        val = st.sidebar.number_input(f"{col} >")
        df = df[df[col] > val]
    elif filter_type == "<":
        val = st.sidebar.number_input(f"{col} <")
        df = df[df[col] < val]
    elif filter_type == "=":
        val = st.sidebar.number_input(f"{col} =")
        df = df[df[col] == val]
    elif filter_type == "Arasında":
        val_min = st.sidebar.number_input(f"{col} min")
        val_max = st.sidebar.number_input(f"{col} max")
        df = df[df[col].between(val_min, val_max)]

# === Sonuçları göster ===
st.subheader("Filtrelenmiş Veri Tablosu")
st.dataframe(df, use_container_width=True)

# === Excel çıktı butonu ===
st.download_button("Excel olarak indir",
                   convert_df_to_excel(df),
                   file_name="hisse_analizi_filtered.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
