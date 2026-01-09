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
from datetime import datetime, timedelta, date
import openpyxl
import streamlit_shadcn_ui as ui
#from streamlit_extras.metric_cards import style_metric_cards
from streamlit_option_menu import option_menu
#from fpdf import FPDF
#import base64
from data.load import load_all_data




# ----------------------------------------------
# MAKE VARIABLES FOR REAL TIME DATA CALCULATIONS
# ----------------------------------------------

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


# --------------------
# MAKE DATA ACCESSIBLE
# --------------------

df, df_quotes, df_cogs, df_shipstat_23, df_shipstat_24, df_qb, df_hsd, df_hist, unique_customer_list, master_customer_list, wholesale_list = load_all_data()


# ----------------------------
# HELPER FUNCTION - VERIFY INT
# ----------------------------

def safe_int(x, default=0) -> int:
    if x is None:
        return default
    if isinstance(x, str):
        x = x.strip()
        if x == "":
            return default
        # optional: remove commas
        x = x.replace(",", "")
    try:
        return int(float(x))
    except (ValueError, TypeError):
        return default

# --------------------------------------------------
# DEFINE A FUNCTION TO CALCULATE AND DISPLAY A DELTA
# --------------------------------------------------

@st.cache_data
def percent_of_change(num1, num2):
    
    delta = num2 - num1
    if num1 == 0:
        perc_change = 100
    else:
        perc_change = (delta / num1) * 100
    if delta > 0:
        v = '+'
    else:
        v = ''

    return '{}{:,.2f}% from last year'.format(v, perc_change)


# ----------------------------------------------------
# DEFINE A FUNCTION TO CALCULATE PERCENTAGE OF A TOTAL 
# ----------------------------------------------------

def percent_of_sales(type1, type2):

    total = type1 + type2
    
    if total == 0:
        return 0
    else:
        answer = (type1 / total) * 100
    
    return answer


# ------------------------------------------------------
# DEFINE A FUNCTION TO CONVERT MONTH STRING TO NUMERICAL
# ------------------------------------------------------

def month_to_num(month):
    months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
    ]
    return (months.index(month) + 1)

# -----------------------------------------------------------------
# DEFINE A FUNCTION TO CONVERT NUMERICAL MONTH TO STRING MONTH NAME
# -----------------------------------------------------------------

def num_to_month(month_num):
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    return months[month_num - 1]


# -------------------------------------------------------------
# FUNCTION TO EXTRACT MONTHLY SALES DATA / WHOLESALE VS. RETAIL
# -------------------------------------------------------------

@st.cache_data
def get_monthly_sales_wvr(df, year):
    # Ensure 'order_date' is in datetime format
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
   
    # Initialize sales dictionary
    months = ["January", "February", "March", "April", "May", "June", 
              "July", "August", "September", "October", "November", "December"]
    sales_dict = {month: [0, 0] for month in months}
    
    # Filter dataset to the required year
    df = df[df["order_date"].dt.year == year]

    # Convert order_date to month names
    df["month"] = df["order_date"].dt.month.map(lambda x: months[x - 1])

    # Determine if the customer is wholesale
    df["is_wholesale"] = df["customer"].isin(wholesale_list)

    # Group by month
    grouped = df.groupby("month")

    for month, group in grouped:
        # Sum of sales for wholesale customers
        sales_dict[month][0] = group.loc[group["is_wholesale"], "total_line_item_spend"].sum()
        # Sum of sales for non-wholesale customers
        sales_dict[month][1] = group.loc[~group["is_wholesale"], "total_line_item_spend"].sum()

    return sales_dict


# ---------------------------------------------------
# FUNCTION TO MAKE THE BEGINNING OF A YEAR A VARIABLE
# ---------------------------------------------------

def beginning_of_year(dt: datetime) -> datetime:
    return datetime(dt.year, 1, 1)


# ----------------------------------------------------------
# MONTHLY SALES YEAR TO DATE WITH WHOLESALE VS. RETAIL SALES
# ----------------------------------------------------------

