import pandas as pd
import numpy as np
import glob
import re

# ==========================================
# CONFIGURATION
# ==========================================
STATE_MAPPING = {
    'orissa': 'Odisha',
    'pondicherry': 'Puducherry',
    'andaman & nicobar islands': 'Andaman and Nicobar Islands',
    'dadra & nagar haveli': 'Dadra and Nagar Haveli',
    'daman & diu': 'Daman and Diu',
    'jammu & kashmir': 'Jammu and Kashmir',
    'delhi': 'NCT of Delhi',
    'chattisgarh': 'Chhattisgarh',
    'uttaranchal': 'Uttarakhand',
    # Add any other variations found in raw data
}

class AadhaarDataRefinery:
    def __init__(self, dataset_name):
        self.dataset_name = dataset_name
        
    def load_shards(self, file_pattern):
        """Step 6: Raw Shard Consolidation"""
        files = glob.glob(file_pattern)
        print(f"[{self.dataset_name}] Found {len(files)} shards: {files}")
        if not files:
            return pd.DataFrame()
        
        df_list = []
        for f in files:
            # Read as string first to preserve Pincode leading zeros
            temp = pd.read_csv(f, dtype={'pincode': str}) 
            df_list.append(temp)
            
        consolidated_df = pd.concat(df_list, ignore_index=True)
        print(f"[{self.dataset_name}] Raw Consolidated Shape: {consolidated_df.shape}")
        return consolidated_df

    def clean_pipeline(self, df, value_cols):
        """Executes Steps 1, 2, 3, 4, 5, 7"""
        initial_rows = len(df)
        
        # --- Step 1: Garbage Row Removal ---
        # Drop rows where critical metadata is missing
        df = df.dropna(subset=['date', 'state', 'district', 'pincode'])
        
        # --- Step 2: Location Normalization ---
        # Strip whitespace and Lowercase for mapping
        df['state'] = df['state'].str.strip().str.lower()
        df['state'] = df['state'].replace(STATE_MAPPING)
        # Title Case for final presentation
        df['state'] = df['state'].str.title() 
        df['district'] = df['district'].str.strip().str.title()
        
        # Parse Dates (Invalid dates become NaT and are dropped)
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
        df = df.dropna(subset=['date'])
        
        # --- Step 3: Pincode Validation ---
        # Regex: Exactly 6 digits
        valid_pincode_mask = df['pincode'].str.match(r'^\d{6}$')
        invalid_count = (~valid_pincode_mask).sum()
        df = df[valid_pincode_mask]
        if invalid_count > 0:
            print(f"[{self.dataset_name}] ⚠️ Dropped {invalid_count} rows with invalid Pincodes.")
            
        # --- Step 4: Missing Value Treatment ---
        # Fill metric columns with 0
        df[value_cols] = df[value_cols].fillna(0)
        
        # --- Step 5: Deduplication ---
        # Remove exact duplicates
        before_dedup = len(df)
        df = df.drop_duplicates()
        print(f"[{self.dataset_name}] ♻️ Removed {before_dedup - len(df)} duplicate rows.")
        
        # --- Step 7: Feature Validity Guarantee ---
        # Ensure metrics are non-negative
        for col in value_cols:
            df = df[df[col] >= 0]
            
        print(f"[{self.dataset_name}] Final Clean Shape: {df.shape} (Removed {initial_rows - len(df)} bad rows)")
        return df

    def create_master_continuity(self, df, value_cols):
        """
        Creates the 'Resilience Master' (District Level)
        Aggregates Pincodes -> Districts and Imputes Missing Dates (0s)
        """
        # Aggregate to District Level
        df_dist = df.groupby(['date', 'state', 'district'])[value_cols].sum().reset_index()
        
        # Time-Series Imputation (The 'Skeleton' method)
        min_date = df_dist['date'].min()
        max_date = df_dist['date'].max()
        all_dates = pd.date_range(min_date, max_date, freq='D')
        
        unique_districts = df_dist[['state', 'district']].drop_duplicates()
        
        # Cartesian Product (All Dates x All Districts)
        # This guarantees NO gaps in the timeline
        idx = pd.MultiIndex.from_product(
            [all_dates, unique_districts['state'].unique()], 
            names=['date', 'state']
        )
        # Note: This simple product assumes all states have all districts, which is wrong.
        # Correct approach: Iterate unique State-District pairs
        
        skeleton_list = []
        for _, row in unique_districts.iterrows():
            # Create a dataframe for this specific district for all dates
            temp = pd.DataFrame({'date': all_dates})
            temp['state'] = row['state']
            temp['district'] = row['district']
            skeleton_list.append(temp)
            
        skeleton_df = pd.concat(skeleton_list, ignore_index=True)
        
        # Merge Data
        final_df = pd.merge(skeleton_df, df_dist, on=['date', 'state', 'district'], how='left')
        final_df[value_cols] = final_df[value_cols].fillna(0)
        
        return final_df

# ==========================================
# EXECUTION
# ==========================================

# 1. BIOMETRIC
bio_refinery = AadhaarDataRefinery("Biometric")
bio_raw = bio_refinery.load_shards('api_data_aadhar_biometric_*.csv')
bio_cols = ['bio_age_5_17', 'bio_age_17_']
if not bio_raw.empty:
    bio_clean = bio_refinery.clean_pipeline(bio_raw, bio_cols)
    bio_master = bio_refinery.create_master_continuity(bio_clean, bio_cols)
    bio_master.to_csv('cleaned_master_biometric.csv', index=False)

# 2. DEMOGRAPHIC
demo_refinery = AadhaarDataRefinery("Demographic")
demo_raw = demo_refinery.load_shards('api_data_aadhar_demographic_*.csv')
demo_cols = ['demo_age_5_17', 'demo_age_17_']
if not demo_raw.empty:
    demo_clean = demo_refinery.clean_pipeline(demo_raw, demo_cols)
    demo_master = demo_refinery.create_master_continuity(demo_clean, demo_cols)
    demo_master.to_csv('cleaned_master_demographic.csv', index=False)

# 3. ENROLMENT
enrol_refinery = AadhaarDataRefinery("Enrolment")
enrol_raw = enrol_refinery.load_shards('api_data_aadhar_enrolment_*.csv')
enrol_cols = ['age_0_5', 'age_5_17', 'age_18_greater']
if not enrol_raw.empty:
    enrol_clean = enrol_refinery.clean_pipeline(enrol_raw, enrol_cols)
    enrol_master = enrol_refinery.create_master_continuity(enrol_clean, enrol_cols)
    enrol_master.to_csv('cleaned_master_enrolment.csv', index=False)

print("\nProcessing Complete. Master files generated.")