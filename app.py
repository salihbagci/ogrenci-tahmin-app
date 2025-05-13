import streamlit as st
import pickle
import numpy as np
import matplotlib.pyplot as plt

# 🎯 Modeli yükle
model = pickle.load(open("model.pkl", "rb"))

# Başlık ve açıklama
st.set_page_config(page_title="Öğrenci Başarı Tahmin Sistemi", layout="centered")
st.title("📘 Öğrenci Başarı Tahmin Sistemi")
st.markdown("Not ve yoklama bilgilerine göre öğrencinin başarı durumu tahmin edilir.")

# Giriş alanları
vize = st.slider("Vize Notu", 0, 100, 50)
final = st.slider("Final Notu", 0, 100, 50)
yoklama = st.slider("Yoklama Oranı (0-1)", 0.0, 1.0, 0.75)
proje = st.radio("Proje Teslim Durumu", ("Teslim Etmedi", "Teslim Etti"))
proje_teslim = 1 if proje == "Teslim Etti" else 0

# Tahmin
if st.button("🎯 Tahmin Et"):
    girdi = np.array([[vize, final, yoklama, proje_teslim]])
    tahmin = model.predict(girdi)[0]
    olasiliklar = model.predict_proba(girdi)[0]

    if tahmin == 1:
        st.success(f"✅ Tahmin: Başarılı (%{olasiliklar[1]*100:.1f} olasılıkla)")
    else:
        st.error(f"❌ Tahmin: Başarısız (%{olasiliklar[0]*100:.1f} olasılıkla)")

    # 📊 Grafik (bar chart)
    st.markdown("### 🎨 Olasılık Dağılımı")
    fig, ax = plt.subplots()
    ax.bar(["Başarısız", "Başarılı"], [olasiliklar[0], olasiliklar[1]], color=["red", "green"])
    ax.set_ylim(0, 1)
    ax.set_ylabel("Olasılık")
    ax.set_title("Model Tahmin Olasılıkları")
    st.pyplot(fig)
