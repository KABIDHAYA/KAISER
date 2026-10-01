# ReviewSense — Product Review Sentiment Analysis Web App

ReviewSense is an AI-powered product review sentiment analysis web application built with **Streamlit** and **Scikit-Learn**. It features real-time single review inspection with keyword importance extraction, bulk CSV analysis, an interactive analytics dashboard (with Plotly charts & Word Cloud), and full historical record management with search, filters, and CSV export.

---

## 🌟 Key Features

1. **Authentication & User Management**:
   - Secure login and registration using `bcrypt` password hashing.
   - Built-in administrator account powered by Streamlit Secrets.
   - 1-Click Demo Login for instant testing.
2. **Single Review Analysis**:
   - Real-time classification: **Positive**, **Negative**, or **Neutral**.
   - Confidence percentage meter.
   - Extracted key influential words with positive/negative weighting badges.
3. **Bulk CSV Processing**:
   - Upload any `.csv` or `.txt` file containing a `review` header or plain one-review-per-line text.
   - Real-time batch classification with progress tracking and summary statistics.
   - Instant export of bulk analysis results to CSV via `st.download_button`.
4. **Interactive Dashboard**:
   - Sentiment distribution donut chart (interactive Plotly visualization).
   - Top positive and negative keyword frequency bar charts.
   - Customer feedback Word Cloud.
   - Quick feed of recent analyses.
5. **History & Management**:
   - Persistent storage per user in SQLite (`analysis_history`).
   - Real-time search by review text or keywords.
   - Filter by sentiment and source (Single / Bulk).
   - Individual item deletion and "Clear All" action.
   - Full history CSV export.

> [!NOTE]
> **Streamlit Community Cloud File System Persistence:**
> Streamlit Community Cloud runs apps inside ephemeral containers. While the app automatically initializes the SQLite database (`reviewsense.db`) and tables on startup, data resets whenever the app container reboots or updates. Use the **Export CSV** button in the History tab to archive your analysis records.

---

## 📁 Repository Structure

```
ReviewSense/
├── .streamlit/
│   ├── secrets.toml.example  # Secrets template for Streamlit Cloud
│   └── secrets.toml          # Local secrets (excluded in .gitignore)
├── data/
│   └── reviews.csv           # Training dataset
├── models/
│   ├── sentiment_model.joblib # Trained Logistic Regression classifier
│   └── tfidf_vectorizer.joblib# Trained TF-IDF Vectorizer
├── .gitignore                # Excludes venv, secrets, cache, and .db files
├── app.py                    # Main Streamlit web application
├── train.py                  # Standalone model training script
├── requirements.txt          # Pinned production dependencies
└── README.md                 # Project documentation
```

---

## 🛠 Local Setup & Running Locally

### 1. Clone the repository
```bash
git clone https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPO_NAME>.git
cd <YOUR_REPO_NAME>
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
```

### 3. Install required dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure local secrets (Optional)
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

### 5. (Optional) Re-train the Machine Learning Model
The model artifacts are already included under `models/`. If you want to retrain:
```bash
python train.py
```

### 6. Run the Streamlit application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🚀 Deployment on Streamlit Community Cloud

### Step 1: Push Code to GitHub
```bash
# 1. Initialize git
git init

# 2. Stage all files (model artifacts are included; secrets & db are ignored)
git add .

# 3. Commit your changes
git commit -m "Deploy ReviewSense to Streamlit Community Cloud"

# 4. Set main branch
git branch -M main

# 5. Link your GitHub repository
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPO_NAME>.git

# 6. Push to GitHub
git push -u origin main
```

### Step 2: Deploy on Streamlit Community Cloud (`share.streamlit.io`)
1. Log in to [Streamlit Community Cloud](https://share.streamlit.io/) with your GitHub account.
2. Click the **"New app"** (or **"Create app"**) button.
3. In the deployment form:
   - **Repository:** Select your repository (`<YOUR_GITHUB_USERNAME>/<YOUR_REPO_NAME>`).
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Click **"Advanced settings..."** before deploying:
   - **Python version:** Select **`3.11`**.
   - **Secrets:** Copy and paste the contents of `.streamlit/secrets.toml.example`:
     ```toml
     admin_email = "admin@reviewsense.ai"
     admin_password = "AdminSecurePassword123!"
     admin_name = "System Administrator"
     secret_key = "reviewsense-production-secret-key-change-me"
     ```
5. Click **"Deploy!"**.
6. Streamlit Cloud will install dependencies from `requirements.txt`, load the pre-trained model from `models/`, and provide you with a live public URL (e.g., `https://<your-app-name>.streamlit.app`).
