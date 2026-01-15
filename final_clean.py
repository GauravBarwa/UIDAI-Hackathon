import pandas as pd
import difflib
import os

# ==========================================
# 1. THE GOLD STANDARD (The "Law")
# ==========================================
# All data MUST fall into these buckets. No exceptions.
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

# Manual Override Dictionary 
# Maps known bad variations to the Official Name immediately (bypassing fuzzy match risks)
MANUAL_MAP = {
    'Nct Of Delhi': 'Delhi (NCT)',
    'Delhi': 'Delhi (NCT)',
    'New Delhi': 'Delhi (NCT)',
    'Dadra And Nagar Haveli': 'Dadra and Nagar Haveli and Daman & Diu',
    'Daman And Diu': 'Dadra and Nagar Haveli and Daman & Diu',
    'The Dadra And Nagar Haveli And Daman And Diu': 'Dadra and Nagar Haveli and Daman & Diu',
    'Dadra & Nagar Haveli': 'Dadra and Nagar Haveli and Daman & Diu',
    'Jammu And Kashmir': 'Jammu & Kashmir',
    'West Bangal': 'West Bengal',
    'Westbengal': 'West Bengal',
    'West  Bengal': 'West Bengal',
    'Chhatisgarh': 'Chhattisgarh',
    'Tamilnadu': 'Tamil Nadu',
    'Orissa': 'Odisha',
    'Pondicherry': 'Puducherry',
    'Uttaranchal': 'Uttarakhand',
    'Ladhak': 'Ladakh'
}

# ==========================================
# 2. THE CLEANING ENGINES
# ==========================================

def get_clean_state(name):
    """
    Forces a state name to match the Gold Standard.
    """
    if pd.isna(name):
        return "UNKNOWN"
    
    # 1. Syntactic Scrub
    clean = str(name).strip().title()
    
    # 2. Check Manual Map (Fast Path)
    # Check lowercase to be safe
    for bad_key, good_val in MANUAL_MAP.items():
        if bad_key.lower() == clean.lower():
            return good_val
            
    # 3. Check if already perfect
    for target in TARGET_LOCATIONS:
        if target.lower() == clean.lower():
            return target
            
    # 4. Fuzzy Force Match (The "Magnet")
    # Finds the closest official state name. 
    # Cutoff 0.6 allows matching "Telengana" -> "Telangana"
    matches = difflib.get_close_matches(clean, TARGET_LOCATIONS, n=1, cutoff=0.6)
    
    if matches:
        return matches[0] # Return the official spelling
    
    return "UNKNOWN" # Mark for deletion

def clean_districts_in_state(df_state):
    """
    Clusters similar district names WITHIN a state.
    Example: Merges 'Ananthapur', 'Anantapur' -> 'Anantapur'
    """
    # Get all unique district spellings in this state
    districts = df_state['district'].value_counts().index.tolist()
    
    mapping = {}
    processed = set()
    
    for dist in districts:
        if dist in processed:
            continue
            
        # This district is now a "Cluster Leader"
        mapping[dist] = dist
        processed.add(dist)
        
        # Find its "Minions" (misspellings)
        # cutoff=0.85 ensures we don't merge different districts (e.g. Rampur vs Hamirpur)
        matches = difflib.get_close_matches(dist, districts, n=10, cutoff=0.85)
        
        for match in matches:
            if match not in processed:
                mapping[match] = dist # Map misspelling to Leader
                processed.add(match)
                
    return df_state['district'].map(mapping)

def process_dataset(filepath, value_cols):
    print(f"🔄 Processing: {filepath}")
    
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"❌ Error: File {filepath} not found.")
        return None

    initial_rows = len(df)
    
    # --- STEP 1: STATE STANDARDIZATION ---
    print("   ... Normalizing States")
    df['state'] = df['state'].apply(get_clean_state)
    
    # Drop rows that couldn't be matched to ANY state (Garbage)
    df = df[df['state'] != "UNKNOWN"]
    
    # --- STEP 2: DISTRICT CLUSTERING ---
    print("   ... Clustering Districts")
    # We apply this state-by-state to avoid cross-state errors
    cleaned_frames = []
    for state_name in df['state'].unique():
        state_subset = df[df['state'] == state_name].copy()
        state_subset['district'] = clean_districts_in_state(state_subset)
        cleaned_frames.append(state_subset)
        
    df = pd.concat(cleaned_frames)
    
    # --- STEP 3: RE-AGGREGATION (Critical) ---
    # Merging "Westbengal" -> "West Bengal" creates duplicate dates. We must Sum them.
    print("   ... Re-aggregating Data")
    df_final = df.groupby(['date', 'state', 'district'])[value_cols].sum().reset_index()
    
    print(f"✅ Done. Rows: {initial_rows} -> {len(df_final)}")
    return df_final

# ==========================================
# 3. EXECUTION BLOCK
# ==========================================

# Define your input files and their metric columns
tasks = {
    'biometric': ('phase2_ready_biometric.csv', ['bio_age_5_17', 'bio_age_17_']),
    'demographic': ('phase2_ready_demographic.csv', ['demo_age_5_17', 'demo_age_17_']),
    'enrolment': ('phase2_ready_enrolment.csv', ['age_0_5', 'age_5_17', 'age_18_greater'])
}

for name, (file, cols) in tasks.items():
    cleaned_df = process_dataset(file, cols)
    if cleaned_df is not None:
        output_name = f"final_cleaned_{name}.csv"
        cleaned_df.to_csv(output_name, index=False)
        print(f"💾 Saved to: {output_name}\n")

print("🚀 ALL SYSTEMS GO. Your data is now statistically pure.")