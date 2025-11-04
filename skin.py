#!/usr/bin/env python3
# app.py — Skin Cancer AI Detector (refactored, responsive, modern UI)
# Run: streamlit run app.py
# NOTE: Set your Roboflow API key in environment: ROBOFLOW_API_KEY

import os
import io
import json
import base64
from datetime import datetime
from pathlib import Path

import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# Optional: If you have an official client, use it.
# from inference_sdk import InferenceHTTPClient
import requests

# -------------------------
# Configuration
# -------------------------
APP_TITLE = "Skin Cancer AI Detector"
OUTPUT_DIR = Path("results")
HISTORY_FILE = OUTPUT_DIR / "history.json"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Roboflow / inference configuration:
ROBOFLOW_API_URL = "https://detect.roboflow.com"
MODEL_ID = "classification-igqvf/1"  # keep as-is or move to env
API_KEY = os.getenv("ROBOFLOW_API_KEY", None)  # IMPORTANT: put your key in env var

# If no API key, app will run in "demo" mode with simple heuristics
DEMO_MODE = API_KEY is None

# -------------------------
# Streamlit page config
# -------------------------
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -------------------------
# Helpers
# -------------------------
def load_history():
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def append_history(item):
    history = load_history()
    history.append(item)
    save_history(history)

def clear_history_files():
    # Remove saved result images and history
    history = load_history()
    for item in history:
        p = Path(item.get("result_path", ""))
        if p.exists():
            try:
                p.unlink()
            except Exception:
                pass
    if HISTORY_FILE.exists():
        HISTORY_FILE.unlink()

def pil_to_base64(img: Image.Image, fmt="JPEG"):
    buf = io.BytesIO()
    img.save(buf, format=fmt, quality=85)
    b = base64.b64encode(buf.getvalue()).decode()
    return b

