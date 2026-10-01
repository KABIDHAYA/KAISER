"""ReviewSense — Sentiment Analysis Web Application
Designed for production deployment on Streamlit Community Cloud.
Features:
  - User Authentication (Login, Signup, Demo Login via st.secrets)
  - Single Review Analysis with real-time confidence & keyword weights
  - Bulk CSV Upload (supports "review" header and plain line-by-line files)
  - Interactive Analytics Dashboard (Plotly Pie & Keyword Bar Charts, WordCloud)
  - Historical Record Management with Search, Filters, Delete & CSV Export
"""

import os
import re
import io
import json
import sqlite3
import joblib
import numpy as np
import pandas as pd
import bcrypt
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# ==============================================================================
# 1. PAGE CONFIGURATION & THEME STYLING
# ==============================================================================
st.set_page_config(
    page_title="ReviewSense — Sentiment AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for rich aesthetics and modern typography
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header hero */
    .hero-container {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #2563EB 100%);
        border-radius: 16px;
        padding: 24px 32px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.25);
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
        color: white !important;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        opacity: 0.9;
        margin-top: 6px;
        font-weight: 400;
        color: #E0E7FF !important;
    }
    
    /* Sentiment badges */
    .badge-pill {
        display: inline-flex;
        align-items: center;
        padding: 4px 14px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 0.02em;
    }
    .badge-positive {
        background-color: #ECFDF5;
        color: #065F46;
        border: 1px solid #A7F3D0;
    }
    .badge-negative {
        background-color: #FEF2F2;
        color: #991B1B;
        border: 1px solid #FECACA;
    }
    .badge-neutral {
        background-color: #FFFBEB;
        color: #92400E;
        border: 1px solid #FDE68A;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 18px 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        margin-bottom: 12px;
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #1E293B;
        margin-top: 4px;
    }
    .metric-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Keyword chips */
    .keyword-chip {
        display: inline-block;
        background: #EEF2FF;
        color: #4338CA;
        border: 1px solid #C7D2FE;
        border-radius: 8px;
        padding: 4px 10px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 3px;
    }
    
    /* Ephemeral cloud notice */
    .cloud-notice {
        background: #EFF6FF;
        border-left: 4px solid #3B82F6;
        padding: 10px 14px;
        border-radius: 6px;
        font-size: 0.82rem;
        color: #1E40AF;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. RELATIVE PATHS & CACHED MODEL LOADING
# ==============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "reviewsense.db")

def resolve_model_paths():
    """Locate model and vectorizer using relative paths only."""
    candidate_dirs = [
        os.path.join(BASE_DIR, "models"),
        os.path.join(BASE_DIR, "backend", "ml", "model"),
        os.path.join(BASE_DIR, "ml", "model"),
        os.path.join(os.path.dirname(BASE_DIR), "models"),
        os.path.join(os.path.dirname(BASE_DIR), "ReviewSense", "models"),
    ]
    for c_dir in candidate_dirs:
        m_path = os.path.join(c_dir, "sentiment_model.joblib")
        v_path = os.path.join(c_dir, "tfidf_vectorizer.joblib")
        if os.path.exists(m_path) and os.path.exists(v_path):
            return m_path, v_path
            
    # If not found, run train_model to generate them
    from train import train_model
    return train_model(model_dir=os.path.join(BASE_DIR, "models"))

@st.cache_resource
def load_ml_pipeline():
    """Loads the trained ML model and TF-IDF vectorizer once into memory."""
    model_path, vec_path = resolve_model_paths()
    model = joblib.load(model_path)
    vectorizer = joblib.load(vec_path)
    return model, vectorizer

# Load model & vectorizer
try:
    classifier_model, tfidf_vectorizer = load_ml_pipeline()
except Exception as err:
    st.error(f"Failed to load ML model: {err}")
    st.stop()

def predict_text(text: str):
    """Predicts sentiment, confidence score, and extracted keyword weights."""
    if not text or not str(text).strip():
        return {"sentiment": "Neutral", "confidence": 50.0, "keywords": []}
    
    clean = re.sub(r'[^a-z\s]', '', str(text).lower()).strip()
    vec = tfidf_vectorizer.transform([clean])
    pred_class = classifier_model.predict(vec)[0]
    probas = classifier_model.predict_proba(vec)[0]
    confidence = float(np.round(np.max(probas) * 100, 1))
    
    feature_names = tfidf_vectorizer.get_feature_names_out()
    class_idx = np.where(classifier_model.classes_ == pred_class)[0][0]
    coef = classifier_model.coef_[class_idx]
    nonzero_idx = vec.nonzero()[1]
    
    keywords = []
    for idx in nonzero_idx:
        keywords.append({
            "word": feature_names[idx],
            "weight": round(abs(float(coef[idx])), 3)
        })
    keywords.sort(key=lambda x: x["weight"], reverse=True)
    return {
        "sentiment": pred_class,
        "confidence": confidence,
        "keywords": keywords[:6]
    }

# ==============================================================================
# 3. SQLITE DATABASE INITIALIZATION & OPERATIONS
# ==============================================================================
def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Creates SQLite tables automatically if they do not exist."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            review_text TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            confidence TEXT NOT NULL,
            keywords TEXT NOT NULL,
            analysis_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

# Initialize DB on load
init_database()

# Seed default admin user from st.secrets if configured
def get_secret(key, default=None):
    try:
        return st.secrets[key]
    except Exception:
        return default

ADMIN_EMAIL = get_secret("admin_email", "admin@reviewsense.ai")
ADMIN_PASSWORD = get_secret("admin_password", "AdminSecurePassword123!")
ADMIN_NAME = get_secret("admin_name", "System Administrator")

def ensure_admin_user():
    """Ensure the administrator account from st.secrets exists in the database."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (ADMIN_EMAIL,))
    if not cursor.fetchone():
        hashed = bcrypt.hashpw(ADMIN_PASSWORD.encode('utf-8')[:72], bcrypt.gensalt()).decode('utf-8')
        cursor.execute(
            "INSERT INTO users (email, hashed_password, full_name) VALUES (?, ?, ?)",
            (ADMIN_EMAIL, hashed, ADMIN_NAME)
        )
        conn.commit()
    conn.close()

ensure_admin_user()

def authenticate_user(email, password):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, hashed_password, full_name FROM users WHERE email = ?", (email.strip().lower(),))
    user = cursor.fetchone()
    conn.close()
    if user:
        if bcrypt.checkpw(password.encode('utf-8')[:72], user["hashed_password"].encode('utf-8')):
            return {"id": user["id"], "email": user["email"], "name": user["full_name"]}
    return None

def register_user(email, password, full_name):
    conn = get_db()
    cursor = conn.cursor()
    try:
        hashed = bcrypt.hashpw(password.encode('utf-8')[:72], bcrypt.gensalt()).decode('utf-8')
        cursor.execute(
            "INSERT INTO users (email, hashed_password, full_name) VALUES (?, ?, ?)",
            (email.strip().lower(), hashed, full_name.strip())
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return {"id": user_id, "email": email, "name": full_name}
    except sqlite3.IntegrityError:
        conn.close()
        return None

def save_analysis(user_id, review_text, sentiment, confidence, keywords, analysis_type):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO analysis_history (user_id, review_text, sentiment, confidence, keywords, analysis_type)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, review_text, sentiment, str(confidence), json.dumps(keywords), analysis_type))
    conn.commit()
    conn.close()

def fetch_user_history(user_id, search_term="", sentiment_filter="All", type_filter="All"):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM analysis_history WHERE user_id = ?"
    params = [user_id]
    
    if search_term:
        query += " AND (review_text LIKE ? OR keywords LIKE ?)"
        params.extend([f"%{search_term}%", f"%{search_term}%"])
        
    if sentiment_filter != "All":
        query += " AND sentiment = ?"
        params.append(sentiment_filter)
        
    if type_filter != "All":
        query += " AND analysis_type = ?"
        params.append(type_filter.lower())
        
    query += " ORDER BY created_at DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_history_item(item_id, user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM analysis_history WHERE id = ? AND user_id = ?", (item_id, user_id))
    conn.commit()
    conn.close()

def clear_all_history(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM analysis_history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def parse_reviews_from_file(file_obj):
    content = file_obj.getvalue().decode('utf-8', errors='replace')
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if not lines:
        return []
    try:
        df = pd.read_csv(io.StringIO(content))
        cols_lower = {str(c).lower().strip(): c for c in df.columns}
        for candidate in ['review', 'reviews', 'text', 'review_text', 'content']:
            if candidate in cols_lower:
                return df[cols_lower[candidate]].dropna().astype(str).tolist()
        if len(df.columns) == 1:
            col = df.columns[0]
            extracted = df[col].dropna().astype(str).tolist()
            if len(str(col).split()) > 2:
                extracted = [str(col)] + extracted
            return extracted
    except Exception:
        pass
    return lines

def render_badge(sentiment, confidence=None):
    sent = str(sentiment).capitalize()
    cls = "badge-positive" if sent == "Positive" else "badge-negative" if sent == "Negative" else "badge-neutral"
    icon = "🟢" if sent == "Positive" else "🔴" if sent == "Negative" else "🟡"
    conf_str = f" • {confidence:.1f}%" if confidence is not None else ""
    return f'<span class="badge-pill {cls}">{icon} {sent}{conf_str}</span>'

# ==============================================================================
# 4. LOGIN & REGISTRATION INTERFACE
# ==============================================================================
def render_login_page():
    st.markdown("""
        <div class="hero-container" style="text-align: center; margin-top: 20px;">
            <h1 class="hero-title">ReviewSense</h1>
            <p class="hero-subtitle">Intelligent Product Review Sentiment Analysis & Insights</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        st.markdown("""
            <div class="cloud-notice">
                ℹ️ <strong>Streamlit Cloud Notice:</strong> The environment uses an ephemeral file system. 
                Accounts and analysis records persist during your session and reset on server reboot.
            </div>
        """, unsafe_allow_html=True)
        
        tab_login, tab_signup = st.tabs(["🔑 Sign In", "📝 Create Account"])
        
        with tab_login:
            st.subheader("Welcome Back")
            login_email = st.text_input("Email Address", value=ADMIN_EMAIL, key="login_email")
            login_password = st.text_input("Password", type="password", value=ADMIN_PASSWORD, key="login_password")
            
            col_btn, col_demo = st.columns([1, 1])
            with col_btn:
                if st.button("Sign In", type="primary", use_container_width=True):
                    user = authenticate_user(login_email, login_password)
                    if user:
                        st.session_state.user = user
                        st.success("Successfully logged in!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")
            with col_demo:
                if st.button("⚡ 1-Click Demo Login", use_container_width=True):
                    user = authenticate_user(ADMIN_EMAIL, ADMIN_PASSWORD)
                    if user:
                        st.session_state.user = user
                        st.rerun()
                    else:
                        ensure_admin_user()
                        st.session_state.user = authenticate_user(ADMIN_EMAIL, ADMIN_PASSWORD)
                        st.rerun()
                        
        with tab_signup:
            st.subheader("Register a New Account")
            new_name = st.text_input("Full Name", placeholder="e.g. Alex Morgan", key="signup_name")
            new_email = st.text_input("Email", placeholder="alex@example.com", key="signup_email")
            new_password = st.text_input("Password", type="password", key="signup_password")
            
            if st.button("Create Account", type="primary", use_container_width=True):
                if not new_name or not new_email or not new_password:
                    st.warning("Please fill in all fields.")
                else:
                    user = register_user(new_email, new_password, new_name)
                    if user:
                        st.session_state.user = user
                        st.success("Account created successfully!")
                        st.rerun()
                    else:
                        st.error("An account with this email already exists.")

# ==============================================================================
# 5. AUTHENTICATED USER INTERFACE & NAVIGATION
# ==============================================================================
def render_main_app():
    # Sidebar
    with st.sidebar:
        st.markdown("### 👤 User Profile")
        st.write(f"**Name:** {st.session_state.user.get('name', 'User')}")
        st.write(f"**Email:** {st.session_state.user.get('email', '')}")
        
        if st.button("🚪 Sign Out", use_container_width=True):
            st.session_state.user = None
            st.rerun()
            
        st.markdown("---")
        st.markdown("### ☁️ Cloud Deployment")
        st.info(
            "ReviewSense is running in **Streamlit Community Cloud** mode.\n\n"
            "- Model: Cached TF-IDF + Logistic Regression\n"
            "- DB: SQLite (Ephemeral per container session)\n"
            "- Use the **Export CSV** feature in History to backup your findings!"
        )
        st.markdown("---")
        st.caption("ReviewSense v2.0 • Sentiment AI")

    # Header
    st.markdown("""
    <div class="hero-container">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <h1 class="hero-title">ReviewSense</h1>
                <p class="hero-subtitle">Real-time sentiment intelligence for customer feedback</p>
            </div>
            <div style="text-align: right; margin-top: 10px;">
                <span style="background: rgba(255,255,255,0.2); padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">
                    🟢 ML Pipeline Active
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_single, tab_bulk, tab_dashboard, tab_history = st.tabs([
        "🔍 Single Analysis",
        "📁 Bulk CSV Upload",
        "📊 Analytics Dashboard",
        "📜 History & Records"
    ])

    # TAB 1: SINGLE REVIEW ANALYSIS
    with tab_single:
        st.subheader("Inspect a Customer Review")
        st.write("Type or paste any product review below for instant sentiment classification, confidence scoring, and key term extraction.")
        
        st.markdown("**Quick Test Samples:**")
        c1, c2, c3 = st.columns(3)
        sample_text = ""
        with c1:
            if st.button("🌟 Positive Sample", use_container_width=True):
                sample_text = "Love this product! Excellent build quality and the support was extremely fast and helpful."
        with c2:
            if st.button("⚠️ Neutral Sample", use_container_width=True):
                sample_text = "It's an okay product, does the job but nothing extraordinary. Matches the description."
        with c3:
            if st.button("🚨 Negative Sample", use_container_width=True):
                sample_text = "Terrible experience. The item arrived damaged, broke after two days, and customer service refused to refund."

        review_input = st.text_area(
            "Customer Review Text",
            value=sample_text,
            height=130,
            placeholder="e.g. This headset exceeded my expectations! Sound is crystal clear and battery lasts for days.",
            key="single_review_input"
        )
        
        col_act1, col_act2 = st.columns([1, 4])
        with col_act1:
            analyze_clicked = st.button("🚀 Analyze Sentiment", type="primary", use_container_width=True)
        with col_act2:
            if st.button("Clear Text", use_container_width=False):
                st.session_state.single_review_input = ""
                st.rerun()

        if analyze_clicked:
            if not review_input.strip():
                st.warning("Please enter a review before analyzing.")
            else:
                with st.spinner("Analyzing text sentiment..."):
                    result = predict_text(review_input)
                    save_analysis(
                        user_id=st.session_state.user["id"],
                        review_text=review_input.strip(),
                        sentiment=result["sentiment"],
                        confidence=result["confidence"],
                        keywords=result["keywords"],
                        analysis_type="single"
                    )
                    
                st.markdown("---")
                st.markdown("### Analysis Result")
                res_col1, res_col2 = st.columns([1.2, 2])
                
                with res_col1:
                    st.markdown(f"**Predicted Sentiment:** {render_badge(result['sentiment'], result['confidence'])}", unsafe_allow_html=True)
                    st.markdown(f"**Confidence Level:** `{result['confidence']}%`")
                    st.progress(min(result["confidence"] / 100.0, 1.0))
                    
                with res_col2:
                    st.markdown("**Top Influential Keywords:**")
                    if result["keywords"]:
                        chips_html = "".join([
                            f'<span class="keyword-chip">{kw["word"]} <small>({kw["weight"]})</small></span>'
                            for kw in result["keywords"]
                        ])
                        st.markdown(chips_html, unsafe_allow_html=True)
                    else:
                        st.caption("No strong vocabulary keywords detected in this sample.")
                st.success("✓ Result recorded in your session history!")

    # TAB 2: BULK CSV UPLOAD
    with tab_bulk:
        st.subheader("Bulk Review Processing")
        st.write("Upload a CSV file containing reviews. We automatically parse columns named **'review'**, **'text'**, or **plain line-by-line** files.")
        
        uploaded_file = st.file_uploader(
            "Upload CSV or TXT file",
            type=["csv", "txt"],
            help="Upload files up to 200MB. Handled in-memory for speed."
        )

        if uploaded_file is not None:
            reviews_list = parse_reviews_from_file(uploaded_file)
            st.write(f"📁 **Detected {len(reviews_list)} reviews** from `{uploaded_file.name}`.")
            
            with st.expander("Preview Extracted Reviews (First 5)", expanded=False):
                st.write(pd.DataFrame({"Review Text": reviews_list[:5]}))
                
            if st.button(f"⚡ Analyze All {len(reviews_list)} Reviews", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                bulk_results = []
                pos_count, neg_count, neu_count = 0, 0, 0
                
                total_items = len(reviews_list)
                for idx, text in enumerate(reviews_list):
                    res = predict_text(text)
                    sent = res["sentiment"]
                    if sent == "Positive": pos_count += 1
                    elif sent == "Negative": neg_count += 1
                    else: neu_count += 1
                    
                    bulk_results.append({
                        "Review": text,
                        "Sentiment": sent,
                        "Confidence": f"{res['confidence']}%",
                        "Keywords": ", ".join([k["word"] for k in res["keywords"]])
                    })
                    
                    save_analysis(
                        user_id=st.session_state.user["id"],
                        review_text=text,
                        sentiment=sent,
                        confidence=res["confidence"],
                        keywords=res["keywords"],
                        analysis_type="bulk"
                    )
                    
                    if (idx + 1) % max(1, total_items // 20) == 0 or (idx + 1) == total_items:
                        progress_bar.progress((idx + 1) / total_items)
                        status_text.text(f"Processing review {idx + 1} of {total_items}...")
                        
                status_text.text("✓ Bulk analysis completed!")
                
                st.markdown("### Bulk Analysis Summary")
                m1, m2, m3, m4 = st.columns(4)
                m1.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Total Analyzed</div>
                        <div class="metric-value">{total_items}</div>
                    </div>
                """, unsafe_allow_html=True)
                m2.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Positive</div>
                        <div class="metric-value" style="color:#10B981;">{pos_count} <small style="font-size:0.9rem">({(pos_count/total_items*100):.1f}%)</small></div>
                    </div>
                """, unsafe_allow_html=True)
                m3.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Negative</div>
                        <div class="metric-value" style="color:#EF4444;">{neg_count} <small style="font-size:0.9rem">({(neg_count/total_items*100):.1f}%)</small></div>
                    </div>
                """, unsafe_allow_html=True)
                m4.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Neutral</div>
                        <div class="metric-value" style="color:#F59E0B;">{neu_count} <small style="font-size:0.9rem">({(neu_count/total_items*100):.1f}%)</small></div>
                    </div>
                """, unsafe_allow_html=True)
                
                results_df = pd.DataFrame(bulk_results)
                st.dataframe(results_df, use_container_width=True)
                
                csv_export = results_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Export Bulk Results to CSV",
                    data=csv_export,
                    file_name="reviewsense_bulk_analysis.csv",
                    mime="text/csv",
                    type="primary"
                )

    # TAB 3: ANALYTICS DASHBOARD
    with tab_dashboard:
        st.subheader("Analytics & Sentiment Intelligence Dashboard")
        user_records = fetch_user_history(st.session_state.user["id"])
        
        if not user_records:
            st.info("No reviews analyzed yet. Analyze a single review, upload a CSV, or load the built-in demo dataset below.")
            if st.button("🚀 Load Sample Reviews Dataset", type="primary"):
                sample_data = [
                    ("Absolutely fantastic quality! Best purchase I have made all year.", "Positive"),
                    ("Fast shipping and great customer support, very happy.", "Positive"),
                    ("Works as advertised, solid construction and reliable.", "Positive"),
                    ("Average item. Decent for the price but nothing special.", "Neutral"),
                    ("It is okay, serves its purpose reasonably well.", "Neutral"),
                    ("Broke after two days of use. Cheap plastic and terrible support.", "Negative"),
                    ("Waste of money. Does not work as described, do not buy.", "Negative"),
                    ("Horrible experience, arrived damaged and stopped working.", "Negative")
                ]
                for text, _ in sample_data:
                    res = predict_text(text)
                    save_analysis(
                        user_id=st.session_state.user["id"],
                        review_text=text,
                        sentiment=res["sentiment"],
                        confidence=res["confidence"],
                        keywords=res["keywords"],
                        analysis_type="single"
                    )
                st.success("Loaded demo dataset! Refreshing dashboard...")
                st.rerun()
        else:
            total = len(user_records)
            pos = sum(1 for r in user_records if r["sentiment"] == "Positive")
            neg = sum(1 for r in user_records if r["sentiment"] == "Negative")
            neu = sum(1 for r in user_records if r["sentiment"] == "Neutral")
            
            confidences = []
            for r in user_records:
                try: confidences.append(float(r["confidence"]))
                except Exception: pass
            avg_conf = np.mean(confidences) if confidences else 0.0
            
            k1, k2, k3, k4, k5 = st.columns(5)
            k1.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Total Analyzed</div>
                    <div class="metric-value">{total}</div>
                </div>
            """, unsafe_allow_html=True)
            k2.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Positive</div>
                    <div class="metric-value" style="color:#10B981;">{(pos/total*100):.1f}%</div>
                </div>
            """, unsafe_allow_html=True)
            k3.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Negative</div>
                    <div class="metric-value" style="color:#EF4444;">{(neg/total*100):.1f}%</div>
                </div>
            """, unsafe_allow_html=True)
            k4.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Neutral</div>
                    <div class="metric-value" style="color:#F59E0B;">{(neu/total*100):.1f}%</div>
                </div>
            """, unsafe_allow_html=True)
            k5.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Avg Confidence</div>
                    <div class="metric-value">{avg_conf:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            c_chart1, c_chart2 = st.columns([1.1, 1.4])
            
            with c_chart1:
                st.markdown("#### Sentiment Distribution")
                pie_df = pd.DataFrame({
                    "Sentiment": ["Positive", "Negative", "Neutral"],
                    "Count": [pos, neg, neu]
                })
                fig_pie = px.pie(
                    pie_df,
                    names="Sentiment",
                    values="Count",
                    hole=0.45,
                    color="Sentiment",
                    color_discrete_map={
                        "Positive": "#10B981",
                        "Negative": "#EF4444",
                        "Neutral": "#F59E0B"
                    }
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#FFFFFF', width=2)))
                fig_pie.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=True, height=330)
                st.plotly_chart(fig_pie, use_container_width=True)
                
            with c_chart2:
                st.markdown("#### Word Cloud of Customer Feedback")
                all_text = " ".join([r["review_text"] for r in user_records])
                if all_text.strip():
                    try:
                        wc = WordCloud(
                            width=650,
                            height=330,
                            background_color="#FFFFFF",
                            colormap="viridis",
                            stopwords=set(["the", "and", "is", "it", "this", "to", "was", "for", "of", "in", "with", "a", "an", "on", "my", "i", "product"])
                        ).generate(all_text)
                        fig_wc, ax = plt.subplots(figsize=(6.5, 3.3))
                        ax.imshow(wc, interpolation="bilinear")
                        ax.axis("off")
                        plt.tight_layout(pad=0)
                        st.pyplot(fig_wc)
                        plt.close(fig_wc)
                    except Exception as e:
                        st.write(f"Word cloud rendering: {e}")
                else:
                    st.caption("No text available for word cloud.")

            st.markdown("---")
            st.markdown("#### Keyword Influence Frequency")
            kw_col1, kw_col2 = st.columns(2)
            
            pos_words = {}
            neg_words = {}
            for r in user_records:
                try:
                    kw_data = json.loads(r["keywords"])
                    for item in kw_data:
                        w = item["word"] if isinstance(item, dict) else item
                        if r["sentiment"] == "Positive":
                            pos_words[w] = pos_words.get(w, 0) + 1
                        elif r["sentiment"] == "Negative":
                            neg_words[w] = neg_words.get(w, 0) + 1
                except Exception:
                    pass
                    
            with kw_col1:
                st.markdown("##### 🟢 Top Positive Keywords")
                if pos_words:
                    sorted_pos = sorted(pos_words.items(), key=lambda x: x[1], reverse=True)[:8]
                    df_pos = pd.DataFrame(sorted_pos, columns=["Keyword", "Occurrences"])
                    fig_pos = px.bar(
                        df_pos,
                        x="Occurrences",
                        y="Keyword",
                        orientation="h",
                        color_discrete_sequence=["#10B981"]
                    )
                    fig_pos.update_layout(yaxis=dict(autorange="reversed"), margin=dict(t=5, b=5, l=10, r=10), height=280)
                    st.plotly_chart(fig_pos, use_container_width=True)
                else:
                    st.caption("No positive keywords recorded yet.")
                    
            with kw_col2:
                st.markdown("##### 🔴 Top Negative Keywords")
                if neg_words:
                    sorted_neg = sorted(neg_words.items(), key=lambda x: x[1], reverse=True)[:8]
                    df_neg = pd.DataFrame(sorted_neg, columns=["Keyword", "Occurrences"])
                    fig_neg = px.bar(
                        df_neg,
                        x="Occurrences",
                        y="Keyword",
                        orientation="h",
                        color_discrete_sequence=["#EF4444"]
                    )
                    fig_neg.update_layout(yaxis=dict(autorange="reversed"), margin=dict(t=5, b=5, l=10, r=10), height=280)
                    st.plotly_chart(fig_neg, use_container_width=True)
                else:
                    st.caption("No negative keywords recorded yet.")

            st.markdown("---")
            st.markdown("#### Recent User Analyses")
            recent = user_records[:6]
            for item in recent:
                with st.container():
                    rc1, rc2 = st.columns([3, 1])
                    with rc1:
                        st.markdown(f"**\"{item['review_text']}\"**")
                        st.caption(f"Type: {item['analysis_type'].capitalize()} • Recorded: {item['created_at']}")
                    with rc2:
                        st.markdown(render_badge(item["sentiment"], float(item["confidence"])), unsafe_allow_html=True)
                    st.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    # TAB 4: HISTORY & EXPORT
    with tab_history:
        st.subheader("Analysis History & Data Management")
        st.markdown("""
            <div class="cloud-notice">
                💾 <strong>Cloud Persistence Note:</strong> Streamlit Community Cloud sessions are hosted in temporary containers. 
                Data resets on container reboot. Use <strong>Export CSV</strong> to save and archive your analysis history.
            </div>
        """, unsafe_allow_html=True)
        
        ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 1, 1])
        with ctrl_col1:
            search_query = st.text_input("🔍 Search Reviews or Keywords", placeholder="Type to search...", key="history_search")
        with ctrl_col2:
            sentiment_select = st.selectbox("Filter Sentiment", ["All", "Positive", "Negative", "Neutral"], key="history_sentiment_filter")
        with ctrl_col3:
            type_select = st.selectbox("Filter Source", ["All", "Single", "Bulk"], key="history_type_filter")

        filtered_history = fetch_user_history(
            user_id=st.session_state.user["id"],
            search_term=search_query,
            sentiment_filter=sentiment_select,
            type_filter=type_select
        )
        
        act_col1, act_col2 = st.columns([1, 1])
        with act_col1:
            if filtered_history:
                export_df = pd.DataFrame([{
                    "ID": item["id"],
                    "Review": item["review_text"],
                    "Sentiment": item["sentiment"],
                    "Confidence": f"{item['confidence']}%",
                    "Keywords": item["keywords"],
                    "Analysis Type": item["analysis_type"],
                    "Date": item["created_at"]
                } for item in filtered_history])
                
                csv_bytes = export_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"📥 Export {len(filtered_history)} Records as CSV",
                    data=csv_bytes,
                    file_name="reviewsense_history_export.csv",
                    mime="text/csv",
                    type="primary",
                    use_container_width=True
                )
        with act_col2:
            with st.expander("🗑️ Clear All History"):
                st.warning("Are you sure? This will delete all your analysis records.")
                if st.button("Confirm Clear All Records", type="secondary", use_container_width=True):
                    clear_all_history(st.session_state.user["id"])
                    st.success("All records cleared.")
                    st.rerun()
                    
        st.markdown("---")
        
        if not filtered_history:
            st.info("No matching history records found.")
        else:
            st.write(f"Showing **{len(filtered_history)}** records:")
            for record in filtered_history:
                with st.container():
                    col_row, col_del = st.columns([5, 1])
                    with col_row:
                        st.markdown(f"**{record['review_text']}**")
                        st.markdown(f"{render_badge(record['sentiment'], float(record['confidence']))} • <small style='color:gray;'>Type: {record['analysis_type'].capitalize()} • {record['created_at']}</small>", unsafe_allow_html=True)
                        try:
                            kws = json.loads(record["keywords"])
                            if kws:
                                kw_chips = "".join([f'<span class="keyword-chip">{k["word"] if isinstance(k, dict) else k}</span>' for k in kws])
                                st.markdown(kw_chips, unsafe_allow_html=True)
                        except Exception:
                            pass
                    with col_del:
                        if st.button("🗑️ Delete", key=f"del_{record['id']}", use_container_width=True):
                            delete_history_item(record["id"], st.session_state.user["id"])
                            st.rerun()
                    st.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

# ==============================================================================
# 6. APPLICATION ENTRY POINT
# ==============================================================================
def main():
    if "user" not in st.session_state:
        st.session_state.user = None

    if not st.session_state.user:
        render_login_page()
    else:
        render_main_app()

if __name__ == '__main__':
    main()
