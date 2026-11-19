import calendar
import html
from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from database import (
    create_table,
    add_expense,
    get_expenses,
    update_expense,
    delete_expense,
    set_budget,
    get_budget,
)

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="NOVA | Expense Tracker",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

create_table()

# =====================================================
# CONSTANTS
# =====================================================

# category -> (icon name, colour)
CATEGORIES = {
    "Food": ("food", "#f59e0b"),
    "Travel": ("travel", "#38bdf8"),
    "Shopping": ("bag", "#ec4899"),
    "Education": ("book", "#818cf8"),
    "Entertainment": ("play", "#c084fc"),
    "Bills": ("receipt", "#fb7185"),
    "Health": ("heart", "#34d399"),
    "Other": ("grid", "#94a3b8"),
}

CATEGORY_LIST = list(CATEGORIES.keys())
PAYMENT_LIST = ["UPI", "Cash", "Debit Card", "Credit Card", "Other"]

NAV_DASHBOARD = "Dashboard"
NAV_ADD = "Add Expense"
NAV_HISTORY = "Transactions"
NAV_MANAGE = "Manage Expenses"
NAV_BUDGET = "Monthly Budget"

NAV_ITEMS = [
    (NAV_DASHBOARD, ":material/dashboard:"),
    (NAV_ADD, ":material/add_circle:"),
    (NAV_HISTORY, ":material/receipt_long:"),
    (NAV_MANAGE, ":material/edit_square:"),
    (NAV_BUDGET, ":material/savings:"),
]

# simple line icons (24x24)
ICONS = {
    "wallet": '<path d="M3 7a2 2 0 0 1 2-2h13a1 1 0 0 1 1 1v2"/><path d="M3 7v10a2 2 0 0 0 2 2h14a1 1 0 0 0 1-1v-3"/><path d="M21 10h-4a2 2 0 0 0 0 4h4z"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18"/>',
    "receipt": '<path d="M6 3h12v18l-3-2-3 2-3-2-3 2z"/><path d="M9 8h6M9 12h6"/>',
    "trend": '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    "food": '<path d="M7 3v8M5 3v5a2 2 0 0 0 4 0V3M7 11v10"/><path d="M17 3c-2 2-3 5-3 8h3v10"/>',
    "travel": '<path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/>',
    "bag": '<path d="M6 7h12l1 13H5z"/><path d="M9 7a3 3 0 0 1 6 0"/>',
    "book": '<path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z"/><path d="M4 19V5"/>',
    "play": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M10 9l5 3-5 3z"/>',
    "heart": '<path d="M12 20s-7-4.4-9-9a5 5 0 0 1 9-3 5 5 0 0 1 9 3c-2 4.6-9 9-9 9z"/>',
    "grid": '<rect x="4" y="4" width="7" height="7" rx="1.5"/><rect x="13" y="4" width="7" height="7" rx="1.5"/><rect x="4" y="13" width="7" height="7" rx="1.5"/><rect x="13" y="13" width="7" height="7" rx="1.5"/>',
    "up": '<path d="M7 17L17 7"/><path d="M9 7h8v8"/>',
    "down": '<path d="M7 7l10 10"/><path d="M17 9v8H9"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    "tag": '<path d="M3 12V4h8l10 10-8 8z"/><circle cx="7.5" cy="8.5" r="1.2"/>',
    "note": '<path d="M5 3h10l4 4v14H5z"/><path d="M9 12h6M9 16h6"/>',
    "bolt": '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
}


def svg(name, size=20):
    return (
        f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" '
        f'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
        f'stroke-linejoin="round">{ICONS[name]}</svg>'
    )


# =====================================================
# GLOBAL CSS
# =====================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #0f0d2a;
    --panel: #1a1747;
    --panel-2: #211d57;
    --border: #2c2767;
    --text: #eceaff;
    --muted: #9a96c9;
    --accent: #a855f7;
    --accent-2: #7c5cff;
    --pink: #d946ef;
    --green: #4ade80;
    --red: #fb7185;
}

/* ---------- Base ---------- */
html, body, .stApp, .stMarkdown, p, label, button, input, textarea, h1, h2, h3, h4 {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(900px 520px at 100% -5%, rgba(168, 85, 247, 0.20), transparent 60%),
        radial-gradient(800px 500px at 0% 100%, rgba(124, 92, 255, 0.14), transparent 60%),
        var(--bg);
    color: var(--text);
}

.block-container {
    padding: 2rem 2.4rem 3rem 2.4rem !important;
    max-width: 1500px;
}

#MainMenu, footer { visibility: hidden; }
div[data-testid="stToolbar"] { display: none; }
div[data-testid="stDecoration"] { display: none; }
header[data-testid="stHeader"] { background: transparent; }

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #342e78; border-radius: 8px; }

hr { border-color: var(--border) !important; }

/* ---------- Floating sidebar ---------- */
section[data-testid="stSidebar"] {
    background: transparent !important;
    border: none !important;
}

section[data-testid="stSidebar"] > div:first-child {
    background: var(--panel);
    margin: 16px 0 16px 16px;
    border-radius: 24px;
    border: 1px solid var(--border);
    height: calc(100vh - 32px);
    overflow-y: auto;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
}

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 4px 4px 20px 4px;
}

.brand-logo {
    width: 42px;
    height: 42px;
    border-radius: 13px;
    background: linear-gradient(135deg, #7c5cff, #d946ef);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #ffffff;
    box-shadow: 0 8px 24px rgba(168, 85, 247, 0.45);
}

.brand-name {
    font-size: 22px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: 0.5px;
    line-height: 1.1;
}

.brand-sub {
    font-size: 10.5px;
    color: var(--muted);
    letter-spacing: 1.6px;
    font-weight: 600;
}

.nav-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.6px;
    color: #6d68a8;
    padding: 2px 6px 8px 6px;
}