@st.cache_data
def get_monthly_sales_wvr_ytd():

    sales_dict = {'January': [0, 0], 'February': [0, 0], 'March': [0, 0], 'April': [0, 0], 'May': [0, 0], 'June': [0, 0], 'July': [0, 0], 'August': [0, 0], 'September': [0, 0], 'October': [0, 0], 'November': [0, 0], 'December': [0, 0]}
    sales_dict_minus1 = {'January': [0, 0], 'February': [0, 0], 'March': [0, 0], 'April': [0, 0], 'May': [0, 0], 'June': [0, 0], 'July': [0, 0], 'August': [0, 0], 'September': [0, 0], 'October': [0, 0], 'November': [0, 0], 'December': [0, 0]}
    sales_dict_minus2 = {'January': [0, 0], 'February': [0, 0], 'March': [0, 0], 'April': [0, 0], 'May': [0, 0], 'June': [0, 0], 'July': [0, 0], 'August': [0, 0], 'September': [0, 0], 'October': [0, 0], 'November': [0, 0], 'December': [0, 0]}
    sales_dict_minus3 = {'January': [0, 0], 'February': [0, 0], 'March': [0, 0], 'April': [0, 0], 'May': [0, 0], 'June': [0, 0], 'July': [0, 0], 'August': [0, 0], 'September': [0, 0], 'October': [0, 0], 'November': [0, 0], 'December': [0, 0]}

    idx = 0

    for cust in df.customer:

        order_date = df.iloc[idx].order_date
        month = num_to_month(df.iloc[idx].order_date.month)

        if three_years_ago >= order_date >= beginning_of_year(three_years_ago):
            if cust in wholesale_list:
                sales_dict_minus3[month][0] += df.iloc[idx].total_line_item_spend
            else:
                sales_dict_minus3[month][1] += df.iloc[idx].total_line_item_spend
    
        elif two_years_ago >= order_date >= beginning_of_year(two_years_ago):
            if cust in wholesale_list:
                sales_dict_minus2[month][0] += df.iloc[idx].total_line_item_spend
            else:
                sales_dict_minus2[month][1] += df.iloc[idx].total_line_item_spend 
                
        elif one_year_ago >= order_date >= beginning_of_year(one_year_ago):
            if cust in wholesale_list:
                sales_dict_minus1[month][0] += df.iloc[idx].total_line_item_spend
            else:
                sales_dict_minus1[month][1] += df.iloc[idx].total_line_item_spend 
                
        elif today >= order_date >= beginning_of_year(today):
            if cust in wholesale_list:
                sales_dict[month][0] += df.iloc[idx].total_line_item_spend
            else:
                sales_dict[month][1] += df.iloc[idx].total_line_item_spend 
                
        idx += 1
    
    return sales_dict, sales_dict_minus1, sales_dict_minus2, sales_dict_minus3


# ----------------------------------------------------
# GENERATE DICTIONARY OF MONTHLY SALES - FOR DASHBOARD
# ----------------------------------------------------

@st.cache_data
def get_monthly_sales_v2(df, year):
    # Ensure 'order_date' is in datetime format
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

    # Initialize sales dictionary
    months = ["January", "February", "March", "April", "May", "June", 
              "July", "August", "September", "October", "November", "December"]
    sales_dict = {month: [[0, 0], [0, 0], [0]] for month in months}
    
    # Filter dataset to the required year
    df = df[df["order_date"].dt.year == year]
    
    # Convert order_date to month names
    df["month"] = df["order_date"].dt.month.map(lambda x: months[x - 1])
    
    # Determine if the sale is from channel "F"
    df["is_F"] = df["channel"].str.startswith("F")

    # Identify Magic/MFX items
    df["is_magic"] = df["line_item"].str.startswith(("Magic", "MFX")) | df["item_sku"].str.startswith(("Magic", "MFX"))

    # Group by month
    for month, group in df.groupby("month"):
        # Total spend for channel "F"
        sales_dict[month][0][0] = group.loc[group["is_F"], "total_line_item_spend"].sum()
        # Count of unique sales orders for channel "F"
        sales_dict[month][0][1] = group.loc[group["is_F"], "sales_order"].nunique()
        
        # Total spend for non-"F" channels
        sales_dict[month][1][0] = group.loc[~group["is_F"], "total_line_item_spend"].sum()
        # Count of unique sales orders for non-"F" channels
        sales_dict[month][1][1] = group.loc[~group["is_F"], "sales_order"].nunique()
        
        # Total spend for Magic/MFX items
        sales_dict[month][2][0] = group.loc[group["is_magic"], "total_line_item_spend"].sum()

    return sales_dict


# -------------------------------------------------------------------
# CALCULATE YEAR TO DATE MONTHLY SALES FOR CURRENT AND LAST TWO YEARS 
# -------------------------------------------------------------------

