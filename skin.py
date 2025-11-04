#!/usr/bin/env python3
# =======================================================
# 🧠 Skin Cancer AI Detector - Skin Cancer Detection Web App (Streamlit Version)
# =======================================================
import streamlit as st
from inference_sdk import InferenceHTTPClient
from PIL import Image, ImageDraw
from datetime import datetime
import os

# === CONFIGURATION ===
API_URL = "https://detect.roboflow.com"
API_KEY = "Kz1uRQNYQfiMGbhGigCh"  # Roboflow API key
MODEL_ID = "classification-igqvf/1"
OUTPUT_DIR = "results"
os.makedirs(OUTPUT_DIR, exist_ok=True)
CLIENT = InferenceHTTPClient(api_url=API_URL, api_key=API_KEY)

# Inject CSS for similar design
st.markdown("""
<style>
body {
    margin: 0;
    font-family: 'Poppins', sans-serif;
    background: linear-gradient(135deg, #8EC5FC, #E0C3FC);
    min-height: 100vh;
    color: #333;
    overflow-x: hidden;
    transition: background 0.5s ease-in-out;
}
/* ===== Navbar ===== */
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(255,255,255,0.2);
    backdrop-filter: blur(8px);
    padding: 10px 20px;
    position: sticky;
    top: 0;
}
.navbar h2 {
    color: white;
}
.menu {
    display: flex;
    gap: 20px;
}
.menu button {
    text-decoration: none;
    color: white;
    font-weight: bold;
    transition: 0.3s;
    background: none;
    border: none;
    cursor: pointer;
}
.menu button:hover {
    color: #ffd700;
}
.hamburger {
    display: none;
    font-size: 26px;
    cursor: pointer;
    color: white;
}
/* ===== Responsive ===== */
@media (max-width: 768px) {
    .menu {
        display: none;
        flex-direction: column;
        background: rgba(255,255,255,0.2);
        position: absolute;
        top: 60px;
        right: 20px;
        padding: 10px;
        border-radius: 8px;
    }
    .menu.active { display: flex; }
    .hamburger { display: block; }
}
/* ===== Main content ===== */
.container {
    text-align: center;
    padding: 50px 20px;
    animation: fadeIn 1s ease-in-out;
}
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(10px);}
    to {opacity: 1; transform: translateY(0);}
}
.upload-box {
    background: rgba(255,255,255,0.3);
    padding: 30px;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    display: inline-block;
    transition: transform 0.3s;
}
.upload-box:hover { transform: scale(1.03); }
button {
    background: #4b6cb7;
    color: white;
    padding: 10px 25px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: 0.3s;
}
button:hover { background: #182848; }
/* ===== Spinner ===== */
.spinner {
    display: none;
    margin: 20px auto;
    border: 5px solid rgba(255,255,255,0.4);
    border-top: 5px solid #4b6cb7;
    border-radius: 50%;
    width: 60px;
    height: 60px;
    animation: spin 1s linear infinite;
}
@keyframes spin { to {transform: rotate(360deg);} }
.result img {
    margin-top: 20px;
    width: 300px;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}
footer {
    text-align: center;
    margin-top: 60px;
    padding: 20px;
    color: white;
}
.page { display: none; }
.page.active { display: block; }
/* ===== Cards (Bosh sahifa) ===== */
.info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-top: 30px;
}
.card {
    background: rgba(255,255,255,0.3);
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    transition: 0.3s;
}
.card:hover {
    transform: scale(1.05);
}
.card img {
    width: 100px; height: 70px;
    border-radius: 10px;
    margin-bottom: 10px;
}
.history-item {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    margin: 10px;
    padding: 10px;
    border-radius: 10px;
    width: 220px;
}
/* AI tekshiruvi sahifasining orqa foni */
.page {
    background-image: url('bg.jpg');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    padding: 50px 20px;
}
.history-item img { width: 100%; border-radius: 8px; }
/* Streamlit overrides */
div.stButton > button:first-child {
    background: transparent;
    color: white;
    border: none;
    font-weight: bold;
}
div.stButton > button:first-child:hover {
    color: #ffd700;
}
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'user' not in st.session_state:
    st.session_state.user = 'active'

# Navbar simulation with Streamlit components
with st.container():
    cols = st.columns([4, 1, 1, 1, 1, 1])
    cols[0].markdown("<h2 style='color:white;'>🧠 Skin Cancer AI Detector</h2>", unsafe_allow_html=True)
    if cols[1].button("Bosh sahifa"):
        st.session_state.current_page = 'home'
    if cols[2].button("AI tekshiruvi"):
        st.session_state.current_page = 'ai'
    if cols[3].button("Tekshiruvlar tarixi"):
        st.session_state.current_page = 'history'
    if cols[4].button("Aloqa"):
        st.session_state.current_page = 'contact'
    if cols[5].button("Chiqish"):
        st.session_state.current_page = 'home'
        st.session_state.user = None
        st.experimental_rerun()

# Main content based on current page
current_page = st.session_state.current_page

if current_page == 'home':
    st.markdown("<div class='container page active' id='home'>", unsafe_allow_html=True)
    st.markdown("<h2>👩‍⚕️ Teri saratoni haqida</h2>", unsafe_allow_html=True)
    st.markdown("""
    <p style="max-width:750px;margin:auto;font-size:18px;">
        Teri saratoni — bu teri hujayralarining nazoratsiz o‘sishidan paydo bo‘ladigan xavfli o‘sma bo‘lib,
        erta bosqichda aniqlansa, davolanish imkoniyati yuqori bo‘ladi. Quyida asosiy turlari bilan tanishing:
    </p>
    """, unsafe_allow_html=True)
    cols = st.columns(4)
    with cols[0]:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.image("https://img.lb.wbmdstatic.com/vim/live/webmd/consumer_assets/site_images/article_thumbnails/reference_guide/malignant_melanoma_ref_guide/1800x1200_malignant_melanoma_ref_guide.jpg", use_column_width=True)
        st.markdown("<h4>Melanoma (Mel)</h4>", unsafe_allow_html=True)
        st.markdown("<p>Eng xavfli turi. Melanin ishlab chiqaruvchi hujayralarda rivojlanadi. Rangi o‘zgaruvchi dog‘lar bilan namoyon bo‘ladi.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.image("https://mismosavama.net/wp-content/uploads/2022/05/bazalni-1.webp", use_column_width=True)
        st.markdown("<h4>Bazal hujayrali saraton (BCC)</h4>", unsafe_allow_html=True)
        st.markdown("<p>Eng ko‘p uchraydigan turi. Odatda yuz yoki bo‘yinda oqish dog‘ sifatida paydo bo‘ladi.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with cols[2]:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.image("https://citydermatologyclinic.com/wp-content/uploads/2025/09/Squamous-Cell-Carcinoma-1024x1024.jpg", use_column_width=True)
        st.markdown("<h4>Yassi hujayrali saraton (SCC)</h4>", unsafe_allow_html=True)
        st.markdown("<p>Teri yuzasida qattiq qizil shishlar yoki yara ko‘rinishida bo‘ladi. Quyosh nuri bilan bog‘liq.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with cols[3]:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.image("https://ballaratskincancer.com.au/wp-content/uploads/2020/04/Ballarat-Skin-Cancer-Centre-naevus-1.jpg", use_column_width=True)
        st.markdown("<h4>Melanotsitik nevi (NV)</h4>", unsafe_allow_html=True)
        st.markdown("<p>Benign (xavfsiz) lezyon, melanotsitlardan hosil bo‘ladi. Ko‘pincha jigarrang yoki qora dog‘; dumaloq yoki oval shaklda; chekkalari aniq. Tananing har qaysi qismida paydo bo‘lishi mumkin. Odatda xavfsiz, lekin ba’zi melanomalar nevi ustidan rivojlanishi mumkin.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br><h3>🧠 AI yordamida aniqlash qanday ishlaydi?</h3>", unsafe_allow_html=True)
    st.markdown("""
    <p style="max-width:750px;margin:auto;font-size:17px;">
        NeuroScan AI siz yuklagan rasmni chuqur neyron tarmoq orqali tahlil qiladi:
    </p>
    <ul style="text-align:left;max-width:600px;margin:20px auto;line-height:1.7;">
        <li>📸 Rasm yuklanadi</li>
        <li>🧮 Model rasmni 1000 dan ortiq o‘qitilgan namunalar bilan solishtiradi</li>
        <li>💡 AI o‘xshashlik va xavf darajasini hisoblaydi</li>
        <li>📊 Natija: aniqlangan turi va ishonchlilik foizi</li>
    </ul>
    """, unsafe_allow_html=True)
    if st.button("🔍 AI tekshiruvni boshlash"):
        st.session_state.current_page = 'ai'
    st.markdown("</div>", unsafe_allow_html=True)

elif current_page == 'ai':
    st.markdown("<div class='container page active' id='ai'>", unsafe_allow_html=True)
    st.markdown("<div class='upload-box'>", unsafe_allow_html=True)
    st.markdown("<h3>AI orqali rasmni tahlil qilish</h3>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    if st.button("Tahlilni boshlash"):
        if uploaded_file is not None:
            with st.spinner("Tahlil qilinmoqda..."):
                img_path = os.path.join(OUTPUT_DIR, uploaded_file.name)
                with open(img_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                try:
                    result = CLIENT.infer(img_path, model_id=MODEL_ID)
                    preds = result.get("predictions", {})
                    if not preds:
                        label = "Teri saratoni aniqlanmadi"
                        conf = 0
                    else:
                        label, info = max(preds.items(), key=lambda x: x[1]["confidence"])
                        conf = info["confidence"] * 100
                    img = Image.open(img_path)
                    draw = ImageDraw.Draw(img)
                    draw.text((20, 20), f"{label} ({conf:.1f}%)", fill="red")
                    result_name = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    result_path = os.path.join(OUTPUT_DIR, result_name)
                    img.save(result_path)
                    with open(os.path.join(OUTPUT_DIR, "history.txt"), "a", encoding="utf-8") as f:
                        f.write(f"{result_path}|{label}|{conf:.1f}|{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    st.markdown(f"<p><b>{label}</b> ({conf:.1f}%)</p>", unsafe_allow_html=True)
                    st.image(result_path, use_column_width=False, width=300)
                except Exception as e:
                    st.error(str(e))
        else:
            st.error("Rasm tanlanmadi")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif current_page == 'history':
    st.markdown("<div class='container page active' id='history'>", unsafe_allow_html=True)
    st.markdown("<h3>📂 Tekshiruvlar tarixi</h3>", unsafe_allow_html=True)
    if st.button("🗑️ Tarixni tozalash"):
        history_file = os.path.join(OUTPUT_DIR, "history.txt")
        if os.path.exists(history_file):
            os.remove(history_file)
        for file in os.listdir(OUTPUT_DIR):
            if file.startswith("result_"):
                os.remove(os.path.join(OUTPUT_DIR, file))
        st.experimental_rerun()
    path = os.path.join(OUTPUT_DIR, "history.txt")
    if not os.path.exists(path):
        st.markdown("<p>Hozircha hech qanday natija yo‘q.</p>", unsafe_allow_html=True)
    else:
        data = []
        with open(path, "r", encoding="utf-8") as f:
            for line in reversed(f.readlines()):
                p, l, c, t = line.strip().split("|")
                data.append({"image": p, "label": l, "confidence": float(c), "time": t})
        cols = st.columns(4)
        for i, item in enumerate(data):
            with cols[i % 4]:
                st.markdown("<div class='history-item'>", unsafe_allow_html=True)
                st.image(item["image"])
                st.markdown(f"<p><b>{item['label']}</b></p>", unsafe_allow_html=True)
                st.markdown(f"<p>{item['confidence']}%</p>", unsafe_allow_html=True)
                st.markdown(f"<small>{item['time']}</small>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif current_page == 'contact':
    st.markdown("<div class='container page active' id='contact'>", unsafe_allow_html=True)
    st.markdown("<h3>📞 Aloqa ma’lumotlari</h3>", unsafe_allow_html=True)
    st.markdown("<p>Email: <b>bobokhonov_a@samdu.uz</b></p>", unsafe_allow_html=True)
    st.markdown("<p>Manzil: Samarqand, O‘zbekiston</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<footer>© 2025 Skin Cancer AI Detector — Barcha huquqlar himoyalangan</footer>", unsafe_allow_html=True)