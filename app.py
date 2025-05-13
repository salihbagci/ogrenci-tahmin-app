import streamlit as st
import pickle
import numpy as np
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt

# 🎯 Modeli yükle
model = pickle.load(open("model.pkl", "rb"))

# 📁 Veritabanı bağlantısı (dosya otomatik oluşur)
conn = sqlite3.connect("tahminler.db", check_same_thread=False)
c = conn.cursor()

# 🗃️ Tablo oluştur (eğer yoksa)
c.execute("""
CREATE TABLE IF NOT EXISTS tahminler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vize INTEGER,
    final INTEGER,
    yoklama REAL,
    proje INTEGER,
    tahmin INTEGER,
    olasilik REAL,
    tarih TEXT
)
""")
conn.commit()

# 🌐 Streamlit ayarları
st.set_page_config(page_title="Öğrenci Başarı Tahmini", layout="centered")
st.title("📘 Öğrenci Başarı Tahmin Sistemi")

# 📥 Giriş alanları
vize = st.slider("Vize Notu", 0, 100, 50)
final = st.slider("Final Notu", 0, 100, 50)
yoklama = st.slider("Yoklama Oranı (0-1)", 0.0, 1.0, 0.75)
proje = st.radio("Proje Teslim Durumu", ("Teslim Etmedi", "Teslim Etti"))
proje_teslim = 1 if proje == "Teslim Etti" else 0

# 🎯 Tahmin
if st.button("🎯 Tahmin Et"):
    girdi = np.array([[vize, final, yoklama, proje_teslim]])
    tahmin = model.predict(girdi)[0]
    olasiliklar = model.predict_proba(girdi)[0]
    olasilik = olasiliklar[tahmin]

    # ✅ Ekrana sonucu yaz
    if tahmin == 1:
        st.success(f"✅ Tahmin: Başarılı (%{olasilik*100:.1f} olasılıkla)")
    else:
        st.error(f"❌ Tahmin: Başarısız (%{olasilik*100:.1f} olasılıkla)")

    # 💾 Veritabanına kaydet
    tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
        INSERT INTO tahminler (vize, final, yoklama, proje, tahmin, olasilik, tarih)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (vize, final, yoklama, proje_teslim, int(tahmin), round(float(olasilik), 4), tarih))
    conn.commit()

    st.info("✅ Tahmin verisi veritabanına kaydedildi.")

    # 📊 Grafik
    st.markdown("### 🎨 Olasılık Dağılımı")
    fig, ax = plt.subplots()
    ax.bar(["Başarısız", "Başarılı"], olasiliklar, color=["red", "green"])
    ax.set_ylim(0, 1)
    ax.set_ylabel("Olasılık")
    ax.set_title("Model Tahmin Olasılıkları")
    st.pyplot(fig)
# 📚 Tahmin geçmişini göster
st.markdown("---")
st.markdown("## 📜 Tahmin Geçmişi")

if st.button("📂 Tahmin Geçmişini Göster"):
    c.execute("SELECT vize, final, yoklama, proje, tahmin, olasilik, tarih FROM tahminler ORDER BY id DESC")
    rows = c.fetchall()

    if len(rows) == 0:
        st.info("Henüz tahmin yapılmamış.")
    else:
        import pandas as pd

        df = pd.DataFrame(rows, columns=["Vize", "Final", "Yoklama", "Proje", "Tahmin", "Olasılık", "Tarih"])
        df["Proje"] = df["Proje"].map({1: "Teslim Etti", 0: "Teslim Etmedi"})
        df["Tahmin"] = df["Tahmin"].map({1: "Başarılı", 0: "Başarısız"})
        df["Olasılık"] = df["Olasılık"].apply(lambda x: f"%{x * 100:.1f}")

        st.dataframe(df, use_container_width=True)

