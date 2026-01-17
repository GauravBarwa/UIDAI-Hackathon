import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ==========================================
# 1. DESIGN SYSTEM & CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Project SAMARTH | UIDAI Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CALLBACK: Safely resets session state
def reset_simulation():
    st.session_state.sim_neev = 0
    st.session_state.sim_gati = 0
    st.session_state.sim_nyay = 0

# Initialize Session State keys
if 'sim_neev' not in st.session_state: st.session_state.sim_neev = 0
if 'sim_gati' not in st.session_state: st.session_state.sim_gati = 0
if 'sim_nyay' not in st.session_state: st.session_state.sim_nyay = 0

css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap');
    
    /* SHIFT GLOBAL HEADER UP */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }

    /* 1. FORCING PURE WHITE BACKGROUND & SOLID BLACK TEXT */
    html, body, [class*="css"], [data-testid="stAppViewContainer"] {
        font-family: 'Poppins', sans-serif;
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    /* TEXT ELEMENTS BLACK */
    [data-testid="stMarkdownContainer"] p, 
    [data-testid="stMarkdownContainer"] h1, 
    [data-testid="stMarkdownContainer"] h2, 
    [data-testid="stMarkdownContainer"] h3, 
    [data-testid="stMarkdownContainer"] h4,
    [data-testid="stWidgetLabel"] p,
    .stTabs [data-baseweb="tab"] {
        color: #000000 !important;
    }

    header[data-testid="stHeader"] {
        background-color: rgba(0,0,0,0) !important;
    }

    /* SUBTITLE STYLE */
    .nowrap-subtitle {
        color: #000000 !important;
        margin-top: -10px;
        font-weight: 500;
        white-space: nowrap; 
        font-size: 1.6rem;
    }
    
    .nowrap-subtitle b {
        color: #B92B27; 
        font-weight: 800;
    }

    /* STATE SELECT CONTAINER */
    .state-select-container {
        margin-top: 35px;
    }

    .state-label {
        color: #000000 !important; 
        font-weight: 700 !important;
        font-size: 16px !important;
        margin-bottom: 5px;
        display: block;
    }

    /* SELECTBOX STYLING */
    div[data-baseweb="select"] > div {
        background-color: #F8F9FA !important;
        border: 1px solid #E0E0E0 !important;
        border-radius: 8px !important;
        color: #000000 !important;
    }
    div[data-baseweb="select"] * {
        color: #000000 !important;
        font-weight: 500 !important;
    }
    ul[data-baseweb="menu"] {
        background-color: #FFFFFF !important;
    }

    /* METRIC CARDS */
    .metric-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        overflow: hidden;
        text-align: center;
        margin-bottom: 20px;
        border: 1px solid #E0E0E0;
    }

    .metric-header {
        padding: 12px;
        color: #000000 !important;
        font-weight: 800;
        font-size: 1.1rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .metric-body {
        padding: 20px 10px;
        background-color: #FFFFFF;
    }

    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #000000 !important;
        margin-bottom: 0px;
    }

    .metric-subtext {
        font-size: 0.9rem;
        color: #555555 !important;
        font-weight: 500;
    }

    /* JUDGE NOTE FORMULA BOX (BIGGER TEXT) */
    .formula-box {
        margin-top: 15px;
        padding: 25px;
        background-color: #F9F9F9;
        border-left: 6px solid #333;
        border-radius: 8px;
        font-size: 1.25rem;
        color: #000000;
        line-height: 1.6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* TECH NOTE BOX (SMALLER) */
    .tech-note-box {
        margin-top: 10px;
        padding: 10px;
        background-color: #F9F9F9;
        border-left: 3px solid #555;
        font-size: 0.9rem;
        color: #333;
    }

    /* CHART NOTES */
    .chart-note {
        font-size: 0.85rem;
        color: #666666;
        font-style: italic;
        margin-top: -10px;
        margin-bottom: 20px;
        text-align: center;
    }
    
    /* MNEMONIC HEADERS (TAB TITLES) */
    .mnemonic-head {
        font-size: 1.4rem;
        font-weight: 500;
        color: #000000;
        margin-bottom: 10px;
    }
    .mnemonic-head b {
        color: #B92B27; /* Red Bold First Letter */
        font-weight: 800;
    }

    /* FLOATING SIMULATOR */
    div[data-testid="stExpander"]:last-of-type {
        position: fixed !important;
        bottom: 20px !important;
        right: 20px !important;
        width: 320px !important;
        z-index: 99999 !important;
        background: #FFFFFF !important;
        border: 2px solid #FF9933 !important;
        box-shadow: 0 12px 35px rgba(0,0,0,0.2) !important;
        border-radius: 15px !important;
    }

    /* EXPANDER HOVER FIX - FORCE WHITE BACKGROUND & BLACK TEXT */
    div[data-testid="stExpander"] details {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    div[data-testid="stExpander"] details summary {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    div[data-testid="stExpander"] details summary:hover {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    div[data-testid="stExpander"] details summary:focus {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    div[data-testid="stExpander"] * {
        color: #000000 !important;
    }

    /* RESET BUTTON */
    div[data-testid="stExpander"] button {
        background-color: #FFFFFF !important;
        color: #B92B27 !important;
        border: 2px solid #B92B27 !important;
        font-weight: 700 !important;
    }
    div[data-testid="stExpander"] button:hover {
        background-color: #FFFFFF !important;
        color: #FF0000 !important;
        border-color: #FF0000 !important;
    }
    
    /* DOWNLOAD BUTTON */
    div[data-testid="stDownloadButton"] button {
        background-color: #FFFFFF !important;
        color: #063970 !important;
        border: 2px solid #063970 !important;
        font-weight: 600 !important;
    }
    div[data-testid="stDownloadButton"] button:hover {
        background-color: #FFFFFF !important;
        color: #063970 !important;
        border-color: #063970 !important;
    }
    div[data-testid="stDownloadButton"] button:active {
        background-color: #F0F0F0 !important;
    }

    [data-testid="stSidebar"] { display: none; }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# ==========================================
# 2. DATA ENGINE
# ==========================================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('aadhaar_hackathon_final_dashboard.csv')
        return df
    except FileNotFoundError:
        return None

df_raw = load_data()
if df_raw is None:
    st.error("DATA MISSING: 'aadhaar_hackathon_final_dashboard.csv' not found.")
    st.stop()

# ==========================================
# 3. FLOATING WHAT-IF SIMULATOR
# ==========================================
with st.expander("What-If Simulator", expanded=False):
    enable_sim = st.checkbox("Enable Simulation Mode", value=False)
    
    if enable_sim:
        st.write("Test interventions:")
        st.slider("Camps (NEEV)", 0, 20, key='sim_neev')
        st.slider("Sync (GATI)", 0, 20, key='sim_gati')
        st.slider("Vans (NYAY)", 0, 20, key='sim_nyay')
        st.button("Reset Simulation", on_click=reset_simulation)
    else:
        st.caption("Enable the checkbox to start simulating policy impacts.")
        if st.session_state.sim_neev != 0: reset_simulation()

# ==========================================
# 4. DATA PROCESSING
# ==========================================
df_sim = df_raw.copy()

if enable_sim:
    df_sim['NEEV_Score'] = (df_sim['MBCI_Score'] + st.session_state.sim_neev).clip(upper=100)
    df_sim['GATI_Score'] = (100 - df_sim['ALV_Score'] + st.session_state.sim_gati).clip(upper=100)
    df_sim['NYAY_Score'] = (df_sim['SEC_Score'] + st.session_state.sim_nyay).clip(upper=100)
    
    df_sim['SAMARTH_Score'] = (
        (0.4 * df_sim['NEEV_Score']) + 
        (0.3 * df_sim['GATI_Score']) + 
        (0.3 * df_sim['NYAY_Score'])
    )
else:
    df_sim['NEEV_Score'] = df_sim['MBCI_Score']
    df_sim['GATI_Score'] = 100 - df_sim['ALV_Score']
    df_sim['NYAY_Score'] = df_sim['SEC_Score']
    df_sim['SAMARTH_Score'] = (
        (0.4 * df_sim['NEEV_Score']) + 
        (0.3 * df_sim['GATI_Score']) + 
        (0.3 * df_sim['NYAY_Score'])
    )

# ==========================================
# 5. HEADER
# ==========================================
c_logo, c_title, c_state = st.columns([1.2, 7.0, 1.8])

with c_logo:
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/c/cf/Aadhaar_Logo.svg/1200px-Aadhaar_Logo.svg.png", width=160)

with c_title:
    st.markdown("<h1 style='color:#B92B27; margin-bottom:0;'>Project SAMARTH</h1>", unsafe_allow_html=True)
    st.markdown("<div class='nowrap-subtitle'><b>S</b>ystemic <b>A</b>adhaar <b>M</b>onitoring <b>A</b>nd <b>R</b>esilience <b>T</b>racking <b>H</b>ub</div>", unsafe_allow_html=True)

with c_state:
    st.markdown('<div class="state-select-container">', unsafe_allow_html=True)
    st.markdown('<span class="state-label">Select State View</span>', unsafe_allow_html=True)
    selected_state = st.selectbox(
        "Select State View",
        ["All India"] + sorted(df_sim['state'].unique().tolist()),
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()
df_view = df_sim if selected_state == "All India" else df_sim[df_sim['state'] == selected_state]

# ==========================================
# 6. CUSTOM METRIC CARDS
# ==========================================
col1, col2, col3, col4 = st.columns(4)

def render_metric_card(column, title, value, subtext, color):
    card_html = f"""
    <div class="metric-card">
        <div class="metric-header" style="background-color: {color}20; color: #000000 !important; border-bottom: 2px solid {color};">
            {title}
        </div>
        <div class="metric-body">
            <div class="metric-value">{value}</div>
            <div class="metric-subtext">{subtext}</div>
        </div>
    </div>
    """
    column.markdown(card_html, unsafe_allow_html=True)

render_metric_card(col1, "SAMARTH Score", f"{df_view['SAMARTH_Score'].mean():.1f}", "Overall Index Score", "#063970")
render_metric_card(col2, "NEEV (Foundation)", f"{df_view['NEEV_Score'].mean():.1f}%", "Compliance (MBCI)", "#FF9933")
render_metric_card(col3, "GATI (Speed)", f"{df_view['GATI_Score'].mean():.1f}%", "Stability (ALV)", "#063970")
render_metric_card(col4, "NYAY (Justice)", f"{df_view['NYAY_Score'].mean():.1f}%", "Equity (SEC)", "#138808")

# ==========================================
# 7. HEATMAP
# ==========================================
shared_chart_layout = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color="#000000", size=12, family="Poppins"), 
    xaxis=dict(
        title_font=dict(color="#000000", size=14, weight='bold'), 
        tickfont=dict(color="#000000"),
        gridcolor="#E0E0E0"
    ),
    yaxis=dict(
        title_font=dict(color="#000000", size=14, weight='bold'), 
        tickfont=dict(color="#000000"),
        gridcolor="#E0E0E0"
    ),
    legend=dict(
        font=dict(color="#000000"),
        title_font=dict(color="#000000")
    ),
    coloraxis_colorbar=dict(
        title_font=dict(color="#000000"),
        tickfont=dict(color="#000000")
    )
)

c_head, c_btn = st.columns([8.5, 1.5])
with c_head:
    st.markdown("### National Resilience Heatmap")
with c_btn:
    csv = df_view.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Analysis Data",
        data=csv,
        file_name='aadhaar_resilience_data.csv',
        mime='text/csv'
    )

fig_tree = px.treemap(
    df_view, 
    path=['state', 'district'], 
    values='Raw_Ratio', 
    color='SAMARTH_Score', 
    color_continuous_scale='RdYlGn',
    title=""
)
fig_tree.update_layout(**shared_chart_layout, height=450, margin=dict(t=0, l=0, r=0, b=0))
st.plotly_chart(fig_tree, use_container_width=True)

# JUDGE'S NOTE (INCREASED SIZE)
st.markdown("""
<div class='formula-box'>
    <b>Judge's Note: How is the SAMARTH Score Calculated?</b><br>
    Formula: <i>SAMARTH = (0.4 × NEEV) + (0.3 × GATI) + (0.3 × NYAY)</i>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.header("Deep Dive Diagnostics")
tab_neev, tab_gati, tab_nyay = st.tabs([" NEEV (Compliance)", " GATI (Stability)", " NYAY (Equity)"])

# --- TAB 1: NEEV ---
with tab_neev:
    st.markdown("<div class='mnemonic-head'><b>N</b>ational <b>E</b>nrolment & <b>E</b>valuation <b>V</b>ertical (NEEV)</div>", unsafe_allow_html=True)
    st.markdown("**Districts where children (Age 5-17) are failing to update mandatory biometrics.**")
    
    c1, c2 = st.columns([2, 1])
    with c1:
        neev_df = df_view.sort_values('NEEV_Score', ascending=True).head(15)
        fig_neev = px.bar(
            neev_df, 
            x='NEEV_Score', 
            y='district', 
            orientation='h', 
            color='NEEV_Score', 
            color_continuous_scale='Oranges_r',
            title="Bottom 15 Districts (Requires Action)"
        )
        fig_neev.update_layout(**shared_chart_layout, xaxis_title="Compliance Score", yaxis_title="District")
        fig_neev.update_xaxes(title_font=dict(color="#000000"))
        fig_neev.update_yaxes(title_font=dict(color="#000000"))
        st.plotly_chart(fig_neev, use_container_width=True)
        st.markdown("<div class='chart-note'>Higher bars indicate worse performance (Need School Camps).</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div style='background-color:#FFF5E6; border-left:6px solid #FF9933; padding:15px; border-radius:8px; color:#000000; font-weight:700;'>Recommendation: Deploy School Saturation Camps here.</div>", unsafe_allow_html=True)
        st.markdown("<div class='tech-note-box'><b>Technical Formula:</b></div>", unsafe_allow_html=True)
        st.latex(r"NEEV = PercentileRank(\frac{Updates_{5-17}}{Enrolments_{5-17}})")

# --- TAB 2: GATI ---
with tab_gati:
    st.markdown("<div class='mnemonic-head'><b>G</b>overnance <b>A</b>nd <b>T</b>hroughput <b>I</b>ndex (GATI)</div>", unsafe_allow_html=True)
    st.markdown("**Districts experiencing 'Batch Dumps' (High Volatility) vs. Smooth Daily Operations.**")
    
    c1, c2 = st.columns([2, 1])
    with c1:
        fig_gati = px.scatter(
            df_view, 
            x='Load_Volatility_StdDev', 
            y='GATI_Score', 
            color='GATI_Score', 
            color_continuous_scale='RdYlGn', 
            hover_name='district',
            size='Raw_Ratio',
            title="Stability vs Volatility (Top-Left is Best)"
        )
        fig_gati.update_layout(**shared_chart_layout, xaxis_title="Volatility (Std Dev)", yaxis_title="GATI Score")
        fig_gati.update_xaxes(title_font=dict(color="#000000"))
        fig_gati.update_yaxes(title_font=dict(color="#000000"))
        st.plotly_chart(fig_gati, use_container_width=True)
        st.markdown("<div class='chart-note'>Points in Red/Bottom-Right indicate high server stress due to batch dumping.</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div style='background-color:#E8F0FE; border-left:6px solid #063970; padding:15px; border-radius:8px; color:#000000; font-weight:700;'>Recommendation: Implement Daily Sync Protocols.</div>", unsafe_allow_html=True)
        st.markdown("<div class='tech-note-box'><b>Technical Formula:</b></div>", unsafe_allow_html=True)
        st.latex(r"GATI = 100 - (\frac{\sigma_{daily}}{\sigma_{max}} \times 100)")

# --- TAB 3: NYAY ---
with tab_nyay:
    st.markdown("<div class='mnemonic-head'><b>N</b>etwork <b>Y</b>ield & <b>A</b>ccessibility <b>Y</b>ardstick (NYAY)</div>", unsafe_allow_html=True)
    st.markdown("**Districts where services are hoarded in city centers, leaving rural 'Service Deserts'.**")
    
    c1, c2 = st.columns([2, 1])
    with c1:
        fig_nyay = px.histogram(
            df_view, 
            x='NYAY_Score', 
            nbins=30, 
            color_discrete_sequence=['#138808'],
            title="Equity Distribution (Left Skew = High Inequality)"
        )
        fig_nyay.update_layout(**shared_chart_layout, xaxis_title="Equity Score", yaxis_title="Count")
        fig_nyay.update_xaxes(title_font=dict(color="#000000"))
        fig_nyay.update_yaxes(title_font=dict(color="#000000"))
        st.plotly_chart(fig_nyay, use_container_width=True)
        st.markdown("<div class='chart-note'>Left Skew = Many Service Deserts. Right Skew = Good coverage.</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div style='background-color:#E6F4EA; border-left:6px solid #138808; padding:15px; border-radius:8px; color:#000000; font-weight:700;'>Recommendation: Deploy Mobile Aadhaar Vans.</div>", unsafe_allow_html=True)
        st.markdown("<div class='tech-note-box'><b>Technical Formula:</b></div>", unsafe_allow_html=True)
        st.latex(r"NYAY = 100 \times (1 - GiniCoefficient_{pincode})")

st.markdown("<div style='text-align: center; color: #000000; padding-bottom: 80px; font-size:14px; font-weight:800;'>Developed for UIDAI Hackathon | Project SAMARTH</div>", unsafe_allow_html=True)