section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 4px;
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label {
    width: 100%;
    padding: 11px 14px;
    border-radius: 12px;
    border: 1px solid transparent;
    cursor: pointer;
    transition: all 0.18s ease;
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
    display: none;
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label p {
    font-size: 14.5px;
    font-weight: 500;
    color: #b3afe0;
    margin: 0;
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background: rgba(168, 85, 247, 0.10);
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
    background: rgba(168, 85, 247, 0.14);
    border-color: #a855f7;
    box-shadow: 0 0 18px rgba(168, 85, 247, 0.25);
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p {
    color: #ffffff;
    font-weight: 700;
}

.st-key-new_btn button {
    background: linear-gradient(90deg, #c026d3, #9333ea) !important;
    height: 46px;
    font-size: 15px;
    box-shadow: 0 10px 26px rgba(192, 38, 211, 0.40) !important;
}

.side-card {
    background: linear-gradient(145deg, #261f66, #1a1747);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 16px;
}

.side-card-label {
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: 1.4px;
    color: var(--muted);
}

.side-card-value {
    font-size: 21px;
    font-weight: 800;
    color: #ffffff;
    margin: 4px 0 10px 0;
}

.side-foot {
    font-size: 11.5px;
    color: #6d68a8;
    text-align: center;
    padding-top: 14px;
}

/* ---------- Navigation buttons ---------- */
[class*="st-key-nav_"] {
    margin-bottom: -0.55rem;
}

[class*="st-key-nav_"] button {
    background: transparent !important;
    border: 1px solid transparent !important;
    box-shadow: none !important;
    justify-content: flex-start !important;
    text-align: left;
    padding: 11px 14px;
    border-radius: 12px;
    width: 100%;
    transform: none !important;
}

[class*="st-key-nav_"] button * {
    color: #c9c5f5 !important;
    font-weight: 500;
    font-size: 14.5px;
}

[class*="st-key-nav_"] button > div {
    justify-content: flex-start !important;
}

[class*="st-key-nav_"] button:hover {
    background: rgba(168, 85, 247, 0.10) !important;
}

/* ---------- Text colours (work even without config.toml) ---------- */
.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stMarkdownContainer"] li {
    color: #e4e1ff;
}

.stApp h1, .stApp h2, .stApp h3 { color: #ffffff; }

div[data-testid="stCheckbox"] label,
div[data-testid="stCheckbox"] label p,
div[data-testid="stCheckbox"] label span {
    color: #d6d2ff !important;
}

div[data-baseweb="select"] div,
div[data-baseweb="select"] span,
div[data-baseweb="select"] input {
    color: #f4f2ff !important;
}

div[data-baseweb="select"] svg { fill: #c9c5f5 !important; }

ul[role="listbox"] li,
ul[role="listbox"] li * {
    color: #e4e1ff !important;
    background-color: transparent;
}

div[data-baseweb="popover"] div[data-baseweb="menu"] {
    background: #1a1747 !important;
}

input::placeholder, textarea::placeholder {
    color: #7f7bb5 !important;
    opacity: 1;
}

div[data-testid="stNumberInputStepUp"],
div[data-testid="stNumberInputStepDown"],
button[data-testid="stNumberInputStepUp"],
button[data-testid="stNumberInputStepDown"] {
    background: #1a1747 !important;
    color: #c9c5f5 !important;
}

div[data-testid="stAlert"] {
    background: rgba(168, 85, 247, 0.10) !important;
}

div[data-testid="stAlert"] * {
    color: #e4e1ff !important;
}

/* ---------- Header ---------- */
.page-head-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    margin-bottom: 22px;
}

.page-title {
    font-size: 2rem;
    font-weight: 800;
    line-height: 1.15;
    color: #ffffff;
}

.page-sub {
    color: var(--muted);
    font-size: 14.5px;
    margin-top: 4px;
}

.head-right {
    display: flex;
    align-items: center;
    gap: 12px;
}

.date-pill {
    background: var(--panel);
    border: 1px solid var(--border);
    color: #c9c5f5;
    padding: 10px 18px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 600;
    white-space: nowrap;
    display: flex;
    align-items: center;
    gap: 8px;
}

.avatar {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: linear-gradient(135deg, #7c5cff, #d946ef);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #ffffff;
    border: 2px solid rgba(255, 255, 255, 0.25);
}

.section-title {
    font-size: 17px;
    font-weight: 700;
    color: #ffffff;
    margin: 24px 0 12px 0;
}

/* ---------- KPI cards ---------- */
.kpi {
    background: linear-gradient(145deg, #201c55, #1a1747);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 20px 22px;
    margin-bottom: 14px;
    min-height: 138px;
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.kpi:hover {
    transform: translateY(-3px);
    border-color: var(--accent);
}

.kpi-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.kpi-label {
    font-size: 15px;
    font-weight: 600;
    color: #e4e1ff;
}

.kpi-icon {
    width: 34px;
    height: 34px;
    border-radius: 10px;
    background: rgba(168, 85, 247, 0.16);
    color: #c4a1ff;
    display: flex;
    align-items: center;
    justify-content: center;
}

.kpi-value {
    font-size: 1.95rem;
    font-weight: 800;
    color: #ffffff;
    margin-top: 12px;
    letter-spacing: -0.5px;
    line-height: 1.15;
}

.kpi-hint {
    font-size: 12.5px;
    color: var(--muted);
    margin-top: 6px;
}

.delta {
    display: inline-flex;
    align-items: center;
    gap: 3px;
    font-weight: 700;
}

.good { color: var(--green); }
.bad { color: var(--red); }

.kpi-bar-row {
    display: flex;
    justify-content: space-between;
    font-size: 17px;
    font-weight: 800;
    color: #ffffff;
    margin-top: 12px;
}

/* ---------- Panels ---------- */
.panel {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 22px 24px;
    margin-bottom: 14px;
}

.tall { min-height: 352px; }
.mid { min-height: 302px; }

.panel-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    gap: 8px;
}

.panel-title {
    font-size: 16px;
    font-weight: 700;
    color: #ffffff;
}

.tag {
    font-size: 12px;
    font-weight: 600;
    color: var(--muted);
}

.empty {
    text-align: center;
    color: var(--muted);
    padding: 34px 10px;
    font-size: 14px;
}

.empty-icon {
    display: flex;
    justify-content: center;
    margin-bottom: 10px;
    color: #7c5cff;
}

/* ---------- Rings ---------- */
.ring-wrap {
    display: flex;
    justify-content: center;
    margin: 6px 0 20px 0;
}

.ring {
    position: relative;
    width: var(--size);
    height: var(--size);
    border-radius: 50%;
    background: conic-gradient(var(--ca), var(--cb) calc(var(--p) * 1%), #2b2668 0);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.ring::before {
    content: "";
    position: absolute;
    inset: var(--th);
    border-radius: 50%;
    background: var(--panel);
}

.ring span {
    position: relative;
    font-size: var(--fs);
    font-weight: 800;
    color: #ffffff;
}

.legend-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 13.5px;
    color: #dcd9ff;
    margin-bottom: 11px;
}

.dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 10px;
}

.rings {
    display: flex;
    flex-wrap: wrap;
    gap: 18px 16px;
    justify-content: center;
    padding-top: 6px;
}

.ring-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 9px;
}

.ring-label {
    font-size: 12.5px;
    font-weight: 600;
    color: #c9c5f5;
}

/* ---------- Calendar ---------- */
.cal-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 4px 0;
    text-align: center;
}

.cal-h {
    font-size: 11px;
    font-weight: 700;
    color: #ffffff;
    padding-bottom: 6px;
}

.cal-d {
    position: relative;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    color: #b9b5e8;
}

.cal-d.today span {
    background: linear-gradient(135deg, #7c5cff, #d946ef);
    color: #ffffff;
    font-weight: 700;
    border-radius: 50%;
    width: 27px;
    height: 27px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.cal-d.has::after {
    content: "";
    position: absolute;
    bottom: 0;
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: #d946ef;
}

.cal-note {
    font-size: 11.5px;
    color: var(--muted);
    margin-top: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ---------- Budget bar ---------- */
.bar {
    width: 100%;
    height: 12px;
    background: #2b2668;
    border-radius: 999px;
    overflow: hidden;
}

.bar-fill {
    height: 100%;
    border-radius: 999px;
}

.chip {
    font-size: 12px;
    font-weight: 700;
    padding: 5px 12px;
    border-radius: 999px;
}

.chip-ok { background: rgba(74, 222, 128, 0.15); color: #4ade80; }
.chip-warn { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
.chip-bad { background: rgba(251, 113, 133, 0.15); color: #fb7185; }

.budget-stats {
    display: flex;
    justify-content: space-between;
    gap: 16px;
    margin-top: 20px;
    flex-wrap: wrap;
}

.bs-label { font-size: 12px; color: var(--muted); font-weight: 600; }
.bs-value { font-size: 21px; font-weight: 800; color: #ffffff; margin-top: 2px; }

/* ---------- Transaction cards ---------- */
.txn {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 12px;
    margin-bottom: 10px;
    border: 1px solid var(--border);
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.025);
}

.txn:last-child { margin-bottom: 0; }

.txn-icon {
    width: 40px;
    height: 40px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.txn-main { flex: 1; min-width: 0; }

.txn-name {
    font-size: 14px;
    font-weight: 700;
    color: #ffffff;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.txn-meta {
    font-size: 12px;
    color: var(--muted);
    margin-top: 2px;
}

.txn-right { text-align: right; flex-shrink: 0; }

.txn-amt {
    font-size: 13.5px;
    font-weight: 700;
    color: #fb7185;
    white-space: nowrap;
}

.txn-date {
    font-size: 11.5px;
    color: var(--muted);
    margin-top: 2px;
}

/* ---------- Footer ---------- */
.footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 28px;
    padding: 18px 24px;
    border-radius: 18px;
    background: #14113a;
    border: 1px solid var(--border);
    color: var(--muted);
    font-size: 12.5px;
}

.footer b { color: #ffffff; font-size: 14px; }

/* ---------- Forms & inputs ---------- */
div[data-testid="stForm"] {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 26px 26px 18px 26px;
}

div[data-testid="stWidgetLabel"] p {
    color: #b3afe0 !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}

div[data-baseweb="input"],
div[data-baseweb="base-input"],
div[data-baseweb="textarea"],
div[data-baseweb="select"] > div {
    background: #120f35 !important;
    border-color: #342e78 !important;
    border-radius: 11px !important;
}

div[data-baseweb="input"]:focus-within,
div[data-baseweb="textarea"]:focus-within,
div[data-baseweb="select"] > div:focus-within {
    border-color: #a855f7 !important;
    box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.22) !important;
}

input, textarea { color: #f4f2ff !important; }

ul[role="listbox"] { background: #1a1747 !important; }

/* ---------- Buttons ---------- */
.stButton > button,
.stDownloadButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(90deg, #7c5cff, #c026d3);
    color: #ffffff !important;
    border: none;
    border-radius: 12px;
    font-weight: 700;
    padding: 10px 20px;
    box-shadow: 0 8px 22px rgba(168, 85, 247, 0.30);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover,
.stFormSubmitButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 28px rgba(168, 85, 247, 0.48);
    color: #ffffff !important;
    border: none;
}

.stButton > button:disabled { opacity: 0.35; box-shadow: none; }

.st-key-delete_btn button {
    background: linear-gradient(90deg, #f43f5e, #f97316);
    box-shadow: 0 8px 22px rgba(244, 63, 94, 0.30);
}

/* ---------- Tables, charts, alerts ---------- */
div[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: hidden;
}

div[data-testid="stPlotlyChart"] {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 10px 8px 0 8px;
    margin-bottom: 14px;
}

div[data-testid="stAlert"] {
    border-radius: 14px;
    border: 1px solid var(--border);
}

/* ---------- Responsive ---------- */
@media (max-width: 900px) {
    .block-container { padding: 1.2rem 1rem 3rem 1rem !important; }
    .page-title { font-size: 1.55rem; }
    .kpi-value { font-size: 1.5rem; }
    .date-pill { display: none; }
    .tall, .mid { min-height: 0; }
    section[data-testid="stSidebar"] > div:first-child {
        margin: 0;
        border-radius: 0;
        height: 100vh;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

# =====================================================
# HELPERS
# =====================================================


def inr(amount):
    """Format a number as Indian Rupees with lakh/crore grouping."""
    amount = float(amount)
    negative = amount < 0
    amount = abs(amount)
    whole, frac = f"{amount:.2f}".split(".")

    if len(whole) > 3:
        head, tail = whole[:-3], whole[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        whole = ",".join(parts + [tail])

    sign = "-" if negative else ""
    return f"{sign}₹{whole}.{frac}"


def short_inr(amount):
    amount = float(amount)
    if amount >= 1e7:
        return f"₹{amount / 1e7:.1f}Cr"
    if amount >= 1e5:
        return f"₹{amount / 1e5:.1f}L"
    if amount >= 1e4:
        return f"₹{amount / 1e3:.0f}k"
    return f"₹{amount:,.0f}"


def page_header(title, subtitle):
    st.markdown(
        '<div class="page-head-row"><div>'
        f'<div class="page-title">{title}</div>'
        f'<div class="page-sub">{subtitle}</div></div>'
        '<div class="head-right">'
        f'<div class="date-pill">{svg("calendar", 16)} {today.strftime("%A, %d %B %Y")}</div>'
        f'<div class="avatar">{svg("user", 22)}</div>'
        "</div></div>",
        unsafe_allow_html=True,
    )


def section_title(text):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


def panel_head(title, tag=""):
    tag_html = f'<span class="tag">{tag}</span>' if tag else ""
    return f'<div class="panel-head"><div class="panel-title">{title}</div>{tag_html}</div>'


def kpi_card(label, value, hint_html, icon):
    return (
        '<div class="kpi">'
        f'<div class="kpi-top"><span class="kpi-label">{label}</span>'
        f'<span class="kpi-icon">{svg(icon, 18)}</span></div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-hint">{hint_html}</div></div>'
    )


def limit_card(budget_amount, spent):
    if budget_amount <= 0:
        return kpi_card("Limit", "Not set", "Set a monthly budget to track it", "target")

    pct = min(spent / budget_amount * 100, 100)
    over = spent > budget_amount
    gradient = (
        "linear-gradient(90deg,#f43f5e,#f97316)"
        if over
        else "linear-gradient(90deg,#7c5cff,#d946ef)"
    )

    return (
        '<div class="kpi">'
        f'<div class="kpi-top"><span class="kpi-label">Limit</span>'
        f'<span class="kpi-icon">{svg("target", 18)}</span></div>'
        f'<div class="bar" style="margin-top:18px"><div class="bar-fill" style="width:{pct:.1f}%;background:{gradient}"></div></div>'
        f'<div class="kpi-bar-row"><span>{short_inr(spent)}</span><span>{short_inr(budget_amount)}</span></div>'
        f'<div class="kpi-hint">{"Over budget this month" if over else "Spent vs monthly limit"}</div>'
        "</div>"
    )


def empty_panel(title, icon, message, extra_class=""):
    return (
        f'<div class="panel {extra_class}">{panel_head(title)}'
        f'<div class="empty"><div class="empty-icon">{svg(icon, 34)}</div>{message}</div></div>'
    )


def ring(pct, text, size=150, thickness=14, color_a="#7c5cff", color_b="#d946ef", font=28):
    pct = max(0.0, min(float(pct), 100.0))
    return (
        f'<div class="ring" style="--p:{pct:.1f};--size:{size}px;--th:{thickness}px;'
        f'--ca:{color_a};--cb:{color_b};--fs:{font}px"><span>{text}</span></div>'
    )


def flash(message, kind="success"):
    st.session_state["flash"] = (kind, message)


def show_flash():
    if "flash" in st.session_state:
        kind, message = st.session_state.pop("flash")
        getattr(st, kind)(message)


def go_add():
    st.session_state["page"] = NAV_ADD


def set_page(name):
    st.session_state["page"] = name


def budget_panel(budget_amount, spent):
    if budget_amount <= 0:
        return empty_panel(
            "Monthly Budget",
            "target",
            "No budget set for this month yet.<br>Create one on the Monthly Budget page.",
        )

    pct = spent / budget_amount * 100
    remaining = budget_amount - spent
    width = min(pct, 100)

    if pct < 75:
        gradient = "linear-gradient(90deg,#7c5cff,#d946ef)"
        chip = '<span class="chip chip-ok">● On track</span>'
    elif pct < 100:
        gradient = "linear-gradient(90deg,#f59e0b,#fbbf24)"
        chip = '<span class="chip chip-warn">● Approaching limit</span>'
    else:
        gradient = "linear-gradient(90deg,#f43f5e,#f97316)"
        chip = '<span class="chip chip-bad">● Over budget</span>'

    remaining_label = "Remaining" if remaining >= 0 else "Over by"

    return (
        '<div class="panel">'
        f'<div class="panel-head"><div class="panel-title">Monthly Budget · {pct:.0f}% used</div>{chip}</div>'
        f'<div class="bar"><div class="bar-fill" style="width:{width:.1f}%;background:{gradient}"></div></div>'
        '<div class="budget-stats">'
        f'<div><div class="bs-label">Budget</div><div class="bs-value">{inr(budget_amount)}</div></div>'
        f'<div><div class="bs-label">Spent</div><div class="bs-value">{inr(spent)}</div></div>'
        f'<div><div class="bs-label">{remaining_label}</div><div class="bs-value">{inr(abs(remaining))}</div></div>'
        "</div></div>"
    )


def txn_row(row):
    icon_name, color = CATEGORIES.get(row["Category"], CATEGORIES["Other"])
    name = html.escape(str(row["Name"]))
    category = html.escape(str(row["Category"]))

    row_date = row["Date"].date()
    if row_date == today:
        when = "Today"
    elif row_date == today - timedelta(days=1):
        when = "Yesterday"
    else:
        when = row_date.strftime("%d %b")

    return (
        '<div class="txn">'
        f'<div class="txn-icon" style="background:{color}22;color:{color};border:1px solid {color}55">{svg(icon_name, 19)}</div>'
        f'<div class="txn-main"><div class="txn-name">{name}</div>'
        f'<div class="txn-meta">{category}</div></div>'
        f'<div class="txn-right"><div class="txn-amt">-{inr(row["Amount"])}</div>'
        f'<div class="txn-date">{when}</div></div>'
        "</div>"
    )


def tip_row(icon, title, text):
    return (
        '<div class="txn">'
        f'<div class="txn-icon" style="background:#a855f722;color:#c4a1ff;border:1px solid #a855f755">{svg(icon, 19)}</div>'
        f'<div class="txn-main"><div class="txn-name" style="white-space:normal">{title}</div>'
        f'<div class="txn-meta">{text}</div></div></div>'
    )


def calendar_panel(spend_days):
    cells = "".join(
        f'<div class="cal-h">{d}</div>'
        for d in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    )

    for day_num in calendar.Calendar(firstweekday=0).itermonthdays(today.year, today.month):
        if day_num == 0:
            cells += '<div class="cal-d"></div>'
            continue

        classes = "cal-d"
        if day_num == today.day:
            classes += " today"
        if day_num in spend_days:
            classes += " has"

        cells += f'<div class="{classes}"><span>{day_num}</span></div>'

    return (
        '<div class="panel">'
        f'{panel_head("Today", today.strftime("%b. %Y"))}'
        f'<div class="cal-grid">{cells}</div>'
        '<div class="cal-note"><span class="dot" style="background:#d946ef;margin:0"></span>Days with spending</div>'
        "</div>"
    )


def style_figure(fig, title, height):
    fig.update_layout(
        title=dict(
            text=title,
            x=0.04,
            y=0.95,
            font=dict(size=16, color="#ffffff", family="Plus Jakarta Sans, sans-serif"),
        ),
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#b3afe0", family="Plus Jakarta Sans, sans-serif"),
        margin=dict(t=64, b=28, l=28, r=24),
        hoverlabel=dict(
            bgcolor="#120f35",
            bordercolor="#a855f7",
            font=dict(color="#ffffff", family="Plus Jakarta Sans, sans-serif"),
        ),
    )
    return fig


# =====================================================
# DATA
# =====================================================


def load_data():
    records = get_expenses()

    columns = [
        "ID",
        "Name",
        "Amount",
        "Category",
        "Date",
        "Payment Method",
        "Description",
    ]

    data = pd.DataFrame(records, columns=columns)

    if not data.empty:
        data["Date"] = pd.to_datetime(data["Date"])
        data["Amount"] = pd.to_numeric(data["Amount"])
        data["Description"] = data["Description"].fillna("")

    return data


df = load_data()

today = date.today()
current_month = today.strftime("%Y-%m")

first_of_month = today.replace(day=1)
last_month_end = first_of_month - timedelta(days=1)
last_month_str = last_month_end.strftime("%Y-%m")

if not df.empty:
    month_key = df["Date"].dt.strftime("%Y-%m")
    monthly_df = df[month_key == current_month]
    last_month_df = df[month_key == last_month_str]
else:
    monthly_df = df.iloc[0:0]
    last_month_df = df.iloc[0:0]

total_expenses = float(df["Amount"].sum()) if not df.empty else 0.0
monthly_expenses = float(monthly_df["Amount"].sum()) if not monthly_df.empty else 0.0
last_month_total = float(last_month_df["Amount"].sum()) if not last_month_df.empty else 0.0

budget = float(get_budget(current_month))

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.markdown(
    '<div class="brand"><div class="brand-logo">'
    f'{svg("wallet", 22)}</div><div>'
    '<div class="brand-name">NOVA</div>'
    '<div class="brand-sub">PERSONAL FINANCE</div></div></div>'
    '<div class="nav-label">MAIN MENU</div>',
    unsafe_allow_html=True,
)

if "page" not in st.session_state:
    st.session_state["page"] = NAV_DASHBOARD

for nav_index, (nav_name, nav_icon) in enumerate(NAV_ITEMS):
    st.sidebar.button(
        nav_name,
        key=f"nav_{nav_index}",
        icon=nav_icon,
        on_click=set_page,
        args=(nav_name,),
        use_container_width=True,
    )

page = st.session_state["page"]
active_index = [name for name, _ in NAV_ITEMS].index(page)

st.sidebar.markdown(
    "<style>"
    f".st-key-nav_{active_index} button {{"
    "background: rgba(168, 85, 247, 0.16) !important;"
    "border: 1px solid #a855f7 !important;"
    "box-shadow: 0 0 18px rgba(168, 85, 247, 0.28) !important;"
    "}"
    f".st-key-nav_{active_index} button * {{"
    "color: #ffffff !important; font-weight: 700 !important;"
    "}"
    "</style>",
    unsafe_allow_html=True,
)

st.sidebar.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

st.sidebar.button(
    "New Expense",
    key="new_btn",
    icon=":material/add:",
    on_click=go_add,
    use_container_width=True,
)

if budget > 0:
    used_pct = monthly_expenses / budget * 100
    side_bar_width = min(used_pct, 100)
    side_text = f"{used_pct:.0f}% of budget used"
else:
    side_bar_width = 0
    side_text = "No budget set"

st.sidebar.markdown(
    '<div style="height:22px"></div>'
    '<div class="side-card">'
    f'<div class="side-card-label">{today.strftime("%B %Y").upper()}</div>'
    f'<div class="side-card-value">{inr(monthly_expenses)}</div>'
    '<div class="bar" style="height:7px"><div class="bar-fill" '
    f'style="width:{side_bar_width:.1f}%;background:linear-gradient(90deg,#7c5cff,#d946ef)"></div></div>'
    f'<div class="kpi-hint" style="margin-top:8px">{side_text}</div>'
    "</div>"
    '<div class="side-foot">NOVA · Built with Python</div>',
    unsafe_allow_html=True,
)

# =====================================================
# DASHBOARD
# =====================================================

if page == NAV_DASHBOARD:

    page_header("Dashboard", "A clear picture of where your money is going.")
    show_flash()

    # ---------- KPI row ----------
    if budget > 0:
        remaining = budget - monthly_expenses
        remaining_value = inr(remaining)
        remaining_hint = (
            f"of {inr(budget)} monthly budget"
            if remaining >= 0
            else '<span class="delta bad">Over budget</span>'
        )
    else:
        remaining_value = "Not set"
        remaining_hint = "Set a monthly budget to track it"

    if last_month_total > 0:
        change = (monthly_expenses - last_month_total) / last_month_total * 100
        if change > 0:
            delta_html = f'<span class="delta bad">{svg("up", 14)}+{change:.1f}%</span> vs last month'
        else:
            delta_html = f'<span class="delta good">{svg("down", 14)}{change:.1f}%</span> vs last month'
    else:
        delta_html = "No spending recorded last month"

    k1, k2, k3, k4 = st.columns(4)

    k1.markdown(
        kpi_card("Remaining Budget", remaining_value, remaining_hint, "wallet"),
        unsafe_allow_html=True,
    )
    k2.markdown(
        kpi_card("This Month", inr(monthly_expenses), delta_html, "calendar"),
        unsafe_allow_html=True,
    )
    k3.markdown(
        kpi_card("Total Expenses", inr(total_expenses), f"{len(df)} transactions recorded", "receipt"),
        unsafe_allow_html=True,
    )
    k4.markdown(limit_card(budget, monthly_expenses), unsafe_allow_html=True)

    # ---------- Main grid ----------
    main_col, side_col = st.columns([3.1, 1.15])

    with main_col:

        ring_col, analytics_col = st.columns([1, 2.1])

        # ----- Ring: budget used -----
        with ring_col:
            if budget > 0:
                used = monthly_expenses / budget * 100
                over = used > 100
                ring_html = ring(
                    used,
                    f"{used:.0f}%",
                    color_a="#f43f5e" if over else "#7c5cff",
                    color_b="#f97316" if over else "#d946ef",
                )
            else:
                ring_html = ring(0, "—")

            legend_html = ""
            if not monthly_df.empty and monthly_expenses > 0:
                top4 = (
                    monthly_df.groupby("Category")["Amount"]
                    .sum()
                    .sort_values(ascending=False)
                    .head(4)
                )
                for cat, amt in top4.items():
                    _, color = CATEGORIES.get(cat, CATEGORIES["Other"])
                    share = amt / monthly_expenses * 100
                    legend_html += (
                        '<div class="legend-row"><span>'
                        f'<span class="dot" style="background:{color}"></span>{html.escape(str(cat))}</span>'
                        f"<b>{share:.0f}%</b></div>"
                    )
            else:
                legend_html = '<div class="empty" style="padding:6px">No spending this month yet.</div>'

            st.markdown(
                f'<div class="panel tall">{panel_head("All Expenses", "Budget used")}'
                f'<div class="ring-wrap">{ring_html}</div>{legend_html}</div>',
                unsafe_allow_html=True,
            )

        # ----- Analytics: this month vs last month -----
        with analytics_col:
            if not df.empty:
                days_now = list(range(1, today.day + 1))
                days_last = list(range(1, last_month_end.day + 1))

                if monthly_df.empty:
                    now_values = [0] * len(days_now)
                else:
                    now_values = (
                        monthly_df.groupby(monthly_df["Date"].dt.day)["Amount"]
                        .sum()
                        .reindex(days_now, fill_value=0)
                        .tolist()
                    )

                if last_month_df.empty:
                    last_values = [0] * len(days_last)
                else:
                    last_values = (
                        last_month_df.groupby(last_month_df["Date"].dt.day)["Amount"]
                        .sum()
                        .reindex(days_last, fill_value=0)
                        .tolist()
                    )

                fig = go.Figure()

                fig.add_trace(
                    go.Scatter(
                        x=days_last,
                        y=last_values,
                        name="Last month",
                        mode="lines",
                        line=dict(color="#7c8cff", width=2.5, shape="spline", smoothing=0.8),
                        fill="tozeroy",
                        fillcolor="rgba(124, 140, 255, 0.12)",
                        hovertemplate="Day %{x}<br>₹%{y:,.2f}<extra>Last month</extra>",
                    )
                )

                fig.add_trace(
                    go.Scatter(
                        x=days_now,
                        y=now_values,
                        name="This month",
                        mode="lines+markers",
                        line=dict(color="#d946ef", width=3, shape="spline", smoothing=0.8),
                        marker=dict(size=7, color="#ffffff", line=dict(color="#d946ef", width=2)),
                        fill="tozeroy",
                        fillcolor="rgba(217, 70, 239, 0.20)",
                        hovertemplate="Day %{x}<br>₹%{y:,.2f}<extra>This month</extra>",
                    )
                )

                style_figure(fig, "Analytics", 330)

                fig.update_layout(
                    hovermode="x unified",
                    legend=dict(
                        orientation="h",
                        x=1,
                        xanchor="right",
                        y=1.16,
                        font=dict(size=12, color="#c9c5f5"),
                    ),
                    xaxis=dict(
                        showgrid=False,
                        dtick=5,
                        linecolor="#2c2767",
                        tickfont=dict(color="#9a96c9"),
                    ),
                    yaxis=dict(
                        gridcolor="rgba(154, 150, 201, 0.14)",
                        griddash="dot",
                        zeroline=False,
                        rangemode="tozero",
                        tickprefix="₹",
                        tickfont=dict(color="#9a96c9"),
                    ),
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={"displayModeBar": False},
                )
            else:
                st.markdown(
                    empty_panel(
                        "Analytics",
                        "trend",
                        "Add your first expense to see spending trends.",
                        "tall",
                    ),
                    unsafe_allow_html=True,
                )

        cat_col, stats_col = st.columns([1.15, 1])

        # ----- Categories rings -----
        with cat_col:
            if not monthly_df.empty and monthly_expenses > 0:
                ranking = (
                    monthly_df.groupby("Category")["Amount"]
                    .sum()
                    .sort_values(ascending=False)
                    .head(5)
                )

                items = ""
                for cat, amt in ranking.items():
                    _, color = CATEGORIES.get(cat, CATEGORIES["Other"])
                    share = amt / monthly_expenses * 100
                    items += (
                        '<div class="ring-item">'
                        f'{ring(share, short_inr(amt), 86, 9, color, color, 13)}'
                        f'<div class="ring-label">{html.escape(str(cat))}</div></div>'
                    )

                st.markdown(
                    f'<div class="panel mid">{panel_head("Categories", "This month")}'
                    f'<div class="rings">{items}</div></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    empty_panel(
                        "Categories",
                        "grid",
                        "Your top spending categories will appear here.",
                        "mid",
                    ),
                    unsafe_allow_html=True,
                )

        # ----- Statistics: weekday bars -----
        with stats_col:
            if not monthly_df.empty:
                weekday_values = (
                    monthly_df.groupby(monthly_df["Date"].dt.dayofweek)["Amount"]
                    .sum()
                    .reindex(range(7), fill_value=0)
                    .tolist()
                )
                labels = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
                peak = max(weekday_values)
                bar_colors = ["#d946ef" if v == peak else "#7c5cff" for v in weekday_values]

                fig = go.Figure(
                    go.Bar(
                        x=labels,
                        y=weekday_values,
                        marker=dict(color=bar_colors),
                        hovertemplate="<b>%{x}</b><br>₹%{y:,.2f}<extra></extra>",
                    )
                )

                style_figure(fig, "Statistics", 280)

                fig.update_layout(
                    bargap=0.55,
                    showlegend=False,
                    xaxis=dict(
                        showgrid=False,
                        linecolor="#2c2767",
                        tickfont=dict(color="#9a96c9"),
                    ),
                    yaxis=dict(
                        gridcolor="rgba(154, 150, 201, 0.14)",
                        griddash="dot",
                        zeroline=False,
                        tickprefix="₹",
                        tickfont=dict(color="#9a96c9"),
                    ),
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={"displayModeBar": False},
                )
            else:
                st.markdown(
                    empty_panel(
                        "Statistics",
                        "trend",
                        "Spending by weekday will appear here.",
                        "mid",
                    ),
                    unsafe_allow_html=True,
                )

    # ---------- Right column: calendar + transactions ----------
    with side_col:
        spend_days = (
            {int(d) for d in monthly_df["Date"].dt.day} if not monthly_df.empty else set()
        )
        st.markdown(calendar_panel(spend_days), unsafe_allow_html=True)

        if not df.empty:
            rows = "".join(txn_row(r) for _, r in df.head(5).iterrows())
            st.markdown(
                f'<div class="panel">{panel_head("Transactions", "Recent")}{rows}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                empty_panel(
                    "Transactions",
                    "receipt",
                    "No transactions yet.<br>Add your first expense!",
                ),
                unsafe_allow_html=True,
            )

# =====================================================
# ADD EXPENSE
# =====================================================

elif page == NAV_ADD:

    page_header("Add Expense", "Record a new transaction in your finance manager.")
    show_flash()

    form_col, tip_col = st.columns([1.7, 1])

    with form_col:
        with st.form("add_form", clear_on_submit=True):

            name = st.text_input("Expense Name", placeholder="e.g. Lunch at campus cafe")

            c1, c2 = st.columns(2)

            with c1:
                amount = st.number_input(
                    "Amount (₹)",
                    min_value=0.01,
                    value=100.0,
                    step=10.0,
                    format="%.2f",
                )
                category = st.selectbox("Category", CATEGORY_LIST)

            with c2:
                expense_date = st.date_input("Date", value=today, max_value=today)
                payment = st.selectbox("Payment Method", PAYMENT_LIST)

            description = st.text_area(
                "Description (optional)",
                placeholder="Add a short note...",
            )

            submit = st.form_submit_button(
                "Save Expense",
                icon=":material/check:",
                use_container_width=True,
            )

            if submit:
                if not name.strip():
                    st.error("Please enter an expense name.")
                else:
                    add_expense(
                        name.strip(),
                        amount,
                        category,
                        expense_date.isoformat(),
                        payment,
                        description,
                    )
                    flash("Expense added successfully!")
                    st.rerun()

    with tip_col:
        st.markdown(
            f'<div class="panel">{panel_head("Quick Tips")}'
            + tip_row("tag", "Pick the right category", "Accurate categories make your charts meaningful.")
            + tip_row("note", "Add short notes", "Helpful when reviewing old transactions.")
            + tip_row("bolt", "Log expenses daily", "A small habit that keeps your budget honest.")
            + "</div>",
            unsafe_allow_html=True,
        )

# =====================================================
# TRANSACTIONS
# =====================================================

elif page == NAV_HISTORY:

    page_header("Transactions", "Search, filter and export your spending records.")
    show_flash()

    if df.empty:
        st.markdown(
            empty_panel("Transaction History", "receipt", "No transactions available yet."),
            unsafe_allow_html=True,
        )

    else:
        f1, f2 = st.columns([1, 2])

        with f1:
            categories = ["All"] + sorted(df["Category"].unique().tolist())
            selected_category = st.selectbox("Category", categories)

        with f2:
            search = st.text_input("Search transaction", placeholder="Type a name to search...")

        filtered = df.copy()

        if selected_category != "All":
            filtered = filtered[filtered["Category"] == selected_category]

        if search:
            filtered = filtered[
                filtered["Name"].str.contains(search, case=False, na=False, regex=False)
            ]

        filtered_total = float(filtered["Amount"].sum()) if not filtered.empty else 0.0
        filtered_avg = float(filtered["Amount"].mean()) if not filtered.empty else 0.0

        s1, s2, s3 = st.columns(3)

        s1.markdown(
            kpi_card("Filtered Total", inr(filtered_total), "Matching records", "wallet"),
            unsafe_allow_html=True,
        )
        s2.markdown(
            kpi_card("Records", f"{len(filtered)}", "Transactions shown", "receipt"),
            unsafe_allow_html=True,
        )
        s3.markdown(
            kpi_card("Average", inr(filtered_avg), "Per transaction", "trend"),
            unsafe_allow_html=True,
        )

        if filtered.empty:
            st.info("No transactions match your filters.")
        else:
            display_df = filtered.copy()
            display_df["Date"] = display_df["Date"].dt.date

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ID": st.column_config.NumberColumn("ID", width="small"),
                    "Amount": st.column_config.NumberColumn("Amount", format="₹%.2f"),
                    "Date": st.column_config.DateColumn("Date", format="DD MMM YYYY"),
                },
            )

            export_df = filtered.copy()
            export_df["Date"] = export_df["Date"].dt.strftime("%Y-%m-%d")
            csv_data = export_df.to_csv(index=False).encode("utf-8")

            st.write("")
            st.download_button(
                "Export CSV Report",
                csv_data,
                "nova_expense_report.csv",
                "text/csv",
                icon=":material/download:",
            )

# =====================================================
# MANAGE EXPENSES (EDIT / DELETE)
# =====================================================

elif page == NAV_MANAGE:

    page_header("Manage Expenses", "Update a transaction or remove it permanently.")
    show_flash()

    if df.empty:
        st.markdown(
            empty_panel("Manage Expenses", "receipt", "No expenses available yet."),
            unsafe_allow_html=True,
        )

    else:
        options = {
            f"#{row['ID']}  ·  {row['Name']}  ·  {inr(row['Amount'])}": row["ID"]
            for _, row in df.iterrows()
        }

        selected_label = st.selectbox("Choose a transaction", list(options.keys()))
        selected_id = options[selected_label]
        selected = df[df["ID"] == selected_id].iloc[0]

        section_title("Edit Transaction")

        with st.form("edit_form"):

            name = st.text_input("Name", value=selected["Name"])

            c1, c2 = st.columns(2)

            with c1:
                amount = st.number_input(
                    "Amount (₹)",
                    min_value=0.01,
                    value=float(selected["Amount"]),
                    step=10.0,
                    format="%.2f",
                )

                category = st.selectbox(
                    "Category",
                    CATEGORY_LIST,
                    index=(
                        CATEGORY_LIST.index(selected["Category"])
                        if selected["Category"] in CATEGORY_LIST
                        else len(CATEGORY_LIST) - 1
                    ),
                )

            with c2:
                saved_date = selected["Date"].date()

                expense_date = st.date_input(
                    "Date",
                    value=min(saved_date, today),
                    max_value=today,
                )

                old_payment = selected["Payment Method"]

                payment = st.selectbox(
                    "Payment Method",
                    PAYMENT_LIST,
                    index=(
                        PAYMENT_LIST.index(old_payment)
                        if old_payment in PAYMENT_LIST
                        else 0
                    ),
                )

            description = st.text_area(
                "Description",
                value=selected["Description"] or "",
            )

            update = st.form_submit_button(
                "Update Expense",
                icon=":material/save:",
                use_container_width=True,
            )

            if update:
                if not name.strip():
                    st.error("Name cannot be empty.")
                else:
                    update_expense(
                        selected_id,
                        name.strip(),
                        amount,
                        category,
                        expense_date.isoformat(),
                        payment,
                        description,
                    )
                    flash("Transaction updated!")
                    st.rerun()

        section_title("Delete Transaction")

        st.markdown(
            '<div class="panel" style="margin-bottom:8px">'
            '<div class="txn-meta" style="font-size:13.5px">'
            "Deleting a transaction is permanent and cannot be undone."
            "</div></div>",
            unsafe_allow_html=True,
        )

        confirm = st.checkbox("I confirm that I want to delete this transaction.")

        if st.button(
            "Delete Expense",
            disabled=not confirm,
            key="delete_btn",
            icon=":material/delete:",
        ):
            delete_expense(selected_id)
            flash("Transaction deleted.")
            st.rerun()

# =====================================================
# MONTHLY BUDGET
# =====================================================

elif page == NAV_BUDGET:

    page_header(
        "Monthly Budget",
        f"Set your spending target for {today.strftime('%B %Y')}.",
    )
    show_flash()

    form_col, status_col = st.columns([1, 1.4])

    with form_col:
        with st.form("budget_form"):

            new_budget = st.number_input(
                "Your Monthly Budget (₹)",
                min_value=0.0,
                value=float(budget),
                step=500.0,
                format="%.2f",
            )

            save = st.form_submit_button(
                "Save Budget",
                icon=":material/check:",
                use_container_width=True,
            )

            if save:
                if new_budget <= 0:
                    st.error("Enter a budget greater than zero.")
                else:
                    set_budget(current_month, new_budget)
                    flash("Budget saved successfully!")
                    st.rerun()

    with status_col:
        st.markdown(budget_panel(budget, monthly_expenses), unsafe_allow_html=True)

        if budget > 0:
            if monthly_expenses <= budget:
                st.success("You're within your budget. Keep it up!")
            else:
                st.warning(f"Budget exceeded by {inr(monthly_expenses - budget)}.")

# =====================================================
# FOOTER
# =====================================================

st.markdown(
    '<div class="footer">'
    '<div><b>NOVA</b> · Personal Finance Manager</div>'
    "<div>Built with Python, Streamlit, Pandas, Plotly and SQLite</div>"
    f"<div>© {today.year} NOVA. All rights reserved.</div>"
    "</div>",
    unsafe_allow_html=True,
)