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
    magic_sales_data,
    df, df_quotes, df_cogs, df_shipstat_23, df_shipstat_24, df_qb, df_hsd, df_hist, unique_customer_list, master_customer_list, wholesale_list
)

#from ui.charts import (
#    display_pie_chart_comp, 
#    plot_bar_chart_product_seg, 
#    format_for_chart_hh,
#    plot_bar_chart_hh,
#    format_for_chart_product_seg
#)

from ui.components import (
    style_metric_cards
)


# --------------------------------------------------
# FUNCTIONS AND VARIABLES FOR REAL TIME CALCULATIONS
# --------------------------------------------------

def beginning_of_year(dt: datetime) -> datetime:
    return datetime(dt.year, 1, 1)

today = datetime.now()
one_year_ago = today - timedelta(days=365)
two_years_ago = today - timedelta(days=730)
three_years_ago = today - timedelta(days=1095)
four_years_ago = today - timedelta(days=1460)

# -----------------
# CREATE DATE LISTS
# -----------------

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

#df, df_quotes, df_cogs, df_shipstat_23, df_shipstat_24, df_qb, df_hsd, df_hist, unique_customer_list, master_customer_list, wholesale_list = load_all_data()

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
# DISPLAY FUNTION FOR PRODUCT SALES BY MONTH
# ------------------------------------------

def display_month_data_prod(
    product,
    sales_dict1,
    sales_dict2=None,
    value_type: str = "Unit",
    months=None,
):
    """
    Display monthly product data as metric cards in a 3-column grid.

    Parameters
    ----------
    product : str
        Product key to look up in the sales dictionaries.
    sales_dict1 : dict
        Current period sales dict: {month: {product: [value, ...]}, ...}
    sales_dict2 : dict or None
        Prior period sales dict with the same structure (optional).
        If provided, diff vs prior is shown in the description.
    value_type : str
        Either "Unit" or "Currency" (case-insensitive).
    months : list[str] or None
        List of month labels to display. If None, uses global months_x.
    """

    if months is None:
        months = months_x

    # Normalize type
    value_type = value_type.lower()  # "unit" or "currency"

    # Create enough rows of 3 columns each for all months
    num_rows = (len(months) + 2) // 3  # ceiling division
    rows = [st.columns(3) for _ in range(num_rows)]

    for idx, month in enumerate(months):
        row_idx, col_idx = divmod(idx, 3)
        col = rows[row_idx][col_idx]

        # Safely get the current value
        current_val = (
            sales_dict1.get(month, {})
                       .get(product, [0])[0]
        )

        # Compute diff vs prior year if provided
        desc = ""
        if sales_dict2 is not None:
            prior_val = (
                sales_dict2.get(month, {})
                           .get(product, [0])[0]
            )
            diff = current_val - prior_val
            sign = "+" if diff > 0 else "-" if diff < 0 else ""
            diff_abs = abs(int(diff))

            if value_type == "currency":
                desc = f"{sign} ${diff_abs:,} vs. prior year"
            else:
                desc = f"{sign} {diff_abs:,} vs. prior year"

        # Format main content based on type
        if value_type == "currency":
            content = f"${int(current_val):,}"
        else:
            content = f"{int(current_val):,}"

        with col:
            ui.metric_card(
                title=month,
                content=content,
                description=desc,
            )


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


# ------------------------------------------------
# DISPLAY FUNCTIONS FOR HOSES - REVENUE AND PROFIT
# ------------------------------------------------

def display_hose_data(hose_details1, hose_details2, hose_details3):
    """
    Display hose data for three years (currently 2025, 2024, 2023).

    Each `hose_detailsX` is expected to be a list of 8 items:
      - hose_detailsX[0..6]: dicts like {'5FT STD': [qty, rev], ...}
      - hose_detailsX[7]: a list/tuple [qty, rev] for '100FT STD'
    """
    # Pair year labels with their corresponding data
    year_data = [
        ("2025", hose_details1),
        ("2024", hose_details2),
        ("2023", hose_details3),
    ]

    cols = st.columns(3)

    for col, (year_label, hose_details) in zip(cols, year_data):
        with col:
            st.subheader(year_label)

            # First 7 groups are dicts of hose-type -> [units, revenue]
            for group_idx, group in enumerate(hose_details[:7]):
                group_units = 0
                group_rev = 0

                with st.container(border=True):
                    for hose_name, vals in group.items():
                        units = vals[0]
                        rev = vals[1]

                        group_units += units
                        group_rev += rev

                        ui.metric_card(
                            title=hose_name,
                            content=f"{int(units)} units",
                            description=f"${rev:,.2f} in rev",
                        )

                    # Group totals
                    st.markdown(
                        f"**Totals: {int(group_units)} - (${int(group_rev):,})**"
                    )

            # The 8th item (index 7) is the 100FT STD summary: [units, rev]
            hundred_units, hundred_rev = hose_details[7]
            ui.metric_card(
                title="100FT STD",
                content=f"{int(hundred_units)} units",
                description=f"${hundred_rev:,.2f} in rev",
                key=f"{year_label}-100FT",
            )

    return None


def display_hose_data_profit(hose_details1, hose_details2, hose_details3):
    """
    Display hose profit data for 2025, 2024, 2023.

    Each hose_detailsX is expected to be a list of 8 items:
      - hose_detailsX[0..6]: dicts like {'5FT STD': [qty, rev], ...}
      - hose_detailsX[7]: [qty, rev] for '100FT STD' (we ignore qty/rev here
        and compute profit based on prodTot* and bom_cost_hose).
    Relies on globals: prodTot25, prodTot24, prodTot23, bom_cost_hose, calc_prod_metrics.
    """

    # Pair each year with: (hose_details, current_prod_tot, prior_prod_tot or None)
    year_data = [
        ("2025", hose_details1, prodTot25["hose"], prodTot24["hose"]),
        ("2024", hose_details2, prodTot24["hose"], prodTot23["hose"]),
        ("2023", hose_details3, prodTot23["hose"], None),  # no prior year passed
    ]

    cols = st.columns(3)

    for col, (year_label, hose_details, prod_tot_curr, prod_tot_prev) in zip(cols, year_data):
        with col:
            st.subheader(year_label)

            # First 7 groups: dicts of hose_name -> [units, revenue]
            for group in hose_details[:7]:
                group_profit = 0.0

                with st.container(border=True):
                    for hose_name, vals in group.items():
                        # Call calc_prod_metrics with or without prior-year totals
                        if prod_tot_prev is not None:
                            prod_profit, profit_per_unit, *rest = calc_prod_metrics(
                                prod_tot_curr,
                                hose_name,
                                bom_cost_hose,
                                prod_tot_prev,
                            )
                        else:
                            prod_profit, profit_per_unit, *rest = calc_prod_metrics(
                                prod_tot_curr,
                                hose_name,
                                bom_cost_hose,
                            )

                        group_profit += prod_profit

                        ui.metric_card(
                            title=hose_name,
                            content=f"Profit: ${prod_profit:,.2f}",
                            description=f"Profit per Unit: ${profit_per_unit:,.2f}",
                        )

                    st.markdown(f"**Group Total: ${group_profit:,.2f}**")

            # 100FT STD – compute profit via calc_prod_metrics as well
            if prod_tot_prev is not None:
                prod_profit100, profit_per_unit100, *rest = calc_prod_metrics(
                    prod_tot_curr,
                    "100FT STD",
                    bom_cost_hose,
                    prod_tot_prev,
                )
            else:
                prod_profit100, profit_per_unit100, *rest = calc_prod_metrics(
                    prod_tot_curr,
                    "100FT STD",
                    bom_cost_hose,
                )

            ui.metric_card(
                title="100FT STD",
                content=f"Profit: ${prod_profit100:,.2f}",
                description=f"Profit per Unit: ${profit_per_unit100:,.2f}",
                key=f"{year_label}-100FT-profit",
            )

    return None


# -----------------------------------------------------
# DISPLAY FUNCTION FOR ACCESSORIES - REVENUE AND PROFIT
# -----------------------------------------------------

def display_acc_data():

    cola, colb, colc, cold, cole, colf, colg = st.columns([.1,.1,.2,.2,.2,.1,.1])
    
    with colc:
        for item, value in prodTot25['acc'].items():
            if item == 'CC-RC-2430':
                ui.metric_card(title='{}'.format(item), content='{} (PJ: {}, LA: {}, QJ: {})'.format(int(value[0]), int(value[2]), int(value[3]), int(value[4])), description='${:,.2f} in Revenue'.format(value[1]))
            else:
                value[0] = int(value[0])
                ui.metric_card(title='{}'.format(item), content='{}'.format(value[0]), description='${:,.2f} in Revenue'.format(value[1])) 
    with cold:
        key = 'anvienial23'
        for item_last, value_last in prodTot24['acc'].items():
            if item_last == 'CC-RC-2430':
                ui.metric_card(title='{}'.format(item_last), content='{} (PJ: {}, LA: {}, QJ: {})'.format(int(value_last[0]), int(value_last[2]), int(value_last[3]), int(value_last[4])), description='${:,.2f} in Revenue'.format(value_last[1]), key=key)
            else:
                value_last[0] = int(value_last[0])
                ui.metric_card(title='{}'.format(item_last), content='{}'.format(value_last[0]), description='${:,.2f} in Revenue'.format(value_last[1]), key=key)
            key += '64sdg5as'
    with cole:
        key2 = 'a'
        for item_last2, value_last2 in prodTot23['acc'].items():
            if item_last2 == 'CC-RC-2430':
                ui.metric_card(title='{}'.format(item_last2), content='{} (PJ: {}, LA: {})'.format(int(value_last2[0]), int(value_last2[2]), int(value_last2[3])), description='${:,.2f} in Revenue'.format(value_last2[1]), key=key2)
            else:
                value_last2[0] = int(value_last2[0])
                ui.metric_card(title='{}'.format(item_last2), content='{}'.format(value_last2[0]), description='${:,.2f} in Revenue'.format(value_last2[1]), key=key2)
            key2 += 'niane7'


def display_acc_data_profit():

    cola, colb, colc, cold, cole, colf, colg = st.columns([.1,.1,.2,.2,.2,.1,.1])

    with colc:
        for item, value in prodTot25['acc'].items():
            prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last = calc_prod_metrics(prodTot25['acc'], item, bom_cost_acc, prodTot24['acc']) 
            if item == 'CC-RC-2430':
                ui.metric_card(title='{}'.format(item), content='Total Profit: ${:,.2f}'.format(prod_profit), description='Profit per Unit: ${:,.2f}'.format(profit_per_unit))
            else:
                value[0] = int(value[0])
                ui.metric_card(title='{}'.format(item), content='Total Profit: ${:,.2f}'.format(prod_profit), description='Profit per Unit: ${:,.2f}'.format(profit_per_unit)) 
    with cold:
        key = '9jasdig'
        for item_last, value_last in prodTot24['acc'].items():
            prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last = calc_prod_metrics(prodTot24['acc'], item_last, bom_cost_acc, prodTot23['acc'])
            if item_last == 'CC-RC-2430':
                ui.metric_card(title='{}'.format(item_last), content='Total Profit: ${:,.2f}'.format(prod_profit), description='Profit per Unit: ${:,.2f}'.format(profit_per_unit))
            else:
                value_last[0] = int(value_last[0])
                ui.metric_card(title='{}'.format(item_last), content='Total Profit: ${:,.2f}'.format(prod_profit), description='Profit per Unit: ${:,.2f}'.format(profit_per_unit), key=key)
            key += 'adsg2f'
    with cole:
        key2 = 'a'
        for item_last2, value_last2 in prodTot23['acc'].items():
            prod_profit, profit_per_unit, avg_price = calc_prod_metrics(prodTot23['acc'], item_last2, bom_cost_acc)
            if item_last2 == 'CC-RC-2430':
                ui.metric_card(title='{}'.format(item_last2), content='Total Profit: ${:,.2f}'.format(prod_profit), description='Profit per Unit: ${:,.2f}'.format(profit_per_unit), key=key2)
            else:
                value_last2[0] = int(value_last2[0])
                ui.metric_card(title='{}'.format(item_last2), content='Total Profit: ${:,.2f}'.format(prod_profit), description='Profit per Unit: ${:,.2f}'.format(profit_per_unit), key=key2)
            key2 += 'ba'
        

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
    two_years_ago_date = two_years_ago.date()
    one_year_ago_date   = one_year_ago.date()
    today_date          = today.date()
    
    begin_two = beginning_of_year(two_years_ago).date()
    begin_one = beginning_of_year(one_year_ago).date()
    begin_today = beginning_of_year(today).date()
    
    # Build boolean masks for the different time ranges.
    mask_23 = (df_sku["order_date_date"] >= begin_two) & (df_sku["order_date_date"] <= two_years_ago_date)
    mask_24 = (df_sku["order_date_date"] >= begin_one) & (df_sku["order_date_date"] <= one_year_ago_date)
    #mask_24 = (df_sku["order_date_date"] >= begin_today) & (df_sku["order_date_date"] <= today_date)
    #mask_25 = (df_sku["order_date"].dt.year == 2025)  # 2025 comparison can remain on timestamps.
    
    # Sum the quantities for each date range.
    #prod_cnt_22 = df_sku.loc[mask_22, "quantity"].sum()
    prod_cnt_23 = df_sku.loc[mask_23, "quantity"].sum()
    prod_cnt_24 = df_sku.loc[mask_24, "quantity"].sum()
    #prod_cnt_25 = df_sku.loc[mask_25, "quantity"].sum()
    
    # (Return only the counts you need. In your example, you returned prod_cnt_23 and prod_cnt_24.)
    return prod_cnt_23, prod_cnt_24


