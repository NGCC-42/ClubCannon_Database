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
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_option_menu import option_menu
#from fpdf import FPDF
#import base64


from data.load import (
    load_all_data,
)

from logic.analytics import (
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
    percent_of_change,
    wholesale_retail_totals,
    calc_hist_metrics,
    quarterly_sales,
    hist_annual_sales, 
    magic_sales_data
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
)

from ui.components import (
    style_metric_cards
)

from logic.products import (
    profit_by_type
)


# -----------------
# CREATE DATE LISTS
# -----------------

months = ['All', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
months_x = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
years = ['2022', '2023', '2024', '2025', '2026']


# --------------------
# MAKE DATA ACCESSIBLE
# --------------------

df, df_quotes, df_cogs, df_shipstat_23, df_shipstat_24, df_qb, df_hsd, df_hist, unique_customer_list, master_customer_list, wholesale_list = load_all_data()


# --------------------------------------------------
# FUNCTIONS AND VARIABLES FOR REAL TIME CALCULATIONS
# --------------------------------------------------


today = datetime.now()
one_year_ago = today - timedelta(days=365)
two_years_ago = today - timedelta(days=730)
three_years_ago = today - timedelta(days=1095)
four_years_ago = today - timedelta(days=1460)


# -------------------------------------------------
# HISTORICAL TO-DATE REVENUE -- NEEDS ANNUAL UPDATE
# -------------------------------------------------

@st.cache_data
def hist_td_rev(year: int) -> float:
    # Make a copy so we don't mutate the original
    df_loc = df_hist.copy()

    # Ensure order_date is datetime
    df_loc["order_date"] = pd.to_datetime(df_loc["order_date"], errors="coerce")

    # Drop rows with invalid/missing dates
    df_loc = df_loc.dropna(subset=["order_date"])

    # Build your "to-date" anchors
    td25 = today - timedelta(days=366)
    td24 = today - timedelta(days=731)
    td23 = today - timedelta(days=1096)
    td22 = today - timedelta(days=1461)
    td21 = today - timedelta(days=1826)
    td20 = today - timedelta(days=2191)
    td19 = today - timedelta(days=2557)
    td18 = today - timedelta(days=2922)
    td17 = today - timedelta(days=3287)
    td16 = today - timedelta(days=3652)
    td15 = today - timedelta(days=4018)
    td14 = today - timedelta(days=4383)
    td13 = today - timedelta(days=4748)

    date_dict = {
        2013: td13,
        2014: td14,
        2015: td15,
        2016: td16,
        2017: td17,
        2018: td18,
        2019: td19,
        2020: td20,
        2021: td21,
        2022: td22,
        2023: td23,
        2024: td24,
        2025: td25
    }

    # Guard in case someone calls with a year you didn't add
    if year not in date_dict:
        return 0.0

    start = datetime(year, 1, 1)
    end = date_dict[year]

    # Vectorized filter instead of manual idx loop
    mask = (
        (df_loc["order_date"] >= start)
        & (df_loc["order_date"] <= end)
        & (df_loc["order_date"].dt.year == year)
    )

    td_sales = df_loc.loc[mask, "total_sale"].sum()

    return float(td_sales)


# ----------------------------------------------
# USE METRIC CARDS TO DISPLAY MONTHLY SALES DATA
# ----------------------------------------------

def display_month_data_x(sales_dict1, sales_dict2=None, note=None):

    dBoard1 = st.columns(3)
    dBoard2 = st.columns(3)
    dBoard3 = st.columns(3)
    dBoard4 = st.columns(3)
    idx = 0
    idx1 = 0
    idx2 = 0
    idx3 = 0

    if note == None:
        for x in months_x:
    
            try:
                var = ''
                diff = (sales_dict1[x][0][0] + sales_dict1[x][1][0]) - (sales_dict2[x][1][0] + sales_dict2[x][0][0])
                if diff > 0:
                    var = '+'
                elif diff < 0:
                    var = '-'
                    
                if idx < 3:
                    with dBoard1[idx]:
                        ui.metric_card(title=x, content='${:,}'.format(int(sales_dict1[x][0][0] + sales_dict1[x][1][0])), description='{} ${:,} vs. prior year'.format(var, abs(int(diff))))
                elif idx >=3 and idx < 6:
                    with dBoard2[idx1]:
                        ui.metric_card(title=x, content='${:,}'.format(int(sales_dict1[x][0][0] + sales_dict1[x][1][0])), description='{} ${:,} vs. prior year'.format(var, abs(int(diff))))
                        idx1 += 1
                elif idx >= 6 and idx < 9:
                    with dBoard3[idx2]:
                        ui.metric_card(title=x, content='${:,}'.format(int(sales_dict1[x][0][0] + sales_dict1[x][1][0])), description='{} ${:,} vs. prior year'.format(var, abs(int(diff))))
                        idx2 += 1
                else:
                    with dBoard4[idx3]:
                        ui.metric_card(title=x, content='${:,}'.format(int(sales_dict1[x][0][0] + sales_dict1[x][1][0])), description='{} ${:,} vs. prior year'.format(var, abs(int(diff))))
                        idx3 += 1
        
                idx += 1
                
            except:
                
                if idx < 3:
                    with dBoard1[idx]:
                        ui.metric_card(title=x, content='${:,}'.format(int(sales_dict1[x][0][0] + sales_dict1[x][1][0])), description='')
                elif idx >=3 and idx < 6:
                    with dBoard2[idx1]:
                        ui.metric_card(title=x, content='${:,}'.format(int(sales_dict1[x][0][0] + sales_dict1[x][1][0])), description='')
                        idx1 += 1
                elif idx >= 6 and idx < 9:
                    with dBoard3[idx2]:
                        ui.metric_card(title=x, content='${:,}'.format(int(sales_dict1[x][0][0] + sales_dict1[x][1][0])), description='')
                        idx2 += 1
                else:
                    with dBoard4[idx3]:
                        ui.metric_card(title=x, content='${:,}'.format(int(sales_dict1[x][0][0] + sales_dict1[x][1][0])), description='')
                        idx3 += 1
        
                idx += 1
                
    return None


# -------------------------------------------------------------------------------------
# DISPLAY SALES METRICS - FORMATS METRIC CARD DISPLAY - SHOULD BE UPDATED OR REFACTORED
# -------------------------------------------------------------------------------------

def display_metrics(sales_dict1, sales_dict2=None, month='All', wvr1=None, wvr2=None, note=None):


    if sales_dict2 == None and note == None:
        
        data = extract_transaction_data(sales_dict1)
        total_sales, total_web_perc, total_fulcrum_perc, avg_month, magic_sales = calc_monthly_totals_v2(sales_dict1)
        
        db1, db2, db3 = st.columns([.3, .4, .3], gap='medium')
        
        db1.metric(label='**Website Sales**', value='${:,}'.format(int(data[3])), delta='')
        db1.metric(label='**Website Transactions**', value='{:,}'.format(data[6]), delta='')
        db1.metric(label='**Website Average Sale**', value='${:,}'.format(int(data[0])), delta='')
    
        db2.metric(label='**Total Sales**', value='${:,}'.format(int(data[5])), delta='')
        db2.metric(label='**Monthly Average**', value='${:,}'.format(int(avg_month)), delta='')
        db2.metric(label='**Total Transactions**', value='{:,}'.format(data[8]), delta='')
        
        db3.metric(label='**Fulcrum Sales**', value='${:,}'.format(int(data[4])), delta='')
        db3.metric(label='**Fulcrum Transactions**', value='{:,}'.format(data[7]), delta='')
        db3.metric(label='**Fulcrum Average Sale**', value='${:,}'.format(int(data[1])), delta='')
        
        style_metric_cards()

    if note != None:
        
        db1, db2, db3 = st.columns([.3, .4, .3], gap='medium')
        
        if sales_dict2 == None:

            sd1_tot, sd1_trans_tot, sd1_avg_month, sd1_avg_trans, sd1_wholesale, sd1_retail, sd1_wholesale_trans, sd1_retail_trans, sd1_avg_wholesale_trans, sd1_avg_retail_trans = calc_hist_metrics(sales_dict1)
            
            db1.metric(label='**Retail Sales**', value='${:,}'.format(int(sd1_retail)), delta='')
            db1.metric(label='**Retail Transactions**', value='{:,}'.format(int(sd1_retail_trans)), delta='')
            db1.metric(label='**Retail Average Sale**', value='${:,}'.format(int(sd1_avg_retail_trans)), delta='')
        
            db2.metric(label='**Total Sales**', value='${:,}'.format(int(sd1_tot)), delta='')
            db2.metric(label='**Monthly Average**', value='${:,}'.format(int(sd1_avg_month)), delta='')
            db2.metric(label='**Total Transactions**', value='{:,}'.format(int(sd1_trans_tot)), delta='')
            db2.metric(label='**Average Sale Amount**', value='${:,}'.format(int(sd1_avg_trans)), delta='')

            db3.metric(label='**Wholesale Sales**', value='${:,}'.format(int(sd1_wholesale)), delta='')
            db3.metric(label='**Wholesale Transactions**', value='{:,}'.format(int(sd1_wholesale_trans)), delta='')
            db3.metric(label='**Wholesale Average Sale**', value='${:,}'.format(int(sd1_avg_wholesale_trans)), delta='')


        else:

            sd1_tot, sd1_trans_tot, sd1_avg_month, sd1_avg_trans, sd1_wholesale, sd1_retail, sd1_wholesale_trans, sd1_retail_trans, sd1_avg_wholesale_trans, sd1_avg_retail_trans, sd2_tot, sd2_trans_tot, sd2_avg_month, sd2_avg_trans, sd2_wholesale, sd2_retail, sd2_wholesale_trans, sd2_retail_trans, sd2_avg_wholesale_trans, sd2_avg_retail_trans = calc_hist_metrics(sales_dict1, sales_dict2)
            
            db1.metric(label='**Retail Sales**', value='${:,}'.format(int(sd1_retail)), delta=percent_of_change(sd2_retail, sd1_retail))
            db1.metric(label='**Retail Transactions**', value='{:,}'.format(int(sd1_retail_trans)), delta=percent_of_change(sd2_retail_trans, sd1_retail_trans))
            db1.metric(label='**Retail Average Sale**', value='${:,}'.format(int(sd1_avg_retail_trans)), delta=percent_of_change(sd2_avg_retail_trans, sd1_avg_retail_trans))
        
            db2.metric(label='**Total Sales**', value='${:,}'.format(int(sd1_tot)), delta=percent_of_change(sd2_tot, sd1_tot))
            db2.metric(label='**Monthly Average**', value='${:,}'.format(int(sd1_avg_month)), delta=percent_of_change(sd2_avg_month, sd1_avg_month))
            db2.metric(label='**Total Transactions**', value='{:,}'.format(int(sd1_trans_tot)), delta=percent_of_change(sd2_trans_tot, sd1_trans_tot))
            db2.metric(label='**Average Sale Amount**', value='${:,}'.format(int(sd1_avg_trans)), delta=percent_of_change(sd2_avg_trans, sd1_avg_trans))

            db3.metric(label='**Wholesale Sales**', value='${:,}'.format(int(sd1_wholesale)), delta=percent_of_change(sd2_wholesale, sd1_wholesale))
            db3.metric(label='**Wholesale Transactions**', value='{:,}'.format(int(sd1_wholesale_trans)), delta=percent_of_change(sd2_wholesale_trans, sd1_wholesale_trans))
            db3.metric(label='**Wholesale Average Sale**', value='${:,}'.format(int(sd1_avg_wholesale_trans)), delta=percent_of_change(sd2_avg_wholesale_trans, sd1_avg_wholesale_trans))   

        style_metric_cards()
    
    elif month == 'All':

        total_sales1, total_web_perc1, total_fulcrum_perc1, avg_month1, magic_sales1 = calc_monthly_totals_v2(sales_dict1)
        total_sales2, total_web_perc2, total_fulcrum_perc2, avg_month2, magic_sales2 = calc_monthly_totals_v2(sales_dict2)

        data1 = extract_transaction_data(sales_dict1)
        data2 = extract_transaction_data(sales_dict2)
        web_sales = percent_of_change(data2[3], data1[3])
        web_trans = percent_of_change(data2[6], data1[6])
        web_avg_sale = percent_of_change(data2[0], data1[0])
        var = percent_of_change(data2[5], data1[5])
        avg_sale = percent_of_change(data2[2], data1[2])
        transaction_ct = percent_of_change(data2[8], data1[8])
        fulcrum_sales = percent_of_change(data2[4], data1[4])
        fulcrum_trans = percent_of_change(data2[7], data1[7])
        fulcrum_avg_sale = percent_of_change(data2[1], data1[1])
        avg_per_month = percent_of_change(avg_month2, avg_month1)

        wholesale_sales1, retail_sales1 = wholesale_retail_totals(wvr1)

        db1, db2, db3 = st.columns([.3, .4, .3], gap='medium')      
        
        if wvr2 == None:

            if data1[5] > 550000:
                
                db1.metric('**Website Sales**', '${:,}'.format(int(data1[3])), web_sales)
                db1.metric('**Website Transactions**', '{:,}'.format(data1[6]), web_trans)
                db1.metric('**Website Average Sale**', '${:,}'.format(int(data1[0])), web_avg_sale)
                db1.metric('**Retail Revenue**', '${:,}'.format(int(retail_sales1)), '')
            
                db2.metric('**Total Sales**', '${:,}'.format(int(data1[5])), var)
                db2.metric('**Monthly Average**', '${:,}'.format(int(avg_month1)), avg_per_month)
                db2.metric('**Total Transactions**', '{:,}'.format(data1[8]), transaction_ct)
                db2.metric('**Gross Profit**', '${:,.0f}'.format(profit_23))
                db2.metric(f':red[**MagicFX Sales**]', '${:,}'.format(int(magic_sales1)))
                
                db3.metric('**Fulcrum Sales**', '${:,}'.format(int(data1[4])), fulcrum_sales)
                db3.metric('**Fulcrum Transactions**', '{:,}'.format(data1[7]), fulcrum_trans)
                db3.metric('**Fulcrum Average Sale**', '${:,}'.format(int(data1[1])), fulcrum_avg_sale)
                db3.metric('**Wholesale Revenue**', '${:,}'.format(int(wholesale_sales1)), '')
                
            else:
                db1.metric('**Website Sales**', '${:,}'.format(int(data1[3])), web_sales)
                db1.metric('**Website Transactions**', '{:,}'.format(data1[6]), web_trans)
                db1.metric('**Website Average Sale**', '${:,}'.format(int(data1[0])), web_avg_sale)
                db1.metric('**Retail Revenue**', '${:,}'.format(int(retail_sales1)), '')
            
                db2.metric('**Total Sales**', '${:,}'.format(int(data1[5])), var)
                if datetime.now().month != 1:
                    db2.metric('**Monthly Average**', '${:,}'.format(int(avg_month1)), avg_per_month)
                db2.metric('**Total Transactions**', '{:,}'.format(data1[8]), transaction_ct)
                #db2.metric('**Gross Profit**', '${:,.0f}'.format(profit_23))
                db2.metric(f':red[**MagicFX Sales**]', '${:,}'.format(int(magic_sales1)))
                
                db3.metric('**Fulcrum Sales**', '${:,}'.format(int(data1[4])), fulcrum_sales)
                db3.metric('**Fulcrum Transactions**', '{:,}'.format(data1[7]), fulcrum_trans)
                db3.metric('**Fulcrum Average Sale**', '${:,}'.format(int(data1[4]/data1[7])), fulcrum_avg_sale)
                db3.metric('**Wholesale Revenue**', '${:,}'.format(int(wholesale_sales1)), '')
                

            style_metric_cards()

        else:

            wholesale_sales2, retail_sales2 = wholesale_retail_totals(wvr2)
            wholesale_delta = percent_of_change(wholesale_sales2, wholesale_sales1)
            retail_delta = percent_of_change(retail_sales2, retail_sales1)
            magic_delta = percent_of_change(magic_sales2, magic_sales1)

            if data1[5] > 1550000:
        
                db1.metric('**Website Sales**', '${:,}'.format(int(data1[3])), web_sales)
                db1.metric('**Website Transactions**', '{:,}'.format(data1[6]), web_trans)
                db1.metric('**Website Average Sale**', '${:,}'.format(int(data1[0])), web_avg_sale)
                db1.metric('**Retail Revenue**', '${:,}'.format(int(retail_sales1)), retail_delta)
                
                db2.metric('**Total Sales**', '${:,}'.format(int(data1[5])), var)
                db2.metric('**Monthly Average**', '${:,}'.format(int(avg_month1)), avg_per_month)
                db2.metric('**Total Transactions**', '{:,}'.format(data1[8]), transaction_ct)
                #db2.metric('**Gross Profit**', '${:,.0f}'.format(profit_24), percent_of_change(profit_23, profit_24))
                db2.metric(f':red[**MagicFX Sales**]', '${:,}'.format(int(magic_sales1)), magic_delta)
                
                db3.metric('**Fulcrum Sales**', '${:,}'.format(int(data1[4])), fulcrum_sales)
                db3.metric('**Fulcrum Transactions**', '{:,}'.format(data1[7]), fulcrum_trans)
                db3.metric('**Fulcrum Average Sale**', '${:,}'.format(int(data1[1])), fulcrum_avg_sale)
                db3.metric('**Wholesale Revenue**', '${:,}'.format(int(wholesale_sales1)), wholesale_delta)
                
            else:
                
                db1.metric('**Website Sales**', '${:,}'.format(int(data1[3])), web_sales)
                db1.metric('**Website Transactions**', '{:,}'.format(data1[6]), web_trans)
                db1.metric('**Website Average Sale**', '${:,}'.format(int(data1[0])), web_avg_sale)
                db1.metric('**Retail Revenue**', '${:,}'.format(int(retail_sales1)), retail_delta)
                
                db2.metric('**Total Sales**', '${:,}'.format(int(data1[5])), var)
                if datetime.now().month != 1:
                    db2.metric('**Monthly Average**', '${:,}'.format(int(avg_month1)), avg_per_month)
                db2.metric('**Total Transactions**', '{:,}'.format(data1[8]), transaction_ct)
                db2.metric(f':red[**MagicFX Sales**]', '${:,}'.format(int(magic_sales1)), magic_delta)
                
                db3.metric('**Fulcrum Sales**', '${:,}'.format(int(data1[4])), fulcrum_sales)
                db3.metric('**Fulcrum Transactions**', '{:,}'.format(data1[7]), fulcrum_trans)
                db3.metric('**Fulcrum Average Sale**', '${:,}'.format(int(data1[1])), fulcrum_avg_sale)
                db3.metric('**Wholesale Revenue**', '${:,}'.format(int(wholesale_sales1)), wholesale_delta)      
                
            style_metric_cards()
        
    else:

        data1 = extract_transaction_data(sales_dict1, month)
        data2 = extract_transaction_data(sales_dict2, month)
        web_sales = percent_of_change(data2[3], data1[3])
        web_trans = percent_of_change(data2[6], data1[6])
        web_avg_sale = percent_of_change(data2[0], data1[0])
        var = percent_of_change(data2[5], data1[5])
        avg_sale = percent_of_change(data2[2], data1[2])
        transaction_ct = percent_of_change(data2[8], data1[8])
        fulcrum_sales = percent_of_change(data2[4], data1[4])
        fulcrum_trans = percent_of_change(data2[7], data1[7])
        fulcrum_avg_sale = percent_of_change(data2[1], data1[1])
        

        db1, db2, db3 = st.columns([.3, .4, .3], gap='medium')

        if wvr2 == None:

            db1.metric('**Website Sales**', '${:,}'.format(int(data1[3])), web_sales)
            db1.metric('**Website Transactions**', '{:,}'.format(data1[6]), web_trans)
            db1.metric('**Website Average Sale**', '${:,}'.format(int(data1[0])), web_avg_sale)
            db1.metric('**Retail Revenue**', '${:,}'.format(int(wvr1[month][1])), '')
        
            db2.metric('**Total Sales**', '${:,}'.format(int(data1[5])), var)
            db2.metric('**Total Transactions**', '{:,}'.format(data1[8]), transaction_ct)
            db2.metric('**Average Sale**', '${:,}'.format(int(data1[2])), avg_sale)
            
            db3.metric('**Fulcrum Sales**', '${:,}'.format(int(data1[4])), fulcrum_sales)
            db3.metric('**Fulcrum Transactions**', '{:,}'.format(data1[7]), fulcrum_trans)
            db3.metric('**Fulcrum Average Sale**', '${:,}'.format(int(data1[1])), fulcrum_avg_sale)
            db3.metric('**Wholesale Revenue**', '${:,}'.format(int(wvr1[month][0])), '')

            style_metric_cards()
        
        else:

            retail_delta = percent_of_change(wvr2[month][1], wvr1[month][1])
            wholesale_delta = percent_of_change(wvr2[month][0], wvr1[month][0])
            
            db1.metric('**Website Sales**', '${:,}'.format(int(data1[3])), web_sales)
            db1.metric('**Website Transactions**', '{:,}'.format(data1[6]), web_trans)
            db1.metric('**Website Average Sale**', '${:,}'.format(int(data1[0])), web_avg_sale)
            db1.metric('**Retail Revenue**', '${:,}'.format(int(wvr1[month][1])), retail_delta)
        
            db2.metric('**Total Sales**', '${:,}'.format(int(data1[5])), var)
            db2.metric('**Total Transactions**', '{:,}'.format(data1[8]), transaction_ct)
            db2.metric('**Average Sale**', '${:,}'.format(int(data1[2])), avg_sale)
            
            db3.metric('**Fulcrum Sales**', '${:,}'.format(int(data1[4])), fulcrum_sales)
            db3.metric('**Fulcrum Transactions**', '{:,}'.format(data1[7]), fulcrum_trans)
            db3.metric('**Fulcrum Average Sale**', '${:,}'.format(int(data1[1])), fulcrum_avg_sale)
            db3.metric('**Wholesale Revenue**', '${:,}'.format(int(wvr1[month][0])), wholesale_delta)
    
            style_metric_cards()
    
    return None


# ----------------------------------------------
# FUNCTION TO CALCULATE HISTORICAL QUARTLY SALES 
# ----------------------------------------------

@st.cache_data
def hist_quarterly_sales():
    # Define the quarters as lists of month names
    quarters = {
        1: ["January", "February", "March"],
        2: ["April", "May", "June"],
        3: ["July", "August", "September"],
        4: ["October", "November", "December"]
    }
    
    def compute_quarterly_sales(sales):
        """
        Given a sales dictionary (e.g., sales13) where each month maps to
        [[wholesale_total, wholesale_order_count], [non_wholesale_total, non_wholesale_order_count]],
        compute a list of quarterly totals by summing the wholesale and non-wholesale totals.
        """
        return [
            sum(sales[month][0][0] + sales[month][1][0] for month in quarters[q])
            for q in range(1, 5)
        ]
    
    # Compute quarterly sales for each year
    qs13 = compute_quarterly_sales(sales13)
    qs14 = compute_quarterly_sales(sales14)
    qs15 = compute_quarterly_sales(sales15)
    qs16 = compute_quarterly_sales(sales16)
    qs17 = compute_quarterly_sales(sales17)
    qs18 = compute_quarterly_sales(sales18)
    qs19 = compute_quarterly_sales(sales19)
    qs20 = compute_quarterly_sales(sales20)
    qs21 = compute_quarterly_sales(sales21)
    qs22 = compute_quarterly_sales(sales22)
    
    return qs13, qs14, qs15, qs16, qs17, qs18, qs19, qs20, qs21, qs22


# -----------------------------
# CALCULATE MAGIC FX SALES DATA
# -----------------------------

mfx_rev, mfx_costs, mfx_profit = magic_sales_data()

# ---------------------
# HISTORICAL SALES DATA
# ---------------------

sales13, sales14, sales15, sales16, sales17, sales18, sales19, sales20, sales21, sales22 = hist_annual_sales()  


# -------------------------------
# WHOLESALE VS. RETAIL SALES DATA
# -------------------------------

wvr_23_months = get_monthly_sales_wvr(df, 2023)
wvr_24_months = get_monthly_sales_wvr(df, 2024)
wvr_25_months = get_monthly_sales_wvr(df, 2025)
wvr_26_months = get_monthly_sales_wvr(df, 2026)
wvr_26_ytd, wvr_25_ytd, wvr_24_ytd, wvr_23_ytd = get_monthly_sales_wvr_ytd()

wvr_23_totals = wholesale_retail_totals(wvr_23_months)
wvr_23_totals_ytd = wholesale_retail_totals(wvr_23_ytd)
wvr_24_totals = wholesale_retail_totals(wvr_24_months)  
wvr_23_totals_ytd = wholesale_retail_totals(wvr_24_ytd)
wvr_24_totals = wholesale_retail_totals(wvr_24_months)
wvr_25_totals_ytd = wholesale_retail_totals(wvr_25_ytd)
wvr_25_totals = wholesale_retail_totals(wvr_25_months)
wvr_26_totals_ytd = wholesale_retail_totals(wvr_26_ytd)

# ----------------------------
# QUARTERLY SALES CALCULATIONS
# ----------------------------

q1_26, q2_26, q3_26, q4_26 = quarterly_sales(2026)
q1_25, q2_25, q3_25, q4_25 = quarterly_sales(2025)
q1_24, q2_24, q3_24, q4_24 = quarterly_sales(2024)
q1_23, q2_23, q3_23, q4_23 = quarterly_sales(2023)
qs13, qs14, qs15, qs16, qs17, qs18, qs19, qs20, qs21, qs22 = hist_quarterly_sales()

# -------------------------------------------
# FACTOR DATA FOR LINE GRAPH COMPARISON CHART
# -------------------------------------------

sales_dict_23 = get_monthly_sales_v2(df, 2023)
total_23, web_23, ful_23, avg_23, magic23 = calc_monthly_totals_v2(sales_dict_23)

sales_dict_24 = get_monthly_sales_v2(df, 2024)
total_24, web_24, ful_24, avg_24, magic24 = calc_monthly_totals_v2(sales_dict_24)

sales_dict_25 = get_monthly_sales_v2(df, 2025)
total_25, web_25, ful_25, avg_25, magic25 = calc_monthly_totals_v2(sales_dict_25)

sales_dict_26 = get_monthly_sales_v2(df, 2026)
total_26, web_26, ful_26, avg_26, magic26 = calc_monthly_totals_v2(sales_dict_26)

# ---------------------------------------------------
# REALTIME TO-DATE SALES CALCULATIONS FOR COMPARISON
# ---------------------------------------------------

td_sales26, td_sales25, td_sales24, td_sales23 = get_monthly_sales_ytd()

# -------------------
# PROFIT CALCULATIONS
# -------------------

profit_26 = profit_by_type(['2026'], ['Jet', 'Control', 'Handheld', 'Hose', 'Accessory'])
profit_25 = profit_by_type(['2025'], ['Jet', 'Control', 'Handheld', 'Hose', 'Accessory'])
profit_24 = profit_by_type(['2024'], ['Jet', 'Control', 'Handheld', 'Hose', 'Accessory']) + mfx_profit
profit_23 = profit_by_type(['2023'], ['Jet', 'Control', 'Handheld', 'Hose', 'Accessory'])

# ------------------------------
# COMPILE DATA FOR SALES REPORTS
# ------------------------------

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

# ---------------------------------------------------
# COMPILE AND FORMAT DATA FOR ANNUAL COMPARISON GRAPH
# ---------------------------------------------------

x = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']

def graph_data():

    y2013 = []
    y2014 = []
    y2015 = []
    y2016 = []
    y2017 = []
    y2018 = []
    y2019 = []
    y2020 = []
    y2021 = []
    y2022 = []
    y2023 = []
    y2024 = []
    y2025 = []
    y2026 = []

    for key, val in sales13.items():
        y2013.append(val[0][0] + val[1][0])
    for key, val in sales14.items():
        y2014.append(val[0][0] + val[1][0])
    for key, val in sales15.items():
        y2015.append(val[0][0] + val[1][0])
    for key, val in sales16.items():
        y2016.append(val[0][0] + val[1][0])
    for key, val in sales17.items():
        y2017.append(val[0][0] + val[1][0])
    for key, val in sales18.items():
        y2018.append(val[0][0] + val[1][0])
    for key, val in sales19.items():
        y2019.append(val[0][0] + val[1][0])
    for key, val in sales20.items():
        y2020.append(val[0][0] + val[1][0])
    for key, val in sales21.items():
        y2021.append(val[0][0] + val[1][0])
    for key, val in sales_dict_22.items():
        y2022.append(val[0][0] + val[1][0])
    for key, val in sales_dict_23.items():
        y2023.append(val[0][0] + val[1][0])
    for key, val in sales_dict_24.items():
        y2024.append(val[0][0] + val[1][0])
    for key, val in sales_dict_25.items():
        y2025.append(val[0][0] + val[1][0])
    for key, val in sales_dict_26.items():
        y2026.append(val[0][0] + val[1][0])

    return y2013, y2014, y2015, y2016, y2017, y2018, y2019, y2020, y2021, y2022, y2023, y2024, y2025, y2026


y2013, y2014, y2015, y2016, y2017, y2018, y2019, y2020, y2021, y2022, y2023, y2024, y2025, y2026 = graph_data()


# ------------------------------------
# RENDER FUNCTION TO DISPLAY DASHBOARD
# ------------------------------------

def render_dashboard(td_26, td_25, td_24, td_23, td_22, sales_dict_26, sales_dict_25, sales_dict_24, sales_dict_23, td_sales25, td_sales24, td_sales23):

    col1, col2, col3 = st.columns([.28, .44, .28], gap='medium')
    colx, coly, colz = st.columns([.28, .44, .28], gap='medium')
    
    with col2:
        
        year_select = ui.tabs(options=['2026', '2025', '2024', '2023', '2022', '2021', '2020', '2019', '2018', '2017', '2016', '2015', '2014', '2013'], default_value='2026')    
        
        #tot_vs_ytd = ui.tabs(options=['Totals', 'YTD'], default_value='Totals')

    series_by_year = {
        '2026': y2026,
        '2025': y2025,
        '2024': y2024,
        '2023': y2023,
        '2022': y2022,
        '2021': y2021,
        '2020': y2020,
        '2019': y2019,
        '2018': y2018,
        '2017': y2017,
        '2016': y2016,
        '2015': y2015,
        '2014': y2014,
        '2013': y2013
    }

    col1.header('Annual Comparison')
    
    plot_annual_comparison(x, years_to_plot=year_select, col1=col1, series_by_year=series_by_year, line_width=11, fig_width=18, fig_height=13)
    
    with colx:
        
        st.header('To-Date Sales')
        
        cola, colb, colc = st.columns(3)

        cola.metric('**2026 Total**', '${:,}'.format(int(td_26[1] + td_26[0])), percent_of_change((td_25[0] + td_25[1]), (td_26[1] + td_26[0])))
        cola.metric('**2026 Web**', '${:,}'.format(int(td_26[0])), percent_of_change(td_25[0], td_26[0]))
        cola.metric('**2026 Fulcrum**', '${:,}'.format(int(td_26[1])), percent_of_change(td_25[1], td_26[1]))

        colb.metric('**2025 Total**', '${:,}'.format(int(td_25[1] + td_25[0])), percent_of_change((td_24[0] + td_24[1]), (td_25[0] + td_25[1])))
        colb.metric('**2025 Web**', '${:,}'.format(int(td_25[0])), percent_of_change(td_24[0], td_25[0]))
        colb.metric('**2025 Fulcrum**', '${:,}'.format(int(td_25[1])), percent_of_change(td_24[1], td_25[1]))
        
        colc.metric('**2024 Total**', '${:,}'.format(int(td_24[1] + td_24[0])), percent_of_change((td_23[0] + td_23[1]), (td_24[0] + td_24[1])))
        colc.metric('**2024 Web**', '${:,}'.format(int(td_24[0])), percent_of_change(td_23[0], td_24[0]))
        colc.metric('**2024 Fulcrum**', '${:,}'.format(int(td_24[1])), percent_of_change(td_23[1], td_24[1]))
        

        style_metric_cards()

    with col2:
        
        if year_select == '2026':
            
            display_metrics(sales_dict_26, td_sales25, wvr1=wvr_26_months, wvr2=wvr_25_ytd)
    
            with col3:
                
                st.header('Sales by Month')
                plot_bar_chart_ms(format_for_chart_ms(sales_dict_26))

            with colz:
                
                st.header('Quarterly Sales')
                
                col6, col7, col8 = st.columns([.3, .4, .3])
                
                col6.metric('**Q1 Web Sales**', '${:,}'.format(int(q1_26[0])), percent_of_change(q1_25[0], q1_26[0]))
                col7.metric('**Q1 Total Sales**', '${:,}'.format(int(q1_26[0] + q1_26[1])), percent_of_change((q1_25[0] + q1_25[1]), (q1_26[0] + q1_26[1])))
                col8.metric('**Q1 Fulcrum Sales**', '${:,}'.format(int(q1_26[1])), percent_of_change(q1_25[1], q1_26[1]))
                
                col6.metric('**Q2 Web Sales**', '${:,}'.format(int(q2_26[0])), percent_of_change(q2_25[0], q2_26[0]))
                col7.metric('**Q2 Total Sales**', '${:,}'.format(int(q2_26[0] + q2_26[1])), percent_of_change((q2_25[0] + q2_25[1]), (q2_26[0] + q2_26[1])))
                col8.metric('**Q2 Fulcrum Sales**', '${:,}'.format(int(q2_26[1])), percent_of_change(q2_25[1], q2_26[1]))
                
                col6.metric('**Q3 Web Sales**', '${:,}'.format(int(q3_26[0])), percent_of_change(q3_25[0], q3_26[0]))
                col7.metric('**Q3 Total Sales**', '${:,}'.format(int(q3_26[0] + q3_26[1])), percent_of_change((q3_25[0] + q3_25[1]), (q3_26[0] + q3_26[1])))
                col8.metric('**Q3 Fulcrum Sales**', '${:,}'.format(int(q3_26[1])), percent_of_change(q3_24[1], q3_25[1]))
    
                col6.metric('**Q4 Web Sales**', '${:,}'.format(int(q4_26[0])), percent_of_change(q4_25[0], q4_26[0]))
                col7.metric('**Q4 Total Sales**', '${:,}'.format(int(q4_26[0] + q4_26[1])), percent_of_change((q4_25[0] + q4_25[1]), (q4_26[0] + q4_26[1])))
                col8.metric('**Q4 Fulcrum Sales**', '${:,}'.format(int(q4_26[1])), percent_of_change(q4_25[1], q4_26[1]))
    
            with coly:
                months[0] = 'Overview'
                focus = st.selectbox('', options=months, key='Focus25')
        
                if focus == 'Overview':
                    display_month_data_x(sales_dict_26, sales_dict_25)
                elif focus == 'January':
                    display_metrics(sales_dict_26, sales_dict_25, 'January', wvr1=wvr_26_months, wvr2=wvr_25_months)
                elif focus == 'February':
                    display_metrics(sales_dict_26, sales_dict_25, 'February', wvr1=wvr_26_months, wvr2=wvr_25_months)
                elif focus == 'March':
                    display_metrics(sales_dict_26, sales_dict_25, 'March', wvr1=wvr_26_months, wvr2=wvr_25_months)
                elif focus == 'April':
                    display_metrics(sales_dict_26, sales_dict_25, 'April', wvr1=wvr_26_months, wvr2=wvr_25_months)
                elif focus == 'May':
                    display_metrics(sales_dict_26, sales_dict_25, 'May', wvr1=wvr_26_months, wvr2=wvr_25_months)
                elif focus == 'June':
                    display_metrics(sales_dict_26, sales_dict_25, 'June', wvr1=wvr_26_months, wvr2=wvr_25_months)
                elif focus == 'July':
                    display_metrics(sales_dict_26, sales_dict_25, 'July', wvr1=wvr_26_months, wvr2=wvr_25_months)
                elif focus == 'August':
                    display_metrics(sales_dict_26, sales_dict_25, 'August', wvr1=wvr_26_months, wvr2=wvr_25_months)
                elif focus == 'September':
                    display_metrics(sales_dict_26, sales_dict_25, 'September', wvr1=wvr_26_months, wvr2=wvr_25_months)
                elif focus == 'October':
                    display_metrics(sales_dict_26, sales_dict_25, 'October', wvr1=wvr_26_months, wvr2=wvr_25_months)
                elif focus == 'November':
                    display_metrics(sales_dict_26, sales_dict_25, 'November', wvr1=wvr_26_months, wvr2=wvr_25_months)
                else:
                    display_metrics(sales_dict_26, sales_dict_25, 'December', wvr1=wvr_26_months, wvr2=wvr_25_months)
                    
        
        if year_select == '2025':

            with col2:
                tot_vs_ytd = ui.tabs(options=['Totals', 'YTD'], default_value='Totals')
                
            if tot_vs_ytd == 'Totals':
                display_metrics(sales_dict_25, td_sales24, wvr1=wvr_25_months, wvr2=wvr_24_ytd)
            else:
                display_metrics(td_sales25, td_sales24, wvr1=wvr_25_ytd, wvr2=wvr_24_ytd)
            
    
            with col3:
                
                st.header('Sales by Month')
                plot_bar_chart_ms(format_for_chart_ms(sales_dict_25))

            with colz:
                
                st.header('Quarterly Sales')
                
                col6, col7, col8 = st.columns([.3, .4, .3])
                
                col6.metric('**Q1 Web Sales**', '${:,}'.format(int(q1_25[0])), percent_of_change(q1_24[0], q1_25[0]))
                col7.metric('**Q1 Total Sales**', '${:,}'.format(int(q1_25[0] + q1_25[1])), percent_of_change((q1_24[0] + q1_24[1]), (q1_25[0] + q1_25[1])))
                col8.metric('**Q1 Fulcrum Sales**', '${:,}'.format(int(q1_25[1])), percent_of_change(q1_24[1], q1_25[1]))
                
                col6.metric('**Q2 Web Sales**', '${:,}'.format(int(q2_25[0])), percent_of_change(q2_24[0], q2_25[0]))
                col7.metric('**Q2 Total Sales**', '${:,}'.format(int(q2_25[0] + q2_25[1])), percent_of_change((q2_24[0] + q2_24[1]), (q2_25[0] + q2_25[1])))
                col8.metric('**Q2 Fulcrum Sales**', '${:,}'.format(int(q2_25[1])), percent_of_change(q2_24[1], q2_25[1]))
                
                col6.metric('**Q3 Web Sales**', '${:,}'.format(int(q3_25[0])), percent_of_change(q3_24[0], q3_25[0]))
                col7.metric('**Q3 Total Sales**', '${:,}'.format(int(q3_25[0] + q3_25[1])), percent_of_change((q3_24[0] + q3_24[1]), (q3_25[0] + q3_25[1])))
                col8.metric('**Q3 Fulcrum Sales**', '${:,}'.format(int(q3_25[1])), percent_of_change(q3_24[1], q3_25[1]))
    
                col6.metric('**Q4 Web Sales**', '${:,}'.format(int(q4_25[0])), percent_of_change(q4_24[0], q4_25[0]))
                col7.metric('**Q4 Total Sales**', '${:,}'.format(int(q4_25[0] + q4_25[1])), percent_of_change((q4_24[0] + q4_24[1]), (q4_25[0] + q4_25[1])))
                col8.metric('**Q4 Fulcrum Sales**', '${:,}'.format(int(q4_25[1])), percent_of_change(q4_24[1], q4_25[1]))
    
            with coly:
                months[0] = 'Overview'
                focus = st.selectbox('', options=months, key='Focus25')
        
                if focus == 'Overview':
                    display_month_data_x(sales_dict_25, sales_dict_24)
                elif focus == 'January':
                    display_metrics(sales_dict_25, sales_dict_24, 'January', wvr1=wvr_25_months, wvr2=wvr_24_months)
                elif focus == 'February':
                    display_metrics(sales_dict_25, sales_dict_24, 'February', wvr1=wvr_25_months, wvr2=wvr_24_months)
                elif focus == 'March':
                    display_metrics(sales_dict_25, sales_dict_24, 'March', wvr1=wvr_25_months, wvr2=wvr_24_months)
                elif focus == 'April':
                    display_metrics(sales_dict_25, sales_dict_24, 'April', wvr1=wvr_25_months, wvr2=wvr_24_months)
                elif focus == 'May':
                    display_metrics(sales_dict_25, sales_dict_24, 'May', wvr1=wvr_25_months, wvr2=wvr_24_months)
                elif focus == 'June':
                    display_metrics(sales_dict_25, sales_dict_24, 'June', wvr1=wvr_25_months, wvr2=wvr_24_months)
                elif focus == 'July':
                    display_metrics(sales_dict_25, sales_dict_24, 'July', wvr1=wvr_25_months, wvr2=wvr_24_months)
                elif focus == 'August':
                    display_metrics(sales_dict_25, sales_dict_24, 'August', wvr1=wvr_25_months, wvr2=wvr_24_months)
                elif focus == 'September':
                    display_metrics(sales_dict_25, sales_dict_24, 'September', wvr1=wvr_25_months, wvr2=wvr_24_months)
                elif focus == 'October':
                    display_metrics(sales_dict_25, sales_dict_24, 'October', wvr1=wvr_25_months, wvr2=wvr_24_months)
                elif focus == 'November':
                    display_metrics(sales_dict_25, sales_dict_24, 'November', wvr1=wvr_25_months, wvr2=wvr_24_months)
                else:
                    display_metrics(sales_dict_25, sales_dict_24, 'December', wvr1=wvr_25_months, wvr2=wvr_24_months)
                    

        elif year_select == '2024':

            with col2:
                tot_vs_ytd = ui.tabs(options=['Totals', 'YTD'], default_value='Totals')
                
            if tot_vs_ytd == 'Totals':
                display_metrics(sales_dict_24, sales_dict_23, wvr1=wvr_24_months, wvr2=wvr_23_months)
            else:
                display_metrics(td_sales24, td_sales23, wvr1=wvr_24_ytd, wvr2=wvr_23_ytd)
        
            with col3:
                
                st.header('Sales by Month')
                plot_bar_chart_ms(format_for_chart_ms(sales_dict_24))
                
            with colz:
                st.header('Quarterly Sales')
                
                col6, col7, col8 = st.columns([.3, .4, .3])
                
                col6.metric('**Q1 Web Sales**', '${:,}'.format(int(q1_24[0])), percent_of_change(q1_23[0], q1_24[0]))
                col7.metric('**Q1 Total Sales**', '${:,}'.format(int(q1_24[0] + q1_24[1])), percent_of_change((q1_23[0] + q1_23[1]), (q1_24[0] + q1_24[1])))
                col8.metric('**Q1 Fulcrum Sales**', '${:,}'.format(int(q1_24[1])), percent_of_change(q1_23[1], q1_24[1]))
                
                col6.metric('**Q2 Web Sales**', '${:,}'.format(int(q2_24[0])), percent_of_change(q2_23[0], q2_24[0]))
                col7.metric('**Q2 Total Sales**', '${:,}'.format(int(q2_24[0] + q2_24[1])), percent_of_change((q2_23[0] + q2_23[1]), (q2_24[0] + q2_24[1])))
                col8.metric('**Q2 Fulcrum Sales**', '${:,}'.format(int(q2_24[1])), percent_of_change(q2_23[1], q2_24[1]))
                
                col6.metric('**Q3 Web Sales**', '${:,}'.format(int(q3_24[0])), percent_of_change(q3_23[0], q3_24[0]))
                col7.metric('**Q3 Total Sales**', '${:,}'.format(int(q3_24[0] + q3_24[1])), percent_of_change((q3_23[0] + q3_23[1]), (q3_24[0] + q3_24[1])))
                col8.metric('**Q3 Fulcrum Sales**', '${:,}'.format(int(q3_24[1])), percent_of_change(q3_23[1], q3_24[1]))
    
                col6.metric('**Q4 Web Sales**', '${:,}'.format(int(q4_24[0])), percent_of_change(q4_23[0], q4_24[0]))
                col7.metric('**Q4 Total Sales**', '${:,}'.format(int(q4_24[0] + q4_24[1])), percent_of_change((q4_23[0] + q4_23[1]), (q4_24[0] + q4_24[1])))
                col8.metric('**Q4 Fulcrum Sales**', '${:,}'.format(int(q4_24[1])), percent_of_change(q4_23[1], q4_24[1]))


            with coly:
                months[0] = 'Overview'
                focus = st.selectbox('', options=months, key='Focus24')
        
                if focus == 'Overview':
                    display_month_data_x(sales_dict_24, sales_dict_23)
                elif focus == 'January':
                    display_metrics(sales_dict_24, sales_dict_23, 'January', wvr1=wvr_24_months, wvr2=wvr_23_months)
                elif focus == 'February':
                    display_metrics(sales_dict_24, sales_dict_23, 'February', wvr1=wvr_24_months, wvr2=wvr_23_months)
                elif focus == 'March':
                    display_metrics(sales_dict_24, sales_dict_23, 'March', wvr1=wvr_24_months, wvr2=wvr_23_months)
                elif focus == 'April':
                    display_metrics(sales_dict_24, sales_dict_23, 'April', wvr1=wvr_24_months, wvr2=wvr_23_months)
                elif focus == 'May':
                    display_metrics(sales_dict_24, sales_dict_23, 'May', wvr1=wvr_24_months, wvr2=wvr_23_months)
                elif focus == 'June':
                    display_metrics(sales_dict_24, sales_dict_23, 'June', wvr1=wvr_24_months, wvr2=wvr_23_months)
                elif focus == 'July':
                    display_metrics(sales_dict_24, sales_dict_23, 'July', wvr1=wvr_24_months, wvr2=wvr_23_months)
                elif focus == 'August':
                    display_metrics(sales_dict_24, sales_dict_23, 'August', wvr1=wvr_24_months, wvr2=wvr_23_months)
                elif focus == 'September':
                    display_metrics(sales_dict_24, sales_dict_23, 'September', wvr1=wvr_24_months, wvr2=wvr_23_months)
                elif focus == 'October':
                    display_metrics(sales_dict_24, sales_dict_23, 'October', wvr1=wvr_24_months, wvr2=wvr_23_months)
                elif focus == 'November':
                    display_metrics(sales_dict_24, sales_dict_23, 'November', wvr1=wvr_24_months, wvr2=wvr_23_months)
                else:
                    display_metrics(sales_dict_24, sales_dict_23, 'December', wvr1=wvr_24_months, wvr2=wvr_23_months)


        elif year_select == '2023':

            with col2:
                tot_vs_ytd = ui.tabs(options=['Totals', 'YTD'], default_value='Totals')

            if tot_vs_ytd == 'Totals':
                display_metrics(sales_dict_23, sales_dict_22, wvr1=wvr_23_months)
            else:
                display_metrics(td_sales23, sales_dict_22, wvr1=wvr_23_ytd)
                
            with col3:
                
                st.header('Sales by Month')
                plot_bar_chart_ms(format_for_chart_ms(sales_dict_23)) 
                
            with colz:

                st.header('Quarterly Sales')
                
                col6, col7, col8 = st.columns([.3, .4, .3])
                
                col6.metric('**Q1 Web Sales**', '${:,}'.format(int(q1_23[0])), percent_of_change((qs22[0] * .4), q1_23[0]))
                col7.metric('**Q1 Total Sales**', '${:,}'.format(int(q1_23[0] + q1_23[1])), percent_of_change((qs22[0]), (q1_23[0] + q1_23[1])))
                col8.metric('**Q1 Fulcrum Sales**', '${:,}'.format(int(q1_23[1])), percent_of_change((qs22[0] * .6), q1_23[1]))
                
                col6.metric('**Q2 Web Sales**', '${:,}'.format(int(q2_23[0])), percent_of_change((qs22[1] * .4), q2_23[0]))
                col7.metric('**Q2 Total Sales**', '${:,}'.format(int(q2_23[0] + q2_23[1])), percent_of_change((qs22[1]), (q2_23[0] + q2_23[1])))
                col8.metric('**Q2 Fulcrum Sales**', '${:,}'.format(int(q2_23[1])), percent_of_change((qs22[1] * .6), q2_23[1]))
                
                col6.metric('**Q3 Web Sales**', '${:,}'.format(int(q3_23[0])), percent_of_change((qs22[2] * .4), q3_23[0]))
                col7.metric('**Q3 Total Sales**', '${:,}'.format(int(q3_23[0] + q3_23[1])), percent_of_change((qs22[2]), (q3_23[0] + q3_23[1])))
                col8.metric('**Q3 Fulcrum Sales**', '${:,}'.format(int(q3_23[1])), percent_of_change((qs22[2] * .6), q3_23[1]))

                col6.metric('**Q4 Web Sales**', '${:,}'.format(int(q4_23[0])), percent_of_change((qs22[3] * .4), q4_23[0]))
                col7.metric('**Q4 Total Sales**', '${:,}'.format(int(q4_23[0] + q4_23[1])), percent_of_change((qs22[3]), (q4_23[0] + q4_23[1])))
                col8.metric('**Q4 Fulcrum Sales**', '${:,}'.format(int(q4_23[1])), percent_of_change((qs22[3] * .6), q4_23[1]))

            with coly:
                months[0] = 'Overview'
                focus = st.selectbox('', options=months, key='Focus23')
                
                if focus == 'Overview':
                    display_month_data_x(sales_dict_23, sales_dict_22)
                elif focus == 'January':
                    display_metrics(sales_dict_23, sales_dict_22, 'January', wvr1=wvr_23_months)
                elif focus == 'February':
                    display_metrics(sales_dict_23, sales_dict_22, 'February', wvr1=wvr_23_months)
                elif focus == 'March':
                    display_metrics(sales_dict_23, sales_dict_22, 'March', wvr1=wvr_23_months)
                elif focus == 'April':
                    display_metrics(sales_dict_23, sales_dict_22, 'April', wvr1=wvr_23_months)
                elif focus == 'May':
                    display_metrics(sales_dict_23, sales_dict_22, 'May', wvr1=wvr_23_months)
                elif focus == 'June':
                    display_metrics(sales_dict_23, sales_dict_22, 'June', wvr1=wvr_23_months)
                elif focus == 'July':
                    display_metrics(sales_dict_23, sales_dict_22, 'July', wvr1=wvr_23_months)
                elif focus == 'August':
                    display_metrics(sales_dict_23, sales_dict_22, 'August', wvr1=wvr_23_months)
                elif focus == 'September':
                    display_metrics(sales_dict_23, sales_dict_22, 'September', wvr1=wvr_23_months)
                elif focus == 'October':
                    display_metrics(sales_dict_23, sales_dict_22, 'October', wvr1=wvr_23_months)
                elif focus == 'November':
                    display_metrics(sales_dict_23, sales_dict_22, 'November', wvr1=wvr_23_months)
                else:
                    display_metrics(sales_dict_23, sales_dict_22, 'December', wvr1=wvr_23_months)
                

        if year_select == '2022':
    
            display_metrics(sales22, sales21, note='22')

            with col3:

                st.header('Sales by Month')
                plot_bar_chart_ms(format_for_chart_ms(sales22))

            with colz:
                
                st.header('Quarterly Sales')
                
                col6, col7, col8 = st.columns([.3, .4, .3])
                
                col7.metric('**Q1 Total Sales**', '${:,}'.format(int(qs22[0])), percent_of_change(qs21[0], qs22[0]))

                col7.metric('**Q2 Total Sales**', '${:,}'.format(int(qs22[1])), percent_of_change(qs21[1], qs22[1]))
        
                col7.metric('**Q3 Total Sales**', '${:,}'.format(int(qs22[2])), percent_of_change(qs21[2], qs22[2]))

                col7.metric('**Q4 Total Sales**', '${:,}'.format(int(qs22[3])), percent_of_change(qs21[3], qs22[3]))  
                
            #st.divider()
            with coly:
                display_month_data_x(sales22, sales21)

        if year_select == '2021':
    
            display_metrics(sales21, sales20, note='21')

            with col3:

                st.header('Sales by Month')
                plot_bar_chart_ms(format_for_chart_ms(sales21))

            with colz:
                
                st.header('Quarterly Sales')
                
                col6, col7, col8 = st.columns([.3, .4, .3])
                
                col7.metric('**Q1 Total Sales**', '${:,}'.format(int(qs21[0])), percent_of_change(qs20[0], qs21[0]))

                col7.metric('**Q2 Total Sales**', '${:,}'.format(int(qs21[1])), percent_of_change(qs20[1], qs21[1]))
        
                col7.metric('**Q3 Total Sales**', '${:,}'.format(int(qs21[2])), percent_of_change(qs20[2], qs21[2]))

                col7.metric('**Q4 Total Sales**', '${:,}'.format(int(qs21[3])), percent_of_change(qs20[3], qs21[3]))                

            #st.divider()
            with coly:
                display_month_data_x(sales21, sales20)

        if year_select == '2020':
    
            display_metrics(sales20, sales19, note='20')

            with col3:

                st.header('Sales by Month')
                plot_bar_chart_ms(format_for_chart_ms(sales20))

            with colz:
                
                st.header('Quarterly Sales')
                
                col6, col7, col8 = st.columns([.3, .4, .3])
                
                col7.metric('**Q1 Total Sales**', '${:,}'.format(int(qs20[0])), percent_of_change(qs19[0], qs20[0]))

                col7.metric('**Q2 Total Sales**', '${:,}'.format(int(qs20[1])), percent_of_change(qs19[1], qs20[1]))
                
                col7.metric('**Q3 Total Sales**', '${:,}'.format(int(qs20[2])), percent_of_change(qs19[2], qs20[2]))

                col7.metric('**Q4 Total Sales**', '${:,}'.format(int(qs20[3])), percent_of_change(qs19[3], qs20[3]))
                
            #st.divider()
            with coly:
                display_month_data_x(sales20, sales19)

        if year_select == '2019':
    
            display_metrics(sales19, sales18, note='19')

            with col3:

                st.header('Sales by Month')
                plot_bar_chart_ms(format_for_chart_ms(sales19))

            with colz:
                
                st.header('Quarterly Sales')
                
                col6, col7, col8 = st.columns([.3, .4, .3])
                
                col7.metric('**Q1 Total Sales**', '${:,}'.format(int(qs19[0])), percent_of_change(qs18[0], qs19[0]))

                col7.metric('**Q2 Total Sales**', '${:,}'.format(int(qs19[1])), percent_of_change(qs18[1], qs19[1]))
                
                col7.metric('**Q3 Total Sales**', '${:,}'.format(int(qs19[2])), percent_of_change(qs18[2], qs19[2]))

                col7.metric('**Q4 Total Sales**', '${:,}'.format(int(qs19[3])), percent_of_change(qs18[3], qs19[3]))
                
            #st.divider()
            with coly:
                display_month_data_x(sales19, sales18)

        if year_select == '2018':
    
            display_metrics(sales18, sales17, note='18')

            with col3:

                st.header('Sales by Month')
                plot_bar_chart_ms(format_for_chart_ms(sales18))

            with colz:
                
                st.header('Quarterly Sales')
                
                col6, col7, col8 = st.columns([.3, .4, .3])
                
                col7.metric('**Q1 Total Sales**', '${:,}'.format(int(qs18[0])), percent_of_change(qs17[0], qs18[0]))

                col7.metric('**Q2 Total Sales**', '${:,}'.format(int(qs18[1])), percent_of_change(qs17[1], qs18[1]))
                
                col7.metric('**Q3 Total Sales**', '${:,}'.format(int(qs18[2])), percent_of_change(qs17[2], qs18[2]))

                col7.metric('**Q4 Total Sales**', '${:,}'.format(int(qs18[3])), percent_of_change(qs17[3], qs18[3]))
                
            #st.divider()
            with coly:
                display_month_data_x(sales18, sales17)

        if year_select == '2017':
    
            display_metrics(sales17, sales16, note='17')

            with col3:

                st.header('Sales by Month')
                plot_bar_chart_ms(format_for_chart_ms(sales17))

            with colz:
                
                st.header('Quarterly Sales')
                
                col6, col7, col8 = st.columns([.3, .4, .3])
                
                col7.metric('**Q1 Total Sales**', '${:,}'.format(int(qs17[0])), percent_of_change(qs16[0], qs17[0]))

                col7.metric('**Q2 Total Sales**', '${:,}'.format(int(qs17[1])), percent_of_change(qs16[1], qs17[1]))
                
                col7.metric('**Q3 Total Sales**', '${:,}'.format(int(qs17[2])), percent_of_change(qs16[2], qs17[2]))

                col7.metric('**Q4 Total Sales**', '${:,}'.format(int(qs17[3])), percent_of_change(qs16[3], qs17[3]))
                
            #st.divider()
            with coly:
                display_month_data_x(sales17, sales16)

        if year_select == '2016':
    
            display_metrics(sales16, sales15, note='16')

            with col3:

                st.header('Sales by Month')
                plot_bar_chart_ms(format_for_chart_ms(sales16))

            with colz:
                
                st.header('Quarterly Sales')
                
                col6, col7, col8 = st.columns([.3, .4, .3])
                
                col7.metric('**Q1 Total Sales**', '${:,}'.format(int(qs16[0])), percent_of_change(qs15[0], qs16[0]))

                col7.metric('**Q2 Total Sales**', '${:,}'.format(int(qs16[1])), percent_of_change(qs15[1], qs16[1]))
                
                col7.metric('**Q3 Total Sales**', '${:,}'.format(int(qs16[2])), percent_of_change(qs15[2], qs16[2]))

                col7.metric('**Q4 Total Sales**', '${:,}'.format(int(qs16[3])), percent_of_change(qs15[3], qs16[3]))
                
            #st.divider()
            with coly:
                display_month_data_x(sales16, sales15)

        if year_select == '2015':
    
            display_metrics(sales15, sales14, note='15')

            with col3:

                st.header('Sales by Month')
                plot_bar_chart_ms(format_for_chart_ms(sales15))

            with colz:
                
                st.header('Quarterly Sales')
                
                col6, col7, col8 = st.columns([.3, .4, .3])
                
                col7.metric('**Q1 Total Sales**', '${:,}'.format(int(qs15[0])), percent_of_change(qs14[0], qs15[0]))

                col7.metric('**Q2 Total Sales**', '${:,}'.format(int(qs15[1])), percent_of_change(qs14[1], qs15[1]))
                
                col7.metric('**Q3 Total Sales**', '${:,}'.format(int(qs15[2])), percent_of_change(qs14[2], qs15[2]))

                col7.metric('**Q4 Total Sales**', '${:,}'.format(int(qs15[3])), percent_of_change(qs14[3], qs15[3]))
                
            #st.divider()
            with coly:
                display_month_data_x(sales15, sales14)

        if year_select == '2014':
    
            display_metrics(sales14, sales13, note='14')

            with col3:

                st.header('Sales by Month')
                plot_bar_chart_ms(format_for_chart_ms(sales14))

            with colz:
                
                st.header('Quarterly Sales')
                
                col6, col7, col8 = st.columns([.3, .4, .3])
                
                
                col7.metric('**Q1 Total Sales**', '${:,}'.format(int(qs14[0])), percent_of_change(qs13[0], qs14[0]))

                col7.metric('**Q2 Total Sales**', '${:,}'.format(int(qs14[1])), percent_of_change(qs13[1], qs14[1]))
                
                col7.metric('**Q3 Total Sales**', '${:,}'.format(int(qs14[2])), percent_of_change(qs13[2], qs14[2]))

                col7.metric('**Q4 Total Sales**', '${:,}'.format(int(qs14[3])), percent_of_change(qs13[3], qs14[3]))
                    
            #st.divider()
            with coly:
                display_month_data_x(sales14, sales13)

        if year_select == '2013':
    
            display_metrics(sales13, note='13')

            with col3:

                st.header('Sales by Month')
                plot_bar_chart_ms(format_for_chart_ms(sales13))

            with colz:
                
                st.header('Quarterly Sales')
                
                col6, col7, col8 = st.columns([.3, .4, .3])
                
                col7.metric('**Q1 Total Sales**', '${:,}'.format(int(qs13[0])))

                col7.metric('**Q2 Total Sales**', '${:,}'.format(int(qs13[1])))
                
                col7.metric('**Q3 Total Sales**', '${:,}'.format(int(qs13[2])))

                col7.metric('**Q4 Total Sales**', '${:,}'.format(int(qs13[3])))
    
            #st.divider()
            with coly:
                display_month_data_x(sales13)

    

