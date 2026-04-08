# Smart Finance Tool - Expense & Risk Analyzer
A Streamlit-based FinTech tool that analyzes bank statement PDFs, categorizes expenses, and detects suspicious transactions using a weighted risk system.

## Try it Yourself
1. Open the app:  
https://smart-finance-tool.streamlit.app/

2. Download any demo PDF below  

3. Upload it in the app to see analysis  

## Sample Bank Statements

- [Normal User](demo_normal_user.pdf)  
- [High Spending Pattern](demo_high_spender.pdf)  
- [Suspicious Transactions](demo_bank_statement.pdf)  

Note: These are demo statements created for testing purposes only.

## Prototype

![Step 1](FIRSTPAGE.png)

![Analysis Output](SECONDPAGE.png)

![Final Output](image.png)


## Overview

This project was developed in Data Engineering and Predictive Logic basics.

It focuses on solving the problem of false alerts in financial systems by using context-aware risk scoring instead of simple amount-based rules.


## Key Features

1. Automated Parsing  
   Uses pdfplumber and regex to convert unstructured PDF data into structured Pandas DataFrames.

2. Data Masking  
   Automatically hides sensitive information like account numbers.

3. Fuzzy Matching  
   Uses difflib to categorize inconsistent transaction names  
   (e.g., "ZOMATO-PAY-123" → "Food & Dining")

4. Weighted Risk Engine  
   Calculates risk score based on multiple factors:
   - Amount (Weight: 0.4)  
   - Transaction Time (Weight: 0.3 – flags late night activity)  
   - Merchant Category (Weight: 0.5 – flags risky merchants like gambling)

5. False Positive Handling  
   Recognizes recurring transactions (like rent) to avoid unnecessary alerts.

## Tech Stack

- Language: Python 3.12  
- Frontend: Streamlit  
- Data Processing: Pandas  
- PDF Extraction: pdfplumber  
- Logic: Regex + Rule-based system  

## Purpose

The goal of this project is to demonstrate how financial systems can move beyond simple rule-based alerts and use contextual logic to improve accuracy and user experience.


## Note

This is a prototype built for learning and experimentation purposes.
