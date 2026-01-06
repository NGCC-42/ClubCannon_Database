import pandas as pd
import streamlit as st
import plotly.express as px
from PIL import Image
import numpy as np
#from collections import ChainMap, defaultdict
#import difflib
import altair as alt
import matplotlib.pyplot as plt
#from operator import itemgetter
from datetime import datetime, timedelta
import openpyxl
import streamlit_shadcn_ui as ui
#from streamlit_extras.metric_cards import style_metric_cards
from streamlit_option_menu import option_menu
from data.load import load_all_data



from logic.analytics import (
    num_to_month, 
    month_to_num,    
    to_date_revenue,
    percent_of_change,
    get_monthly_sales_v2,
    calc_monthly_totals_v2,
    magic_sales_data
)


from ui.components import (
    style_metric_cards
)


# --------------------------------------------------
# FUNCTIONS AND VARIABLES FOR REAL TIME CALCULATIONS
# --------------------------------------------------

def beginning_of_year(dt: datetime) -> datetime:
    return datetime(dt.year, 1, 1)

def calc_time_context():
    
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)
    two_years_ago = today - timedelta(days=730)
    three_years_ago = today - timedelta(days=1095)
    four_years_ago = today - timedelta(days=1460)

    return today, one_year_ago, two_years_ago, three_years_ago, four_years_ago

# -----------------
# CREATE DATE LISTS
# -----------------

today, one_year_ago, two_years_ago, three_years_ago, four_years_ago = calc_time_context()

