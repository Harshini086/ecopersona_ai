# 🌍 EcoPersona AI

> An AI-powered gamified web app that analyzes your lifestyle, predicts environmental impact,
> assigns you a persona, and delivers smart personalized nudges — built with Streamlit + scikit-learn.

---

## 📁 File Structure

```
ecopersona_ai/
│
├── app.py              ← Main Streamlit UI (entry point)
├── model.py            ← Decision Tree ML model (train + predict)
├── utils.py            ← CO₂ estimation, scoring, persona, nudges
├── game.py             ← Points, levels, streaks, badge system
├── data.csv            ← Synthetic training dataset (60 rows)
├── requirements.txt    ← Python dependencies
└── README.md           ← This file
```

---

## ⚙️ Tech Stack

| Layer       | Library            |
|-------------|--------------------|
| UI          | Streamlit 1.32     |
| ML Model    | scikit-learn 1.4   |
| Data        | pandas 2.2         |
| Charts      | Plotly 5.20        |
| Viz         | Matplotlib 3.8     |
| Numerics    | NumPy 1.26         |

---

## 🚀 How to Run — Step by Step

### Step 1 — Prerequisites

Make sure you have **Python 3.9 or higher** installed.

```bash
python --version
# Should print: Python 3.9.x or higher
```

If not installed, download from https://www.python.org/downloads/

---

### Step 2 — Clone / Download the Project

If you have git:
```bash
git clone <your-repo-url>
cd ecopersona_ai
```

Or simply unzip the downloaded folder and open a terminal inside it:
```bash
cd path/to/ecopersona_ai
```

---

### Step 3 — Create a Virtual Environment (Recommended)

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

You should see `(venv)` appear in your terminal prompt.

---

### Step 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all required packages. It may take 1–2 minutes on first run.

---

### Step 5 — Run the App

```bash
streamlit run app.py
```

Streamlit will automatically open your browser at:
```
http://localhost:8501
```

---

### Step 6 — Use the App

1. **Configure your lifestyle** in the left sidebar:
   - Choose your transport mode
   - Set your weekly travel distance
   - Select your food habits
   - Pick your shopping frequency
   - Adjust your monthly electricity usage

2. **Click "🔍 Analyze My EcoPersona"**

3. **Explore your results:**
   - 📊 Dashboard — Eco Score, Impact Level, CO₂, EcoPoints
   - 🌿 Score & Persona — Donut chart, category breakdown, your persona card
   - 📈 Future Projection — 12-month CO₂ forecast chart
   - 💡 Smart Nudges — 3 personalized, measurable action suggestions
   - 🏅 Badges & Rewards — Unlock achievements based on your habits
   - 🔍 Model Insights — Feature importance from the Decision Tree

---

## 🧠 How the ML Model Works

1. **Dataset** (`data.csv`): 60 synthetic records covering 5 lifestyle features
2. **Encoding**: Categorical inputs are mapped to integers via lookup dictionaries
3. **Model**: `DecisionTreeClassifier` (max_depth=6) from scikit-learn
4. **Train/Test Split**: 80/20 with stratification
5. **Output**: Predicts impact level → `Low`, `Medium`, or `High`
6. **Probability**: Confidence scores shown in the Persona card

---

## 🎮 Game System

| Element     | Description                                          |
|-------------|------------------------------------------------------|
| EcoPoints   | Score × 12 + impact bonus (Low=+300, Med=+150)       |
| Levels      | Beginner → Aware Explorer → Green Citizen → Eco Champion → Planet Protector |
| Badges      | 8 badges unlocked by specific lifestyle conditions   |
| Streaks     | 7-day weekly streak tracker (simulated)              |

---

## 🛠️ Troubleshooting

**`ModuleNotFoundError`** — Run `pip install -r requirements.txt` again with venv active.

**`streamlit: command not found`** — Use `python -m streamlit run app.py` instead.

**Port already in use** — Run on a different port:
```bash
streamlit run app.py --server.port 8502
```

**Blank page in browser** — Hard refresh with `Ctrl+Shift+R` (or `Cmd+Shift+R` on Mac).

---

## 📦 Deactivating the Virtual Environment

When you're done:
```bash
deactivate
```

---

## 📄 License

MIT — free to use, modify, and distribute.
