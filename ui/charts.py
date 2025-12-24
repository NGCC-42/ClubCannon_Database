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



### CREATE DATE LISTS ###

months = ['All', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
months_x = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
years = ['2022', '2023', '2024', '2025', '2026']


# --------------------------------------------------
# FORMAT DICTIONARY HANDHELD DATA FOR CHART PLOTTING
# --------------------------------------------------

def format_for_chart_hh(data_dict):
    temp_dict = {'Years': [], 'Handheld Sales': []}

    for year, sales in data_dict.items():
        temp_dict['Years'].append(year)
              
        temp_dict['Handheld Sales'].append(sales)
                
    df = pd.DataFrame(temp_dict)
    
    return df


# ---------------------------------------------
# FUNCTION TO DISPLAY HANDHELD COMPARISON CHART
# ---------------------------------------------

def plot_bar_chart_hh(df):
    st.write(alt.Chart(df).mark_bar().encode(
        x=alt.X('Years', sort=None).title('Year'),
        y='Handheld Sales',
    ).properties(height=800, width=1150).configure_mark(
        color='limegreen'
    ))


# ------------------------------------------------------------
# FUNCTION TO CONVERT - SERIES --> DICT --> DATAFRAME
# ------------------------------------------------------------

def format_for_chart(series):
    
    temp_dict = {'Months': months_x,
                'Units Sold': []}
    
    for month in series[1:]:
        if len(temp_dict['Units Sold']) >= 12:
            pass
        else:
            temp_dict['Units Sold'].append(month)
    df = pd.DataFrame(temp_dict)
    
    return df


# --------------------------------------------
# FUNCTION TO PLOT BAR GRAPH FOR PRODUCT SALES
# --------------------------------------------

def plot_bar_chart(df):
    st.write(alt.Chart(df).mark_bar().encode(
        x=alt.X('Months', sort=None).title('Month'),
        y='Units Sold',
    ).properties(height=500, width=750).configure_mark(
        color='limegreen'
    ))


# -----------------------------------------
# DAILY SALES PLOT GRAPH - CURRENTLY UNUSED
# -----------------------------------------

def display_daily_plot(month, years=['All']):
    
    daily23, daily24, daily25 = daily_sales(month)
    col1.write(daily23)

    x = [i for i in range(len(daily24))]

    fig, ax = plt.subplots()

    if years == ['All']:
    
        ax.plot(x, daily23, label='2023', color='darkgreen', linewidth=2)
        ax.plot(x, daily24, label='2024', color='white', linewidth=2)
        ax.plot(x, daily25, label='2025', color='limegreen', linewidth=2)
        ax.set_facecolor('#000000')
        fig.set_facecolor('#000000')
        plt.yticks([1000, 2500, 5000, 7500, 10000, 15000, 20000, 25000])
        plt.tick_params(axis='x', colors='white')
        plt.tick_params(axis='y', colors='white')
        plt.ylim(0, 20000)
        #plt.fill_between(x, daily23, color='darkgreen')
        #plt.fill_between(x, daily24, color='white', alpha=0.7)
        #plt.fill_between(x, daily25, color='limegreen')
        #plt.title('Annual Comparison', color='green')
        plt.figure(figsize=(10,10))
    
        fig.legend()
        
        col2.pyplot(fig)

    elif years == ['2025']:
        
        ax.plot(x, daily25, label='2025', color='limegreen', linewidth=2)
        ax.set_facecolor('#000000')
        fig.set_facecolor('#000000')
        plt.yticks([1000, 2500, 5000, 7500, 10000, 15000, 20000, 25000])
   
        plt.tick_params(axis='x', colors='white')
        plt.tick_params(axis='y', colors='white')
        plt.ylim(0, 20000)
        plt.fill_between(x, daily25, color='limegreen')
        #plt.title('Annual Comparison', color='green')
        plt.figure(figsize=(10,10))
    
        #fig.legend()

        col2.pyplot(fig)
        
    elif years == ['2024']:
        
        ax.plot(x, daily24, label='2024', color='limegreen', linewidth=2)
        ax.set_facecolor('#000000')
        fig.set_facecolor('#000000')
        plt.yticks([1000, 2500, 5000, 7500, 10000, 15000, 20000, 25000])
   
        plt.tick_params(axis='x', colors='white')
        plt.tick_params(axis='y', colors='white')
        plt.ylim(0, 20000)
        plt.fill_between(x, daily24, color='limegreen')
        #plt.title('Annual Comparison', color='green')
        plt.figure(figsize=(10,10))
    
        #fig.legend()

        col2.pyplot(fig)

    elif years == ['2023']:
        
        ax.plot(x, daily23, label='2023', color='limegreen', linewidth=2)
        ax.set_facecolor('#000000')
        fig.set_facecolor('#000000')
        plt.yticks([1000, 2500, 5000, 7500, 10000, 15000, 20000, 25000])
   
        plt.tick_params(axis='x', colors='white')
        plt.tick_params(axis='y', colors='white')
        plt.ylim(0, 20000)
        plt.fill_between(x, daily23, color='limegreen')
        #plt.title('Annual Comparison', color='green')
        plt.figure(figsize=(10,10))
    
        #fig.legend()

        col2.pyplot(fig)
    
    return None


# --------------------------------------------------------------------
# FUNCTION TO FORMAT DATA FOR MONTHLY SALES GRAPH / DICT --> DATAFRAME
# --------------------------------------------------------------------

def format_for_chart_ms(data_dict, note=None):
    temp_dict = {'Months': months_x, 'Total Sales': []}
    
    for month, sales in data_dict.items():
        if len(temp_dict['Total Sales']) >= 12:
            pass
        else:
            temp_dict['Total Sales'].append(sales[0][0] + sales[1][0])
                
    df = pd.DataFrame(temp_dict)
    
    return df


# -----------------------------------------
# DISPLAY FUNCTION FOR MONTHLY SALES GRAPH
# -----------------------------------------

def plot_bar_chart_ms(df):
    st.write(alt.Chart(df).mark_bar().encode(
        x=alt.X('Months', sort=None).title('Month'),
        y='Total Sales',
    ).properties(height=500, width=700).configure_mark(
        color='limegreen'
    ))


# ----------------------------------------------------------------
# DISPLAY FUNCTION FOR MONTHLY SALES COMPARISON - CURRENTLY UNUSED
# ----------------------------------------------------------------

def plot_bar_chart_ms_comp(df):
    st.write(alt.Chart(df).mark_bar().encode(
        x=alt.X('Months', sort=None).title('Month'),
        y='Total Sales',
    ).properties(height=500, width=350).configure_mark(
        color='limegreen'
    ))


# ------------------------------------------------------
# FORMAT DATA FOR PRODUCT PIE CHART - DICT --> DATAFRAME
# ------------------------------------------------------

def format_for_pie_chart(dict, key=0):
    
    prods = []
    vals = []
    columns = ['Product', 'Totals']

    for prod, val in dict.items():
        prods.append(prod)
        vals.append(int(val[key]))
        
    df = pd.DataFrame(np.column_stack([prods, vals]), index=[prods], columns=columns)

    return df


# ------------------------------------------------------------------
# FORMAT DATA FOR LINE GRAPH - DICT --> DATAFRAME - CURRENTLY UNUSED
# ------------------------------------------------------------------
    
def format_for_line_graph(dict1, product, dict2=None, key=0):

    months = []
    units_sold = []
    columns = ['Months', 'Units Sold']

    for month, prod in dict1.items():
        months.append(month)
        units_sold.append(dict1[month][product][key])

    df = pd.DataFrame(np.column_stack([months, units_sold]), columns=columns)

    return df


# -------------------------------------------------
# DISPLAY FUNCTION FOR PRODUCT COMPARISON PIE CHART
# -------------------------------------------------
        
def display_pie_chart_comp(df):
    col1, col2 = st.columns(2)
    colors = ["rgb(115, 255, 165)", "rgb(88, 92, 89)", "rgb(7, 105, 7)", "rgb(0, 255, 0"]
    with col1:
        saleFig = px.pie(format_for_pie_chart(df), values='Totals', names='Product', title='Units', height=400, width=400)
        saleFig.update_layout(margin=dict(l=10, r=10, t=20, b=0))
        saleFig.update_traces(textfont_size=18, marker=dict(colors=colors))
        st.plotly_chart(saleFig, use_container_width=False)
    with col2:
        revFig = px.pie(format_for_pie_chart(df, 1), values='Totals', names='Product', title='Revenue', height=400, width=400)
        revFig.update_layout(margin=dict(l=10, r=10, t=20, b=0))
        revFig.update_traces(textfont_size=18, marker=dict(colors=colors))
        st.plotly_chart(revFig, use_container_width=False)        

    return None


# ------------------------------------------------------
# DISPLAY ANNUAL SALES COMPARISON LINE GRAPH - DASHBOARD
# ------------------------------------------------------

def plot_annual_comparison(x, years_to_plot='2025', col1=None, series_by_year=None, line_width=4.5, fig_width=12, fig_height=8):
    # Define year series mapping

    if series_by_year is None:
        series_by_year = {}
    
    year_series = {
        '2026': ['2023', '2024', '2025'],
        '2025': ['2022', '2023', '2024'],
        '2024': ['2022', '2023', '2024'],
        '2023': ['2022', '2023', '2024'],
        '2022': ['2021', '2022', '2023'],
        '2021': ['2020', '2021', '2022'],
        '2020': ['2019', '2020', '2021'],
        '2019': ['2018', '2019', '2020'],
        '2018': ['2017', '2018', '2019'],
        '2017': ['2016', '2017', '2018'],
        '2016': ['2015', '2016', '2017'],
        '2015': ['2014', '2015', '2016'],
        '2014': ['2013', '2014', '2015'],
        '2013': ['2013', '2014', '2015']
    }

    # Define corresponding colors
    colors = ['limegreen', 'white', 'grey']

    # Retrieve year labels based on selection
    selected_years = year_series.get(years_to_plot, ['2022', '2023', '2024'])

    # Create figure and axis with dynamic size
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=100)

    # Plot data dynamically with adjustable line width
    for idx, year in enumerate(selected_years):
        y = series_by_year.get(year, [])
        #ax.plot(x, series_by_year.get(year, []), label=year, color=colors[idx], linewidth=line_width)
        if not y:
            continue

        if len(y) != len(x):
            raise ValueError(
                f"x (len={len(x)}) and y (len={len(y)}) differ for year {year}"
            )
        ax.plot(x, y, label=year, color=colors[idx], linewidth=line_width)

    # Set background colors
    ax.set_facecolor('#000000')
    fig.patch.set_facecolor('#000000')

    # Customize tick labels for responsiveness
    ax.tick_params(axis='x', labelsize=25, colors='white')
    ax.tick_params(axis='y', labelsize=25, colors='white')

    # Set dynamic y-ticks based on data range
    #all_y_values = [globals().get(f"y{year}", []) for year in selected_years if globals().get(f"y{year}") is not None]
    #if all_y_values:
        #y_min = min(map(min, all_y_values))
        #y_max = max(map(max, all_y_values))
        #y_ticks = range(int(y_min // 20000) * 20000, int(y_max // 20000 + 2) * 20000, 20000)
        #ax.set_yticks(y_ticks)
    plt.yticks([20000, 40000, 60000, 80000, 100000, 120000, 140000, 160000, 180000, 200000, 220000, 240000, 260000, 280000])
    plt.tick_params(axis='x', colors='white')
    plt.tick_params(axis='y', colors='white')
    # Customize legend
    #ax.legend(fontsize=16, loc="upper right", frameon=False)
    fig.legend(fontsize=25)
    # Ensure proper figure scaling for Streamlit
    if col1 is not None:
        col1.pyplot(fig, use_container_width=True)
    else:
        st.pyplot(fig, use_container_width=True)


