import streamlit as st

st.set_page_config(page_title='Magic FX USA', 
           page_icon='data/Images/MFX_favicon.png',
                   layout='wide',
           initial_sidebar_state='collapsed')

import pandas as pd
import plotly.express as px
from PIL import Image
import numpy as np
#from collections import ChainMap, defaultdict
#import difflib
import altair as alt
import matplotlib.pyplot as plt
#from operator import itemgetter
from datetime import datetime, timedelta, date
import openpyxl
import streamlit_shadcn_ui as ui
#from streamlit_extras.metric_cards import style_metric_cards
from streamlit_option_menu import option_menu
#from fpdf import FPDF
import base64

from data.load import load_all_data
from modules.customer_details import render_customer
from modules.leaderboards import render_leaderboards
#from modules.leaderboards import render_customer_spend_leaderboard

from logic.analytics import (
    percent_of_change, 
    percent_of_sales, 
    num_to_month, 
    month_to_num, 
    get_monthly_sales_wvr, 
    beginning_of_year, 
    get_monthly_sales_wvr_ytd, 
    get_monthly_sales_v2, 
    get_monthly_sales_ytd, 
    calc_monthly_totals_v2, 
    extract_transaction_data, 
    calc_hist_metrics,
    quarterly_sales,
    wholesale_retail_totals,
    to_date_revenue,
    magic_sales_data,
    daily_sales,
    hist_cust_data,
    hist_annual_sales
)

from logic.products import (
    extract_handheld_data, 
    extract_hose_data, 
    extract_acc_data, 
    extract_control_data, 
    extract_jet_data, 
    collect_product_data, 
    organize_hose_data, 
    magic_sales,
    product_annual_totals,
    calc_prod_metrics,
    annual_product_totals,
    to_date_product,
    to_date_product_rev,
    profit_by_type,
    to_date_product_profit,
    convert_prod_select,
    convert_prod_select_profit,
    hist_product_data,
    prep_data_context
)

from modules.product_reports import (
    display_month_data_prod,
    display_hose_data,
    display_hose_data_profit,
    display_acc_data,
    render_products
)

from ui.charts import (
    format_for_chart_hh, 
    plot_bar_chart_hh, 
    format_for_chart, 
    plot_bar_chart, 
    display_daily_plot, 
    format_for_chart_ms, 
    plot_bar_chart_ms, 
    plot_bar_chart_ms_comp,
    format_for_pie_chart,
    format_for_line_graph,
    display_pie_chart_comp,
    plot_annual_comparison,
    format_for_chart_product, 
    plot_bar_chart_product,
    format_for_chart_product_seg,
    plot_bar_chart_product_seg
)

from modules.dashboard import (
    display_month_data_x,
    display_metrics, 
    render_dashboard
)

from ui.components import (
    style_metric_cards,
    apply_selectbox_theme_fix
)




