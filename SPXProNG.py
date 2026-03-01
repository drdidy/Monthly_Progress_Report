import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time
import json

# ============================================================
# SPX PROPHET NEXT GEN v1.0
# Proprietary Market Structure System by David
# Built on the Proprietary Rate Line Projection Framework
# ============================================================

st.set_page_config(
    page_title="SPX Prophet Next Gen",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM STYLING — Mission Control Terminal Design
# ============================================================
st.markdown("""
<style>
    /* ═══════════════════════════════════════════════════════════
       FONTS — Google Fonts: Orbitron (display), JetBrains Mono (data), Rajdhani (body)
       ═══════════════════════════════════════════════════════════ */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500;600;700&display=swap');
    
    /* ═══════════════════════════════════════════════════════════
       ANIMATIONS — Pulse, glow, fade-in, price flash
       ═══════════════════════════════════════════════════════════ */
    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 8px rgba(0,212,255,0.15), inset 0 0 8px rgba(0,212,255,0.05); }
        50% { box-shadow: 0 0 20px rgba(0,212,255,0.3), inset 0 0 15px rgba(0,212,255,0.08); }
    }
    @keyframes pulse-border-bull {
        0%, 100% { border-color: rgba(0,230,118,0.4); box-shadow: 0 0 15px rgba(0,230,118,0.1); }
        50% { border-color: rgba(0,230,118,0.9); box-shadow: 0 0 30px rgba(0,230,118,0.25); }
    }
    @keyframes pulse-border-bear {
        0%, 100% { border-color: rgba(255,23,68,0.4); box-shadow: 0 0 15px rgba(255,23,68,0.1); }
        50% { border-color: rgba(255,23,68,0.9); box-shadow: 0 0 30px rgba(255,23,68,0.25); }
    }
    @keyframes pulse-border-neutral {
        0%, 100% { border-color: rgba(255,215,64,0.4); box-shadow: 0 0 15px rgba(255,215,64,0.1); }
        50% { border-color: rgba(255,215,64,0.9); box-shadow: 0 0 30px rgba(255,215,64,0.2); }
    }
    @keyframes live-dot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(0.7); }
    }
    @keyframes fade-in-up {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes price-flash {
        0% { background: rgba(0,212,255,0.15); }
        100% { background: transparent; }
    }
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    @keyframes gradient-text {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* ═══════════════════════════════════════════════════════════
       APP SHELL — Deep space background with subtle noise
       ═══════════════════════════════════════════════════════════ */
    .stApp {
        background: 
            radial-gradient(ellipse at 20% 50%, rgba(0,212,255,0.03) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 20%, rgba(123,47,247,0.03) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 80%, rgba(255,107,53,0.02) 0%, transparent 50%),
            linear-gradient(180deg, #050810 0%, #080d16 40%, #0a0f1a 100%);
    }
    
    /* ═══════════════════════════════════════════════════════════
       HIDE STREAMLIT CHROME — Clean terminal look
       ═══════════════════════════════════════════════════════════ */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }
    div[data-testid="stDecoration"] { display: none; }
    
    /* ═══════════════════════════════════════════════════════════
       SCROLLBAR — Thin glowing accent
       ═══════════════════════════════════════════════════════════ */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #060910; }
    ::-webkit-scrollbar-thumb { 
        background: linear-gradient(180deg, #00d4ff44, #7b2ff744); 
        border-radius: 3px; 
    }
    ::-webkit-scrollbar-thumb:hover { background: #00d4ff88; }
    
    /* ═══════════════════════════════════════════════════════════
       SIDEBAR — Cockpit control panel
       ═══════════════════════════════════════════════════════════ */
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #060910 0%, #0a0f1a 50%, #080d16 100%);
        border-right: 1px solid rgba(0,212,255,0.1);
    }
    div[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        font-family: 'Rajdhani', sans-serif;
    }
    
    /* ═══════════════════════════════════════════════════════════
       TABS — Cockpit segment buttons
       ═══════════════════════════════════════════════════════════ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(6,9,16,0.8);
        border: 1px solid rgba(0,212,255,0.08);
        border-radius: 10px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Orbitron', monospace;
        font-size: 0.72rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        border-radius: 8px;
        padding: 8px 16px;
        color: #5a6a8a;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #ccd6f6;
        background: rgba(0,212,255,0.06);
    }
    .stTabs [aria-selected="true"] {
        color: #00d4ff !important;
        background: rgba(0,212,255,0.08) !important;
        border-bottom: 2px solid #00d4ff !important;
    }
    
    /* ═══════════════════════════════════════════════════════════
       HEADER — Animated gradient title
       ═══════════════════════════════════════════════════════════ */
    .main-header {
        font-family: 'Orbitron', monospace;
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00d4ff, #7b2ff7, #ff6b35, #00d4ff);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 8px 0 4px 0;
        letter-spacing: 4px;
        text-transform: uppercase;
        animation: gradient-text 6s ease infinite;
    }
    
    .sub-header {
        font-family: 'Rajdhani', sans-serif;
        color: #3a4a6a;
        text-align: center;
        font-size: 0.85rem;
        letter-spacing: 6px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    
    /* ═══════════════════════════════════════════════════════════
       LIVE STATUS BAR — Full width indicator
       ═══════════════════════════════════════════════════════════ */
    .live-bar {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        background: rgba(0,212,255,0.04);
        border: 1px solid rgba(0,212,255,0.1);
        border-radius: 10px;
        padding: 10px 20px;
        margin: 8px 0 16px 0;
        animation: fade-in-up 0.5s ease;
    }
    .live-dot {
        width: 8px; height: 8px;
        background: #ff1744;
        border-radius: 50%;
        animation: live-dot 1.5s ease-in-out infinite;
    }
    .live-dot.active {
        background: #00e676;
    }
    
    /* ═══════════════════════════════════════════════════════════
       METRIC CARDS — Glassmorphism with glow
       ═══════════════════════════════════════════════════════════ */
    .metric-card {
        background: linear-gradient(145deg, 
            rgba(14,20,36,0.95) 0%, 
            rgba(10,15,26,0.98) 100%);
        border: 1px solid rgba(30,45,74,0.5);
        border-radius: 14px;
        padding: 22px 16px;
        margin: 8px 0;
        box-shadow: 
            0 4px 24px rgba(0,0,0,0.4),
            0 1px 3px rgba(0,212,255,0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        min-height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        animation: fade-in-up 0.4s ease;
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-card:hover {
        border-color: rgba(0,212,255,0.3);
        box-shadow: 
            0 8px 32px rgba(0,0,0,0.5),
            0 0 20px rgba(0,212,255,0.08);
    }
    .metric-card.glow-live {
        animation: pulse-glow 3s ease-in-out infinite;
    }
    
    .metric-label {
        font-family: 'Rajdhani', sans-serif;
        color: #3a4a6a;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 2.5px;
        margin-bottom: 4px;
    }
    
    .metric-value-bull {
        font-family: 'JetBrains Mono', monospace;
        color: #00e676;
        font-size: 1.7rem;
        font-weight: 700;
        text-shadow: 0 0 20px rgba(0,230,118,0.2);
    }
    
    .metric-value-bear {
        font-family: 'JetBrains Mono', monospace;
        color: #ff1744;
        font-size: 1.7rem;
        font-weight: 700;
        text-shadow: 0 0 20px rgba(255,23,68,0.2);
    }
    
    .metric-value-neutral {
        font-family: 'JetBrains Mono', monospace;
        color: #00d4ff;
        font-size: 1.7rem;
        font-weight: 700;
        text-shadow: 0 0 20px rgba(0,212,255,0.2);
    }
    
    /* ═══════════════════════════════════════════════════════════
       SIGNAL BOXES — Animated glow borders
       ═══════════════════════════════════════════════════════════ */
    .signal-box-bull {
        background: linear-gradient(145deg, rgba(0,46,26,0.6) 0%, rgba(10,15,26,0.95) 100%);
        border: 2px solid rgba(0,230,118,0.4);
        border-radius: 14px;
        padding: 24px;
        text-align: center;
        animation: pulse-border-bull 3s ease-in-out infinite, fade-in-up 0.5s ease;
    }
    
    .signal-box-bear {
        background: linear-gradient(145deg, rgba(46,10,10,0.6) 0%, rgba(10,15,26,0.95) 100%);
        border: 2px solid rgba(255,23,68,0.4);
        border-radius: 14px;
        padding: 24px;
        text-align: center;
        animation: pulse-border-bear 3s ease-in-out infinite, fade-in-up 0.5s ease;
    }
    
    .signal-box-neutral {
        background: linear-gradient(145deg, rgba(26,26,46,0.6) 0%, rgba(10,15,26,0.95) 100%);
        border: 2px solid rgba(255,215,64,0.4);
        border-radius: 14px;
        padding: 24px;
        text-align: center;
        animation: pulse-border-neutral 3s ease-in-out infinite, fade-in-up 0.5s ease;
    }
    
    /* ═══════════════════════════════════════════════════════════
       CONFLUENCE — Score display
       ═══════════════════════════════════════════════════════════ */
    .confluence-high {
        font-family: 'Orbitron', monospace;
        color: #00e676;
        font-size: 2.2rem;
        text-shadow: 0 0 30px rgba(0,230,118,0.3);
    }
    .confluence-med {
        font-family: 'Orbitron', monospace;
        color: #ffd740;
        font-size: 2.2rem;
        text-shadow: 0 0 30px rgba(255,215,64,0.3);
    }
    .confluence-low {
        font-family: 'Orbitron', monospace;
        color: #ff1744;
        font-size: 2.2rem;
        text-shadow: 0 0 30px rgba(255,23,68,0.3);
    }
    
    /* ═══════════════════════════════════════════════════════════
       TRADE CARD — Premium glassmorphism with direction glow
       ═══════════════════════════════════════════════════════════ */
    .trade-card {
        background: linear-gradient(145deg, 
            rgba(14,20,36,0.95) 0%, 
            rgba(8,13,22,0.98) 100%);
        border-radius: 16px;
        padding: 24px;
        margin: 12px 0;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        animation: fade-in-up 0.5s ease;
    }
    .trade-card-bull {
        border: 2px solid rgba(0,230,118,0.25);
        box-shadow: 0 8px 32px rgba(0,0,0,0.4), 0 0 40px rgba(0,230,118,0.06);
    }
    .trade-card-bear {
        border: 2px solid rgba(255,82,82,0.25);
        box-shadow: 0 8px 32px rgba(0,0,0,0.4), 0 0 40px rgba(255,82,82,0.06);
    }
    
    /* ═══════════════════════════════════════════════════════════
       LADDER ROWS — Hover highlight
       ═══════════════════════════════════════════════════════════ */
    .ladder-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 14px;
        margin: 2px 0;
        border-radius: 0 8px 8px 0;
        transition: all 0.2s ease;
    }
    .ladder-row:hover {
        transform: translateX(4px);
        filter: brightness(1.3);
    }
    
    /* ═══════════════════════════════════════════════════════════
       SECTION DIVIDER — Subtle gradient line
       ═══════════════════════════════════════════════════════════ */
    .section-divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(0,212,255,0.15), transparent);
        margin: 24px 0;
    }
    
    /* ═══════════════════════════════════════════════════════════
       PROP ACCOUNT CARDS
       ═══════════════════════════════════════════════════════════ */
    .prop-account {
        background: linear-gradient(145deg, rgba(14,20,36,0.9) 0%, rgba(10,15,26,0.95) 100%);
        border: 1px solid rgba(30,45,74,0.4);
        border-radius: 14px;
        padding: 16px;
        margin: 6px 0;
        transition: border-color 0.3s ease;
    }
    .prop-account:hover {
        border-color: rgba(0,212,255,0.2);
    }
    
    /* ═══════════════════════════════════════════════════════════
       BUTTONS — Styled Streamlit buttons
       ═══════════════════════════════════════════════════════════ */
    .stButton > button {
        font-family: 'Rajdhani', sans-serif !important;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-weight: 600;
        transition: all 0.3s ease;
        border: 1px solid rgba(0,212,255,0.2) !important;
        background: rgba(0,212,255,0.06) !important;
    }
    .stButton > button:hover {
        border-color: rgba(0,212,255,0.5) !important;
        box-shadow: 0 0 20px rgba(0,212,255,0.15);
        background: rgba(0,212,255,0.12) !important;
    }
    
    /* ═══════════════════════════════════════════════════════════
       INPUTS — Number inputs, selectboxes
       ═══════════════════════════════════════════════════════════ */
    .stNumberInput input, .stTextInput input, .stSelectbox select {
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    /* ═══════════════════════════════════════════════════════════
       SCENARIO GRID — Premium projection cards
       ═══════════════════════════════════════════════════════════ */
    .scenario-card {
        background: linear-gradient(145deg, rgba(14,20,36,0.9) 0%, rgba(10,15,26,0.95) 100%);
        border-radius: 12px;
        padding: 14px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .scenario-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    }
    
    /* ═══════════════════════════════════════════════════════════
       PRICE MARKER — Current price in ladder
       ═══════════════════════════════════════════════════════════ */
    .price-marker {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 8px 14px;
        margin: 5px 0;
        border-radius: 10px;
        animation: fade-in-up 0.4s ease;
        position: relative;
        overflow: hidden;
    }
    .price-marker::before {
        content: '';
        position: absolute;
        top: 0; left: -200%; right: -200%; bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
        animation: shimmer 3s ease-in-out infinite;
    }
    
    /* ═══════════════════════════════════════════════════════════
       RULES BOX — Session rules with left accent
       ═══════════════════════════════════════════════════════════ */
    .rules-box {
        background: linear-gradient(145deg, rgba(14,20,36,0.9) 0%, rgba(10,15,26,0.95) 100%);
        border: 1px solid rgba(30,45,74,0.4);
        border-left: 3px solid #ffd740;
        border-radius: 0 14px 14px 0;
        padding: 18px 20px;
        margin: 12px 0;
    }
    
    /* ═══════════════════════════════════════════════════════════
       QUILL EDITOR — Dark theme override
       ═══════════════════════════════════════════════════════════ */
    .ql-toolbar.ql-snow {
        background: #0c1220 !important;
        border-color: rgba(30,45,74,0.5) !important;
        border-radius: 10px 10px 0 0 !important;
    }
    .ql-toolbar.ql-snow .ql-stroke {
        stroke: #8892b0 !important;
    }
    .ql-toolbar.ql-snow .ql-fill {
        fill: #8892b0 !important;
    }
    .ql-toolbar.ql-snow .ql-picker-label {
        color: #8892b0 !important;
    }
    .ql-toolbar.ql-snow button:hover .ql-stroke,
    .ql-toolbar.ql-snow .ql-picker-label:hover .ql-stroke {
        stroke: #00d4ff !important;
    }
    .ql-toolbar.ql-snow button:hover .ql-fill {
        fill: #00d4ff !important;
    }
    .ql-toolbar.ql-snow button.ql-active .ql-stroke {
        stroke: #00d4ff !important;
    }
    .ql-toolbar.ql-snow button.ql-active .ql-fill {
        fill: #00d4ff !important;
    }
    .ql-container.ql-snow {
        background: #060910 !important;
        border-color: rgba(30,45,74,0.5) !important;
        color: #ccd6f6 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 15px !important;
        min-height: 220px;
        border-radius: 0 0 10px 10px !important;
    }
    .ql-editor {
        color: #ccd6f6 !important;
        min-height: 220px;
    }
    .ql-editor.ql-blank::before {
        color: #3a4a6a !important;
        font-style: italic !important;
    }
    .ql-snow .ql-picker-options {
        background: #0c1220 !important;
        border-color: rgba(30,45,74,0.5) !important;
    }
    .ql-snow .ql-picker-item {
        color: #8892b0 !important;
    }
    .ql-snow .ql-picker-item:hover {
        color: #00d4ff !important;
    }
    .ql-editor h1, .ql-editor h2, .ql-editor h3 {
        color: #ccd6f6 !important;
    }
    .ql-editor a {
        color: #00d4ff !important;
    }
    .ql-tooltip {
        background: #0c1220 !important;
        border-color: rgba(30,45,74,0.5) !important;
        color: #ccd6f6 !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5) !important;
    }
    .ql-tooltip input[type=text] {
        background: #060910 !important;
        border-color: rgba(30,45,74,0.5) !important;
        color: #ccd6f6 !important;
    }
    .ql-tooltip a {
        color: #00d4ff !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# CORE ENGINE: Line Projection Calculator
# ============================================================

RATE_PER_CANDLE = 13/25  # Default rate (override via secrets.toml)
CANDLE_MINUTES = 30
MAINTENANCE_START_CT = time(16, 0)  # 4:00 PM CT
MAINTENANCE_END_CT = time(17, 0)    # 5:00 PM CT
NY_OPEN_CT = time(8, 30)
NY_DECISION_CT = time(9, 0)
NY_CLOSE_CT = time(15, 0)


def count_candles_between(start_dt: datetime, end_dt: datetime) -> int:
    """
    Count the number of 30-minute candles between two datetimes,
    excluding the maintenance window (4:00 PM - 5:00 PM CT).
    
    Candles are counted at each 30-min mark: :00 and :30 of each hour.
    The candle at start_dt is candle 0, so we count candles from start
    up to (but not including) end_dt's candle.
    
    Skips:
    - Maintenance window: 4:00 PM - 5:00 PM CT Mon-Thu only
    - Weekend closure: Friday 4:00 PM CT through Sunday 5:00 PM CT
      (Friday evening, Saturday all day, Sunday before 5:00 PM CT)
    """
    if end_dt <= start_dt:
        return 0
    
    count = 0
    current = start_dt
    
    while current < end_dt:
        current += timedelta(minutes=CANDLE_MINUTES)
        current_time = current.time()
        weekday = current.weekday()  # 0=Monday, 4=Friday, 5=Saturday, 6=Sunday
        
        # Skip all of Saturday (weekday 5)
        if weekday == 5:
            continue
        
        # Skip Sunday before 5:00 PM CT (weekday 6)
        if weekday == 6 and current_time < MAINTENANCE_END_CT:
            continue
        
        # Skip Friday after market close at 4:00 PM CT (weekday 4)
        # Market closes Friday at 4pm, no evening globex session
        if weekday == 4 and current_time >= MAINTENANCE_START_CT:
            continue
        
        # Skip maintenance window (4:00 PM - 5:00 PM CT) Mon-Thu
        if MAINTENANCE_START_CT <= current_time < MAINTENANCE_END_CT:
            continue
        
        count += 1
    
    return count


def calculate_line_value(anchor_price: float, anchor_time: datetime, 
                         target_time: datetime, direction: str) -> float:
    """
    Calculate the projected line value at a target time.
    
    direction: 'ascending' (+rate/candle) or 'descending' (-rate/candle)
    """
    candles = count_candles_between(anchor_time, target_time)
    
    if direction == 'ascending':
        return anchor_price + (RATE_PER_CANDLE * candles)
    else:
        return anchor_price - (RATE_PER_CANDLE * candles)


def generate_line_series(anchor_price: float, anchor_time: datetime,
                         start_time: datetime, end_time: datetime,
                         direction: str) -> list:
    """
    Generate a series of (datetime, price) tuples for plotting a projected line.
    """
    points = []
    current = anchor_time
    
    # First point at anchor
    points.append((anchor_time, anchor_price))
    
    # Step forward in 30-min increments
    while current < end_time:
        current += timedelta(minutes=CANDLE_MINUTES)
        current_time_only = current.time()
        weekday = current.weekday()
        
        # Skip Saturday entirely
        if weekday == 5:
            continue
        
        # Skip Sunday before 5:00 PM CT
        if weekday == 6 and current_time_only < MAINTENANCE_END_CT:
            continue
        
        # Skip Friday after 4:00 PM CT (no evening session)
        if weekday == 4 and current_time_only >= MAINTENANCE_START_CT:
            continue
        
        # Skip maintenance window (4:00 PM - 5:00 PM CT) Mon-Thu
        if MAINTENANCE_START_CT <= current_time_only < MAINTENANCE_END_CT:
            continue
        
        value = calculate_line_value(anchor_price, anchor_time, current, direction)
        points.append((current, value))
    
    # Filter to only show from start_time onward
    points = [(t, v) for t, v in points if t >= start_time]
    
    return points


def calculate_nine_am_levels(bounces: list, rejections: list,
                             highest_wick: dict, lowest_wick: dict,
                             next_day_date: datetime) -> dict:
    """
    Calculate the four key horizontal levels at 9:00 AM CT the next day.
    
    bounces: list of {'price': float, 'time': datetime}
    rejections: list of {'price': float, 'time': datetime}
    highest_wick: {'price': float, 'time': datetime}
    lowest_wick: {'price': float, 'time': datetime}
    """
    nine_am = datetime.combine(next_day_date.date(), NY_DECISION_CT)
    
    # Calculate all ascending lines at 9 AM (from bounces + highest wick)
    ascending_at_9am = []
    for bounce in bounces:
        val = calculate_line_value(bounce['price'], bounce['time'], nine_am, 'ascending')
        ascending_at_9am.append({
            'source': f"Bounce @ {bounce['price']:.2f} ({bounce['time'].strftime('%I:%M %p')})",
            'anchor_price': bounce['price'],
            'anchor_time': bounce['time'],
            'value_at_9am': val,
            'type': 'bounce'
        })
    
    # Highest wick ascending
    hw_val = calculate_line_value(highest_wick['price'], highest_wick['time'], nine_am, 'ascending')
    ascending_at_9am.append({
        'source': f"Highest Wick @ {highest_wick['price']:.2f} ({highest_wick['time'].strftime('%I:%M %p')})",
        'anchor_price': highest_wick['price'],
        'anchor_time': highest_wick['time'],
        'value_at_9am': hw_val,
        'type': 'highest_wick'
    })
    
    # Calculate all descending lines at 9 AM (from rejections + lowest wick)
    descending_at_9am = []
    for rejection in rejections:
        val = calculate_line_value(rejection['price'], rejection['time'], nine_am, 'descending')
        descending_at_9am.append({
            'source': f"Rejection @ {rejection['price']:.2f} ({rejection['time'].strftime('%I:%M %p')})",
            'anchor_price': rejection['price'],
            'anchor_time': rejection['time'],
            'value_at_9am': val,
            'type': 'rejection'
        })
    
    # Lowest wick descending
    lw_val = calculate_line_value(lowest_wick['price'], lowest_wick['time'], nine_am, 'descending')
    descending_at_9am.append({
        'source': f"Lowest Wick @ {lowest_wick['price']:.2f} ({lowest_wick['time'].strftime('%I:%M %p')})",
        'anchor_price': lowest_wick['price'],
        'anchor_time': lowest_wick['time'],
        'value_at_9am': lw_val,
        'type': 'lowest_wick'
    })
    
    # Sort to find the key levels
    ascending_at_9am.sort(key=lambda x: x['value_at_9am'], reverse=True)
    descending_at_9am.sort(key=lambda x: x['value_at_9am'])
    
    # Identify the four key lines
    highest_wick_asc = next((l for l in ascending_at_9am if l['type'] == 'highest_wick'), ascending_at_9am[0])
    highest_bounce_asc = next((l for l in ascending_at_9am if l['type'] == 'bounce'), None)
    
    # If highest bounce is actually higher than highest wick, swap labels for clarity
    # The "highest" refers to the line with the highest 9am value
    
    lowest_wick_desc = next((l for l in descending_at_9am if l['type'] == 'lowest_wick'), descending_at_9am[0])
    lowest_rejection_desc = next((l for l in descending_at_9am if l['type'] == 'rejection'), None)
    
    return {
        'ascending': ascending_at_9am,
        'descending': descending_at_9am,
        'key_levels': {
            'highest_wick_ascending': highest_wick_asc,
            'highest_bounce_ascending': highest_bounce_asc,
            'lowest_wick_descending': lowest_wick_desc,
            'lowest_rejection_descending': lowest_rejection_desc,
        },
        'nine_am_time': nine_am
    }


# ============================================================
# PROP FIRM RISK CALCULATOR
# ============================================================

def calculate_prop_firm_risk(daily_limit: float, stop_points: float, 
                             instrument: str = 'ES') -> dict:
    """Calculate position sizing for prop firm accounts."""
    point_value = 50.0 if instrument == 'ES' else 5.0  # ES=$50/pt, MES=$5/pt
    risk_per_trade = daily_limit * 0.40  # 40% of daily limit
    
    contracts = int(risk_per_trade / (stop_points * point_value))
    actual_risk = contracts * stop_points * point_value
    
    profit_5pt = contracts * 5 * point_value
    profit_10pt = contracts * 10 * point_value
    
    return {
        'contracts': contracts,
        'risk_per_trade': actual_risk,
        'max_trades': 2,
        'remaining_after_1_loss': daily_limit - actual_risk,
        'profit_5pt_move': profit_5pt,
        'profit_10pt_move': profit_10pt,
        'point_value': point_value,
        'instrument': instrument
    }


# ============================================================
# CONFLUENCE SCORE CALCULATOR
# ============================================================

def calculate_confluence(asian_aligns: bool, london_sweep: bool,
                        data_reaction: str, opening_drive: bool,
                        line_cluster: bool) -> dict:
    """Calculate the 5-factor confluence score."""
    score = 0
    factors = []
    
    if asian_aligns:
        score += 1
        factors.append("✅ Asian Session Aligned")
    else:
        factors.append("❌ Asian Session Misaligned")
    
    if london_sweep:
        score += 1
        factors.append("✅ London Sweep Confirmed")
    else:
        factors.append("❌ No London Sweep")
    
    if data_reaction == 'aligned':
        score += 1
        factors.append("✅ Data Reaction Aligned")
    elif data_reaction == 'absorbed':
        score += 0.5
        factors.append("⚡ Data Absorbed (Half Point)")
    else:
        factors.append("❌ Data Reaction Against")
    
    if opening_drive:
        score += 1
        factors.append("✅ Opening Drive Aligned")
    else:
        factors.append("❌ Opening Drive Against")
    
    if line_cluster:
        score += 1
        factors.append("✅ Line Cluster Confluence")
    else:
        factors.append("❌ No Line Cluster")
    
    if score >= 4:
        recommendation = "FULL SIZE — High confidence setup"
        size_pct = 100
        color = "high"
    elif score >= 3:
        recommendation = "STANDARD SIZE — Solid setup"
        size_pct = 75
        color = "high"
    elif score >= 2:
        recommendation = "HALF SIZE — Mixed context"
        size_pct = 50
        color = "med"
    else:
        recommendation = "NO TRADE — Insufficient confluence"
        size_pct = 0
        color = "low"
    
    return {
        'score': score,
        'factors': factors,
        'recommendation': recommendation,
        'size_pct': size_pct,
        'color': color
    }


def auto_detect_confluence(ny_trade_direction: str, ny_ladder: list,
                           current_price: float, candles_df=None,
                           es_offset: float = 0) -> dict:
    """
    Automatically detect all 5 confluence factors from available data.
    
    Args:
        ny_trade_direction: 'PUT' or 'CALL' from NY signal logic
        ny_ladder: list of ladder dicts with 'value', 'direction', 'short'
        current_price: SPX price at 9 AM
        candles_df: DataFrame of ES 30-min candles (if available)
        es_offset: ES-SPX spread for converting candle prices
    
    Returns:
        dict with all 5 boolean factors plus detail strings
    """
    results = {
        'asian_aligns': False, 'asian_detail': 'No candle data',
        'london_sweep': False, 'london_detail': 'No candle data',
        'data_reaction': 'absorbed', 'data_detail': 'No candle data (default: absorbed)',
        'opening_drive': False, 'opening_detail': 'No candle data',
        'line_cluster': False, 'cluster_detail': 'No cluster detected',
    }
    
    # ── Factor 5: Line Cluster (always available from ladder) ──
    if ny_ladder and len(ny_ladder) >= 3:
        values = sorted([l['value'] for l in ny_ladder])
        for i in range(len(values) - 2):
            if values[i+2] - values[i] <= 5.0:  # 3 lines within 5 points
                cluster_lines = [l for l in ny_ladder if values[i] <= l['value'] <= values[i+2]]
                cluster_names = ', '.join([l['short'] for l in cluster_lines[:3]])
                results['line_cluster'] = True
                results['cluster_detail'] = f"3 lines within {values[i+2]-values[i]:.1f}pt ({cluster_names})"
                break
    
    if candles_df is None or len(candles_df) == 0:
        return results
    
    try:
        df = candles_df.copy()
        # Ensure datetime index
        if 'Datetime' in df.columns:
            df['Datetime'] = pd.to_datetime(df['Datetime'])
            df = df.set_index('Datetime')
        elif not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        
        # Convert ES to SPX terms
        if es_offset != 0:
            for col in ['Open', 'High', 'Low', 'Close']:
                if col in df.columns:
                    df[col] = df[col] - es_offset
        
        # Get session candles by hour (CT timezone)
        # Asian: 5:00 PM - 2:00 AM CT (previous day 17:00 to 02:00)
        # London: 2:00 AM - 8:30 AM CT
        # Pre-market data: 7:30-8:00 AM, 8:00-8:30 AM candles
        # Opening: 8:30-9:00 AM candle
        
        hours = df.index.hour
        minutes = df.index.minute
        time_decimal = hours + minutes / 60.0
        
        # Asian session: 17:00 - 02:00 CT
        asian_mask = (time_decimal >= 17.0) | (time_decimal < 2.0)
        asian_candles = df[asian_mask]
        
        # London session: 2:00 - 8:30 CT
        london_mask = (time_decimal >= 2.0) & (time_decimal < 8.5)
        london_candles = df[london_mask]
        
        # Data candle: 7:30-8:00 AM and 8:00-8:30 AM
        data_mask = (time_decimal >= 7.5) & (time_decimal < 8.5)
        data_candles = df[data_mask]
        
        # Opening drive: 8:30-9:00 AM candle
        open_mask = (time_decimal >= 8.5) & (time_decimal < 9.0)
        open_candles = df[open_mask]
        
        # ── Factor 1: Asian Session Aligned ──
        if len(asian_candles) >= 2:
            asian_open = asian_candles.iloc[0]['Open']
            asian_close = asian_candles.iloc[-1]['Close']
            asian_move = asian_close - asian_open
            
            if ny_trade_direction == 'PUT' and asian_move < -1.0:
                results['asian_aligns'] = True
                results['asian_detail'] = f"Asian sold off {asian_move:.1f}pt → aligns with PUT"
            elif ny_trade_direction == 'CALL' and asian_move > 1.0:
                results['asian_aligns'] = True
                results['asian_detail'] = f"Asian rallied +{asian_move:.1f}pt → aligns with CALL"
            elif abs(asian_move) <= 1.0:
                results['asian_detail'] = f"Asian flat ({asian_move:+.1f}pt) → no alignment"
            else:
                direction_word = "rallied" if asian_move > 0 else "sold off"
                results['asian_detail'] = f"Asian {direction_word} {asian_move:+.1f}pt → AGAINST {ny_trade_direction}"
        
        # ── Factor 2: London Sweep ──
        if len(asian_candles) >= 2 and len(london_candles) >= 2:
            asian_high = asian_candles['High'].max()
            asian_low = asian_candles['Low'].min()
            london_high = london_candles['High'].max()
            london_low = london_candles['Low'].min()
            london_close = london_candles.iloc[-1]['Close']
            
            # London swept Asian high then reversed down → bearish sweep
            swept_high = london_high > asian_high + 0.5
            reversed_from_high = london_close < asian_high
            # London swept Asian low then reversed up → bullish sweep
            swept_low = london_low < asian_low - 0.5
            reversed_from_low = london_close > asian_low
            
            if ny_trade_direction == 'PUT' and swept_high and reversed_from_high:
                results['london_sweep'] = True
                results['london_detail'] = f"London swept Asian high {asian_high:.0f}→{london_high:.0f} then reversed ↓"
            elif ny_trade_direction == 'CALL' and swept_low and reversed_from_low:
                results['london_sweep'] = True
                results['london_detail'] = f"London swept Asian low {asian_low:.0f}→{london_low:.0f} then reversed ↑"
            elif swept_high or swept_low:
                results['london_detail'] = f"Sweep detected but against direction"
            else:
                results['london_detail'] = f"No sweep (London H:{london_high:.0f} L:{london_low:.0f} vs Asian H:{asian_high:.0f} L:{asian_low:.0f})"
        
        # ── Factor 3: Data Reaction (7:30-8:30 AM) ──
        if len(data_candles) >= 1:
            data_open = data_candles.iloc[0]['Open']
            data_high = data_candles['High'].max()
            data_low = data_candles['Low'].min()
            data_close = data_candles.iloc[-1]['Close']
            data_range = data_high - data_low
            data_move = data_close - data_open
            
            # Check if there was a significant spike (> 3pt range = data release)
            if data_range > 3.0:
                if ny_trade_direction == 'PUT' and data_move < -1.0:
                    results['data_reaction'] = 'aligned'
                    results['data_detail'] = f"Data drop {data_move:+.1f}pt → aligns with PUT"
                elif ny_trade_direction == 'CALL' and data_move > 1.0:
                    results['data_reaction'] = 'aligned'
                    results['data_detail'] = f"Data rally {data_move:+.1f}pt → aligns with CALL"
                elif abs(data_move) <= 1.0 and data_range > 3.0:
                    results['data_reaction'] = 'absorbed'
                    results['data_detail'] = f"Data spike absorbed ({data_range:.1f}pt range, net {data_move:+.1f}pt)"
                else:
                    results['data_reaction'] = 'against'
                    results['data_detail'] = f"Data moved against ({data_move:+.1f}pt vs {ny_trade_direction})"
            else:
                results['data_reaction'] = 'absorbed'
                results['data_detail'] = f"Quiet pre-market ({data_range:.1f}pt range) → neutral"
        
        # ── Factor 4: Opening Drive (8:30-9:00 AM) ──
        if len(open_candles) >= 1:
            open_o = open_candles.iloc[0]['Open']
            open_c = open_candles.iloc[-1]['Close']
            open_move = open_c - open_o
            
            if ny_trade_direction == 'PUT' and open_move < -0.5:
                results['opening_drive'] = True
                results['opening_detail'] = f"Opening drive down {open_move:+.1f}pt → aligns with PUT"
            elif ny_trade_direction == 'CALL' and open_move > 0.5:
                results['opening_drive'] = True
                results['opening_detail'] = f"Opening drive up {open_move:+.1f}pt → aligns with CALL"
            else:
                direction_word = "up" if open_move > 0 else "down" if open_move < 0 else "flat"
                results['opening_drive'] = False
                results['opening_detail'] = f"Opening drive {direction_word} {open_move:+.1f}pt → AGAINST {ny_trade_direction}"
        
    except Exception as e:
        results['asian_detail'] = f"Auto-detect error: {str(e)[:50]}"
    
    return results


# ============================================================
# SESSION TIME ZONES (all in CT)
# ============================================================

SESSION_TIMES = {
    'Sydney': {'start': time(15, 0), 'end': time(0, 0), 'color': 'rgba(255,152,0,0.08)', 'border': 'rgba(255,152,0,0.3)'},
    'Tokyo': {'start': time(19, 0), 'end': time(2, 0), 'color': 'rgba(76,175,80,0.08)', 'border': 'rgba(76,175,80,0.3)'},
    'London': {'start': time(2, 0), 'end': time(8, 30), 'color': 'rgba(33,150,243,0.08)', 'border': 'rgba(33,150,243,0.3)'},
    'New York': {'start': time(8, 30), 'end': time(15, 0), 'color': 'rgba(156,39,176,0.08)', 'border': 'rgba(156,39,176,0.3)'},
}


# ============================================================
# DATA SOURCE MODULE
# yfinance (primary for historical) → Tastytrade SDK (live streaming)
# ============================================================

class DataSourceStatus:
    """Track data source status for display"""
    def __init__(self):
        self.tastytrade_ok = False
        self.yfinance_ok = False
        self.source_used = "manual"
        self.error_msg = ""
        self.candles = None  # DataFrame with OHLC 30-min candles


def fetch_yfinance_candles(start_date: str, end_date: str) -> dict:
    """
    Fetch ES futures 30-min candles from Yahoo Finance.
    ES=F gives the full 23-hour session including overnight.
    """
    try:
        import yfinance as yf
        es = yf.Ticker("ES=F")
        df = es.history(start=start_date, end=end_date, interval="30m")
        if len(df) > 0:
            df = df.reset_index()
            # Normalize column names
            col_map = {}
            for col in df.columns:
                cl = col.lower().replace(' ', '_')
                if 'datetime' in cl or 'date' in cl:
                    col_map[col] = 'datetime'
                elif cl == 'open':
                    col_map[col] = 'open'
                elif cl == 'high':
                    col_map[col] = 'high'
                elif cl == 'low':
                    col_map[col] = 'low'
                elif cl == 'close':
                    col_map[col] = 'close'
                elif cl == 'volume':
                    col_map[col] = 'volume'
            df = df.rename(columns=col_map)
            if 'datetime' not in df.columns:
                df = df.rename(columns={df.columns[0]: 'datetime'})
            df['datetime'] = pd.to_datetime(df['datetime'])
            # Convert to CT if timezone-aware
            if df['datetime'].dt.tz is not None:
                import pytz
                ct = pytz.timezone('America/Chicago')
                df['datetime'] = df['datetime'].dt.tz_convert(ct).dt.tz_localize(None)
            df = df.sort_values('datetime').reset_index(drop=True)
            return {'ok': True, 'data': df}
        return {'ok': False, 'error': 'No data returned from Yahoo Finance'}
    except ImportError:
        return {'ok': False, 'error': 'yfinance not installed (add to requirements.txt)'}
    except Exception as e:
        return {'ok': False, 'error': str(e)}


def fetch_tastytrade_candles_via_sdk(start_dt: datetime, end_dt: datetime) -> dict:
    """
    Fetch historical candles via Tastytrade SDK + DXLink streamer.
    Uses Candle event with symbol '/ES{=30m}' and from_time parameter.
    Requires tastytrade SDK with async support.
    """
    try:
        from tastytrade import Session, DXLinkStreamer
        from tastytrade.dxfeed import Candle
        import asyncio
        
        tt = st.secrets.get("tastytrade", {})
        client_secret = tt.get("client_secret")
        refresh_token = tt.get("refresh_token")
        
        if not client_secret or not refresh_token:
            return {'ok': False, 'error': 'Missing tastytrade secrets'}
        
        async def _fetch():
            session = Session(client_secret, refresh_token)
            candles = []
            from_time_ms = int(start_dt.timestamp() * 1000)
            
            async with DXLinkStreamer(session) as streamer:
                # Subscribe to 30-min ES candles from start_dt
                symbol = '/ES{=30m}'
                await streamer.subscribe_candle(symbol, from_time_ms)
                
                # Collect candles until we have enough or timeout
                import asyncio as aio
                try:
                    while True:
                        candle = await aio.wait_for(streamer.get_event(Candle), timeout=10)
                        candles.append({
                            'datetime': datetime.fromtimestamp(candle.time / 1000),
                            'open': float(candle.open),
                            'high': float(candle.high),
                            'low': float(candle.low),
                            'close': float(candle.close),
                            'volume': float(candle.volume) if candle.volume else 0,
                        })
                except aio.TimeoutError:
                    pass  # Done collecting
            
            return candles
        
        # Run async in sync context
        loop = asyncio.new_event_loop()
        candles = loop.run_until_complete(_fetch())
        loop.close()
        
        if candles:
            df = pd.DataFrame(candles)
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.sort_values('datetime').reset_index(drop=True)
            # Filter to date range
            df = df[(df['datetime'] >= start_dt) & (df['datetime'] <= end_dt)]
            if len(df) > 0:
                return {'ok': True, 'data': df}
        return {'ok': False, 'error': 'No candle data received from DXLink'}
    except ImportError:
        return {'ok': False, 'error': 'tastytrade SDK not installed'}
    except Exception as e:
        return {'ok': False, 'error': str(e)}


def fetch_es_candles(prior_date, next_date) -> DataSourceStatus:
    """
    Master fetcher: tries yfinance first (reliable for historical),
    then Tastytrade SDK, reports status clearly.
    """
    status = DataSourceStatus()
    
    start_str = prior_date.strftime('%Y-%m-%d')
    end_str = (next_date + timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Try yfinance first (most reliable for historical 30-min candles)
    result = fetch_yfinance_candles(start_str, end_str)
    if result['ok']:
        status.yfinance_ok = True
        status.source_used = "yfinance"
        status.candles = result['data']
        return status
    
    yf_error = result['error']
    
    # Fallback: try Tastytrade SDK
    start_dt = datetime.combine(prior_date, time(8, 30))
    end_dt = datetime.combine(next_date, time(15, 0))
    result = fetch_tastytrade_candles_via_sdk(start_dt, end_dt)
    if result['ok']:
        status.tastytrade_ok = True
        status.source_used = "tastytrade"
        status.candles = result['data']
        return status
    
    tt_error = result['error']
    status.error_msg = f"yfinance: {yf_error} | Tastytrade: {tt_error}"
    status.source_used = "manual"
    return status


def calculate_es_spx_spread(es_candles: pd.DataFrame, session_date) -> dict:
    """
    Calculate the ES - SPX spread by comparing ES futures to SPX index
    during overlapping RTH hours. Returns the last spread value.
    """
    try:
        import yfinance as yf
        
        start_str = session_date.strftime('%Y-%m-%d')
        end_str = (session_date + timedelta(days=1)).strftime('%Y-%m-%d')
        
        spx = yf.Ticker("^GSPC")
        spx_df = spx.history(start=start_str, end=end_str, interval="30m")
        
        if len(spx_df) == 0:
            return {'ok': False, 'error': 'No SPX data', 'spread': 0.0}
        
        spx_df = spx_df.reset_index()
        col_map = {}
        for col in spx_df.columns:
            cl = col.lower().replace(' ', '_')
            if 'datetime' in cl or 'date' in cl:
                col_map[col] = 'datetime'
            elif cl == 'close':
                col_map[col] = 'close'
        spx_df = spx_df.rename(columns=col_map)
        if 'datetime' not in spx_df.columns:
            spx_df = spx_df.rename(columns={spx_df.columns[0]: 'datetime'})
        spx_df['datetime'] = pd.to_datetime(spx_df['datetime'])
        if spx_df['datetime'].dt.tz is not None:
            import pytz
            ct = pytz.timezone('America/Chicago')
            spx_df['datetime'] = spx_df['datetime'].dt.tz_convert(ct).dt.tz_localize(None)
        
        # Round both to nearest 30 min for matching
        es_rth = es_candles.copy()
        es_rth['dt_round'] = es_rth['datetime'].dt.round('30min')
        spx_df['dt_round'] = spx_df['datetime'].dt.round('30min')
        
        merged = es_rth.merge(spx_df[['dt_round', 'close']], on='dt_round', 
                               suffixes=('_es', '_spx'), how='inner')
        
        if len(merged) == 0:
            return {'ok': False, 'error': 'No overlapping candles', 'spread': 0.0}
        
        if 'close_es' in merged.columns and 'close_spx' in merged.columns:
            spreads = merged['close_es'] - merged['close_spx']
        else:
            return {'ok': False, 'error': 'Column merge issue', 'spread': 0.0}
        
        return {
            'ok': True, 
            'spread': round(float(spreads.iloc[-1]), 2),
            'avg_spread': round(float(spreads.mean()), 2),
            'samples': len(merged)
        }
    except ImportError:
        return {'ok': False, 'error': 'yfinance not installed', 'spread': 0.0}
    except Exception as e:
        return {'ok': False, 'error': str(e), 'spread': 0.0}


def apply_offset(items: list, offset: float) -> list:
    """Subtract offset from prices (ES → SPX conversion)."""
    return [{'price': item['price'] - offset, 'time': item['time']} for item in items]


def fetch_live_price() -> dict:
    """Fetch current ES=F price from yfinance for live tracking."""
    try:
        import yfinance as yf
        es = yf.Ticker("ES=F")
        data = es.history(period="1d", interval="1m")
        if len(data) > 0:
            last = data.iloc[-1]
            last_time = data.index[-1]
            if hasattr(last_time, 'tz') and last_time.tz is not None:
                import pytz
                ct = pytz.timezone('America/Chicago')
                last_time = last_time.tz_convert(ct).tz_localize(None)
            return {
                'ok': True,
                'price': float(last['Close']),
                'high': float(last['High']),
                'low': float(last['Low']),
                'time': last_time,
                'source': 'ES=F'
            }
        return {'ok': False, 'error': 'No data', 'price': 0}
    except Exception as e:
        return {'ok': False, 'error': str(e), 'price': 0}


def estimate_option_premium(spx_price: float, strike: float, vix: float,
                             hours_to_expiry: float, opt_type: str) -> float:
    """
    Estimate 0DTE SPX option premium using Black-Scholes with 0DTE adjustment.
    
    Real 0DTE options trade at a discount to theoretical BS because:
    - Realized vol is lower than implied for short timeframes
    - Bid-ask spread compresses theoretical value
    - Market makers discount extreme gamma risk
    
    We apply a 0.35x discount factor to align with typical 0DTE market prices.
    """
    import math
    
    if hours_to_expiry <= 0:
        if opt_type == 'CALL':
            return max(0, spx_price - strike)
        else:
            return max(0, strike - spx_price)
    
    T = hours_to_expiry / (252 * 6.5)  # fraction of trading year
    sigma = vix / 100.0  # annualized vol
    
    if T <= 0 or sigma <= 0:
        return 0.25
    
    def norm_cdf(x):
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))
    
    vol_t = sigma * math.sqrt(T)
    
    # Standard Black-Scholes
    d1 = (math.log(spx_price / strike)) / vol_t + 0.5 * vol_t
    d2 = d1 - vol_t
    
    if opt_type == 'CALL':
        premium = spx_price * norm_cdf(d1) - strike * norm_cdf(d2)
    else:
        premium = strike * norm_cdf(-d2) - spx_price * norm_cdf(-d1)
    
    # 0DTE discount: real market trades at ~35% of theoretical BS for OTM options
    # This narrows as options go ITM (intrinsic value dominates)
    intrinsic = max(0, (strike - spx_price) if opt_type == 'PUT' else (spx_price - strike))
    extrinsic = max(0, premium - intrinsic)
    adjusted = intrinsic + extrinsic * 0.35
    
    return max(0.25, round(adjusted * 4) / 4)  # min $0.25, round to nearest 0.25


def project_premium_at_scenarios(current_spx: float, strike: float, vix: float,
                                  opt_type: str, stop_price: float,
                                  tp1_price: float, tp2_price: float,
                                  base_premium: float = None,
                                  current_hours: float = 6.5,
                                  entry_hours: float = 5.9) -> dict:
    """
    Project option premium at 9:05 AM entry under three scenarios using actual trade levels.
    
    If base_premium (live 8:30 AM price) is available, calibrates the model to match it,
    then projects forward. Otherwise uses pure estimation.
    
    Args:
        current_spx: SPX price right now
        strike: Option strike
        vix: Current VIX
        opt_type: 'CALL' or 'PUT'
        stop_price: SPX stop loss level
        tp1_price: SPX Target 1 level
        tp2_price: SPX Target 2 level  
        base_premium: Live premium pulled at 8:30 AM (None if unavailable)
        current_hours: Hours to expiry at time of live pull (default 6.5 = 8:30 AM)
        entry_hours: Hours to expiry at 9:05 AM entry (default 5.9)
    
    Returns:
        Dict with scenario projections
    """
    # Estimate premiums at different SPX levels at entry time
    est_at_entry = estimate_option_premium(current_spx, strike, vix, entry_hours, opt_type)
    est_at_stop = estimate_option_premium(stop_price, strike, vix, entry_hours, opt_type)
    est_at_tp1 = estimate_option_premium(tp1_price, strike, vix, entry_hours, opt_type)
    est_at_tp2 = estimate_option_premium(tp2_price, strike, vix, entry_hours, opt_type)
    
    # If we have a live base premium, calibrate with a scaling factor
    if base_premium and base_premium > 0:
        est_now = estimate_option_premium(current_spx, strike, vix, current_hours, opt_type)
        if est_now > 0:
            calibration = base_premium / est_now
        else:
            calibration = 1.0
        
        est_at_entry = round(est_at_entry * calibration * 4) / 4
        est_at_stop = round(est_at_stop * calibration * 4) / 4
        est_at_tp1 = round(est_at_tp1 * calibration * 4) / 4
        est_at_tp2 = round(est_at_tp2 * calibration * 4) / 4
    
    return {
        'at_entry': max(0.25, est_at_entry),
        'at_stop': max(0.25, est_at_stop),
        'at_tp1': max(0.25, est_at_tp1),
        'at_tp2': max(0.25, est_at_tp2),
        'calibrated': base_premium is not None and base_premium > 0,
    }


# ============================================================
# AUTO-DETECTION ENGINE
# Detect bounces, rejections, and wick extremes from candle data
# ============================================================

def filter_ny_session(df: pd.DataFrame, session_date) -> pd.DataFrame:
    """
    Filter candles to only the NY regular session: 8:30 AM - 3:00 PM CT.
    Uses a flexible window to catch candles even if timestamps are slightly off.
    """
    session_start = datetime.combine(session_date, time(8, 0))   # slightly early to catch 8:30
    session_end = datetime.combine(session_date, time(15, 30))    # slightly late to catch 3:00
    
    mask = (df['datetime'] >= session_start) & (df['datetime'] <= session_end)
    filtered = df[mask].copy().reset_index(drop=True)
    return filtered


def detect_inflections(ny_candles: pd.DataFrame) -> dict:
    """
    Auto-detect bounces and rejections from 30-min candle data.
    
    Uses LINE CHART logic: closing prices only for bounces/rejections.
    
    Bounce = trough: close[i] <= close[i-1] AND close[i] < close[i+1]
      OR close[i] < close[i-1] AND close[i] <= close[i+1]
      (handles flat bottoms)
    
    Rejection = peak: close[i] >= close[i-1] AND close[i] > close[i+1]
      OR close[i] > close[i-1] AND close[i] >= close[i+1]
      (handles flat tops)
    
    For multi-candle patterns (W-bottoms, M-tops), uses a 5-candle window:
      If close[i] is the lowest/highest within a 5-candle window centered on it,
      it's also detected as a bounce/rejection.
    
    Highest Wick = highest HIGH of a BEARISH candle (close < open)
      - Exclude the 8:30 AM candle (opening noise)
    
    Lowest Wick = lowest LOW of a BULLISH candle (close > open)
      - Exclude the 8:30 AM candle (opening noise)
    """
    if len(ny_candles) < 3:
        return {'bounces': [], 'rejections': [], 'highest_wick': None, 'lowest_wick': None}
    
    closes = ny_candles['close'].values
    times = ny_candles['datetime'].values
    opens = ny_candles['open'].values
    highs = ny_candles['high'].values
    lows = ny_candles['low'].values
    n = len(closes)
    
    bounces = []
    rejections = []
    bounce_times = set()
    rejection_times = set()
    
    # Pass 1: Standard 3-candle pattern (with <= to catch flat edges)
    for i in range(1, n - 1):
        t = pd.Timestamp(times[i]).to_pydatetime()
        
        # Bounce: local trough
        is_bounce = (
            (closes[i] < closes[i-1] and closes[i] < closes[i+1]) or
            (closes[i] <= closes[i-1] and closes[i] < closes[i+1] and closes[i] < closes[max(0,i-2)] if i >= 2 else False) or
            (closes[i] < closes[i-1] and closes[i] <= closes[i+1] and closes[i] < closes[min(n-1,i+2)] if i < n-2 else False)
        )
        
        if is_bounce:
            bounces.append({'price': float(closes[i]), 'time': t})
            bounce_times.add(i)
        
        # Rejection: local peak
        is_rejection = (
            (closes[i] > closes[i-1] and closes[i] > closes[i+1]) or
            (closes[i] >= closes[i-1] and closes[i] > closes[i+1] and closes[i] > closes[max(0,i-2)] if i >= 2 else False) or
            (closes[i] > closes[i-1] and closes[i] >= closes[i+1] and closes[i] > closes[min(n-1,i+2)] if i < n-2 else False)
        )
        
        if is_rejection:
            rejections.append({'price': float(closes[i]), 'time': t})
            rejection_times.add(i)
    
    # Pass 2: 5-candle window for broader patterns (W-bottom, M-top)
    for i in range(2, n - 2):
        if i in bounce_times or i in rejection_times:
            continue
        
        t = pd.Timestamp(times[i]).to_pydatetime()
        window = closes[i-2:i+3]
        
        # Bounce: lowest in 5-candle window
        if closes[i] == window.min() and closes[i] < closes[i-2] and closes[i] < closes[i+2]:
            bounces.append({'price': float(closes[i]), 'time': t})
        
        # Rejection: highest in 5-candle window
        if closes[i] == window.max() and closes[i] > closes[i-2] and closes[i] > closes[i+2]:
            rejections.append({'price': float(closes[i]), 'time': t})
    
    # Sort by time
    bounces.sort(key=lambda x: x['time'])
    rejections.sort(key=lambda x: x['time'])
    
    # Highest wick: highest HIGH of a BEARISH candle (close < open)
    # Only consider candles from 9:00 AM to 2:30 PM CT (exclude open/close noise)
    bearish_mask = closes < opens
    highest_wick = None
    if bearish_mask.any():
        best_high = -1
        best_idx = None
        for idx in range(n):
            if not bearish_mask[idx]:
                continue
            t = pd.Timestamp(times[idx]).to_pydatetime()
            # Skip opening noise (before 9:00 AM)
            if t.hour < 9:
                continue
            # Skip closing noise (2:30 PM and later)
            if t.hour >= 15 or (t.hour == 14 and t.minute >= 30):
                continue
            if highs[idx] > best_high:
                best_high = highs[idx]
                best_idx = idx
        
        if best_idx is not None:
            highest_wick = {
                'price': float(highs[best_idx]),
                'time': pd.Timestamp(times[best_idx]).to_pydatetime()
            }
    
    # Lowest wick: lowest LOW of a BULLISH candle (close > open)
    # Only consider candles from 9:00 AM to 2:30 PM CT (exclude open/close noise)
    bullish_mask = closes > opens
    lowest_wick = None
    if bullish_mask.any():
        best_low = float('inf')
        best_idx = None
        for idx in range(n):
            if not bullish_mask[idx]:
                continue
            t = pd.Timestamp(times[idx]).to_pydatetime()
            # Skip opening noise (before 9:00 AM)
            if t.hour < 9:
                continue
            # Skip closing noise (2:30 PM and later)
            if t.hour >= 15 or (t.hour == 14 and t.minute >= 30):
                continue
            if lows[idx] < best_low:
                best_low = lows[idx]
                best_idx = idx
        
        if best_idx is not None:
            lowest_wick = {
                'price': float(lows[best_idx]),
                'time': pd.Timestamp(times[best_idx]).to_pydatetime()
            }
    
    return {
        'bounces': bounces,
        'rejections': rejections,
        'highest_wick': highest_wick,
        'lowest_wick': lowest_wick,
    }


# ============================================================
# MAIN APPLICATION
# ============================================================

def main():
    # Header
    st.markdown('<div class="main-header">SPX Prophet Next Gen</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Structural Flow Engine • Futures & Options</div>', unsafe_allow_html=True)
    
    # Live price tracking toggle
    live_mode = st.toggle("🔴 LIVE MODE", value=False, help="Auto-refresh every 30 seconds with current ES price")
    
    # ============================================================
    # SIDEBAR: Input Panel
    # ============================================================
    with st.sidebar:
        st.markdown("### 📊 Prior NY Session Data")
        st.markdown("---")
        
        # Date selection
        prior_date = st.date_input("Prior NY Session Date", 
                                    value=datetime.now().date() - timedelta(days=1),
                                    help="The NY session day you're analyzing")
        
        next_date = st.date_input("Next Trading Day",
                                   value=datetime.now().date(),
                                   help="The day you're projecting lines into")
        
        st.markdown("---")
        
        # Data Source Selection
        st.markdown("### 📡 Data Source")
        data_mode = st.radio(
            "How to get ES data:",
            ["Auto (Tastytrade → yfinance)", "Manual Input"],
            index=0,
            help="Auto tries Tastytrade first, then Yahoo Finance. Manual lets you enter values from TradingView."
        )
        
        # Initialize variables
        bounces = []
        rejections = []
        highest_wick = {'price': 6920.0, 'time': datetime.combine(prior_date, time(10, 0))}
        lowest_wick = {'price': 6840.0, 'time': datetime.combine(prior_date, time(14, 0))}
        data_status = DataSourceStatus()
        
        if data_mode == "Auto (Tastytrade → yfinance)":
            st.caption("📡 Tries yfinance (ES=F) first, then Tastytrade SDK")
            
            fetch_btn = st.button("🔄 Fetch ES Data", use_container_width=True)
            
            # Status display
            if fetch_btn or st.session_state.get('last_fetch_status'):
                if fetch_btn:
                    with st.spinner("Fetching ES candle data..."):
                        data_status = fetch_es_candles(prior_date, next_date)
                        st.session_state['last_fetch_status'] = data_status
                        st.session_state['last_fetch_candles'] = data_status.candles
                else:
                    data_status = st.session_state.get('last_fetch_status', DataSourceStatus())
                
                # Show connection status
                if data_status.source_used == "yfinance":
                    st.success("✅ **Yahoo Finance (ES=F)** — Connected")
                elif data_status.source_used == "tastytrade":
                    st.success("✅ **Tastytrade DXLink** — Connected")
                else:
                    st.error("❌ **No data source available**")
                    if data_status.error_msg:
                        st.caption(data_status.error_msg)
                    st.info("Falling back to manual input below.")
                
                # If we got candle data, run auto-detection
                if data_status.candles is not None and len(data_status.candles) > 0:
                    ny_candles = filter_ny_session(data_status.candles, prior_date)
                    
                    if len(ny_candles) >= 3:
                        detected = detect_inflections(ny_candles)
                        
                        # Debug: show raw candle data
                        with st.expander(f"🔬 Raw NY Candles ({len(ny_candles)} bars)", expanded=False):
                            debug_df = ny_candles[['datetime', 'open', 'high', 'low', 'close']].copy()
                            debug_df['datetime'] = debug_df['datetime'].dt.strftime('%I:%M %p')
                            debug_df = debug_df.rename(columns={'datetime': 'Time'})
                            for col in ['open', 'high', 'low', 'close']:
                                debug_df[col] = debug_df[col].map(lambda x: f"{x:.2f}")
                            st.dataframe(debug_df, use_container_width=True, hide_index=True)
                        
                        # Calculate ES-SPX spread
                        st.markdown("---")
                        st.markdown("### 📐 ES → SPX Offset")
                        
                        spread_result = calculate_es_spx_spread(data_status.candles, prior_date)
                        
                        if spread_result['ok']:
                            auto_spread = spread_result['spread']
                            st.caption(f"Auto-detected ES-SPX spread: **{auto_spread:+.2f}** (from {spread_result['samples']} matched candles)")
                            # Store for the Settings section to pick up as default
                            if '_es_offset' not in st.session_state or st.session_state.get('_auto_spread_fresh', False):
                                st.session_state['_es_offset'] = auto_spread
                                st.session_state['_auto_spread_fresh'] = False
                        else:
                            st.caption(f"Could not auto-detect spread: {spread_result['error']}")
                        
                        # Use the global offset from Settings
                        es_offset = st.session_state.get('_es_offset', 0.0)
                        
                        # Apply offset to detected values
                        if es_offset != 0:
                            if detected['bounces']:
                                detected['bounces'] = apply_offset(detected['bounces'], es_offset)
                            if detected['rejections']:
                                detected['rejections'] = apply_offset(detected['rejections'], es_offset)
                            if detected['highest_wick']:
                                detected['highest_wick']['price'] -= es_offset
                            if detected['lowest_wick']:
                                detected['lowest_wick']['price'] -= es_offset
                            st.caption(f"✅ Offset of {es_offset:+.2f} applied to all levels")
                        
                        st.markdown("---")
                        st.markdown("### 🔍 Auto-Detected (SPX-adjusted)" if es_offset != 0 else "### 🔍 Auto-Detected")
                        
                        # Bounces
                        if detected['bounces']:
                            st.markdown(f"**Bounces found: {len(detected['bounces'])}**")
                            for b in detected['bounces']:
                                st.caption(f"↗ {b['price']:.2f} @ {b['time'].strftime('%I:%M %p')}")
                            bounces = detected['bounces']
                        else:
                            st.caption("No bounces detected")
                        
                        # Rejections
                        if detected['rejections']:
                            st.markdown(f"**Rejections found: {len(detected['rejections'])}**")
                            for r in detected['rejections']:
                                st.caption(f"↘ {r['price']:.2f} @ {r['time'].strftime('%I:%M %p')}")
                            rejections = detected['rejections']
                        else:
                            st.caption("No rejections detected")
                        
                        # Highest wick (bearish candle)
                        if detected['highest_wick']:
                            hw = detected['highest_wick']
                            st.markdown(f"**Highest Wick (bearish): {hw['price']:.2f}** @ {hw['time'].strftime('%I:%M %p')}")
                            highest_wick = hw
                        else:
                            st.caption("No bearish candle wick found")
                        
                        # Lowest wick (bullish candle)
                        if detected['lowest_wick']:
                            lw = detected['lowest_wick']
                            st.markdown(f"**Lowest Wick (bullish): {lw['price']:.2f}** @ {lw['time'].strftime('%I:%M %p')}")
                            lowest_wick = lw
                        else:
                            st.caption("No bullish candle wick found")
                        
                        st.markdown("---")
                        st.markdown("### ✏️ Override Auto-Detection")
                        st.caption("Edit any value below to override what was detected.")
                        
                        # Allow manual override of auto-detected values
                        override_bounces = st.checkbox("Override bounces", value=False, key="override_b")
                        override_rejections = st.checkbox("Override rejections", value=False, key="override_r")
                        override_wicks = st.checkbox("Override wicks", value=False, key="override_w")
                    else:
                        st.warning(f"Only {len(ny_candles)} NY session candles found. Need at least 3.")
                        data_status.source_used = "manual"
                else:
                    if fetch_btn:
                        st.info("No candle data retrieved. Use manual input.")
            
            # If overriding or no data, show manual inputs
            show_manual_bounces = (data_status.source_used == "manual" or 
                                    st.session_state.get('override_b', False))
            show_manual_rejections = (data_status.source_used == "manual" or 
                                       st.session_state.get('override_r', False))
            show_manual_wicks = (data_status.source_used == "manual" or 
                                  st.session_state.get('override_w', False))
        else:
            # Full manual mode
            show_manual_bounces = True
            show_manual_rejections = True
            show_manual_wicks = True
        
        # Manual input sections (shown when needed)
        if show_manual_bounces:
            st.markdown("---")
            st.markdown("### 🔺 Bounces (Line Chart Troughs)")
            st.markdown("*Close prices where price dipped and reversed up*")
            
            num_bounces = st.number_input("Number of bounces", min_value=0, max_value=8, value=2, key="num_bounces")
            
            bounces = []
            for i in range(num_bounces):
                col1, col2 = st.columns(2)
                with col1:
                    price = st.number_input(f"Bounce {i+1} Price", 
                                            value=6860.0, step=0.5, key=f"bounce_price_{i}",
                                            format="%.2f")
                with col2:
                    hour = st.selectbox(f"Hour", 
                                        options=list(range(8, 16)),
                                        index=2, key=f"bounce_hour_{i}",
                                        format_func=lambda x: f"{x}:00" if x < 12 else f"{x-12 if x > 12 else 12}:00 PM")
                    minute = st.selectbox(f"Min",
                                          options=[0, 30],
                                          index=0, key=f"bounce_min_{i}")
                
                bounce_time = datetime.combine(prior_date, time(hour, minute))
                bounces.append({'price': price, 'time': bounce_time})
        
        if show_manual_rejections:
            st.markdown("---")
            st.markdown("### 🔻 Rejections (Line Chart Peaks)")
            st.markdown("*Close prices where price pushed up and reversed down*")
            
            num_rejections = st.number_input("Number of rejections", min_value=0, max_value=8, value=2, key="num_rejections")
            
            rejections = []
            for i in range(num_rejections):
                col1, col2 = st.columns(2)
                with col1:
                    price = st.number_input(f"Rejection {i+1} Price",
                                            value=6910.0, step=0.5, key=f"rej_price_{i}",
                                            format="%.2f")
                with col2:
                    hour = st.selectbox(f"Hour",
                                        options=list(range(8, 16)),
                                        index=2, key=f"rej_hour_{i}",
                                        format_func=lambda x: f"{x}:00" if x < 12 else f"{x-12 if x > 12 else 12}:00 PM")
                    minute = st.selectbox(f"Min",
                                          options=[0, 30],
                                          index=0, key=f"rej_min_{i}")
                
                rej_time = datetime.combine(prior_date, time(hour, minute))
                rejections.append({'price': price, 'time': rej_time})
        
        if show_manual_wicks:
            st.markdown("---")
            st.markdown("### 📍 Session Extremes (Candlestick Wicks)")
            st.markdown("*Highest wick = bearish candle • Lowest wick = bullish candle*")
            st.caption("*Exclude if first bearish/bullish candle is 8:30 AM*")
            
            col1, col2 = st.columns(2)
            with col1:
                hw_price = st.number_input("Highest Wick Price", value=6920.0, step=0.5, format="%.2f")
            with col2:
                hw_hour = st.selectbox("HW Hour", options=list(range(8, 16)), index=2, key="hw_hour",
                                        format_func=lambda x: f"{x}:00" if x < 12 else f"{x-12 if x > 12 else 12}:00 PM")
                hw_min = st.selectbox("HW Min", options=[0, 30], index=0, key="hw_min")
            
            highest_wick = {
                'price': hw_price,
                'time': datetime.combine(prior_date, time(hw_hour, hw_min))
            }
            
            col1, col2 = st.columns(2)
            with col1:
                lw_price = st.number_input("Lowest Wick Price", value=6840.0, step=0.5, format="%.2f")
            with col2:
                lw_hour = st.selectbox("LW Hour", options=list(range(8, 16)), index=2, key="lw_hour",
                                        format_func=lambda x: f"{x}:00" if x < 12 else f"{x-12 if x > 12 else 12}:00 PM")
                lw_min = st.selectbox("LW Min", options=[0, 30], index=0, key="lw_min")
            
            lowest_wick = {
                'price': lw_price,
                'time': datetime.combine(prior_date, time(lw_hour, lw_min))
            }
        
        st.markdown("---")
        st.markdown("### ⚙️ Settings")
        
        # Rate from secrets (keeps your edge private)
        default_rate = 13/25
        try:
            default_rate = float(st.secrets.get("rate", default_rate))
        except:
            pass
        rate = st.number_input("Rate per candle", value=default_rate, step=0.01, format="%.2f",
                               help="Your proprietary rate (add 'rate' to secrets.toml to persist)")
        
        # Universal ES-SPX offset (always available)
        # Auto-detected value may have been stored from auto-fetch
        auto_offset_val = st.session_state.get('_es_offset', 0.0)
        es_spx_offset = st.number_input("ES - SPX offset", value=auto_offset_val, step=0.25, format="%.2f",
                                         key="global_es_offset",
                                         help="NY tab uses SPX (subtracts offset). Asian tab uses ES (adds offset back).")
        st.session_state['_es_offset'] = es_spx_offset
        
        show_all_lines = st.checkbox("Show all projected lines", value=True)
        show_session_boxes = st.checkbox("Show session boxes", value=True)
    
    # ============================================================
    # CALCULATIONS
    # ============================================================
    
    # Override global rate if changed
    global RATE_PER_CANDLE
    RATE_PER_CANDLE = rate
    
    # Calculate 9 AM levels
    next_day_dt = datetime.combine(next_date, time(9, 0))
    levels = calculate_nine_am_levels(bounces, rejections, highest_wick, lowest_wick, next_day_dt)
    
    # ============================================================
    # LIVE PRICE TRACKING
    # ============================================================
    live_price_data = None
    es_offset_val = st.session_state.get('_es_offset', 0.0)
    
    if live_mode:
        # Auto-refresh every 30 seconds
        try:
            from streamlit_autorefresh import st_autorefresh
            st_autorefresh(interval=30000, limit=None, key="live_refresh")
        except ImportError:
            # Fallback: manual refresh button
            st.caption("⚠️ Install `streamlit-autorefresh` for auto-polling. Using manual refresh.")
            if st.button("🔄 Refresh Price", key="manual_refresh"):
                st.rerun()
        
        live_price_data = fetch_live_price()
        
        if live_price_data['ok']:
            es_price = live_price_data['price']
            spx_price = es_price - es_offset_val
            price_time = live_price_data['time']
            time_str = price_time.strftime('%I:%M:%S %p') if hasattr(price_time, 'strftime') else str(price_time)
            
            # Get level values
            hw_val_live = levels['key_levels']['highest_wick_ascending']['value_at_9am'] if levels['key_levels']['highest_wick_ascending'] else None
            hb_val_live = levels['key_levels']['highest_bounce_ascending']['value_at_9am'] if levels['key_levels']['highest_bounce_ascending'] else None
            lr_val_live = levels['key_levels']['lowest_rejection_descending']['value_at_9am'] if levels['key_levels']['lowest_rejection_descending'] else None
            lw_val_live = levels['key_levels']['lowest_wick_descending']['value_at_9am'] if levels['key_levels']['lowest_wick_descending'] else None
            
            # Determine live position
            all_levels = {}
            if hw_val_live: all_levels['HW Asc'] = hw_val_live
            if hb_val_live: all_levels['HB Asc'] = hb_val_live
            if lr_val_live: all_levels['LR Desc'] = lr_val_live
            if lw_val_live: all_levels['LW Desc'] = lw_val_live
            
            # Live signal
            live_signal = ""
            live_color = "#ffd740"
            if hw_val_live and hb_val_live and lr_val_live and lw_val_live:
                asc_h = max(hw_val_live, hb_val_live)
                asc_l = min(hw_val_live, hb_val_live)
                desc_h = max(lr_val_live, lw_val_live)
                desc_l = min(lr_val_live, lw_val_live)
                
                if spx_price > asc_h:
                    live_signal = "BULLISH TREND DAY"
                    live_color = "#00e676"
                elif spx_price >= asc_l:
                    live_signal = "BETWEEN ASCENDING"
                    live_color = "#ffd740"
                elif spx_price > desc_h:
                    live_signal = "BEARISH BIAS"
                    live_color = "#ff5252"
                elif spx_price >= desc_l:
                    live_signal = "BETWEEN DESCENDING"
                    live_color = "#ffd740"
                else:
                    live_signal = "BEARISH TREND DAY"
                    live_color = "#ff1744"
            
            # Distances
            distances = []
            for name, val in sorted(all_levels.items(), key=lambda x: x[1], reverse=True):
                diff = spx_price - val
                arrow = "▲" if diff > 0 else "▼"
                distances.append(f"{name}: {val:.2f} ({arrow}{abs(diff):.2f})")
            
            # Display live banner
            offset_note = f" (offset {es_offset_val:+.1f})" if es_offset_val != 0 else ""
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #0d1117 0%, #131a2e 100%); border: 2px solid {live_color}; 
                        border-radius: 12px; padding: 15px; margin: 10px 0; text-align: center;">
                <div style="font-family: 'Rajdhani'; color: #8892b0; font-size: 0.85rem;">
                    🔴 LIVE • ES=F @ {time_str}{offset_note}
                </div>
                <div style="font-family: 'Orbitron'; font-size: 2.2rem; color: {live_color}; margin: 5px 0;">
                    {spx_price:.2f}
                </div>
                <div style="font-family: 'Orbitron'; font-size: 1rem; color: {live_color};">
                    {live_signal}
                </div>
                <div style="font-family: 'JetBrains Mono'; font-size: 0.8rem; color: #8892b0; margin-top: 8px;">
                    {'  •  '.join(distances)}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning(f"Live price unavailable: {live_price_data.get('error', 'Unknown')}")
    
    # ============================================================
    # MAIN CONTENT: Tabs
    # ============================================================
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 STRUCTURAL MAP", 
        "🌙 ASIAN SESSION (Futures)", 
        "☀️ NY SESSION (Options)",
        "📋 TRADE LOG",
        "🔬 BACKTEST"
    ])
    
    # ============================================================
    # TAB 1: STRUCTURAL MAP
    # ============================================================
    with tab1:
        st.markdown("### 9:00 AM CT Decision Levels")
        
        # Display the four key levels in a uniform CSS grid
        hw_asc = levels['key_levels']['highest_wick_ascending']
        hb_asc = levels['key_levels']['highest_bounce_ascending']
        lr_desc = levels['key_levels']['lowest_rejection_descending']
        lw_desc = levels['key_levels']['lowest_wick_descending']
        
        cards_html = '<div style="display:grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 10px 0;">'
        
        for label, level, color_class in [
            ("HW Ascending ↗", hw_asc, "bear"),
            ("HB Ascending ↗", hb_asc, "bear"),
            ("LR Descending ↘", lr_desc, "bull"),
            ("LW Descending ↘", lw_desc, "bull"),
        ]:
            if level:
                val = f"{level['value_at_9am']:.2f}"
                anchor = f"{level['anchor_price']:.2f}"
                color = "#ff1744" if color_class == "bear" else "#00e676"
            else:
                val = "—"
                anchor = "—"
                color = "#5a6a8a"
            
            cards_html += f"""
            <div style="background: linear-gradient(145deg, #131a2e 0%, #0d1220 100%);
                        border: 1px solid #1e2d4a; border-radius: 12px; padding: 20px;
                        box-shadow: 0 4px 20px rgba(0,0,0,0.3); text-align: center;">
                <div style="font-family: 'Rajdhani', sans-serif; color: #5a6a8a; font-size: 0.8rem;
                            text-transform: uppercase; letter-spacing: 2px;">{label}</div>
                <div style="font-family: 'JetBrains Mono', monospace; color: {color};
                            font-size: 1.6rem; font-weight: 700; margin: 8px 0;">{val}</div>
                <div style="font-family: 'Rajdhani', sans-serif; color: #5a6a8a; font-size: 0.7rem;">Anchor: {anchor}</div>
            </div>"""
        
        cards_html += '</div>'
        st.markdown(cards_html, unsafe_allow_html=True)
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # ============================================================
        # STRUCTURAL MAP CHART
        # ============================================================
        
        # Chart time range: from prior NY session start through next day NY close
        chart_start = datetime.combine(prior_date, time(8, 30))
        chart_end = datetime.combine(next_date, time(15, 0))
        
        # ============================================================
        # Build master time axis (sequential indices, no gaps)
        # ============================================================
        master_times = []
        scan_t = chart_start
        while scan_t <= chart_end:
            ct_t = scan_t.time()
            wd_t = scan_t.weekday()
            skip = (wd_t == 5 or (wd_t == 6 and ct_t < time(17, 0)) or
                    (wd_t == 4 and ct_t >= time(16, 0)) or
                    (time(16, 0) <= ct_t < time(17, 0)))
            if not skip:
                master_times.append(scan_t)
            scan_t += timedelta(minutes=CANDLE_MINUTES)
        time_to_idx = {t: i for i, t in enumerate(master_times)}
        
        # ============================================================
        # Session block labels for x-axis (clean, professional)
        # ============================================================
        
        # Define session blocks with their display names and boundaries
        prior_wd_chart = prior_date.weekday() if hasattr(prior_date, 'weekday') else datetime.combine(prior_date, time(0,0)).weekday()
        is_friday_chart = prior_wd_chart == 4
        overnight_chart = (next_date - timedelta(days=1)) if is_friday_chart else prior_date
        
        session_blocks = []
        
        # Prior NY session
        ny1_start = datetime.combine(prior_date, time(8, 30))
        ny1_end = datetime.combine(prior_date, time(15, 0))
        day_abbr = prior_date.strftime('%a')
        session_blocks.append(('NY', f"{day_abbr} NY", ny1_start, ny1_end))
        
        if is_friday_chart:
            # Weekend gap: Fri close to Sun globex open
            sun_open = datetime.combine(next_date - timedelta(days=1), time(17, 0))
            session_blocks.append(('Globex', "Sun Globex", sun_open, datetime.combine(next_date - timedelta(days=1), time(19, 0))))
            session_blocks.append(('Tokyo', "Tokyo", datetime.combine(next_date - timedelta(days=1), time(19, 0)), datetime.combine(next_date, time(2, 0))))
        else:
            # Overnight: same day globex through next morning
            session_blocks.append(('Globex', "Globex Open", datetime.combine(prior_date, time(17, 0)), datetime.combine(prior_date, time(19, 0))))
            session_blocks.append(('Tokyo', "Tokyo", datetime.combine(prior_date, time(19, 0)), datetime.combine(next_date, time(2, 0))))
        
        session_blocks.append(('London', "London", datetime.combine(next_date, time(2, 0)), datetime.combine(next_date, time(8, 30))))
        
        next_day_abbr = next_date.strftime('%a')
        ny2_start = datetime.combine(next_date, time(8, 30))
        ny2_end = datetime.combine(next_date, time(15, 0))
        session_blocks.append(('NY2', f"{next_day_abbr} NY", ny2_start, ny2_end))
        
        # Build tick labels: one centered label per session block
        tick_vals = []
        tick_texts = []
        
        for _, label, s_start, s_end in session_blocks:
            # Find indices within this session
            s_indices = [i for i, t in enumerate(master_times) if s_start <= t <= s_end]
            if s_indices:
                # Place label at center of the block
                center_idx = s_indices[len(s_indices) // 2]
                tick_vals.append(center_idx)
                tick_texts.append(label)
        
        # Also add the 9 AM marker between sessions
        nine_am_dt = datetime.combine(next_date, time(9, 0))
        if nine_am_dt in time_to_idx:
            tick_vals.append(time_to_idx[nine_am_dt])
            tick_texts.append("9AM ▶")
        
        fig = go.Figure()
        
        # ── Session shading with gradient-style overlays ──
        if show_session_boxes:
            session_colors = {
                'NY': ('rgba(0,212,255,0.04)', 'rgba(0,212,255,0.12)'),
                'Globex': ('rgba(255,215,64,0.03)', 'rgba(255,215,64,0.08)'),
                'Tokyo': ('rgba(233,30,99,0.03)', 'rgba(233,30,99,0.08)'),
                'London': ('rgba(123,47,247,0.03)', 'rgba(123,47,247,0.08)'),
                'NY2': ('rgba(0,212,255,0.04)', 'rgba(0,212,255,0.12)'),
            }
            session_labels = {
                'NY': '🇺🇸 NEW YORK', 'Globex': '🌐 GLOBEX', 
                'Tokyo': '🇯🇵 TOKYO', 'London': '🇬🇧 LONDON', 'NY2': '🇺🇸 NY'
            }
            
            for skey, sname, s_start, s_end in session_blocks:
                sfill, sborder = session_colors.get(skey, ('rgba(128,128,128,0.03)', 'rgba(128,128,128,0.1)'))
                s_idx = [i for i, t in enumerate(master_times) if s_start <= t <= s_end]
                if s_idx:
                    fig.add_vrect(x0=min(s_idx), x1=max(s_idx), fillcolor=sfill,
                        line=dict(color=sborder, width=1, dash='dot'))
                    # Session label at top
                    label = session_labels.get(skey, sname)
                    fig.add_annotation(
                        x=(min(s_idx) + max(s_idx)) / 2, y=1.02, yref="paper",
                        text=f"<b>{label}</b>", showarrow=False,
                        font=dict(color=sborder.replace('0.08','0.6').replace('0.12','0.6'), size=9, family="Rajdhani"),
                    )
        
        # ── 9:00 AM Decision Line — prominent golden line ──
        nine_am = datetime.combine(next_date, time(9, 0))
        if nine_am in time_to_idx:
            idx9 = time_to_idx[nine_am]
            fig.add_shape(type="line", x0=idx9, x1=idx9, y0=0, y1=1, yref="paper",
                line=dict(color="#ffd740", width=2, dash="dash"))
            fig.add_annotation(x=idx9, y=1.05, yref="paper", 
                text="<b>9:00 AM DECISION</b>",
                showarrow=False, font=dict(color="#ffd740", size=11, family="Orbitron"))
        
        # ── Ascending lines (bounce/wick) with glow effect ──
        for li, asc_line in enumerate(levels['ascending']):
            series = generate_line_series(asc_line['anchor_price'], asc_line['anchor_time'], chart_start, chart_end, 'ascending')
            xi = [time_to_idx[t] for t, _ in series if t in time_to_idx]
            yi = [p for t, p in series if t in time_to_idx]
            if xi:
                is_wick = asc_line['type'] == 'highest_wick'
                line_color = '#ff1744' if is_wick else '#ff5252'
                line_width = 3 if is_wick else 2
                opacity = 1.0 if is_wick or show_all_lines else 0.35
                
                # Glow layer (wider, transparent) for key lines
                if is_wick or show_all_lines:
                    fig.add_trace(go.Scatter(x=xi, y=yi, mode='lines',
                        line=dict(color=line_color, width=line_width + 6), opacity=0.08,
                        showlegend=False, hoverinfo='skip'))
                
                fig.add_trace(go.Scatter(x=xi, y=yi, mode='lines',
                    name=f"↗ {'HW' if is_wick else f'B{li+1}'}: {asc_line['anchor_price']:.1f}",
                    line=dict(color=line_color, width=line_width, dash='solid' if is_wick else 'dash'),
                    opacity=opacity,
                    hovertemplate=f"{'HW' if is_wick else f'Bounce {li+1}'}<br>Price: %{{y:.2f}}<extra></extra>"))
        
        # ── Descending lines (rejection/wick) with glow effect ──
        for li, desc_line in enumerate(levels['descending']):
            series = generate_line_series(desc_line['anchor_price'], desc_line['anchor_time'], chart_start, chart_end, 'descending')
            xi = [time_to_idx[t] for t, _ in series if t in time_to_idx]
            yi = [p for t, p in series if t in time_to_idx]
            if xi:
                is_wick = desc_line['type'] == 'lowest_wick'
                line_color = '#00e676' if is_wick else '#69f0ae'
                line_width = 3 if is_wick else 2
                opacity = 1.0 if is_wick or show_all_lines else 0.35
                
                # Glow layer
                if is_wick or show_all_lines:
                    fig.add_trace(go.Scatter(x=xi, y=yi, mode='lines',
                        line=dict(color=line_color, width=line_width + 6), opacity=0.08,
                        showlegend=False, hoverinfo='skip'))
                
                fig.add_trace(go.Scatter(x=xi, y=yi, mode='lines',
                    name=f"↘ {'LW' if is_wick else f'R{li+1}'}: {desc_line['anchor_price']:.1f}",
                    line=dict(color=line_color, width=line_width, dash='solid' if is_wick else 'dash'),
                    opacity=opacity,
                    hovertemplate=f"{'LW' if is_wick else f'Rejection {li+1}'}<br>Price: %{{y:.2f}}<extra></extra>"))
        
        # ── 9 AM Key Level horizontal lines with enhanced labels ──
        key = levels['key_levels']
        level_configs = [
            (key['highest_wick_ascending'], '#ff1744', 'HW', '▲'),
            (key['highest_bounce_ascending'], '#ff5252', 'HB', '△'),
            (key['lowest_rejection_descending'], '#69f0ae', 'LR', '▽'),
            (key['lowest_wick_descending'], '#00e676', 'LW', '▼'),
        ]
        for level, color, label, icon in level_configs:
            if level:
                fig.add_shape(type="line", x0=0, x1=len(master_times)-1,
                    y0=level['value_at_9am'], y1=level['value_at_9am'],
                    line=dict(color=color, width=1, dash="dot"))
                fig.add_annotation(x=len(master_times)-1, y=level['value_at_9am'],
                    text=f"<b>{icon} {label}</b> {level['value_at_9am']:.2f}",
                    showarrow=False, font=dict(size=10, color=color, family='JetBrains Mono'), 
                    xshift=8, xanchor="left",
                    bgcolor='rgba(6,9,16,0.8)', bordercolor=color, borderwidth=1, borderpad=3)
        
        # ── Bounce markers with enhanced styling ──
        for bounce in bounces:
            if bounce['time'] in time_to_idx:
                fig.add_trace(go.Scatter(
                    x=[time_to_idx[bounce['time']]], y=[bounce['price']],
                    mode='markers', showlegend=False,
                    marker=dict(symbol='triangle-up', size=14, color='#ff5252',
                        line=dict(width=1.5, color='rgba(255,82,82,0.5)')),
                    hovertemplate=f"<b>BOUNCE</b><br>{bounce['price']:.2f}<br>{bounce['time'].strftime('%I:%M %p')}<extra></extra>"
                ))
        for rejection in rejections:
            if rejection['time'] in time_to_idx:
                fig.add_trace(go.Scatter(
                    x=[time_to_idx[rejection['time']]], y=[rejection['price']],
                    mode='markers', showlegend=False,
                    marker=dict(symbol='triangle-down', size=14, color='#69f0ae',
                        line=dict(width=1.5, color='rgba(105,240,174,0.5)')),
                    hovertemplate=f"<b>REJECTION</b><br>{rejection['price']:.2f}<br>{rejection['time'].strftime('%I:%M %p')}<extra></extra>"
                ))
        
        # ── Wick markers — diamonds with glow ring ──
        if highest_wick['time'] in time_to_idx:
            fig.add_trace(go.Scatter(
                x=[time_to_idx[highest_wick['time']]], y=[highest_wick['price']],
                mode='markers', showlegend=False,
                marker=dict(symbol='diamond', size=16, color='#ff1744',
                    line=dict(width=2, color='rgba(255,23,68,0.6)')),
                hovertemplate=f"<b>HIGHEST WICK</b><br>{highest_wick['price']:.2f}<extra></extra>"
            ))
        if lowest_wick['time'] in time_to_idx:
            fig.add_trace(go.Scatter(
                x=[time_to_idx[lowest_wick['time']]], y=[lowest_wick['price']],
                mode='markers', showlegend=False,
                marker=dict(symbol='diamond', size=16, color='#00e676',
                    line=dict(width=2, color='rgba(0,230,118,0.6)')),
                hovertemplate=f"<b>LOWEST WICK</b><br>{lowest_wick['price']:.2f}<extra></extra>"
            ))
        
        # ── Live price line — golden pulse ──
        if live_mode and live_price_data and live_price_data.get('ok'):
            live_spx = live_price_data['price'] - es_offset_val
            # Glow band
            fig.add_hline(y=live_spx, line_dash="dot", line_color="rgba(255,215,64,0.15)", line_width=12)
            # Main line
            fig.add_hline(y=live_spx, line_dash="dot", line_color="#ffd740", line_width=2,
                          annotation_text=f"<b>◉ LIVE {live_spx:.2f}</b>",
                          annotation_position="right",
                          annotation_font=dict(color="#ffd740", size=12, family="Orbitron"))
        
        # ── Chart layout — terminal cockpit aesthetic ──
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(5,8,16,1)',
            plot_bgcolor='rgba(8,13,22,1)',
            height=750,
            margin=dict(l=10, r=200, t=50, b=60),
            xaxis=dict(
                gridcolor='rgba(30,45,74,0.15)',
                showgrid=True, gridwidth=1,
                zeroline=False,
                tickmode='array', tickvals=tick_vals, ticktext=tick_texts, tickangle=0,
                tickfont=dict(size=11, family='Rajdhani', color='#3a4a6a'),
                showline=True, linecolor='rgba(30,45,74,0.3)', linewidth=1,
                spikemode='across', spikethickness=1, spikecolor='rgba(0,212,255,0.3)',
                spikesnap='cursor', spikedash='dot',
            ),
            yaxis=dict(
                gridcolor='rgba(30,45,74,0.12)',
                showgrid=True, gridwidth=1,
                zeroline=False,
                tickformat='.2f', side='right',
                tickfont=dict(size=11, family='JetBrains Mono', color='#5a6a8a'),
                showline=True, linecolor='rgba(30,45,74,0.3)', linewidth=1,
                spikemode='across', spikethickness=1, spikecolor='rgba(0,212,255,0.3)',
                spikesnap='cursor', spikedash='dot',
            ),
            legend=dict(
                bgcolor='rgba(6,9,16,0.95)', 
                bordercolor='rgba(30,45,74,0.4)', borderwidth=1,
                font=dict(size=10, family='JetBrains Mono', color='#8892b0'), 
                x=1.01, y=1,
                itemsizing='constant',
            ),
            font=dict(family='JetBrains Mono', color='#8892b0'),
            hovermode='x unified',
            hoverlabel=dict(
                bgcolor='rgba(6,9,16,0.95)',
                bordercolor='rgba(0,212,255,0.2)',
                font=dict(family='JetBrains Mono', size=11, color='#ccd6f6'),
            ),
            dragmode='pan',
        )
        
        # Chart config for clean interaction
        chart_config = {
            'displayModeBar': True,
            'modeBarButtonsToRemove': ['autoScale2d', 'lasso2d', 'select2d'],
            'displaylogo': False,
            'scrollZoom': True,
        }
        
        st.plotly_chart(fig, use_container_width=True, config=chart_config)
        
        # ============================================================
        # 9 AM LINE LADDER (all lines sorted by value)
        # ============================================================
        st.markdown("### 📊 Line Ladder @ 9:00 AM CT")
        st.caption("All projected lines sorted by 9 AM value — highest to lowest")
        
        # Build unified ladder
        ladder_9am = []
        for line in levels['ascending']:
            ladder_9am.append({
                'name': line['source'].split(' @ ')[0] if ' @ ' in line['source'] else line['source'],
                'short': f"{'HW' if line['type'] == 'highest_wick' else 'B'} ↗",
                'value': line['value_at_9am'],
                'anchor': line['anchor_price'],
                'change': line['value_at_9am'] - line['anchor_price'],
                'direction': 'ascending',
                'color': '#ff1744' if line['type'] == 'highest_wick' else '#ff5252',
                'is_key': line['type'] in ('highest_wick', 'highest_bounce'),
            })
        for line in levels['descending']:
            ladder_9am.append({
                'name': line['source'].split(' @ ')[0] if ' @ ' in line['source'] else line['source'],
                'short': f"{'LW' if line['type'] == 'lowest_wick' else 'R'} ↘",
                'value': line['value_at_9am'],
                'anchor': line['anchor_price'],
                'change': line['value_at_9am'] - line['anchor_price'],
                'direction': 'descending',
                'color': '#00e676' if line['type'] == 'lowest_wick' else '#69f0ae',
                'is_key': line['type'] in ('lowest_wick', 'lowest_rejection'),
            })
        
        ladder_9am.sort(key=lambda x: x['value'], reverse=True)
        
        if ladder_9am:
            ladder_html = '<div style="font-family: JetBrains Mono, monospace; font-size: 0.85rem;">'
            for i, line in enumerate(ladder_9am):
                bg = 'rgba(255,23,68,0.06)' if line['direction'] == 'ascending' else 'rgba(0,230,118,0.06)'
                border = line['color']
                weight = 'bold' if line['is_key'] else 'normal'
                key_tag = ' ★' if line['is_key'] else ''
                change_sign = '+' if line['change'] >= 0 else ''
                delay = i * 0.04
                ladder_html += f"""
                <div class="ladder-row" style="border-left: 3px solid {border};
                            background: {bg}; animation: fade-in-up 0.3s ease {delay}s both;">
                    <span style="color: {line['color']}; min-width: 140px; font-weight: {weight};">
                        {line['short']} {line['name'][:20]}{key_tag}
                    </span>
                    <span style="color: #ccd6f6; font-weight: 700; min-width: 80px; text-align:right;">
                        {line['value']:.2f}
                    </span>
                    <span style="color: #3a4a6a; font-size: 0.73rem; min-width: 100px; text-align:right;">
                        Anchor: {line['anchor']:.2f}
                    </span>
                    <span style="color: {'#00e676' if line['change'] >= 0 else '#ff5252'}; font-size: 0.73rem; min-width: 70px; text-align:right;">
                        {change_sign}{line['change']:.2f}
                    </span>
                </div>"""
            ladder_html += '</div>'
            st.markdown(ladder_html, unsafe_allow_html=True)
            
            st.caption("★ = Key decision level (highest bounce, lowest rejection, wicks)")
    
    # ============================================================
    # TAB 2: ASIAN SESSION FUTURES — 6 PM DECISION FRAMEWORK
    # ============================================================
    with tab2:
        st.markdown("### 🌙 Asian Session — ES Futures (Prop Firm)")
        st.markdown("*6:00 PM Decision • 6-7 PM Trading Window • Flat by 7 PM*")
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Determine correct overnight date
        prior_wd_tab2 = prior_date.weekday() if hasattr(prior_date, 'weekday') else datetime.combine(prior_date, time(0,0)).weekday()
        if prior_wd_tab2 == 4:  # Friday
            overnight_date_tab2 = next_date - timedelta(days=1)  # Sunday
            st.markdown("*⚠️ Friday → Monday: Globex opens Sunday 5:00 PM CT*")
        else:
            overnight_date_tab2 = prior_date
        
        # ============================================================
        # CALCULATE ALL LINE VALUES AT 6 PM CT
        # Lines are stored as SPX-adjusted if offset was applied.
        # For ES futures trading, add the offset back.
        # ============================================================
        decision_time_6pm = datetime.combine(overnight_date_tab2, time(18, 0))
        exit_time_7pm = datetime.combine(overnight_date_tab2, time(19, 0))
        
        # Get the offset — try widget key first, then session state
        es_offset_asian = st.session_state.get('global_es_offset', st.session_state.get('_es_offset', 0.0))
        
        st.markdown(f"""
        <div style="background: rgba(255,215,0,0.08); border: 1px solid rgba(255,215,0,0.3); 
                    border-radius: 8px; padding: 10px; margin: 5px 0; text-align:center;">
            <span style="font-family: JetBrains Mono; color: #ffd740; font-size: 0.85rem;">
                📐 ES-SPX Offset: <strong>{es_offset_asian:+.2f}</strong> 
                {'→ All levels shown in ES terms' if es_offset_asian != 0 else '→ No offset applied (set in sidebar Settings)'}
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        # Build the full line ladder at 6 PM (in ES terms)
        line_ladder_6pm = []
        
        # All ascending lines (bounces + highest wick)
        for line in levels['ascending']:
            val_6pm = calculate_line_value(line['anchor_price'], line['anchor_time'], decision_time_6pm, 'ascending')
            val_7pm = calculate_line_value(line['anchor_price'], line['anchor_time'], exit_time_7pm, 'ascending')
            # Add offset back: SPX → ES
            val_6pm += es_offset_asian
            val_7pm += es_offset_asian
            line_ladder_6pm.append({
                'name': line['source'].split(' @ ')[0] if ' @ ' in line['source'] else line['source'],
                'short': f"{'HW' if line['type'] == 'highest_wick' else 'B'} ↗",
                'value_6pm': val_6pm,
                'value_7pm': val_7pm,
                'direction': 'ascending',
                'anchor': line['anchor_price'] + es_offset_asian,
                'color': '#ff1744' if line['type'] == 'highest_wick' else '#ff5252',
                'is_key': line['type'] == 'highest_wick',
            })
        
        # All descending lines (rejections + lowest wick)
        for line in levels['descending']:
            val_6pm = calculate_line_value(line['anchor_price'], line['anchor_time'], decision_time_6pm, 'descending')
            val_7pm = calculate_line_value(line['anchor_price'], line['anchor_time'], exit_time_7pm, 'descending')
            # Add offset back: SPX → ES
            val_6pm += es_offset_asian
            val_7pm += es_offset_asian
            line_ladder_6pm.append({
                'name': line['source'].split(' @ ')[0] if ' @ ' in line['source'] else line['source'],
                'short': f"{'LW' if line['type'] == 'lowest_wick' else 'R'} ↘",
                'value_6pm': val_6pm,
                'value_7pm': val_7pm,
                'direction': 'descending',
                'anchor': line['anchor_price'] + es_offset_asian,
                'color': '#00e676' if line['type'] == 'lowest_wick' else '#69f0ae',
                'is_key': line['type'] == 'lowest_wick',
            })
        
        # Sort by 6 PM value, highest to lowest
        line_ladder_6pm.sort(key=lambda x: x['value_6pm'], reverse=True)
        
        # ============================================================
        # 6 PM LINE LADDER DISPLAY
        # ============================================================
        st.markdown("### 📊 Line Ladder @ 6:00 PM CT")
        st.caption("All projected lines sorted by 6 PM value — highest to lowest")
        
        if line_ladder_6pm:
            ladder_html = '<div style="font-family: JetBrains Mono; font-size: 0.85rem;">'
            for i, line in enumerate(line_ladder_6pm):
                bg = 'rgba(255,23,68,0.08)' if line['direction'] == 'ascending' else 'rgba(0,230,118,0.08)'
                border = line['color']
                ladder_html += f"""
                <div style="display:flex; justify-content:space-between; align-items:center;
                            padding: 8px 12px; margin: 2px 0; border-left: 3px solid {border};
                            background: {bg}; border-radius: 0 6px 6px 0;">
                    <span style="color: {line['color']}; min-width: 120px;">{line['short']} {line['name'][:20]}</span>
                    <span style="color: #ccd6f6; font-weight: 700;">{line['value_6pm']:.2f}</span>
                    <span style="color: #5a6a8a; font-size: 0.75rem;">→ 7PM: {line['value_7pm']:.2f}</span>
                </div>"""
            ladder_html += '</div>'
            st.markdown(ladder_html, unsafe_allow_html=True)
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # ============================================================
        # 6 PM PRICE INPUT & TRADE SETUP
        # ============================================================
        st.markdown("### 🎯 6:00 PM Decision Framework")
        
        # Auto-fill from live price if available
        asian_default = 6870.0
        if live_mode and live_price_data and live_price_data.get('ok'):
            # Only auto-update if NOT locked
            if not st.session_state.get('asian_6pm_locked', False):
                asian_default = live_price_data['price']  # ES price, no SPX offset for futures
                st.session_state['_asian_live_price'] = asian_default
            else:
                asian_default = st.session_state.get('_asian_locked_price', asian_default)
        
        col_price, col_lock = st.columns([3, 1])
        
        with col_price:
            asian_price = st.number_input("ES Price at 6:00 PM CT", 
                                           value=asian_default, step=0.25, format="%.2f",
                                           key="asian_es_price",
                                           help="Auto-fills from live ES price. Lock to freeze for trade planning.")
        
        with col_lock:
            st.markdown("<br>", unsafe_allow_html=True)  # spacing
            is_locked = st.session_state.get('asian_6pm_locked', False)
            
            if is_locked:
                locked_price = st.session_state.get('_asian_locked_price', 0)
                st.markdown(f"""
                <div style="font-family: JetBrains Mono; color: #ffd740; font-size: 0.8rem; text-align:center;">
                    🔒 Locked @ {locked_price:.2f}
                </div>""", unsafe_allow_html=True)
                if st.button("🔓 Unlock", key="unlock_asian", use_container_width=True):
                    st.session_state['asian_6pm_locked'] = False
                    st.rerun()
            else:
                if st.button("🔒 Lock 6PM Price", key="lock_asian", use_container_width=True):
                    st.session_state['asian_6pm_locked'] = True
                    st.session_state['_asian_locked_price'] = asian_price
                    st.rerun()
        
        max_move = st.number_input("Max expected move (pts)", value=5.0, step=0.5, format="%.1f",
                                    key="asian_max_move",
                                    help="Maximum points expected in the 6-7 PM window")
        
        if line_ladder_6pm:
            # Find lines immediately above and below price
            lines_above = [l for l in line_ladder_6pm if l['value_6pm'] > asian_price]
            lines_below = [l for l in line_ladder_6pm if l['value_6pm'] <= asian_price]
            
            nearest_above = lines_above[-1] if lines_above else None  # closest above
            nearest_below = lines_below[0] if lines_below else None   # closest below
            second_above = lines_above[-2] if len(lines_above) >= 2 else None
            second_below = lines_below[1] if len(lines_below) >= 2 else None
            
            # Position description
            if nearest_above and nearest_below:
                gap = nearest_above['value_6pm'] - nearest_below['value_6pm']
                dist_above = nearest_above['value_6pm'] - asian_price
                dist_below = asian_price - nearest_below['value_6pm']
                
                position_text = f"Price is between **{nearest_above['short']}** ({nearest_above['value_6pm']:.2f}, {dist_above:.2f} pts above) and **{nearest_below['short']}** ({nearest_below['value_6pm']:.2f}, {dist_below:.2f} pts below). Gap: {gap:.2f} pts."
            elif nearest_above and not nearest_below:
                position_text = f"Price is **BELOW all lines**. Nearest above: {nearest_above['short']} at {nearest_above['value_6pm']:.2f}"
            elif nearest_below and not nearest_above:
                position_text = f"Price is **ABOVE all lines**. Nearest below: {nearest_below['short']} at {nearest_below['value_6pm']:.2f}"
            else:
                position_text = "No lines available"
            
            st.markdown(position_text)
            
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            
            # ============================================================
            # GENERATE TRADE SETUPS
            # ============================================================
            st.markdown("### 📋 Trade Setups (6:00 - 7:00 PM CT)")
            st.caption("Flat by 7:00 PM before Nikkei opens. Max hold: 1 hour.")
            
            trades = []
            
            # SETUP 1: SHORT — if there's resistance above and room to drop
            if nearest_above and nearest_below:
                # Short setup: price rallies to nearest line above, reject back down
                short_entry = nearest_above['value_6pm']
                short_stop = short_entry + 2.0
                short_t1 = asian_price  # back to current price
                short_t2 = nearest_below['value_6pm']  # to the line below
                short_exit_7pm = nearest_above['value_7pm']  # line moves by 7PM
                
                # Cap target at max_move
                if short_entry - short_t2 > max_move:
                    short_t2 = short_entry - max_move
                
                trades.append({
                    'direction': 'SHORT',
                    'bias': 'Rejection at resistance',
                    'trigger': f"Price rallies to {short_entry:.2f} ({nearest_above['short']})",
                    'entry': short_entry,
                    'stop': short_stop,
                    'target_1': short_t1,
                    'target_2': short_t2,
                    'risk': short_stop - short_entry,
                    'reward_1': short_entry - short_t1,
                    'reward_2': short_entry - short_t2,
                    'color': '#ff5252',
                    'icon': '🔻',
                })
                
                # Long setup: price drops to nearest line below, bounce back up
                long_entry = nearest_below['value_6pm']
                long_stop = long_entry - 2.0
                long_t1 = asian_price  # back to current price
                long_t2 = nearest_above['value_6pm']  # to the line above
                
                # Cap target at max_move
                if long_t2 - long_entry > max_move:
                    long_t2 = long_entry + max_move
                
                trades.append({
                    'direction': 'LONG',
                    'bias': 'Bounce at support',
                    'trigger': f"Price drops to {long_entry:.2f} ({nearest_below['short']})",
                    'entry': long_entry,
                    'stop': long_stop,
                    'target_1': long_t1,
                    'target_2': long_t2,
                    'risk': long_entry - long_stop,
                    'reward_1': long_t1 - long_entry,
                    'reward_2': long_t2 - long_entry,
                    'color': '#00e676',
                    'icon': '🔺',
                })
            
            # SETUP 2: Breakout — if price is already at or past a line
            if nearest_above and dist_above <= 1.0:
                # Price is right at resistance — could break through
                break_entry = nearest_above['value_6pm'] + 0.5
                break_stop = nearest_above['value_6pm'] - 1.5
                break_t1 = break_entry + 2.5
                break_t2 = break_entry + max_move
                if second_above:
                    break_t2 = min(break_t2, second_above['value_6pm'])
                
                trades.append({
                    'direction': 'LONG BREAKOUT',
                    'bias': f"Break above {nearest_above['short']}",
                    'trigger': f"Price breaks above {nearest_above['value_6pm']:.2f} with momentum",
                    'entry': break_entry,
                    'stop': break_stop,
                    'target_1': break_t1,
                    'target_2': break_t2,
                    'risk': break_entry - break_stop,
                    'reward_1': break_t1 - break_entry,
                    'reward_2': break_t2 - break_entry,
                    'color': '#ffd740',
                    'icon': '⚡',
                })
            
            if nearest_below and dist_below <= 1.0:
                break_entry = nearest_below['value_6pm'] - 0.5
                break_stop = nearest_below['value_6pm'] + 1.5
                break_t1 = break_entry - 2.5
                break_t2 = break_entry - max_move
                if second_below:
                    break_t2 = max(break_t2, second_below['value_6pm'])
                
                trades.append({
                    'direction': 'SHORT BREAKDOWN',
                    'bias': f"Break below {nearest_below['short']}",
                    'trigger': f"Price breaks below {nearest_below['value_6pm']:.2f} with momentum",
                    'entry': break_entry,
                    'stop': break_stop,
                    'target_1': break_t1,
                    'target_2': break_t2,
                    'risk': break_stop - break_entry,
                    'reward_1': break_entry - break_t1,
                    'reward_2': break_entry - break_t2,
                    'color': '#ffd740',
                    'icon': '⚡',
                })
            
            # ============================================================
            # DISPLAY TRADE CARDS
            # ============================================================
            for trade in trades:
                rr1 = trade['reward_1'] / trade['risk'] if trade['risk'] > 0 else 0
                rr2 = trade['reward_2'] / trade['risk'] if trade['risk'] > 0 else 0
                
                st.markdown(f"""
                <div style="background: linear-gradient(145deg, #131a2e 0%, #0d1220 100%);
                            border: 1px solid {trade['color']}33; border-radius: 12px;
                            padding: 16px; margin: 10px 0;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 10px;">
                        <span style="font-family: Orbitron; font-size: 1.2rem; color: {trade['color']};">
                            {trade['icon']} {trade['direction']}
                        </span>
                        <span style="font-family: Rajdhani; color: #8892b0; font-size: 0.85rem;">
                            {trade['bias']}
                        </span>
                    </div>
                    <div style="font-family: JetBrains Mono; font-size: 0.8rem; color: #5a6a8a; margin-bottom: 8px;">
                        Trigger: {trade['trigger']}
                    </div>
                    <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap: 8px; text-align:center;">
                        <div>
                            <div style="font-family: Rajdhani; color: #5a6a8a; font-size: 0.7rem; text-transform:uppercase;">Entry</div>
                            <div style="font-family: JetBrains Mono; color: #ccd6f6; font-size: 1.1rem; font-weight:700;">{trade['entry']:.2f}</div>
                        </div>
                        <div>
                            <div style="font-family: Rajdhani; color: #5a6a8a; font-size: 0.7rem; text-transform:uppercase;">Stop</div>
                            <div style="font-family: JetBrains Mono; color: #ff1744; font-size: 1.1rem; font-weight:700;">{trade['stop']:.2f}</div>
                            <div style="font-family: JetBrains Mono; color: #5a6a8a; font-size: 0.7rem;">{trade['risk']:.1f} pts</div>
                        </div>
                        <div>
                            <div style="font-family: Rajdhani; color: #5a6a8a; font-size: 0.7rem; text-transform:uppercase;">Target 1</div>
                            <div style="font-family: JetBrains Mono; color: #00e676; font-size: 1.1rem; font-weight:700;">{trade['target_1']:.2f}</div>
                            <div style="font-family: JetBrains Mono; color: #5a6a8a; font-size: 0.7rem;">{trade['reward_1']:.1f} pts • {rr1:.1f}R</div>
                        </div>
                        <div>
                            <div style="font-family: Rajdhani; color: #5a6a8a; font-size: 0.7rem; text-transform:uppercase;">Target 2</div>
                            <div style="font-family: JetBrains Mono; color: #00e676; font-size: 1.1rem; font-weight:700;">{trade['target_2']:.2f}</div>
                            <div style="font-family: JetBrains Mono; color: #5a6a8a; font-size: 0.7rem;">{trade['reward_2']:.1f} pts • {rr2:.1f}R</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            
            # ============================================================
            # RULES REMINDER
            # ============================================================
            st.markdown("""
            <div class="rules-box">
                <div style="font-family: Orbitron, monospace; color: #ffd740; font-size: 0.9rem; margin-bottom: 10px; letter-spacing: 2px;">
                    ⏰ SESSION RULES
                </div>
                <div style="font-family: JetBrains Mono, monospace; color: #8892b0; font-size: 0.8rem; line-height: 2;">
                    5:00 PM — Globex opens. NO TRADES. Observe range formation.<br>
                    6:00 PM — DECISION POINT. Read price vs line ladder. Plan entries.<br>
                    6:00-7:00 PM — TRADING WINDOW. Execute setups. Max 5 pt move expected.<br>
                    7:00 PM — HARD CLOSE. Flatten all positions. Nikkei opens.
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # ============================================================
    # TAB 3: NY SESSION OPTIONS — 9 AM DECISION FRAMEWORK
    # ============================================================
    with tab3:
        st.markdown("### ☀️ NY Session — SPX 0DTE Options")
        st.markdown("*Tastytrade • 20pt OTM • 3 Contracts • Exit at SPX Level*")
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # ============================================================
        # 9 AM PRICE INPUT
        # ============================================================
        st.markdown("### 🎯 9:00 AM Decision Framework")
        
        # Auto-fill from live price if available
        default_price = 6865.0
        if live_mode and live_price_data and live_price_data.get('ok'):
            default_price = live_price_data['price'] - es_offset_val
        
        current_price = st.number_input("Current SPX Price at 9:00 AM CT", 
                                         value=default_price, step=0.5, format="%.2f",
                                         key="current_spx",
                                         help="Auto-filled from live ES price when LIVE MODE is on")
        
        # ============================================================
        # BUILD 9 AM LINE LADDER (reuse from structural map)
        # ============================================================
        ny_ladder = []
        for line in levels['ascending']:
            ny_ladder.append({
                'name': line['source'].split(' @ ')[0] if ' @ ' in line['source'] else line['source'],
                'short': f"{'HW' if line['type'] == 'highest_wick' else 'B'} ↗",
                'value': line['value_at_9am'],
                'direction': 'ascending',
                'color': '#ff1744' if line['type'] == 'highest_wick' else '#ff5252',
            })
        for line in levels['descending']:
            ny_ladder.append({
                'name': line['source'].split(' @ ')[0] if ' @ ' in line['source'] else line['source'],
                'short': f"{'LW' if line['type'] == 'lowest_wick' else 'R'} ↘",
                'value': line['value_at_9am'],
                'direction': 'descending',
                'color': '#00e676' if line['type'] == 'lowest_wick' else '#69f0ae',
            })
        ny_ladder.sort(key=lambda x: x['value'], reverse=True)
        
        # Find nearest lines above and below current price
        lines_above = [l for l in ny_ladder if l['value'] > current_price]
        lines_below = [l for l in ny_ladder if l['value'] <= current_price]
        
        nearest_above = lines_above[-1] if lines_above else None
        nearest_below = lines_below[0] if lines_below else None
        
        # ============================================================
        # POSITION & SIGNAL
        # ============================================================
        # Count ascending vs descending lines above/below
        asc_above = sum(1 for l in lines_above if l['direction'] == 'ascending')
        desc_below = sum(1 for l in lines_below if l['direction'] == 'descending')
        
        # Determine signal based on position
        signal = "NEUTRAL"
        signal_detail = ""
        signal_class = "neutral"
        trade_direction = None  # 'PUT' or 'CALL'
        stop_line = None
        target_lines = []
        
        if nearest_above and nearest_below:
            dist_above = nearest_above['value'] - current_price
            dist_below = current_price - nearest_below['value']
            
            # Check if price is below all ascending lines
            all_asc_values = [l['value'] for l in ny_ladder if l['direction'] == 'ascending']
            all_desc_values = [l['value'] for l in ny_ladder if l['direction'] == 'descending']
            
            if all_asc_values and current_price < min(all_asc_values):
                # Below ALL ascending lines = bearish
                signal = "BEARISH — BUY PUTS"
                signal_class = "bear"
                trade_direction = "PUT"
                stop_line = nearest_above  # line above = invalidation
                target_lines = [l for l in lines_below if l['direction'] == 'descending'][:2]
                signal_detail = f"Price {current_price:.2f} is BELOW all ascending lines. Buyers trapped above. Stop: {stop_line['value']:.2f} ({stop_line['short']})"
                
            elif all_desc_values and current_price > max(all_desc_values) and all_asc_values and current_price > max(all_asc_values):
                # Above ALL lines = strong bullish
                signal = "BULLISH TREND — BUY CALLS"
                signal_class = "bull"
                trade_direction = "CALL"
                stop_line = nearest_below
                target_lines = []  # no ceiling, use fixed targets
                signal_detail = f"Price {current_price:.2f} is ABOVE all lines. Strong trend day. Stop: {stop_line['value']:.2f} ({stop_line['short']})"
                
            elif all_desc_values and current_price < min(all_desc_values):
                # Below ALL lines = strong bearish
                signal = "BEARISH TREND — BUY PUTS"
                signal_class = "bear"
                trade_direction = "PUT"
                stop_line = nearest_above
                target_lines = []
                signal_detail = f"Price {current_price:.2f} is BELOW all lines including descending. Stop: {stop_line['value']:.2f} ({stop_line['short']})"
                
            elif all_asc_values and current_price > max(all_asc_values):
                # Above all ascending = bullish
                signal = "BULLISH — BUY CALLS"
                signal_class = "bull"
                trade_direction = "CALL"
                stop_line = nearest_below
                target_lines = [l for l in lines_above if l['direction'] == 'ascending'][:2]
                signal_detail = f"Price {current_price:.2f} is ABOVE all ascending lines. Stop: {stop_line['value']:.2f} ({stop_line['short']})"
                
            elif nearest_above['direction'] == 'ascending' and nearest_below['direction'] == 'descending':
                # Between ascending above and descending below — choppy, wait
                signal = "BETWEEN ASC ↗ & DESC ↘ — WAIT"
                signal_class = "neutral"
                signal_detail = f"Price {current_price:.2f} between {nearest_above['short']} ({nearest_above['value']:.2f}) and {nearest_below['short']} ({nearest_below['value']:.2f}). No clear bias."
                
            elif nearest_above['direction'] == 'descending':
                # Descending line above = resistance, bearish lean
                signal = "BEARISH LEAN — BUY PUTS"
                signal_class = "bear"
                trade_direction = "PUT"
                stop_line = nearest_above
                target_lines = [l for l in lines_below][:2]
                signal_detail = f"Descending resistance at {nearest_above['value']:.2f} above. Stop: {stop_line['value']:.2f}"
                
            elif nearest_below['direction'] == 'ascending':
                # Ascending line below = support, bullish lean
                signal = "BULLISH LEAN — BUY CALLS"
                signal_class = "bull"
                trade_direction = "CALL"
                stop_line = nearest_below
                target_lines = [l for l in lines_above][:2]
                signal_detail = f"Ascending support at {nearest_below['value']:.2f} below. Stop: {stop_line['value']:.2f}"
        
        # Signal display
        sig_color = '#00e676' if signal_class == 'bull' else '#ff1744' if signal_class == 'bear' else '#ffd740'
        st.markdown(f"""
        <div class="signal-box-{signal_class}">
            <div style="font-family: 'Orbitron'; font-size: 1.5rem; color: {sig_color};">
                {signal}
            </div>
            <div style="font-family: 'Rajdhani'; font-size: 1rem; color: #8892b0; margin-top: 10px;">
                {signal_detail}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ============================================================
        # LINE LADDER WITH PRICE POSITION
        # ============================================================
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📊 9 AM Line Ladder — Price Position")
        
        if ny_ladder:
            ladder_html = '<div style="font-family: JetBrains Mono; font-size: 0.85rem;">'
            price_inserted = False
            
            for i, line in enumerate(ny_ladder):
                # Insert price marker when we pass below it
                if not price_inserted and line['value'] <= current_price:
                    ladder_html += f"""
                    <div style="display:flex; justify-content:center; align-items:center;
                                padding: 6px 12px; margin: 4px 0; border: 2px solid {sig_color};
                                background: rgba(255,215,64,0.1); border-radius: 8px;">
                        <span style="color: {sig_color}; font-weight: 700; font-size: 1.1rem;">
                            ▶ SPX: {current_price:.2f} ◀
                        </span>
                    </div>"""
                    price_inserted = True
                
                bg = 'rgba(255,23,68,0.08)' if line['direction'] == 'ascending' else 'rgba(0,230,118,0.08)'
                dist = current_price - line['value']
                dist_str = f"{'▲' if dist > 0 else '▼'}{abs(dist):.1f}"
                
                ladder_html += f"""
                <div style="display:flex; justify-content:space-between; align-items:center;
                            padding: 6px 12px; margin: 2px 0; border-left: 3px solid {line['color']};
                            background: {bg}; border-radius: 0 6px 6px 0;">
                    <span style="color: {line['color']}; min-width: 120px;">{line['short']} {line['name'][:18]}</span>
                    <span style="color: #ccd6f6; font-weight: 700;">{line['value']:.2f}</span>
                    <span style="color: #5a6a8a; font-size: 0.75rem;">{dist_str}</span>
                </div>"""
            
            # If price is below all lines
            if not price_inserted:
                ladder_html += f"""
                <div style="display:flex; justify-content:center; padding: 6px 12px; margin: 4px 0;
                            border: 2px solid {sig_color}; background: rgba(255,215,64,0.1); border-radius: 8px;">
                    <span style="color: {sig_color}; font-weight: 700; font-size: 1.1rem;">
                        ▶ SPX: {current_price:.2f} ◀
                    </span>
                </div>"""
            
            ladder_html += '</div>'
            st.markdown(ladder_html, unsafe_allow_html=True)
        
        # ============================================================
        # OPTIONS TRADE CARD
        # ============================================================
        if trade_direction:
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            st.markdown("### 📋 0DTE Trade Setup")
            
            # Calculate strike: 20 points OTM, rounded to nearest 5
            if trade_direction == "PUT":
                raw_strike = current_price - 20
                strike = int(raw_strike // 5) * 5  # round down to nearest 5
            else:
                raw_strike = current_price + 20
                strike = int((raw_strike + 4) // 5) * 5  # round up to nearest 5
            
            otm_distance = abs(strike - current_price)
            
            # Stop and targets (SPX levels)
            stop_price = stop_line['value'] if stop_line else (current_price + 10 if trade_direction == "PUT" else current_price - 10)
            
            if target_lines:
                tp1 = target_lines[0]['value']
                tp1_name = f"{target_lines[0]['short']}"
                tp2 = target_lines[1]['value'] if len(target_lines) >= 2 else (tp1 - 5 if trade_direction == "PUT" else tp1 + 5)
                tp2_name = f"{target_lines[1]['short']}" if len(target_lines) >= 2 else "Fixed 5pt"
            else:
                # Trend day — no opposing lines, use fixed targets
                if trade_direction == "PUT":
                    tp1 = current_price - 10
                    tp2 = current_price - 20
                else:
                    tp1 = current_price + 10
                    tp2 = current_price + 20
                tp1_name = "10pt move"
                tp2_name = "20pt move"
            
            # ============================================================
            # PREMIUM: Auto-fetch + Scenario Projections
            # ============================================================
            
            # Fetch VIX
            try:
                import yfinance as yf
                vix_data = yf.Ticker("^VIX").history(period="1d")
                current_vix = float(vix_data['Close'].iloc[-1]) if len(vix_data) > 0 else 18.0
            except:
                current_vix = 18.0
            
            import math
            from datetime import time as dt_time
            
            # Determine current time context for hours-to-expiry
            try:
                import pytz
                ct_tz = pytz.timezone('America/Chicago')
                now_ct = datetime.now(ct_tz).replace(tzinfo=None)
                market_close = datetime.combine(next_date, dt_time(15, 0))
                hours_now = max(0.1, (market_close - now_ct).total_seconds() / 3600)
            except:
                hours_now = 6.5  # default to 8:30 AM
            
            # Hours at 9:05 AM entry
            entry_dt = datetime.combine(next_date, dt_time(9, 5))
            hours_at_entry = max(0.1, (market_close - entry_dt).total_seconds() / 3600)
            
            # Black-Scholes estimate (always available)
            est_premium = estimate_option_premium(current_price, strike, current_vix, hours_at_entry, trade_direction)
            
            # Auto-fetch live premium when LIVE MODE is on and market is open
            live_premium = None
            live_bid = None
            live_ask = None
            
            auto_fetch = live_mode and hours_now < 7.0 and hours_now > 0.5  # between 8:00 AM and 2:30 PM
            manual_fetch = False
            
            if not auto_fetch:
                col_f1, col_f2 = st.columns([3, 1])
                with col_f1:
                    st.markdown(f"""
                    <div style="font-family: JetBrains Mono; color: #8892b0; font-size: 0.85rem;">
                        VIX: {current_vix:.1f} • Pre-Market Est: ${est_premium:.2f}/contract
                    </div>""", unsafe_allow_html=True)
                with col_f2:
                    manual_fetch = st.button("📊 Fetch Live Price", key="fetch_tt_chain")
            
            if auto_fetch or manual_fetch:
                try:
                    import requests as req
                    tt_token = st.session_state.get('_tt_session_token', '')
                    
                    if not tt_token:
                        # Authenticate with Tastytrade
                        tt_user = st.secrets.get("tastytrade", {}).get("username", "")
                        tt_pass = st.secrets.get("tastytrade", {}).get("password", "")
                        if tt_user and tt_pass:
                            auth_resp = req.post("https://api.tastytrade.com/sessions",
                                                  json={"login": tt_user, "password": tt_pass}, timeout=10)
                            if auth_resp.status_code in (200, 201):
                                tt_token = auth_resp.json().get("data", {}).get("session-token", "")
                                st.session_state['_tt_session_token'] = tt_token
                    
                    if tt_token:
                        headers = {"Authorization": tt_token, "Content-Type": "application/json"}
                        
                        # Build OCC symbol
                        exp_date = next_date
                        date_str = exp_date.strftime("%y%m%d")
                        opt_char = "C" if trade_direction == "CALL" else "P"
                        strike_str = f"{int(strike * 1000):08d}"
                        occ_symbol = f"SPXW  {date_str}{opt_char}{strike_str}"
                        
                        quote_url = f"https://api.tastytrade.com/market-data/{occ_symbol}/quote"
                        quote_resp = req.get(quote_url, headers=headers, timeout=10)
                        
                        if quote_resp.status_code == 200:
                            q = quote_resp.json().get("data", {})
                            live_bid = float(q.get("bid", 0))
                            live_ask = float(q.get("ask", 0))
                            mid = (live_bid + live_ask) / 2 if live_bid and live_ask else 0
                            if mid > 0:
                                live_premium = mid
                                st.session_state['_live_premium'] = mid
                                st.session_state['_live_premium_hours'] = hours_now
                except Exception as e:
                    if manual_fetch:
                        st.warning(f"Could not fetch: {str(e)[:80]}")
            
            # Also check session state for previously fetched premium
            if not live_premium and '_live_premium' in st.session_state:
                live_premium = st.session_state['_live_premium']
                hours_now = st.session_state.get('_live_premium_hours', hours_now)
            
            # Project premiums at entry using actual trade levels
            scenarios = project_premium_at_scenarios(
                current_spx=current_price,
                strike=strike,
                vix=current_vix,
                opt_type=trade_direction,
                stop_price=stop_price,
                tp1_price=tp1,
                tp2_price=tp2,
                base_premium=live_premium,
                current_hours=hours_now,
                entry_hours=hours_at_entry,
            )
            
            # Determine which premium to use for the trade card
            final_premium = scenarios['at_entry']
            cost_per_contract = final_premium * 100
            num_contracts = 3
            total_cost = num_contracts * cost_per_contract
            
            # Source indicator
            if live_premium:
                premium_source = "🔴 LIVE → Projected to 9:05 AM"
            else:
                premium_source = "📐 Estimated at 9:05 AM"
            
            # ============================================================
            # SCENARIO TABLE
            # ============================================================
            st.markdown("### 💲 Premium Projections @ 9:05 AM Entry")
            if scenarios['calibrated']:
                st.caption(f"Calibrated from live pull: ${live_premium:.2f} (Bid ${live_bid:.2f} / Ask ${live_ask:.2f})")
            else:
                st.caption(f"Black-Scholes estimate • VIX: {current_vix:.1f} • {hours_at_entry:.1f}hrs to expiry")
            
            # Scenario cards
            scenario_data = [
                ("AT ENTRY", f"SPX @ {current_price:.2f}", scenarios['at_entry'], '#ccd6f6', 
                 f"{current_price:.0f}", "Your expected entry cost"),
                ("AT STOP ✋", f"SPX @ {stop_price:.2f}", scenarios['at_stop'], '#ff1744',
                 f"{stop_price:.0f}", f"Option value if stopped ({stop_line['short'] if stop_line else 'N/A'})"),
                ("AT TP1 🎯", f"SPX @ {tp1:.2f}", scenarios['at_tp1'], '#00e676',
                 f"{tp1:.0f}", f"Option value at Target 1 ({tp1_name})"),
                ("AT TP2 🎯🎯", f"SPX @ {tp2:.2f}", scenarios['at_tp2'], '#00e676',
                 f"{tp2:.0f}", f"Option value at Target 2 ({tp2_name})"),
            ]
            
            scenario_html = '<div style="display:grid; grid-template-columns: repeat(4, 1fr); gap: 10px;">'
            for label, spx_label, prem, color, spx_short, desc in scenario_data:
                pnl_per_contract = (prem - scenarios['at_entry']) * 100
                pnl_total = pnl_per_contract * num_contracts
                pnl_color = '#00e676' if pnl_total >= 0 else '#ff1744'
                pnl_sign = '+' if pnl_total >= 0 else ''
                
                scenario_html += f"""
                <div style="background: linear-gradient(145deg, #131a2e 0%, #0d1220 100%);
                            border: 1px solid {color}33; border-radius: 10px; padding: 12px; text-align:center;">
                    <div style="font-family: Rajdhani; color: {color}; font-size: 0.75rem; text-transform:uppercase;
                                letter-spacing: 1px;">{label}</div>
                    <div style="font-family: JetBrains Mono; color: #5a6a8a; font-size: 0.7rem; margin: 2px 0;">
                        {spx_label}</div>
                    <div style="font-family: JetBrains Mono; color: {color}; font-size: 1.4rem; font-weight:700;">
                        ${prem:.2f}</div>
                    <div style="font-family: JetBrains Mono; color: #5a6a8a; font-size: 0.7rem;">
                        ${prem*100:.0f}/contract</div>
                    <div style="font-family: JetBrains Mono; color: {pnl_color}; font-size: 0.8rem; margin-top: 4px;">
                        {pnl_sign}${pnl_total:,.0f}</div>
                    <div style="font-family: Rajdhani; color: #3a4a6a; font-size: 0.65rem; margin-top: 2px;">
                        {desc}</div>
                </div>"""
            scenario_html += '</div>'
            st.markdown(scenario_html, unsafe_allow_html=True)
            
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            
            # Trade card — split into separate markdown calls for reliable rendering
            trade_color = '#ff5252' if trade_direction == 'PUT' else '#00e676'
            trade_icon = '🔻' if trade_direction == 'PUT' else '🔺'
            trade_class = 'trade-card-bear' if trade_direction == 'PUT' else 'trade-card-bull'
            
            st.markdown("### 📋 Trade Card")
            
            # Header
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; 
                        padding: 16px 20px; margin: 0;
                        background: linear-gradient(145deg, rgba(14,20,36,0.95), rgba(8,13,22,0.98));
                        border: 2px solid {trade_color}33; border-bottom: none;
                        border-radius: 14px 14px 0 0;">
                <span style="font-family: Orbitron, monospace; font-size: 1.4rem; color: {trade_color}; letter-spacing: 2px;">
                    {trade_icon} BUY {trade_direction} — SPX {strike}
                </span>
                <span style="font-family: JetBrains Mono, monospace; color: #3a4a6a; font-size: 0.8rem;">
                    {otm_distance:.0f}pt OTM • 0DTE • {premium_source}
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            # Premium / Contracts / Risk row
            st.markdown(f"""
            <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap: 0; 
                        border-left: 2px solid {trade_color}33; border-right: 2px solid {trade_color}33;
                        background: rgba(10,15,26,0.95);">
                <div style="text-align:center; padding: 14px; border-right: 1px solid rgba(30,45,74,0.3);">
                    <div style="font-family: Rajdhani, sans-serif; color: #3a4a6a; font-size: 0.7rem; text-transform:uppercase; letter-spacing: 2px;">Premium</div>
                    <div style="font-family: JetBrains Mono, monospace; color: #ccd6f6; font-size: 1.4rem; font-weight:700;">${final_premium:.2f}</div>
                    <div style="font-family: JetBrains Mono, monospace; color: #3a4a6a; font-size: 0.7rem;">${cost_per_contract:.0f} / contract</div>
                </div>
                <div style="text-align:center; padding: 14px; border-right: 1px solid rgba(30,45,74,0.3);">
                    <div style="font-family: Rajdhani, sans-serif; color: #3a4a6a; font-size: 0.7rem; text-transform:uppercase; letter-spacing: 2px;">Contracts</div>
                    <div style="font-family: JetBrains Mono, monospace; color: #ccd6f6; font-size: 1.4rem; font-weight:700;">{num_contracts}</div>
                    <div style="font-family: JetBrains Mono, monospace; color: #3a4a6a; font-size: 0.7rem;">× ${cost_per_contract:.0f} ea</div>
                </div>
                <div style="text-align:center; padding: 14px;">
                    <div style="font-family: Rajdhani, sans-serif; color: #3a4a6a; font-size: 0.7rem; text-transform:uppercase; letter-spacing: 2px;">Total Risk</div>
                    <div style="font-family: JetBrains Mono, monospace; color: #ff1744; font-size: 1.4rem; font-weight:700;">${total_cost:,.0f}</div>
                    <div style="font-family: JetBrains Mono, monospace; color: #3a4a6a; font-size: 0.7rem;">Max loss = premium</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Stop / TP1 / TP2 row
            st.markdown(f"""
            <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap: 0;
                        border: 2px solid {trade_color}33; border-top: 1px solid rgba(30,45,74,0.3);
                        border-radius: 0 0 14px 14px;
                        background: rgba(10,15,26,0.95);">
                <div style="text-align:center; padding: 14px; border-right: 1px solid rgba(30,45,74,0.3);
                            background: rgba(255,23,68,0.04);">
                    <div style="font-family: Rajdhani, sans-serif; color: #ff1744; font-size: 0.7rem; text-transform:uppercase; letter-spacing: 2px;">Stop Loss (SPX)</div>
                    <div style="font-family: JetBrains Mono, monospace; color: #ff1744; font-size: 1.3rem; font-weight:700;">{stop_price:.2f}</div>
                    <div style="font-family: JetBrains Mono, monospace; color: #3a4a6a; font-size: 0.7rem;">{stop_line['short'] if stop_line else 'Fixed'} • {abs(current_price - stop_price):.1f}pt</div>
                </div>
                <div style="text-align:center; padding: 14px; border-right: 1px solid rgba(30,45,74,0.3);
                            background: rgba(0,230,118,0.04);">
                    <div style="font-family: Rajdhani, sans-serif; color: #00e676; font-size: 0.7rem; text-transform:uppercase; letter-spacing: 2px;">Target 1 (SPX)</div>
                    <div style="font-family: JetBrains Mono, monospace; color: #00e676; font-size: 1.3rem; font-weight:700;">{tp1:.2f}</div>
                    <div style="font-family: JetBrains Mono, monospace; color: #3a4a6a; font-size: 0.7rem;">{tp1_name} • {abs(current_price - tp1):.1f}pt</div>
                </div>
                <div style="text-align:center; padding: 14px;
                            background: rgba(0,230,118,0.04);">
                    <div style="font-family: Rajdhani, sans-serif; color: #00e676; font-size: 0.7rem; text-transform:uppercase; letter-spacing: 2px;">Target 2 (SPX)</div>
                    <div style="font-family: JetBrains Mono, monospace; color: #00e676; font-size: 1.3rem; font-weight:700;">{tp2:.2f}</div>
                    <div style="font-family: JetBrains Mono, monospace; color: #3a4a6a; font-size: 0.7rem;">{tp2_name} • {abs(current_price - tp2):.1f}pt</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Execution rules
            st.markdown(f"""
            <div class="rules-box">
                <div style="font-family: Orbitron, monospace; color: #ffd740; font-size: 0.9rem; margin-bottom: 10px; letter-spacing: 2px;">
                    ⏰ EXECUTION RULES
                </div>
                <div style="font-family: JetBrains Mono, monospace; color: #8892b0; font-size: 0.8rem; line-height: 2;">
                    9:00 AM — DECISION. Read ladder position. Determine bias.<br>
                    9:05 AM — ENTRY. Let opening IV settle. Buy 3× SPX {strike} {'P' if trade_direction == 'PUT' else 'C'} @ ~${final_premium:.2f}<br>
                    STOP — Close ALL 3 contracts if SPX {'rises above' if trade_direction == 'PUT' else 'drops below'} {stop_price:.2f} ({stop_line['short'] if stop_line else 'N/A'})<br>
                    TP1 — Close ALL 3 contracts at SPX {tp1:.2f} ({tp1_name})<br>
                    TP2 — If TP1 missed, hold for {tp2:.2f} ({tp2_name})<br>
                    TIME STOP — Close by 11:00 AM CT if trade not working
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        else:
            # No clear direction
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="signal-box-neutral" style="animation: pulse-border-neutral 3s ease-in-out infinite, fade-in-up 0.5s ease;">
                <div style="font-family: Orbitron, monospace; color: #ffd740; font-size: 1.2rem; letter-spacing: 2px;">
                    ⏸️ NO TRADE — WAIT FOR CLARITY
                </div>
                <div style="font-family: Rajdhani, sans-serif; color: #8892b0; font-size: 1rem; margin-top: 12px;">
                    Price is between conflicting lines. Wait for a break above or below to establish direction.
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # ============================================================
        # CONFLUENCE SCORE
        # ============================================================
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 🔗 Confluence Score")
        
        # Auto-detect confluence from candle data
        candles_for_detection = st.session_state.get('last_fetch_candles', None)
        
        if trade_direction:
            auto = auto_detect_confluence(
                ny_trade_direction=trade_direction,
                ny_ladder=ny_ladder,
                current_price=current_price,
                candles_df=candles_for_detection,
                es_offset=es_offset_val
            )
            
            has_candle_data = candles_for_detection is not None and len(candles_for_detection) > 0
            
            # Show auto-detected values with detail
            if has_candle_data:
                st.caption("🤖 Auto-detected from candle data • Toggle overrides below if needed")
            else:
                st.caption("⚠️ No candle data — fetch data in Structural Map tab for auto-detection")
            
            # Use auto values as defaults, allow manual override
            allow_override = st.toggle("Manual Override", value=False, key="confluence_override",
                                        help="Override auto-detected values")
            
            if allow_override:
                col1, col2 = st.columns(2)
                with col1:
                    asian_aligns = st.checkbox("Asian session aligned", value=auto['asian_aligns'],
                                                help=auto['asian_detail'])
                    london_sweep = st.checkbox("London sweep confirmed", value=auto['london_sweep'],
                                                help=auto['london_detail'])
                    line_cluster = st.checkbox("Lines cluster within 5 pts", value=auto['line_cluster'],
                                                help=auto['cluster_detail'])
                with col2:
                    data_reaction = st.radio("7:30 AM Data Reaction", 
                                              ["aligned", "absorbed", "against"],
                                              index=["aligned", "absorbed", "against"].index(auto['data_reaction']),
                                              horizontal=True)
                    opening_drive = st.checkbox("Opening drive aligned", value=auto['opening_drive'],
                                                help=auto['opening_detail'])
            else:
                asian_aligns = auto['asian_aligns']
                london_sweep = auto['london_sweep']
                data_reaction = auto['data_reaction']
                opening_drive = auto['opening_drive']
                line_cluster = auto['line_cluster']
                
                # Show auto-detected details as styled rows
                factors_display = [
                    ("Asian Session", auto['asian_aligns'], auto['asian_detail']),
                    ("London Sweep", auto['london_sweep'], auto['london_detail']),
                    ("Data Reaction", auto['data_reaction'] == 'aligned', auto['data_detail']),
                    ("Opening Drive", auto['opening_drive'], auto['opening_detail']),
                    ("Line Cluster", auto['line_cluster'], auto['cluster_detail']),
                ]
                for name, passed, detail in factors_display:
                    icon = "✅" if passed else ("⚡" if "absorbed" in detail.lower() else "❌")
                    color = "#00e676" if passed else ("#ffd740" if "absorbed" in detail.lower() else "#ff5252")
                    st.markdown(f"""
                    <div style="display:flex; align-items:center; gap: 10px; padding: 6px 12px; margin: 3px 0;
                                background: rgba(255,255,255,0.02); border-radius: 8px; border-left: 3px solid {color};">
                        <span style="font-size: 0.9rem;">{icon}</span>
                        <span style="font-family: Rajdhani, sans-serif; color: {color}; font-weight: 600; min-width: 120px;">{name}</span>
                        <span style="font-family: JetBrains Mono, monospace; color: #8892b0; font-size: 0.78rem;">{detail}</span>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            asian_aligns = False
            london_sweep = False
            data_reaction = 'absorbed'
            opening_drive = False
            line_cluster = False
            st.info("Waiting for trade direction signal to calculate confluence...")
        
        confluence = calculate_confluence(asian_aligns, london_sweep, data_reaction,
                                          opening_drive, line_cluster)
        
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <div class="metric-label">Confluence Score</div>
            <div class="confluence-{confluence['color']}">{confluence['score']}/5</div>
            <div style="font-family: 'Rajdhani'; color: {'#00e676' if confluence['color']=='high' else '#ffd740' if confluence['color']=='med' else '#ff1744'}; font-size: 1.1rem; margin-top: 8px;">
                {confluence['recommendation']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        for factor in confluence['factors']:
            st.markdown(f"<span style='font-family: JetBrains Mono; font-size: 0.85rem; color: #8892b0;'>{factor}</span>", unsafe_allow_html=True)
    
    # ============================================================
    # TAB 4: TRADE LOG — Daily Journal + Persistent Trade Storage
    # ============================================================
    with tab4:
        st.markdown("### 📋 Trade Log & Journal")
        st.markdown("*Daily journal • Trade tracking • Performance analytics*")
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # ── File paths ──
        import os
        TRADE_LOG_FILE = os.path.expanduser("~/.spx_prophet_trades.json")
        JOURNAL_FILE = os.path.expanduser("~/.spx_prophet_journal.json")
        
        def load_trades() -> list:
            """Load trades from persistent JSON file."""
            try:
                if os.path.exists(TRADE_LOG_FILE):
                    with open(TRADE_LOG_FILE, 'r') as f:
                        return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
            return []
        
        def save_trades(trades: list):
            """Save trades to persistent JSON file."""
            try:
                with open(TRADE_LOG_FILE, 'w') as f:
                    json.dump(trades, f, indent=2)
            except IOError as e:
                st.error(f"Could not save trades: {e}")
        
        def load_journal() -> dict:
            """Load journal entries from persistent JSON file. Keys are date strings."""
            try:
                if os.path.exists(JOURNAL_FILE):
                    with open(JOURNAL_FILE, 'r') as f:
                        return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
            return {}
        
        def save_journal(journal: dict):
            """Save journal entries to persistent JSON file."""
            try:
                with open(JOURNAL_FILE, 'w') as f:
                    json.dump(journal, f, indent=2)
            except IOError as e:
                st.error(f"Could not save journal: {e}")
        
        # ── DAILY JOURNAL SECTION ──
        st.markdown("### 📝 Daily Journal")
        
        journal_data = load_journal()
        journal_date = st.date_input("Journal Date", value=datetime.now().date(), key="journal_date")
        journal_key = str(journal_date)
        
        # Load existing entry for this date
        existing_entry = journal_data.get(journal_key, {})
        existing_content = existing_entry.get('content', '')
        existing_tags = existing_entry.get('tags', [])
        
        # Try to use streamlit-quill for rich text; fall back to text_area
        try:
            from streamlit_quill import st_quill
            
            st.caption("Rich text editor • Your entries are saved per date")
            
            journal_content = st_quill(
                value=existing_content,
                html=True,
                toolbar=[
                    ['bold', 'italic', 'underline', 'strike'],
                    [{'header': [1, 2, 3, False]}],
                    [{'list': 'ordered'}, {'list': 'bullet'}],
                    [{'color': []}, {'background': []}],
                    ['link'],
                    ['clean'],
                ],
                key=f"journal_quill_{journal_key}",
                placeholder="What happened today? Pre-market plan, session observations, lessons learned..."
            )
        except ImportError:
            st.caption("Text editor • Install `streamlit-quill` for rich text formatting")
            journal_content = st.text_area(
                "Journal Entry",
                value=existing_content,
                height=250,
                key=f"journal_text_{journal_key}",
                placeholder="What happened today? Pre-market plan, session observations, lessons learned...",
                label_visibility="collapsed"
            )
        
        # Quick tags
        tag_options = ["📈 Green Day", "📉 Red Day", "😐 Flat", "🎯 Hit All Targets", 
                       "✋ Stopped Out", "⏰ Time Stopped", "🧠 Lesson Learned", 
                       "💎 Diamond Hands", "🐔 Chickened Out", "📊 High Confluence"]
        
        # Pre-select existing tags
        default_tags = [t for t in existing_tags if t in tag_options]
        journal_tags = st.pills("Quick Tags", tag_options, selection_mode="multi", 
                                default=default_tags, key=f"journal_tags_{journal_key}")
        
        jcol1, jcol2, jcol3 = st.columns([1, 1, 2])
        with jcol1:
            if st.button("💾 Save Entry", use_container_width=True, key="save_journal"):
                journal_data[journal_key] = {
                    'content': journal_content if journal_content else '',
                    'tags': list(journal_tags) if journal_tags else [],
                    'updated': datetime.now().isoformat(),
                }
                save_journal(journal_data)
                st.success("Journal saved!")
        
        with jcol2:
            if st.button("🗑️ Clear Entry", use_container_width=True, key="clear_journal"):
                if journal_key in journal_data:
                    del journal_data[journal_key]
                    save_journal(journal_data)
                    st.success("Entry cleared.")
                    st.rerun()
        
        # Show recent journal entries
        if len(journal_data) > 0:
            sorted_dates = sorted(journal_data.keys(), reverse=True)
            recent_dates = [d for d in sorted_dates if d != journal_key][:5]
            
            if recent_dates:
                with st.expander(f"📖 Recent Entries ({len(journal_data)} total)", expanded=False):
                    for jd in recent_dates:
                        entry = journal_data[jd]
                        content_preview = entry.get('content', '')
                        # Strip HTML for preview
                        import re
                        text_only = re.sub(r'<[^>]+>', '', content_preview)[:120]
                        tags_str = ' '.join(entry.get('tags', []))
                        
                        st.markdown(f"""
                        <div style="padding: 10px 14px; margin: 4px 0; border-left: 3px solid rgba(0,212,255,0.3);
                                    background: rgba(255,255,255,0.02); border-radius: 0 8px 8px 0;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span style="font-family: Orbitron, monospace; color: #00d4ff; font-size: 0.8rem;">{jd}</span>
                                <span style="font-size: 0.75rem;">{tags_str}</span>
                            </div>
                            <div style="font-family: Rajdhani, sans-serif; color: #8892b0; font-size: 0.85rem; margin-top: 4px;">
                                {text_only}{'...' if len(text_only) >= 120 else ''}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        
        # ── SECTION DIVIDER ──
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # ── TRADE LOG SECTION ──
        st.markdown("### 💰 Trade Log")
        
        def calculate_pnl(session, direction, entry, exit_price, contracts, premium_per_contract=0):
            """Calculate P&L based on session type."""
            if "Futures" in session:
                # ES futures: $50 per point per contract (MES: $5)
                pnl_per_point = 5  # MES default — user can override
                mult = 1 if direction == "LONG" else -1
                pnl = mult * (exit_price - entry) * contracts * pnl_per_point
            else:
                # SPX options: premium-based
                # Entry cost = premium × 100 × contracts
                # Exit value = exit_premium × 100 × contracts  
                # For simplicity: user enters entry/exit as premium per share
                mult = 1  # options are always long (buy to open)
                pnl = (exit_price - entry) * 100 * contracts
            return round(pnl, 2)
        
        # Load persistent trades
        all_trades = load_trades()
        
        # ── Log New Trade ──
        with st.expander("➕ Log New Trade", expanded=len(all_trades) == 0):
            tcol1, tcol2 = st.columns(2)
            
            with tcol1:
                trade_date = st.date_input("Trade Date", value=datetime.now().date(), key="trade_date")
                trade_session = st.selectbox("Session", ["NY (Options)", "Asian (Futures)"], key="trade_sess")
                trade_direction_input = st.selectbox("Direction", 
                    ["PUT", "CALL"] if "Options" in trade_session else ["LONG", "SHORT"],
                    key="trade_dir")
                trade_confluence_input = st.slider("Confluence Score", 0.0, 5.0, 3.0, 0.5, key="trade_conf")
            
            with tcol2:
                if "Options" in trade_session:
                    trade_strike = st.number_input("Strike", value=6845, step=5, key="trade_strike")
                    trade_entry_premium = st.number_input("Entry Premium (per share)", value=6.50, step=0.25, format="%.2f", key="trade_entry_prem")
                    trade_exit_premium = st.number_input("Exit Premium (per share)", value=9.00, step=0.25, format="%.2f", key="trade_exit_prem")
                    trade_contracts_input = st.number_input("Contracts", value=3, min_value=1, key="trade_contracts")
                else:
                    trade_entry_price = st.number_input("Entry Price", value=6865.0, step=0.25, key="trade_entry_es")
                    trade_exit_price = st.number_input("Exit Price", value=6870.0, step=0.25, key="trade_exit_es")
                    trade_contracts_input = st.number_input("Contracts (MES)", value=2, min_value=1, key="trade_contracts_es")
                    trade_strike = 0
                    trade_entry_premium = trade_entry_price
                    trade_exit_premium = trade_exit_price
            
            trade_result = st.selectbox("Result", ["Win", "Loss", "Breakeven", "Stopped Out", "Time Stop"], key="trade_result")
            trade_notes_input = st.text_input("Notes", key="trade_notes", placeholder="What worked? What didn't?")
            
            # Preview P&L
            if "Options" in trade_session:
                preview_pnl = (trade_exit_premium - trade_entry_premium) * 100 * trade_contracts_input
                preview_cost = trade_entry_premium * 100 * trade_contracts_input
                st.markdown(f"""
                <div style="font-family: JetBrains Mono, monospace; font-size: 0.85rem; color: #8892b0; padding: 8px 0;">
                    Entry: {trade_contracts_input}× ${trade_entry_premium:.2f} = <span style="color:#ccd6f6;">${preview_cost:,.0f}</span> &nbsp;→&nbsp;
                    P&L: <span style="color: {'#00e676' if preview_pnl >= 0 else '#ff1744'}; font-weight:700;">${preview_pnl:+,.0f}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                mult = 1 if trade_direction_input == "LONG" else -1
                preview_pnl = mult * (trade_exit_price - trade_entry_price) * trade_contracts_input * 5
                st.markdown(f"""
                <div style="font-family: JetBrains Mono, monospace; font-size: 0.85rem; color: #8892b0; padding: 8px 0;">
                    {trade_direction_input} {trade_contracts_input} MES @ {trade_entry_price:.2f} → {trade_exit_price:.2f} &nbsp;→&nbsp;
                    P&L: <span style="color: {'#00e676' if preview_pnl >= 0 else '#ff1744'}; font-weight:700;">${preview_pnl:+,.0f}</span>
                </div>
                """, unsafe_allow_html=True)
            
            save_col1, save_col2 = st.columns([1, 3])
            with save_col1:
                if st.button("💾 Save Trade", use_container_width=True):
                    if "Options" in trade_session:
                        pnl = (trade_exit_premium - trade_entry_premium) * 100 * trade_contracts_input
                    else:
                        mult = 1 if trade_direction_input == "LONG" else -1
                        pnl = mult * (trade_exit_price - trade_entry_price) * trade_contracts_input * 5
                    
                    new_trade = {
                        'id': f"{trade_date}_{len(all_trades)+1}",
                        'date': str(trade_date),
                        'session': trade_session,
                        'direction': trade_direction_input,
                        'strike': trade_strike if "Options" in trade_session else 0,
                        'entry': trade_entry_premium if "Options" in trade_session else trade_entry_price,
                        'exit': trade_exit_premium if "Options" in trade_session else trade_exit_price,
                        'contracts': trade_contracts_input,
                        'pnl': round(pnl, 2),
                        'confluence': trade_confluence_input,
                        'result': trade_result,
                        'notes': trade_notes_input,
                    }
                    all_trades.append(new_trade)
                    save_trades(all_trades)
                    st.success(f"Trade saved! P&L: ${pnl:+,.0f}")
                    st.rerun()
        
        # ── Performance Dashboard ──
        if all_trades:
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            st.markdown("### 📊 Performance Dashboard")
            
            df_trades = pd.DataFrame(all_trades)
            df_trades['pnl'] = pd.to_numeric(df_trades['pnl'], errors='coerce').fillna(0)
            df_trades['date'] = pd.to_datetime(df_trades['date'])
            
            total_pnl = df_trades['pnl'].sum()
            total_trades = len(df_trades)
            wins = len(df_trades[df_trades['pnl'] > 0])
            losses = len(df_trades[df_trades['pnl'] < 0])
            breakevens = total_trades - wins - losses
            win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
            avg_win = df_trades[df_trades['pnl'] > 0]['pnl'].mean() if wins > 0 else 0
            avg_loss = df_trades[df_trades['pnl'] < 0]['pnl'].mean() if losses > 0 else 0
            profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
            best_trade = df_trades['pnl'].max()
            worst_trade = df_trades['pnl'].min()
            
            # Equity curve
            df_trades_sorted = df_trades.sort_values('date')
            df_trades_sorted['cumulative_pnl'] = df_trades_sorted['pnl'].cumsum()
            
            # Running max for drawdown
            df_trades_sorted['peak'] = df_trades_sorted['cumulative_pnl'].cummax()
            df_trades_sorted['drawdown'] = df_trades_sorted['cumulative_pnl'] - df_trades_sorted['peak']
            max_drawdown = df_trades_sorted['drawdown'].min()
            
            # ── Summary Cards ──
            pnl_color = "bull" if total_pnl >= 0 else "bear"
            wr_color = "bull" if win_rate >= 50 else ("neutral" if win_rate >= 40 else "bear")
            
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Total P&L</div>
                    <div class="metric-value-{pnl_color}">${total_pnl:+,.0f}</div>
                    <div style="font-family: JetBrains Mono, monospace; color: #3a4a6a; font-size: 0.75rem;">{total_trades} trades</div>
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Win Rate</div>
                    <div class="metric-value-{wr_color}">{win_rate:.0f}%</div>
                    <div style="font-family: JetBrains Mono, monospace; color: #3a4a6a; font-size: 0.75rem;">{wins}W / {losses}L / {breakevens}BE</div>
                </div>""", unsafe_allow_html=True)
            with c3:
                pf_color = "bull" if profit_factor >= 1.5 else ("neutral" if profit_factor >= 1.0 else "bear")
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Profit Factor</div>
                    <div class="metric-value-{pf_color}">{profit_factor:.2f}</div>
                    <div style="font-family: JetBrains Mono, monospace; color: #3a4a6a; font-size: 0.75rem;">Avg W: ${avg_win:+,.0f} / L: ${avg_loss:+,.0f}</div>
                </div>""", unsafe_allow_html=True)
            with c4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Max Drawdown</div>
                    <div class="metric-value-bear">${max_drawdown:,.0f}</div>
                    <div style="font-family: JetBrains Mono, monospace; color: #3a4a6a; font-size: 0.75rem;">Best: ${best_trade:+,.0f} / Worst: ${worst_trade:+,.0f}</div>
                </div>""", unsafe_allow_html=True)
            
            # ── Equity Curve Chart ──
            if len(df_trades_sorted) >= 2:
                st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                st.markdown("### 📈 Equity Curve")
                
                eq_fig = go.Figure()
                
                # Equity line with fill
                eq_fig.add_trace(go.Scatter(
                    x=df_trades_sorted['date'], 
                    y=df_trades_sorted['cumulative_pnl'],
                    mode='lines+markers',
                    name='Equity',
                    line=dict(color='#00d4ff', width=2.5),
                    marker=dict(size=6, color=df_trades_sorted['pnl'].apply(lambda x: '#00e676' if x >= 0 else '#ff1744')),
                    fill='tozeroy',
                    fillcolor='rgba(0,212,255,0.06)',
                    hovertemplate='<b>%{x|%b %d}</b><br>Equity: $%{y:+,.0f}<extra></extra>'
                ))
                
                # Zero line
                eq_fig.add_hline(y=0, line_dash="dot", line_color="rgba(255,255,255,0.1)", line_width=1)
                
                # Drawdown shading
                if max_drawdown < 0:
                    eq_fig.add_trace(go.Scatter(
                        x=df_trades_sorted['date'],
                        y=df_trades_sorted['drawdown'],
                        mode='lines',
                        name='Drawdown',
                        line=dict(color='#ff1744', width=1, dash='dot'),
                        fill='tozeroy',
                        fillcolor='rgba(255,23,68,0.06)',
                        hovertemplate='Drawdown: $%{y:,.0f}<extra></extra>'
                    ))
                
                eq_fig.update_layout(
                    template='plotly_dark',
                    paper_bgcolor='rgba(5,8,16,1)',
                    plot_bgcolor='rgba(8,13,22,1)',
                    height=350,
                    margin=dict(l=10, r=20, t=10, b=40),
                    xaxis=dict(
                        gridcolor='rgba(30,45,74,0.12)', showgrid=True,
                        tickfont=dict(family='Rajdhani', size=11, color='#3a4a6a'),
                    ),
                    yaxis=dict(
                        gridcolor='rgba(30,45,74,0.12)', showgrid=True,
                        tickformat='$,.0f', side='right',
                        tickfont=dict(family='JetBrains Mono', size=11, color='#5a6a8a'),
                    ),
                    legend=dict(bgcolor='rgba(6,9,16,0.95)', font=dict(size=10, family='JetBrains Mono', color='#8892b0')),
                    font=dict(family='JetBrains Mono', color='#8892b0'),
                    hovermode='x unified',
                    hoverlabel=dict(bgcolor='rgba(6,9,16,0.95)', bordercolor='rgba(0,212,255,0.2)',
                        font=dict(family='JetBrains Mono', size=11, color='#ccd6f6')),
                )
                st.plotly_chart(eq_fig, use_container_width=True)
            
            # ── Win Rate by Confluence ──
            if len(df_trades) >= 3:
                st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                st.markdown("### 🎯 Win Rate by Confluence Score")
                
                conf_groups = df_trades.groupby(df_trades['confluence'].apply(lambda x: f"{x:.0f}+")).agg(
                    trades=('pnl', 'count'),
                    wins=('pnl', lambda x: (x > 0).sum()),
                    total_pnl=('pnl', 'sum'),
                ).reset_index()
                conf_groups['win_rate'] = (conf_groups['wins'] / conf_groups['trades'] * 100).round(0)
                
                for _, row in conf_groups.iterrows():
                    wr = row['win_rate']
                    wr_bar_color = '#00e676' if wr >= 60 else ('#ffd740' if wr >= 45 else '#ff5252')
                    pnl_val = row['total_pnl']
                    pnl_color_str = '#00e676' if pnl_val >= 0 else '#ff1744'
                    bar_width = max(5, wr)
                    st.markdown(f"""
                    <div style="display:flex; align-items:center; gap: 12px; padding: 8px 14px; margin: 3px 0;
                                background: rgba(255,255,255,0.02); border-radius: 8px;">
                        <span style="font-family: Orbitron, monospace; color: #ccd6f6; font-size: 0.85rem; min-width: 50px;">
                            {row['confluence']}
                        </span>
                        <div style="flex:1; height: 20px; background: rgba(255,255,255,0.03); border-radius: 4px; overflow:hidden;">
                            <div style="height:100%; width:{bar_width}%; background: {wr_bar_color}; border-radius: 4px; 
                                        transition: width 0.5s ease;"></div>
                        </div>
                        <span style="font-family: JetBrains Mono, monospace; color: {wr_bar_color}; font-size: 0.85rem; min-width: 45px; text-align:right;">
                            {wr:.0f}%
                        </span>
                        <span style="font-family: JetBrains Mono, monospace; color: {pnl_color_str}; font-size: 0.8rem; min-width: 70px; text-align:right;">
                            ${pnl_val:+,.0f}
                        </span>
                        <span style="font-family: Rajdhani, sans-serif; color: #3a4a6a; font-size: 0.75rem; min-width: 50px;">
                            {int(row['trades'])} trades
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
            
            # ── Trade History Table ──
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            st.markdown("### 📋 Trade History")
            
            # Format for display
            display_df = df_trades_sorted[['date', 'session', 'direction', 'strike', 'entry', 'exit', 
                                            'contracts', 'pnl', 'confluence', 'result', 'notes']].copy()
            display_df['date'] = display_df['date'].dt.strftime('%b %d')
            display_df.columns = ['Date', 'Session', 'Dir', 'Strike', 'Entry', 'Exit', 'Qty', 'P&L', 'Conf', 'Result', 'Notes']
            
            # Style the dataframe
            def style_pnl(val):
                if isinstance(val, (int, float)):
                    color = '#00e676' if val >= 0 else '#ff1744'
                    return f'color: {color}; font-weight: bold'
                return ''
            
            st.dataframe(
                display_df.style.applymap(style_pnl, subset=['P&L']),
                use_container_width=True, hide_index=True, height=400
            )
            
            # ── Delete Trade ──
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            with st.expander("🗑️ Delete a Trade"):
                if all_trades:
                    trade_options = [f"{t['date']} | {t['direction']} | ${t['pnl']:+,.0f} | {t.get('notes','')[:30]}" for t in all_trades]
                    delete_idx = st.selectbox("Select trade to delete", range(len(trade_options)), format_func=lambda i: trade_options[i])
                    
                    dc1, dc2 = st.columns([1, 3])
                    with dc1:
                        if st.button("🗑️ Delete", type="secondary", use_container_width=True):
                            all_trades.pop(delete_idx)
                            save_trades(all_trades)
                            st.success("Trade deleted.")
                            st.rerun()
            
            # ── Export ──
            with st.expander("📤 Export Trades"):
                export_col1, export_col2 = st.columns(2)
                with export_col1:
                    csv_data = display_df.to_csv(index=False)
                    st.download_button("📥 Download CSV", csv_data, "spx_prophet_trades.csv", "text/csv",
                                        use_container_width=True)
                with export_col2:
                    json_data = json.dumps(all_trades, indent=2)
                    st.download_button("📥 Download JSON", json_data, "spx_prophet_trades.json", "application/json",
                                        use_container_width=True)
        
        else:
            st.markdown("""
            <div class="signal-box-neutral" style="text-align:center; animation: none;">
                <div style="font-family: Orbitron, monospace; color: #ffd740; font-size: 1.1rem; letter-spacing: 2px;">
                    NO TRADES LOGGED YET
                </div>
                <div style="font-family: Rajdhani, sans-serif; color: #8892b0; font-size: 1rem; margin-top: 10px;">
                    Start tracking your trades to build your performance history.
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # ============================================================
    # TAB 5: HISTORICAL BACKTEST
    # ============================================================
    with tab5:
        st.markdown("### 🔬 Historical Backtest")
        st.markdown("*Pick a past date • Replay structural lines vs actual price*")
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # ── Date Selection ──
        st.markdown("#### 📅 Select Backtest Date")
        st.caption("Choose a trading date. The system will fetch candle data, build the line ladder, and overlay actual price action.")
        
        bcol1, bcol2 = st.columns([1, 2])
        with bcol1:
            # Default to last Friday if weekend
            today = datetime.now().date()
            if today.weekday() >= 5:  # Saturday or Sunday
                default_bt = today - timedelta(days=(today.weekday() - 4))
            else:
                default_bt = today - timedelta(days=1)
            
            bt_date = st.date_input("Backtest Date (trading day)", value=default_bt, key="bt_date",
                                     help="Pick a weekday. This is the NY session date — candles fetched from prior day 3PM through this date 3PM.")
            
            bt_es_offset = st.number_input("ES-SPX Offset", value=es_offset_val, step=0.5, key="bt_offset",
                                            help="ES-SPX spread for this date. Use ~65 as default.")
        
        with bcol2:
            bt_bounces_input = st.text_area("Manual Bounces (if no candle data)", 
                                             placeholder="6850 @ 8:00 PM\n6860 @ 10:30 PM\n6845 @ 1:00 AM",
                                             height=100, key="bt_bounces_manual")
        
        run_backtest = st.button("🚀 Run Backtest", use_container_width=True, type="primary", key="run_bt")
        
        if run_backtest:
            with st.spinner("Fetching candle data and running structural analysis..."):
                # ── Fetch candle data ──
                bt_prior = bt_date - timedelta(days=1)
                # Adjust for weekends
                while bt_prior.weekday() >= 5:
                    bt_prior = bt_prior - timedelta(days=1)
                
                bt_status = fetch_es_candles(bt_prior, bt_date)
                
                if bt_status.candles is not None and len(bt_status.candles) > 0:
                    st.success(f"Loaded {len(bt_status.candles)} candles via {bt_status.source_used}")
                    
                    bt_candles = bt_status.candles.copy()
                    
                    # ── Filter overnight session: prior day 3PM to bt_date 9AM ──
                    bt_candles['Datetime'] = pd.to_datetime(bt_candles['Datetime'])
                    
                    overnight_start = datetime.combine(bt_prior, time(15, 0))
                    nine_am_bt = datetime.combine(bt_date, time(9, 0))
                    three_pm_bt = datetime.combine(bt_date, time(15, 0))
                    
                    overnight_mask = (bt_candles['Datetime'] >= overnight_start) & (bt_candles['Datetime'] <= nine_am_bt)
                    overnight = bt_candles[overnight_mask].copy()
                    
                    # Full day (for actual price overlay)
                    full_day_mask = (bt_candles['Datetime'] >= overnight_start) & (bt_candles['Datetime'] <= three_pm_bt)
                    full_day = bt_candles[full_day_mask].copy()
                    
                    if len(overnight) < 3:
                        st.warning(f"Only {len(overnight)} overnight candles found. Results may be limited.")
                    
                    # ── Extract bounces and rejections from candle data ──
                    # Convert to SPX terms
                    overnight_spx = overnight.copy()
                    full_day_spx = full_day.copy()
                    for col in ['Open', 'High', 'Low', 'Close']:
                        overnight_spx[col] = overnight_spx[col] - bt_es_offset
                        full_day_spx[col] = full_day_spx[col] - bt_es_offset
                    
                    # Auto-detect bounces/rejections from candles
                    bt_bounces = []
                    bt_rejections = []
                    bt_highest_wick = {'price': 0, 'time': overnight_start}
                    bt_lowest_wick = {'price': 99999, 'time': overnight_start}
                    
                    for _, row in overnight_spx.iterrows():
                        candle_time = row['Datetime']
                        high = row['High']
                        low = row['Low']
                        open_p = row['Open']
                        close = row['Close']
                        body_top = max(open_p, close)
                        body_bottom = min(open_p, close)
                        upper_wick = high - body_top
                        lower_wick = body_bottom - low
                        body_size = abs(close - open_p)
                        
                        # Track highest/lowest wicks
                        if high > bt_highest_wick['price']:
                            bt_highest_wick = {'price': high, 'time': candle_time}
                        if low < bt_lowest_wick['price']:
                            bt_lowest_wick = {'price': low, 'time': candle_time}
                        
                        # Bounce: long lower wick (wick > body, close near high)
                        if lower_wick > max(body_size, 1.0) and close > open_p:
                            bt_bounces.append({'price': low, 'time': candle_time, 'source': f"Bounce @ {candle_time.strftime('%I:%M %p')}"})
                        
                        # Rejection: long upper wick (wick > body, close near low)
                        if upper_wick > max(body_size, 1.0) and close < open_p:
                            bt_rejections.append({'price': high, 'time': candle_time, 'source': f"Rejection @ {candle_time.strftime('%I:%M %p')}"})
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="display:flex; justify-content:space-around; text-align:center;">
                            <div>
                                <div class="metric-label">Overnight Candles</div>
                                <div style="font-family: Orbitron; color: #00d4ff; font-size: 1.5rem;">{len(overnight)}</div>
                            </div>
                            <div>
                                <div class="metric-label">Bounces Found</div>
                                <div style="font-family: Orbitron; color: #ff5252; font-size: 1.5rem;">{len(bt_bounces)}</div>
                            </div>
                            <div>
                                <div class="metric-label">Rejections Found</div>
                                <div style="font-family: Orbitron; color: #69f0ae; font-size: 1.5rem;">{len(bt_rejections)}</div>
                            </div>
                            <div>
                                <div class="metric-label">Overnight Range</div>
                                <div style="font-family: Orbitron; color: #ffd740; font-size: 1.5rem;">
                                    {bt_highest_wick['price'] - bt_lowest_wick['price']:.1f}pt
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # ── Build structural levels ──
                    chart_start = overnight_start
                    chart_end = three_pm_bt
                    
                    bt_levels = build_structural_levels(
                        bt_highest_wick, bt_lowest_wick, bt_bounces, bt_rejections,
                        chart_start, chart_end
                    )
                    
                    # ── Build chart with actual price overlay ──
                    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                    st.markdown("### 📊 Structural Lines vs Actual Price")
                    
                    # Master timeline for chart
                    bt_times = sorted(full_day_spx['Datetime'].tolist())
                    bt_time_to_idx = {t: i for i, t in enumerate(bt_times)}
                    
                    # Tick marks
                    bt_tick_vals = []
                    bt_tick_texts = []
                    for t in bt_times:
                        h, m = t.hour, t.minute
                        if m == 0 and h in [17, 20, 23, 2, 5, 8, 9, 10, 11, 12, 13, 14]:
                            bt_tick_vals.append(bt_time_to_idx[t])
                            if h == 9:
                                bt_tick_texts.append("9AM ▶")
                            elif h >= 12:
                                bt_tick_texts.append(f"{h-12 if h > 12 else 12}PM")
                            else:
                                bt_tick_texts.append(f"{h}AM" if h < 12 else "12PM")
                    
                    bt_fig = go.Figure()
                    
                    # ── Actual price line (candlestick-style: OHLC as line) ──
                    bt_fig.add_trace(go.Scatter(
                        x=list(range(len(bt_times))),
                        y=full_day_spx['Close'].tolist(),
                        mode='lines',
                        name='Actual Price',
                        line=dict(color='rgba(255,255,255,0.7)', width=2),
                        hovertemplate='<b>%{text}</b><br>Price: %{y:.2f}<extra></extra>',
                        text=[t.strftime('%I:%M %p') for t in bt_times],
                    ))
                    
                    # Price area fill
                    bt_fig.add_trace(go.Scatter(
                        x=list(range(len(bt_times))),
                        y=full_day_spx['Close'].tolist(),
                        mode='lines', showlegend=False,
                        line=dict(width=0),
                        fill='tozeroy', fillcolor='rgba(255,255,255,0.02)',
                        hoverinfo='skip',
                    ))
                    
                    # ── 9 AM decision line ──
                    if nine_am_bt in bt_time_to_idx:
                        idx9 = bt_time_to_idx[nine_am_bt]
                        bt_fig.add_shape(type="line", x0=idx9, x1=idx9, y0=0, y1=1, yref="paper",
                            line=dict(color="#ffd740", width=2, dash="dash"))
                        bt_fig.add_annotation(x=idx9, y=1.05, yref="paper",
                            text="<b>9:00 AM DECISION</b>", showarrow=False,
                            font=dict(color="#ffd740", size=11, family="Orbitron"))
                    
                    # ── Ascending structural lines ──
                    for li, asc_line in enumerate(bt_levels['ascending']):
                        series = generate_line_series(asc_line['anchor_price'], asc_line['anchor_time'], chart_start, chart_end, 'ascending')
                        xi = [bt_time_to_idx[t] for t, _ in series if t in bt_time_to_idx]
                        yi = [p for t, p in series if t in bt_time_to_idx]
                        if xi:
                            is_wick = asc_line['type'] == 'highest_wick'
                            line_color = '#ff1744' if is_wick else '#ff5252'
                            bt_fig.add_trace(go.Scatter(x=xi, y=yi, mode='lines',
                                name=f"↗ {'HW' if is_wick else f'B{li+1}'}: {asc_line['anchor_price']:.1f}",
                                line=dict(color=line_color, width=3 if is_wick else 2, dash='solid' if is_wick else 'dash'),
                                opacity=0.9 if is_wick else 0.5))
                    
                    # ── Descending structural lines ──
                    for li, desc_line in enumerate(bt_levels['descending']):
                        series = generate_line_series(desc_line['anchor_price'], desc_line['anchor_time'], chart_start, chart_end, 'descending')
                        xi = [bt_time_to_idx[t] for t, _ in series if t in bt_time_to_idx]
                        yi = [p for t, p in series if t in bt_time_to_idx]
                        if xi:
                            is_wick = desc_line['type'] == 'lowest_wick'
                            line_color = '#00e676' if is_wick else '#69f0ae'
                            bt_fig.add_trace(go.Scatter(x=xi, y=yi, mode='lines',
                                name=f"↘ {'LW' if is_wick else f'R{li+1}'}: {desc_line['anchor_price']:.1f}",
                                line=dict(color=line_color, width=3 if is_wick else 2, dash='solid' if is_wick else 'dash'),
                                opacity=0.9 if is_wick else 0.5))
                    
                    # ── 9 AM key level horizontals ──
                    bt_key = bt_levels['key_levels']
                    for level, color, label, icon in [
                        (bt_key['highest_wick_ascending'], '#ff1744', 'HW', '▲'),
                        (bt_key['highest_bounce_ascending'], '#ff5252', 'HB', '△'),
                        (bt_key['lowest_rejection_descending'], '#69f0ae', 'LR', '▽'),
                        (bt_key['lowest_wick_descending'], '#00e676', 'LW', '▼'),
                    ]:
                        if level:
                            bt_fig.add_shape(type="line", x0=0, x1=len(bt_times)-1,
                                y0=level['value_at_9am'], y1=level['value_at_9am'],
                                line=dict(color=color, width=1, dash="dot"))
                            bt_fig.add_annotation(x=len(bt_times)-1, y=level['value_at_9am'],
                                text=f"<b>{icon} {label}</b> {level['value_at_9am']:.2f}",
                                showarrow=False, font=dict(size=10, color=color, family='JetBrains Mono'),
                                xshift=8, xanchor="left",
                                bgcolor='rgba(6,9,16,0.8)', bordercolor=color, borderwidth=1, borderpad=3)
                    
                    # ── Bounce / Rejection markers ──
                    for b in bt_bounces:
                        if b['time'] in bt_time_to_idx:
                            bt_fig.add_trace(go.Scatter(
                                x=[bt_time_to_idx[b['time']]], y=[b['price']],
                                mode='markers', showlegend=False,
                                marker=dict(symbol='triangle-up', size=14, color='#ff5252',
                                    line=dict(width=1.5, color='rgba(255,82,82,0.5)')),
                                hovertemplate=f"<b>BOUNCE</b><br>{b['price']:.2f}<extra></extra>"
                            ))
                    for r in bt_rejections:
                        if r['time'] in bt_time_to_idx:
                            bt_fig.add_trace(go.Scatter(
                                x=[bt_time_to_idx[r['time']]], y=[r['price']],
                                mode='markers', showlegend=False,
                                marker=dict(symbol='triangle-down', size=14, color='#69f0ae',
                                    line=dict(width=1.5, color='rgba(105,240,174,0.5)')),
                                hovertemplate=f"<b>REJECTION</b><br>{r['price']:.2f}<extra></extra>"
                            ))
                    
                    # ── Wick markers ──
                    if bt_highest_wick['time'] in bt_time_to_idx:
                        bt_fig.add_trace(go.Scatter(
                            x=[bt_time_to_idx[bt_highest_wick['time']]], y=[bt_highest_wick['price']],
                            mode='markers', showlegend=False,
                            marker=dict(symbol='diamond', size=16, color='#ff1744',
                                line=dict(width=2, color='rgba(255,23,68,0.6)')),
                            hovertemplate=f"<b>HIGHEST WICK</b><br>{bt_highest_wick['price']:.2f}<extra></extra>"
                        ))
                    if bt_lowest_wick['time'] in bt_time_to_idx:
                        bt_fig.add_trace(go.Scatter(
                            x=[bt_time_to_idx[bt_lowest_wick['time']]], y=[bt_lowest_wick['price']],
                            mode='markers', showlegend=False,
                            marker=dict(symbol='diamond', size=16, color='#00e676',
                                line=dict(width=2, color='rgba(0,230,118,0.6)')),
                            hovertemplate=f"<b>LOWEST WICK</b><br>{bt_lowest_wick['price']:.2f}<extra></extra>"
                        ))
                    
                    # ── Chart layout ──
                    bt_fig.update_layout(
                        template='plotly_dark',
                        paper_bgcolor='rgba(5,8,16,1)',
                        plot_bgcolor='rgba(8,13,22,1)',
                        height=750,
                        margin=dict(l=10, r=200, t=50, b=60),
                        title=dict(text=f"<b>Backtest: {bt_date.strftime('%A, %B %d, %Y')}</b>",
                            font=dict(family='Orbitron', size=16, color='#ccd6f6'), x=0.5),
                        xaxis=dict(
                            gridcolor='rgba(30,45,74,0.15)', showgrid=True,
                            tickmode='array', tickvals=bt_tick_vals, ticktext=bt_tick_texts,
                            tickfont=dict(size=11, family='Rajdhani', color='#3a4a6a'),
                            spikemode='across', spikethickness=1, spikecolor='rgba(0,212,255,0.3)',
                            spikesnap='cursor', spikedash='dot',
                        ),
                        yaxis=dict(
                            gridcolor='rgba(30,45,74,0.12)', showgrid=True,
                            tickformat='.2f', side='right',
                            tickfont=dict(family='JetBrains Mono', size=11, color='#5a6a8a'),
                            spikemode='across', spikethickness=1, spikecolor='rgba(0,212,255,0.3)',
                            spikesnap='cursor', spikedash='dot',
                        ),
                        legend=dict(bgcolor='rgba(6,9,16,0.95)', bordercolor='rgba(30,45,74,0.4)', borderwidth=1,
                            font=dict(size=10, family='JetBrains Mono', color='#8892b0'), x=1.01, y=1),
                        font=dict(family='JetBrains Mono', color='#8892b0'),
                        hovermode='x unified',
                        hoverlabel=dict(bgcolor='rgba(6,9,16,0.95)', bordercolor='rgba(0,212,255,0.2)',
                            font=dict(family='JetBrains Mono', size=11, color='#ccd6f6')),
                        dragmode='pan',
                    )
                    
                    st.plotly_chart(bt_fig, use_container_width=True, config={
                        'displayModeBar': True, 'displaylogo': False, 'scrollZoom': True,
                        'modeBarButtonsToRemove': ['autoScale2d', 'lasso2d', 'select2d'],
                    })
                    
                    # ── Backtest Analysis ──
                    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                    st.markdown("### 📋 Backtest Analysis")
                    
                    # Get 9AM price
                    nine_am_candles = full_day_spx[full_day_spx['Datetime'] == nine_am_bt]
                    if len(nine_am_candles) > 0:
                        bt_9am_price = nine_am_candles.iloc[0]['Open']
                    else:
                        # Closest candle to 9 AM
                        closest = full_day_spx.iloc[(full_day_spx['Datetime'] - nine_am_bt).abs().argsort()[:1]]
                        bt_9am_price = closest.iloc[0]['Close'] if len(closest) > 0 else 0
                    
                    # Get session high/low after 9 AM
                    rth_mask = full_day_spx['Datetime'] >= nine_am_bt
                    rth_candles = full_day_spx[rth_mask]
                    if len(rth_candles) > 0:
                        rth_high = rth_candles['High'].max()
                        rth_low = rth_candles['Low'].min()
                        rth_close = rth_candles.iloc[-1]['Close']
                        session_move = rth_close - bt_9am_price
                        session_range = rth_high - rth_low
                        
                        # Check which lines were hit
                        lines_hit = []
                        for level_name, level_data in [
                            ('HW Ascending', bt_key['highest_wick_ascending']),
                            ('HB Ascending', bt_key['highest_bounce_ascending']),
                            ('LR Descending', bt_key['lowest_rejection_descending']),
                            ('LW Descending', bt_key['lowest_wick_descending']),
                        ]:
                            if level_data:
                                val = level_data['value_at_9am']
                                if rth_low <= val <= rth_high:
                                    lines_hit.append((level_name, val))
                        
                        # Direction that day
                        day_direction = "BULLISH" if session_move > 2 else ("BEARISH" if session_move < -2 else "FLAT")
                        day_color = "#00e676" if session_move > 2 else ("#ff1744" if session_move < -2 else "#ffd740")
                        
                        acol1, acol2, acol3, acol4 = st.columns(4)
                        with acol1:
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">9 AM Price</div>
                                <div style="font-family: Orbitron; color: #00d4ff; font-size: 1.3rem;">{bt_9am_price:.2f}</div>
                            </div>""", unsafe_allow_html=True)
                        with acol2:
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">Day Direction</div>
                                <div style="font-family: Orbitron; color: {day_color}; font-size: 1.3rem;">{day_direction}</div>
                                <div style="font-family: JetBrains Mono; color: #3a4a6a; font-size: 0.75rem;">{session_move:+.1f}pt</div>
                            </div>""", unsafe_allow_html=True)
                        with acol3:
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">RTH Range</div>
                                <div style="font-family: Orbitron; color: #ccd6f6; font-size: 1.3rem;">{session_range:.1f}pt</div>
                                <div style="font-family: JetBrains Mono; color: #3a4a6a; font-size: 0.75rem;">H:{rth_high:.0f} L:{rth_low:.0f}</div>
                            </div>""", unsafe_allow_html=True)
                        with acol4:
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">Lines Hit</div>
                                <div style="font-family: Orbitron; color: {'#00e676' if lines_hit else '#ff5252'}; font-size: 1.3rem;">{len(lines_hit)}/4</div>
                            </div>""", unsafe_allow_html=True)
                        
                        if lines_hit:
                            st.markdown("**Lines touched during RTH:**")
                            for name, val in lines_hit:
                                st.markdown(f"""
                                <div style="display:flex; align-items:center; gap: 10px; padding: 6px 12px; margin: 2px 0;
                                            background: rgba(0,230,118,0.05); border-radius: 8px; border-left: 3px solid #00e676;">
                                    <span style="font-family: Orbitron, monospace; color: #00e676; font-size: 0.85rem;">✅ {name}</span>
                                    <span style="font-family: JetBrains Mono, monospace; color: #8892b0; font-size: 0.8rem;">@ {val:.2f}</span>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div style="padding: 8px 14px; background: rgba(255,23,68,0.05); border-radius: 8px; border-left: 3px solid #ff1744;">
                                <span style="font-family: Rajdhani, sans-serif; color: #ff5252;">No key levels were hit during RTH. Price stayed in a narrow band.</span>
                            </div>
                            """, unsafe_allow_html=True)
                    
                else:
                    st.warning("Could not fetch candle data for this date. Try a different date or check if markets were open.")


if __name__ == "__main__":
    main()
