# 🚛 Moving Inventory Audits — Monthly Material Inventory Audit

A clean, Streamlit web app for monthly inventory audits across four moving trucks.

## Features

- **Four truck tabs** — enter items independently per truck
- **Live editable table** — fix quantities or remove rows after entry
- **One-click report** — generates a formatted, human-readable audit report
- **Download options** — export as `.txt` (formatted report) or `.csv` (spreadsheet)


## 🖥 Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```


## Project structure

```
moving_inventory_audit/
├── app.py            # Main Streamlit application
├── requirements.txt  # Python dependencies
└── README.md         # This file
```


## How to use

1. Enter the **Auditor Name** and **Audit Date** at the top.
2. Click each **Truck tab** and add items with their quantities using the form.
3. Edit or delete rows directly in the table if needed.
4. Click **Generate Audit Report** to preview the formatted report.
5. Download as `.txt` (clean printable report) or `.csv` (for spreadsheets).
