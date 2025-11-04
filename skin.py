#!/usr/bin/env python3
# =======================================================
# Skin Cancer AI Detector – Bootstrap 5 Navbar
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

# === Bootstrap 5 CDN + Custom CSS ===
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
    .stApp {
        background: linear-gradient(135deg, #8EC5FC, #E0C3FC);
        min-height: 100vh;
        font-family: 'Inter', sans-serif;
    }
    .navbar {
        background: rgba(255, 255, 255, 0.2) !important;
        backdrop-filter: blur(12px);
        border-bottom: 1px solid rgba(75, 108, 183, 0.3);
        padding: 0.8rem 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .navbar-brand {
        font-weight: 800;
        font-size: 1.8rem;
        color: white !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .nav-link {
        color: white !important;
        font-weight: 600;
        font-size: 1.1rem;
        padding: 0.6rem 1.2rem !important;
        border-radius: 12px;
        transition: all 0.3s ease;
        margin: 0 0.3rem;
    }
    .nav-link:hover {
        background: #4b6cb7 !important;
        color: white !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(75, 108, 183, 0.35);
    }
    .nav-link.active {
        background: #4b6cb7 !important;
        color: white !important;
        font-weight: 700;
        box-shadow: 0 6px 15px rgba(75, 108, 183, 0.4);
    }
    .info-card {
        background: rgba(255, 255, 255, 0.3);
        padding: 1.5rem;
        border-radius: 18px;
        text-align: center;
        height: 100%;
        border: 1px solid rgba(255,255,255,0.5);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        box-shadow: 0 6px 18px rgba(0,0,0,0.12);
    }
    .info-card:hover {
        transform: translateY(-8px);
        background: rgba(255, 255, 255, 0.45);
        box-shadow: 0 12px 28px rgba(0,0,0,0.18);
    }
    .info-card img {
        width: 100%;
        height: 180px;
        object-fit: cover;
        border-radius: 14px;
        border: 3px solid #4b6cb7;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .info-card h4 {
        color: #4b6cb7;
        font-weight: 700;
        margin: 0.8rem 0 0.5rem;
    }
    .info-card p {
        color: #333;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .result-box {
        background: rgba(255,255,255,0.92);
        padding: 2rem;
        border-radius: 18px;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border: 1px solid #4b6cb7;
    }
    .result-img {
        border-radius: 16px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.2);
        max-width: 100%;
        width: 420px;
        border: 3px solid #4b6cb7;
    }
    .history-item {
        background: rgba(255,255,255,0.25);
        border-radius: 16px;
        padding: 1.2rem;
        margin: 1rem 0;
        text-align: center;
        color: #333;
        border: 1px solid rgba(75,108,183,0.3);
    }
    .history-item img {
        border-radius: 12px;
        margin-bottom: 0.6rem;
        border: 2px solid #4b6cb7;
        max-width: 100%;
        height: 180px;
        object-fit: cover;
    }
    .footer {
        text-align: center;
        color: white;
        margin-top: 4rem;
        font-size: 0.95rem;
        opacity: 0.9;
    }
</style>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# === Dark Mode Toggle (o‘ng yuqori burchak) ===
with st.container():
    col1, col2 = st.columns([8, 1])
    with col2:
        if st.button("Dark" if not st.session_state.dark_mode else "Light", key="theme"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

# === Bootstrap Navbar ===
def show_nav():
    nav_items = [
        ("Bosh sahifa", 'home'),
        ("AI Tekshiruv", 'ai'),
        ("Tarix", 'history'),
        ("Aloqa", 'contact'),
        ("Chiqish", 'home')
    ]

    nav_html = '''
    <nav class="navbar navbar-expand-lg">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">Skin Cancer AI Detector</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse justify-content-center" id="navbarNav">
          <ul class="navbar-nav">
    '''

    for text, page in nav_items:
        is_active = st.session_state.page == page
        active_class = "active" if is_active else ""
        nav_html += f'''
            <li class="nav-item">
              <a class="nav-link {active_class}" href="#" onclick="document.getElementById('nav_{page}').click()">{text}</a>
            </li>
        '''

    nav_html += '''
          </ul>
        </div>
      </div>
    </nav>
    '''

    st.markdown(nav_html, unsafe_allow_html=True)

    # Yashirin tugmalar (bosish uchun)
    for _, page in nav_items:
        if st.button("", key=f"nav_{page}", help=""):
            st.session_state.page = page
            st.rerun()

    st.markdown("<hr style='border:0;height:2px;background:linear-gradient(90deg,transparent,#4b6cb7,transparent);margin:1.5rem 0;'>", unsafe_allow_html=True)

# === Bosh sahifa ===
def home_page():
    st.markdown("<h2 class='text-center text-white mb-4'>Teri saratoni turlari</h2>", unsafe_allow_html=True)
    
    cards = [
        ("Melanoma", "Eng xavfli turi. Rangi o‘zgaruvchi, assimetrik dog‘lar bilan namoyon bo‘ladi.",
         "https://img.lb.wbmdstatic.com/vim/live/webmd/consumer_assets/site_images/article_thumbnails/reference_guide/malignant_melanoma_ref_guide/1800x1200_malignant_melanoma_ref_guide.jpg"),
        ("BCC", "Eng ko‘p uchraydigan turi. Odatda yuzda oqish yoki qon ketadigan dog‘ sifatida paydo bo‘ladi.",
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

    st.markdown("<h3 class='text-white text-center mt-5 mb-3'>AI qanday ishlaydi?</h3>", unsafe_allow_html=True)
    st.success("""
    **1. Rasm yuklang** → Yuqori sifatli teri fotosurati  
    **2. AI tahlil qiladi** → 1000+ o‘qitilgan namunalar bilan solishtirish  
    **3. Natija chiqaradi** → Saraton turi + ishonchlilik foizi  
    """)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("AI Tekshiruvni Boshlash", type="primary", use_container_width=True):
            st.session_state.page = 'ai'

# === AI Tekshiruv ===
def ai_page():
    st.markdown("<h2 class='text-center text-white mb-4'>Teri rasmini yuklang</h2>", unsafe_allow_html=True)
    
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
            if st.button("AI bilan tahlil qilish", type="primary", use_container_width=True):
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
                            font = ImageFont.truetype("arial.ttf", 42)
                        except:
                            font = ImageFont.load_default()
                        draw.text((22, 22), f"{label} ({conf:.1f}%)", fill="#ff0066", font=font, stroke_width=3, stroke_fill="black")

                        result_name = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                        result_path = os.path.join(OUTPUT_DIR, result_name)
                        img.save(result_path)

                        with open(os.path.join(OUTPUT_DIR, "history.txt"), "a", encoding="utf-8") as f:
                            f.write(f"{result_path}|{label}|{conf:.1f}|{datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

                        st.markdown(f"""
                        <div class='result-box'>
                            <h3 style='color:#4b6cb7;'>Natija</h3>
                            <h2 style='color:#ff0066;'>{label}</h2>
                            <p style='font-size:1.3rem;'><b>{conf:.1f}%</b> ishonch bilan</p>
                        </div>
                        """, unsafe_allow_html=True)

                        st.image(result_path, caption="Tahlil natijasi", width=420)

                        if "melanoma" in label.lower():
                            st.error("**Melanoma ehtimoli yuqori!** Zudlik bilan dermatologga murojaat qiling!")
                        elif conf > 70:
                            st.warning("Yuqori ehtimollik. Mutaxassis maslahati tavsiya etiladi.")
                        else:
                            st.info("Past ehtimollik. Doimiy kuzatish tavsiya etiladi.")

                    except Exception as e:
                        st.error(f"Xatolik: {str(e)}")

# === Tarix ===
def history_page():
    st.markdown("<h2 class='text-center text-white mb-4'>Tekshiruvlar tarixi</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Tarixni tozalash", type="secondary", use_container_width=True):
            for f in os.listdir(OUTPUT_DIR):
                path = os.path.join(OUTPUT_DIR, f)
                if os.path.isfile(path):
                    os.remove(path)
            st.success("Barcha ma'lumotlar tozalandi!")
            st.rerun()

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
            with open(path, "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode()
            st.markdown(f"""
            <div class='history-item'>
                <img src='data:image/jpeg;base64,{img_base64}' alt='natija'>
                <h4 style='color:#4b6cb7;'>{label}</h4>
                <p style='font-weight:600;'>{conf}%</p>
                <small>{time}</small>
            </div>
            """, unsafe_allow_html=True)

# === Aloqa ===
def contact_page():
    st.markdown("<h2 class='text-center text-white mb-4'>Bog‘lanish</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align:center;background:rgba(255,255,255,0.15);padding:2.5rem;border-radius:18px;backdrop-filter:blur(10px);border:1px solid rgba(75,108,183,0.3);'>
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

# === Bootstrap JS (toggler uchun) ===
st.markdown("""
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
""", unsafe_allow_html=True)
