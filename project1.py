import streamlit as st
import pandas as pd
import pdfplumber
import re
from difflib import SequenceMatcher

def redact_account_info(text):
    return re.sub(r'\b\d{10,16}\b', 'XXXXXXXXXXXX', text)

def fuzzy_match(text, target_list, threshold=0.6):
    for target in target_list:
        score = SequenceMatcher(None, text.lower(), target.lower()).ratio()
        if score > threshold:
            return True
    return False

def highlight_risk(val):
    return 'background-color: #ff4b4b; color: white' if val >= 0.7 else ''

st.set_page_config(page_title="Smart Finance Tool", layout="wide")
st.title("🛡️ Smart Finance Tool")

if 'processed_files' not in st.session_state:
    st.session_state.processed_files = set()

with st.sidebar:
    st.header("Settings")
    monthly_limit = st.number_input("Monthly Budget (₹)", value=20000)

st.subheader("📤 Step 1: Upload Statement")
uploaded_file = st.file_uploader("Choose a Bank PDF", type="pdf")

if uploaded_file is not None:
    file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            all_text = ""
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    all_text += extracted
        
        if not all_text.strip():
            st.error("PDF IS empty or contains non-text content.")
            st.stop()
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        st.stop()

    if file_id in st.session_state.processed_files:
        st.warning("⚠️ Duplicate file detected.")
    else:
        st.session_state.processed_files.add(file_id)
        st.success("File processed!")

    all_text = redact_account_info(all_text)
    transaction_pattern = r'(\d{2}[/-]\d{2}[/-]\d{2,4})\s+(.*?)\s+(\d+\.\d{2})'
    matches = re.findall(transaction_pattern, all_text)

    if matches:
        df = pd.DataFrame(matches, columns=['Date', 'Description', 'Amount'])
        df['Amount'] = pd.to_numeric(df["Amount"])
        
        def categorize(desc):
            desc = desc.lower()
            if fuzzy_match(desc, ["swiggy", "zomato", "eat", "restaurant", "starbucks", "kfc", "mcdonalds", "food", "bharatpe"]): return "Food & Dining 🍔"
            if fuzzy_match(desc, ["amazon", "flipkart", "myntra", "ajio", "nykaa", "blinkit", "zepto", "bigbasket", "shopping", "meesho"]): return "Shopping 🛍️"
            if fuzzy_match(desc, ["uber", "ola", "petrol", "shell", "hpcl", "iocl", "metro", "irctc", "indigo", "airindia"]): return "Travel 🚗"
            if fuzzy_match(desc, ["rent", "society", "maintenance", "electricity", "jio", "airtel", "water", "recharge"]): return "Bills & Housing 🏠"
            if fuzzy_match(desc, ["medical", "apollo", "pharmacy", "hospital", "pharmeasy"]): return "Health 🏥"
            return "Others 💸"
                    
        df['Category'] = df['Description'].apply(categorize)  

        total_expenses = df['Amount'].sum()
        usage_pct = (total_expenses / monthly_limit) * 100

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Total Spent", f"₹{total_expenses:.2f}")
        col_b.metric("Budget Limit", f"₹{monthly_limit}")
        col_c.metric("Budget Used", f"{usage_pct:.1f}%", delta=f"{usage_pct - 100:.1f}%" if usage_pct > 100 else None, delta_color="inverse")

        if total_expenses > monthly_limit:
            chart_data = df.groupby("Category")["Amount"].sum()
            culprit = chart_data.idxmax()
            st.error(f"⚠️ **Budget Breached!** Your spending in **{culprit}** is the primary driver.")

        st.divider()
        st.subheader("🛡️ Multi-Factor Risk Scoring")

        risk_list = []
        for index, row in df.iterrows():
            score, reasons, status = 0.0, [], "Pending Review"
            desc_lower, cat = row['Description'].lower(), row['Category']

            if row['Amount'] > 5000:
                if "Housing" in cat: status = "✅ Verified Bill"
                else: score += 0.4; reasons.append("High Amount")
            
            time_match = re.search(r'(\d{2}):(\d{2})', row['Description'])
            if time_match:
                hour = int(time_match.group(1))
                if 0 <= hour <= 5: score += 0.3; reasons.append("Night-time Transaction")

            if any(x in desc_lower for x in ["casino", "bet", "crypto", "unknown", "lotto"]): score += 0.5; reasons.append("High-Risk Merchant")

            if score > 0.0 or status == "✅ Verified Bill":
                risk_list.append({"Date": row['Date'], "Description": row['Description'], "Amount": row['Amount'], "Risk Score": round(score, 2), "Flags": ", ".join(reasons) if reasons else "None", "Status": status})

        if risk_list:
            risk_df = pd.DataFrame(risk_list)
            st.dataframe(
                risk_df.style.map(highlight_risk, subset=['Risk Score']),
                use_container_width=True
            )

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 Category Breakdown")
            chart_data = df.groupby("Category")["Amount"].sum()
            st.bar_chart(chart_data)
        
        with col2:
            st.subheader("🤖 Your Financial Coach")
            if not chart_data.empty:
                top_cat = chart_data.idxmax()
                advice_map = {
                    "Food & Dining 🍔": "High food delivery costs. Set a weekly cap.",
                    "Shopping 🛍️": "E-commerce spending is high. Use the 24-hour rule.",
                    "Travel 🚗": "Commute costs are peaking. Check for monthly passes.",
                    "Bills & Housing 🏠": "Fixed costs are within range.",
                    "Health 🏥": "Medical expenses noted. Keep insurance docs ready.",
                    "Others 💸": "Review smaller UPI transfers."
                }
                st.info(f"💡 AI Insight: {advice_map.get(top_cat, 'Well balanced!')}")

        if usage_pct < 100: st.balloons()
    else:
        st.error("No transactions found.")
else:
    st.info("Awaiting statement upload...")