@st.cache_data
def get_monthly_sales_ytd():

    unique_sales_orders = []
    unique_sales_orders_minus1 = []
    unique_sales_orders_minus2 = []
    unique_sales_orders_minus3 = []
    

    sales_dict = {'January': [[0, 0], [0, 0], [0]], 'February': [[0, 0], [0, 0], [0]], 'March': [[0, 0], [0, 0], [0]], 'April': [[0, 0], [0, 0], [0]], 'May': [[0, 0], [0, 0], [0]], 'June': [[0, 0], [0, 0], [0]], 'July': [[0, 0], [0, 0], [0]], 'August': [[0, 0], [0, 0], [0]], 'September': [[0, 0], [0, 0], [0]], 'October': [[0, 0], [0, 0], [0]], 'November': [[0, 0], [0, 0], [0]], 'December': [[0, 0], [0, 0], [0]]}
    sales_dict_minus1 = {'January': [[0, 0], [0, 0], [0]], 'February': [[0, 0], [0, 0], [0]], 'March': [[0, 0], [0, 0], [0]], 'April': [[0, 0], [0, 0], [0]], 'May': [[0, 0], [0, 0], [0]], 'June': [[0, 0], [0, 0], [0]], 'July': [[0, 0], [0, 0], [0]], 'August': [[0, 0], [0, 0], [0]], 'September': [[0, 0], [0, 0], [0]], 'October': [[0, 0], [0, 0], [0]], 'November': [[0, 0], [0, 0], [0]], 'December': [[0, 0], [0, 0], [0]]}
    sales_dict_minus2 = {'January': [[0, 0], [0, 0], [0]], 'February': [[0, 0], [0, 0], [0]], 'March': [[0, 0], [0, 0], [0]], 'April': [[0, 0], [0, 0], [0]], 'May': [[0, 0], [0, 0], [0]], 'June': [[0, 0], [0, 0], [0]], 'July': [[0, 0], [0, 0], [0]], 'August': [[0, 0], [0, 0], [0]], 'September': [[0, 0], [0, 0], [0]], 'October': [[0, 0], [0, 0], [0]], 'November': [[0, 0], [0, 0], [0]], 'December': [[0, 0], [0, 0], [0]]}
    sales_dict_minus3 = {'January': [[0, 0], [0, 0], [0]], 'February': [[0, 0], [0, 0], [0]], 'March': [[0, 0], [0, 0], [0]], 'April': [[0, 0], [0, 0], [0]], 'May': [[0, 0], [0, 0], [0]], 'June': [[0, 0], [0, 0], [0]], 'July': [[0, 0], [0, 0], [0]], 'August': [[0, 0], [0, 0], [0]], 'September': [[0, 0], [0, 0], [0]], 'October': [[0, 0], [0, 0], [0]], 'November': [[0, 0], [0, 0], [0]], 'December': [[0, 0], [0, 0], [0]]}


    idx = 0

    for sale in df.sales_order:
    
        
        order_date = df.iloc[idx].order_date
        month = num_to_month(df.iloc[idx].order_date.month)
            
        if df.iloc[idx].channel[0] == 'F':

            if three_years_ago.date() >= order_date.date() >= beginning_of_year(three_years_ago).date():
                sales_dict_minus3[month][0][0] += df.iloc[idx].total_line_item_spend
                if sale not in unique_sales_orders_minus3:
                    sales_dict_minus3[month][0][1] += 1
                    unique_sales_orders_minus3.append(sale)
                    
            if two_years_ago.date() >= order_date.date() >= beginning_of_year(two_years_ago).date():
                sales_dict_minus2[month][0][0] += df.iloc[idx].total_line_item_spend
                if sale not in unique_sales_orders_minus2:
                    sales_dict_minus2[month][0][1] += 1
                    unique_sales_orders_minus2.append(sale)
                    
            elif one_year_ago.date() >= order_date.date() >= beginning_of_year(one_year_ago).date():
                sales_dict_minus1[month][0][0] += df.iloc[idx].total_line_item_spend
                if sale not in unique_sales_orders_minus1:
                    sales_dict_minus1[month][0][1] += 1
                    unique_sales_orders_minus1.append(sale)
                    
            elif today.date() >= order_date.date() >= beginning_of_year(today).date():
                sales_dict[month][0][0] += df.iloc[idx].total_line_item_spend
                if sale not in unique_sales_orders:
                    sales_dict[month][0][1] += 1
                    unique_sales_orders.append(sale)

        else:

            if three_years_ago.date() >= order_date.date() >= beginning_of_year(three_years_ago).date():
                sales_dict_minus3[month][1][0] += df.iloc[idx].total_line_item_spend 
                if df.iloc[idx].line_item[:5] == 'Magic' or df.iloc[idx].line_item[:3] == 'MFX':
                    sales_dict_minus3[month][2][0] += df.iloc[idx].total_line_item_spend
                if sale not in unique_sales_orders_minus3:
                    sales_dict_minus3[month][1][1] += 1
                    unique_sales_orders_minus3.append(sale)
                    
            if two_years_ago.date() >= order_date.date() >= beginning_of_year(two_years_ago).date():
                sales_dict_minus2[month][1][0] += df.iloc[idx].total_line_item_spend 
                if df.iloc[idx].line_item[:5] == 'Magic' or df.iloc[idx].line_item[:3] == 'MFX':
                    sales_dict_minus2[month][2][0] += df.iloc[idx].total_line_item_spend
                if sale not in unique_sales_orders_minus2:
                    sales_dict_minus2[month][1][1] += 1
                    unique_sales_orders_minus2.append(sale)
                    
            elif one_year_ago.date() >= order_date.date() >= beginning_of_year(one_year_ago).date():
                sales_dict_minus1[month][1][0] += df.iloc[idx].total_line_item_spend
                if df.iloc[idx].line_item[:5] == 'Magic' or df.iloc[idx].line_item[:3] == 'MFX':
                    sales_dict_minus1[month][2][0] += df.iloc[idx].total_line_item_spend
                if sale not in unique_sales_orders_minus1:
                    sales_dict_minus1[month][1][1] += 1
                    unique_sales_orders_minus1.append(sale)
                    
            elif today.date() >= order_date.date() >= beginning_of_year(today).date():
                sales_dict[month][1][0] += df.iloc[idx].total_line_item_spend
                if df.iloc[idx].line_item[:5] == 'Magic' or df.iloc[idx].line_item[:3] == 'MFX':
                    sales_dict[month][2][0] += df.iloc[idx].total_line_item_spend
                if sale not in unique_sales_orders:
                    sales_dict[month][1][1] += 1
                    unique_sales_orders.append(sale)

        idx += 1

    return sales_dict, sales_dict_minus1, sales_dict_minus2, sales_dict_minus3


