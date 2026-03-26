import streamlit as st
import pandas as pd
from datetime import datetime
import io

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Good Bye Garbage Co. Inventory Audit",
    page_icon="🚛",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
}

h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
}

.block-container { padding-top: 2rem; }

.truck-header {
    background: #1a1a2e;
    color: #f0a500;
    padding: 0.6rem 1.2rem;
    border-radius: 6px;
    font-family: 'Syne', sans-serif;
    font-size: 1.15rem;
    font-weight: 800;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
}

.audit-box {
    background: #f9f6f0;
    border: 2px solid #1a1a2e;
    border-radius: 8px;
    padding: 1.5rem;
    margin-top: 1rem;
    font-family: 'DM Mono', monospace;
    white-space: pre-wrap;
    font-size: 0.82rem;
    line-height: 1.7;
    color: #1a1a2e;
}

.stButton > button {
    background-color: #f0a500;
    color: #1a1a2e;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    border: none;
    border-radius: 6px;
    padding: 0.5rem 1.4rem;
}
.stButton > button:hover {
    background-color: #1a1a2e;
    color: #f0a500;
}

div[data-testid="stDownloadButton"] > button {
    background-color: #1a1a2e;
    color: #f0a500;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    border: none;
    border-radius: 6px;
}
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
TRUCKS = ["Truck 1", "Truck 2", "Truck 3", "Truck 4"]

if "inventory" not in st.session_state:
    # { "Truck 1": [ {"item": ..., "qty": ...}, ... ], ... }
    st.session_state.inventory = {t: [] for t in TRUCKS}

if "auditor" not in st.session_state:
    st.session_state.auditor = ""

if "audit_date" not in st.session_state:
    st.session_state.audit_date = datetime.today()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🚛 Monthly Inventory Audit")
st.markdown("**Moving Company — Truck Inventory Tracker**")
st.divider()

# ── Meta info ─────────────────────────────────────────────────────────────────
col_a, col_b = st.columns(2)
with col_a:
    st.session_state.auditor = st.text_input("Auditor Name", value=st.session_state.auditor, placeholder="Your name")
with col_b:
    st.session_state.audit_date = st.date_input("Audit Date", value=st.session_state.audit_date)

st.divider()

# ── Truck tabs ────────────────────────────────────────────────────────────────
tabs = st.tabs([f"🚛 {t}" for t in TRUCKS])

for i, tab in enumerate(tabs):
    truck = TRUCKS[i]
    with tab:
        st.markdown(f'<div class="truck-header">📦 {truck} — Item Entry</div>', unsafe_allow_html=True)

        with st.form(key=f"form_{truck}", clear_on_submit=True):
            c1, c2, c3 = st.columns([4, 2, 1])
            with c1:
                item_name = st.text_input("Item Name", placeholder="e.g. Moving blankets", key=f"item_{truck}")
            with c2:
                qty = st.number_input("Quantity", min_value=0, step=1, key=f"qty_{truck}")
            with c3:
                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("➕ Add")

            if submitted:
                if item_name.strip():
                    st.session_state.inventory[truck].append(
                        {"Item": item_name.strip(), "Quantity": int(qty)}
                    )
                    st.success(f"Added: {item_name.strip()} × {qty}")
                else:
                    st.warning("Please enter an item name.")

        # ── Current list for this truck ───────────────────────────────────────
        items = st.session_state.inventory[truck]
        if items:
            df = pd.DataFrame(items)
            df.index = df.index + 1

            edited = st.data_editor(
                df,
                use_container_width=True,
                num_rows="dynamic",
                key=f"editor_{truck}",
            )
            # Sync edits back
            st.session_state.inventory[truck] = edited.to_dict("records")

            total = sum(r.get("Quantity", 0) or 0 for r in st.session_state.inventory[truck])
            st.markdown(f"**Total items counted: `{total}`**")

            if st.button(f"🗑 Clear {truck}", key=f"clear_{truck}"):
                st.session_state.inventory[truck] = []
                st.rerun()
        else:
            st.info("No items added yet for this truck.")

st.divider()

# ── Generate report ───────────────────────────────────────────────────────────
def build_report_text() -> str:
    date_str = st.session_state.audit_date.strftime("%B %d, %Y")
    auditor = st.session_state.auditor.strip() or "N/A"
    lines = []
    lines.append("=" * 58)
    lines.append("       MONTHLY INVENTORY AUDIT REPORT")
    lines.append("=" * 58)
    lines.append(f"  Date     : {date_str}")
    lines.append(f"  Auditor  : {auditor}")
    lines.append(f"  Company  : Moving Company")
    lines.append("=" * 58)

    grand_total = 0
    for truck in TRUCKS:
        items = st.session_state.inventory[truck]
        lines.append("")
        lines.append(f"  ── {truck.upper()} ──────────────────────────────────")
        if not items:
            lines.append("    (no items recorded)")
        else:
            lines.append(f"    {'ITEM':<35} {'QTY':>6}")
            lines.append(f"    {'-'*35} {'------':>6}")
            truck_total = 0
            for row in items:
                name = str(row.get("Item", "")).strip()
                qty = int(row.get("Quantity", 0) or 0)
                truck_total += qty
                lines.append(f"    {name:<35} {qty:>6}")
            lines.append(f"    {'─'*35} {'──────':>6}")
            lines.append(f"    {'TRUCK TOTAL':<35} {truck_total:>6}")
            grand_total += truck_total

    lines.append("")
    lines.append("=" * 58)
    lines.append(f"  {'GRAND TOTAL (ALL TRUCKS)':<34} {grand_total:>6}")
    lines.append("=" * 58)
    lines.append(f"\n  Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 58)
    return "\n".join(lines)


def build_csv() -> str:
    rows = []
    for truck in TRUCKS:
        for row in st.session_state.inventory[truck]:
            rows.append({
                "Truck": truck,
                "Item": row.get("Item", ""),
                "Quantity": row.get("Quantity", 0),
                "Audit Date": st.session_state.audit_date.strftime("%Y-%m-%d"),
                "Auditor": st.session_state.auditor.strip(),
            })
    if not rows:
        return "Truck,Item,Quantity,Audit Date,Auditor\n"
    return pd.DataFrame(rows).to_csv(index=False)


col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    if st.button("📋 Generate Audit Report"):
        report = build_report_text()
        st.markdown('<div class="audit-box">' + report.replace("\n", "<br>") + '</div>', unsafe_allow_html=True)
        st.session_state["last_report"] = report

# Always show download buttons if a report was generated
if "last_report" in st.session_state:
    with col2:
        st.download_button(
            label="⬇️ Download .txt",
            data=st.session_state["last_report"],
            file_name=f"audit_{st.session_state.audit_date.strftime('%Y%m')}.txt",
            mime="text/plain",
        )
    with col3:
        st.download_button(
            label="⬇️ Download .csv",
            data=build_csv(),
            file_name=f"audit_{st.session_state.audit_date.strftime('%Y%m')}.csv",
            mime="text/csv",
        )
