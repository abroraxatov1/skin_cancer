#!/usr/bin/env python3
# =======================================================
# Skin Cancer AI Detector – To'liq to'g'rilangan & Professional
# =======================================================
import streamlit as st
from inference_sdk import InferenceHTTPClient
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os
import base64
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
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
# === Fon rasmini base64 ga aylantirish (ixtiyoriy) ===
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()
# === Zamonaviy CSS (to'g'ri ishlaydi) ===
st.markdown(f"""
<style>
    .stApp {{
        background: {'#0e1117' if st.session_state.dark_mode else 'linear-gradient(135deg, #8EC5FC, #E0C3FC)'};
        min-height: 100vh;
        font-family: 'Inter', sans-serif;
    }}
    .header {{
        text-align: center;
        color: {'#ffffff' if st.session_state.dark_mode else 'white'};
        font-size: 2.8rem;
        font-weight: 800;
        margin: 1rem 0 1.5rem;
        text-shadow: {'none' if st.session_state.dark_mode else '0 2px 4px rgba(0,0,0,0.3)'};
    }}
    /* Navbar tugmalari – bir xil o‘lcham */
    div[data-testid="column"] > div > div > button {{
        background: {'rgba(255,255,255,0.15)' if st.session_state.dark_mode else 'rgba(255,255,255,0.25)'} !important;
        color: white !important;
        border: 2px solid #4b6cb7 !important;
        padding: 0.8rem 1.2rem !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        min-width: 140px !important;
        height: 52px !important;
        width: 100% !important;
        backdrop-filter: blur(10px) !important;
        transition: all 0.3s !important;
        margin: 0.4rem auto !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    div[data-testid="column"] > div > div > button:hover {{
        background: #4b6cb7 !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 20px rgba(75, 108, 183, 0.4) !important;
    }}
    /* Info kartalar */
    .info-card {{
       
        padding: 0.7rem;
      
        backdrop-filter: blur(12px);
        transition: all 0.3s;
        text-align: center;
        height: 100%;
     
    }}
    .info-card:hover {{
        background: {'rgba(30, 33, 43, 0.9)' if st.session_state.dark_mode else 'rgba(255,255,255,0.35)'};
        transform: translateY(-8px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.2);
        border: 1px solid {'rgba(255,255,255,0.1)' if st.session_state.dark_mode else 'rgba(255,255,255,0.4)'};
    }}
    .info-card img {{
        width: 100%;
        height: 100px;
        object-fit: cover;
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 2px solid #4b6cb7;
    }}
    .info-card h4 {{
        margin: 0.8rem 0 0.5rem;
        color: #4b6cb7;
        font-weight: 700;
    }}
    .info-card p {{
        font-size: 0.95rem;
        color: {'#e0e0e0' if st.session_state.dark_mode else '#333'};
        line-height: 1.5;
    }}
    .result-box {{
        background: {'#1e212b' if st.session_state.dark_mode else 'rgba(255,255,255,0.9)'};
        padding: 2rem;
        border-radius: 18px;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border: 1px solid #4b6cb7;
    }}
    .result-img {{
        border-radius: 16px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.2);
        margin: 1rem auto;
        max-width: 380px;
        border: 3px solid #4b6cb7;
    }}
    .history-item {{
        background: {'#1a1d26' if st.session_state.dark_mode else 'rgba(255,255,255,0.25)'};
        border-radius: 16px;
        padding: 1.2rem;
        margin: 1rem 0;
        text-align: center;
        color: white;
        border: 1px solid rgba(75,108,183,0.3);
    }}
    .history-item img {{
        border-radius: 12px;
        margin-bottom: 0.6rem;
        border: 2px solid #4b6cb7;
        max-width: 100%;
    }}
    .stButton > button {{
        background: #4b6cb7 !important;
        color: white !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        padding: 0.8rem;
        width: 100% !important;
        border: 2px solid #4b6cb7 !important;
    }}
    .stButton > button:hover {{
        background: #182848 !important;
        border-color: #182848 !important;
    }}
    .footer {{
        text-align: center;
        color: {'#aaa' if st.session_state.dark_mode else 'white'};
        margin-top: 4rem;
        font-size: 0.9rem;
        opacity: 0.8;
    }}
    .dark-toggle {{
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 1000;
        background: rgba(0,0,0,0.3);
        border-radius: 50px;
        padding: 0.5rem;
    }}
</style>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)
# === Dark Mode Toggle ===
with st.container():
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("Dark" if not st.session_state.dark_mode else "Light", key="theme"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun() # st.experimental_rerun() o'rniga
# === Navbar ===
def show_nav():
    st.markdown("<div class='header'>Skin Cancer AI Detector</div>", unsafe_allow_html=True)
    cols = st.columns(5)
    nav_items = ["Bosh sahifa", "AI Tekshiruv", "Tarix", "Aloqa", "Chiqish"]
    pages = ['home', 'ai', 'history', 'contact', 'home']
    for col, text, page in zip(cols, nav_items, pages):
        with col:
            if st.button(text, key=f"nav_{text}"):
                st.session_state.page = page
    st.markdown("<hr style='border:0;height:2px;background:linear-gradient(90deg,transparent,#4b6cb7,transparent);margin:1.5rem 0;'>", unsafe_allow_html=True)
# === Bosh sahifa ===
def home_page():
    st.markdown("<h2 style='text-align:center;color:white;margin-bottom:1.5rem;'>Teri saratoni turlari</h2>", unsafe_allow_html=True)
   
    cards = [
        ("Melanoma", "Eng xavfli turi. Rangi o‘zgaruvchi, assimetrik dog‘lar bilan namoyon bo‘ladi.",
         "https://img.lb.wbmdstatic.com/vim/live/webmd/consumer_assets/site_images/article_thumbnails/reference_guide/malignant_melanoma_ref_guide/1800x1200_malignant_melanoma_ref_guide.jpg"),
        ("BCC", "Eng ko‘p uchraydigan turi. Odatda yuzda oqish dog‘ sifatida paydo bo‘ladi.",
         "https://mismosavama.net/wp-content/uploads/2022/05/bazalni-1.webp"),
        ("SCC", "Qattiq qizil shishlar yoki yara ko‘rinishida. Quyosh nuri bilan kuchayadi.",
         "https://citydermatologyclinic.com/wp-content/uploads/2025/09/Squamous-Cell-Carcinoma-1024x1024.jpg"),
        ("Nevus", "Xavfsiz (benign) dog‘. Dumaloq, chekkalari aniq. Kuzatish kerak.",
         "https://ballaratskincancer.com.au/wp-content/uploads/2020/04/Ballarat-Skin-Cancer-Centre-naevus-1.jpg")
    ]
    cols = st.columns(4)
    for i, (title, desc, url) in enumerate(cards):
        with cols[i]:
            st.markdown(f"""
            <div class='info-card'>
                <img src='{url}' alt='{title}'>
                <h4>{title}</h4>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("<h3 style='color:white;text-align:center;margin:2.5rem 0 1.5rem;'>AI qanday ishlaydi?</h3>", unsafe_allow_html=True)
    st.success("""
    **1. Rasm yuklang** → Yuqori sifatli teri fotosurati
    **2. AI tahlil qiladi** → 1000+ o‘qitilgan namunalar bilan solishtirish
    **3. Natija chiqaradi** → Saraton turi + ishonchlilik foizi
    """)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("AI Tekshiruvni Boshlash", type="primary"):
            st.session_state.page = 'ai'
# === AI Tekshiruv ===
def ai_page():
    st.markdown("<h2 style='text-align:center;color:white;margin-bottom:1.5rem;'>Teri rasmini yuklang</h2>", unsafe_allow_html=True)
   
    uploaded_file = st.file_uploader(
        "JPG, PNG formatidagi rasmni yuklang",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )
    if uploaded_file:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(uploaded_file, caption="Yuklangan rasm", use_column_width=True)
        with col2:
            if st.button("AI bilan tahlil qilish", type="primary"):
                with st.spinner("AI tahlil qilmoqda..."):
                    try:
                        img_path = os.path.join(OUTPUT_DIR, uploaded_file.name)
                        with open(img_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        result = CLIENT.infer(img_path, model_id=MODEL_ID)
                        preds = result.get("predictions", {})
                        if not preds:
                            label, conf = "Aniqlanmadi", 0
                        else:
                            label, info = max(preds.items(), key=lambda x: x[1]["confidence"])
                            conf = info["confidence"] * 100
                        img = Image.open(img_path)
                        draw = ImageDraw.Draw(img)
                        try:
                            font = ImageFont.truetype("arial.ttf", 40)
                        except:
                            font = ImageFont.load_default()
                        draw.text((20, 20), f"{label} ({conf:.1f}%)", fill="#ff0066", font=font, stroke_width=3, stroke_fill="black")
                        result_name = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                        result_path = os.path.join(OUTPUT_DIR, result_name)
                        img.save(result_path)
                        with open(os.path.join(OUTPUT_DIR, "history.txt"), "a", encoding="utf-8") as f:
                            f.write(f"{result_path}|{label}|{conf:.1f}|{datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                        st.markdown(f"""
                        <div class='result-box'>
                            <h3 style='color:#4b6cb7;margin:0;'>Natija</h3>
                            <h2 style='color:#ff0066;margin:0.5rem 0;'>{label}</h2>
                            <p style='font-size:1.2rem;'><b>{conf:.1f}%</b> ishonch bilan</p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.image(result_path, width=380, caption="Tahlil natijasi")
                        if "melanoma" in label.lower():
                            st.error("Melanoma ehtimoli yuqori! Zudlik bilan dermatologga murojaat qiling!")
                        elif conf > 70:
                            st.warning("Yuqori ehtimollik. Mutaxassis maslahati tavsiya etiladi.")
                        else:
                            st.info("Past ehtimollik. Doimiy kuzatish tavsiya etiladi.")
                    except Exception as e:
                        st.error(f"Xatolik: {str(e)}")
# === Tarix ===
def history_page():
    st.markdown("<h2 style='text-align:center;color:white;margin-bottom:1.5rem;'>Tekshiruvlar tarixi</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Tarixni tozalash", type="secondary"):
            for f in os.listdir(OUTPUT_DIR):
                path = os.path.join(OUTPUT_DIR, f)
                if os.path.isfile(path):
                    os.remove(path)
            st.success("Barcha ma'lumotlar tozalandi!")
            st.rerun() # To'g'ri!
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
            # Base64 orqali rasm ko'rsatish
            with open(path, "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode()
            st.markdown(f"""
            <div class='history-item'>
                <img src='data:image/jpeg;base64,{img_base64}' alt='natija'>
                <h4 style='margin:0.5rem 0;color:#4b6cb7;'>{label}</h4>
                <p style='margin:0;font-weight:600;'>{conf}%</p>
                <small>{time}</small>
            </div>
            """, unsafe_allow_html=True)
# === Aloqa ===
def contact_page():
    st.markdown("<h2 style='text-align:center;color:white;margin-bottom:1.5rem;'>Bog‘lanish</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align:center;background:rgba(255,255,255,0.15);padding:2rem;border-radius:18px;backdrop-filter:blur(10px);border:1px solid rgba(75,108,183,0.3);'>
        <p style='margin:0.8rem 0;font-size:1.1rem;'><b>Email:</b> <a href='mailto:bobokhonov_a@samdu.uz' style='color:#4b6cb7;text-decoration:none;'>bobokhonov_a@samdu.uz</a></p>
        <p style='margin:0.8rem 0;font-size:1.1rem;'><b>Manzil:</b> Samarqand, O‘zbekiston</p>
        <p style='margin:1.5rem 0 0;font-size:0.95rem;color:#ccc;'>© 2025 Skin Cancer AI Detector</p>
    </div>
    """, unsafe_allow_html=True)
# === Asosiy oqim ===
show_nav()
if st.session_state.page == 'home':
    home_page()
elif st.session_state.page == 'ai':
    ai_page()
elif st.session_state.page == 'history':
    history_page()
elif st.session_state.page == 'contact':
    contact_page()
st.markdown("<div class='footer'>Barcha huquqlar himoyalangan • AI faqat maslahat uchun</div>", unsafe_allow_html=True)