# ----------------------
# MONTHLY PRODUCT TOTALS
# ----------------------

@st.cache_data
def calc_monthly_totals_v2(sales_dict, months=['All']):
    total_sales = 0
    total_web = 0
    total_fulcrum = 0
    magic_sales = 0
    num_months = 0

    # Determine which months to iterate over
    if months == ['All']:
        selected_items = sales_dict.items()
    else:
        selected_items = ((m, sales) for m, sales in sales_dict.items() if m in months)

    # Loop over the selected months
    for m, sales in selected_items:
        web      = sales[0][0]
        fulcrum  = sales[1][0]
        magic    = sales[2][0]
        month_total = web + fulcrum

        total_sales   += month_total
        total_web     += web
        total_fulcrum += fulcrum
        magic_sales   += magic

        # Only count the month if total sales are at least 100
        if month_total >= 100:
            num_months += 1

    # Compute average monthly sales (if no month qualifies, set average to 0)
    avg_month = total_sales / num_months if num_months else 0

    # Compute percentages using your helper function (assumed to be defined elsewhere)
    total_web_perc     = percent_of_sales(total_web, total_fulcrum)
    total_fulcrum_perc = percent_of_sales(total_fulcrum, total_web)

    return total_sales, total_web_perc, total_fulcrum_perc, avg_month, magic_sales


# -------------------------------------------------------
# DEFINE A FUNCTION TO EXTRACT DATA FROM SALES DICTIONARY 
# -------------------------------------------------------

@st.cache_data
def extract_transaction_data(sales_dict, month='All'):
    if month == 'All':
        # Sum the wholesale and non-wholesale values over all months using generator expressions.
        sales_sum_web      = sum(sales[0][0] for sales in sales_dict.values())
        sales_sum_fulcrum  = sum(sales[1][0] for sales in sales_dict.values())
        total_trans_web    = sum(sales[0][1] for sales in sales_dict.values())
        total_trans_fulcrum= sum(sales[1][1] for sales in sales_dict.values())
    else:
        # For a specific month, extract values directly
        sales_sum_web       = sales_dict[month][0][0]
        sales_sum_fulcrum   = sales_dict[month][1][0]
        total_trans_web     = sales_dict[month][0][1]
        total_trans_fulcrum = sales_dict[month][1][1]
    
    sales_sum   = sales_sum_web + sales_sum_fulcrum
    total_trans = total_trans_web + total_trans_fulcrum

    # Calculate averages using inline conditional expressions
    avg_order         = sales_sum / total_trans if total_trans else 0
    avg_order_web     = sales_sum_web / total_trans_web if total_trans_web else 0
    avg_order_fulcrum = sales_sum_fulcrum / total_trans_fulcrum if total_trans_fulcrum else 0

    return [avg_order_web, avg_order_fulcrum, avg_order,
            sales_sum_web, sales_sum_fulcrum, sales_sum,
            total_trans_web, total_trans_fulcrum, total_trans]


# -------------------------------------------------------------
# FUNCTION TO CALCULATE METRICS OF HISTORICAL SALES (2013-2022)
# -------------------------------------------------------------

