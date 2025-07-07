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
st.title("Hisse Verileri Analizi")

# Google Sheets CSV linkleri
sheet1_url = convert_edit_url_to_csv("https://docs.google.com/spreadsheets/d/1u9WT-P9dEoXYuCOX1ojkFUySeJVmznc6dEFzhq0Ob8M/edit?usp=drivesdk")
sheet2_url = convert_edit_url_to_csv("https://docs.google.com/spreadsheets/d/1MnhlPTx6aD5a4xuqsVLRw3ktLmf-NwSpXtw_IteXIFs/edit?usp=drivesdk")

df1 = read_public_google_sheet(sheet1_url)
df2 = read_public_google_sheet(sheet2_url)

# "Ticker" varsa "Hisse Adı" olarak değiştir
if "Ticker" in df1.columns:
    df1 = df1.rename(columns={"Ticker": "Hisse Adı"})
if "Ticker" in df2.columns:
    df2 = df2.rename(columns={"Ticker": "Hisse Adı"})

# Birleştir
if "Hisse Adı" in df1.columns and "Hisse Adı" in df2.columns:
    df = pd.merge(df2, df1, on="Hisse Adı", how="outer")
else:
    st.error(f"'Hisse Adı' sütunu her iki tabloda da olmalı.\nSheet1: {list(df1.columns)}\nSheet2: {list(df2.columns)}")
    st.stop()

df = df.fillna("N/A")

st.sidebar.header("Filtreler")

# === Kolon seçimi ===
st.sidebar.subheader("Görünür Kolonlar")
all_columns = df.columns.tolist()
selected_columns = st.sidebar.multiselect("Kolonları seç", all_columns, default=all_columns)

# === Kategorik filtreler ===
for col in df.columns:
    if df[col].nunique() < 100 and df[col].dtype == 'object':
        options = df[col].dropna().unique().tolist()
        selected_options = st.sidebar.multiselect(f"{col}", options, default=options)
        df = df[df[col].isin(selected_options)]

# === Sayısal filtreler ===
#for col in df.select_dtypes(include='number').columns:
#    min_val = float(df[col].min())
#    max_val = float(df[col].max())
#    selected_range = st.sidebar.slider(
#        f"{col}", min_value=min_val, max_value=max_val,
#        value=(min_val, max_val), step=(max_val - min_val) / 100 if max_val != min_val else 1.0
#    )
#    df = df[df[col].between(*selected_range)]

for col in df.select_dtypes(include='number').columns:
    clean_series = df[col].dropna()

    if clean_series.empty:
        continue  # NaN doluysa geç

    min_val = float(clean_series.min())
    max_val = float(clean_series.max())

    # Eğer sadece tek bir değer varsa (örneğin 0) — filtreleme yapma
    if min_val == max_val:
        # İsteğe bağlı: slider yerine sabit bilgi göster
        st.sidebar.markdown(f"**{col}**: Sabit değer ({min_val}), filtrelenmedi.")
        continue

    # Slider koy ama sadece kullanıcı değeri değiştirirse filtre uygula
    selected_range = st.sidebar.slider(
        f"{col}",
        min_value=min_val,
        max_value=max_val,
        value=(min_val, max_val),
        step=(max_val - min_val) / 100
    )

    if selected_range != (min_val, max_val):
        df = df[df[col].between(*selected_range)]
        
# === Gösterim ===
st.subheader("Filtrelenmiş Veri Tablosu")
st.dataframe(df[selected_columns], use_container_width=True)

st.download_button("Excel olarak indir",
                   convert_df_to_excel(df[selected_columns]),
                   file_name="hisse_analizi_filtered.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