def main():


    # ----------------
    # SET HEADER IMAGE
    # ----------------

    image = Image.open('data/Images/Magic_FX_Logo_PNG@10x.png')
    col1, col2, col3 = st.columns([1.3,1.4,1.3])
    col2.image(image, 
            use_container_width=True)

    st.header('')

    
    # -----------------
    # CREATE DATE LISTS
    # -----------------
    
    months = ['All', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    months_x = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    years = ['2022', '2023', '2024', '2025', '2026']


    # ----------------------------------
    # LOAD IN ALL DATA FROM data.load.py
    # ----------------------------------
    
    df, df_quotes, df_cogs, df_shipstat_23, df_shipstat_24, df_qb, df_hsd, df_hist, unique_customer_list, master_customer_list, wholesale_list = load_all_data()
    
    # --------------------------
    # MAKE LIST OF PRODUCT TYPES
    # --------------------------
    
    product_types = ['Jets', 'Controllers', 'Hoses', 'Accessories', 'Handhelds']
    

    # ---------------------
    # GENERATE SIDEBAR MENU 
    # ---------------------
    
    task_select = ''
    #task_choice = ''
    
    st.markdown("""
    <style>
        [data-testid=stSidebar] {
            background-color: #121212;
        }
    </style>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        task_choice = option_menu(None, ["Dashboard", "Product Reports", "Customer Details", "Leaderboards"], 
            icons=['house', 'projector', 'person-circle', 'trophy'], 
            menu_icon="cast", default_index=0, orientation="vertical",
            styles={
                "container": {"padding": "0!important"},
                "icon": {"color": "red", "font-size": "18px"}, 
                "nav-link": {"color": "white", "font-size": "22px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "gray"},
                }
            )
    
    apply_selectbox_theme_fix()
    
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

    # ----------------------------------------------
    # MAKE VARIABLES FOR REAL TIME DATA CALCULATIONS
    # ----------------------------------------------
    
    def beginning_of_year(dt: datetime) -> datetime:
        return datetime(dt.year, 1, 1)
    
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)
    two_years_ago = today - timedelta(days=730)
    three_years_ago = today - timedelta(days=1095)
    four_years_ago = today - timedelta(days=1460)
    

    # -----------------------------
    # CALCULATE MAGIC FX SALES DATA
    # -----------------------------
    
    mfx_rev, mfx_costs, mfx_profit = magic_sales_data()
    

    # ---------------------
    # HISTORICAL SALES DATA
    # ---------------------
    
    sales13, sales14, sales15, sales16, sales17, sales18, sales19, sales20, sales21, sales22 = hist_annual_sales()  


    # ----------------------------------
    # REAL-TIME TO-DATE DATA CALCULATION
    # ----------------------------------
    
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


    # ---------------------------
    # CALCULATE ANNUAL SALES DATA
    # ---------------------------
    
    sales_dict_23 = get_monthly_sales_v2(df, 2023)
    total_23, web_23, ful_23, avg_23, magic23 = calc_monthly_totals_v2(sales_dict_23)
    
    sales_dict_24 = get_monthly_sales_v2(df, 2024)
    total_24, web_24, ful_24, avg_24, magic24 = calc_monthly_totals_v2(sales_dict_24)
    
    sales_dict_25 = get_monthly_sales_v2(df, 2025)
    total_25, web_25, ful_25, avg_25, magic25 = calc_monthly_totals_v2(sales_dict_25)

    sales_dict_26 = get_monthly_sales_v2(df, 2026)
    total_26, web_26, ful_26, avg_26, magic26 = calc_monthly_totals_v2(sales_dict_26)


    # -----------------------------------
    # CREATE PRODUCT REPORTS DATA CONTEXT
    # -----------------------------------

    product_ctx = prep_data_context()


    # -------
    # MODULES
    # -------
    
    if task_choice == 'Dashboard':
    
    
        # ------------------------------
        # COMPILE DATA FOR SALES REPORTS 
        # ------------------------------
        
        td_sales26, td_sales25, td_sales24, td_sales23 = get_monthly_sales_ytd()
        
        total_22 = 1483458.64
        avg_22 = 147581.12
        trans_22 = 1266
        trans_avg_22 = 126.6
        sales_dict_22 = {'January': [[0, 1], [0, 1], [0]], 
                         'February': [[0, 1], [7647.42, 25], [0]], 
                         'March': [[48547.29, 80], [48457.28, 30], [0]], 
                         'April': [[69081.04, 86], [69081.05, 30], [0]], 
                         'May': [[64976.18, 72], [64976.18, 40], [0]], 
                         'June': [[88817.15, 90], [88817.15, 51], [0]], 
                         'July': [[104508.24, 86], [104508.24, 30], [0]], 
                         'August': [[74166.78, 94], [74166.78, 50], [0]], 
                         'September': [[68018.74, 99], [68018.74, 50], [0]], 
                         'October': [[86874.13, 126], [86874.13, 40], [0]], 
                         'November': [[57760.81, 77], [57760.82, 30], [0]], 
                         'December': [[75155.19, 64], [75155.20, 30], [0]]}


    
        # ---------------------
        # RENDER DASHBOARD PAGE 
        # ---------------------
        render_dashboard(td_26, td_25, td_24, td_23, td_22, sales_dict_26, sales_dict_25, sales_dict_24, sales_dict_23, td_sales25, td_sales24, td_sales23)

    
    if task_choice == 'Product Reports':
 
        # ----------------------
        # RENDER PRODUCT REPORTS 
        # ----------------------
        render_products(product_ctx, wholesale_list, bom_cost_jet, bom_cost_control, bom_cost_hh, bom_cost_hose, bom_cost_acc, bom_cost_mfx)
            
    
    if task_choice == 'Customer Details':

        # -----------------------
        # RENDER CUSTOMER DETAILS 
        # -----------------------
        render_customer(df, df_qb, master_customer_list)
        
    
    if task_choice == 'Leaderboards':

        # -------------------
        # RENDER LEADERBOARDS 
        # -------------------
        render_leaderboards()

    if task_choice == 'Customer Spending':

        render_customer_spend_leaderboard(df, df_qb, master_customer_list)
    

    
if __name__ == "__main__":
    main()

  