@st.cache_data
def calc_hist_metrics(sales_dict1, sales_dict2=None):

    sd1_wholesale = 0
    sd1_retail = 0
    sd1_tot = 0
    sd2_wholesale = 0
    sd2_retail = 0
    sd2_tot = 0
    
    sd1_wholesale_trans = 0
    sd1_retail_trans = 0
    sd1_trans_tot = 0
    sd2_wholesale_trans = 0
    sd2_retail_trans = 0
    sd2_trans_tot = 0

    sd1_avg_wholesale_trans = 0
    sd1_avg_retail_trans = 0
    sd1_avg_trans = 0
    sd2_avg_wholesale_trans = 0
    sd2_avg_retail_trans = 0
    sd2_avg_trans = 0
    
    sd1_avg_month = 0
    sd2_avg_month = 0 
    
    if sales_dict2 != None:

        for month, val in sales_dict1.items():
            sd1_wholesale += val[0][0]
            sd1_retail += val[1][0]
            
            sd1_wholesale_trans += val[0][1]
            sd1_retail_trans += val[1][1]
    
    
        for month, val in sales_dict2.items():
            sd2_wholesale += val[0][0]
            sd2_retail += val[1][0]
            
            sd2_wholesale_trans += val[0][1]
            sd2_retail_trans += val[1][1]

        sd1_tot = sd1_wholesale + sd1_retail
        sd2_tot = sd2_wholesale + sd2_retail
        sd1_trans_tot = sd1_wholesale_trans + sd1_retail_trans
        sd2_trans_tot = sd2_wholesale_trans + sd2_retail_trans

        if sd1_wholesale_trans == 0:
            sd1_avg_wholesale_trans = 0
        else:
            sd1_avg_wholesale_trans = sd1_wholesale / sd1_wholesale_trans
        if sd1_retail_trans == 0:
            sd1_avg_retail_trans = 0
        else:
            sd1_avg_retail_trans = sd1_retail / sd1_retail_trans
            

        sd1_avg_trans = sd1_tot / sd1_trans_tot
        sd1_avg_month = sd1_tot / 12
        
        if sd2_wholesale_trans == 0:
            sd2_avg_wholesale_trans = 0
        else:
            sd2_avg_wholesale_trans = sd2_wholesale / sd2_wholesale_trans
        if sd2_retail_trans == 0:
            sd2_avg_retail_trans = 0
        else:
            sd2_avg_retail_trans = sd2_retail / sd2_retail_trans
            
        sd2_avg_trans = sd2_tot / sd2_trans_tot
        sd2_avg_month = sd2_tot / 12

        return sd1_tot, sd1_trans_tot, sd1_avg_month, sd1_avg_trans, sd1_wholesale, sd1_retail, sd1_wholesale_trans, sd1_retail_trans, sd1_avg_wholesale_trans, sd1_avg_retail_trans, sd2_tot, sd2_trans_tot, sd2_avg_month, sd2_avg_trans, sd2_wholesale, sd2_retail, sd2_wholesale_trans, sd2_retail_trans, sd2_avg_wholesale_trans, sd2_avg_retail_trans

    else:     

        for month, val in sales_dict1.items():
            sd1_wholesale += val[0][0]
            sd1_retail += val[1][0]
            sd1_wholesale_trans += val[0][1]
            sd1_retail_trans += val[1][1]
            
        sd1_tot += sd1_wholesale + sd1_retail
        sd1_trans_tot += sd1_wholesale_trans + sd1_retail_trans

        sd1_avg_wholesale_trans = 0
        sd1_avg_retail_trans = sd1_retail / sd1_retail_trans
        sd1_avg_trans = sd1_tot / sd1_trans_tot    
        sd1_avg_month = sd1_tot / 5

        return sd1_tot, sd1_trans_tot, sd1_avg_month, sd1_avg_trans, sd1_wholesale, sd1_retail, sd1_wholesale_trans, sd1_retail_trans, sd1_avg_wholesale_trans, sd1_avg_retail_trans

    
# ---------------------------------------------------------
# FUNCTION TO CALCULATE QUARTLY SALES - WEBSITE VS. FULCRUM
# ---------------------------------------------------------

@st.cache_data
def quarterly_sales(year):

    q1_end = datetime(year, 3, 31)
    q2_start = datetime(year, 4, 1)
    q2_end = datetime(year, 6, 30)
    q3_start = datetime(year, 7, 1)
    q3_end = datetime(year, 9, 30)
    q4_start = datetime(year, 10, 1)
    q4_end = datetime(year, 12, 31)
    
    
    q1_count = [0, 0]
    q2_count = [0, 0]
    q3_count = [0, 0]
    q4_count = [0, 0]
    
    idx = 0
    
    for sale in df.sales_order:
        order_date = df.iloc[idx].order_date
        if df.iloc[idx].channel[0] == 'F':
            if q1_end.date() >= order_date.date() >= beginning_of_year(q1_end).date():
                q1_count[0] += df.iloc[idx].total_line_item_spend
            elif q2_end.date() >= order_date.date() >= q2_start.date():
                q2_count[0] += df.iloc[idx].total_line_item_spend
            elif q3_end.date() >= order_date.date() >= q3_start.date():
                q3_count[0] += df.iloc[idx].total_line_item_spend
            elif q4_end.date() >= order_date.date() >= q4_start.date():
                q4_count[0] += df.iloc[idx].total_line_item_spend
        else:
            if q1_end.date() >= order_date.date() >= beginning_of_year(q1_end).date():
                q1_count[1] += df.iloc[idx].total_line_item_spend
            elif q2_end.date() >= order_date.date() >= q2_start.date():
                q2_count[1] += df.iloc[idx].total_line_item_spend
            elif q3_end.date() >= order_date.date() >= q3_start.date():
                q3_count[1] += df.iloc[idx].total_line_item_spend
            elif q4_end.date() >= order_date.date() >= q4_start.date():
                q4_count[1] += df.iloc[idx].total_line_item_spend
    
        idx += 1
    
    return q1_count, q2_count, q3_count, q4_count


