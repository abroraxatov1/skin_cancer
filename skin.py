#!/usr/bin/env python3
# =======================================================
# Skin Cancer AI Detector – Streamlit 1.50.0+ (Ishlaydigan CSS + HTML)
# =======================================================
import streamlit as st
from inference_sdk import InferenceHTTPClient
from PIL import Image, ImageDraw
from datetime import datetime
import os

# === KONFIGURATSIYA ===
API_URL = "https://detect.roboflow.com"
API_KEY = "Kz1uRQNYQfiMGbhGigCh"
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

# === Session state ===
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# === To'liq ishlaydigan CSS (Streamlit komponentlariga mos) ===
st.markdown("""
<style>
    /* Fon va asosiy konteyner */
    .stApp {
        background: linear-gradient(135deg, #8EC5FC, #E0C3FC);
        min-height: 100vh;
        padding: 2rem;
        font-family: 'Segoe UI', sans-serif;
    }
    .header {
        text-align: center;
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    /* Navbar tugmalari */
    div[data-testid="column"] button {
        background: rgba(255,255,255,0.25) !important;
        color: white !important;
        border: none !important;
        padding: 0.7rem 1.5rem !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        backdrop-filter: blur(8px) !important;
        transition: all 0.3s !important;
        margin: 0.3rem !important;
    }
    div[data-testid="column"] button:hover {
        background: #4b6cb7 !important;
        transform: translateY(-2px) !important;
    }
    /* Karta */
    .info-card {
        background: rgba(255,255,255,0.3);
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        transition: transform 0.3s;
        text-align: center;
    }
    .info-card:hover {
        transform: translateY(-5px);
    }
    .info-card img {
        border-radius: 12px;
        margin-bottom: 0.8rem;
    }
    /* Natija rasm */
    .result-image {
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        margin: 1rem auto;
        display: block;
    }
    /* Tarix elementi */
    .history-item {
        background: rgba(255,255,255,0.2);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.8rem 0;
        text-align: center;
        color: white;
    }
    .history-item img {
        border-radius: 10px;
        margin-bottom: 0.5rem;
    }
    /* Tahlil tugmasi */
    .stButton > button {
        background: #4b6cb7 !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        width: 100% !important;
        padding: 0.8rem !important;
    }
    .footer {
        text-align: center;
        color: white;
        margin-top: 3rem;
        font-size: 0.9rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# === Navbar (Streamlit columns + CSS orqali stil) ===
def show_nav():
    st.markdown("<div class='header'>Skin Cancer AI Detector</div>", unsafe_allow_html=True)
    cols = st.columns(5)
    with cols[0]:
        if st.button("Bosh sahifa"):
            st.session_state.page = 'home'
    with cols[1]:
        if st.button("AI Tekshiruv"):
            st.session_state.page = 'ai'
    with cols[2]:
        if st.button("Tarix"):
            st.session_state.page = 'history'
    with cols[3]:
        if st.button("Aloqa"):
            st.session_state.page = 'contact'
    with cols[4]:
        if st.button("Chiqish"):
            st.session_state.page = 'home'
    st.markdown("<hr style='border-color:rgba(255,255,255,0.3);'>", unsafe_allow_html=True)

# === Bosh sahifa ===
def home_page():
    st.markdown("<h2 style='text-align:center;color:white;margin-bottom:1rem;'>Teri saratoni haqida</h2>", unsafe_allow_html=True)
    st.markdown("""
    <p style='text-align:center;color:white;font-size:1.1rem;max-width:800px;margin:auto;'>
    Teri saratoni erta aniqlansa, davolanish imkoniyati <b>95% dan yuqori</b>. AI yordamida shubhali dog‘larni tezkor tahlil qiling.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color:white;text-align:center;margin:2rem 0 1rem;'>Asosiy turlari</h3>", unsafe_allow_html=True)
    cols = st.columns(4)
    cards = [
        ("Melanoma", "Eng xavfli turi. Rangi o‘zgaruvchi dog‘lar.", "https://img.lb.wbmdstatic.com/vim/live/webmd/consumer_assets/site_images/article_thumbnails/reference_guide/malignant_melanoma_ref_guide/1800x1200_malignant_melanoma_ref_guide.jpg"),
        ("BCC", "Eng ko‘p uchraydigan, oqish dog‘lar.", "https://mismosavama.net/wp-content/uploads/2022/05/bazalni-1.webp"),
        ("SCC", "Qizil shishlar, quyosh ta’sirida.", "https://citydermatologyclinic.com/wp-content/uploads/2025/09/Squamous-Cell-Carcinoma-1024x1024.jpg"),
        ("Nevus", "Xavfsiz dog‘, lekin kuzatish kerak.", "https://ballaratskincancer.com.au/wp-content/uploads/2020/04/Ballarat-Skin-Cancer-Centre-naevus-1.jpg")
    ]
    for col, (title, desc, img) in zip(cols, cards):
        with col:
            st.markdown(f"<div class='info-card'>", unsafe_allow_html=True)
            st.image(img, use_column_width=True)
            st.markdown(f"**{title}**", unsafe_allow_html=True)
            st.markdown(f"<small style='color:#f0f0f0;'>{desc}</small>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<h3 style='color:white;text-align:center;margin:2rem 0 1rem;'>AI qanday ishlaydi?</h3>", unsafe_allow_html=True)
    st.info("""
    1. **Rasm yuklang**  
    2. **AI 1000+ namunani solishtiradi**  
    3. **Natija: Tur + Ishonchlilik %**  
    """)

    if st.button("AI Tekshiruvni Boshlash", type="primary"):
        st.session_state.page = 'ai'

# === AI Tekshiruv ===
def ai_page():
    st.markdown("<h2 style='text-align:center;color:white;margin-bottom:1.5rem;'>Rasmni yuklang</h2>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

    if uploaded_file:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Tahlil qilish", type="primary"):
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

                        # Natija rasmi
                        img = Image.open(img_path)
                        draw = ImageDraw.Draw(img)
                        draw.text((15, 15), f"{label} ({conf:.1f}%)", fill="red", stroke_width=2, stroke_fill="black")
                        result_name = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                        result_path = os.path.join(OUTPUT_DIR, result_name)
                        img.save(result_path)

                        # Tarixga saqlash
                        with open(os.path.join(OUTPUT_DIR, "history.txt"), "a", encoding="utf-8") as f:
                            f.write(f"{result_path}|{label}|{conf:.1f}|{datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

                        # Natija
                        st.success(f"**{label}** – {conf:.1f}% ishonch bilan")
                        st.image(result_path, width=350, cls="result-image")

                    except Exception as e:
                        st.error(f"Xatolik: {str(e)}")

# === Tarix ===
def history_page():
    st.markdown("<h2 style='text-align:center;color:white;margin-bottom:1.5rem;'>Tekshiruvlar tarixi</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Tarixni tozalash", type="secondary"):
            history_file = os.path.join(OUTPUT_DIR, "history.txt")
            if os.path.exists(history_file):
                os.remove(history_file)
            for f in os.listdir(OUTPUT_DIR):
                if f.startswith("result_") or f == "history.txt":
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
            st.markdown(f"**{label}**", unsafe_allow_html=True)
            st.markdown(f"*{conf}%* – {time}", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# === Aloqa ===
def contact_page():
    st.markdown("<h2 style='text-align:center;color:white;margin-bottom:1.5rem;'>Aloqa</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align:center;color:white;background:rgba(255,255,255,0.2);padding:1.5rem;border-radius:16px;'>
    <p><b>Email:</b> bobokhonov_a@samdu.uz</p>
    <p><b>Manzil:</b> Samarqand, O‘zbekiston</p>
    </div>
    """, unsafe_allow_html=True)

# === Asosiy oqim ===
st.markdown("<div class='main-container'>", unsafe_allow_html=True)
show_nav()

if st.session_state.page == 'home':
    home_page()
elif st.session_state.page == 'ai':
    ai_page()
elif st.session_state.page == 'history':
    history_page()
elif st.session_state.page == 'contact':
    contact_page()

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<div class='footer'>© 2025 Skin Cancer AI Detector — Barcha huquqlar himoyalangan</div>", unsafe_allow_html=True)

