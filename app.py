import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="UIDAI Resilience Cockpit",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Government" Look
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1, h2, h3 {
        color: #0e3d5e;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA LOADING & PREPROCESSING
# ==========================================
@st.cache_data
def load_data():
    # Load the Final Phase 2 Output
    df = pd.read_csv('aadhaar_hackathon_final_dashboard.csv')
    
    # CALCULATE "RESILIENCE SCORE" (The Final Composite Metric)
    # Formula: 40% Compliance (MBCI) + 30% Stability (100 - ALV) + 30% Equity (SEC)
    # Note: High ALV (Volatility) is bad, so Stability = 100 - ALV
    df['Stability_Score'] = 100 - df['ALV_Score']
    df['Resilience_Score'] = (
        (0.4 * df['MBCI_Score']) + 
        (0.3 * df['Stability_Score']) + 
        (0.3 * df['SEC_Score'])
    )
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ Critical Error: 'aadhaar_hackathon_final_dashboard.csv' not found. Please run Phase 2 first.")
    st.stop()

# ==========================================
# 3. SIDEBAR CONTROLS
# ==========================================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/c/cf/Aadhaar_Logo.svg/1200px-Aadhaar_Logo.svg.png", width=150)
st.sidebar.title("Governance Cockpit")

# State Filter
selected_state = st.sidebar.selectbox(
    "🌍 Select State",
    ["All India"] + sorted(df['state'].unique().tolist())
)

# Simulation Mode Toggle
st.sidebar.markdown("---")
st.sidebar.header("🛠 Intervention Simulator")
simulate_mode = st.sidebar.checkbox("Enable 'What-If' Mode")

mbci_boost = 0
sec_boost = 0

if simulate_mode:
    st.sidebar.info("Simulate policy impacts on the Resilience Score.")
    mbci_boost = st.sidebar.slider("🏫 School Camps (Boost Compliance)", 0, 50, 0, help="Projected impact on MBCI Score")
    sec_boost = st.sidebar.slider("glimpse 🚐 Mobile Vans (Boost Equity)", 0, 50, 0, help="Projected impact on SEC Score")

# Apply Simulation
if simulate_mode:
    # Create a copy to show "Simulated" data
    sim_df = df.copy()
    sim_df['MBCI_Score'] = (sim_df['MBCI_Score'] + mbci_boost).clip(upper=100)
    sim_df['SEC_Score'] = (sim_df['SEC_Score'] + sec_boost).clip(upper=100)
    # Recalculate Resilience
    sim_df['Resilience_Score'] = (
        (0.4 * sim_df['MBCI_Score']) + 
        (0.3 * sim_df['Stability_Score']) + 
        (0.3 * sim_df['SEC_Score'])
    )
    display_df = sim_df
else:
    display_df = df

# Filter Data based on State Selection
if selected_state != "All India":
    filtered_df = display_df[display_df['state'] == selected_state]
else:
    filtered_df = display_df

# ==========================================
# 4. MAIN DASHBOARD
# ==========================================

# Title Section
col1, col2 = st.columns([3, 1])
with col1:
    st.title("Operationalizing Aadhaar: Resilience Framework")
    st.markdown("**Objective:** Shift from 'Descriptive Counting' to 'Prescriptive Resilience'.")
with col2:
    if simulate_mode:
        st.warning("⚠️ SIMULATION MODE ACTIVE")

# KPI Row
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

avg_res = filtered_df['Resilience_Score'].mean()
avg_mbci = filtered_df['MBCI_Score'].mean()
avg_stab = filtered_df['Stability_Score'].mean()
at_risk = len(filtered_df[filtered_df['Resilience_Score'] < 50])

# Determine delta color
delta_res = None
if simulate_mode:
    base_res = df[df['state'] == selected_state]['Resilience_Score'].mean() if selected_state != "All India" else df['Resilience_Score'].mean()
    delta_res = f"{avg_res - base_res:.1f} pts"

with kpi1:
    st.metric("Avg Resilience Score", f"{avg_res:.1f}", delta=delta_res)
with kpi2:
    st.metric("Avg Compliance (MBCI)", f"{avg_mbci:.1f}")
with kpi3:
    st.metric("Avg Stability (100-ALV)", f"{avg_stab:.1f}")
with kpi4:
    st.metric("🚨 At-Risk Districts (<50)", f"{at_risk}")

st.markdown("---")

# ==========================================
# 5. VISUALIZATION ROWS
# ==========================================

# Row 1: The "National View" (Treemap) and "At Risk" Radar
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("🗺️ National Resilience Heatmap")
    st.markdown("Hierarchy: **State > District**. Color: **Resilience Score** (Red=Low, Green=High).")
    
    # Treemap is better than a Map when we don't have a GeoJSON file for Districts
    fig_tree = px.treemap(
        filtered_df,
        path=[px.Constant("India"), 'state', 'district'],
        values='Raw_Ratio', # Size represents volume/importance (proxy)
        color='Resilience_Score',
        color_continuous_scale='RdYlGn',
        hover_data=['MBCI_Score', 'ALV_Score', 'SEC_Score'],
        title="District-Level Resilience Distribution"
    )
    st.plotly_chart(fig_tree, use_container_width=True)

with c2:
    st.subheader("🎯 Priority Intervention Zones")
    # Table of Bottom 10 Districts
    worst_districts = filtered_df.sort_values('Resilience_Score').head(10)
    st.dataframe(
        worst_districts[['district', 'state', 'Resilience_Score']],
        hide_index=True,
        use_container_width=True
    )
    
    st.markdown("### Diagnosis")
    if not worst_districts.empty:
        worst = worst_districts.iloc[0]
        st.error(f"**Critical Alert: {worst['district']}**")
        st.write(f"compliance (MBCI): {worst['MBCI_Score']:.1f}")
        st.write(f"Stability (ALV Inv): {100-worst['ALV_Score']:.1f}")
        st.write(f"Equity (SEC): {worst['SEC_Score']:.1f}")
        
        rec = "None"
        if worst['MBCI_Score'] < 30: rec = "Deploy School Saturation Camps"
        elif worst['SEC_Score'] < 30: rec = "Deploy Mobile Vans to Villages"
        elif worst['ALV_Score'] > 70: rec = "Increase Server Capacity / Temp Staff"
        
        st.markdown(f"**🤖 AI Recommendation:** `{rec}`")

# Row 2: Deep Dive Analytics
st.markdown("---")
st.subheader("📊 Pillar Analysis: Why are districts failing?")

tab1, tab2, tab3 = st.tabs(["Pillar 1: Compliance (MBCI)", "Pillar 2: Stability (ALV)", "Pillar 3: Equity (SEC)"])

with tab1:
    st.markdown("### Mandatory Biometric Compliance Index")
    st.write("Districts where children are NOT updating their biometrics (Potential Service Denial).")
    fig_bar = px.bar(
        filtered_df.sort_values('MBCI_Score').head(20),
        x='district',
        y='MBCI_Score',
        color='MBCI_Score',
        color_continuous_scale='Reds_r',
        title="Bottom 20 Districts by Compliance"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    st.markdown("### Administrative Load Velocity")
    st.write("Districts facing 'Batch Dumps' and high operational stress.")
    fig_scat = px.scatter(
        filtered_df,
        x='Load_Volatility_StdDev',
        y='ALV_Score',
        hover_name='district',
        color='state',
        title="Stress Correlation: Volatility vs ALV Score"
    )
    st.plotly_chart(fig_scat, use_container_width=True)

with tab3:
    st.markdown("### Spatial Equity Coefficient")
    st.write("Districts with unequal service distribution (Service Deserts).")
    fig_hist = px.histogram(
        filtered_df,
        x='SEC_Score',
        nbins=20,
        title="Distribution of Equity Scores (Left Skew = Many Service Deserts)",
        color_discrete_sequence=['#00CC96']
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("Developed for **UIDAI Data Hackathon 2026** | Team Code: *RESILIENCE-01*")