def to_date_product_rev(sku_string):

    # Filter rows where the item_sku starts with sku_sting
    mask_sku = df['item_sku'].str.startswith(sku_string)
    df_sku = df[mask_sku].copy()

    # Ensure order_date is a datetime and create a date-only column
    df_sku['order_date'] = pd.to_datetime(df_sku['order_date'], errors='coerce')
    df_sku['order_date_date'] = df_sku['order_date'].dt.date

    # Convert reference datetime values to dates
    two_years_ago_date = two_years_ago.date()
    one_year_ago_date = one_year_ago.date()
    today_datet = today.date()

    begin_two = beginning_of_year(two_years_ago).date()
    begin_one = beginning_of_year(one_year_ago).date()
    begin_today = beginning_of_year(today).date()

    # Build boolean masks for the different time ranges
    mask_23 = (df_sku['order_date_date'] >= begin_two) & (df_sku['order_date_date'] <= two_years_ago_date)
    mask_24 = (df_sku['order_date_date'] >= begin_one) & (df_sku['order_date_date'] <= one_year_ago_date)

    # Sum the sales totals for each date range
    prod_rev23 = df_sku.loc[mask_23, 'total_line_item_spend'].sum()
    prod_rev24 = df_sku.loc[mask_24, 'total_line_item_spend'].sum()
    

    return prod_rev23, prod_rev24


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
                    if year == 2025:
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

#profit_26 = profit_by_type(['2026'], ['Jet', 'Control', 'Handheld', 'Hose', 'Accessory'])
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
        rev23, rev24 = to_date_product_rev(sku_map[prod_select])

        return rev24 if year == 2025 else rev23 if year == 2024 else None

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


# -----------------------------------
# RENDER FUNCTION FOR DISPLAY IN MAIN
# -----------------------------------