# --------------------------------------------------------------------
# FUNCTION TO CALCULATE WHOLESALE VS. RETAIL TOTALS - CURRENTLY UNUSED
# --------------------------------------------------------------------

def wholesale_retail_totals(monthly_sales_wVr):
    
    wholesale_totals = 0
    retail_totals = 0

    for month, sales in monthly_sales_wVr.items():
        wholesale_totals += sales[0]
        retail_totals += sales[1]

    return wholesale_totals, retail_totals


# -------------------------------------------------------------
# FUNCTION TO CALCULATE REALTIME TO-DATE REVENUE FOR COMPARISON
# -------------------------------------------------------------

def to_date_revenue(df, today=None):
    """
    Calculate year-to-date revenue for all years present in df, split by:
      - channel starting with 'F'
      - all other channels

    Returns
    -------
    dict[int, list[float, float]]
        {year: [sum_for_F_channels, sum_for_non_F_channels]}, sorted by year.
    """
    if today is None:
        today = pd.Timestamp.today().normalize()

    df = df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

    # Only keep rows with valid dates
    df = df.dropna(subset=["order_date"])

    # Flag channels starting with 'F'
    cond_F = df["channel"].astype(str).str.startswith("F")

    # All years present in the data, but not beyond the current year
    years = sorted(
        int(y) for y in df["order_date"].dt.year.unique()
        if int(y) <= today.year
    )

    results = {}

    for year in years:
        # Start: Jan 1 of that year
        start = pd.Timestamp(year=year, month=1, day=1)

        # End: same month/day as today, but in that year (YTD comparison)
        end_month, end_day = today.month, today.day
        try:
            end = pd.Timestamp(year=year, month=end_month, day=end_day)
        except ValueError:
            # Handles cases like Feb 29 -> use Feb 28 in non-leap years
            if end_month == 2 and end_day == 29:
                end = pd.Timestamp(year=year, month=2, day=28)
            else:
                raise

        # For the current year, we truly only want up to "today"
        if year == today.year:
            end = today

        mask = (df["order_date"] >= start) & (df["order_date"] <= end)

        results[year] = [
            df.loc[mask & cond_F, "total_line_item_spend"].sum(),
            df.loc[mask & ~cond_F, "total_line_item_spend"].sum(),
        ]

    return results


# -----------------------------------------------
# FUNCTION TO EXTRACT SALES OF MAGIC FX EQUIPMENT
# -----------------------------------------------

@st.cache_data
def magic_sales_data():
    
    mfx_list = []

    mfx_profit = 0
    mfx_costs = 0
    mfx_rev = 0

    
    idx = 0
    
    for item in df_cogs.item:

        if item[:3] == 'MFX' or item[:5] == 'Magic':
            mfx_list.append('{} x {} = ${:,.2f} total, ${:,.2f} each. Total Profit = ${:,.2f}'.format(item, df_cogs.iloc[idx].quantity, df_cogs.iloc[idx].total_price, df_cogs.iloc[idx].unit_price, (df_cogs.iloc[idx].total_price - df_cogs.iloc[idx].total_cost)))
            mfx_profit += df_cogs.iloc[idx].total_price - df_cogs.iloc[idx].total_cost
            mfx_costs += df_cogs.iloc[idx].total_cost
            mfx_rev += df_cogs.iloc[idx].total_price


        idx += 1
        
    return mfx_rev, mfx_costs, mfx_profit


# --------------------------------------------------
# FUNCTION TO EXTRACT DAILY SALES - CURRENTLY UNUSED
# --------------------------------------------------

