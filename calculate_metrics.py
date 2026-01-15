import pandas as pd
import numpy as np
import glob
import difflib

# ==========================================
# 0. CONFIGURATION & CLEANING MODEL (Re-used for Raw Data)
# ==========================================
OFFICIAL_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", 
    "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", 
    "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", 
    "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", 
    "Uttar Pradesh", "Uttarakhand", "West Bengal"
]
OFFICIAL_UTS = [
    "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman & Diu", 
    "Delhi (NCT)", "Jammu & Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
]
TARGET_LOCATIONS = OFFICIAL_STATES + OFFICIAL_UTS

MANUAL_MAP = {
    'Nct Of Delhi': 'Delhi (NCT)', 'Delhi': 'Delhi (NCT)', 'New Delhi': 'Delhi (NCT)',
    'Dadra And Nagar Haveli': 'Dadra and Nagar Haveli and Daman & Diu',
    'Daman And Diu': 'Dadra and Nagar Haveli and Daman & Diu',
    'Dadra & Nagar Haveli': 'Dadra and Nagar Haveli and Daman & Diu',
    'The Dadra And Nagar Haveli And Daman And Diu': 'Dadra and Nagar Haveli and Daman & Diu',
    'Jammu And Kashmir': 'Jammu & Kashmir', 'West Bangal': 'West Bengal',
    'Westbengal': 'West Bengal', 'West  Bengal': 'West Bengal',
    'Chhatisgarh': 'Chhattisgarh', 'Tamilnadu': 'Tamil Nadu',
    'Orissa': 'Odisha', 'Pondicherry': 'Puducherry',
    'Uttaranchal': 'Uttarakhand', 'Ladhak': 'Ladakh'
}

def get_clean_state(name):
    if pd.isna(name): return "UNKNOWN"
    clean = str(name).strip().title()
    for bad, good in MANUAL_MAP.items():
        if bad.lower() == clean.lower(): return good
    for target in TARGET_LOCATIONS:
        if target.lower() == clean.lower(): return target
    matches = difflib.get_close_matches(clean, TARGET_LOCATIONS, n=1, cutoff=0.6)
    return matches[0] if matches else "UNKNOWN"

def clean_districts_in_state(df_state):
    districts = df_state['district'].value_counts().index.tolist()
    mapping = {}
    processed = set()
    for dist in districts:
        if dist in processed: continue
        mapping[dist] = dist
        processed.add(dist)
        matches = difflib.get_close_matches(dist, districts, n=10, cutoff=0.85)
        for match in matches:
            if match not in processed:
                mapping[match] = dist
                processed.add(match)
    return df_state['district'].map(mapping)

# ==========================================
# PART 1: MBCI & ALV (The Realistic Approach)
# ==========================================

def calculate_mbci_alv_realistic():
    print("🚀 PHASE 2 (REALISTIC) START...")
    
    # Load the Gold Standard Files
    try:
        bio = pd.read_csv('final_cleaned_biometric.csv')
        enrol = pd.read_csv('final_cleaned_enrolment.csv')
    except FileNotFoundError:
        print("❌ CRITICAL: 'final_cleaned' files not found.")
        return pd.DataFrame()

    # --- 1. MBCI (Relative Compliance) ---
    print("   ... Calculating MBCI (Percentile Ranking)")
    bio_total = bio.groupby(['state', 'district'])['bio_age_5_17'].sum().reset_index()
    enrol_total = enrol.groupby(['state', 'district'])['age_5_17'].sum().reset_index()
    
    # Merge & Calculate Raw Ratio
    mbci_df = pd.merge(bio_total, enrol_total, on=['state', 'district'], suffixes=('_upd', '_base'))
    mbci_df['Raw_Ratio'] = mbci_df['bio_age_5_17'] / (mbci_df['age_5_17'] + 1)
    
    # THE GENUINE FIX: Percentile Ranking
    # Instead of capping at 100, we rank them. Top performer = 100, Median = 50.
    mbci_df['MBCI_Score'] = mbci_df['Raw_Ratio'].rank(pct=True) * 100
    
    # --- 2. ALV (Load Volatility) ---
    print("   ... Calculating ALV (Volatility / Batch-Dump Detection)")
    # We use Standard Deviation of Daily Volume.
    # High StdDev = Massive spikes (Stress). Low StdDev = Smooth (Resilient).
    daily_volatility = bio.groupby(['state', 'district'])['bio_age_5_17'].std().reset_index()
    daily_volatility.rename(columns={'bio_age_5_17': 'Load_Volatility_StdDev'}, inplace=True)
    
    # Fill NaNs (for districts with 1 day of data) with 0
    daily_volatility['Load_Volatility_StdDev'] = daily_volatility['Load_Volatility_StdDev'].fillna(0)
    
    # Normalize ALV (Min-Max Scaling)
    max_vol = daily_volatility['Load_Volatility_StdDev'].max()
    daily_volatility['ALV_Score'] = (daily_volatility['Load_Volatility_StdDev'] / max_vol) * 100
    
    # Combine Pillars 1 & 2
    core_metrics = pd.merge(mbci_df, daily_volatility, on=['state', 'district'], how='left')
    return core_metrics