def render_products():
    

    col1, col2, col3 = st.columns([.25, .5, .25], gap='medium')

    with col2:
        # NAVIGATION TABS
        prod_cat = ui.tabs(options=['Jets', 'Controllers', 'Handhelds', 'Hoses', 'Accessories', 'MagicFX'], default_value='Jets', key='Product Categories')
        #year = ui.tabs(options=[2025, 2024, 2023], default_value=2024, key='Products Year Select')


    
    if prod_cat == 'Jets':

        pj_td23, pj_td24 = to_date_product('CC-PROJ')
        mj_td23, mj_td24 = to_date_product('CC-MJMK')
        qj_td23, qj_td24 = to_date_product('CC-QJ')
        cc_td23, cc_td24 = to_date_product('CC-CC2')

        with col2:
            year = ui.tabs(options=[2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015, 2014, 'Historical'], default_value=2025, key='Jet Year Select')

        if year == 2025:
            
            total_jet_rev = prodTot25['jet']['Pro Jet'][1] + prodTot25['jet']['Quad Jet'][1] + prodTot25['jet']['Micro Jet'][1] + prodTot25['jet']['Cryo Clamp'][1]
            
            with col2:
                cola, colb, colc, cold = st.columns(4, gap='medium')
    
                cola.subheader('Pro Jet')
                cola.metric('{:.1f}% of Total Revenue'.format((prodTot25['jet']['Pro Jet'][1] / td_25_tot) * 100), '{}'.format(int(prodTot25['jet']['Pro Jet'][0])), int(prodTot25['jet']['Pro Jet'][0] - pj_td24))
    
                colb.subheader('Quad Jet')
                colb.metric('{:.1f}% of Total Revenue'.format((prodTot25['jet']['Quad Jet'][1] / td_25_tot) * 100), '{}'.format(int(prodTot25['jet']['Quad Jet'][0])), int(prodTot25['jet']['Quad Jet'][0] - qj_td24))
    
                colc.subheader('Micro Jet')
                colc.metric('{:.1f}% of Total Revenue'.format((prodTot25['jet']['Micro Jet'][1] / td_25_tot) * 100), '{}'.format(int(prodTot25['jet']['Micro Jet'][0])), int(prodTot25['jet']['Micro Jet'][0] - mj_td24))
    
                cold.subheader('Cryo Clamp')
                cold.metric('{:.1f}% of Total Revenue'.format((prodTot25['jet']['Cryo Clamp'][1] / td_25_tot) * 100), '{}'.format(int(prodTot25['jet']['Cryo Clamp'][0])), int(prodTot25['jet']['Cryo Clamp'][0] - cc_td24))

                prod_profit_PJ, profit_per_unit_PJ, prod_profit_last_PJ, avg_price_PJ, avg_price_last_PJ, wholesale_sales_PJ, wholesale_percentage_PJ, wholesale_delta_PJ = calc_prod_metrics(prodTot25['jet'], 'Pro Jet', bom_cost_jet, prodTot24['jet'])
                prod_profit_QJ, profit_per_unit_QJ, prod_profit_last_QJ, avg_price_QJ, avg_price_last_QJ, wholesale_sales_QJ, wholesale_percentage_QJ, wholesale_delta_QJ = calc_prod_metrics(prodTot25['jet'], 'Quad Jet', bom_cost_jet, prodTot24['jet'])
                prod_profit_MJ, profit_per_unit_MJ, prod_profit_last_MJ, avg_price_MJ, avg_price_last_MJ, wholesale_sales_MJ, wholesale_percentage_MJ, wholesale_delta_MJ = calc_prod_metrics(prodTot25['jet'], 'Micro Jet', bom_cost_jet, prodTot24['jet'])
                prod_profit_CC, profit_per_unit_CC, prod_profit_last_CC, avg_price_CC, avg_price_last_CC, wholesale_sales_CC, wholesale_percentage_CC, wholesale_delta_CC = calc_prod_metrics(prodTot25['jet'], 'Cryo Clamp', bom_cost_jet, prodTot24['jet'])
                
                tot_jet_rev25 = prodTot25['jet']['Pro Jet'][1] + prodTot25['jet']['Quad Jet'][1] + prodTot25['jet']['Micro Jet'][1] + prodTot25['jet']['Cryo Clamp'][1]
                tot_jet_prof25 = prod_profit_PJ + prod_profit_QJ + prod_profit_MJ + prod_profit_CC
                if tot_jet_rev25 == 0:
                    jet_prof_margin25 = 0
                else:
                    jet_prof_margin25 = (tot_jet_prof25 / tot_jet_rev25) * 100
                
                colx, coly, colz = st.columns(3)
    
                colx.metric('**Total Revenue**', '${:,}'.format(int(tot_jet_rev25)))
                coly.metric('**Profit Margin**', '{:,.2f}%'.format(jet_prof_margin25))
                colz.metric('**Total Profit**', '${:,}'.format(int(tot_jet_prof25)))
    
                style_metric_cards()

                st.divider()
                display_pie_chart_comp(prodTot25['jet'])
                st.divider()

                prod_select = ui.tabs(options=['Pro Jet', 'Quad Jet', 'Micro Jet', 'Cryo Clamp'], default_value='Pro Jet', key='Jets')
        
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
    
                prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last, wholesale_sales, wholesale_percentage, wholesale_delta = calc_prod_metrics(prodTot25['jet'], prod_select, bom_cost_jet, prodTot24['jet'])

                # Calculate prior year to-date revenue for selected product
                prior_td_revenue = convert_prod_select(prod_select, 2025)

                # Convert prod_select to the td variable for 2024
                prod_td24 = convert_prod_select_profit(prod_select)
    
                col5.metric('**Revenue**', '${:,.2f}'.format(prodTot25['jet'][prod_select][1]), percent_of_change(prior_td_revenue, prodTot25['jet'][prod_select][1]))
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), percent_of_change(to_date_product_profit(prod_td24, prior_td_revenue, bom_cost_jet[prod_select]), prod_profit))
                col6.metric('**Wholesale**', '{:.2f}%'.format(wholesale_percentage))
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), percent_of_change(avg_price_last, avg_price))        
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_jet[prod_select]), '')
                
                display_month_data_prod(prod_select, jet25, jet24)
        
        elif year == 2024:
            
            total_jet_rev = prodTot24['jet']['Pro Jet'][1] + prodTot24['jet']['Quad Jet'][1] + prodTot24['jet']['Micro Jet'][1] + prodTot24['jet']['Cryo Clamp'][1]
            
            with col2:
                cola, colb, colc, cold = st.columns(4)
    
                cola.subheader('Pro Jet')
                cola.metric('{:.1f}% of Total Revenue'.format((prodTot24['jet']['Pro Jet'][1] / total_24) * 100), '{}'.format(int(prodTot24['jet']['Pro Jet'][0])), int(prodTot24['jet']['Pro Jet'][0] - prodTot23['jet']['Pro Jet'][0]))
    
                colb.subheader('Quad Jet')
                colb.metric('{:.1f}% of Total Revenue'.format((prodTot24['jet']['Quad Jet'][1] / total_24) * 100), '{}'.format(int(prodTot24['jet']['Quad Jet'][0])), int(prodTot24['jet']['Quad Jet'][0] - prodTot23['jet']['Quad Jet'][0]))
    
                colc.subheader('Micro Jet')
                colc.metric('{:.1f}% of Total Revenue'.format((prodTot24['jet']['Micro Jet'][1] / total_24) * 100), '{}'.format(int(prodTot24['jet']['Micro Jet'][0])), int(prodTot24['jet']['Micro Jet'][0] - prodTot23['jet']['Micro Jet'][0]))
    
                cold.subheader('Cryo Clamp')
                cold.metric('{:.1f}% of Total Revenue'.format((prodTot24['jet']['Cryo Clamp'][1] / total_24) * 100), '{}'.format(int(prodTot24['jet']['Cryo Clamp'][0])), int(prodTot24['jet']['Cryo Clamp'][0] - prodTot23['jet']['Cryo Clamp'][0]))

                prod_profit_PJ, profit_per_unit_PJ, prod_profit_last_PJ, avg_price_PJ, avg_price_last_PJ, wholesale_sales_PJ, wholesale_percentage_PJ, wholesale_delta_PJ = calc_prod_metrics(prodTot24['jet'], 'Pro Jet', bom_cost_jet, prodTot23['jet'])
                prod_profit_QJ, profit_per_unit_QJ, prod_profit_last_QJ, avg_price_QJ, avg_price_last_QJ, wholesale_sales_QJ, wholesale_percentage_QJ, wholesale_delta_QJ = calc_prod_metrics(prodTot24['jet'], 'Quad Jet', bom_cost_jet, prodTot23['jet'])
                prod_profit_MJ, profit_per_unit_MJ, prod_profit_last_MJ, avg_price_MJ, avg_price_last_MJ, wholesale_sales_MJ, wholesale_percentage_MJ, wholesale_delta_MJ = calc_prod_metrics(prodTot24['jet'], 'Micro Jet', bom_cost_jet, prodTot23['jet'])
                prod_profit_CC, profit_per_unit_CC, prod_profit_last_CC, avg_price_CC, avg_price_last_CC, wholesale_sales_CC, wholesale_percentage_CC, wholesale_delta_CC = calc_prod_metrics(prodTot24['jet'], 'Cryo Clamp', bom_cost_jet, prodTot23['jet'])
                
                tot_jet_rev24 = prodTot24['jet']['Pro Jet'][1] + prodTot24['jet']['Quad Jet'][1] + prodTot24['jet']['Micro Jet'][1] + prodTot24['jet']['Cryo Clamp'][1]
                tot_jet_prof24 = prod_profit_PJ + prod_profit_QJ + prod_profit_MJ + prod_profit_CC
                jet_prof_margin24 = (tot_jet_prof24 / tot_jet_rev24) * 100
                
                colx, coly, colz = st.columns(3)
    
                colx.metric('**Total Revenue**', '${:,}'.format(int(tot_jet_rev24)))
                coly.metric('**Profit Margin**', '{:,.2f}%'.format(jet_prof_margin24))
                colz.metric('**Total Profit**', '${:,}'.format(int(tot_jet_prof24)))
                
                style_metric_cards()

                st.divider()
                display_pie_chart_comp(prodTot24['jet'])
                st.divider()
                
                prod_select = ui.tabs(options=['Pro Jet', 'Quad Jet', 'Micro Jet', 'Cryo Clamp'], default_value='Pro Jet', key='Jets')
        
                prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last, wholesale_sales, wholesale_percentage, wholesale_delta = calc_prod_metrics(prodTot24['jet'], prod_select, bom_cost_jet, prodTot23['jet'])

                # Calculate prior year to-date revenue for selected product
                #prior_td_revenue = convert_prod_select(prod_select, 2024)
                
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
        
                col5.metric('**Revenue**', '${:,.2f}'.format(prodTot24['jet'][prod_select][1]), percent_of_change(prodTot23['jet'][prod_select][1], prodTot24['jet'][prod_select][1]))
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), percent_of_change(prod_profit_last, prod_profit))
                col6.metric('**Wholesale**', '{:.2f}%'.format(wholesale_percentage))
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), percent_of_change(avg_price_last, avg_price))        
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_jet[prod_select]), '')
            
                    
                display_month_data_prod(prod_select, jet24, jet23)
            
            
        elif year == 2023:
            
            total_jet_rev = prodTot23['jet']['Pro Jet'][1] + prodTot23['jet']['Quad Jet'][1] + prodTot23['jet']['Micro Jet'][1] + prodTot23['jet']['Cryo Clamp'][1]
            
            with col2:
                cola, colb, colc, cold = st.columns(4)
        
                cola.subheader('Pro Jet')
                cola.metric('{:.1f}% of Total Revenue'.format((prodTot23['jet']['Pro Jet'][1] / total_23) * 100), '{}'.format(int(prodTot23['jet']['Pro Jet'][0])), '')
    
                colb.subheader('Quad Jet')
                colb.metric('{:.1f}% of Total Revenue'.format((prodTot23['jet']['Quad Jet'][1] / total_23) * 100), '{}'.format(int(prodTot23['jet']['Quad Jet'][0])), '')
    
                colc.subheader('Micro Jet')
                colc.metric('{:.1f}% of Total Revenue'.format((prodTot23['jet']['Micro Jet'][1] / total_23) * 100), '{}'.format(int(prodTot23['jet']['Micro Jet'][0])), '')
    
                cold.subheader('Cryo Clamp')
                cold.metric('{:.1f}% of Total Revenue'.format((prodTot23['jet']['Cryo Clamp'][1] / total_23) * 100), '{}'.format(int(prodTot23['jet']['Cryo Clamp'][0])), '')
    
                prod_profit_PJ, profit_per_unit_PJ, prod_profit_last_PJ, avg_price_PJ, avg_price_last_PJ = calc_prod_metrics(prodTot23['jet'], 'Pro Jet', bom_cost_jet)
                prod_profit_QJ, profit_per_unit_QJ, prod_profit_last_QJ, avg_price_QJ, avg_price_last_QJ = calc_prod_metrics(prodTot23['jet'], 'Quad Jet', bom_cost_jet)
                prod_profit_MJ, profit_per_unit_MJ, prod_profit_last_MJ, avg_price_MJ, avg_price_last_MJ = calc_prod_metrics(prodTot23['jet'], 'Micro Jet', bom_cost_jet)
                prod_profit_CC, profit_per_unit_CC, prod_profit_last_CC, avg_price_CC, avg_price_last_CC = calc_prod_metrics(prodTot23['jet'], 'Cryo Clamp', bom_cost_jet)
                
                tot_jet_rev23 = prodTot23['jet']['Pro Jet'][1] + prodTot23['jet']['Quad Jet'][1] + prodTot23['jet']['Micro Jet'][1] + prodTot23['jet']['Cryo Clamp'][1]
                tot_jet_prof23 = prod_profit_PJ + prod_profit_QJ + prod_profit_MJ + prod_profit_CC
                jet_prof_margin23 = (tot_jet_prof23 / tot_jet_rev23) * 100
                
                colx, coly, colz = st.columns(3)
    
                colx.metric('**Total Revenue**', '${:,}'.format(int(tot_jet_rev23)))
                coly.metric('**Profit Margin**', '{:,.2f}%'.format(jet_prof_margin23))
                colz.metric('**Total Profit**', '${:,}'.format(int(tot_jet_prof23)))
         
                style_metric_cards()
                
                st.divider()
                display_pie_chart_comp(prodTot23['jet'])
                st.divider()
                
                prod_select = ui.tabs(options=['Pro Jet', 'Quad Jet', 'Micro Jet', 'Cryo Clamp'], default_value='Pro Jet', key='Jets')
        
        
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
                
                prod_profit, profit_per_unit, avg_price, wholesale_sales, wholesale_percentage = calc_prod_metrics(prodTot23['jet'], prod_select, bom_cost_jet)
    
    
                col5.metric('**Revenue**', '${:,.2f}'.format(prodTot23['jet'][prod_select][1]), '')
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), '')
                col6.metric('**Wholesale**', '{:.2f}%'.format(wholesale_percentage))
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), '')        
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_jet[prod_select]), '')
                
                display_month_data_prod(prod_select, jet23)  

        elif year == 2022:
            
            with col2:
                cola, colb, colc= st.columns(3)
        
                cola.subheader('Pro Jet')
                cola.metric('', '{}'.format(pj_annual['2022']), 'N/A')
    
                colb.subheader('Quad Jet')
                colb.metric('', '{}'.format(qj_annual['2022']), (qj_annual['2022'] - qj_annual['2021']))

                colc.subheader('Cryo Clamp MK1')
                colc.metric('', '{}'.format(ccmk1_annual['2022']), (ccmk1_annual['2022'] - ccmk1_annual['2021']))
    
                cola.subheader('Micro Jet MK1')
                cola.metric('', '{}'.format(mjmk1_annual['2022']), (mjmk1_annual['2022'] - mjmk1_annual['2021']))
                                        
                colb.subheader('Total Jets')
                colb.metric('', '{}'.format(mjmk1_annual['2022'] + mjmk2_annual['2022'] + ccmk1_annual['2022'] + pj_annual['2022'] + qj_annual['2022']), ((mjmk1_annual['2022'] + mjmk2_annual['2022'] + ccmk1_annual['2022'] + pj_annual['2022'] + qj_annual['2022']) - (mjmk1_annual['2021'] + mjmk2_annual['2021'] + ccmk1_annual['2021'] + jet_og_annual['2021'] + qj_annual['2021'] + pwj_annual['2021'])))
                
                colc.subheader('Micro Jet MK2')
                colc.metric('', '{}'.format(mjmk2_annual['2022']), (mjmk2_annual['2022'] - mjmk2_annual['2021']))

                style_metric_cards()

        elif year == 2021:
            
            with col2:
                cola, colb, colc = st.columns(3)
        
                cola.subheader('DMX Jet')
                cola.metric('', '{}'.format(jet_og_annual['2021']), (jet_og_annual['2021'] - jet_og_annual['2020']))
    
                colb.subheader('Quad Jet')
                colb.metric('', '{}'.format(qj_annual['2021']), (qj_annual['2021'] - qj_annual['2020']))

                colc.subheader('Cryo Clamp MK1')
                colc.metric('', '{}'.format(ccmk1_annual['2021']), (ccmk1_annual['2021'] - ccmk1_annual['2020']))
    
                cola.subheader('Micro Jet MK1')
                cola.metric('', '{}'.format(mjmk1_annual['2021']), (mjmk1_annual['2021'] - mjmk1_annual['2020']))

                colb.subheader('Power Jet')
                colb.metric('', '{}'.format(pwj_annual['2021']), (pwj_annual['2021'] - pwj_annual['2020']))
                                        
                colb.subheader('Total Jets')
                colb.metric('', '{}'.format(mjmk1_annual['2021'] + mjmk2_annual['2021'] + ccmk1_annual['2021'] + jet_og_annual['2021'] + qj_annual['2021'] + pwj_annual['2021']), (mjmk1_annual['2021'] + mjmk2_annual['2021'] + ccmk1_annual['2021'] + jet_og_annual['2021'] + qj_annual['2021'] + pwj_annual['2021'] - (mjmk1_annual['2020'] + ccmk1_annual['2020'] + jet_og_annual['2020'] +  pwj_annual['2020'])))
                
                colc.subheader('Micro Jet MK2')
                colc.metric('', '{}'.format(mjmk2_annual['2021']), (mjmk2_annual['2021'] - mjmk2_annual['2020']))

                style_metric_cards()

        elif year == 2020:
            
            with col2:
                cola, colb, colc = st.columns(3)
        
                cola.subheader('DMX Jet')
                cola.metric('', '{}'.format(jet_og_annual['2020']), (jet_og_annual['2020'] - jet_og_annual['2019']))
    
                colb.subheader('Micro Jet MK1')
                colb.metric('', '{}'.format(mjmk1_annual['2020']), (mjmk1_annual['2020'] - mjmk1_annual['2019']))

                colc.subheader('Power Jet')
                colc.metric('', '{}'.format(pwj_annual['2020']), (pwj_annual['2020'] - pwj_annual['2019']))

                colb.subheader('Cryo Clamp MK1')
                colb.metric('', '{}'.format(ccmk1_annual['2020']), (ccmk1_annual['2020'] - ccmk1_annual['2019']))

                colb.subheader('Total Jets')
                colb.metric('', '{}'.format(mjmk1_annual['2020'] + ccmk1_annual['2020'] + jet_og_annual['2020'] +  pwj_annual['2020']), ((mjmk1_annual['2020'] + ccmk1_annual['2020'] + jet_og_annual['2020'] +  pwj_annual['2020']) - (mjmk1_annual['2019'] + ccmk1_annual['2019'] + jet_og_annual['2019'] +  pwj_annual['2019'])))
                

                style_metric_cards()

        elif year == 2019:
            
            with col2:
                cola, colb, colc = st.columns(3)
        
                cola.subheader('DMX Jet')
                cola.metric('', '{}'.format(jet_og_annual['2019']), (jet_og_annual['2019'] - jet_og_annual['2018']))
    
                colb.subheader('Micro Jet MK1')
                colb.metric('', '{}'.format(mjmk1_annual['2019']), (mjmk1_annual['2019'] - mjmk1_annual['2018']))

                colc.subheader('Power Jet')
                colc.metric('', '{}'.format(pwj_annual['2019']), (pwj_annual['2019'] - pwj_annual['2018']))

                colb.subheader('Cryo Clamp MK1')
                colb.metric('', '{}'.format(ccmk1_annual['2019']), (ccmk1_annual['2019'] - ccmk1_annual['2018']))

                colb.subheader('Total Jets')
                colb.metric('', '{}'.format(mjmk1_annual['2019'] + ccmk1_annual['2019'] + jet_og_annual['2019'] +  pwj_annual['2019']), ((mjmk1_annual['2019'] + ccmk1_annual['2019'] + jet_og_annual['2019'] +  pwj_annual['2019']) - (mjmk1_annual['2018'] + ccmk1_annual['2018'] + jet_og_annual['2018'] +  pwj_annual['2018'])))
                
                style_metric_cards()

        elif year == 2018:
            
            with col2:
                cola, colb, colc = st.columns(3)
        
                cola.subheader('DMX Jet')
                cola.metric('', '{}'.format(jet_og_annual['2018']), (jet_og_annual['2018'] - jet_og_annual['2017']))

                colb.subheader('Power Jet')
                colb.metric('', '{}'.format(pwj_annual['2018']), (pwj_annual['2018'] - pwj_annual['2017']))

                colc.subheader('Cryo Clamp MK1')
                colc.metric('', '{}'.format(ccmk1_annual['2018']), (ccmk1_annual['2018'] - ccmk1_annual['2017']))

                colb.subheader('Total Jets')
                colb.metric('', '{}'.format(ccmk1_annual['2018'] + jet_og_annual['2018'] +  pwj_annual['2018']), ((ccmk1_annual['2018'] + jet_og_annual['2018'] +  pwj_annual['2018']) - (ccmk1_annual['2017'] + jet_og_annual['2017'] +  pwj_annual['2017'])))

                style_metric_cards()

        elif year == 2017:
            
            with col2:
                cola, colb, colc = st.columns(3)
        
                cola.subheader('DMX Jet')
                cola.metric('', '{}'.format(jet_og_annual['2017']), (jet_og_annual['2017'] - jet_og_annual['2016']))

                colb.subheader('Power Jet')
                colb.metric('', '{}'.format(pwj_annual['2017']), (pwj_annual['2017'] - pwj_annual['2016']))

                colc.subheader('**Total Jets**')
                colc.metric('', '{}'.format(jet_og_annual['2017'] + pwj_annual['2017']), ((jet_og_annual['2017'] +  pwj_annual['2017']) - (jet_og_annual['2016'] +  pwj_annual['2016'])))
            
                style_metric_cards()

        elif year == 2016:
            
            with col2:
                cola, colb, colc = st.columns(3)
        
                colb.subheader('DMX Jet')
                colb.metric('', '{}'.format(jet_og_annual['2016']), (jet_og_annual['2016'] - jet_og_annual['2015']))

                style_metric_cards()

        elif year == 2015:
            
            with col2:
                cola, colb, colc = st.columns(3)
        
                colb.subheader('DMX Jet')
                colb.metric('', '{}'.format(jet_og_annual['2015']), (jet_og_annual['2015'] - jet_og_annual['2014']))

                style_metric_cards()

        elif year == 2014:
            
            with col2:
                cola, colb, colc = st.columns(3)
        
                colb.subheader('DMX Jet')
                colb.metric('', '{}'.format(jet_og_annual['2014']), '')

                style_metric_cards()

        elif year == 'Historical':

            pj_tot_unit = prodTot25['jet']['Pro Jet'][0] + prodTot24['jet']['Pro Jet'][0] + prodTot23['jet']['Pro Jet'][0] + pj_annual['2022']
            pj_tot_rev = prodTot25['jet']['Pro Jet'][1] + prodTot24['jet']['Pro Jet'][1] + prodTot23['jet']['Pro Jet'][1] + (pj_annual['2022'] * 1174)

            qj_tot_unit = prodTot25['jet']['Quad Jet'][0] + prodTot24['jet']['Quad Jet'][0] + prodTot23['jet']['Quad Jet'][0] + qj_annual['2022']
            qj_tot_rev = prodTot25['jet']['Quad Jet'][1] + prodTot24['jet']['Quad Jet'][1] + prodTot23['jet']['Quad Jet'][1] + (qj_annual['2022'] * 1800)

            mj2_tot_unit = prodTot25['jet']['Micro Jet'][0] + prodTot24['jet']['Micro Jet'][0] + prodTot23['jet']['Micro Jet'][0] + mjmk2_annual['2022'] + mjmk2_annual['2021']
            mj2_tot_rev = prodTot25['jet']['Micro Jet'][1] + prodTot24['jet']['Micro Jet'][1] + prodTot23['jet']['Micro Jet'][1] + (mjmk2_annual['2022'] * 778) + (mjmk2_annual['2021'] * 778)

            mj1_tot_unit = mjmk1_annual['2022'] + mjmk1_annual['2021'] + mjmk1_annual['2020'] + mjmk1_annual['2019']
            mj1_tot_rev = (mjmk1_annual['2022'] * 778.63) + (mjmk1_annual['2021'] * 778.99) + (mjmk1_annual['2020'] * 778.52) + (mjmk1_annual['2019'] * 778)

            cc2_tot_unit = prodTot25['jet']['Cryo Clamp'][0] + prodTot24['jet']['Cryo Clamp'][0] + prodTot23['jet']['Cryo Clamp'][0]
            cc2_tot_rev = prodTot25['jet']['Cryo Clamp'][1] + prodTot24['jet']['Cryo Clamp'][1] + prodTot23['jet']['Cryo Clamp'][1] 

            cc1_tot_unit = ccmk1_annual['2022'] + ccmk1_annual['2021'] + ccmk1_annual['2020'] + ccmk1_annual['2019'] + ccmk1_annual['2018']
            cc1_tot_rev = (ccmk1_annual['2022'] * 387.91) + (ccmk1_annual['2021'] * 387.91) + (ccmk1_annual['2020'] * 387.91) + (ccmk1_annual['2019'] * 387.91) + (ccmk1_annual['2018'] * 387.91)

            dmx_jet_tot_unit = jet_og_annual['2021'] + jet_og_annual['2020'] + jet_og_annual['2019'] + jet_og_annual['2018'] + jet_og_annual['2017'] + jet_og_annual['2016'] + jet_og_annual['2015'] + jet_og_annual['2014']
            dmx_jet_tot_rev = (jet_og_annual['2021'] * 1098.54) + (jet_og_annual['2020'] * 1098.54) + (jet_og_annual['2019'] * 1098.54) + (jet_og_annual['2018'] * 1098.54) + (jet_og_annual['2017'] * 1098.54) + (jet_og_annual['2016'] * 1098.54) + (jet_og_annual['2015'] * 1098.54) + (jet_og_annual['2014'] * 1098.54)
            
            pwj_tot_unit = pwj_annual['2021'] + pwj_annual['2020'] + pwj_annual['2019'] + pwj_annual['2018'] + pwj_annual['2017'] 
            pwj_tot_rev = (pwj_annual['2021'] * 948.53) + (pwj_annual['2020'] * 948.53) + (pwj_annual['2019'] * 948.53) + (pwj_annual['2018'] * 948.53) + (pwj_annual['2017'] * 948.53)


            cola, colb, colc, cold, cole = st.columns(5)

            colb.subheader('Pro Jet')
            colb.metric('**${:,.2f}**'.format(pj_tot_rev), '{}'.format(int(pj_tot_unit)))
            colb.subheader('Cryo Clamp MKII')
            colb.metric('**${:,.2f}**'.format(cc2_tot_rev), '{}'.format(int(cc2_tot_unit)))
            colb.subheader('Cryo Clamp MKI')
            colb.metric('**${:,.2f}**'.format(cc1_tot_rev), '{}'.format(cc1_tot_unit))

            colc.subheader('Quad Jet')
            colc.metric('**${:,.2f}**'.format(qj_tot_rev), '{}'.format(int(qj_tot_unit)))
            colc.subheader('Power Jet')
            colc.metric('**${:,.2f}**'.format(pwj_tot_rev), '{}'.format(pwj_tot_unit))
            colc.subheader('Total Jets')
            colc.metric('**${:,.2f}**'.format(pwj_tot_rev + dmx_jet_tot_rev + cc1_tot_rev + cc2_tot_rev + mj1_tot_rev + mj2_tot_rev + qj_tot_rev + pj_tot_rev), '{}'.format(int(pwj_tot_unit + dmx_jet_tot_unit + cc1_tot_unit + cc2_tot_unit + mj1_tot_unit + mj2_tot_unit + qj_tot_unit + pj_tot_unit)))

            cold.subheader('DMX Jet')
            cold.metric('**${:,.2f}**'.format(dmx_jet_tot_rev), '{}'.format(dmx_jet_tot_unit))
            cold.subheader('Micro Jet MKII')
            cold.metric('**${:,.2f}**'.format(mj2_tot_rev), '{}'.format(int(mj2_tot_unit)))
            cold.subheader('Micro Jet MKI')
            cold.metric('**${:,.2f}**'.format(mj1_tot_rev), '{}'.format(mj1_tot_unit))

            style_metric_cards()

            jet_annual_dict = {'2025': 0, '2024': 0, '2023': 0, '2022': 0, '2021': 0, '2020': 0, '2019': 0, '2018': 0, '2017': 0, '2016': 0, '2015': 0, '2014': 0}
            jet_annual_dict_seg = {'2025': {'Pro Jet': prodTot25['jet']['Pro Jet'][0], 'Quad Jet': prodTot25['jet']['Quad Jet'][0], 'Micro Jet MKII': prodTot25['jet']['Micro Jet'][0], 'Cryo Clamp': prodTot25['jet']['Cryo Clamp'][0]}, '2024': {'Pro Jet': prodTot24['jet']['Pro Jet'][0], 'Quad Jet': prodTot24['jet']['Quad Jet'][0], 'Micro Jet MKII': prodTot24['jet']['Micro Jet'][0], 'Cryo Clamp': prodTot24['jet']['Cryo Clamp'][0]}, '2023': {'Pro Jet': prodTot23['jet']['Pro Jet'][0], 'Quad Jet': prodTot23['jet']['Quad Jet'][0], 'Micro Jet MKII': prodTot23['jet']['Micro Jet'][0], 'Cryo Clamp': prodTot23['jet']['Cryo Clamp'][0]}, '2022': {'Pro Jet': pj_annual['2022'], 'Quad Jet': qj_annual['2022'], 'Micro Jet MKII': mjmk2_annual['2022'], 'Micro Jet MKI': mjmk1_annual['2022'], 'Cryo Clamp MKI': ccmk1_annual['2022']}, '2021': {'Micro Jet MKII': mjmk2_annual['2021'], 'Micro Jet MKI': mjmk1_annual['2021'], 'Cryo Clamp MKI': ccmk1_annual['2021'], 'Quad Jet': qj_annual['2021'], 'DMX Jet': jet_og_annual['2021'], 'Power Jet': pwj_annual['2021']}, '2020': {'Micro Jet MKI': mjmk1_annual['2020'], 'Cryo Clamp MKI': ccmk1_annual['2020'], 'DMX Jet': jet_og_annual['2020'], 'Power Jet': pwj_annual['2020']}, '2019': {'Micro Jet MKI': mjmk1_annual['2019'], 'Cryo Clamp MKI': ccmk1_annual['2019'], 'DMX Jet': jet_og_annual['2019'], 'Power Jet': pwj_annual['2019']}, '2018': {'Cryo Clamp MKI': ccmk1_annual['2018'], 'DMX Jet': jet_og_annual['2018'], 'Power Jet': pwj_annual['2018']}, '2017': {'DMX Jet': jet_og_annual['2017'], 'Power Jet': pwj_annual['2017']}, '2016': {'DMX Jet': jet_og_annual['2016']}, '2015': {'DMX Jet': jet_og_annual['2015']}, '2014': {'DMX Jet': jet_og_annual['2014']}}
            jet_annual_dict['2025'] += prodTot25['jet']['Pro Jet'][0] + prodTot25['jet']['Quad Jet'][0] + prodTot25['jet']['Micro Jet'][0] + prodTot25['jet']['Cryo Clamp'][0] 
            jet_annual_dict['2024'] += prodTot24['jet']['Pro Jet'][0] + prodTot24['jet']['Quad Jet'][0] + prodTot24['jet']['Micro Jet'][0] + prodTot24['jet']['Cryo Clamp'][0]
            jet_annual_dict['2023'] += prodTot23['jet']['Pro Jet'][0] + prodTot23['jet']['Quad Jet'][0] + prodTot23['jet']['Micro Jet'][0] + prodTot23['jet']['Cryo Clamp'][0]

            jet_list = [pj_annual, pwj_annual, jet_og_annual, ccmk1_annual, mjmk1_annual, mjmk2_annual, qj_annual]
            year_list = ['2022', '2021', '2020', '2019', '2018', '2017', '2016', '2015', '2014']
            
            colx, coly, colz = st.columns([.2, .6, .2])
            with coly:
                plot_bar_chart_product_seg(format_for_chart_product_seg(jet_annual_dict_seg, 'Total Jet Sales'), 'Total Jet Sales')


            

    elif prod_cat == 'Controllers':

        with col2:
            year = ui.tabs(options=[2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015, 'Historical'], default_value=2025, key='Control Year Select')

        if year == 2025:

            tb_td23, tb_td24 = to_date_product('CC-TB-35')
            ss_td23, ss_td24 = to_date_product('CC-SS-35')
            sm_td23, sm_td24 = to_date_product('CC-SM')
            
            total_cntl_rev = prodTot25['control']['The Button'][1] + prodTot25['control']['Shostarter'][1] + prodTot25['control']['Shomaster'][1]
            
            with col2:
                cola, colb, colc = st.columns(3)
                
                cola.subheader('The Button')
                cola.metric('{:.1f}% of Total Revenue'.format((prodTot25['control']['The Button'][1] / td_25_tot) * 100), '{}'.format(int(prodTot25['control']['The Button'][0])), int(prodTot25['control']['The Button'][0] - tb_td24))
                colb.subheader('Shostarter')
                colb.metric('{:.1f}% of Total Revenue'.format((prodTot25['control']['Shostarter'][1] / td_25_tot) * 100), '{}'.format(int(prodTot25['control']['Shostarter'][0])), int(prodTot25['control']['Shostarter'][0] - ss_td24))
                colc.subheader('Shomaster')
                colc.metric('{:.1f}% of Total Revenue'.format((prodTot25['control']['Shomaster'][1] / td_25_tot) * 100), '{}'.format(int(prodTot25['control']['Shomaster'][0])), int(prodTot25['control']['Shomaster'][0] - sm_td24))
    
                prod_profit_TB, profit_per_unit_TB, prod_profit_last_TB, avg_price_TB, avg_price_last_TB, wholesale_sales_TB, wholesale_percentage_TB, wholesale_delta_TB = calc_prod_metrics(prodTot25['control'], 'The Button', bom_cost_control, prodTot24['control'])
                prod_profit_SS, profit_per_unit_SS, prod_profit_last_SS, avg_price_SS, avg_price_last_SS, wholesale_sales_SS, wholesale_percentage_SS, wholesale_delta_SS = calc_prod_metrics(prodTot25['control'], 'Shostarter', bom_cost_control, prodTot24['control'])
                prod_profit_SM, profit_per_unit_SM, prod_profit_last_SM, avg_price_SM, avg_price_last_SM, wholesale_sales_SM, wholesale_percentage_SM, wholesale_delta_SM = calc_prod_metrics(prodTot25['control'], 'Shomaster', bom_cost_control, prodTot24['control'])
    
                tot_cntl_rev25 = prodTot25['control']['The Button'][1] + prodTot25['control']['Shostarter'][1] + prodTot25['control']['Shomaster'][1]
                tot_cntl_prof25 = prod_profit_TB + prod_profit_SS + prod_profit_SM
                if tot_cntl_rev25 == 0:
                    cntl_prof_margin25 = 0
                else:
                    cntl_prof_margin25 = (tot_cntl_prof25 / tot_cntl_rev25) * 100
    
                cola.metric('**Total Revenue**', '${:,}'.format(int(tot_cntl_rev25)))
                colb.metric('**Profit Margin**', '{:,.2f}%'.format(cntl_prof_margin25))
                colc.metric('**Total Profit**', '${:,}'.format(int(tot_cntl_prof25)))
        
                st.divider()
                display_pie_chart_comp(prodTot25['control'])
                st.divider()
                
                prod_select = ui.tabs(options=['The Button', 'Shostarter', 'Shomaster'], default_value='The Button', key='Controllers')
        
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
    
                prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last, wholesale_sales, wholesale_percentage, wholesale_delta = calc_prod_metrics(prodTot25['control'], prod_select, bom_cost_control, prodTot24['control'])

                # Calculate prior year to-date revenue for selected product
                prior_td_revenue = convert_prod_select(prod_select, 2025)

                # Convert prod_select to the td variable for 2024
                prod_td24 = convert_prod_select_profit(prod_select)
                
                col5.metric('**Revenue**', '${:,.2f}'.format(prodTot25['control'][prod_select][1]), percent_of_change(prior_td_revenue, prodTot25['control'][prod_select][1]))
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), percent_of_change(to_date_product_profit(prod_td24, prior_td_revenue, bom_cost_control[prod_select]), prod_profit))
                col6.metric('**Wholesale**', '{:.2f}%'.format(wholesale_percentage))
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), percent_of_change(avg_price_last, avg_price))
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_control[prod_select]), '')
                
                style_metric_cards()
                
                display_month_data_prod(prod_select, control25, control24) 
        
        elif year == 2024:

            total_cntl_rev = prodTot24['control']['The Button'][1] + prodTot24['control']['Shostarter'][1] + prodTot24['control']['Shomaster'][1]
            
            with col2:
                cola, colb, colc = st.columns(3)
                
                cola.subheader('The Button')
                cola.metric('{:.1f}% of Total Revenue'.format((prodTot24['control']['The Button'][1] / total_24) * 100), '{}'.format(int(prodTot24['control']['The Button'][0])), int(prodTot24['control']['The Button'][0] - prodTot23['control']['The Button'][0]))
                colb.subheader('Shostarter')
                colb.metric('{:.1f}% of Total Revenue'.format((prodTot24['control']['Shostarter'][1] / total_24) * 100), '{}'.format(int(prodTot24['control']['Shostarter'][0])), int(prodTot24['control']['Shostarter'][0] - prodTot23['control']['Shostarter'][0]))
                colc.subheader('Shomaster')
                colc.metric('{:.1f}% of Total Revenue'.format((prodTot24['control']['Shomaster'][1] / total_24) * 100), '{}'.format(int(prodTot24['control']['Shomaster'][0])), int(prodTot24['control']['Shomaster'][0] - prodTot23['control']['Shomaster'][0]))
    
                prod_profit_TB, profit_per_unit_TB, prod_profit_last_TB, avg_price_TB, avg_price_last_TB, wholesale_sales_TB, wholesale_percentage_TB, wholesale_delta_TB = calc_prod_metrics(prodTot24['control'], 'The Button', bom_cost_control, prodTot23['control'])
                prod_profit_SS, profit_per_unit_SS, prod_profit_last_SS, avg_price_SS, avg_price_last_SS, wholesale_sales_SS, wholesale_percentage_SS, wholesale_delta_SS = calc_prod_metrics(prodTot24['control'], 'Shostarter', bom_cost_control, prodTot23['control'])
                prod_profit_SM, profit_per_unit_SM, prod_profit_last_SM, avg_price_SM, avg_price_last_SM, wholesale_sales_SM, wholesale_percentage_SM, wholesale_delta_SM = calc_prod_metrics(prodTot24['control'], 'Shomaster', bom_cost_control, prodTot23['control'])
    
                tot_cntl_rev24 = prodTot24['control']['The Button'][1] + prodTot24['control']['Shostarter'][1] + prodTot24['control']['Shomaster'][1]
                tot_cntl_prof24 = prod_profit_TB + prod_profit_SS + prod_profit_SM
                cntl_prof_margin24 = (tot_cntl_prof24 / tot_cntl_rev24) * 100
    
                cola.metric('**Total Revenue**', '${:,}'.format(int(tot_cntl_rev24)))
                colb.metric('**Profit Margin**', '{:,.2f}%'.format(cntl_prof_margin24))
                colc.metric('**Total Profit**', '${:,}'.format(int(tot_cntl_prof24)))
                
                st.divider()
                display_pie_chart_comp(prodTot24['control'])
                st.divider()
                
                prod_select = ui.tabs(options=['The Button', 'Shostarter', 'Shomaster'], default_value='The Button', key='Controllers')
        
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
    
                prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last, wholesale_sales, wholesale_percentage, wholesale_delta = calc_prod_metrics(prodTot24['control'], prod_select, bom_cost_control, prodTot23['control'])

                # Calculate prior year to-date revenue for selected product
                #prior_td_revenue = convert_prod_select(prod_select, 2024)
    
                
                col5.metric('**Revenue**', '${:,.2f}'.format(prodTot24['control'][prod_select][1]), percent_of_change(prodTot23['control'][prod_select][1], prodTot24['control'][prod_select][1]))
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), percent_of_change(prod_profit_last, prod_profit))
                col6.metric('**Wholesale**', '{:.2f}%'.format(wholesale_percentage))
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), percent_of_change(avg_price_last, avg_price))
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_control[prod_select]), '')
    
                style_metric_cards()
                
                display_month_data_prod(prod_select, control24, control23)

        elif year == 2023:

            total_cntl_rev = prodTot23['control']['The Button'][1] + prodTot23['control']['Shostarter'][1] + prodTot23['control']['Shomaster'][1]
            
            with col2:
                cola, colb, colc = st.columns(3)
                
                cola.subheader('The Button')
                cola.metric('{:.1f}% of Total Revenue'.format((prodTot23['control']['The Button'][1] / total_23) * 100), '{}'.format(int(prodTot23['control']['The Button'][0])), '')
                colb.subheader('Shostarter')
                colb.metric('{:.1f}% of Total Revenue'.format((prodTot23['control']['Shostarter'][1] / total_23) * 100), '{}'.format(int(prodTot23['control']['Shostarter'][0])), '')
                colc.subheader('Shomaster')
                colc.metric('{:.1f}% of Total Revenue'.format((prodTot23['control']['Shomaster'][1] / total_23) * 100), '{}'.format(int(prodTot23['control']['Shomaster'][0])), '')
    
                prod_profit_TB, profit_per_unit_TB, prod_profit_last_TB, avg_price_TB, avg_price_last_TB = calc_prod_metrics(prodTot23['control'], 'The Button', bom_cost_control)
                prod_profit_SS, profit_per_unit_SS, prod_profit_last_SS, avg_price_SS, avg_price_last_SS = calc_prod_metrics(prodTot23['control'], 'Shostarter', bom_cost_control)
                prod_profit_SM, profit_per_unit_SM, prod_profit_last_SM, avg_price_SM, avg_price_last_SM = calc_prod_metrics(prodTot23['control'], 'Shomaster', bom_cost_control)
    
                tot_cntl_rev23 = prodTot23['control']['The Button'][1] + prodTot23['control']['Shostarter'][1] + prodTot23['control']['Shomaster'][1]
                tot_cntl_prof23 = prod_profit_TB + prod_profit_SS + prod_profit_SM
                cntl_prof_margin23 = (tot_cntl_prof23 / tot_cntl_rev23) * 100
    
                cola.metric('**Total Revenue**', '${:,}'.format(int(tot_cntl_rev23)))
                colb.metric('**Profit Margin**', '{:,.2f}%'.format(cntl_prof_margin23))
                colc.metric('**Total Profit**', '${:,}'.format(int(tot_cntl_prof23)))
        
                st.divider()
                display_pie_chart_comp(prodTot23['control'])
                st.divider()
                
                prod_select = ui.tabs(options=['The Button', 'Shostarter', 'Shomaster'], default_value='The Button', key='Controllers')
        
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
    
                prod_profit, profit_per_unit, avg_price, wholesale_sales, wholesale_percentage = calc_prod_metrics(prodTot23['control'], prod_select, bom_cost_control)
    
                col5.metric('**Revenue**', '${:,.2f}'.format(prodTot23['control'][prod_select][1]), '')
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), '')
                col6.metric('**Wholesale**', '{:.2f}%'.format(wholesale_percentage))
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), '')
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_control[prod_select]), '')
    
                style_metric_cards()
                
                display_month_data_prod(prod_select, control23)

        elif year == 2022:

            total_cntl = dmx_cntl_annual['2022'] + lcd_cntl_annual['2022'] + tbmk1_annual['2022'] + tbmk2_annual['2022'] + sm_annual['2022'] + pwr_cntl_annual['2022']
            
            with col2:
                cola, colb, colc = st.columns(3)
                
                cola.subheader('Shomaster')
                cola.metric('', '{}'.format(sm_annual['2022']), sm_annual['2022'] - sm_annual['2021'])
                cola.subheader('The Button MK1')
                cola.metric('', '{}'.format(tbmk1_annual['2022']), tbmk1_annual['2022'] - tbmk1_annual['2021'])
                colb.subheader('LCD Controller')
                colb.metric('', '{}'.format(lcd_cntl_annual['2022']), lcd_cntl_annual['2022'] - lcd_cntl_annual['2021'])
                colb.subheader('Total Controllers')
                colb.metric('', '{}'.format(total_cntl), total_cntl - (dmx_cntl_annual['2021'] + lcd_cntl_annual['2021'] + tbmk1_annual['2021'] + tbmk2_annual['2021'] + sm_annual['2021'] + pwr_cntl_annual['2021']))
                colc.subheader('DMX Controller')
                colc.metric('', '{}'.format(dmx_cntl_annual['2022']), dmx_cntl_annual['2022'] - dmx_cntl_annual['2021'])
                colc.subheader('The Button')
                colc.metric('', '{}'.format(tbmk2_annual['2022']), 'N/A')
    
                style_metric_cards()

        elif year == 2021:

            total_cntl = dmx_cntl_annual['2021'] + lcd_cntl_annual['2021'] + tbmk1_annual['2021'] + tbmk2_annual['2021'] + sm_annual['2021'] + pwr_cntl_annual['2021']
            
            with col2:
                cola, colb, colc = st.columns(3)
                
                cola.subheader('Shomaster')
                cola.metric('', '{}'.format(sm_annual['2021']), sm_annual['2021'] - sm_annual['2020'])
                cola.subheader('The Button MK1')
                cola.metric('', '{}'.format(tbmk1_annual['2021']), tbmk1_annual['2021'] - tbmk1_annual['2020'])
                colb.subheader('LCD Controller')
                colb.metric('', '{}'.format(lcd_cntl_annual['2021']), lcd_cntl_annual['2021'] - lcd_cntl_annual['2020'])
                colb.subheader('Total Controllers')
                colb.metric('', '{}'.format(total_cntl), total_cntl - (dmx_cntl_annual['2020'] + lcd_cntl_annual['2020'] + tbmk1_annual['2020'] + tbmk2_annual['2020'] + sm_annual['2020'] + pwr_cntl_annual['2020']))
                colc.subheader('DMX Controller')
                colc.metric('', '{}'.format(dmx_cntl_annual['2021']), dmx_cntl_annual['2021'] - dmx_cntl_annual['2020'])
                colc.subheader('Power Controller')
                colc.metric('', '{}'.format(pwr_cntl_annual['2021']), pwr_cntl_annual['2021'] - pwr_cntl_annual['2020'])
    
                style_metric_cards()

        elif year == 2020:

            total_cntl = dmx_cntl_annual['2020'] + lcd_cntl_annual['2020'] + tbmk1_annual['2020'] + tbmk2_annual['2020'] + sm_annual['2020'] + pwr_cntl_annual['2020']
            
            with col2:
                cola, colb, colc = st.columns(3)
                
                cola.subheader('LCD Controller')
                cola.metric('', '{}'.format(lcd_cntl_annual['2020']), lcd_cntl_annual['2020'] - lcd_cntl_annual['2019'])
                colb.subheader('DMX Controller')
                colb.metric('', '{}'.format(dmx_cntl_annual['2020']), dmx_cntl_annual['2020'] - dmx_cntl_annual['2019'])
                colb.subheader('Total Controllers')
                colb.metric('', '{}'.format(total_cntl), total_cntl - (dmx_cntl_annual['2019'] + lcd_cntl_annual['2019'] + tbmk1_annual['2019'] + tbmk2_annual['2019'] + sm_annual['2019'] + pwr_cntl_annual['2019']))
                colc.subheader('Power Controller')
                colc.metric('', '{}'.format(pwr_cntl_annual['2020']), pwr_cntl_annual['2020'] - pwr_cntl_annual['2019'])
    
                style_metric_cards()

        elif year == 2019:

            total_cntl = dmx_cntl_annual['2019'] + lcd_cntl_annual['2019'] + tbmk1_annual['2019'] + tbmk2_annual['2019'] + sm_annual['2019'] + pwr_cntl_annual['2019']
            
            with col2:
                cola, colb, colc = st.columns(3)

                cola.subheader('LCD Controller')
                cola.metric('', '{}'.format(lcd_cntl_annual['2019']), lcd_cntl_annual['2019'] - lcd_cntl_annual['2018'])
                colb.subheader('DMX Controller')
                colb.metric('', '{}'.format(dmx_cntl_annual['2019']), dmx_cntl_annual['2019'] - dmx_cntl_annual['2018'])
                colb.subheader('Total Controllers')
                colb.metric('', '{}'.format(total_cntl), total_cntl - (dmx_cntl_annual['2018'] + lcd_cntl_annual['2018'] + tbmk1_annual['2018'] + tbmk2_annual['2018'] + sm_annual['2018'] + pwr_cntl_annual['2018']))
                colc.subheader('Power Controller')
                colc.metric('', '{}'.format(pwr_cntl_annual['2019']), pwr_cntl_annual['2019'] - pwr_cntl_annual['2018'])
    
                style_metric_cards()

        elif year == 2018:

            total_cntl = dmx_cntl_annual['2018'] + lcd_cntl_annual['2018'] + tbmk1_annual['2018'] + tbmk2_annual['2018'] + sm_annual['2018'] + pwr_cntl_annual['2018']
            
            with col2:
                cola, colb, colc = st.columns(3)

                cola.subheader('LCD Controller')
                cola.metric('', '{}'.format(lcd_cntl_annual['2018']), lcd_cntl_annual['2018'] - lcd_cntl_annual['2017'])
                colb.subheader('DMX Controller')
                colb.metric('', '{}'.format(dmx_cntl_annual['2018']), dmx_cntl_annual['2018'] - dmx_cntl_annual['2017'])
                colb.subheader('Total Controllers')
                colb.metric('', '{}'.format(total_cntl), total_cntl - (dmx_cntl_annual['2017'] + lcd_cntl_annual['2017'] + tbmk1_annual['2017'] + tbmk2_annual['2017'] + sm_annual['2017'] + pwr_cntl_annual['2017']))
                colc.subheader('Power Controller')
                colc.metric('', '{}'.format(pwr_cntl_annual['2018']), pwr_cntl_annual['2018'] - pwr_cntl_annual['2017'])
    
                style_metric_cards()

        elif year == 2017:

            total_cntl = dmx_cntl_annual['2017'] + lcd_cntl_annual['2017'] + tbmk1_annual['2017'] + tbmk2_annual['2017'] + sm_annual['2017'] + pwr_cntl_annual['2017']
            
            with col2:
                cola, colb, colc = st.columns(3)
            
                cola.subheader('DMX Controller')
                cola.metric('', '{}'.format(dmx_cntl_annual['2017']), dmx_cntl_annual['2017'] - dmx_cntl_annual['2016'])
                colb.subheader('Power Controller')
                colb.metric('', '{}'.format(pwr_cntl_annual['2017']), pwr_cntl_annual['2017'] - pwr_cntl_annual['2016'])
                colc.subheader('Total Controllers')
                colc.metric('', '{}'.format(total_cntl), total_cntl - (dmx_cntl_annual['2016'] + lcd_cntl_annual['2016'] + tbmk1_annual['2016'] + tbmk2_annual['2016'] + sm_annual['2016'] + pwr_cntl_annual['2016']))

                style_metric_cards()

        elif year == 2016:

            with col2:
                cola, colb, colc = st.columns(3)

                colb.subheader('DMX Controller')
                colb.metric('', '{}'.format(dmx_cntl_annual['2016']), dmx_cntl_annual['2016'] - dmx_cntl_annual['2015'])
    
                style_metric_cards()
                
        elif year == 2015:

            with col2:
                cola, colb, colc = st.columns(3)

                colb.subheader('DMX Controller')
                colb.metric('', '{}'.format(dmx_cntl_annual['2015']), '')
    
                style_metric_cards()

        elif year == 'Historical':

            tb_tot_unit = prodTot25['control']['The Button'][0] + prodTot24['control']['The Button'][0] + prodTot23['control']['The Button'][0] + tbmk2_annual['2022']
            tb_tot_rev = prodTot25['control']['The Button'][1] + prodTot24['control']['The Button'][1] + prodTot23['control']['The Button'][1] + (tbmk2_annual['2022'] * 383)

            ss_tot_unit = prodTot25['control']['Shostarter'][0] + prodTot24['control']['Shostarter'][0] + prodTot23['control']['Shostarter'][0]
            ss_tot_rev = prodTot25['control']['Shostarter'][1] + prodTot24['control']['Shostarter'][1] + prodTot23['control']['Shostarter'][1] 

            sm_tot_unit = prodTot25['control']['Shomaster'][0] + prodTot24['control']['Shomaster'][0] + prodTot23['control']['Shomaster'][0] + sm_annual['2022'] + sm_annual['2021']
            sm_tot_rev = prodTot25['control']['Shomaster'][1] + prodTot24['control']['Shomaster'][1] + prodTot23['control']['Shomaster'][1] + (sm_annual['2022'] * 2880) + (sm_annual['2021'] * 2880)

            dmx_cntl_tot_unit = dmx_cntl_annual['2022'] + dmx_cntl_annual['2021'] + dmx_cntl_annual['2020'] + dmx_cntl_annual['2019'] + dmx_cntl_annual['2018'] + dmx_cntl_annual['2017'] + dmx_cntl_annual['2016'] + dmx_cntl_annual['2015']
            dmx_cntl_tot_rev = (dmx_cntl_annual['2022'] * 450) + (dmx_cntl_annual['2021'] * 450) + (dmx_cntl_annual['2020'] * 450) + (dmx_cntl_annual['2019'] * 450) + (dmx_cntl_annual['2018'] * 450) + (dmx_cntl_annual['2017'] * 450) + (dmx_cntl_annual['2016'] * 450) + (dmx_cntl_annual['2015'] * 450)

            lcd_tot_unit = lcd_cntl_annual['2022'] + lcd_cntl_annual['2021'] + lcd_cntl_annual['2020'] + lcd_cntl_annual['2019'] + lcd_cntl_annual['2018']
            lcd_tot_rev = (lcd_cntl_annual['2022'] * 450) + (lcd_cntl_annual['2021'] * 450) + (lcd_cntl_annual['2020'] * 450) + (lcd_cntl_annual['2019'] * 450) + (lcd_cntl_annual['2018'] * 450)

            pwr_cntl_tot_unit = pwr_cntl_annual['2021'] + pwr_cntl_annual['2020'] + pwr_cntl_annual['2019'] + pwr_cntl_annual['2018'] + pwr_cntl_annual['2017']
            pwr_cntl_tot_rev = (pwr_cntl_annual['2021'] * 260) + (pwr_cntl_annual['2020'] * 260) + (pwr_cntl_annual['2019'] * 260) + (pwr_cntl_annual['2018'] * 260) + (pwr_cntl_annual['2017'] * 260)
            
            tbmk1_tot_unit = tbmk1_annual['2022'] + tbmk1_annual['2021']
            tbmk1_tot_rev = (tbmk1_annual['2022'] * 360) + (tbmk1_annual['2021'] * 360) 


            cola, colb, colc, cold, cole = st.columns(5)

            colb.subheader('The Button')
            colb.metric('**${:,.2f}**'.format(tb_tot_rev), '{}'.format(int(tb_tot_unit)))
            colb.subheader('The Button MKI')
            colb.metric('**${:,.2f}**'.format(tbmk1_tot_rev), '{}'.format(tbmk1_tot_unit))
            colb.subheader('Power Controller')
            colb.metric('**${:,.2f}**'.format(pwr_cntl_tot_rev), '{}'.format(pwr_cntl_tot_unit))

            colc.subheader('Shostarter')
            colc.metric('**${:,.2f}**'.format(ss_tot_rev), '{}'.format(int(ss_tot_unit)))
            colc.subheader('LCD Controller')
            colc.metric('**${:,.2f}**'.format(lcd_tot_rev), '{}'.format(lcd_tot_unit))

            cold.subheader('Shomaster')
            cold.metric('**${:,.2f}**'.format(sm_tot_rev), '{}'.format(int(sm_tot_unit)))
            cold.subheader('DMX Controller')
            cold.metric('**${:,.2f}**'.format(dmx_cntl_tot_rev), '{}'.format(dmx_cntl_tot_unit))
            cold.subheader('Total Controllers')
            cold.metric('**${:,.2f}**'.format(tbmk1_tot_rev + pwr_cntl_tot_rev + lcd_tot_rev + dmx_cntl_tot_rev + sm_tot_rev + ss_tot_rev + tb_tot_rev), '{}'.format(int(tbmk1_tot_unit + pwr_cntl_tot_unit + lcd_tot_unit + dmx_cntl_tot_unit + sm_tot_unit + ss_tot_unit + tb_tot_unit)))

            style_metric_cards()

            cntl_annual_dict = {'2025': 0, '2024': 0, '2023': 0, '2022': 0, '2021': 0, '2020': 0, '2019': 0, '2018': 0, '2017': 0, '2016': 0, '2015': 0, '2014': 0}
            cntl_annual_dict_seg = {'2025': {'The Button': prodTot25['control']['The Button'][0], 'Shostarter': prodTot25['control']['Shostarter'][0], 'Shomaster': prodTot25['control']['Shomaster'][0]}, '2024': {'The Button': prodTot24['control']['The Button'][0], 'Shostarter': prodTot24['control']['Shostarter'][0], 'Shomaster': prodTot24['control']['Shomaster'][0]}, '2023': {'The Button': prodTot23['control']['The Button'][0], 'Shostarter': prodTot23['control']['Shostarter'][0], 'Shomaster': prodTot23['control']['Shomaster'][0]}, '2022': {'The Button': tbmk2_annual['2022'], 'The Button MKI': tbmk1_annual['2022'], 'Shomaster': sm_annual['2022'], 'LCD Controller': lcd_cntl_annual['2022'], 'DMX Controller': dmx_cntl_annual['2022']}, '2021': {'Power Controller': pwr_cntl_annual['2021'], 'The Button MKI': tbmk1_annual['2021'], 'Shomaster': sm_annual['2021'], 'LCD Controller': lcd_cntl_annual['2021'], 'DMX Controller': dmx_cntl_annual['2021']}, '2020': {'Power Controller': pwr_cntl_annual['2020'], 'LCD Controller': lcd_cntl_annual['2020'], 'DMX Controller': dmx_cntl_annual['2020']}, '2019': {'Power Controller': pwr_cntl_annual['2019'], 'LCD Controller': lcd_cntl_annual['2019'], 'DMX Controller': dmx_cntl_annual['2019']}, '2018': {'Power Controller': pwr_cntl_annual['2018'], 'LCD Controller': lcd_cntl_annual['2018'], 'DMX Controller': dmx_cntl_annual['2018']}, '2017': {'Power Controller': pwr_cntl_annual['2017'], 'DMX Controller': dmx_cntl_annual['2017']}, '2016': {'DMX Controller': dmx_cntl_annual['2016']}, '2015': {'DMX Controller': dmx_cntl_annual['2015']}}
            cntl_annual_dict['2025'] += prodTot25['control']['The Button'][0] + prodTot25['control']['Shostarter'][0] + prodTot25['control']['Shomaster'][0] 
            cntl_annual_dict['2024'] += prodTot24['control']['The Button'][0] + prodTot24['control']['Shostarter'][0] + prodTot24['control']['Shomaster'][0]
            cntl_annual_dict['2023'] += prodTot23['control']['The Button'][0] + prodTot23['control']['Shostarter'][0] + prodTot23['control']['Shomaster'][0]

            cntl_list = [tbmk1_annual, pwr_cntl_annual, lcd_cntl_annual, dmx_cntl_annual, tbmk2_annual, sm_annual]
            year_list = ['2022', '2021', '2020', '2019', '2018', '2017', '2016', '2015', '2014']
            
            colx, coly, colz = st.columns([.2, .6, .2])
            with coly:
                plot_bar_chart_product_seg(format_for_chart_product_seg(cntl_annual_dict_seg, 'Total Controller Sales'), 'Total Controller Sales')
            

    elif prod_cat == 'Handhelds':

        td_8nc23, td_8nc24 = to_date_product('CC-HCCMKII-08-NC')
        td_8tc23, td_8tc24 = to_date_product('CC-HCCMKII-08-TC')
        td_15nc23, td_15nc24 = to_date_product('CC-HCCMKII-15-NC')
        td_15tc23, td_15tc24 = to_date_product('CC-HCCMKII-15-TC')

        with col2:
            year = ui.tabs(options=[2025, 2024, 2023, 'Historical'], default_value=2025, key='Handheld Year Select')

        if year == 2025:

            total_hh_rev = prodTot25['handheld']['8FT - No Case'][1] + prodTot25['handheld']['8FT - Travel Case'][1] + prodTot25['handheld']['15FT - No Case'][1] + prodTot25['handheld']['15FT - Travel Case'][1]
            
            with col2:
                cola, colb, colc, cold = st.columns(4)
        
                cola.subheader('8FT NC')
                cola.metric('{:.1f}% of Total Revenue'.format((prodTot25['handheld']['8FT - No Case'][1] / td_25_tot) * 100), '{}'.format(int(prodTot25['handheld']['8FT - No Case'][0])), '{}'.format(int(prodTot25['handheld']['8FT - No Case'][0] - td_8nc24)))
                cola.metric('', '${:,}'.format(int(prodTot25['handheld']['8FT - No Case'][1])), percent_of_change(convert_prod_select('8FT - No Case', 2025), prodTot25['handheld']['8FT - No Case'][1]))
                colb.subheader('8FT TC')
                colb.metric('{:.1f}% of Total Revenue'.format((prodTot25['handheld']['8FT - Travel Case'][1] / td_25_tot) * 100), '{}'.format(int(prodTot25['handheld']['8FT - Travel Case'][0])),  '{}'.format(int(prodTot25['handheld']['8FT - Travel Case'][0] - td_8tc24)))
                colb.metric('', '${:,}'.format(int(prodTot25['handheld']['8FT - Travel Case'][1])), percent_of_change(convert_prod_select('8FT - Travel Case', 2025), prodTot25['handheld']['8FT - Travel Case'][1]))
                colc.subheader('15FT NC')
                colc.metric('{:.1f}% of Total Revenue'.format((prodTot25['handheld']['15FT - No Case'][1] / td_25_tot) * 100), '{}'.format(int(prodTot25['handheld']['15FT - No Case'][0])),  '{}'.format(int(prodTot25['handheld']['15FT - No Case'][0] - td_15nc24)))
                colc.metric('', '${:,}'.format(int(prodTot25['handheld']['15FT - No Case'][1])), percent_of_change(convert_prod_select('15FT - No Case', 2025), prodTot25['handheld']['15FT - No Case'][1]))
                cold.subheader('15FT TC')
                cold.metric('{:.1f}% of Total Revenue'.format((prodTot25['handheld']['15FT - Travel Case'][1] / td_25_tot) * 100), '{}'.format(int(prodTot25['handheld']['15FT - Travel Case'][0])),  '{}'.format(int(prodTot25['handheld']['15FT - Travel Case'][0] - td_15tc24)))
                cold.metric('', '${:,}'.format(int(prodTot25['handheld']['15FT - Travel Case'][1])), percent_of_change(convert_prod_select('15FT - Travel Case', 2025), prodTot25['handheld']['15FT - Travel Case'][1]))
    
    
                prod_profit_8NC, profit_per_unit_8NC, prod_profit_last_8NC, avg_price_8NC, avg_price_last_8NC = calc_prod_metrics(prodTot25['handheld'], '8FT - No Case', bom_cost_hh, prodTot24['handheld'])
                prod_profit_8TC, profit_per_unit_8TC, prod_profit_last_8TC, avg_price_8TC, avg_price_last_8TC = calc_prod_metrics(prodTot25['handheld'], '8FT - Travel Case', bom_cost_hh, prodTot24['handheld'])
                prod_profit_15NC, profit_per_unit_15NC, prod_profit_last_15NC, avg_price_15NC, avg_price_last_15NC = calc_prod_metrics(prodTot25['handheld'], '15FT - No Case', bom_cost_hh, prodTot24['handheld'])
                prod_profit_15TC, profit_per_unit_15TC, prod_profit_last_15TC, avg_price_15TC, avg_price_last_15TC = calc_prod_metrics(prodTot25['handheld'], '15FT - Travel Case', bom_cost_hh, prodTot24['handheld'])
                
                tot_hh_rev25 = prodTot25['handheld']['8FT - No Case'][1] + prodTot25['handheld']['8FT - Travel Case'][1] + prodTot25['handheld']['15FT - No Case'][1] + prodTot25['handheld']['15FT - Travel Case'][1]
                tot_hh_prof25 = prod_profit_8NC + prod_profit_8TC + prod_profit_15NC + prod_profit_15TC
                prof_margin25 = (tot_hh_prof25 / tot_hh_rev25) * 100
                
                colx, coly, colz = st.columns(3)
    
                colx.metric('**Total Revenue**', '${:,}'.format(int(tot_hh_rev25)))
                coly.metric('**Profit Margin**', '{:,.2f}%'.format(prof_margin25))
                colz.metric('**Total Profit**', '${:,}'.format(int(tot_hh_prof25)))
            
                st.divider()
                display_pie_chart_comp(prodTot25['handheld'])
                st.divider()
        
                prod_select = ui.tabs(options=['8FT - No Case', '8FT - Travel Case', '15FT - No Case', '15FT - Travel Case'], default_value='8FT - No Case', key='Handhelds')
        
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
    
                prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last = calc_prod_metrics(prodTot25['handheld'], prod_select, bom_cost_hh, prodTot24['handheld'])

                # Calculate prior year to-date revenue for selected product
                prior_td_revenue = convert_prod_select(prod_select, 2025)

                # Convert prod_select to the td variable for 2024
                prod_td24 = convert_prod_select_profit(prod_select)
                
                
                col5.metric('**Revenue**', '${:,.2f}'.format(int(prodTot25['handheld'][prod_select][1])), percent_of_change(prior_td_revenue, prodTot25['handheld'][prod_select][1]))
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), percent_of_change(to_date_product_profit(prod_td24, prior_td_revenue, bom_cost_hh[prod_select]), prod_profit))
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), percent_of_change(avg_price_last, avg_price))
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_hh[prod_select]), '')        
    
                style_metric_cards()
                
                display_month_data_prod(prod_select, handheld25, handheld24)
        
        elif year == 2024:

            total_hh_rev = prodTot24['handheld']['8FT - No Case'][1] + prodTot24['handheld']['8FT - Travel Case'][1] + prodTot24['handheld']['15FT - No Case'][1] + prodTot24['handheld']['15FT - Travel Case'][1]
            
            with col2:
                
                cola, colb, colc, cold = st.columns(4)
        
                cola.subheader('8FT NC')
                cola.metric('{:.1f}% of Total Revenue'.format((prodTot24['handheld']['8FT - No Case'][1] / total_24) * 100), '{}'.format(int(prodTot24['handheld']['8FT - No Case'][0])), '{}'.format(int(prodTot24['handheld']['8FT - No Case'][0] - prodTot23['handheld']['8FT - No Case'][0])))
                cola.metric('', '${:,}'.format(int(prodTot24['handheld']['8FT - No Case'][1])), percent_of_change(prodTot23['handheld']['8FT - No Case'][1], prodTot24['handheld']['8FT - No Case'][1]))
                colb.subheader('8FT TC')
                colb.metric('{:.1f}% of Total Revenue'.format((prodTot24['handheld']['8FT - Travel Case'][1] / total_24) * 100), '{}'.format(int(prodTot24['handheld']['8FT - Travel Case'][0])),  '{}'.format(int(prodTot24['handheld']['8FT - Travel Case'][0] - prodTot23['handheld']['8FT - Travel Case'][0])))
                colb.metric('', '${:,}'.format(int(prodTot24['handheld']['8FT - Travel Case'][1])), percent_of_change(prodTot23['handheld']['8FT - Travel Case'][1], prodTot24['handheld']['8FT - Travel Case'][1]))
                colc.subheader('15FT NC')
                colc.metric('{:.1f}% of Total Revenue'.format((prodTot24['handheld']['15FT - No Case'][1] / total_24) * 100), '{}'.format(int(prodTot24['handheld']['15FT - No Case'][0])),  '{}'.format(int(prodTot24['handheld']['15FT - No Case'][0] - prodTot23['handheld']['15FT - No Case'][0])))
                colc.metric('', '${:,}'.format(int(prodTot24['handheld']['15FT - No Case'][1])), percent_of_change(prodTot23['handheld']['15FT - No Case'][1], prodTot24['handheld']['15FT - No Case'][1]))
                cold.subheader('15FT TC')
                cold.metric('{:.1f}% of Total Revenue'.format((prodTot24['handheld']['15FT - Travel Case'][1] / total_24) * 100), '{}'.format(int(prodTot24['handheld']['15FT - Travel Case'][0])),  '{}'.format(int(prodTot24['handheld']['15FT - Travel Case'][0] - prodTot23['handheld']['15FT - Travel Case'][0])))
                cold.metric('', '${:,}'.format(int(prodTot24['handheld']['15FT - Travel Case'][1])), percent_of_change(prodTot23['handheld']['15FT - Travel Case'][1], prodTot24['handheld']['15FT - Travel Case'][1]))
    
    
                prod_profit_8NC, profit_per_unit_8NC, prod_profit_last_8NC, avg_price_8NC, avg_price_last_8NC = calc_prod_metrics(prodTot24['handheld'], '8FT - No Case', bom_cost_hh, prodTot23['handheld'])
                prod_profit_8TC, profit_per_unit_8TC, prod_profit_last_8TC, avg_price_8TC, avg_price_last_8TC = calc_prod_metrics(prodTot24['handheld'], '8FT - Travel Case', bom_cost_hh, prodTot23['handheld'])
                prod_profit_15NC, profit_per_unit_15NC, prod_profit_last_15NC, avg_price_15NC, avg_price_last_15NC = calc_prod_metrics(prodTot24['handheld'], '15FT - No Case', bom_cost_hh, prodTot23['handheld'])
                prod_profit_15TC, profit_per_unit_15TC, prod_profit_last_15TC, avg_price_15TC, avg_price_last_15TC = calc_prod_metrics(prodTot24['handheld'], '15FT - Travel Case', bom_cost_hh, prodTot23['handheld'])
                
                tot_hh_rev24 = prodTot24['handheld']['8FT - No Case'][1] + prodTot24['handheld']['8FT - Travel Case'][1] + prodTot24['handheld']['15FT - No Case'][1] + prodTot24['handheld']['15FT - Travel Case'][1]
                tot_hh_prof24 = prod_profit_8NC + prod_profit_8TC + prod_profit_15NC + prod_profit_15TC
                prof_margin24 = (tot_hh_prof24 / tot_hh_rev24) * 100
                
                colx, coly, colz = st.columns(3)
    
                colx.metric('**Total Revenue**', '${:,}'.format(int(tot_hh_rev24)))
                coly.metric('**Profit Margin**', '{:,.2f}%'.format(prof_margin24))
                colz.metric('**Total Profit**', '${:,}'.format(int(tot_hh_prof24)))
            
                st.divider()
                display_pie_chart_comp(prodTot24['handheld'])
                st.divider()
        
                prod_select = ui.tabs(options=['8FT - No Case', '8FT - Travel Case', '15FT - No Case', '15FT - Travel Case'], default_value='8FT - No Case', key='Handhelds')
        
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
    
                prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last = calc_prod_metrics(prodTot24['handheld'], prod_select, bom_cost_hh, prodTot23['handheld'])

                # Calculate prior year to-date revenue for selected product
                #prior_td_revenue = convert_prod_select(prod_select, 2024)
                
                
                col5.metric('**Revenue**', '${:,.2f}'.format(int(prodTot24['handheld'][prod_select][1])), percent_of_change(prodTot23['handheld'][prod_select][1], prodTot24['handheld'][prod_select][1]))
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), percent_of_change(prod_profit_last, prod_profit))
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), percent_of_change(avg_price_last, avg_price))
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_hh[prod_select]), '')        
    
                style_metric_cards()
                
                display_month_data_prod(prod_select, handheld24, handheld23)
            
        elif year == 2023:

            total_hh_rev = prodTot23['handheld']['8FT - No Case'][1] + prodTot23['handheld']['8FT - Travel Case'][1] + prodTot23['handheld']['15FT - No Case'][1] + prodTot23['handheld']['15FT - Travel Case'][1]
            
            with col2:
                
                cola, colb, colc, cold = st.columns(4)
        
                cola.subheader('8FT NC')
                cola.metric('{:.1f}% of Total Revenue'.format((prodTot23['handheld']['8FT - No Case'][1] / total_23) * 100), '{}'.format(int(prodTot23['handheld']['8FT - No Case'][0]), ''))
                cola.metric('', '${:,}'.format(int(prodTot23['handheld']['8FT - No Case'][1])), '')
                colb.subheader('8FT TC')
                colb.metric('{:.1f}% of Total Revenue'.format((prodTot23['handheld']['8FT - Travel Case'][1] / total_23) * 100), '{}'.format(int(prodTot23['handheld']['8FT - Travel Case'][0]),  ''))
                colb.metric('', '${:,}'.format(int(prodTot23['handheld']['8FT - Travel Case'][1])), '')
                colc.subheader('15FT NC')
                colc.metric('{:.1f}% of Total Revenue'.format((prodTot23['handheld']['15FT - No Case'][1] / total_23) * 100), '{}'.format(int(prodTot23['handheld']['15FT - No Case'][0]),  ''))
                colc.metric('', '${:,}'.format(int(prodTot23['handheld']['15FT - No Case'][1])), '')
                cold.subheader('15FT TC')
                cold.metric('{:.1f}% of Total Revenue'.format((prodTot23['handheld']['15FT - Travel Case'][1] / total_23) * 100), '{}'.format(int(prodTot23['handheld']['15FT - Travel Case'][0]),  ''))
                cold.metric('', '${:,}'.format(int(prodTot23['handheld']['15FT - Travel Case'][1])), '')
    
    
                prod_profit_8NC, profit_per_unit_8NC, avg_price_8NC = calc_prod_metrics(prodTot23['handheld'], '8FT - No Case', bom_cost_hh)
                prod_profit_8TC, profit_per_unit_8TC, avg_price_8TC = calc_prod_metrics(prodTot23['handheld'], '8FT - Travel Case', bom_cost_hh)
                prod_profit_15NC, profit_per_unit_15NC, avg_price_15NC = calc_prod_metrics(prodTot23['handheld'], '15FT - No Case', bom_cost_hh)
                prod_profit_15TC, profit_per_unit_15TC, avg_price_15TC = calc_prod_metrics(prodTot23['handheld'], '15FT - Travel Case', bom_cost_hh)
                
                tot_hh_rev23 = prodTot23['handheld']['8FT - No Case'][1] + prodTot23['handheld']['8FT - Travel Case'][1] + prodTot23['handheld']['15FT - No Case'][1] + prodTot23['handheld']['15FT - Travel Case'][1]
                tot_hh_prof23 = prod_profit_8NC + prod_profit_8TC + prod_profit_15NC + prod_profit_15TC
                prof_margin23 = (tot_hh_prof23 / tot_hh_rev23) * 100
                
                colx, coly, colz = st.columns(3)
    
                colx.metric('**Total Revenue**', '${:,}'.format(int(tot_hh_rev23)))
                coly.metric('**Profit Margin**', '{:,.2f}%'.format(prof_margin23))
                colz.metric('**Total Profit**', '${:,}'.format(int(tot_hh_prof23)))   
    
                st.divider()
                display_pie_chart_comp(prodTot23['handheld'])
                st.divider()
        
                prod_select = ui.tabs(options=['8FT - No Case', '8FT - Travel Case', '15FT - No Case', '15FT - Travel Case'], default_value='8FT - No Case', key='Handhelds')
        
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
        
                prod_profit = (prodTot23['handheld'][prod_select][1]) - (prodTot23['handheld'][prod_select][0] * bom_cost_hh[prod_select])
                avg_price = prodTot23['handheld'][prod_select][1] / prodTot23['handheld'][prod_select][0]
                profit_per_unit = avg_price - bom_cost_hh[prod_select]
                
                col5.metric('**Revenue**', '${:,.2f}'.format(prodTot23['handheld'][prod_select][1]), '')
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), '')
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), '')
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_hh[prod_select]), '')        
                
                style_metric_cards()
                
                display_month_data_prod(prod_select, handheld23)

        elif year == 'Historical':

            mk1_tot = 0
            mk2_tot = prodTot25['handheld']['8FT - No Case'][0] + prodTot25['handheld']['8FT - Travel Case'][0] + prodTot25['handheld']['15FT - No Case'][0] + prodTot25['handheld']['15FT - Travel Case'][0] + prodTot24['handheld']['8FT - No Case'][0] + prodTot24['handheld']['8FT - Travel Case'][0] + prodTot24['handheld']['15FT - No Case'][0] + prodTot24['handheld']['15FT - Travel Case'][0] + prodTot23['handheld']['8FT - No Case'][0] + prodTot23['handheld']['8FT - Travel Case'][0] + prodTot23['handheld']['15FT - No Case'][0] + prodTot23['handheld']['15FT - Travel Case'][0]

            for key, val in hhmk1_annual.items():
                mk1_tot += val
            for key, val in hhmk2_annual.items():
                mk2_tot += val

            with col2:
                
                cola, colb, colc = st.columns(3)
        
                cola.metric('**2022**', '{}'.format(hhmk1_annual['2022'] + hhmk2_annual['2022']), (hhmk1_annual['2022'] + hhmk2_annual['2022']) - (hhmk1_annual['2021'] + hhmk2_annual['2021']))
                cola.metric('**2019**', '{}'.format(hhmk1_annual['2019'] + hhmk2_annual['2019']), (hhmk1_annual['2019'] + hhmk2_annual['2019']) - hhmk1_annual['2018'])
                cola.metric('**2016**', '{}'.format(hhmk1_annual['2016']), hhmk1_annual['2016'] - hhmk1_annual['2015'])
                cola.metric('**Total MKII**', '{}'.format(int(mk2_tot)), '')
     
                colb.metric('**2021**', '{}'.format(hhmk1_annual['2021'] + hhmk2_annual['2021']),  (hhmk1_annual['2021'] + hhmk2_annual['2021']) - (hhmk1_annual['2020'] + hhmk2_annual['2020']))
                colb.metric('**2018**', '{}'.format(hhmk1_annual['2018']), hhmk1_annual['2018'] - hhmk1_annual['2017'])
                colb.metric('**2015**', '{}'.format(hhmk1_annual['2015']), hhmk1_annual['2015'] - hhmk1_annual['2014'])
                colb.metric('**2013**', '{}'.format(hhmk1_annual['2013']), '')
                colb.metric('**Total Handhelds Sold**', '{}'.format(int(mk1_tot + mk2_tot)), '')
                
                colc.metric('**2020**', '{}'.format(hhmk1_annual['2020'] + hhmk2_annual['2020']),  (hhmk1_annual['2020'] + hhmk2_annual['2020']) - (hhmk1_annual['2019'] + hhmk2_annual['2019']))
                colc.metric('**2017**', '{}'.format(hhmk1_annual['2017']), hhmk1_annual['2017'] - hhmk1_annual['2016'])
                colc.metric('**2014**', '{}'.format(hhmk1_annual['2014']), hhmk1_annual['2014'] - hhmk1_annual['2013'])
                colc.metric('**Total MKI**', '{}'.format(mk1_tot), '')

                style_metric_cards()

                hh_dict = {}
                
                hh_dict['2025'] = prodTot25['handheld']['8FT - No Case'][0] + prodTot25['handheld']['8FT - Travel Case'][0] + prodTot25['handheld']['15FT - No Case'][0] + prodTot25['handheld']['15FT - Travel Case'][0]
                hh_dict['2024'] = prodTot24['handheld']['8FT - No Case'][0] + prodTot24['handheld']['8FT - Travel Case'][0] + prodTot24['handheld']['15FT - No Case'][0] + prodTot24['handheld']['15FT - Travel Case'][0]
                hh_dict['2023'] = prodTot23['handheld']['8FT - No Case'][0] + prodTot23['handheld']['8FT - Travel Case'][0] + prodTot23['handheld']['15FT - No Case'][0] + prodTot23['handheld']['15FT - Travel Case'][0]
                
                for year, sales in hhmk1_annual.items():
                    hh_dict[year] = sales

                for year, sales in hhmk2_annual.items():
                    hh_dict[year] += sales


                hh_dict = {key: hh_dict[key] for key in reversed(hh_dict)}

                plot_bar_chart_hh(format_for_chart_hh(hh_dict))

        
    elif prod_cat == 'Hoses':

        with col2:
            hose_scope = ui.tabs(options=['Overview', 'Profit'], default_value='Overview', key='Hose Metric Scope')

        if hose_scope == 'Overview':
            cola, colb, colc = st.columns([.2, .6, .2])
            with colb:
                display_hose_data(hose_detail25, hose_detail24, hose_detail23)
                
        if hose_scope == 'Profit':
            
            cola, colb, colc = st.columns([.2, .6, .2])
            with colb:
                display_hose_data_profit(hose_detail25, hose_detail24, hose_detail23)
          
    elif prod_cat == 'Accessories':

        with col2:
            acc_scope = ui.tabs(options=['Overview', 'Profit'], default_value='Overview', key='Acc Metric Scope')

        cola, colb, colc, cold, cole, colf, colg = st.columns([.1,.1,.2,.2,.2,.1,.1])
        colc.subheader('2025')
        cold.subheader('2024')
        cole.subheader('2023')

        if acc_scope == 'Overview':

            display_acc_data()

        if acc_scope == 'Profit':

            display_acc_data_profit()


    elif prod_cat == 'MagicFX':
        
        with col2:
            year = ui.tabs(options=[2025, 2024, 2023], default_value=2025, key='Products Year Select')

        cola, colx, coly, colz, colb = st.columns([.15, .23, .23, .23, .15], gap='medium')

        if year == 2025:

            idx = 0
            
            count, magic_dict = magic_sales('2025')

            group1 = [1, 4, 7, 10]
            group2 = [2, 5, 8, 11]
            group3 = [3, 6, 9, 12]
            
            for key, val in magic_dict.items():
                if val[0] >= 1 and key != 'MFX-ECO2JET-BKT':
                    if idx in group1:
                        colx.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))
                    elif idx in group2:
                        coly.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))    
                    else:
                        colz.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))

                    idx += 1
            
        if year == 2024:

            idx = 0
            
            count, magic_dict = magic_sales('2024')

            
            for key, val in magic_dict.items():
                if val[0] >= 1:
                    if 0 <= idx <= 5:
                        colx.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))
                    elif 5 < idx <= 10:
                        coly.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))    
                    else:
                        colz.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))

                    idx += 1

        if year == 2023:

            idx = 0
            
            count, magic_dict = magic_sales('2023')
            for key, val in magic_dict.items():
                if val[0] >= 1:
                    if 0 <= idx <= 5:
                        colx.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))
                    elif 5 < idx <= 10:
                        coly.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))    
                    else:
                        colz.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))

                    idx += 1
            
        style_metric_cards()
