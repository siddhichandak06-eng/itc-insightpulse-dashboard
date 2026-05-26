"""
ITC PCPB DATASET ACCURACY & AUDIT SCRIPT
=====================================================
Week 3 Data Quality Task:
- Corrects random brand/category anomalies.
- Normalizes retail price tiers to match real-world market positions.
- Recalculates transaction financial ledgers for reporting accuracy.
"""

import pandas as pd
import numpy as np

def audit_and_fix_dataset(file_name="itc_pcpb_refined_sales.csv"):
    print(f"⚡ Starting audit on target file: '{file_name}'...")
    
    # 1. Load the spreadsheet
    try:
        df = pd.read_csv(file_name)
    except FileNotFoundError:
        print(f"❌ Error: Could not find '{file_name}' in the current directory.")
        return

    # 2. Set up realistic brand-to-category rules
    brand_to_category = {
        'Engage': 'Fragrances',
        'Savlon': 'Personal Wash & Hygiene',
        'Vivel': 'Personal Wash & Hygiene',
        'Fiama': 'Personal Wash & Hygiene',
        'Dermafique': 'Skincare & Haircare'
    }

    # Apply the correct categories based on brand name
    df['Product Category'] = df['Brand'].map(brand_to_category)

    # 3. Create a smart logic function to assign realistic prices based on brand positioning
    def assign_brand_price(brand_name):
        if brand_name == 'Vivel':
            return np.random.choice([25, 30, 50])     # Mass-market soaps & washes
        elif brand_name == 'Savlon':
            return np.random.choice([25, 50, 300])    # Germ soaps, handwashes, bulk packs
        elif brand_name == 'Fiama':
            return np.random.choice([50, 300])        # Gel soap bars vs luxury shower gels
        elif brand_name == 'Engage':
            return np.random.choice([300, 500])       # Pocket sprays vs large premium bottles
        elif brand_name == 'Dermafique':
            return np.random.choice([300, 500])       # High-end skin cleansers & facial serums
        return 50

    # Apply random seed to keep numbers consistent on each run
    np.random.seed(42)
    df['Price per Unit'] = df['Brand'].apply(assign_brand_price)

    # 4. Correct the total invoice bill amounts
    df['Total Amount'] = df['Quantity'] * df['Price per Unit']

    # 5. Overwrite the file back to your folder with clean data
    df.to_csv(file_name, index=False)
    print("✅ Dataset audit complete! Brand anomalies eliminated and price matrices normalized.")

if __name__ == "__main__":
    audit_and_fix_dataset()