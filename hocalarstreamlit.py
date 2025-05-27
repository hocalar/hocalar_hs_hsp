import streamlit as st
import pandas as pd
from io import BytesIO

# === Google Sheets edit linkini CSV linke dönüştür ===
def convert_edit_url_to_csv(url):
    return url.split("/edit")[0] + "/export?format=csv"

# === Google Sheets'ten veri çek (herkese açık paylaşımlı link) ===
def read_public_google_sheet(csv_url):
    df = pd.read_csv(csv_url)
    return df

# === Excel çıktı fonksiyonu ===
def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# === Sayfa ayarı ===
st.set_page_config(layout="wide")
st.title("Hocalar Hisse Analizi")

# === CSV linkleri ===
sheet1_url = convert_edit_url_to_csv("https://docs.google.com/spreadsheets/d/1MnhlPTx6aD5a4xuqsVLRw3ktLmf-NwSpXtw_IteXIFs/edit?usp=drivesdk")
sheet2_url = convert_edit_url_to_csv("https://docs.google.com/spreadsheets/d/1u9WT-P9dEoXYuCOX1ojkFUySeJVmznc6dEFzhq0Ob8M/edit?usp=drivesdk")

# === Verileri al ===
df1 = read_public_google_sheet(sheet1_url)
df2 = read_public_google_sheet(sheet2_url)

# === "Hisse Adı" ortak sütun ise merge yap
if "Hisse Adı" in df1.columns and "Hisse Adı" in df2.columns:
    df = pd.merge(df2, df1, on="Hisse Adı", how="outer")
else:
    st.error("Her iki tabloda da 'Hisse Adı' sütunu bulunmalıdır.")
    st.stop()

# === Eksik hücreleri 'N/A' ile doldur
df.fillna("N/A", inplace=True)

# === Sidebar filtreleme ===
st.sidebar.header("Filtreler")

# Hisse ve sektör seçimi
hisseler = df["Hisse Adı"].dropna().unique().tolist()
secilen_hisseler = st.sidebar.multiselect("Hisse Adı", options=hisseler, default=hisseler)

sektorler = df["Sektör"].dropna().unique().tolist() if "Sektör" in df.columns else []
secilen_sektorler = st.sidebar.multiselect("Sektör", options=sektorler, default=sektorler)

# Sayısal kolonlar için karşılaştırmalı filtre
numeric_cols = df.select_dtypes(include='number').columns.tolist()
filter_logic = {}

st.sidebar.markdown("### Sayısal Filtreler")
for col in numeric_cols:
    operator = st.sidebar.selectbox(f"{col} için karşılaştırma", options=["Yok", "=", ">", "<", "Arasında"], key=col)
    if operator == "=":
        val = st.sidebar.number_input(f"{col} =", key=f"{col}_eq")
        filter_logic[col] = lambda x, val=val: x == val
    elif operator == ">":
        val = st.sidebar.number_input(f"{col} >", key=f"{col}_gt")
        filter_logic[col] = lambda x, val=val: x > val
    elif operator == "<":
        val = st.sidebar.number_input(f"{col} <", key=f"{col}_lt")
        filter_logic[col] = lambda x, val=val: x < val
    elif operator == "Arasında":
        val_min = st.sidebar.number_input(f"{col} Min", key=f"{col}_min")
        val_max = st.sidebar.number_input(f"{col} Max", key=f"{col}_max")
        filter_logic[col] = lambda x, val_min=val_min, val_max=val_max: val_min <= x <= val_max

# === Filtre uygulama ===
filtered_df = df[df["Hisse Adı"].isin(secilen_hisseler)]
if secilen_sektorler:
    filtered_df = filtered_df[filtered_df["Sektör"].isin(secilen_sektorler)]

# Sayısal filtreleri uygula
for col, logic in filter_logic.items():
    filtered_df = filtered_df[filtered_df[col].apply(lambda x: logic(x) if x != "N/A" else False)]

# === Gösterim ===
st.subheader("Filtrelenmiş Veri Tablosu")
st.dataframe(filtered_df, use_container_width=True)

st.download_button("Excel olarak indir",
                   convert_df_to_excel(filtered_df),
                   file_name="hisse_analizi_filtered.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# === Sonuçları göster ===
st.subheader("Filtrelenmiş Veri Tablosu")
st.dataframe(df, use_container_width=True)

# === Excel çıktı butonu ===
st.download_button("Excel olarak indir",
                   convert_df_to_excel(df),
                   file_name="hisse_analizi_filtered.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
