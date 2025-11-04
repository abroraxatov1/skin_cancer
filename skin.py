#!/usr/bin/env python3
# =======================================================
# Skin Cancer AI Detector – Streamlit 1.50.0+ (Sodda & Chiroyli)
# =======================================================

import streamlit as st
from inference_sdk import InferenceHTTPClient
from PIL import Image, ImageDraw
from datetime import datetime
import os

# === KONFIGURATSIYA ===
API_URL = "https://detect.roboflow.com"
API_KEY = "Kz1uRQNYQfiMGbhGigCh"  # Roboflow API kaliti
MODEL_ID = "classification-igqvf/1"
OUTPUT_DIR = "results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CLIENT = InferenceHTTPClient(api_url=API_URL, api_key=API_KEY)

# === Sahifa sozlamalari ===
st.set_page_config(
    page_title="Skin Cancer AI",
    page_icon="brain",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# === CSS – Sodda va chiroyli dizayn ===
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #8EC5FC, #E0C3FC);
        padding: 2rem;
        min-height: 100vh;
    }
    .header {
        text-align: center;
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .nav {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin-bottom: 2rem;
        flex-wrap: wrap;
    }
    .nav-button {
        background: rgba(255,255,255,0.25);
        color: white;
        border: none;
        padding: 0.7rem 1.5rem;
        border-radius: 12px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s;
        backdrop-filter: blur(8px);
    }
    .nav-button:hover {
        background: #4b6cb7;
        transform: translateY(-2px);
    }
    .card {
        background: rgba(255,255,255,0.3);
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        transition: transform 0.3s;
    }
    .card:hover {
        transform: translateY(-5px);
    }
    .result-img {
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        margin: 1rem 0;
    }
    .history-item {
        background: rgba(255,255,255,0.2);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        text-align: center;
    }
    .stButton > button {
        background: #4b6cb7 !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: bold !important;
    }
    .footer {
        text-align: center;
        color: white;
        margin-top: 3rem;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# === Session state ===
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# === Navbar ===
def show_nav():
    st.markdown("<div class='header'>Skin Cancer AI Detector</div>", unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("Bosh sahifa", key="nav_home"):
            st.session_state.page = 'home'
    with col2:
        if st.button("AI Tekshiruv", key="nav_ai"):
            st.session_state.page = 'ai'
    with col3:
        if st.button("Tarix", key="nav_history"):
            st.session_state.page = 'history'
    with col4:
        if st.button("Aloqa", key="nav_contact"):
            st.session_state.page = 'contact'
    with col5:
        if st.button("Chiqish", key="nav_logout"):
            st.session_state.page = 'home'
    st.markdown("---")

# === Bosh sahifa ===
def home_page():
    st.markdown("<h2 style='text-align:center;color:white;'>Teri saratoni haqida</h2>", unsafe_allow_html=True)
    st.markdown("""
    <p style='text-align:center;color:white;font-size:1.1rem;max-width:800px;margin:auto;'>
    Teri saratoni erta aniqlansa, davolanish imkoniyati 95% dan yuqori. AI yordamida shubhali dog‘larni tezkor tahlil qiling.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("### Asosiy turlari")
    cols = st.columns(4)
    cards = [
        ("Melanoma", "Eng xavfli turi. Rangi o‘zgaruvchi dog‘lar.", "https://img.lb.wbmdstatic.com/vim/live/webmd/consumer_assets/site_images/article_thumbnails/reference_guide/malignant_melanoma_ref_guide/1800x1200_malignant_melanoma_ref_guide.jpg"),
        ("BCC", "Eng ko‘p uchraydigan, oqish dog‘lar.", "https://mismosavama.net/wp-content/uploads/2022/05/bazalni-1.webp"),
        ("SCC", "Qizil shishlar, quyosh ta’sirida.", "https://citydermatologyclinic.com/wp-content/uploads/2025/09/Squamous-Cell-Carcinoma-1024x1024.jpg"),
        ("Nevus", "Xavfsiz dog‘, lekin kuzatish kerak.", "https://ballaratskincancer.com.au/wp-content/uploads/2020/04/Ballarat-Skin-Cancer-Centre-naevus-1.jpg")
    ]
    for col, (title, desc, img) in zip(cols, cards):
        with col:
            st.markdown(f"<div class='card'>", unsafe_allow_html=True)
            st.image(img, use_column_width=True)
            st.markdown(f"**{title}**")
            st.markdown(f"<small>{desc}</small>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### AI qanday ishlaydi?")
    st.info("""
    1. **Rasm yuklang**  
    2. **AI 1000+ namunani solishtiradi**  
    3. **Natija: Tur + Ishonchlilik %**  
    """)

    if st.button("AI Tekshiruvni Boshlash", type="primary"):
        st.session_state.page = 'ai'

# === AI Tekshiruv ===
def ai_page():
    st.markdown("<h2 style='text-align:center;color:white;'>Rasmni yuklang</h2>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

    if uploaded_file and st.button("Tahlil qilish", type="primary"):
        with st.spinner("AI tahlil qilmoqda..."):
            try:
                # Saqlash
                img_path = os.path.join(OUTPUT_DIR, uploaded_file.name)
                with open(img_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # AI tahlil
                result = CLIENT.infer(img_path, model_id=MODEL_ID)
                preds = result.get("predictions", {})

                if not preds:
                    label, conf = "Aniqlanmadi", 0
                else:
                    label, info = max(preds.items(), key=lambda x: x[1]["confidence"])
                    conf = info["confidence"] * 100

                # Natija rasmini yaratish
                img = Image.open(img_path)
                draw = ImageDraw.Draw(img)
                draw.text((15, 15), f"{label} ({conf:.1f}%)", fill="red", stroke_width=2, stroke_fill="black")

                result_name = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                result_path = os.path.join(OUTPUT_DIR, result_name)
                img.save(result_path)

                # Tarixga saqlash
                with open(os.path.join(OUTPUT_DIR, "history.txt"), "a", encoding="utf-8") as f:
                    f.write(f"{result_path}|{label}|{conf:.1f}|{datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

                # Natija ko‘rsatish
                st.success(f"**{label}** – {conf:.1f}% ishonch bilan")
                st.image(result_path, caption="Natija", width=350, cls="result-img")

            except Exception as e:
                st.error(f"Xatolik: {str(e)}")

# === Tarix ===
def history_page():
    st.markdown("<h2 style='text-align:center;color:white;'>Tekshiruvlar tarixi</h2>", unsafe_allow_html=True)

    if st.button("Tarixni tozalash", type="secondary"):
        history_file = os.path.join(OUTPUT_DIR, "history.txt")
        if os.path.exists(history_file):
            os.remove(history_file)
        for f in os.listdir(OUTPUT_DIR):
            if f.startswith("result_"):
                os.remove(os.path.join(OUTPUT_DIR, f))
        st.success("Tarix tozalandi!")
        st.experimental_rerun()

    history_file = os.path.join(OUTPUT_DIR, "history.txt")
    if not os.path.exists(history_file):
        st.info("Hozircha hech qanday tekshiruv yo‘q.")
        return

    with open(history_file, "r", encoding="utf-8") as f:
        lines = f.readlines()[::-1]

    cols = st.columns(3)
    for i, line in enumerate(lines):
        path, label, conf, time = line.strip().split("|")
        with cols[i % 3]:
            st.markdown(f"<div class='history-item'>", unsafe_allow_html=True)
            st.image(path, use_column_width=True)
            st.markdown(f"**{label}**")
            st.markdown(f"*{conf}%* – {time}")
            st.markdown("</div>", unsafe_allow_html=True)

# === Aloqa ===
def contact_page():
    st.markdown("<h2 style='text-align:center;color:white;'>Aloqa</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align:center;color:white;'>
    <p><b>Email:</b> bobokhonov_a@samdu.uz</p>
    <p><b>Manzil:</b> Samarqand, O‘zbekiston</p>
    </div>
    """, unsafe_allow_html=True)

# === Asosiy sahifa ===
show_nav()

if st.session_state.page == 'home':
    home_page()
elif st.session_state.page == 'ai':
    ai_page()
elif st.session_state.page == 'history':
    history_page()
elif st.session_state.page == 'contact':
    contact_page()

# === Footer ===
st.markdown("<div class='footer'>© 2025 Skin Cancer AI Detector — Barcha huquqlar himoyalangan</div>", unsafe_allow_html=True)