def daily_sales(month):

    daily_sales23 = []
    daily_sales24 = []
    daily_sales25 = []
                
    month_num = month_to_num(month)

    for i in range(days_in_month(month)):
        daily_sales23.append(0)
        daily_sales24.append(0)
        daily_sales25.append(0)
        
    idx = 0 
    
    for sale in df.sales_order:
        if df.iloc[idx].order_date.month == int(month_num):
            if df.iloc[idx].order_date.year == 2025:
                daily_sales25[(df.iloc[idx].order_date.day) - 1] += df.iloc[idx].total_line_item_spend
            if df.iloc[idx].order_date.year == 2024:
                daily_sales24[(df.iloc[idx].order_date.day) - 1] += df.iloc[idx].total_line_item_spend
            if df.iloc[idx].order_date.year == 2023:
                daily_sales23[(df.iloc[idx].order_date.day) - 1] += df.iloc[idx].total_line_item_spend

        idx += 1
            
    return daily_sales23, daily_sales24, daily_sales25
    

# -----------------------------------------------------------
# ENSURE DATES FROM HISTORICAL DATA ARE FORMATTED IN DATETIME
# -----------------------------------------------------------

df_hist['order_date'] = pd.to_datetime(df_hist['order_date'])
    

# ----------------------------------------------------------------------------
# FUNCTION TO EXTRACT HISTORICAL CUSTOMER DATA - PRODUCT & SALES (2013 - 2022) 
# ----------------------------------------------------------------------------

def hist_cust_data(customer):
    
    target_years = [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]
    
    spending_dict = {2013: 0, 2014: 0, 2015: 0, 2016: 0, 2017: 0, 2018: 0, 2019: 0, 2020: 0, 2021: 0, 2022: 0}
    spending_total = 0

    jets = ['DMX Jet', 'Pro Jet', 'Power Jet', 'Micro Jet MKI', 'Micro Jet MKII', 'Cryo Clamp MKI', 'Cryo Clamp', 'Quad Jet']
    handhelds = ['Handheld MKI', 'Handheld MKII']
    controllers = ['DMX Controller', 'LCD Controller', 'The Button MKI', 'The Button', 'Shomaster', 'Shostarter', 'Power Controller']
    accessories = ['Travel Case', 'Original Travel Case', 'Back Pack', 'Manifold', '20LB Tank Cover', '50LB Tank Cover', 'LED Attachment I', 'LED Attachment II', 'Power Pack', 'Confetti Blower']
    
    hist_products = {
        'hh_mk2': 'Handheld MKII',
        'hh_mk1': 'Handheld MKI', 
        'travel_case': 'Travel Case',
        'travel_case_og': 'Original Travel Case', 
        'backpack': 'Back Pack',
        'jets_og': 'DMX Jet',
        'pro_jet': 'Pro Jet',
        'power_jet': 'Power Jet',
        'micro_jet_mk1': 'Micro Jet MKI',
        'micro_jet_mk2': 'Micro Jet MKII',
        'cryo_clamp_mk1': 'Cryo Clamp MKI',
        'cryo_clamp_mk2': 'Cryo Clamp',
        'quad_jet': 'Quad Jet',
        'dmx_controller': 'DMX Controller',
        'lcd_controller': 'LCD Controller',
        'the_button_mk1': 'The Button MKI',
        'the_button_mk2': 'The Button',
        'shomaster': 'Shomaster',
        'shostarter': 'Shostarter',
        'power_controller': 'Power Controller',
        'hoses': 'Hoses',
        'manifold': 'Manifold',
        'ctc_20': '20LB Tank Cover',
        'ctc_50': '50LB Tank Cover',
        'led_attachment_mk1': 'LED Attachment I', 
        'led_attachment_mk2': 'LED Attachment II',
        'power_pack': 'Power Pack',
        'confetti_blower': 'Confetti Blower',
        
    }
    
    cust_products = {
        'hh_mk2': [0, []],
        'hh_mk1': [0, []], 
        'travel_case': [0, []],
        'travel_case_og': [0, []], 
        'backpack': [0, []],
        'jets_og': [0, []],
        'pro_jet': [0, []],
        'power_jet': [0, []],
        'micro_jet_mk1': [0, []],
        'micro_jet_mk2': [0, []],
        'cryo_clamp_mk1': [0, []],
        'cryo_clamp_mk2': [0, []],
        'quad_jet': [0, []],
        'dmx_controller': [0, []],
        'lcd_controller': [0, []],
        'the_button_mk1': [0, []],
        'the_button_mk2': [0, []],
        'shomaster': [0, []],
        'shostarter': [0, []],
        'power_controller': [0, []],
        'hoses': [0, []],
        'manifold': [0, []],
        'ctc_20': [0, []],
        'ctc_50': [0, []],
        'led_attachment_mk1': [0, []], 
        'led_attachment_mk2': [0, []],
        'power_pack': [0, []],
        'confetti_blower': [0, []],
        
    }
            
    cust_rows = df_hist.loc[df_hist['customer'] == customer].reset_index()
    
    cust_filtered = cust_rows[cust_rows['order_date'].dt.year.isin(target_years)]
    
    cust_filtered['year'] = cust_filtered['order_date'].dt.year
    spending_dict = cust_filtered.groupby('year')['total_spend'].sum().to_dict()
    
    spending_total = sum(spending_dict.values())

    idx = 0
    for sale in cust_filtered.order_date:
        for prod in cust_products.keys():
            raw = cust_filtered.iloc[idx][prod]
    
            # Skip real NaNs / None
            if raw is None or (isinstance(raw, float) and np.isnan(raw)) or pd.isna(raw):
                continue
    
            # Skip blank / whitespace strings
            if isinstance(raw, str) and raw.strip() == "":
                continue
    
            qty = safe_int(raw)  # <- your helper
    
            if qty == 0:
                continue
    
            cust_products[prod][0] += qty
            cust_products[prod][1].append((qty, str(cust_filtered.iloc[idx].order_date.date())))
    
        idx += 1

    # CONVERT TO READABLE NAMES
    keyed_cust_products = dict(zip(hist_products.values(), cust_products.values()))

    # SPLIT DICT INTO CATEGORY DICTS
    jet_dict = {key: keyed_cust_products[key] for key in jets}
    handheld_dict = {key: keyed_cust_products[key] for key in handhelds}
    controller_dict = {key: keyed_cust_products[key] for key in controllers}
    acc_dict = {key: keyed_cust_products[key] for key in accessories}

    return spending_dict, spending_total, jet_dict, handheld_dict, controller_dict, acc_dict


