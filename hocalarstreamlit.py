import streamlit as st
import pandas as pd
from io import BytesIO

# === Google Sheets edit linkini CSV linke dönüştür ===
def convert_edit_url_to_csv(url):
    return url.split("/edit")[0] + "/export?format=csv"

# === Google Sheets'ten veri çek (herkese açık paylaşılmış link) ===
def read_public_google_sheet(csv_url, selected_columns):
    df = pd.read_csv(csv_url)
    existing_columns = [col for col in selected_columns if col in df.columns]
    missing = set(selected_columns) - set(existing_columns)
    if missing:
        st.warning(f"Google Sheet'te eksik sütunlar: {missing}")
    return df[existing_columns]

# === Excel'e dönüştürme fonksiyonu ===
def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# === Sayfa başlığı ve ayar ===
st.set_page_config(layout="wide")
st.title("Hocalar Hisse Analizi")

# === Google Sheets linkleri ===
sheet1_url = convert_edit_url_to_csv("https://docs.google.com/spreadsheets/d/1MnhlPTx6aD5a4xuqsVLRw3ktLmf-NwSpXtw_IteXIFs/edit?usp=drivesdk")
sheet2_url = convert_edit_url_to_csv("https://docs.google.com/spreadsheets/d/1u9WT-P9dEoXYuCOX1ojkFUySeJVmznc6dEFzhq0Ob8M/edit?usp=drivesdk")

# === Kolon seçimleri ===
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

# === Veri çekme ve birleştirme ===
df1 = read_public_google_sheet(sheet1_url, sheet1_cols)
df2 = read_public_google_sheet(sheet2_url, sheet2_cols)
df = pd.concat([df2, df1], axis=1)

# === Veri tablosu gösterimi ===
st.subheader("Veri Tablosu")
st.dataframe(df, use_container_width=True)

# === Excel olarak indir ===
st.download_button("Excel olarak indir",
                   convert_df_to_excel(df),
                   file_name="hisse_analizi.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
