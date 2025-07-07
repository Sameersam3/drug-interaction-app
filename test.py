import streamlit as st
import pandas as pd

# === Load & Preprocess Dataset ===
df = pd.read_csv(r'D:\web project\drug interaction\data\db_drug_interactions.csv')

# Clean column names
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
        return 'severe'
    elif any(word in text for word in moderate):
        return 'moderate'
    elif any(word in text for word in mild):
        return 'mild'
    else:
        return 'unknown'

df['severity'] = df['interaction_description'].apply(map_severity)

# === Get unique sorted drug list ===
all_drugs = sorted(set(df['drug_1'].unique()) | set(df['drug_2'].unique()))

# === Streamlit App UI ===
st.set_page_config(page_title="Clinical Drug Interaction Checker", layout="centered")

st.title("💊 Clinical Drug Interaction Checker")
st.markdown("Select two drugs below to check for possible clinical interactions:")

# Dropdown inputs
drug1 = st.selectbox("Select Drug 1", all_drugs, index=0)
drug2 = st.selectbox("Select Drug 2", all_drugs, index=1)

# Button
if st.button("Check Interaction"):
    d1, d2 = drug1.lower().strip(), drug2.lower().strip()
    result = df[
        ((df['drug_1'] == d1) & (df['drug_2'] == d2)) |
        ((df['drug_1'] == d2) & (df['drug_2'] == d1))
    ]

    if not result.empty:
        st.subheader("⚠️ Interaction(s) Found")
        for _, row in result.iterrows():
            severity = row['severity'].capitalize()
            if severity == 'Severe':
                color = '🔴'
            elif severity == 'Moderate':
                color = '🟠'
            elif severity == 'Mild':
                color = '🟢'
            else:
                color = '🔵'
            st.markdown(f"{color} **{severity}** — {row['interaction_description']}")
    else:
        st.success("✅ No known interaction between the selected drugs.")
