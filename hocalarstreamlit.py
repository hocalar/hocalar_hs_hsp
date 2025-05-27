import streamlit as st
import pandas as pd
from io import BytesIO

def convert_edit_url_to_csv(url):
    return url.split("/edit")[0] + "/export?format=csv"

def read_public_google_sheet(csv_url, selected_columns):
    try:
        df = pd.read_csv(csv_url)
    except Exception as e:
        st.error(f"Veri alınamadı: {e}")
        return pd.DataFrame(columns=selected_columns)

    for col in selected_columns:
        if col not in df.columns:
            df[col] = "N/A"
    return df[selected_columns]

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

# === Kolonlar ===
sheet1_cols = [
    "ATH Değişimi TL (%)", "Geçen Gün", "AVWAP", "AVWAP +4σ", "% Fark VWAP",
    "POC", "VAL", "VAH", "% Fark POC", "% Fark VAL", "VP Bant / ATH Aralığı (%)"
]

sheet2_cols = [
    "Hisse Adı", "Sektör", "Period", "Ortalama Hedef Fiyat", "OHD - USD",
    "Hisse Potansiyeli (Yüzde)", "Hisse Puanı", "YDF Oranı", "Özkaynak Karlılığı",
    "Yıllık Net Kar", "Borç Özkaynak Oranı", "Ödenmiş Sermaye", "Bölünme",
    "Piyasa Değeri", "Peg Rasyosu", "FD/FAVÖK", "ROIC Oranı", "PD/FCF", "Cari Oran",
    "Net Borç/Favök", "F/K Oranı", "PD/DD Oranı", "Hisse Fiyatı"
]

# === Verileri oku ===
df1 = read_public_google_sheet(sheet1_url, sheet1_cols)
df2 = read_public_google_sheet(sheet2_url, sheet2_cols)

# === Hisse adlarına göre hizalanan birleşik tablo ===
df = pd.concat([df2.reset_index(drop=True), df1.reset_index(drop=True)], axis=1)

# === Gösterim ===
st.subheader("Tüm Hisseler")
st.dataframe(df, use_container_width=True)

# === Excel indirme ===
st.download_button("Excel olarak indir",
                   convert_df_to_excel(df),
                   file_name="hisse_analizi_tam.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# === Gösterim ===
st.subheader("Filtrelenmiş Veri Tablosu")
st.dataframe(filtered_df, use_container_width=True)

# === Excel indirme ===
st.download_button("Excel olarak indir",
                   convert_df_to_excel(filtered_df),
                   file_name="hisse_analizi_filtered.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
