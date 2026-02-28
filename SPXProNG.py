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
# Built on the 0.52 Rate Line Projection Framework
# ============================================================

st.set_page_config(
    page_title="SPX Prophet Next Gen",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM STYLING
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #0d1117 50%, #0a0f1a 100%);
    }
    
    .main-header {
        font-family: 'Orbitron', monospace;
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00d4ff 0%, #7b2ff7 50%, #ff6b35 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 10px 0;
        letter-spacing: 3px;
        text-transform: uppercase;
    }
    
    .sub-header {
        font-family: 'Rajdhani', sans-serif;
        color: #8892b0;
        text-align: center;
        font-size: 1rem;
        letter-spacing: 5px;
        text-transform: uppercase;
        margin-bottom: 20px;
    }
    
    .metric-card {
        background: linear-gradient(145deg, #131a2e 0%, #0d1220 100%);
        border: 1px solid #1e2d4a;
        border-radius: 12px;
        padding: 20px;
        margin: 8px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    
    .metric-label {
        font-family: 'Rajdhani', sans-serif;
        color: #5a6a8a;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .metric-value-bull {
        font-family: 'JetBrains Mono', monospace;
        color: #00e676;
        font-size: 1.6rem;
        font-weight: 700;
    }
    
    .metric-value-bear {
        font-family: 'JetBrains Mono', monospace;
        color: #ff1744;
        font-size: 1.6rem;
        font-weight: 700;
    }
    
    .metric-value-neutral {
        font-family: 'JetBrains Mono', monospace;
        color: #00d4ff;
        font-size: 1.6rem;
        font-weight: 700;
    }
    
    .signal-box-bull {
        background: linear-gradient(145deg, #0a2e1a 0%, #0d1220 100%);
        border: 1px solid #00e676;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    
    .signal-box-bear {
        background: linear-gradient(145deg, #2e0a0a 0%, #0d1220 100%);
        border: 1px solid #ff1744;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    
    .signal-box-neutral {
        background: linear-gradient(145deg, #1a1a2e 0%, #0d1220 100%);
        border: 1px solid #ffd740;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    
    .confluence-high {
        font-family: 'Orbitron', monospace;
        color: #00e676;
        font-size: 2rem;
    }
    
    .confluence-med {
        font-family: 'Orbitron', monospace;
        color: #ffd740;
        font-size: 2rem;
    }
    
    .confluence-low {
        font-family: 'Orbitron', monospace;
        color: #ff1744;
        font-size: 2rem;
    }
    
    .prop-account {
        background: linear-gradient(145deg, #131a2e 0%, #0d1220 100%);
        border: 1px solid #1e2d4a;
        border-radius: 12px;
        padding: 15px;
        margin: 5px 0;
    }
    
    .section-divider {
        border-top: 1px solid #1e2d4a;
        margin: 20px 0;
    }
    
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0e17 0%, #0d1220 100%);
        border-right: 1px solid #1e2d4a;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-family: 'Rajdhani', sans-serif;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# CORE ENGINE: Line Projection Calculator
# ============================================================

RATE_PER_CANDLE = 0.52
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
    
    direction: 'ascending' (+0.52/candle) or 'descending' (-0.52/candle)
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
# MAIN APPLICATION
# ============================================================

def main():
    # Header
    st.markdown('<div class="main-header">SPX Prophet Next Gen</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">0.52 Rate Structure Engine • Futures & Options</div>', unsafe_allow_html=True)
    
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
        
        st.markdown("---")
        st.markdown("### 📍 Session Extremes (Candlestick Wicks)")
        
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
        
        rate = st.number_input("Rate per 30min candle", value=0.52, step=0.01, format="%.2f",
                               help="The proprietary rate of price movement per candle")
        
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
        
        # Display the four key levels
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            hw_asc = levels['key_levels']['highest_wick_ascending']
            if hw_asc:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Highest Wick Ascending</div>
                    <div class="metric-value-bear">{hw_asc['value_at_9am']:.2f}</div>
                    <div class="metric-label" style="font-size:0.7rem; margin-top:5px;">Anchor: {hw_asc['anchor_price']:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            hb_asc = levels['key_levels']['highest_bounce_ascending']
            if hb_asc:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Highest Bounce Ascending</div>
                    <div class="metric-value-bear">{hb_asc['value_at_9am']:.2f}</div>
                    <div class="metric-label" style="font-size:0.7rem; margin-top:5px;">Anchor: {hb_asc['anchor_price']:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col3:
            lr_desc = levels['key_levels']['lowest_rejection_descending']
            if lr_desc:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Lowest Rejection Descending</div>
                    <div class="metric-value-bull">{lr_desc['value_at_9am']:.2f}</div>
                    <div class="metric-label" style="font-size:0.7rem; margin-top:5px;">Anchor: {lr_desc['anchor_price']:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col4:
            lw_desc = levels['key_levels']['lowest_wick_descending']
            if lw_desc:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Lowest Wick Descending</div>
                    <div class="metric-value-bull">{lw_desc['value_at_9am']:.2f}</div>
                    <div class="metric-label" style="font-size:0.7rem; margin-top:5px;">Anchor: {lw_desc['anchor_price']:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # ============================================================
        # STRUCTURAL MAP CHART
        # ============================================================
        
        # Chart time range: from prior NY session start through next day NY close
        chart_start = datetime.combine(prior_date, time(8, 30))
        chart_end = datetime.combine(next_date, time(15, 0))
        
        fig = go.Figure()
        
        # Add session boxes if enabled
        if show_session_boxes:
            # We'll add sessions for the overnight and next day
            sessions_to_draw = []
            
            # Prior day NY session
            sessions_to_draw.append({
                'name': 'New York',
                'start': datetime.combine(prior_date, time(8, 30)),
                'end': datetime.combine(prior_date, time(15, 0)),
                'color': SESSION_TIMES['New York']['color'],
                'border': SESSION_TIMES['New York']['border']
            })
            
            # Maintenance
            sessions_to_draw.append({
                'name': 'Maintenance',
                'start': datetime.combine(prior_date, time(16, 0)),
                'end': datetime.combine(prior_date, time(17, 0)),
                'color': 'rgba(100,100,100,0.1)',
                'border': 'rgba(100,100,100,0.3)'
            })
            
            # Sydney (overnight)
            sessions_to_draw.append({
                'name': 'Sydney',
                'start': datetime.combine(prior_date, time(17, 0)),
                'end': datetime.combine(prior_date, time(19, 0)),
                'color': SESSION_TIMES['Sydney']['color'],
                'border': SESSION_TIMES['Sydney']['border']
            })
            
            # Tokyo
            sessions_to_draw.append({
                'name': 'Tokyo',
                'start': datetime.combine(prior_date, time(19, 0)),
                'end': datetime.combine(next_date, time(2, 0)),
                'color': SESSION_TIMES['Tokyo']['color'],
                'border': SESSION_TIMES['Tokyo']['border']
            })
            
            # London
            sessions_to_draw.append({
                'name': 'London',
                'start': datetime.combine(next_date, time(2, 0)),
                'end': datetime.combine(next_date, time(8, 30)),
                'color': SESSION_TIMES['London']['color'],
                'border': SESSION_TIMES['London']['border']
            })
            
            # Next day NY
            sessions_to_draw.append({
                'name': 'New York',
                'start': datetime.combine(next_date, time(8, 30)),
                'end': datetime.combine(next_date, time(15, 0)),
                'color': SESSION_TIMES['New York']['color'],
                'border': SESSION_TIMES['New York']['border']
            })
            
            for session in sessions_to_draw:
                fig.add_vrect(
                    x0=session['start'], x1=session['end'],
                    fillcolor=session['color'],
                    line=dict(color=session['border'], width=1, dash='dot'),
                )
                # Add session label as separate annotation
                mid_time = session['start'] + (session['end'] - session['start']) / 2
                fig.add_annotation(
                    x=session['start'], y=1, yref="paper",
                    text=session['name'], showarrow=False,
                    font=dict(size=10, color=session['border']),
                    xanchor="left", yshift=10
                )
        
        # Add 9:00 AM vertical decision line
        nine_am = datetime.combine(next_date, time(9, 0))
        nine_am_ts = nine_am.timestamp() * 1000
        fig.add_shape(
            type="line", x0=nine_am, x1=nine_am, y0=0, y1=1,
            yref="paper", line=dict(color="#ffd740", width=2, dash="dash")
        )
        fig.add_annotation(
            x=nine_am, y=1, yref="paper",
            text="9:00 AM Decision", showarrow=False,
            font=dict(color="#ffd740", size=11),
            yshift=10
        )
        
        # Plot ascending lines (red)
        for i, asc_line in enumerate(levels['ascending']):
            series = generate_line_series(
                asc_line['anchor_price'], asc_line['anchor_time'],
                chart_start, chart_end, 'ascending'
            )
            if series:
                times, prices = zip(*series)
                is_wick = asc_line['type'] == 'highest_wick'
                fig.add_trace(go.Scatter(
                    x=list(times), y=list(prices),
                    mode='lines',
                    name=f"↗ {'HW' if is_wick else f'B{i+1}'}: {asc_line['anchor_price']:.1f}",
                    line=dict(
                        color='#ff1744' if is_wick else '#ff5252',
                        width=3 if is_wick else 2,
                        dash='solid' if is_wick else 'dash'
                    ),
                    opacity=1.0 if is_wick or show_all_lines else 0.4
                ))
        
        # Plot descending lines (green)
        for i, desc_line in enumerate(levels['descending']):
            series = generate_line_series(
                desc_line['anchor_price'], desc_line['anchor_time'],
                chart_start, chart_end, 'descending'
            )
            if series:
                times, prices = zip(*series)
                is_wick = desc_line['type'] == 'lowest_wick'
                fig.add_trace(go.Scatter(
                    x=list(times), y=list(prices),
                    mode='lines',
                    name=f"↘ {'LW' if is_wick else f'R{i+1}'}: {desc_line['anchor_price']:.1f}",
                    line=dict(
                        color='#00e676' if is_wick else '#69f0ae',
                        width=3 if is_wick else 2,
                        dash='solid' if is_wick else 'dash'
                    ),
                    opacity=1.0 if is_wick or show_all_lines else 0.4
                ))
        
        # Add horizontal 9 AM levels
        key = levels['key_levels']
        level_configs = [
            (key['highest_wick_ascending'], '#ff1744', 'HW Asc @ 9AM'),
            (key['highest_bounce_ascending'], '#ff5252', 'HB Asc @ 9AM'),
            (key['lowest_rejection_descending'], '#69f0ae', 'LR Desc @ 9AM'),
            (key['lowest_wick_descending'], '#00e676', 'LW Desc @ 9AM'),
        ]
        
        for level, color, label in level_configs:
            if level:
                fig.add_shape(
                    type="line", x0=0, x1=1, xref="paper",
                    y0=level['value_at_9am'], y1=level['value_at_9am'],
                    line=dict(color=color, width=1, dash="dot")
                )
                fig.add_annotation(
                    x=1, xref="paper", y=level['value_at_9am'],
                    text=f"{label}: {level['value_at_9am']:.2f}",
                    showarrow=False, font=dict(size=9, color=color),
                    xshift=5, xanchor="left"
                )
        
        # Add anchor point markers
        for bounce in bounces:
            fig.add_trace(go.Scatter(
                x=[bounce['time']], y=[bounce['price']],
                mode='markers',
                marker=dict(symbol='triangle-up', size=14, color='#ff5252',
                           line=dict(width=2, color='white')),
                name=f"Bounce: {bounce['price']:.1f}",
                showlegend=False
            ))
        
        for rejection in rejections:
            fig.add_trace(go.Scatter(
                x=[rejection['time']], y=[rejection['price']],
                mode='markers',
                marker=dict(symbol='triangle-down', size=14, color='#69f0ae',
                           line=dict(width=2, color='white')),
                name=f"Rejection: {rejection['price']:.1f}",
                showlegend=False
            ))
        
        # Highest/lowest wick markers
        fig.add_trace(go.Scatter(
            x=[highest_wick['time']], y=[highest_wick['price']],
            mode='markers',
            marker=dict(symbol='diamond', size=14, color='#ff1744',
                       line=dict(width=2, color='white')),
            name=f"Highest Wick: {highest_wick['price']:.1f}",
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=[lowest_wick['time']], y=[lowest_wick['price']],
            mode='markers',
            marker=dict(symbol='diamond', size=14, color='#00e676',
                       line=dict(width=2, color='white')),
            name=f"Lowest Wick: {lowest_wick['price']:.1f}",
            showlegend=False
        ))
        
        # Chart styling
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='#0a0a0f',
            plot_bgcolor='#0d1117',
            height=700,
            margin=dict(l=60, r=200, t=40, b=60),
            xaxis=dict(
                gridcolor='#1a2332',
                showgrid=True,
                tickformat='%b %d\n%I:%M %p',
                dtick=3600000 * 2,  # 2 hour ticks
            ),
            yaxis=dict(
                gridcolor='#1a2332',
                showgrid=True,
                tickformat='.2f',
                side='right',
            ),
            legend=dict(
                bgcolor='rgba(13,18,32,0.9)',
                bordercolor='#1e2d4a',
                borderwidth=1,
                font=dict(size=10, family='JetBrains Mono'),
                x=1.01, y=1,
            ),
            font=dict(family='JetBrains Mono', color='#8892b0'),
            hovermode='x unified',
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # ============================================================
        # ALL LINES TABLE
        # ============================================================
        st.markdown("### 📋 All Projected Lines at 9:00 AM CT")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🔺 Ascending Lines (Red)**")
            asc_data = []
            for line in levels['ascending']:
                asc_data.append({
                    'Source': line['source'],
                    'Anchor Price': f"{line['anchor_price']:.2f}",
                    'Value @ 9AM': f"{line['value_at_9am']:.2f}",
                    'Change': f"+{line['value_at_9am'] - line['anchor_price']:.2f}"
                })
            if asc_data:
                st.dataframe(pd.DataFrame(asc_data), use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("**🔻 Descending Lines (Green)**")
            desc_data = []
            for line in levels['descending']:
                desc_data.append({
                    'Source': line['source'],
                    'Anchor Price': f"{line['anchor_price']:.2f}",
                    'Value @ 9AM': f"{line['value_at_9am']:.2f}",
                    'Change': f"{line['value_at_9am'] - line['anchor_price']:.2f}"
                })
            if desc_data:
                st.dataframe(pd.DataFrame(desc_data), use_container_width=True, hide_index=True)
    
    # ============================================================
    # TAB 2: ASIAN SESSION FUTURES
    # ============================================================
    with tab2:
        st.markdown("### 🌙 Asian Session Futures Module")
        st.markdown("*Futures Desk — ES/MES • Target: 5 points*")
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Prop Firm Accounts
        st.markdown("### 💼 Account Status")
        
        accounts = [
            {"name": "Account 1", "daily_limit": 800, "max_dd": -2000, "started": "2/18/26", "days": "8 of 5"},
            {"name": "Account 2", "daily_limit": 800, "max_dd": -2000, "started": "2/23/26", "days": "4 of 5"},
            {"name": "Account 3", "daily_limit": 400, "max_dd": -2000, "started": "2/24/26", "days": "3 of 5"},
        ]
        
        cols = st.columns(3)
        for idx, acct in enumerate(accounts):
            with cols[idx]:
                st.markdown(f"""
                <div class="prop-account">
                    <div class="metric-label">{acct['name']}</div>
                    <div class="metric-value-neutral" style="font-size:1.2rem;">
                        Daily Limit: ${acct['daily_limit']}
                    </div>
                    <div class="metric-label" style="margin-top:8px;">
                        Max DD: ${acct['max_dd']:,} • Started: {acct['started']}<br>
                        Days Traded: {acct['days']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Position Size Calculator
        st.markdown("### 📐 Position Size Calculator")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_account = st.selectbox("Select Account", 
                                            ["Account 1 ($800)", "Account 2 ($800)", "Account 3 ($400)"])
        with col2:
            stop_distance = st.number_input("Stop Distance (points)", value=3.0, step=0.25, 
                                            min_value=1.0, max_value=20.0)
        with col3:
            instrument = st.selectbox("Instrument", ["ES ($50/pt)", "MES ($5/pt)"])
        
        daily_limit = 400 if "400" in selected_account else 800
        instr = "ES" if "ES" in instrument else "MES"
        
        risk = calculate_prop_firm_risk(daily_limit, stop_distance, instr)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Contracts</div>
                <div class="metric-value-neutral">{risk['contracts']} {instr}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Risk Per Trade</div>
                <div class="metric-value-bear">${risk['risk_per_trade']:.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Profit on 5pt Move</div>
                <div class="metric-value-bull">${risk['profit_5pt_move']:.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">After 1 Loss, Remaining</div>
                <div class="metric-value-neutral">${risk['remaining_after_1_loss']:.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # ES-specific display for the bigger accounts
        if instr == "ES":
            st.markdown(f"""
            <div class="metric-card" style="text-align:center; margin-top:10px;">
                <div class="metric-label">RECOMMENDED SETUP</div>
                <div style="font-family: 'JetBrains Mono'; color: #00d4ff; font-size: 1.3rem; margin-top: 8px;">
                    {risk['contracts']} ES × 5pt target = ${risk['profit_5pt_move']:.0f} per trade
                </div>
                <div style="font-family: 'Rajdhani'; color: #5a6a8a; font-size: 0.9rem; margin-top: 5px;">
                    Stop: {stop_distance}pt (${risk['risk_per_trade']:.0f} risk) • Max 2 trades per session • 
                    R:R = {5/stop_distance:.1f}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Asian Session Trading Windows
        st.markdown("### 🕐 Trading Windows")
        
        st.markdown("""
        <div class="metric-card">
            <table style="width:100%; font-family: 'JetBrains Mono'; color: #8892b0; font-size: 0.85rem;">
                <tr style="border-bottom: 1px solid #1e2d4a;">
                    <td style="padding: 8px; color: #5a6a8a;">5:00 - 6:00 PM CT</td>
                    <td style="padding: 8px;">Globex Open</td>
                    <td style="padding: 8px; color: #ffd740;">⚡ Watch for gap fills at projected lines</td>
                </tr>
                <tr style="border-bottom: 1px solid #1e2d4a;">
                    <td style="padding: 8px; color: #5a6a8a;">6:00 - 8:00 PM CT</td>
                    <td style="padding: 8px;">Sydney / Early Tokyo</td>
                    <td style="padding: 8px; color: #ff5252;">🔇 Dead zone — avoid unless at a line</td>
                </tr>
                <tr style="border-bottom: 1px solid #1e2d4a;">
                    <td style="padding: 8px; color: #5a6a8a;">8:00 PM - 12:00 AM CT</td>
                    <td style="padding: 8px;">Tokyo Active</td>
                    <td style="padding: 8px; color: #00e676;">✅ PRIMARY WINDOW — Best setups here</td>
                </tr>
                <tr>
                    <td style="padding: 8px; color: #5a6a8a;">12:00 - 2:00 AM CT</td>
                    <td style="padding: 8px;">Tokyo Close / Pre-London</td>
                    <td style="padding: 8px; color: #ffd740;">⚡ Secondary window — new moves can start</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Quick reference: where are lines right now
        st.markdown("### 📍 Line Values at Key Times")
        
        key_times_ct = [
            ("5:00 PM (Globex Open)", time(17, 0), prior_date),
            ("8:00 PM (Tokyo Active)", time(20, 0), prior_date),
            ("10:00 PM", time(22, 0), prior_date),
            ("12:00 AM", time(0, 0), next_date),
            ("2:00 AM (London Open)", time(2, 0), next_date),
            ("7:30 AM (Data Drop)", time(7, 30), next_date),
            ("8:30 AM (Market Open)", time(8, 30), next_date),
            ("9:00 AM (Decision)", time(9, 0), next_date),
        ]
        
        time_table = []
        for label, t, d in key_times_ct:
            dt = datetime.combine(d, t)
            row = {'Time (CT)': label}
            
            # Highest wick ascending
            hw = levels['key_levels']['highest_wick_ascending']
            if hw:
                row['HW Asc'] = f"{calculate_line_value(hw['anchor_price'], hw['anchor_time'], dt, 'ascending'):.2f}"
            
            # Highest bounce ascending
            hb = levels['key_levels']['highest_bounce_ascending']
            if hb:
                row['HB Asc'] = f"{calculate_line_value(hb['anchor_price'], hb['anchor_time'], dt, 'ascending'):.2f}"
            
            # Lowest rejection descending
            lr = levels['key_levels']['lowest_rejection_descending']
            if lr:
                row['LR Desc'] = f"{calculate_line_value(lr['anchor_price'], lr['anchor_time'], dt, 'descending'):.2f}"
            
            # Lowest wick descending
            lw = levels['key_levels']['lowest_wick_descending']
            if lw:
                row['LW Desc'] = f"{calculate_line_value(lw['anchor_price'], lw['anchor_time'], dt, 'descending'):.2f}"
            
            time_table.append(row)
        
        st.dataframe(pd.DataFrame(time_table), use_container_width=True, hide_index=True)
    
    # ============================================================
    # TAB 3: NY SESSION OPTIONS
    # ============================================================
    with tab3:
        st.markdown("### ☀️ NY Session Options Module")
        st.markdown("*Tastytrade — Naked SPX Calls & Puts • 0DTE*")
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # 9 AM Read
        st.markdown("### 🎯 9:00 AM Decision Framework")
        
        current_price = st.number_input("Current SPX Price (at 9:00 AM CT)", 
                                         value=6865.0, step=0.5, format="%.2f",
                                         key="current_spx")
        
        # Determine position relative to lines
        hw_val = levels['key_levels']['highest_wick_ascending']['value_at_9am'] if levels['key_levels']['highest_wick_ascending'] else None
        hb_val = levels['key_levels']['highest_bounce_ascending']['value_at_9am'] if levels['key_levels']['highest_bounce_ascending'] else None
        lr_val = levels['key_levels']['lowest_rejection_descending']['value_at_9am'] if levels['key_levels']['lowest_rejection_descending'] else None
        lw_val = levels['key_levels']['lowest_wick_descending']['value_at_9am'] if levels['key_levels']['lowest_wick_descending'] else None
        
        # Determine signal
        signal = "NEUTRAL"
        signal_detail = ""
        signal_class = "neutral"
        
        if hw_val and hb_val and lr_val and lw_val:
            upper_high = max(hw_val, hb_val)
            upper_low = min(hw_val, hb_val)
            lower_high = max(lr_val, lw_val)
            lower_low = min(lr_val, lw_val)
            
            if current_price > upper_high:
                signal = "BULLISH — TREND DAY"
                signal_detail = f"Price {current_price:.2f} is ABOVE all ascending lines. Highest ascending line ({upper_high:.2f}) becomes support. Look for bounces off this line to buy calls."
                signal_class = "bull"
            elif current_price < upper_low:
                if current_price > lower_high:
                    signal = "BEARISH BIAS"
                    signal_detail = f"Price {current_price:.2f} is BELOW ascending lines ({upper_low:.2f} - {upper_high:.2f}). The trap has set — market sucked in buyers above and rejected. Buy PUTS."
                    signal_class = "bear"
                elif current_price < lower_low:
                    signal = "BEARISH — TREND DAY"
                    signal_detail = f"Price {current_price:.2f} is BELOW all descending lines. Lowest descending line ({lower_low:.2f}) becomes resistance. Look for rejections off this line to buy puts."
                    signal_class = "bear"
                else:
                    signal = "AT DESCENDING ZONE"
                    signal_detail = f"Price {current_price:.2f} is between descending lines ({lower_low:.2f} - {lower_high:.2f}). Use lowest rejection line as entry, lowest wick line as exit for CALL setup (bear trap)."
                    signal_class = "neutral"
            else:
                signal = "BETWEEN ASCENDING LINES"
                signal_detail = f"Price {current_price:.2f} is between ascending lines ({upper_low:.2f} - {upper_high:.2f}). Use highest bounce line as entry, highest wick line as exit."
                signal_class = "neutral"
        
        st.markdown(f"""
        <div class="signal-box-{signal_class}">
            <div style="font-family: 'Orbitron'; font-size: 1.5rem; color: {'#00e676' if signal_class == 'bull' else '#ff1744' if signal_class == 'bear' else '#ffd740'};">
                {signal}
            </div>
            <div style="font-family: 'Rajdhani'; font-size: 1rem; color: #8892b0; margin-top: 10px;">
                {signal_detail}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Confluence Score
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
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Options Calculator
        st.markdown("### 💰 Options Setup")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            option_type = st.selectbox("Direction", ["PUT (Bearish)", "CALL (Bullish)"])
        with col2:
            premium = st.number_input("Premium per contract ($)", value=8.00, step=0.50,
                                       help="Cost of the ATM 0DTE option")
        with col3:
            options_budget = st.number_input("Max risk budget ($)", value=2000, step=100)
        
        premium_total = premium * 100  # SPX options are $100 multiplier
        contracts = int(options_budget / premium_total) if premium_total > 0 else 0
        
        # Calculate targets based on lines
        if "PUT" in option_type and lr_val and lw_val:
            target_1 = max(lr_val, lw_val)  # first descending line
            target_2 = min(lr_val, lw_val)  # second descending line
            target_label = "Descending line targets"
        elif "CALL" in option_type and hw_val and hb_val:
            target_1 = min(hw_val, hb_val)
            target_2 = max(hw_val, hb_val)
            target_label = "Ascending line targets"
        else:
            target_1 = current_price + 10
            target_2 = current_price + 20
            target_label = "Default targets"
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Contracts</div>
                <div class="metric-value-neutral">{contracts}</div>
                <div class="metric-label" style="font-size:0.7rem;">@ ${premium:.2f} ea (${premium_total:.0f})</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Risk</div>
                <div class="metric-value-bear">${contracts * premium_total:,.0f}</div>
                <div class="metric-label" style="font-size:0.7rem;">Max loss = premium paid</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            move_to_target = abs(target_1 - current_price)
            est_profit_1 = contracts * move_to_target * 100  # rough estimate at high delta
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Target 1: {target_1:.2f}</div>
                <div class="metric-value-bull">~${est_profit_1:,.0f}</div>
                <div class="metric-label" style="font-size:0.7rem;">{move_to_target:.1f}pt move • Take 1/3</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            move_to_target2 = abs(target_2 - current_price)
            est_profit_2 = contracts * move_to_target2 * 100
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Target 2: {target_2:.2f}</div>
                <div class="metric-value-bull">~${est_profit_2:,.0f}</div>
                <div class="metric-label" style="font-size:0.7rem;">{move_to_target2:.1f}pt move • Take 1/3</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card" style="margin-top:10px;">
            <div style="font-family: 'JetBrains Mono'; color: #8892b0; font-size: 0.85rem;">
                <strong style="color: #ffd740;">⏰ ENTRY:</strong> After 9:05 AM CT (let IV settle)<br>
                <strong style="color: #ffd740;">⏰ TIME STOP:</strong> Close by 11:00 AM CT if not working<br>
                <strong style="color: #ffd740;">📏 STRIKE:</strong> ATM {'put' if 'PUT' in option_type else 'call'} — 0DTE expiration<br>
                <strong style="color: #ffd740;">🔄 SCALING:</strong> If price touches ascending line and rejects, add 50% more contracts<br>
                <strong style="color: #ffd740;">🚪 EXIT:</strong> Take 1/3 at each target, trail final 1/3 on lowest descending line
            </div>
        </div>
        """, unsafe_allow_html=True)
    
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