# ----------------------------------------------------------
# FORMAT FOR HISTORICAL PRODUCTS FUNCTION - CURRENTLY UNUSED
# ----------------------------------------------------------

def format_for_chart_product(data_dict, prod_label):
    temp_dict = {'Years': [], prod_label: []}

    for year, sales in data_dict.items():
        temp_dict['Years'].append(year)
              
        temp_dict[prod_label].append(sales)
                
    df = pd.DataFrame(temp_dict)
    
    return df


# -------------------------------------------------------
# DISPLAY HISTORICAL PRODUCT BAR CHART - CURRENTLY UNUSED
# -------------------------------------------------------

def plot_bar_chart_product(df, prod_label):
    st.write(alt.Chart(df).mark_bar().encode(
        x=alt.X('Years', sort=None).title('Year'),
        y=prod_label,
    ).properties(height=800, width=1400).configure_mark(
        color='limegreen'
    ))


# -------------------------------------------------
# FORMAT FOR HISTORICAL PRODUCTS FUNCTION - STACKED
# -------------------------------------------------

def format_for_chart_product_seg(data_dict, prod_label):
    """
    Format data for a segmented bar chart.
    
    Args:
        data_dict (dict): A dictionary where keys are years and values are dictionaries of product sales.
                         Example: {2021: {'Product A': 100, 'Product B': 200}}
    
    Returns:
        pd.DataFrame: A DataFrame suitable for a segmented bar chart.
    """
    temp_dict = {'Years': [], 'Product': [], 'Sales': []}

    for year, product_sales in data_dict.items():
        for product, sales in product_sales.items():
            temp_dict['Years'].append(year)
            temp_dict['Product'].append(product)
            temp_dict['Sales'].append(sales)
    
    return pd.DataFrame(temp_dict)


# ----------------------------------------------
# DISPLAY HISTORICAL PRODUCTS FUNCTION - STACKED
# ----------------------------------------------

def plot_bar_chart_product_seg(df, prod_label):
    """
    Plot a segmented bar chart using Altair.

    Args:
        df (pd.DataFrame): A DataFrame with columns 'Years', 'Product', and 'Sales'.
    """
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X('Years:O', title='Year'),
            y=alt.Y('sum(Sales):Q', title='Total Sales'),
            color=alt.Color('Product:N', title='Product', scale=alt.Scale(scheme='tableau10')),
            tooltip=['Years', 'Product', 'Sales'],
        )
        .properties(height=800, width=1400)
    )
    st.altair_chart(chart, use_container_width=True)