def annotate_image(img_path, label, conf, accent="#ff0066"):
    try:
        img = Image.open(img_path).convert("RGB")
    except Exception:
        return None
    draw = ImageDraw.Draw(img)
    # choose a font if available
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
    except Exception:
        font = ImageFont.load_default()
    text = f"{label} — {conf:.1f}%"
    padding = 14
    w, h = draw.textsize(text, font=font)
    rect_x0, rect_y0 = padding, padding
    rect_x1, rect_y1 = rect_x0 + w + padding * 2, rect_y0 + h + padding
    draw.rectangle([rect_x0, rect_y0, rect_x1, rect_y1], fill=(30, 30, 30, 200))
    draw.text((rect_x0 + padding, rect_y0 + (padding // 2)), text, fill=accent, font=font)
    return img

def infer_with_roboflow(image_path):
    """Simple POST request to Roboflow inference endpoint.
       If API_KEY missing or request fails, raises Exception."""
    if API_KEY is None:
        raise RuntimeError("No API key provided (demo mode).")
    url = f"{ROBOFLOW_API_URL}/{MODEL_ID}"
    headers = {"Authorization": API_KEY}
    with open(image_path, "rb") as f:
        files = {"file": f}
        resp = requests.post(url, headers=headers, files=files, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"Inference failed: {resp.status_code} {resp.text}")
    return resp.json()

def demo_predict(image_path):
    """A simple fallback 'demo' predictor (not medical). Uses average brightness."""
    img = Image.open(image_path).convert("L").resize((64, 64))
    avg = sum(img.getdata()) / (64 * 64)
    # heuristic: darker lesions might be more suspicious (this is NOT medical advice)
    if avg < 100:
        return {"label": "Melanoma-like", "confidence": float(55 + (120 - avg) * 0.2)}
    elif avg < 140:
        return {"label": "Suspicious", "confidence": float(40 + (140 - avg) * 0.3)}
    else:
        return {"label": "Benign-like", "confidence": float(min(95, avg * 0.4))}

# -------------------------
# Styling (responsive + modern)
# -------------------------
# Important: keep CSS scoped and minimal to avoid breaking Streamlit internals.
st.markdown(
    """
    <style>
    :root{
      --primary: #4b6cb7;
      --secondary: #182848;
      --accent: #ff0066;
      --card-bg: rgba(255,255,255,0.85);
      --glass: rgba(255,255,255,0.08);
      --radius: 14px;
      --shadow: 0 8px 30px rgba(15,23,42,0.12);
    }
    /* Make top bar sticky */
    .topbar {
      position: sticky;
      top: 0;
      z-index: 999;
      backdrop-filter: blur(6px);
      display:flex;
      align-items:center;
      justify-content:space-between;
      padding:10px 20px;
      border-bottom: 1px solid rgba(0,0,0,0.06);
      background: linear-gradient(180deg, rgba(255,255,255,0.6), rgba(255,255,255,0.35));
    }
    .brand {
      display:flex;
      align-items:center;
      gap:12px;
      font-weight:700;
      font-size:18px;
      color:var(--secondary);
    }
    .brand .logo {
      width:42px;height:42px;border-radius:10px;
      display:inline-block;background:linear-gradient(135deg,var(--primary),var(--secondary));
      color:white;align-items:center;justify-content:center;display:flex;font-weight:800;
    }
    .nav {
      display:flex;
      gap:8px;
      align-items:center;
    }
    .nav button {
      border-radius: 10px;
      padding:8px 14px;
      background:transparent;
      border: 1px solid rgba(76, 108, 183, 0.18);
      color:var(--secondary);
      font-weight:600;
    }
    .nav button.active {
      background: linear-gradient(90deg,var(--primary),var(--secondary));
      color:white;
      border:none;
      box-shadow:var(--shadow);
    }
    .hero {
      display:flex;
      gap:30px;
      align-items:center;
      justify-content:space-between;
      padding:40px 20px;
      margin-bottom: 20px;
      border-radius: var(--radius);
    }
    .hero .content {
      flex:1;
      min-width: 220px;
    }
    .hero .visual {
      width:420px;
      max-width:40%;
    }
    /* Cards grid */
    .cards-grid {
      display:grid;
      grid-template-columns: repeat(4, 1fr);
      gap:16px;
    }
    @media (max-width: 1100px) {
      .cards-grid { grid-template-columns: repeat(3,1fr); }
      .hero { flex-direction:column; align-items:flex-start; }
      .hero .visual { max-width:100%; width:100%; }
    }
    @media (max-width: 760px) {
      .cards-grid { grid-template-columns: repeat(2,1fr); }
      .nav { display:none; }
    }
    @media (max-width: 420px) {
      .cards-grid { grid-template-columns: 1fr; }
    }
    .card {
      border-radius:12px;
      padding:12px;
      background: linear-gradient(180deg, rgba(255,255,255,0.9), rgba(255,255,255,0.8));
      border: 1px solid rgba(75,108,183,0.12);
      box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    }
    .result-panel {
      padding:18px;
      border-radius:12px;
      background:linear-gradient(180deg, rgba(255,255,255,0.95), rgba(255,255,255,0.9));
      border:1px solid rgba(75,108,183,0.12);
    }
    .history-grid {
      display:grid;
      grid-template-columns: repeat(3,1fr);
      gap:12px;
    }
    @media (max-width: 1100px) { .history-grid { grid-template-columns: repeat(2,1fr); } }
    @media (max-width: 760px) { .history-grid { grid-template-columns: 1fr; } }
    .history-item {
      border-radius:12px;padding:10px;background:linear-gradient(180deg, #fff,#f7f9ff);border:1px solid rgba(75,108,183,0.06);
    }
    .footer {
      padding:22px;text-align:center;color:#666;font-size:13px;margin-top:34px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Topbar / Navbar (custom)
# -------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "dark" not in st.session_state:
    st.session_state.dark = False

# build topbar
topbar_html = f"""
<div class="topbar">
  <div class="brand">
    <div class="logo">AI</div>
    <div>
      <div style="font-size:14px;color:#222;font-weight:800;">{APP_TITLE}</div>
      <div style="font-size:12px;color:#666;margin-top:2px;">Skin lesion image classification (assistive)</div>
    </div>
  </div>

  <div style="display:flex;align-items:center;gap:12px;">
    <div class="nav">
      <button class="{'active' if st.session_state.page=='home' else ''}" onclick="window.dispatchEvent(new CustomEvent('streamlit:nav',{{detail:'home'}}))">Home</button>
      <button class="{'active' if st.session_state.page=='ai' else ''}" onclick="window.dispatchEvent(new CustomEvent('streamlit:nav',{{detail:'ai'}}))">AI Check</button>
      <button class="{'active' if st.session_state.page=='history' else ''}" onclick="window.dispatchEvent(new CustomEvent('streamlit:nav',{{detail:'history'}}))">History</button>
      <button class="{'active' if st.session_state.page=='contact' else ''}" onclick="window.dispatchEvent(new CustomEvent('streamlit:nav',{{detail:'contact'}}))">Contact</button>
    </div>
  </div>
</div>
"""
# Note: onClick JS events won't work with Streamlit's sandboxed environment.
# We still render the topbar and use Streamlit buttons below for navigation.
st.markdown(topbar_html, unsafe_allow_html=True)

# Provide fallback navigation buttons (these are the actual controls)
nav_cols = st.columns([1, 1, 1, 1, 4])
with nav_cols[0]:
    if st.button("Home", key="nav_home"):
        st.session_state.page = "home"
with nav_cols[1]:
    if st.button("AI Check", key="nav_ai"):
        st.session_state.page = "ai"
with nav_cols[2]:
    if st.button("History", key="nav_history"):
        st.session_state.page = "history"
with nav_cols[3]:
    if st.button("Contact", key="nav_contact"):
        st.session_state.page = "contact"
with nav_cols[4]:
    # Theme toggle placeholder (we keep streamlit default)
    st.write("")

# -------------------------
# Page: Home
# -------------------------
def page_home():
    st.markdown(
        """
        <div class="hero">
            <div class="content">
                <h1 style="margin:0;color:#182848;">Check skin lesions with AI — quick, visual, assistive</h1>
                <p style="color:#444;margin-top:8px;">
                    Upload a clinical-quality photo of a skin lesion. This tool compares the image to a trained model and returns a classification with confidence.
                    <strong>Not a diagnosis.</strong> Always consult a dermatologist for medical decisions.
                </p>
                <div style="margin-top:18px;">
                    <a href="#ai" style="text-decoration:none;">
                        <button style="padding:10px 16px;border-radius:10px;background:linear-gradient(90deg,#4b6cb7,#182848);color:white;border:none;font-weight:700;">Start AI Check</button>
                    </a>
                    <span style="margin-left:12px;color:#666;font-size:13px;">Or scroll to see lesion types</span>
                </div>
            </div>
            <div class="visual">
                <img src="https://images.unsplash.com/photo-1517694712202-14dd9538aa97?q=80&w=800&auto=format&fit=crop&ixlib=rb-4.0.3&s=6c668d26b1f4c3c2d4e7a4f9e7223a68" style="width:100%;border-radius:12px;box-shadow:0 8px 30px rgba(24,40,72,0.08);" />
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<h3 style='color:#182848;margin-top:18px;'>Common lesion types</h3>", unsafe_allow_html=True)
    # Cards grid
    cards = [
        ("Melanoma", "Potentially serious; asymmetry, border irregularity, color variegation.", "https://images.unsplash.com/photo-1526256262350-7da7584cf5eb?q=80&w=1200&auto=format&fit=crop&ixlib=rb-4.0.3&s=ea6e0372fb1f2b2ad5f9f9b7f4a2f2b9"),
        ("Basal Cell Carcinoma (BCC)", "Often pearly nodules or non-healing sores, common on sun-exposed areas.", "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?q=80&w=1200&auto=format&fit=crop&ixlib=rb-4.0.3&s=61f1c8b7c6b0713a8d7c6a8c4f8b2bfa"),
        ("Squamous Cell Carcinoma (SCC)", "Red, scaly patches or ulcers; can arise on chronic sun-damaged skin.", "https://images.unsplash.com/photo-1582719478250-1d5b0945f8f4?q=80&w=1200&auto=format&fit=crop&ixlib=rb-4.0.3&s=3f8a4e2a49de15f3b9a9a2a4f3b7c8d9"),
        ("Nevus (Mole)", "Benign-looking round/oval lesions with regular borders — monitoring recommended.", "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?q=80&w=1200&auto=format&fit=crop&ixlib=rb-4.0.3&s=9b3f7f4f6f3b5e6d7c8f9a0b1c2d3e4f"),
    ]

    # responsive grid using columns
    cols = st.columns(4)
    for col, (title, desc, url) in zip(cols, cards):
        with col:
            st.markdown(
                f"""
                <div class="card">
                  <img src="{url}" style="width:100%;height:140px;object-fit:cover;border-radius:10px;margin-bottom:8px;" />
                  <h4 style="margin:6px 0 4px;color:#182848;">{title}</h4>
                  <p style="margin:0;font-size:14px;color:#444;">{desc}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.markdown(
        """
        <div style="display:flex;gap:12px;align-items:center;">
            <div style="flex:1">
                <h3 style="margin:0;color:#182848;">Why use this tool?</h3>
                <p style="color:#444;">It performs quick image classification using a trained model and gives a confidence estimate. It is for triage and educational purposes only.</p>
            </div>
            <div style="width:220px;">
                <button style="padding:10px 12px;border-radius:10px;background:linear-gradient(90deg,#4b6cb7,#182848);color:white;border:none;font-weight:700;width:100%;">Learn more</button>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -------------------------
# Page: AI Check
# -------------------------
def page_ai():
    st.markdown("<h2 style='color:#182848;'>AI Check — Upload image</h2>", unsafe_allow_html=True)

    left, right = st.columns([2, 1])

    with left:
        uploaded = st.file_uploader(
            "Upload a clear photo of the lesion (JPG/PNG). For best results: good lighting, lesion filling most of frame.",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=False,
            help="Drag & drop supported."
        )

        # optional patient note
        patient_note = st.text_input("Short note (optional): where on the body, age, prior changes etc.")

        # upload example / demo images
        examples_exp = st.expander("See example images")
        with examples_exp:
            demo_cols = st.columns(4)
            demo_imgs = [
                "https://images.unsplash.com/photo-1526256262350-7da7584cf5eb?q=80&w=800&auto=format&fit=crop&ixlib=rb-4.0.3&s=ea6e0372fb1f2b2ad5f9f9b7f4a2f2b9",
                "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?q=80&w=800&auto=format&fit=crop&ixlib=rb-4.0.3&s=61f1c8b7c6b0713a8d7c6a8c4f8b2bfa",
                "https://images.unsplash.com/photo-1582719478250-1d5b0945f8f4?q=80&w=800&auto=format&fit=crop&ixlib=rb-4.0.3&s=3f8a4e2a49de15f3b9a9a2a4f3b7c8d9",
                "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?q=80&w=800&auto=format&fit=crop&ixlib=rb-4.0.3&s=9b3f7f4f6f3b5e6d7c8f9a0b1c2d3e4f",
            ]
            for c, url in zip(demo_cols, demo_imgs):
                with c:
                    st.image(url, use_column_width=True, caption="Example", output_format="auto")

    with right:
        st.markdown("<div class='result-panel'>", unsafe_allow_html=True)
        st.markdown("<h4 style='margin:0;color:#182848;'>Result</h4>", unsafe_allow_html=True)
        placeholder = st.empty()
        if DEMO_MODE:
            st.info("Running in demo mode (no API key). To enable real inference set ROBOFLOW_API_KEY env variable.")
        st.markdown("</div>", unsafe_allow_html=True)

    # perform inference
    if uploaded:
        # save original
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = f"{Path(uploaded.name).stem}_{ts}{Path(uploaded.name).suffix}"
        saved_path = OUTPUT_DIR / safe_name
        with open(saved_path, "wb") as f:
            f.write(uploaded.getbuffer())

        # Show preview
        st.image(saved_path, caption="Uploaded image", use_column_width=True)

        # action buttons
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            if st.button("Run AI Check", key=f"run_{ts}"):
                # perform inference with spinner
                with st.spinner("Running model..."):
                    try:
                        if not DEMO_MODE:
                            resp = infer_with_roboflow(str(saved_path))
                            # Roboflow classification format may vary — try to read safely
                            preds = resp.get("predictions") if isinstance(resp, dict) else None
                            if preds:
                                # pick highest confidence
                                best = max(preds, key=lambda p: p.get("confidence", 0))
                                label = best.get("class", best.get("label", "Unknown"))
                                conf = float(best.get("confidence", 0) * 100)
                            else:
                                # If Roboflow returns different structure, try to parse
                                # fallback:
                                label = resp.get("label", "Unknown")
                                conf = float(resp.get("confidence", 0) * 100)
                        else:
                            pred = demo_predict(str(saved_path))
                            label = pred["label"]
                            conf = pred["confidence"]

                        # annotate image
                        annotated = annotate_image(str(saved_path), label, conf)
                        result_name = f"result_{ts}.jpg"
                        result_path = OUTPUT_DIR / result_name
                        if annotated:
                            annotated.save(result_path)
                        else:
                            # fallback copy
                            Image.open(saved_path).save(result_path)

                        # save history entry
                        entry = {
                            "timestamp": datetime.now().isoformat(timespec="minutes"),
                            "source_name": uploaded.name,
                            "note": patient_note,
                            "label": label,
                            "confidence": round(conf, 1),
                            "result_path": str(result_path),
                        }
                        append_history(entry)

                        # show result
                        st.success(f"{label} — {conf:.1f}%")
                        st.image(result_path, caption="Annotated result", use_column_width=False, width=420)

                        # alerts
                        if "melanoma" in label.lower() or "melanoma" in str(label).lower() or conf > 85:
                            st.error("High suspicion — please consult a dermatologist urgently.")
                        elif conf > 70:
                            st.warning("Moderate-to-high confidence. Seek specialist opinion.")
                        else:
                            st.info("Low confidence — consider monitoring and consulting a professional if concerned.")
                    except Exception as e:
                        st.exception(f"Inference error: {e}")

        with c2:
            if st.button("Save to History", key=f"save_{ts}"):
                # If user wants to save without running inference (e.g., sample)
                annotated = annotate_image(str(saved_path), "Saved (no AI)", 0.0)
                result_name = f"result_saved_{ts}.jpg"
                result_path = OUTPUT_DIR / result_name
                (annotated or Image.open(saved_path)).save(result_path)
                entry = {
                    "timestamp": datetime.now().isoformat(timespec="minutes"),
                    "source_name": uploaded.name,
                    "note": patient_note,
                    "label": "Saved (no AI)",
                    "confidence": 0.0,
                    "result_path": str(result_path),
                }
                append_history(entry)
                st.success("Saved to history.")

        with c3:
            if st.button("Discard", key=f"discard_{ts}"):
                try:
                    saved_path.unlink()
                except Exception:
                    pass
                st.info("Upload discarded.")
    else:
        st.info("Please upload an image to start an AI check.")


# -------------------------
# Page: History
# -------------------------
def page_history():
    st.markdown("<h2 style='color:#182848;'>History</h2>", unsafe_allow_html=True)
    history = load_history()[::-1]  # show latest first
    if not history:
        st.info("No history yet. Run an AI check to populate history.")
        return

    # Controls
    col_a, col_b = st.columns([1, 4])
    with col_a:
        if st.button("Clear all history"):
            clear_history_files()
            st.success("All history cleared. Reload the page.")
            st.experimental_rerun()

    # display grid
    grid_cols = st.columns(3)
    for i, item in enumerate(history):
        col = grid_cols[i % 3]
        with col:
            path = Path(item.get("result_path", ""))
            caption = f"{item.get('label')} — {item.get('confidence')}%"
            time = item.get("timestamp", "")
            note = item.get("note", "")
            if path.exists():
                img_b64 = pil_to_base64(Image.open(path))
                st.markdown(
                    f"""
                    <div class="history-item">
                      <img src="data:image/jpeg;base64,{img_b64}" style="width:100%;border-radius:8px;" />
                      <h4 style="margin:8px 0 4px;color:#182848;">{caption}</h4>
                      <p style="margin:0;font-size:13px;color:#444;">{note}</p>
                      <small style="color:#666;">{time}</small>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.warning(f"Missing file: {path}")

# -------------------------
# Page: Contact
# -------------------------
def page_contact():
    st.markdown("<h2 style='color:#182848;'>Contact / About</h2>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="display:flex;gap:18px;align-items:flex-start;">
          <div style="flex:1">
            <p style="color:#444;">
              This tool is built for educational and triage purposes. It is NOT a diagnostic tool. Always consult
              a qualified dermatologist for medical advice.
            </p>
            <p style="margin-top:12px;color:#444;"><b>Developer:</b> Bobokhonov A. — Samarkand State University</p>
            <p style="margin-top:6px;color:#444;"><b>Email:</b> <a href="mailto:bobokhonov_a@samdu.uz">bobokhonov_a@samdu.uz</a></p>
          </div>
          <div style="width:300px;">
            <div style="padding:12px;border-radius:10px;background:linear-gradient(180deg,#fff,#f7fbff);border:1px solid rgba(75,108,183,0.06);">
              <strong style="color:#182848;">Security note</strong>
              <p style="color:#444;font-size:13px;margin-top:8px;">Do not hard-code API keys into source. Use environment variables on the server.</p>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -------------------------
# Router
# -------------------------
if st.session_state.page == "home":
    page_home()
elif st.session_state.page == "ai":
    page_ai()
elif st.session_state.page == "history":
    page_history()
elif st.session_state.page == "contact":
    page_contact()
else:
    page_home()

st.markdown('<div class="footer">© 2025 Skin Cancer AI Detector — For educational use only.</div>', unsafe_allow_html=True)