months = ['All', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
months_x = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
years = ['2022', '2023', '2024', '2025', '2026']

# ---------------------
# BOM COST DICTIONARIES
# ---------------------

bom_cost_jet = {'Pro Jet': 290.86, 'Quad Jet': 641.43, 'Micro Jet': 243.57, 'Cryo Clamp': 166.05}
bom_cost_control = {'The Button': 141.07, 'Shostarter': 339.42, 'Shomaster': 667.12}
bom_cost_hh = {'8FT - No Case': 143.62, '8FT - Travel Case': 219.06, '15FT - No Case': 153.84, '15FT - Travel Case': 231.01}
bom_cost_hose = {'2FT MFD': 20.08, '3.5FT MFD': 22.50, '5FT MFD': 24.25, '5FT STD': 31.94, '5FT DSY': 31.84, '5FT EXT': 33.24, '8FT STD': 32.42, '8FT DSY': 34.52, '8FT EXT': 34.82, '15FT STD': 43.55, '15FT DSY': 46.47, '15FT EXT': 46.77, '25FT STD': 59.22, '25FT DSY': 61.87, '25FT EXT': 62.17, '35FT STD': 79.22, '35FT DSY': 81.32, '35FT EXT': 81.62, '50FT STD': 103.57, '50FT EXT': 105.97, '100FT STD': 183.39}
bom_cost_acc = {'CC-AC-CCL': 29.17, 'CC-AC-CTS': 6.70, 'CC-F-DCHA': 7.15, 'CC-F-HEA': 6.86, 'CC-AC-RAA': 11.94, 'CC-AC-4PM': 48.12, 'CC-F-MFDCGAJIC': 7.83, ' CC-AC-CGAJIC-SET': 5.16, 'CC-AC-CGAJIC-SET': 5.16, 'CC-AC-CGAJIC-SET - 1': 5.16, 'CC-CTC-20': 10.92, 'CC-CTC-50': 19.36, 'CC-AC-TC': 89.46, 'CC-VV-KIT': 29.28, 
                'CC-RC-2430': 847, 'CC-AC-LA2': 248.10, 'CC-SW-05': 157.24, 'CC-NPTC-06-STD': 10.99, 'CC-NPTC-10-DSY': 18.90, 'CC-NPTC-15-DSY': 27.08, 'CC-NPTC-25-DSY': 39.37}
bom_cost_mfx = {'MagicFX Commander': 355.73, 'Magic FX Smoke Bubble Blaster': 3328.63, 'MagicFX ARM SFX SAFETY TERMINATOR': 12.50, 'MagicFX Device Updater': 38.37, 'MagicFX PSYCO2JET': 1158.63, 'MagicFX Red Button': 61.23, 'MagicFX Replacement Keys': 7.27, 
                'MagicFX SFX Safety ARM Controller': 616.13, 'MagicFX SPARXTAR': 1623.63, 'MagicFX Sparxtar powder': 19.84, 'MagicFX StadiumBlaster': 2893.56, 'MagicFX StadiumBlower': 2858.90, 'MagicFX StadiumShot III': 2321.13, 'MagicFX SuperBlaster II': 1468.63, 
                'MagicFX Swirl Fan II': 1406.63, 'MagicFX Switchpack II': 448.73, 'MFX-AC-SBRV': 328.68, 'MFX-E2J-230': 3282.40, 'MFX-E2J-2LFA': 97, 'MFX-E2J-5LFCB': 128, 'MFX-E2J-F-ID': 30.45, 'MFX-E2J-F-OD': 37.92, 'MFX-E2J-FC': 673.48, 'MFX-E2J-FEH-1M': 46, 'MFX-E2J-FEH-2M': 69, 
                'MFX-E2J-OB': 46, 'MFX-ECO2JET-BKT': 193, 'MFX-SS3-RB': 136.13}



# --------------------
# MAKE DATA ACCESSIBLE
# --------------------

df, df_quotes, df_cogs, df_shipstat_23, df_shipstat_24, df_qb, df_hsd, df_hist, unique_customer_list, master_customer_list, wholesale_list = load_all_data()

rev_by_year = to_date_revenue(df)

#td_26 = [rev_by_year[2026][0], rev_by_year[2026][1]]
td_25 = [rev_by_year[2025][0], rev_by_year[2025][1]]
td_24 = [rev_by_year[2024][0], rev_by_year[2024][1]]
td_23 = [rev_by_year[2023][0], rev_by_year[2023][1]]
td_22 = [rev_by_year[2022][0], rev_by_year[2022][1]]

#td_26_tot = td_26[0] + td_26[1]
td_25_tot = td_25[0] + td_25[1]
td_24_tot = td_24[0] + td_24[1]
td_23_tot = td_23[0] + td_23[1]
td_22_tot = td_22[0] + td_22[1]

sales_dict_23 = get_monthly_sales_v2(df, 2023)
total_23, web_23, ful_23, avg_23, magic23 = calc_monthly_totals_v2(sales_dict_23)

sales_dict_24 = get_monthly_sales_v2(df, 2024)
total_24, web_24, ful_24, avg_24, magic24 = calc_monthly_totals_v2(sales_dict_24)

sales_dict_25 = get_monthly_sales_v2(df, 2025)
total_25, web_25, ful_25, avg_25, magic25 = calc_monthly_totals_v2(sales_dict_25)

#sales_dict_26 = get_monthly_sales_v2(df, 2026)
#total_26, web_26, ful_26, avg_26, magic26 = calc_monthly_totals_v2(sales_dict_26)


# ----------------------------------------
# EXTRA PRODUCT SALES DATA FROM DATAFRAMES
# ----------------------------------------

# ---------
# HANDHELDS
# ---------

@st.cache_data
def extract_handheld_data(df):

    dict_23 = {}
    dict_24 = {}
    dict_25 = {}
    dict_26 = {}
    hose_count_23 = {}
    hose_count_24 = {}
    hose_count_25 = {}
    hose_count_26 = {}
    
    # CREATE DATA DICTS 
    for month in months_x:
        dict_23[month] = {'8FT - No Case': [0,0],
                     '8FT - Travel Case': [0,0],
                     '15FT - No Case': [0,0],
                     '15FT - Travel Case': [0,0]}
        dict_24[month] = {'8FT - No Case': [0,0],
                     '8FT - Travel Case': [0,0],
                     '15FT - No Case': [0,0],
                     '15FT - Travel Case': [0,0]}
        dict_25[month] = {'8FT - No Case': [0,0],
                     '8FT - Travel Case': [0,0],
                     '15FT - No Case': [0,0],
                     '15FT - Travel Case': [0,0]}
        dict_26[month] = {'8FT - No Case': [0,0],
                     '8FT - Travel Case': [0,0],
                     '15FT - No Case': [0,0],
                     '15FT - Travel Case': [0,0]}
        
        hose_count_23[month] = [0,0]
        hose_count_24[month] = [0,0]
        hose_count_25[month] = [0,0]
        hose_count_26[month] = [0,0]
    
    idx = 0
    for line in df.item_sku:

        if df.iloc[idx].order_date.year == 2026:
            if line[:16] == 'CC-HCCMKII-08-NC':
                dict_26[num_to_month(df.iloc[idx].order_date.month)]['8FT - No Case'][0] += df.iloc[idx].quantity
                hose_count_26[num_to_month(df.iloc[idx].order_date.month)][0] += df.iloc[idx].quantity
                dict_26[num_to_month(df.iloc[idx].order_date.month)]['8FT - No Case'][1] += df.iloc[idx].total_line_item_spend
            elif line[:16] == 'CC-HCCMKII-08-TC':
                dict_26[num_to_month(df.iloc[idx].order_date.month)]['8FT - Travel Case'][0] += df.iloc[idx].quantity
                hose_count_26[num_to_month(df.iloc[idx].order_date.month)][0] += df.iloc[idx].quantity
                dict_26[num_to_month(df.iloc[idx].order_date.month)]['8FT - Travel Case'][1] += df.iloc[idx].total_line_item_spend
            elif line[:16] == 'CC-HCCMKII-15-NC':
                dict_26[num_to_month(df.iloc[idx].order_date.month)]['15FT - No Case'][0] += df.iloc[idx].quantity
                hose_count_26[num_to_month(df.iloc[idx].order_date.month)][1] += df.iloc[idx].quantity
                dict_26[num_to_month(df.iloc[idx].order_date.month)]['15FT - No Case'][1] += df.iloc[idx].total_line_item_spend
            elif line[:16] == 'CC-HCCMKII-15-TC':
                dict_26[num_to_month(df.iloc[idx].order_date.month)]['15FT - Travel Case'][0] += df.iloc[idx].quantity
                hose_count_26[num_to_month(df.iloc[idx].order_date.month)][1] += df.iloc[idx].quantity
                dict_26[num_to_month(df.iloc[idx].order_date.month)]['15FT - Travel Case'][1] += df.iloc[idx].total_line_item_spend

        if df.iloc[idx].order_date.year == 2025:
            if line[:16] == 'CC-HCCMKII-08-NC':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['8FT - No Case'][0] += df.iloc[idx].quantity
                hose_count_25[num_to_month(df.iloc[idx].order_date.month)][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['8FT - No Case'][1] += df.iloc[idx].total_line_item_spend
            elif line[:16] == 'CC-HCCMKII-08-TC':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['8FT - Travel Case'][0] += df.iloc[idx].quantity
                hose_count_25[num_to_month(df.iloc[idx].order_date.month)][0] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['8FT - Travel Case'][1] += df.iloc[idx].total_line_item_spend
            elif line[:16] == 'CC-HCCMKII-15-NC':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['15FT - No Case'][0] += df.iloc[idx].quantity
                hose_count_25[num_to_month(df.iloc[idx].order_date.month)][1] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['15FT - No Case'][1] += df.iloc[idx].total_line_item_spend
            elif line[:16] == 'CC-HCCMKII-15-TC':
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['15FT - Travel Case'][0] += df.iloc[idx].quantity
                hose_count_25[num_to_month(df.iloc[idx].order_date.month)][1] += df.iloc[idx].quantity
                dict_25[num_to_month(df.iloc[idx].order_date.month)]['15FT - Travel Case'][1] += df.iloc[idx].total_line_item_spend
                
        if df.iloc[idx].order_date.year == 2024:
            if line[:16] == 'CC-HCCMKII-08-NC':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['8FT - No Case'][0] += df.iloc[idx].quantity
                hose_count_24[num_to_month(df.iloc[idx].order_date.month)][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['8FT - No Case'][1] += df.iloc[idx].total_line_item_spend
            elif line[:16] == 'CC-HCCMKII-08-TC':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['8FT - Travel Case'][0] += df.iloc[idx].quantity
                hose_count_24[num_to_month(df.iloc[idx].order_date.month)][0] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['8FT - Travel Case'][1] += df.iloc[idx].total_line_item_spend
            elif line[:16] == 'CC-HCCMKII-15-NC':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['15FT - No Case'][0] += df.iloc[idx].quantity
                hose_count_24[num_to_month(df.iloc[idx].order_date.month)][1] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['15FT - No Case'][1] += df.iloc[idx].total_line_item_spend
            elif line[:16] == 'CC-HCCMKII-15-TC':
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['15FT - Travel Case'][0] += df.iloc[idx].quantity
                hose_count_24[num_to_month(df.iloc[idx].order_date.month)][1] += df.iloc[idx].quantity
                dict_24[num_to_month(df.iloc[idx].order_date.month)]['15FT - Travel Case'][1] += df.iloc[idx].total_line_item_spend
                
        elif df.iloc[idx].order_date.year == 2023:
            if line[:16] == 'CC-HCCMKII-08-NC':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['8FT - No Case'][0] += df.iloc[idx].quantity
                hose_count_23[num_to_month(df.iloc[idx].order_date.month)][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['8FT - No Case'][1] += df.iloc[idx].total_line_item_spend
            elif line[:16] == 'CC-HCCMKII-08-TC':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['8FT - Travel Case'][0] += df.iloc[idx].quantity
                hose_count_23[num_to_month(df.iloc[idx].order_date.month)][0] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['8FT - Travel Case'][1] += df.iloc[idx].total_line_item_spend
            elif line[:16] == 'CC-HCCMKII-15-NC':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['15FT - No Case'][0] += df.iloc[idx].quantity
                hose_count_23[num_to_month(df.iloc[idx].order_date.month)][1] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['15FT - No Case'][1] += df.iloc[idx].total_line_item_spend
            elif line[:16] == 'CC-HCCMKII-15-TC':
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['15FT - Travel Case'][0] += df.iloc[idx].quantity
                hose_count_23[num_to_month(df.iloc[idx].order_date.month)][1] += df.iloc[idx].quantity
                dict_23[num_to_month(df.iloc[idx].order_date.month)]['15FT - Travel Case'][1] += df.iloc[idx].total_line_item_spend
                
        idx += 1
    
    return dict_23, dict_24, dict_25, dict_26, hose_count_23, hose_count_24, hose_count_25, hose_count_26
    

# -----
# HOSES
# -----

@st.cache_data
def extract_hose_data(df):

    # DEFINE TARGET YEARS
    target_years = [2023, 2024, 2025, 2026]

    # DEFINE TARGET PRODUCTS    
    products = ['2FT MFD', '3.5FT MFD', '5FT MFD', '5FT STD', '5FT DSY', '5FT EXT', '8FT STD', '8FT DSY', '8FT EXT', '15FT STD', '15FT DSY', '15FT EXT', '25FT STD', '25FT DSY', '25FT EXT', '35FT STD', '35FT DSY', '35FT EXT', '50FT STD', '50FT EXT', '100FT STD', 'CUSTOM']

    # DEFINE TARGET PRODUCT SKUS
    conditions = [
        df['item_sku'].str.startswith('CC-CH-02', na=False),
        df['item_sku'].str.startswith('CC-CH-03', na=False),
        df['item_sku'].str.startswith('CC-CH-05-M', na=False),
        df['item_sku'].str.startswith('CC-CH-05-S', na=False),
        df['item_sku'].str.startswith('CC-CH-05-D', na=False),
        df['item_sku'].str.startswith('CC-CH-05-E', na=False),
        df['item_sku'].str.startswith('CC-CH-08-S', na=False),
        df['item_sku'].str.startswith('CC-CH-08-D', na=False),
        df['item_sku'].str.startswith('CC-CH-08-E', na=False),
        df['item_sku'].str.startswith('CC-CH-15-S', na=False),
        df['item_sku'].str.startswith('CC-CH-15-D', na=False),
        df['item_sku'].str.startswith('CC-CH-15-E', na=False),
        df['item_sku'].str.startswith('CC-CH-25-S', na=False),
        df['item_sku'].str.startswith('CC-CH-25-D', na=False),
        df['item_sku'].str.startswith('CC-CH-25-E', na=False),
        df['item_sku'].str.startswith('CC-CH-35-S', na=False),
        df['item_sku'].str.startswith('CC-CH-35-D', na=False),
        df['item_sku'].str.startswith('CC-CH-35-E', na=False),
        df['item_sku'].str.startswith('CC-CH-50-S', na=False),
        df['item_sku'].str.startswith('CC-CH-50-E', na=False),
        df['item_sku'].str.startswith('CC-CH-100-S', na=False),
        df['item_sku'].str.startswith('CC-CH-XX', na=False),
    ]

    # GENERATE A NEW COLUMN 'PRODUCT' BASED ON CONDITIONS IN A COPY OF THE DATAFRAME
    df = df.copy()
    df['product'] = np.select(conditions, products, default=None)

    # REMOVE ROWS THAT DON'T MEET CONDITIONS
    df = df[df['product'].notnull()]

    # ENSURE ORDER_DATE IS DATETIME, CREATE YEAR AND MONTH COLUMNS
    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    df['year'] = df['order_date'].dt.year
    df['month'] = df['order_date'].dt.month.apply(lambda m: months_x[m - 1])

    # CREATE A WHOLESALE FLAG COLUMN
    df['wholesale'] = df['customer'].isin(wholesale_list)

    # GROUP BY YEAR, MONTH, AND PRODUCT FOR OVERALL TOTALS
    overall = df.groupby(['year', 'month', 'product']).agg(qty_sum=('quantity', 'sum'), 
                                                           spend_sum=('total_line_item_spend', 'sum')
                                                          ).reset_index()

    # GROUP BY YEAR, MONTH AND PRODUCT FOR WHOLESALE RESULTS
    #ws_group = df[df['wholesale']].groupby(['year', 'month', 'product'])['quantity'].sum().reset_index()
    #ws_group = ws_group.rename(columns={'quantity': 'wholesale_qty'})

    # MERGE OVERALL AND WHOLESALE RESULTS
    #merged = pd.merge(overall, ws_group, on=['year', 'month', 'product'], how='left')
    #merged['wholesale_qty'] = merged['wholesale_qty'].fillna(0)

    # BUILD A RESULT DICT FOR EACH TARGET YEAR
    result = {}

    for year in target_years:
        # PREFILL WITH DEFAULT VALUES FOR EACH MONTH AND PRODUCT
        year_dict = {month: {'2FT MFD': [0,0], '3.5FT MFD': [0,0], '5FT MFD': [0,0], '5FT STD': [0,0], '5FT DSY': [0,0], 
                            '5FT EXT': [0,0], '8FT STD': [0,0], '8FT DSY': [0,0], '8FT EXT': [0,0], '15FT STD': [0,0], 
                            '15FT DSY': [0,0], '15FT EXT': [0,0], '25FT STD': [0,0], '25FT DSY': [0,0], '25FT EXT': [0,0], 
                            '35FT STD': [0,0], '35FT DSY': [0,0], '35FT EXT': [0,0], '50FT STD': [0,0], '50FT EXT': [0,0],
                            '100FT STD': [0,0], 'CUSTOM': [0,0]}
                    for month in months_x}
        
        sub = overall[overall['year'] == year]
        for _, row in sub.iterrows():
            month = row['month']
            product = row['product']
            year_dict[month][product] = [row['qty_sum'], row['spend_sum']]
        result[year] = year_dict

    return result.get(2023), result.get(2024), result.get(2025), result.get(2026)


# -----------
# ACCESSORIES
# -----------

@st.cache_data
def extract_acc_data(df):
    # Define month names.
    months_x = ["January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"]
    target_years = [2023, 2024, 2025, 2026]
    
    # Define the products that are handled uniformly (their keys and the expected substring lengths).
    # For these, the default accumulator is a list: [quantity, total_line_item_spend]
    simple_products = {
        'CC-AC-CCL': 9,
        'CC-AC-CTS': 9,
        'CC-F-DCHA': 9,
        'CC-F-HEA': 8,
        'CC-AC-RAA': 9,
        'CC-AC-4PM': 9,
        'CC-F-MFDCGAJIC': 14,
        ' CC-AC-CGAJIC-SET': 17,  # note the leading space if that is intentional
        'CC-AC-CGAJIC-SET - 1': 20,
        'CC-CTC-20': 9,
        'CC-CTC-50': 9,
        'CC-AC-TC': 8,
        'CC-VV-KIT': 9,
        'CC-AC-LA2': 9,
        'CC-SW-05': 8,
        'CC-NPTC-06-STD': 14,
        'CC-NPTC-10-DSY': 14,
        'CC-NPTC-15-DSY': 14,
        'CC-NPTC-25-DSY': 14
    }
    # For "CC-RC-2430", we need a 5-element list:
    rc_key = 'CC-RC-2430'
    # For rc, the base case will update indices 0 (qty) and 1 (spend). 
    # Then there are special cases for:
    #   - 'CC-RC-2430-PJI'  -> index 2 (quantity)
    #   - 'CC-RC-2430-LAI'  -> index 3 (quantity)
    #   - 'CC-RC-2430-QJF'  -> index 4 (quantity)
    
    # Preinitialize dictionaries for each target year.
    results = {yr: {month: {} for month in months_x} for yr in target_years}
    for yr in target_years:
        for m in months_x:
            # Fill in simple product keys with [0,0]
            for prod in simple_products.keys():
                results[yr][m][prod] = [0, 0]
            # Initialize the special product "CC-RC-2430" with a 5-element list.
            results[yr][m][rc_key] = [0, 0, 0, 0, 0]
    
    # Ensure order_date is datetime and create year and month columns.
    df = df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["year"] = df["order_date"].dt.year
    df["month"] = df["order_date"].dt.month.apply(lambda m: months_x[m - 1])
    
    # Process each target year separately.
    for yr in target_years:
        df_year = df[df["year"] == yr]
        
        # Process simple products.
        for prod, sig_len in simple_products.items():
            # Create a boolean mask: rows where the line_item starts with prod (using sig_len)
            mask = df_year["item_sku"].str[:sig_len] == prod
            if mask.sum() == 0:
                continue
            # Group by month
            grp = df_year.loc[mask].groupby("month").agg({
                "quantity": "sum",
                "total_line_item_spend": "sum"
            })
            for month, row in grp.iterrows():
                results[yr][month][prod][0] = row["quantity"]
                results[yr][month][prod][1] = row["total_line_item_spend"]
        
        # Process the special product "CC-RC-2430".
        df_rc = df_year[df_year["item_sku"].str.startswith("CC-RC", na=False)]
        if not df_rc.empty:
            # Base mask for rows related to "CC-RC-2430" (we assume they start with that string)
            base_mask = df_rc["item_sku"] == rc_key
            grp_base = df_rc.loc[base_mask].groupby("month").agg({
                "quantity": "sum",
                "total_line_item_spend": "sum"
            })
            for month, row in grp_base.iterrows():
                # For the base case, update indices 0 and 1.
                results[yr][month][rc_key][0] = row["quantity"]
                results[yr][month][rc_key][1] = row["total_line_item_spend"]
            
            # Now handle special cases:
            # PJI, LAI, QJF - these are based on line_item starting with these exact strings.
            for suffix, idx_to_update in [('CC-RC-2430-PJI', 2),
                                          ('CC-RC-2430-LAI', 3),
                                          ('CC-RC-2430-QJF', 4)]:
                mask_special = df_rc["item_sku"].str.startswith(suffix, na=False)
                grp_special = df_rc.loc[mask_special].groupby("month")["quantity"].sum()
                for month, qty in grp_special.items():
                    results[yr][month][rc_key][idx_to_update] = qty

    # Combine CGAJIC set sku totals 
    for yr in target_years:
        for month in months_x:
            results[yr][month][' CC-AC-CGAJIC-SET'][0] += results[yr][month]['CC-AC-CGAJIC-SET - 1'][0]
            results[yr][month][' CC-AC-CGAJIC-SET'][1] += results[yr][month]['CC-AC-CGAJIC-SET - 1'][1]
            
            # Remove revision of CGAJIC set
            del results[yr][month]['CC-AC-CGAJIC-SET - 1']
                    
    # Return dictionaries for each year: 2023, 2024, 2025, 2026.
    return results[2023], results[2024], results[2025], results[2026]


# -----------
# CONTROLLERS
# -----------

@st.cache_data
def extract_control_data(df):

    
    # Define product mapping using the prefixes in line_item.
    conditions = [
        df["item_sku"].str.startswith("CC-TB-3", na=False),
        df["item_sku"].str.startswith("CC-SS-3", na=False),
        df["item_sku"].str.startswith("CC-SM", na=False),
    ]
    choices = ["The Button", "Shostarter", "Shomaster"]
    
    # Create a new column "product" based on the above conditions.
    df = df.copy()
    df["product"] = np.select(conditions, choices, default=None)
    # Remove rows that are not one of our desired product types.
    df = df[df["product"].notnull()]
    
    # Ensure order_date is datetime and add year and month columns.
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["year"] = df["order_date"].dt.year
    df["month"] = df["order_date"].dt.month.apply(lambda m: months_x[m - 1])
    
    # Create a wholesale flag column.
    df["wholesale"] = df["customer"].isin(wholesale_list)
    
    # Group by year, month, and product for overall totals.
    overall = df.groupby(["year", "month", "product"]).agg(
        qty_sum=("quantity", "sum"),
        spend_sum=("total_line_item_spend", "sum")
    ).reset_index()
    
    # Group by year, month, and product for wholesale only quantities.
    wholesale_grp = df[df["wholesale"]].groupby(["year", "month", "product"])["quantity"].sum().reset_index()
    wholesale_grp = wholesale_grp.rename(columns={"quantity": "wholesale_qty"})
    
    # Merge the overall and wholesale results.
    merged = pd.merge(overall, wholesale_grp, on=["year", "month", "product"], how="left")
    merged["wholesale_qty"] = merged["wholesale_qty"].fillna(0)
    
    # Build a result dictionary for each target year.
    result = {}
    # Target years: 2023, 2024, 2025 and 2026.
    for y in [2023, 2024, 2025, 2026]:
        # Pre-fill with default values for every month and each product.
        year_dict = {month: {"The Button": [0, 0, 0], "Shostarter": [0, 0, 0],
                             "Shomaster": [0, 0, 0]}
                     for month in months_x}
        sub = merged[merged["year"] == y]
        for _, row in sub.iterrows():
            month = row["month"]
            product = row["product"]
            # Update the values: [total_quantity, total_spend, wholesale_quantity]
            year_dict[month][product] = [row["qty_sum"], row["spend_sum"], row["wholesale_qty"]]
        result[y] = year_dict
    
    # Return dictionaries for the target years.
    return result.get(2023), result.get(2024), result.get(2025), result.get(2026)


# ---------------
# STATIONARY JETS
# ---------------

@st.cache_data
def extract_jet_data(df):
    # Define month names if not already defined
    months_x = ["January", "February", "March", "April", "May", "June", 
                "July", "August", "September", "October", "November", "December"]
    
    # Define product mapping using the prefixes in line_item.
    conditions = [
        df["item_sku"].str.startswith("CC-PRO", na=False),
        df["item_sku"].str.startswith("CC-QJ", na=False),
        df["item_sku"].str.startswith("CC-MJM", na=False),
        df["item_sku"].str.startswith("CC-CC2", na=False)
    ]
    choices = ["Pro Jet", "Quad Jet", "Micro Jet", "Cryo Clamp"]
    
    # Create a new column "product" based on the above conditions.
    df = df.copy()
    df["product"] = np.select(conditions, choices, default=None)
    # Remove rows that are not one of our desired product types.
    df = df[df["product"].notnull()]
    
    # Ensure order_date is datetime and add year and month columns.
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["year"] = df["order_date"].dt.year
    df["month"] = df["order_date"].dt.month.apply(lambda m: months_x[m - 1])
    
    # Create a wholesale flag column.
    df["wholesale"] = df["customer"].isin(wholesale_list)
    
    # Group by year, month, and product for overall totals.
    overall = df.groupby(["year", "month", "product"]).agg(
        qty_sum=("quantity", "sum"),
        spend_sum=("total_line_item_spend", "sum")
    ).reset_index()
    
    # Group by year, month, and product for wholesale only quantities.
    wholesale_grp = df[df["wholesale"]].groupby(["year", "month", "product"])["quantity"].sum().reset_index()
    wholesale_grp = wholesale_grp.rename(columns={"quantity": "wholesale_qty"})
    
    # Merge the overall and wholesale results.
    merged = pd.merge(overall, wholesale_grp, on=["year", "month", "product"], how="left")
    merged["wholesale_qty"] = merged["wholesale_qty"].fillna(0)
    
    # Build a result dictionary for each target year.
    result = {}
    # Target years: 2023, 2024, 2025 and 2026.
    for y in [2023, 2024, 2025, 2026]:
        # Pre-fill with default values for every month and each product.
        year_dict = {month: {"Pro Jet": [0, 0, 0], "Quad Jet": [0, 0, 0],
                             "Micro Jet": [0, 0, 0], "Cryo Clamp": [0, 0, 0]}
                     for month in months_x}
        sub = merged[merged["year"] == y]
        for _, row in sub.iterrows():
            month = row["month"]
            product = row["product"]
            # Update the values: [total_quantity, total_spend, wholesale_quantity]
            year_dict[month][product] = [row["qty_sum"], row["spend_sum"], row["wholesale_qty"]]
        result[y] = year_dict
    
    # Return dictionaries for the target years.
    return result.get(2023), result.get(2024), result.get(2025), result.get(2026)
    

# ----------------------------------------------------------------------------
# COLLECT AND ORGANIZE PRODUCT SALES DATA - ACCOUNT FOR HOSES IN HANDHELD KITS
# ----------------------------------------------------------------------------

@st.cache_data
def collect_product_data(df, prod='All', years=[2023, 2024, 2025, 2026]):


    jet23, jet24, jet25, jet26 = extract_jet_data(df)
    control23, control24, control25, control26 = extract_control_data(df)
    handheld23, handheld24, handheld25, handheld26, hh_hose_count_23, hh_hose_count_24, hh_hose_count_25, hh_hose_count_26 = extract_handheld_data(df)
    hose23, hose24, hose25, hose26 = extract_hose_data(df)
    acc23, acc24, acc25, acc26 = extract_acc_data(df)

    # INCLUDE HANDHELD HOSES IN COUNTS
    for key, val in hose23.items():
        hose23[key]['8FT STD'][0] += hh_hose_count_23[key][0]
        hose23[key]['15FT STD'][0] += hh_hose_count_23[key][1]
    for key, val in hose24.items():
        hose24[key]['8FT STD'][0] += hh_hose_count_24[key][0]
        hose24[key]['15FT STD'][0] += hh_hose_count_24[key][1] 
    for key, val in hose25.items():
        hose25[key]['8FT STD'][0] += hh_hose_count_25[key][0]
        hose25[key]['15FT STD'][0] += hh_hose_count_25[key][1] 
    for key, val in hose26.items():
        hose26[key]['8FT STD'][0] += hh_hose_count_26[key][0]
        hose26[key]['15FT STD'][0] += hh_hose_count_26[key][1] 

    return jet23, jet24, jet25, jet26, control23, control24, control25, control26, handheld23, handheld24, handheld25, handheld26, hose23, hose24, hose25, hose26, acc23, acc24, acc25, acc26


@st.cache_data
def organize_hose_data(dict):
    
    count_mfd = {'2FT MFD': [0, 0], '3.5FT MFD': [0, 0], '5FT MFD': [0, 0]}
    count_5ft = {'5FT STD': [0, 0], '5FT DSY': [0, 0], '5FT EXT': [0, 0]}
    count_8ft = {'8FT STD': [0, 0], '8FT DSY': [0, 0], '8FT EXT': [0, 0]}
    count_15ft = {'15FT STD': [0, 0], '15FT DSY': [0, 0], '15FT EXT': [0, 0]}
    count_25ft = {'25FT STD': [0, 0], '25FT DSY': [0, 0], '25FT EXT': [0, 0]}
    count_35ft = {'35FT STD': [0, 0], '35FT DSY': [0, 0], '35FT EXT': [0, 0]}
    count_50ft = {'50FT STD': [0, 0], '50FT EXT': [0, 0]}
    count_100ft = [0, 0]
    
    for month, prod in dict.items():
        for hose, val in prod.items():

            if 'MFD' in hose:
                count_mfd[hose][0] += val[0]
                count_mfd[hose][1] += val[1]
            elif hose == '5FT STD' or hose == '5FT DSY' or hose == '5FT EXT':
                count_5ft[hose][0] += val[0]
                count_5ft[hose][1] += val[1]
            elif '8FT' in hose:
                count_8ft[hose][0] += val[0]
                count_8ft[hose][1] += val[1]            
            elif '15FT' in hose:
                count_15ft[hose][0] += val[0]
                count_15ft[hose][1] += val[1]   
            elif '25FT' in hose:
                count_25ft[hose][0] += val[0]
                count_25ft[hose][1] += val[1]   
            elif '35FT' in hose:
                count_35ft[hose][0] += val[0]
                count_35ft[hose][1] += val[1]   
            elif '50FT' in hose:
                count_50ft[hose][0] += val[0]
                count_50ft[hose][1] += val[1]  
            elif '100FT' in hose:
                count_100ft[0] += val[0]
                count_100ft[1] += val[1]
    
    return [count_mfd, count_5ft, count_8ft, count_15ft, count_25ft, count_35ft, count_50ft, count_100ft]


@st.cache_data
def magic_sales(year):

    # Filter for rows that match the given year.
    #mask_year = df["ordered_year"] == year
    
    # Force conversion of order_date to datetime
    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    
    # Debugging: Check if conversion worked
    #print(df[['order_date']].head())  # Should display datetime values
    #print(df['order_date'].dtype)  # Should be 'datetime64[ns]'
    
    # Now, extract the year safely
    mask_year = df['order_date'].dt.year == int(year)

    # Build a mask for rows where either 'line_item' or 'item_sku' starts with "Magic" or "MFX"
    mask_magic = (
        #df["line_item"].str.startswith("Magic", na=False) |
        #df["line_item"].str.startswith("MFX", na=False) |
        df["item_sku"].str.startswith("Magic", na=False) |
        df["item_sku"].str.startswith("MFX", na=False)
    )
    
    # Combined mask: only consider rows from the given year that mention Magic/MFX
    mask = mask_year & mask_magic

    # Sum total_line_item_spend for these rows
    total_spend = df.loc[mask, "total_line_item_spend"].sum()
    
    # Create (or copy) the magic_products dictionary
    magic_products = {
        'MagicFX Commander': [0, 0],
        'Magic FX Smoke Bubble Blaster': [0, 0],
        'MagicFX ARM SFX SAFETY TERMINATOR': [0, 0],
        'MagicFX Device Updater': [0, 0],
        'MagicFX PSYCO2JET': [0, 0],
        'MagicFX Red Button': [0, 0],
        'MagicFX Replacement Keys': [0, 0],
        'MagicFX SFX Safety ARM Controller': [0, 0],
        'MagicFX SPARXTAR': [0, 0],
        'MagicFX Sparxtar powder': [0, 0],
        'MagicFX StadiumBlaster': [0, 0],
        'MagicFX StadiumBlower': [0, 0],
        'MagicFX StadiumShot III': [0, 0],
        'MagicFX SuperBlaster II': [0, 0],
        'MagicFX Swirl Fan II': [0, 0],
        'MagicFX Switchpack II': [0, 0],
        'MFX-AC-SBRV': [0, 0],
        'MFX-E2J-230': [0, 0],
        'MFX-E2J-2LFA': [0, 0],
        'MFX-E2J-5LFCB': [0, 0],
        'MFX-E2J-F-ID': [0, 0],
        'MFX-E2J-F-OD': [0, 0],
        'MFX-E2J-FC': [0, 0],
        'MFX-E2J-FEH-1M': [0, 0],
        'MFX-E2J-FEH-2M': [0, 0],
        'MFX-E2J-OB': [0, 0],
        'MFX-ECO2JET-BKT': [0, 0],
        'MFX-E2J-BKT': [0, 0],
        'MFX-SS3-RB': [0, 0]
    }

    #for prod in magic_products:
        #mask_prod = mask_year & df["line_item"].str.lower().str.startswith(prod.lower(), na=False)
        #st.write(f"Checking {prod}: {mask_prod.sum()} rows matched")
    
    # For each magic product, create a mask (using the line_item column) and aggregate quantity and sales.
    for prod in magic_products:
        # Check if the beginning of line_item matches the product name.
        mask_prod = mask & (df["item_sku"] == prod)
        qty_sum   = df.loc[mask_prod, "quantity"].sum()
        spend_sum = df.loc[mask_prod, "total_line_item_spend"].sum()
        magic_products[prod] = [qty_sum, spend_sum]
        
    magic_products['MFX-E2J-BKT'][0] = magic_products['MFX-ECO2JET-BKT'][0] + magic_products['MFX-E2J-BKT'][0]
    magic_products['MFX-E2J-BKT'][1] = magic_products['MFX-ECO2JET-BKT'][1] + magic_products['MFX-E2J-BKT'][1]
    
    return total_spend, magic_products


# -----------------------------------
# PROCESS AND ORGANIZE EXTRACTED DATA
# -----------------------------------


def product_annual_totals(prod_dict_list):
    """
    prod_dict_list: list of dicts for the SAME year.
    Each dict: {month: {sku: [values...]}, ...}

    Returns a single nested dict:
      {category: {product: values}}
    """

    # --- SKU NORMALIZATION MAP ---
    normalize_map = {
        "CC-AC-CGAJIC-SET": "CC-AC-CGAJIC-SET",
        "CC-AC-CGAJIC-SET-1": "CC-AC-CGAJIC-SET",
        "CC-AC-CGAJIC-SET - 1": "CC-AC-CGAJIC-SET",
        " CC-AC-CGAJIC-SET-1": "CC-AC-CGAJIC-SET",

    }

    jet_list = ['Pro Jet', 'Quad Jet', 'Micro Jet', 'Cryo Clamp']
    control_list = ['The Button', 'Shostarter', 'Shomaster']
    handheld_list = ['8FT - No Case', '8FT - Travel Case', '15FT - No Case', '15FT - Travel Case']
    hose_list = [
        '2FT MFD', '3.5FT MFD', '5FT MFD', '5FT STD', '5FT DSY', '5FT EXT',
        '8FT STD', '8FT DSY', '8FT EXT',
        '15FT STD', '15FT DSY', '15FT EXT',
        '25FT STD', '25FT DSY', '25FT EXT',
        '35FT STD', '35FT DSY', '35FT EXT',
        '50FT STD', '50FT EXT',
        '100FT STD', 'CUSTOM'
    ]
    acc_list = [
        'CC-AC-CCL', 'CC-AC-CTS', 'CC-F-DCHA', 'CC-F-HEA', 'CC-AC-RAA',
        'CC-AC-4PM', 'CC-F-MFDCGAJIC', 'CC-AC-CGAJIC-SET',
        'CC-AC-CGAJIC-SET - 1', 'CC-CTC-20', 'CC-CTC-50', 'CC-AC-TC',
        'CC-VV-KIT', 'CC-RC-2430', 'CC-AC-LA2', 'CC-SW-05',
        'CC-NPTC-06-STD', 'CC-NPTC-10-DSY', 'CC-NPTC-15-DSY', 'CC-NPTC-25-DSY'
    ]

    categories = ['jet', 'control', 'handheld', 'hose', 'acc']

    year_totals = {cat: {} for cat in categories}
    

    # --- PROCESS ALL DATASETS ---
    for year_data in prod_dict_list:
        for month, products in year_data.items():
            for raw_sku, vals in products.items():

                # -------- NORMALIZE SKU --------
                sku = raw_sku.strip()
                sku = normalize_map.get(sku, sku)  # rewrite if in the map

                # -------- CATEGORY --------
                if sku in jet_list:
                    cat = 'jet'
                elif sku in control_list:
                    cat = 'control'
                elif sku in hose_list:
                    cat = 'hose'
                elif sku in acc_list:
                    cat = 'acc'
                elif sku in handheld_list:
                    cat = 'handheld'

                # -------- VALUE VECTOR SIZE --------
                if sku == 'CC-RC-2430':
                    size = 5
                elif cat in ('jet', 'control'):
                    size = 3
                else:
                    size = 2

                # -------- INIT BUCKET --------
                if sku not in year_totals[cat]:
                    year_totals[cat][sku] = [0] * size

                # -------- ACCUMULATE --------
                for i in range(min(len(vals), size)):
                    year_totals[cat][sku][i] += vals[i]

    return year_totals


# ------------------------
# PREP DATA FOR PROCESSING
# ------------------------

jet23, jet24, jet25, jet26, control23, control24, control25, control26, handheld23, handheld24, handheld25, handheld26, hose23, hose24, hose25, hose26, acc23, acc24, acc25, acc26 = collect_product_data(df)

hose_detail26 = organize_hose_data(hose26)
hose_detail25 = organize_hose_data(hose25)
hose_detail24 = organize_hose_data(hose24)
hose_detail23 = organize_hose_data(hose23)


@st.cache_data
def annual_product_totals():

    prodTot26 = product_annual_totals([jet26, control26, handheld26, hose26, acc26])
    prodTot25 = product_annual_totals([jet25, control25, handheld25, hose25, acc25])
    prodTot24 = product_annual_totals([jet24, control24, handheld24, hose24, acc24])
    prodTot23 = product_annual_totals([jet23, control23, handheld23, hose23, acc23])

    return prodTot23, prodTot24, prodTot25, prodTot26


prodTot23, prodTot24, prodTot25, prodTot26 = annual_product_totals()



# ------------------------------------------
# PRODUCT METRICS - PROFIT AND AVERAGE PRICE
# ------------------------------------------

def calc_prod_metrics(prod_dict, product, bom_dict, prod_dict_prior=None):

    jet_list = ['Pro Jet', 'Quad Jet', 'Micro Jet', 'Cryo Clamp']
    control_list = ['The Button', 'Shostarter', 'Shomaster']

    prod_profit = (prod_dict[product][1]) - (prod_dict[product][0] * bom_dict[product])
    
    if prod_dict[product][0] == 0:
        profit_per_unit = 0
        avg_price = 0
    else:
        profit_per_unit = prod_profit / prod_dict[product][0]
        avg_price = prod_dict[product][1] / prod_dict[product][0]

    if prod_dict_prior != None:
        if prod_dict_prior[product][0] == 0:
            avg_price_last = 0
            prod_profit_last = 0
        else:
            avg_price_last = prod_dict_prior[product][1] / prod_dict_prior[product][0]
            prod_profit_last = (prod_dict_prior[product][1]) - (prod_dict_prior[product][0] * bom_dict[product])

    if product in jet_list or product in control_list:
        wholesale_sales = prod_dict[product][2]
        if prod_dict[product][0] == 0:
            wholesale_percentage = 0
        else:
            wholesale_percentage = (prod_dict[product][2] / prod_dict[product][0]) * 100

        if prod_dict_prior != None:
            wholesale_delta = wholesale_percentage - ((prod_dict_prior[product][2] / prod_dict_prior[product][0]) * 100)
            return prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last, wholesale_sales, wholesale_percentage, wholesale_delta
        else:
            return prod_profit, profit_per_unit, avg_price, wholesale_sales, wholesale_percentage

    elif prod_dict_prior == None:
        return prod_profit, profit_per_unit, avg_price

    else:
        return prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last




# ----------------------------------------------
# GENEREATE REALTIME ANNUAL COMPARISON FUNCTIONS
# ----------------------------------------------
    
def to_date_product(sku_string):
    # Filter rows where the line_item starts with sku_string.
    mask_sku = df["item_sku"].str.startswith(sku_string)
    df_sku = df[mask_sku].copy()
    
    # Ensure order_date is a datetime and create a date-only column.
    df_sku["order_date"] = pd.to_datetime(df_sku["order_date"], errors="coerce")
    df_sku["order_date_date"] = df_sku["order_date"].dt.date
    
    # Convert our reference datetime values to dates.
    three_years_ago_date = three_years_ago.date()
    two_years_ago_date = two_years_ago.date()
    one_year_ago_date   = one_year_ago.date()
    today_date          = today.date()

    begin_three = beginning_of_year(three_years_ago).date()
    begin_two = beginning_of_year(two_years_ago).date()
    begin_one = beginning_of_year(one_year_ago).date()
    begin_today = beginning_of_year(today).date()
    
    # Build boolean masks for the different time ranges.
    mask_23 = (df_sku["order_date_date"] >= begin_three) & (df_sku["order_date_date"] <= three_years_ago_date)
    mask_24 = (df_sku["order_date_date"] >= begin_two) & (df_sku["order_date_date"] <= two_years_ago_date)
    mask_25 = (df_sku["order_date_date"] >= begin_one) & (df_sku["order_date_date"] <= one_year_ago_date)
    
    # Sum the quantities for each date range.
    #prod_cnt_22 = df_sku.loc[mask_22, "quantity"].sum()
    prod_cnt_23 = df_sku.loc[mask_23, "quantity"].sum()
    prod_cnt_24 = df_sku.loc[mask_24, "quantity"].sum()
    prod_cnt_25 = df_sku.loc[mask_25, "quantity"].sum()
    
    # (Return only the counts you need. In your example, you returned prod_cnt_23 and prod_cnt_24.)
    return prod_cnt_23, prod_cnt_24, prod_cnt_25


def to_date_product_rev(sku_string):

    # Filter rows where the item_sku starts with sku_sting
    mask_sku = df['item_sku'].str.startswith(sku_string)
    df_sku = df[mask_sku].copy()

    # Ensure order_date is a datetime and create a date-only column
    df_sku['order_date'] = pd.to_datetime(df_sku['order_date'], errors='coerce')
    df_sku['order_date_date'] = df_sku['order_date'].dt.date

    # Convert reference datetime values to dates
    three_years_ago_date = three_years_ago.date()
    two_years_ago_date = two_years_ago.date()
    one_year_ago_date = one_year_ago.date()
    today_datet = today.date()

    begin_three = beginning_of_year(three_years_ago).date()
    begin_two = beginning_of_year(two_years_ago).date()
    begin_one = beginning_of_year(one_year_ago).date()
    begin_today = beginning_of_year(today).date()

    # Build boolean masks for the different time ranges
    mask_23 = (df_sku['order_date_date'] >= begin_three) & (df_sku['order_date_date'] <= three_years_ago_date)
    mask_24 = (df_sku['order_date_date'] >= begin_two) & (df_sku['order_date_date'] <= two_years_ago_date)
    mask_25 = (df_sku['order_date_date'] >= begin_one) & (df_sku['order_date_date'] <= one_year_ago_date)

    # Sum the sales totals for each date range
    prod_rev23 = df_sku.loc[mask_23, 'total_line_item_spend'].sum()
    prod_rev24 = df_sku.loc[mask_24, 'total_line_item_spend'].sum()
    prod_rev25 = df_sku.loc[mask_25, 'total_line_item_spend'].sum()
    

    return prod_rev23, prod_rev24, prod_rev25


# ---------------------------------
# CALCULATE PRODUCT PROFIT FUNCTION
# ---------------------------------

@st.cache_data
def profit_by_type(year_list, product_type_list):

    # Calculate total profit for the selected years and product types.


    # Start with zero total profit and add to this as we go.
    total_profit = 0  

    # Map each product type string to the corresponding BOM cost dictionary.
    # These dicts must exist in the outer scope just like in your original code.
    type_to_bom_cost = {
        "Jet": bom_cost_jet,
        "Control": bom_cost_control,
        "Handheld": bom_cost_hh,
        "Hose": bom_cost_hose,
        "Accessory": bom_cost_acc,
    }

    # Map each product type to corresponding key
    type_to_key = {
        "Jet": 'jet', 
        "Control": 'control',
        "Handheld": 'handheld',
        "Hose": 'hose',
        "Accessory": 'acc',
    }


    # Loop over each product type the caller is interested in (e.g. "Jet", "Hose").
    for product_type in product_type_list:

        # Use match/case as a "switch" on product_type.
        match product_type:

            # Handle all the known product types.
            case "Jet" | "Control" | "Handheld" | "Hose" | "Accessory":
                # Get the BOM cost dictionary for this product type.
                bom_cost_dict = type_to_bom_cost[product_type]
                key = type_to_key[product_type]

                # Loop over each requested year as a string, e.g. "2023", "2024", "2025".
                for year_str in year_list:
                    try:
                        # Convert the year string to an integer so we can do math with it.
                        year = int(year_str)
                    except ValueError:
                        # If it isn't a valid integer year (e.g. "All"), skip it.
                        continue

                    # Get the per-SKU totals for this product type and year.
                    # This should be a dict like: {sku: [quantity, revenue], ...}
                    #product_totals_for_year = annual_product_totals[index]
                    if year == 2026:
                        product_totals_for_year = prodTot26[key]
                    elif year == 2025:
                        product_totals_for_year = prodTot25[key]
                    elif year == 2024:
                        product_totals_for_year = prodTot24[key]
                    elif year == 2023:
                        product_totals_for_year = prodTot23[key]
                    

                    # Loop through each SKU and its associated data tuple.
                    for sku, data in product_totals_for_year.items():

                        # For hoses, if the SKU is "CUSTOM", skip it (same as your original code).
                        if product_type == "Hose" and sku == "CUSTOM":
                            continue

                        # Now handle the different tuple shapes:
                        #   Jet/Control/Handheld: (qty, revenue, wholesale_qty)
                        #   Hose/Accessory:       (qty, revenue)
                        if product_type in ("Jet", "Control"):
                            # Unpack three values: quantity, revenue, and wholesale quantity.
                            qty, revenue, wholesale_qty = data
                            # (wholesale_qty is available here if you need it later)
                        elif product_type == "Accessory" and sku.startswith('CC-RC-2430'):
                            qty, revenue, pji, led, qji = data
                        else:
                            # For Hose and Accessory, we only expect quantity and revenue.
                            qty, revenue = data

                        # Look up the unit cost from the correct BOM dict.
                        # If the SKU somehow isn't in the BOM dict, default to cost 0.
                        unit_cost = bom_cost_dict.get(sku, 0)

                        # Add this SKU's profit to the running total:
                        # profit = revenue - (quantity * unit_cost).
                        total_profit += revenue - (qty * unit_cost)

            # Default case: if we see an unknown product type, do nothing and continue.
            case _:
                # You could log or print a warning here if you want.
                continue

    # After processing all requested product types and years, return the final total profit.
    return total_profit




# CALCULATE MAGIC FX SALES DATA
mfx_rev, mfx_costs, mfx_profit = magic_sales_data()


# CALCULATE PRODUCT PROFIT

profit_26 = profit_by_type(['2026'], ['Jet', 'Control', 'Handheld', 'Hose', 'Accessory'])
profit_25 = profit_by_type(['2025'], ['Jet', 'Control', 'Handheld', 'Hose', 'Accessory'])
profit_24 = profit_by_type(['2024'], ['Jet', 'Control', 'Handheld', 'Hose', 'Accessory']) + mfx_profit
profit_23 = profit_by_type(['2023'], ['Jet', 'Control', 'Handheld', 'Hose', 'Accessory'])


# -------------------------------------------
# REALTIME ANNUAL PRODUCT COMPARISON - PROFIT
# -------------------------------------------

def to_date_product_profit(to_date_total, to_date_rev, product_bom_cost):

    td_profit = to_date_rev - (to_date_total * product_bom_cost)
    
    return td_profit


# INITIALIZE PRODUCT COUNT VARIABLES
pj_td24 = 0
mj_td24 = 0
qj_td24 = 0
cc_td24 = 0
tb_td24 = 0
ss_td24 = 0
sm_td24 = 0
td_8nc24 = 0
td_8tc24 = 0
td_15nc24 = 0
td_15tc24 = 0



def convert_prod_select(prod_select, year):

    # Map product selection to SKU
    sku_map = {
        'Pro Jet': 'CC-PROJ',
        'Micro Jet': 'CC-MJMK',
        'Quad Jet': 'CC-QJ',
        'Cryo Clamp': 'CC-CC2',
        'The Button': 'CC-TB-35',
        'Shostarter': 'CC-SS-35',
        'Shomaster': 'CC-SM',
        '8FT - No Case': 'CC-HCCMKII-08-NC',
        '8FT - Travel Case': 'CC-HCCMKII-08-TC', 
        '15FT - No Case': 'CC-HCCMKII-15-NC',
        '15FT - Travel Case': 'CC-HCCMKII-15-TC'
    }
    if prod_select in sku_map:
        rev23, rev24, rev25 = to_date_product_rev(sku_map[prod_select])

        return rev25 if year == 2026 else rev24 if year == 2025 else rev23 if year == 2024 else None

    return None

def convert_prod_select_profit(prod_select):

    var_map = {
        'Pro Jet': pj_td24,
        'Micro Jet': mj_td24, 
        'Quad Jet': qj_td24,
        'Cryo Clamp': cc_td24, 
        'The Button': tb_td24,
        'Shostarter': ss_td24,
        'Shomaster': sm_td24,
        '8FT - No Case': td_8nc24, 
        '8FT - Travel Case': td_8tc24,
        '15FT - No Case': td_15nc24,
        '15FT - Travel Case': td_15tc24   
    }
    if prod_select in var_map:
        return var_map[prod_select]


# -----------------------------------
# HISTORICAL PRODUCT DATA / 2013-2022
# -----------------------------------

@st.cache_data
def hist_product_data(product_tag):

    # Make a copy so we don't mutate the original
    df_loc = df_hist.copy()

    # Ensure order_date is datetime
    df_loc["order_date"] = pd.to_datetime(df_loc["order_date"], errors="coerce")

    # Drop rows with invalid/missing dates
    df_loc = df_loc.dropna(subset=["order_date"])


    cust_dict = {}
    for cust in master_customer_list:
        cust_dict[cust] = 0
        
    annual_dict = {'2022': 0, '2021': 0, '2020': 0, '2019': 0, '2018': 0, '2017': 0, '2016': 0, '2015': 0, '2014': 0, '2013': 0}

    idx = 0
    for line in product_tag:

        if df_loc.iloc[idx].order_date.year in [2023, 2024, 2025, 1970]:
            pass
        else:
            year = str(df_loc.iloc[idx].order_date.year)
            if year == '2104':
                year = '2014'
            else:
                try:
                    annual_dict[year] += int(line)
                    if line > 0:
                        cust_dict[df_loc.iloc[idx].customer] += int(line)
                except:
                    pass
                    
        if idx <= len(df_loc): 
            idx += 1

    return cust_dict, annual_dict


def hist_annual_prod_totals(prod_annual_dict, prod_list, year_list):

    for year in year_list:
        for prod in prod_list:
            prod_annual_dict[year] += prod[year]

    prod_annual_dict = dict(reversed(list(prod_annual_dict.items())))
    
    return prod_annual_dict

def prep_data_context():

    rev_by_year = to_date_revenue(df)

    td_26 = [rev_by_year[2026][0], rev_by_year[2026][1]]
    td_25 = [rev_by_year[2025][0], rev_by_year[2025][1]]
    td_24 = [rev_by_year[2024][0], rev_by_year[2024][1]]
    td_23 = [rev_by_year[2023][0], rev_by_year[2023][1]]
    td_22 = [rev_by_year[2022][0], rev_by_year[2022][1]]
    
    td_26_tot = td_26[0] + td_26[1]
    td_25_tot = td_25[0] + td_25[1]
    td_24_tot = td_24[0] + td_24[1]
    td_23_tot = td_23[0] + td_23[1]
    td_22_tot = td_22[0] + td_22[1]
    
    sales_dict_23 = get_monthly_sales_v2(df, 2023)
    total_23, web_23, ful_23, avg_23, magic23 = calc_monthly_totals_v2(sales_dict_23)
    
    sales_dict_24 = get_monthly_sales_v2(df, 2024)
    total_24, web_24, ful_24, avg_24, magic24 = calc_monthly_totals_v2(sales_dict_24)
    
    sales_dict_25 = get_monthly_sales_v2(df, 2025)
    total_25, web_25, ful_25, avg_25, magic25 = calc_monthly_totals_v2(sales_dict_25)
    
    sales_dict_26 = get_monthly_sales_v2(df, 2026)
    total_26, web_26, ful_26, avg_26, magic26 = calc_monthly_totals_v2(sales_dict_26)
    
    
    # ------------------------
    # PREP DATA FOR PROCESSING
    # ------------------------
    
    jet23, jet24, jet25, jet26, control23, control24, control25, control26, handheld23, handheld24, handheld25, handheld26, hose23, hose24, hose25, hose26, acc23, acc24, acc25, acc26 = collect_product_data(df)
    
    hose_detail26 = organize_hose_data(hose26)
    hose_detail25 = organize_hose_data(hose25)
    hose_detail24 = organize_hose_data(hose24)
    hose_detail23 = organize_hose_data(hose23)
    
    prodTot23, prodTot24, prodTot25, prodTot26 = annual_product_totals()
    
    # CALCULATE MAGIC FX SALES DATA
    mfx_rev, mfx_costs, mfx_profit = magic_sales_data()
    
    
    # CALCULATE PRODUCT PROFIT
    
    profit_26 = profit_by_type(['2026'], ['Jet', 'Control', 'Handheld', 'Hose', 'Accessory'])
    profit_25 = profit_by_type(['2025'], ['Jet', 'Control', 'Handheld', 'Hose', 'Accessory'])
    profit_24 = profit_by_type(['2024'], ['Jet', 'Control', 'Handheld', 'Hose', 'Accessory']) + mfx_profit
    profit_23 = profit_by_type(['2023'], ['Jet', 'Control', 'Handheld', 'Hose', 'Accessory'])


    
    # HISTORICAL HANDHELDS
    hhmk1_cust, hhmk1_annual = hist_product_data(df_hist.hh_mk1)
    hhmk2_cust, hhmk2_annual = hist_product_data(df_hist.hh_mk2)
    
    # HISTORICAL ACCESSORIES
    tc_cust, tc_annual = hist_product_data(df_hist.travel_case)
    tcog_cust, tcog_annual = hist_product_data(df_hist.travel_case_og)
    bp_cust, bp_annual = hist_product_data(df_hist.backpack)
    mfd_cust, mfd_annual = hist_product_data(df_hist.manifold)
    ctc_20_cust, ctc_20_annual = hist_product_data(df_hist.ctc_20)
    ctc_50_cust, ctc_50_annual = hist_product_data(df_hist.ctc_50)
    ledmk1_cust, ledmk1_annual = hist_product_data(df_hist.led_attachment_mk1)
    ledmk2_cust, ledmk2_annual = hist_product_data(df_hist.led_attachment_mk2)
    pwrpack_cust, pwrpack_annual = hist_product_data(df_hist.power_pack)
    
    # HISTORICAL JETS
    jet_og_cust, jet_og_annual = hist_product_data(df_hist.jets_og)
    pj_cust, pj_annual = hist_product_data(df_hist.pro_jet)
    pwj_cust, pwj_annual = hist_product_data(df_hist.power_jet)
    mjmk1_cust, mjmk1_annual = hist_product_data(df_hist.micro_jet_mk1)
    mjmk2_cust, mjmk2_annual = hist_product_data(df_hist.micro_jet_mk2)
    ccmk1_cust, ccmk1_annual = hist_product_data(df_hist.cryo_clamp_mk1)
    ccmk2_cust, ccmk2_annual = hist_product_data(df_hist.cryo_clamp_mk2)
    qj_cust, qj_annual = hist_product_data(df_hist.quad_jet)
    
    # HISTORICAL CONTROLLERS
    dmx_cntl_cust, dmx_cntl_annual = hist_product_data(df_hist.dmx_controller)
    lcd_cntl_cust, lcd_cntl_annual = hist_product_data(df_hist.lcd_controller)
    tbmk1_cust, tbmk1_annual = hist_product_data(df_hist.the_button_mk1)
    tbmk2_cust, tbmk2_annual = hist_product_data(df_hist.the_button_mk2)
    sm_cust, sm_annual = hist_product_data(df_hist.shomaster)
    ss_cust, ss_annual = hist_product_data(df_hist.shostarter)
    pwr_cntl_cust, pwr_cntl_annual = hist_product_data(df_hist.power_controller)
    
    # HISTORICAL CONFETTI
    blwr_cust, blwr_annual = hist_product_data(df_hist.confetti_blower)

    return {
        "td_26": td_26, "td_25": td_25, "td_24": td_24, "td_23": td_23, "td_22": td_22, 
        "td_26_tot": td_26_tot, "td_25_tot": td_25_tot, "td_24_tot": td_24_tot, "td_23_tot": td_23_tot, "td_22_tot": td_22_tot,
        "sales_dict_26": sales_dict_26, "sales_dict_25": sales_dict_25, "sales_dict_24": sales_dict_24, "sales_dict_23": sales_dict_23,
        "total_25": total_25, "web_25": web_25, "ful_25": ful_25, "avg_25": avg_25, "magic25": magic25,
        "total_24": total_24, "web_24": web_24, "ful_24": ful_24, "avg_24": avg_24, "magic24": magic24,
        "total_23": total_23, "web_23": web_23, "ful_23": ful_23, "avg_23": avg_23, "magic23": magic23,
        "jet26": jet26, "control26": control26, "handheld26": handheld26, "hose26": hose26, "acc26": acc26,
        "jet25": jet25, "control25": control25, "handheld25": handheld25, "hose25": hose25, "acc25": acc25,
        "jet24": jet24, "control24": control24, "handheld24": handheld24, "hose24": hose24, "acc24": acc24,
        "jet23": jet23, "control23": control23, "handheld23": handheld23, "hose23": hose23, "acc23": acc23,
        "hose_detail26": hose_detail26, "hose_detail25": hose_detail25, "hose_detail24": hose_detail24, "hose_detail23": hose_detail23,
        "prodTot26": prodTot26, "prodTot25": prodTot25, "prodTot24": prodTot24, "prodTot23": prodTot23,
        "mfx_rev": mfx_rev, "mfx_costs": mfx_costs, "mfx_profit": mfx_profit, "profit_25": profit_25, "profit_24": profit_24,
        "profit_23": profit_23, 
        "hhmk1_cust": hhmk1_cust, "hhmk1_annual": hhmk1_annual, "hhmk2_cust": hhmk2_cust, "hhmk2_annual": hhmk2_annual, "tc_cust": tc_cust, 
        "tc_annual": tc_annual, "tcog_cust": tcog_cust, "tcog_annual": tcog_annual, "bp_cust": bp_cust, "bp_annual": bp_annual, "mfd_cust": mfd_cust, 
        "mfd_annual": mfd_annual, "ctc_20_cust": ctc_20_cust, "ctc_20_annual": ctc_20_annual, "ctc_50_cust": ctc_50_cust, "ctc_50_annual": ctc_50_annual, "ledmk1_cust": ledmk1_cust, "ledmk1_annual": ledmk1_annual, 
        "ledmk2_cust": ledmk2_cust, "ledmk2_annual": ledmk2_annual, "pwrpack_cust": pwrpack_cust, "pwrpack_annual": pwrpack_annual, "jet_og_cust": jet_og_cust, "jet_og_annual": jet_og_annual, 
        "pj_cust": pj_cust, "pj_annual": pj_annual, "pwj_cust": pwj_cust, "pwj_annual": pwj_annual, "mjmk1_cust": mjmk1_cust, "mjmk1_annual": mjmk1_annual, "mjmk2_cust": mjmk2_cust, 
        "mjmk2_annual": mjmk2_annual, "ccmk1_cust": ccmk1_cust, "ccmk1_annual": ccmk1_annual, "ccmk2_cust": ccmk2_cust, "ccmk2_annual": ccmk2_annual, "qj_cust": qj_cust, 
        "qj_annual": qj_annual, "dmx_cntl_cust": dmx_cntl_cust, "dmx_cntl_annual": dmx_cntl_annual, "lcd_cntl_cust": lcd_cntl_cust, "lcd_cntl_annual": lcd_cntl_annual, "tbmk1_cust": tbmk1_cust, 
        "tbmk1_annual": tbmk1_annual, "tbmk2_cust": tbmk2_cust, "tbmk2_annual": tbmk2_annual, "sm_cust": sm_cust, "sm_annual": sm_annual, "ss_cust": ss_cust, "ss_annual": ss_annual, "pwr_cntl_cust": pwr_cntl_cust, 
        "pwr_cntl_annual": pwr_cntl_annual, "blwr_cust": blwr_cust, "blwr_annual": blwr_annual
    
    }


