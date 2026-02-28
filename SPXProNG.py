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
    Estimate 0DTE SPX option premium using Black-Scholes approximation.
    
    Args:
        spx_price: Current SPX index price
        strike: Strike price
        vix: Current VIX level
        hours_to_expiry: Hours until 3:00 PM CT close
        opt_type: 'CALL' or 'PUT'
    
    Returns:
        Estimated premium per share (multiply by 100 for contract cost)
    """
    import math
    
    if hours_to_expiry <= 0:
        # At expiry, intrinsic only
        if opt_type == 'CALL':
            return max(0, spx_price - strike)
        else:
            return max(0, strike - spx_price)
    
    # Annualized vol from VIX
    daily_vol = vix / 100 / (252 ** 0.5)
    # Scale to remaining hours (6.5 hour trading day)
    intraday_vol = daily_vol * (hours_to_expiry / 6.5) ** 0.5
    
    # Simplified Black-Scholes
    d1_denom = intraday_vol if intraday_vol > 0.0001 else 0.0001
    moneyness = math.log(spx_price / strike) / d1_denom if strike > 0 else 0
    
    # Normal CDF approximation
    def norm_cdf(x):
        return 0.5 * (1 + math.erf(x / (2 ** 0.5)))
    
    d1 = moneyness / d1_denom + 0.5 * d1_denom if d1_denom > 0.0001 else 0
    d2 = d1 - d1_denom
    
    if opt_type == 'CALL':
        premium = spx_price * norm_cdf(d1) - strike * norm_cdf(d2)
    else:
        premium = strike * norm_cdf(-d2) - spx_price * norm_cdf(-d1)
    
    return max(0.10, round(premium * 4) / 4)  # min $0.10, round to 0.25


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
    st.markdown('<div class="sub-header">Structural Rate Engine • Futures & Options</div>', unsafe_allow_html=True)
    
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
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 STRUCTURAL MAP", 
        "🌙 ASIAN SESSION (Futures)", 
        "☀️ NY SESSION (Options)",
        "📋 TRADE LOG"
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
        
        # Session boxes using candle indices
        if show_session_boxes:
            session_colors = {
                'NY': ('rgba(66,133,244,0.08)', 'rgba(66,133,244,0.3)'),
                'Globex': ('rgba(255,215,0,0.05)', 'rgba(255,215,0,0.2)'),
                'Tokyo': ('rgba(233,30,99,0.05)', 'rgba(233,30,99,0.2)'),
                'London': ('rgba(0,188,212,0.05)', 'rgba(0,188,212,0.2)'),
                'NY2': ('rgba(66,133,244,0.08)', 'rgba(66,133,244,0.3)'),
            }
            
            for skey, sname, s_start, s_end in session_blocks:
                sfill, sborder = session_colors.get(skey, ('rgba(128,128,128,0.05)', 'rgba(128,128,128,0.2)'))
                s_idx = [i for i, t in enumerate(master_times) if s_start <= t <= s_end]
                if s_idx:
                    fig.add_vrect(x0=min(s_idx), x1=max(s_idx), fillcolor=sfill,
                        line=dict(color=sborder, width=1, dash='dot'))
        
        
        # 9:00 AM decision line
        nine_am = datetime.combine(next_date, time(9, 0))
        nine_am_ts = nine_am.timestamp() * 1000
        if nine_am in time_to_idx:
            idx9 = time_to_idx[nine_am]
            fig.add_shape(type="line", x0=idx9, x1=idx9, y0=0, y1=1, yref="paper",
                line=dict(color="#ffd740", width=2, dash="dash"))
            fig.add_annotation(x=idx9, y=1, yref="paper", text="9:00 AM Decision",
                showarrow=False, font=dict(color="#ffd740", size=11), yshift=10)
        
        for li, asc_line in enumerate(levels['ascending']):
            series = generate_line_series(asc_line['anchor_price'], asc_line['anchor_time'], chart_start, chart_end, 'ascending')
            xi = [time_to_idx[t] for t, _ in series if t in time_to_idx]
            yi = [p for t, p in series if t in time_to_idx]
            if xi:
                is_wick = asc_line['type'] == 'highest_wick'
                fig.add_trace(go.Scatter(x=xi, y=yi, mode='lines',
                    name=f"↗ {'HW' if is_wick else f'B{li+1}'}: {asc_line['anchor_price']:.1f}",
                    line=dict(color='#ff1744' if is_wick else '#ff5252', width=3 if is_wick else 2, dash='solid' if is_wick else 'dash'),
                    opacity=1.0 if is_wick or show_all_lines else 0.4))
        
        for li, desc_line in enumerate(levels['descending']):
            series = generate_line_series(desc_line['anchor_price'], desc_line['anchor_time'], chart_start, chart_end, 'descending')
            xi = [time_to_idx[t] for t, _ in series if t in time_to_idx]
            yi = [p for t, p in series if t in time_to_idx]
            if xi:
                is_wick = desc_line['type'] == 'lowest_wick'
                fig.add_trace(go.Scatter(x=xi, y=yi, mode='lines',
                    name=f"↘ {'LW' if is_wick else f'R{li+1}'}: {desc_line['anchor_price']:.1f}",
                    line=dict(color='#00e676' if is_wick else '#69f0ae', width=3 if is_wick else 2, dash='solid' if is_wick else 'dash'),
                    opacity=1.0 if is_wick or show_all_lines else 0.4))
        
        key = levels['key_levels']
        for level, color, label in [
            (key['highest_wick_ascending'], '#ff1744', 'HW Asc @ 9AM'),
            (key['highest_bounce_ascending'], '#ff5252', 'HB Asc @ 9AM'),
            (key['lowest_rejection_descending'], '#69f0ae', 'LR Desc @ 9AM'),
            (key['lowest_wick_descending'], '#00e676', 'LW Desc @ 9AM'),
        ]:
            if level:
                fig.add_shape(type="line", x0=0, x1=len(master_times)-1,
                    y0=level['value_at_9am'], y1=level['value_at_9am'],
                    line=dict(color=color, width=1, dash="dot"))
                fig.add_annotation(x=len(master_times)-1, y=level['value_at_9am'],
                    text=f"{label}: {level['value_at_9am']:.2f}",
                    showarrow=False, font=dict(size=9, color=color), xshift=5, xanchor="left")
        
        for bounce in bounces:
            if bounce['time'] in time_to_idx:
                fig.add_trace(go.Scatter(x=[time_to_idx[bounce['time']]], y=[bounce['price']],
                    mode='markers', marker=dict(symbol='triangle-up', size=14, color='#ff5252', line=dict(width=2, color='white')), showlegend=False))
        for rejection in rejections:
            if rejection['time'] in time_to_idx:
                fig.add_trace(go.Scatter(x=[time_to_idx[rejection['time']]], y=[rejection['price']],
                    mode='markers', marker=dict(symbol='triangle-down', size=14, color='#69f0ae', line=dict(width=2, color='white')), showlegend=False))
        if highest_wick['time'] in time_to_idx:
            fig.add_trace(go.Scatter(x=[time_to_idx[highest_wick['time']]], y=[highest_wick['price']],
                mode='markers', marker=dict(symbol='diamond', size=14, color='#ff1744', line=dict(width=2, color='white')), showlegend=False))
        if lowest_wick['time'] in time_to_idx:
            fig.add_trace(go.Scatter(x=[time_to_idx[lowest_wick['time']]], y=[lowest_wick['price']],
                mode='markers', marker=dict(symbol='diamond', size=14, color='#00e676', line=dict(width=2, color='white')), showlegend=False))
        
        # Live price line on chart
        if live_mode and live_price_data and live_price_data.get('ok'):
            live_spx = live_price_data['price'] - es_offset_val
            # Full-width horizontal dashed line
            fig.add_hline(y=live_spx, line_dash="dot", line_color="#ffd740", line_width=2,
                          annotation_text=f"LIVE {live_spx:.2f}",
                          annotation_position="right",
                          annotation_font=dict(color="#ffd740", size=12, family="Orbitron"))
        
        fig.update_layout(
            template='plotly_dark', paper_bgcolor='#0a0a0f', plot_bgcolor='#0d1117',
            height=700, margin=dict(l=60, r=200, t=40, b=60),
            xaxis=dict(gridcolor='#1a2332', showgrid=False, tickmode='array',
                tickvals=tick_vals, ticktext=tick_texts, tickangle=0, 
                tickfont=dict(size=11, family='Rajdhani', color='#8892b0')),
            yaxis=dict(gridcolor='#1a2332', showgrid=True, tickformat='.2f', side='right'),
            legend=dict(bgcolor='rgba(13,18,32,0.9)', bordercolor='#1e2d4a', borderwidth=1,
                font=dict(size=10, family='JetBrains Mono'), x=1.01, y=1),
            font=dict(family='JetBrains Mono', color='#8892b0'), hovermode='x unified',
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
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
            
            # Trade card
            trade_color = '#ff5252' if trade_direction == 'PUT' else '#00e676'
            trade_icon = '🔻' if trade_direction == 'PUT' else '🔺'
            
            st.markdown(f"""
            <div style="background: linear-gradient(145deg, #131a2e 0%, #0d1220 100%);
                        border: 2px solid {trade_color}44; border-radius: 12px;
                        padding: 20px; margin: 10px 0;">
                
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 15px;">
                    <span style="font-family: Orbitron; font-size: 1.4rem; color: {trade_color};">
                        {trade_icon} BUY {trade_direction} — SPX {strike}
                    </span>
                    <span style="font-family: JetBrains Mono; color: #5a6a8a; font-size: 0.8rem;">
                        {otm_distance:.0f}pt OTM • 0DTE • {premium_source}
                    </span>
                </div>
                
                <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap: 12px; text-align:center; margin-bottom: 15px;">
                    <div style="background: rgba(255,255,255,0.03); border-radius: 8px; padding: 12px;">
                        <div style="font-family: Rajdhani; color: #5a6a8a; font-size: 0.7rem; text-transform:uppercase;">Premium</div>
                        <div style="font-family: JetBrains Mono; color: #ccd6f6; font-size: 1.3rem; font-weight:700;">${final_premium:.2f}</div>
                        <div style="font-family: JetBrains Mono; color: #5a6a8a; font-size: 0.7rem;">${cost_per_contract:.0f} / contract</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.03); border-radius: 8px; padding: 12px;">
                        <div style="font-family: Rajdhani; color: #5a6a8a; font-size: 0.7rem; text-transform:uppercase;">Contracts</div>
                        <div style="font-family: JetBrains Mono; color: #ccd6f6; font-size: 1.3rem; font-weight:700;">{num_contracts}</div>
                        <div style="font-family: JetBrains Mono; color: #5a6a8a; font-size: 0.7rem;">× ${cost_per_contract:.0f} ea</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.03); border-radius: 8px; padding: 12px;">
                        <div style="font-family: Rajdhani; color: #5a6a8a; font-size: 0.7rem; text-transform:uppercase;">Total Risk</div>
                        <div style="font-family: JetBrains Mono; color: #ff1744; font-size: 1.3rem; font-weight:700;">${total_cost:,.0f}</div>
                        <div style="font-family: JetBrains Mono; color: #5a6a8a; font-size: 0.7rem;">Max loss = premium</div>
                    </div>
                </div>
                
                <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap: 12px; text-align:center;">
                    <div style="background: rgba(255,23,68,0.08); border-radius: 8px; padding: 12px;">
                        <div style="font-family: Rajdhani; color: #ff1744; font-size: 0.7rem; text-transform:uppercase;">Stop Loss (SPX)</div>
                        <div style="font-family: JetBrains Mono; color: #ff1744; font-size: 1.3rem; font-weight:700;">{stop_price:.2f}</div>
                        <div style="font-family: JetBrains Mono; color: #5a6a8a; font-size: 0.7rem;">{stop_line['short'] if stop_line else 'Fixed'} • {abs(current_price - stop_price):.1f}pt</div>
                    </div>
                    <div style="background: rgba(0,230,118,0.08); border-radius: 8px; padding: 12px;">
                        <div style="font-family: Rajdhani; color: #00e676; font-size: 0.7rem; text-transform:uppercase;">Target 1 (SPX)</div>
                        <div style="font-family: JetBrains Mono; color: #00e676; font-size: 1.3rem; font-weight:700;">{tp1:.2f}</div>
                        <div style="font-family: JetBrains Mono; color: #5a6a8a; font-size: 0.7rem;">{tp1_name} • {abs(current_price - tp1):.1f}pt</div>
                    </div>
                    <div style="background: rgba(0,230,118,0.08); border-radius: 8px; padding: 12px;">
                        <div style="font-family: Rajdhani; color: #00e676; font-size: 0.7rem; text-transform:uppercase;">Target 2 (SPX)</div>
                        <div style="font-family: JetBrains Mono; color: #00e676; font-size: 1.3rem; font-weight:700;">{tp2:.2f}</div>
                        <div style="font-family: JetBrains Mono; color: #5a6a8a; font-size: 0.7rem;">{tp2_name} • {abs(current_price - tp2):.1f}pt</div>
                    </div>
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
        
        col1, col2 = st.columns(2)
        
        with col1:
            asian_aligns = st.checkbox("Asian session aligned with direction", value=False)
            london_sweep = st.checkbox("London sweep confirmed", value=False)
            line_cluster = st.checkbox("Lines cluster within 3 points", value=False)
        
        with col2:
            data_reaction = st.radio("7:30 AM Data Reaction", 
                                      ["aligned", "absorbed", "against"],
                                      horizontal=True)
            opening_drive = st.checkbox("8:30-9:00 AM drive aligned", value=False)
        
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
    # TAB 4: TRADE LOG
    # ============================================================
    with tab4:
        st.markdown("### 📋 Trade Log")
        st.markdown("*Track your trades to measure the system's performance*")
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Initialize session state for trades
        if 'trades' not in st.session_state:
            st.session_state.trades = []
        
        with st.expander("➕ Log New Trade", expanded=True):
            tcol1, tcol2, tcol3 = st.columns(3)
            
            with tcol1:
                trade_date = st.date_input("Trade Date", value=datetime.now().date(), key="trade_date")
                trade_session = st.selectbox("Session", ["Asian (Futures)", "NY (Options)"])
                trade_direction = st.selectbox("Direction", ["LONG", "SHORT"])
            
            with tcol2:
                trade_entry = st.number_input("Entry Price", value=6865.0, step=0.25, key="trade_entry")
                trade_exit = st.number_input("Exit Price", value=6870.0, step=0.25, key="trade_exit")
                trade_contracts = st.number_input("Contracts", value=2, min_value=1, key="trade_contracts")
            
            with tcol3:
                trade_confluence = st.slider("Confluence Score", 0.0, 5.0, 3.0, 0.5, key="trade_conf")
                trade_notes = st.text_input("Notes", key="trade_notes")
                trade_account = st.selectbox("Account", ["Account 1", "Account 2", "Account 3", "Tastytrade"],
                                             key="trade_acct")
            
            if st.button("💾 Save Trade"):
                pnl_per_point = 50 if "Futures" in trade_session else 100
                direction_mult = 1 if trade_direction == "LONG" else -1
                pnl = direction_mult * (trade_exit - trade_entry) * trade_contracts * pnl_per_point
                
                trade = {
                    'Date': str(trade_date),
                    'Session': trade_session,
                    'Direction': trade_direction,
                    'Entry': trade_entry,
                    'Exit': trade_exit,
                    'Contracts': trade_contracts,
                    'P&L': f"${pnl:,.0f}",
                    'Confluence': trade_confluence,
                    'Account': trade_account,
                    'Notes': trade_notes
                }
                st.session_state.trades.append(trade)
                st.success(f"Trade logged! P&L: ${pnl:,.0f}")
        
        if st.session_state.trades:
            st.markdown("### 📊 Trade History")
            df = pd.DataFrame(st.session_state.trades)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Summary stats
            total_trades = len(st.session_state.trades)
            st.markdown(f"**Total Trades Logged: {total_trades}**")
        else:
            st.info("No trades logged yet. Start tracking your trades above.")


if __name__ == "__main__":
    main()
