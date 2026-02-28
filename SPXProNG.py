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
        min-height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
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
                            st.caption(f"Auto-detected: ES - SPX = **{auto_spread:+.2f}** (from {spread_result['samples']} matched candles)")
                        else:
                            auto_spread = 0.0
                            st.caption(f"Could not auto-detect spread: {spread_result['error']}")
                        
                        es_offset = st.number_input(
                            "ES - SPX offset", 
                            value=auto_spread, step=0.25, format="%.2f",
                            help="Subtracted from ES prices to approximate SPX levels. Positive = ES trades above SPX."
                        )
                        st.session_state['_es_offset'] = es_offset
                        
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
        
        # Display the four key levels
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            hw_asc = levels['key_levels']['highest_wick_ascending']
            if hw_asc:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">HW Ascending ↗</div>
                    <div class="metric-value-bear">{hw_asc['value_at_9am']:.2f}</div>
                    <div class="metric-label" style="font-size:0.7rem; margin-top:5px;">Anchor: {hw_asc['anchor_price']:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            hb_asc = levels['key_levels']['highest_bounce_ascending']
            if hb_asc:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">HB Ascending ↗</div>
                    <div class="metric-value-bear">{hb_asc['value_at_9am']:.2f}</div>
                    <div class="metric-label" style="font-size:0.7rem; margin-top:5px;">Anchor: {hb_asc['anchor_price']:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col3:
            lr_desc = levels['key_levels']['lowest_rejection_descending']
            if lr_desc:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">LR Descending ↘</div>
                    <div class="metric-value-bull">{lr_desc['value_at_9am']:.2f}</div>
                    <div class="metric-label" style="font-size:0.7rem; margin-top:5px;">Anchor: {lr_desc['anchor_price']:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col4:
            lw_desc = levels['key_levels']['lowest_wick_descending']
            if lw_desc:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">LW Descending ↘</div>
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
        st.markdown("### 🌙 Asian Session — Projected Line Levels")
        st.markdown("*Where are the lines during the overnight session?*")
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Determine correct overnight date
        prior_wd_tab2 = prior_date.weekday() if hasattr(prior_date, 'weekday') else datetime.combine(prior_date, time(0,0)).weekday()
        if prior_wd_tab2 == 4:  # Friday
            overnight_date_tab2 = next_date - timedelta(days=1)  # Sunday
            st.markdown("*⚠️ Friday → Monday: Globex opens Sunday 5:00 PM CT*")
        else:
            overnight_date_tab2 = prior_date
        
        # Line Values at Key Overnight Times
        key_times_ct = [
            ("5:00 PM — Globex Open", time(17, 0), overnight_date_tab2),
            ("6:00 PM — Sydney", time(18, 0), overnight_date_tab2),
            ("7:00 PM — Pre-Tokyo", time(19, 0), overnight_date_tab2),
            ("8:00 PM — Tokyo Active", time(20, 0), overnight_date_tab2),
            ("9:00 PM", time(21, 0), overnight_date_tab2),
            ("10:00 PM", time(22, 0), overnight_date_tab2),
            ("11:00 PM", time(23, 0), overnight_date_tab2),
            ("12:00 AM — Midnight", time(0, 0), next_date),
            ("1:00 AM", time(1, 0), next_date),
            ("2:00 AM — London Open", time(2, 0), next_date),
            ("4:00 AM", time(4, 0), next_date),
            ("6:00 AM", time(6, 0), next_date),
            ("7:30 AM — Data Drop", time(7, 30), next_date),
            ("8:30 AM — Market Open", time(8, 30), next_date),
            ("9:00 AM — Decision", time(9, 0), next_date),
        ]
        
        time_table = []
        for label, t, d in key_times_ct:
            dt = datetime.combine(d, t)
            row = {'Time (CT)': label}
            
            hw = levels['key_levels']['highest_wick_ascending']
            if hw:
                row['HW Asc ↗'] = f"{calculate_line_value(hw['anchor_price'], hw['anchor_time'], dt, 'ascending'):.2f}"
            
            hb = levels['key_levels']['highest_bounce_ascending']
            if hb:
                row['HB Asc ↗'] = f"{calculate_line_value(hb['anchor_price'], hb['anchor_time'], dt, 'ascending'):.2f}"
            
            lr = levels['key_levels']['lowest_rejection_descending']
            if lr:
                row['LR Desc ↘'] = f"{calculate_line_value(lr['anchor_price'], lr['anchor_time'], dt, 'descending'):.2f}"
            
            lw = levels['key_levels']['lowest_wick_descending']
            if lw:
                row['LW Desc ↘'] = f"{calculate_line_value(lw['anchor_price'], lw['anchor_time'], dt, 'descending'):.2f}"
            
            time_table.append(row)
        
        st.dataframe(pd.DataFrame(time_table), use_container_width=True, hide_index=True, height=560)
        
        st.markdown("""
        <div class="metric-card" style="margin-top:10px;">
            <div style="font-family: 'JetBrains Mono'; color: #8892b0; font-size: 0.85rem;">
                <strong style="color: #ff5252;">HW Asc ↗</strong> = Highest Wick Ascending • 
                <strong style="color: #ff5252;">HB Asc ↗</strong> = Highest Bounce Ascending<br>
                <strong style="color: #69f0ae;">LR Desc ↘</strong> = Lowest Rejection Descending • 
                <strong style="color: #69f0ae;">LW Desc ↘</strong> = Lowest Wick Descending<br><br>
                <strong style="color: #ffd740;">Trade Setup:</strong> When price touches a projected line during Tokyo Active (8PM-12AM CT), 
                enter with 3pt stop, 5pt target. Max 2 trades per session.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # ============================================================
    # TAB 3: NY SESSION OPTIONS
    # ============================================================
    with tab3:
        st.markdown("### ☀️ NY Session Options Module")
        st.markdown("*Tastytrade — Naked SPX Calls & Puts • 0DTE*")
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # 9 AM Read
        st.markdown("### 🎯 9:00 AM Decision Framework")
        
        # Auto-fill from live price if available
        default_price = 6865.0
        if live_mode and live_price_data and live_price_data.get('ok'):
            default_price = live_price_data['price'] - es_offset_val
        
        current_price = st.number_input("Current SPX Price", 
                                         value=default_price, step=0.5, format="%.2f",
                                         key="current_spx",
                                         help="Auto-filled from live ES price when LIVE MODE is on")
        
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
            # The two ascending lines
            asc_high = max(hw_val, hb_val)
            asc_low = min(hw_val, hb_val)
            
            # The two descending lines
            desc_high = max(lr_val, lw_val)
            desc_low = min(lr_val, lw_val)
            
            if current_price > asc_high:
                signal = "BULLISH — TREND DAY"
                signal_detail = f"Price {current_price:.2f} is ABOVE both ascending lines ({asc_low:.2f} & {asc_high:.2f}). Highest ascending line becomes support. Buy CALLS on pullbacks to {asc_high:.2f}."
                signal_class = "bull"
            
            elif current_price >= asc_low and current_price <= asc_high:
                signal = "BETWEEN ASCENDING LINES"
                signal_detail = f"Price {current_price:.2f} is between ascending lines. Entry: Highest Bounce line ({hb_val:.2f}). Exit: Highest Wick line ({hw_val:.2f})."
                signal_class = "neutral"
            
            elif current_price < asc_low and current_price > desc_low:
                signal = "BEARISH BIAS"
                signal_detail = f"Price {current_price:.2f} is BELOW both ascending lines ({asc_low:.2f} & {asc_high:.2f}). Buyers trapped above. Buy PUTS. Target 1: {desc_high:.2f}. Target 2: {desc_low:.2f}."
                signal_class = "bear"
            
            elif current_price >= desc_low and current_price <= desc_high:
                signal = "BETWEEN DESCENDING LINES"
                signal_detail = f"Price {current_price:.2f} is between descending lines. Entry: Lowest Rejection line ({lr_val:.2f}). Exit: Lowest Wick line ({lw_val:.2f})."
                signal_class = "neutral"
            
            elif current_price < desc_low:
                signal = "BEARISH — TREND DAY"
                signal_detail = f"Price {current_price:.2f} is BELOW all lines including descending ({desc_high:.2f} & {desc_low:.2f}). Lowest descending line becomes resistance. Buy PUTS on rallies to {desc_low:.2f}."
                signal_class = "bear"
        
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