# ==========================================
# PART 2: SEC (Mining Raw Data)
# ==========================================

def calculate_sec_realistic():
    print("\n⛏️  PHASE 2 MINING: Extracting Pincodes for SEC...")
    
    raw_files = glob.glob('api_data_aadhar_biometric_*.csv')
    if not raw_files:
        print("⚠️  WARNING: No raw files found.")
        return pd.DataFrame()
        
    df_list = []
    for f in raw_files:
        df_list.append(pd.read_csv(f))
    raw_df = pd.concat(df_list, ignore_index=True)
    
    # Apply Cleaning Force Model
    raw_df['state'] = raw_df['state'].apply(get_clean_state)
    raw_df = raw_df[raw_df['state'] != "UNKNOWN"]
    
    cleaned_frames = []
    for state in raw_df['state'].unique():
        sub = raw_df[raw_df['state'] == state].copy()
        sub['district'] = clean_districts_in_state(sub)
        cleaned_frames.append(sub)
    raw_clean = pd.concat(cleaned_frames)
    
    # Gini Calculation
    def gini(x):
        total = 0
        for i, xi in enumerate(x[:-1], 1):
            total += np.sum(np.abs(xi - x[i:]))
        return total / (len(x)**2 * np.mean(x)) if np.mean(x) > 0 else 0

    raw_clean['pincode'] = pd.to_numeric(raw_clean['pincode'], errors='coerce')
    raw_clean = raw_clean.dropna(subset=['pincode'])
    
    pincode_dist = raw_clean.groupby(['state', 'district', 'pincode'])['bio_age_5_17'].sum().reset_index()
    
    sec_results = []
    for (state, district), group in pincode_dist.groupby(['state', 'district']):
        volumes = group['bio_age_5_17'].values
        if len(volumes) > 1 and np.sum(volumes) > 0:
            g = gini(volumes)
            sec_score = 100 * (1 - g) 
        else:
            sec_score = 0
        sec_results.append({'state': state, 'district': district, 'SEC_Score': sec_score})
        
    return pd.DataFrame(sec_results)

# ==========================================
# PART 3: MAIN EXECUTION
# ==========================================

master_df = calculate_mbci_alv_realistic()
sec_df = calculate_sec_realistic()

if not master_df.empty:
    print("\n🔗 Merging & Generating Final Report...")
    if not sec_df.empty:
        final_dashboard = pd.merge(master_df, sec_df[['state', 'district', 'SEC_Score']], 
                                   on=['state', 'district'], how='left')
        final_dashboard['SEC_Score'] = final_dashboard['SEC_Score'].fillna(0)
    else:
        final_dashboard = master_df
        final_dashboard['SEC_Score'] = 0

    # Final Polish
    final_cols = ['state', 'district', 'MBCI_Score', 'ALV_Score', 'SEC_Score', 'Raw_Ratio', 'Load_Volatility_StdDev']
    final_dashboard = final_dashboard[final_cols]
    
    output_file = 'aadhaar_hackathon_final_dashboard.csv'
    final_dashboard.to_csv(output_file, index=False)
    
    print(f"\n✅ COMPLETE. Real-world insights generated in: {output_file}")
    print(final_dashboard.head(10))
else:
    print("❌ Process Failed.")