# -------------------------------------------------------
# FUNCTION TO EXTRACT HISTORICAL SALES DATA (2013 - 2022) 
# -------------------------------------------------------

@st.cache_data
def hist_annual_sales():
    # Define month names
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    
    # Template dictionary for a year: for each month, a list of two lists:
    # index 0: [wholesale_total, wholesale_order_count]
    # index 1: [non_wholesale_total, non_wholesale_order_count]
    empty_year_dict = {month: [[0, 0], [0, 0]] for month in months}
    
    # Work on a copy of df_hist
    #df = df_hist.copy()
    
    # Ensure 'order_date' is datetime
    df_hist["order_date"] = pd.to_datetime(df_hist["order_date"], errors="coerce")
    
    # Create new columns for year and month (as month names)
    df_hist["year"] = df_hist["order_date"].dt.year
    df_hist["month"] = df_hist["order_date"].dt.month.apply(lambda m: months[int(m)-1] if pd.notnull(m) else None)
    
    # Convert 'total_sale' to numeric (if not already) and fill invalid values with 0
    df_hist["total_sale"] = pd.to_numeric(df_hist["total_sale"], errors="coerce").fillna(0)
    
    # Create a wholesale flag column (True if customer is in wholesale_list)
    df_hist["wholesale"] = df_hist["customer"].isin(wholesale_list)
    
    # Group by year, month, and wholesale flag.
    # For each group, compute:
    #   - Sum of total_sale.
    #   - Count of orders (each row is one order).
    grouped = df_hist.groupby(["year", "month", "wholesale"]).agg(
        total_sale_sum=("total_sale", "sum"),
        order_count=("total_sale", "size")
    ).reset_index()
    
    # Prepare a dictionary to hold results for years 2013 to 2022.
    yearly_results = {yr: {month: [[0, 0], [0, 0]] for month in months} for yr in range(2013, 2023)}
    
    # Populate the results dictionary using the grouped data.
    for _, row in grouped.iterrows():
        yr = row["year"]
        month = row["month"]
        # Wholesale orders go in index 0; non-wholesale in index 1.
        idx = 0 if row["wholesale"] else 1
        if yr in yearly_results:
            yearly_results[yr][month][idx][0] = row["total_sale_sum"]
            yearly_results[yr][month][idx][1] = row["order_count"]
    
    # Extract results for each year. If a particular year has no data, use the empty template.
    sales13 = yearly_results.get(2013, empty_year_dict)
    sales14 = yearly_results.get(2014, empty_year_dict)
    sales15 = yearly_results.get(2015, empty_year_dict)
    sales16 = yearly_results.get(2016, empty_year_dict)
    sales17 = yearly_results.get(2017, empty_year_dict)
    sales18 = yearly_results.get(2018, empty_year_dict)
    sales19 = yearly_results.get(2019, empty_year_dict)
    sales20 = yearly_results.get(2020, empty_year_dict)
    sales21 = yearly_results.get(2021, empty_year_dict)
    sales22 = yearly_results.get(2022, empty_year_dict)
    
    return sales13, sales14, sales15, sales16, sales17, sales18, sales19, sales20, sales21, sales22


# --------------------------------------------------------------
# FUNCTION TO CALCULATE HISTORICAL QUARTERLY SALES (2013 - 2022)
# --------------------------------------------------------------

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
