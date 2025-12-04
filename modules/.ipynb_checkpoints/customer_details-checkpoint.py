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

from data.load import load_all_data
from logic.analytics import (
    hist_cust_data,
    percent_of_change
)

from ui.components import style_metric_cards
from logic.customer_logic import compute_customer_details




def render_customer(df, df_qb, master_customer_list):
    
    cola, colb, colc = st.columns([0.25, 0.5, 0.25])

    with colb:
        st.header("Customer Details")
        text_input = st.multiselect(
            "Search Customers",
            options=master_customer_list,
            max_selections=1,
            placeholder="Start Typing Customer Name",
        )

    if len(text_input) >= 1:
        selected_customer = text_input[0]
    else:
        selected_customer = ""

    # Compute all customer data (or None)
    data = compute_customer_details(df, df_qb, selected_customer)

    with colb:
        st.header("")
        st.subheader("")

        if not selected_customer or data is None:
            st.info("Select a customer to view details.")
            return

        # ─── NEW SPENDING UNPACK ──────────────────────────────────────
        year_metrics = data["year_metrics"]              # [(year, spend, delta), ...]
        total_spending_all = data["total_spending_all"]

        num_years = len(year_metrics)
        cols = st.columns(num_years + 1)  # one per year + one for Total

        # Latest years (already last N in compute_customer_details)
        for idx, (year, spend, delta) in enumerate(year_metrics):
            cols[idx].metric(
                f"{year} Spending",
                f"${spend:,.2f}",
                delta,
            )

        # Total across all years (historical + recent)
        cols[-1].metric(
            "**Total Spending**",
            f"${total_spending_all:,.2f}",
            "",
        )
        # ──────────────────────────────────────────────────────────────

        style_metric_cards()

        # ─── UNPACK THE REST (unchanged keys) ────────────────────────
        jet_totals_cust = data["jet_totals_cust"]
        controller_totals_cust = data["controller_totals_cust"]
        cust_handheld_mk2_cnt = data["cust_handheld_mk2_cnt"]
        cust_handheld_mk1_cnt = data["cust_handheld_mk1_cnt"]
        cust_LED_mk2_cnt = data["cust_LED_mk2_cnt"]
        cust_LED_mk1_cnt = data["cust_LED_mk1_cnt"]
        cust_RC_cnt = data["cust_RC_cnt"]

        jet_list = data["jet_list"]
        controller_list = data["controller_list"]
        handheld_list = data["handheld_list"]
        hose_list = data["hose_list"]
        fittings_accessories_list = data["fittings_accessories_list"]
        misc_list = data["misc_list"]
        magic_list = data["magic_list"]
        # ──────────────────────────────────────────────────────────────

        # ---------------------------
        # Product totals summary
        # ---------------------------
        st.subheader("Product Totals:")
        col6, col7, col8 = st.columns(3)

        with col6.container(border=True):
            for jet, totl in jet_totals_cust.items():
                if totl > 0:
                    st.markdown(f" - **{jet}: {int(totl)}**")

        with col7.container(border=True):
            for controller, totl in controller_totals_cust.items():
                if totl > 0:
                    st.markdown(f" - **{controller}: {int(totl)}**")

        with col8.container(border=True):
            if cust_LED_mk2_cnt > 0:
                st.markdown(f" - **LED Attachment II: {int(cust_LED_mk2_cnt)}**")
            if cust_LED_mk1_cnt > 0:
                st.markdown(f" - **LED Attachment I: {int(cust_LED_mk1_cnt)}**")
            if cust_RC_cnt > 0:
                st.markdown(f" - **Road Cases: {int(cust_RC_cnt)}**")
            if cust_handheld_mk2_cnt > 0:
                st.markdown(f" - **Handheld MKII: {int(cust_handheld_mk2_cnt)}**")
            if cust_handheld_mk1_cnt > 0:
                st.markdown(f" - **Handheld MKI: {int(cust_handheld_mk1_cnt)}**")

        # ---------------------------
        # Category breakdown sections
        # ---------------------------
        if jet_list:
            with st.container(border=True):
                st.subheader("Stationary Jets:")
                for item in jet_list:
                    st.markdown(item)

        if controller_list:
            with st.container(border=True):
                st.subheader("Controllers:")
                for item in controller_list:
                    st.markdown(item)

        if handheld_list:
            with st.container(border=True):
                st.subheader("Handhelds:")
                for item in handheld_list:
                    st.markdown(item)

        if hose_list:
            with st.container(border=True):
                st.subheader("Hoses:")
                for item in hose_list:
                    st.markdown(item)

        if fittings_accessories_list:
            with st.container(border=True):
                st.subheader("Fittings & Accessories:")
                for item in fittings_accessories_list:
                    st.markdown(item)

        if misc_list:
            with st.container(border=True):
                st.subheader("Misc:")
                for item in misc_list:
                    st.markdown(item)

        if magic_list:
            with st.container(border=True):
                st.subheader("Magic FX:")
                for item in magic_list:
                    st.markdown(item)







