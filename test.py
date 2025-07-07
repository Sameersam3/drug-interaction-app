import streamlit as st
import pandas as pd

# === Load & Preprocess Dataset ===
df = pd.read_csv('data/db_drug_interactions.csv')

# Rename and clean columns
df.rename(columns={
    'Drug 1': 'drug_1',
    'Drug 2': 'drug_2',
    'Interaction Description': 'interaction_description'
}, inplace=True)

df['drug_1'] = df['drug_1'].str.lower().str.strip()
df['drug_2'] = df['drug_2'].str.lower().str.strip()
df['interaction_description'] = df['interaction_description'].str.strip()

# === Add Severity Detection ===
def map_severity(text):
    text = text.lower()
    severe = ['death', 'cardiac arrest', 'coma', 'seizure', 'anaphylaxis', 'stroke', 'renal failure', 'hepatotoxicity']
    moderate = ['hypokalemia', 'hypokalemic', 'toxicity', 'arrhythmia', 'bleeding', 'neutropenia', 'qt prolongation']
    mild = ['nausea', 'headache', 'dizziness', 'fatigue', 'vomiting', 'diarrhea']

    if any(word in text for word in severe):
        return 'Severe'
    elif any(word in text for word in moderate):
        return 'Moderate'
    elif any(word in text for word in mild):
        return 'Mild'
    else:
        return 'Unknown'

df['severity'] = df['interaction_description'].apply(map_severity)

# === Get unique sorted drug list ===
all_drugs = sorted(set(df['drug_1'].unique()) | set(df['drug_2'].unique()))

# === Streamlit UI Config ===
st.set_page_config(page_title="Drug Interaction Checker", layout="centered")

# === Custom CSS for styling ===
st.markdown("""
    <style>
        .main-title {
            font-size: 36px;
            font-weight: bold;
            color: #2c3e50;
            text-align: center;
        }
        .subtext {
            text-align: center;
            font-size: 18px;
            color: #555;
            margin-bottom: 30px;
        }
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 10px;
            font-weight: bold;
            margin-top: 5px;
            font-size: 14px;
        }
        .Severe { background-color: #ff4c4c; color: white; }
        .Moderate { background-color: #ffa500; color: white; }
        .Mild { background-color: #2ecc71; color: white; }
        .Unknown { background-color: #6c757d; color: white; }
    </style>
""", unsafe_allow_html=True)

# === Header ===
st.markdown('<div class="main-title">💊 Drug Interaction Checker</div>', unsafe_allow_html=True)
st.markdown('<div class="subtext">Check if two drugs have any known interaction and see its severity.</div>', unsafe_allow_html=True)

# === Drug Selection Dropdowns ===
col1, col2 = st.columns(2)
with col1:
    drug1 = st.selectbox("Select Drug 1", all_drugs)
with col2:
    drug2 = st.selectbox("Select Drug 2", all_drugs)

# === Check Button ===
if st.button("🔍 Check Interaction"):
    d1 = drug1.lower().strip()
    d2 = drug2.lower().strip()

    result = df[
        ((df['drug_1'] == d1) & (df['drug_2'] == d2)) |
        ((df['drug_1'] == d2) & (df['drug_2'] == d1))
    ]

    if not result.empty:
        st.subheader("⚠️ Interaction(s) Found")
        for _, row in result.iterrows():
            severity = row['severity']
            badge = f'<span class="badge {severity}">{severity}</span>'
            st.markdown(f"- {row['interaction_description']}<br>{badge}", unsafe_allow_html=True)
    else:
        st.success("✅ No known interaction between the selected drugs.")