"""
    cola, colb, colc = st.columns([.25, .5, .25])
    
    with colb:
        st.header('Customer Details')

        text_input = st.multiselect('Search Customers', 
                                   options=master_customer_list, 
                                   max_selections=1,
                                   placeholder='Start Typing Customer Name')
    
    if len(text_input) >= 1:
        text_input = text_input[0]
    else:
        text_input = ''

    
    ### PRODUCT CATEGORY LISTS ###
    sales_order_list = []
    jet_list = []
    controller_list = []
    misc_list = []
    magic_list = []
    hose_list = []
    fittings_accessories_list = []
    handheld_list = []
    
    ### PRODUCT TOTALS SUMMARY DICTS ###
    jet_totals_cust = {'Quad Jet': 0, 
                       'Pro Jet': 0, 
                       'Micro Jet MKII': 0,
                       'Micro Jet MKI': 0,
                       'Cryo Clamp': 0,
                       'Cryo Clamp MKI': 0,
                       'DMX Jet': 0,
                       'Power Jet': 0, 
                      }
    
    controller_totals_cust = {'The Button': 0,
                              'Shostarter': 0,
                              'Shomaster': 0,
                              'DMX Controller': 0,
                              'LCD Controller': 0,
                              'The Button MKI': 0,
                              'Power Controller': 0,                         
                             }
    
    cust_handheld_mk2_cnt = 0
    cust_handheld_mk1_cnt = 0
    cust_LED_mk2_cnt = 0
    cust_LED_mk1_cnt = 0
    cust_RC_cnt = 0
    
    ### LISTS OF HISTORICAL SALES FOR CUSTOMER ###
    spend_total = {2023: None, 2024: None, 2025: None}
    spend_total_2023 = 0.0
    spend_total_2024 = 0.0
    spend_total_2025 = 0.0
    sales_order_list = []
    
    idx = 0
    
    for customer in df.customer:
        
        if customer.upper() == text_input.upper():
            
            ### LOCATE AND PULL SPEND TOTALS FOR SELECTED CUSTOMER AND ADD TO LISTS ###
            if df.iloc[idx].ordered_year == 2023:
                spend_total_2023 += df.iloc[idx].total_line_item_spend
            elif df.iloc[idx].ordered_year == 2024:
                spend_total_2024 += df.iloc[idx].total_line_item_spend
            elif df.iloc[idx].ordered_year == 2025:
                spend_total_2025 += df.iloc[idx].total_line_item_spend
    
    
    
            ### LOCATE ALL ITEMS FROM SOLD TO SELECTED CUSTOMER AND ADD TO LISTS ###
            if df.iloc[idx].item_sku[:5] == 'CC-QJ' or df.iloc[idx].item_sku[:5] == 'CC-PR' or df.iloc[idx].item_sku[:5] == 'CC-MJ' or df.iloc[idx].item_sku[:6] == 'CC-CC2':
                jet_list.append('|    {}    |     ( {}x )    {}  --  {}'.format(
                    df.iloc[idx].sales_order, 
                    int(df.iloc[idx].quantity),
                    df.iloc[idx].item_sku,
                    df.iloc[idx].line_item))
                if df.iloc[idx].item_sku[:5] == 'CC-QJ':
                    jet_totals_cust['Quad Jet'] += df.iloc[idx].quantity
                elif df.iloc[idx].item_sku[:5] == 'CC-PR':
                    jet_totals_cust['Pro Jet'] += df.iloc[idx].quantity
                elif df.iloc[idx].item_sku[:5] == 'CC-MJ':
                    jet_totals_cust['Micro Jet MKII'] += df.iloc[idx].quantity
                elif df.iloc[idx].item_sku[:6] == 'CC-CC2':
                    jet_totals_cust['Cryo Clamp'] += df.iloc[idx].quantity
            elif df.iloc[idx].item_sku[:5] == 'CC-TB' or df.iloc[idx].item_sku[:5] == 'CC-SS' or df.iloc[idx].item_sku[:5] == 'CC-SM':
                controller_list.append('|    {}    |     ( {}x )    {}  --  {}'.format(
                    df.iloc[idx].sales_order, 
                    int(df.iloc[idx].quantity),
                    df.iloc[idx].item_sku,
                    df.iloc[idx].line_item))
                if df.iloc[idx].item_sku[:5] == 'CC-TB':
                    controller_totals_cust['The Button'] += df.iloc[idx].quantity
                elif df.iloc[idx].item_sku[:5] == 'CC-SS':
                    controller_totals_cust['Shostarter'] += df.iloc[idx].quantity
                elif df.iloc[idx].item_sku[:5] == 'CC-SM':
                    controller_totals_cust['Shomaster'] += df.iloc[idx].quantity
            elif df.iloc[idx].item_sku[:5] == 'Magic' or df.iloc[idx].item_sku[:4] == 'MFX-':
                magic_list.append('|    {}    |     ( {}x )    {}  --  {}'.format(
                    df.iloc[idx].sales_order, 
                    int(df.iloc[idx].quantity),
                    df.iloc[idx].item_sku,
                    df.iloc[idx].line_item))
            elif df.iloc[idx].item_sku[:5] == 'CC-CH':
                hose_list.append('|    {}    |     ( {}x )    {}  --  {}'.format(
                    df.iloc[idx].sales_order, 
                    int(df.iloc[idx].quantity),
                    df.iloc[idx].item_sku,
                    df.iloc[idx].line_item))
            elif df.iloc[idx].item_sku[:5] == 'CC-F-' or df.iloc[idx].item_sku[:5] == 'CC-AC' or df.iloc[idx].item_sku[:5] == 'CC-CT' or df.iloc[idx].item_sku[:5] == 'CC-WA':
                fittings_accessories_list.append('|    {}    |     ( {}x )    {}  --  {}'.format(
                    df.iloc[idx].sales_order, 
                    int(df.iloc[idx].quantity),
                    df.iloc[idx].item_sku,
                    df.iloc[idx].line_item))
                if df.iloc[idx].item_sku[:9] == 'CC-AC-LA2':
                    cust_LED_mk2_cnt += df.iloc[idx].quantity                    
            elif df.iloc[idx].item_sku[:6] == 'CC-HCC' or df.iloc[idx].item_sku[:6] == 'Handhe':
                handheld_list.append('|    {}    |     ( {}x )    {}  --  {}'.format(
                    df.iloc[idx].sales_order, 
                    int(df.iloc[idx].quantity),
                    df.iloc[idx].item_sku,
                    df.iloc[idx].line_item))
                cust_handheld_mk2_cnt += df.iloc[idx].quantity
            elif df.iloc[idx].item_sku[:5] == 'Shipp' or df.iloc[idx].item_sku[:5] == 'Overn' or df.iloc[idx].item_sku[:5] == 'CC-NP':
                pass
            else:
                misc_list.append('|    {}    |     ( {}x )     {}  --  {}'.format(
                    df.iloc[idx].sales_order, 
                    int(df.iloc[idx].quantity),
                    df.iloc[idx].item_sku,
                    df.iloc[idx].line_item))
                if df.iloc[idx].item_sku == 'CC-RC-2430':
                    cust_RC_cnt += df.iloc[idx].quantity

            if df.iloc[idx].sales_order in sales_order_list:
                pass
            else:
                sales_order_list.append(df.iloc[idx].sales_order)
        idx += 1


    spending_dict, spending_total, cust_jet, cust_hh, cust_cntl, cust_acc = hist_cust_data(text_input)

    df_qb['date'] = pd.to_datetime(df_qb['date'], errors='coerce')
    df_qb['date'] = df_qb['date'].dt.strftime('%Y-%m-%d')

    
    # ADD IN HISTORICAL PRODUCTS
    for hh, tot in cust_hh.items():
        for sale in tot[1]:
            match = df_qb.loc[(df_qb['customer'] == text_input) & (df_qb['date'] == sale[1])]
            try:
                order_num = match['order_num'].iloc[0]
                handheld_list.append('| {} | {} | ( {}x ) {}'.format(order_num, sale[1], int(sale[0]), hh))
            except:
                handheld_list.append('| {} | ( {}x ) {}'.format(sale[1], int(sale[0]), hh))
    
    for jet, tot in cust_jet.items():
        jet_totals_cust[jet] += tot[0]
        for sale in tot[1]:
            match = df_qb.loc[(df_qb['customer'] == text_input) & (df_qb['date'] == sale[1])]
            try:
                order_num = match['order_num'].iloc[0]
                jet_list.append('| {} | {} | ( {}x ) {}'.format(order_num, sale[1], int(sale[0]), jet))
            except:
                jet_list.append('| {} | ( {}x ) {}'.format(sale[1], int(sale[0]), jet))

    for cntl, tot in cust_cntl.items():
        controller_totals_cust[cntl] += tot[0]
        for sale in tot[1]:
            match = df_qb.loc[(df_qb['customer'] == text_input) & (df_qb['date'] == sale[1])]
            try:
                order_num = match['order_num'].iloc[0]
                controller_list.append('| {} | {} | ( {}x ) {}'.format(order_num, sale[1], int(sale[0]), cntl))
            except:
                controller_list.append('| {} | ( {}x ) {}'.format(sale[1], int(sale[0]), cntl))

    for acc, tot in cust_acc.items():
        for sale in tot[1]:
            match = df_qb.loc[(df_qb['customer'] == text_input) & (df_qb['date'] == sale[1])]
            try:
                order_num = match['order_num'].iloc[0]
                fittings_accessories_list.append('| {} | {} | ( {}x ) {}'.format(order_num, sale[1], int(sale[0]), acc))
            except:
                fittings_accessories_list.append('| {} | ( {}x ) {}'.format(sale[1], int(sale[0]), acc))

    cust_handheld_mk2_cnt += cust_hh['Handheld MKII'][0]
    cust_handheld_mk1_cnt = cust_hh['Handheld MKI'][0]

    cust_LED_mk2_cnt += cust_acc['LED Attachment II'][0]
    cust_LED_mk1_cnt = cust_acc['LED Attachment I'][0]
    
        
    # CALCULATE SPENDING TREANDS
    if 2022 in spending_dict.keys():
        perc_change = percent_of_change(spending_dict[2022], spend_total_2023)
    else:
        perc_change = '100%'
    perc_change1 = percent_of_change(spend_total_2023, spend_total_2024) 
    perc_change2 = percent_of_change(spend_total_2024, spend_total_2025)

    
    with colb:
        st.header('')
        st.subheader('')
    
        ### DISPLAY PRODUCT PURCHASE SUMMARIES FOR SELECTED CUSTOMER ###
        if len(text_input) > 1:
    
            col3, col4, col5 = st.columns(3)
            
            ### DISPLAY CUSTOMER SPENDING TRENDS AND TOTALS
            with col3:
                st.metric('2023 Spending', '${:,.2f}'.format(spend_total_2023), perc_change)
        
            with col4:
                st.metric('2024 Spending', '${:,.2f}'.format(spend_total_2024), perc_change1)
                st.metric('**Total Spending**', '${:,.2f}'.format(spend_total_2023 + spend_total_2024 + spend_total_2025 + spending_total), '')
                
            with col5:
                st.metric('2025 Spending', '${:,.2f}'.format(spend_total_2025), perc_change2)
    
            style_metric_cards()       
            
            st.subheader('Product Totals:')
            col6, col7, col8 = st.columns(3)
            with col6.container(border=True):
                for jet, totl in jet_totals_cust.items():
                    if totl > 0:
                        st.markdown(' - **{}: {}**'.format(jet, int(totl)))
                        
            with col7.container(border=True):
                for controller, totl in controller_totals_cust.items():
                    if totl > 0:
                        st.markdown(' - **{}: {}**'.format(controller, int(totl)))
                    
            with col8.container(border=True):
                if cust_LED_mk2_cnt > 0:
                    st.markdown(' - **LED Attachment II: {}**'.format(int(cust_LED_mk2_cnt)))
                if cust_LED_mk1_cnt > 0:
                    st.markdown(' - **LED Attachment I: {}**'.format(int(cust_LED_mk1_cnt)))
                if cust_RC_cnt > 0:
                    st.markdown(' - **Road Cases: {}**'.format(int(cust_RC_cnt)))
                if cust_handheld_mk2_cnt > 0:
                    st.markdown(' - **Handheld MKII: {}**'.format(int(cust_handheld_mk2_cnt)))
                if cust_handheld_mk1_cnt > 0:
                    st.markdown(' - **Handheld MKI: {}**'.format(int(cust_handheld_mk1_cnt)))
    
### DISPLAY CATEGORIES OF PRODUCTS PURCHASED BY SELECTED CUSTOMER ###
        if len(jet_list) >= 1:
            with st.container(border=True):
                st.subheader('Stationary Jets:')
                for item in jet_list:
                    st.markdown(item)
        if len(controller_list) >= 1:
            with st.container(border=True):
                st.subheader('Controllers:')
                for item in controller_list:
                    st.markdown(item)
        if len(handheld_list) >= 1:
            with st.container(border=True):
                st.subheader('Handhelds:')
                for item in handheld_list:
                    st.markdown(item)
        if len(hose_list) >= 1:
            with st.container(border=True):
                st.subheader('Hoses:')
                for item in hose_list:
                    st.markdown(item)
        if len(fittings_accessories_list) >= 1:
            with st.container(border=True):
                st.subheader('Fittings & Accessories:')
                for item in fittings_accessories_list:
                    st.markdown(item)
        if len(misc_list) >= 1:
            with st.container(border=True):
                st.subheader('Misc:')
                for item in misc_list:
                    st.markdown(item)
        if len(magic_list):
            with st.container(border=True):
                st.subheader('Magic FX:')
                for item in magic_list:
                    st.markdown(item)
"""