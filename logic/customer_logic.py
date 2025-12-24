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
import pandas as pd
import streamlit as st
from logic.analytics import percent_of_change 



# -----------------------------------------------------------
# HELPER FUNCTION TO PROCESS DATA FOR CUSTOMER DETAILS MODULE
# -----------------------------------------------------------

@st.cache_data
def compute_customer_details(df, df_qb, customer_name):
    if not customer_name:
        return None
    
    df = df.copy()
    df_qb = df_qb.copy()
    
    # ---- Filter this customer ----
    mask = df["customer"].str.upper() == customer_name.upper()
    df_cust = df.loc[mask].copy()
    if df_cust.empty:
        return None
    
    # ---- Build year column from ordered_year / order_date ----
    df_cust["order_date"] = pd.to_datetime(df_cust["order_date"], errors="coerce")
    ordered_year = pd.to_numeric(df_cust.get("ordered_year"), errors="coerce")
    year_from_date = df_cust["order_date"].dt.year
    df_cust["year"] = ordered_year.fillna(year_from_date).astype("Int64")
    
    # ---- Spend by year from DF (2023+ etc) ----
    spend_by_year_df = (
        df_cust.groupby("year")["total_line_item_spend"]
               .sum()
               .to_dict()
    )
    
    # ---- Historical spend (pre-DF) ----
    # Your existing function
    spending_dict, spending_total, cust_jet, cust_hh, cust_cntl, cust_acc = hist_cust_data(
        customer_name
    )
    # spending_dict: {year: amount} for older years, e.g. 2015–2022
    
    # ---- Combine historical + DF years into one dict ----
    combined_spend = dict(spending_dict)  # start with historical
    for year, amt in spend_by_year_df.items():
        combined_spend[year] = combined_spend.get(year, 0) + float(amt)
    
    if not combined_spend:
        year_metrics = []
        total_spending_all = 0.0
    else:
        # Sort all years and keep the last N (e.g. last 3)
        all_years = sorted(combined_spend.keys())
        max_years_to_show = 3
        last_years = all_years[-max_years_to_show:]
    
        year_metrics = []
        for year in last_years:
            spend = float(combined_spend[year])
            prev_year = year - 1
            prev_spend = float(combined_spend.get(prev_year, 0))
            # If there's no previous year at all, you can decide what to show
            if prev_year in combined_spend:
                delta = percent_of_change(prev_spend, spend)
            else:
                # you can also use "N/A" here if you prefer
                delta = percent_of_change(0, spend)
            year_metrics.append((year, spend, delta))
    
        total_spending_all = float(sum(combined_spend.values()))


    # ---------------------------
    # Category lists & totals
    # ---------------------------
    sales_order_list = []
    jet_list = []
    controller_list = []
    misc_list = []
    magic_list = []
    hose_list = []
    fittings_accessories_list = []
    handheld_list = []

    jet_totals_cust = {
        "Quad Jet": 0,
        "Pro Jet": 0,
        "Micro Jet MKII": 0,
        "Micro Jet MKI": 0,
        "Cryo Clamp": 0,
        "Cryo Clamp MKI": 0,
        "DMX Jet": 0,
        "Power Jet": 0,
    }

    controller_totals_cust = {
        "The Button": 0,
        "Shostarter": 0,
        "Shomaster": 0,
        "DMX Controller": 0,
        "LCD Controller": 0,
        "The Button MKI": 0,
        "Power Controller": 0,
    }

    cust_handheld_mk2_cnt = 0
    cust_handheld_mk1_cnt = 0
    cust_LED_mk2_cnt = 0
    cust_LED_mk1_cnt = 0
    cust_RC_cnt = 0

    # Helper to build the "| SO | ( qtyx ) sku -- desc" string
    def fmt_line(so, qty, sku, line):
        return f"|    {so}    |     ( {int(qty)}x )    {sku}  --  {line}"

    # Iterate through customer rows
    for row in df_cust.itertuples():
        sku = str(row.item_sku) if pd.notna(row.item_sku) else ""
        so = row.sales_order
        qty = row.quantity
        line = row.line_item

        # Jets
        if sku.startswith(("CC-QJ", "CC-PR", "CC-MJ", "CC-CC2")):
            jet_list.append(fmt_line(so, qty, sku, line))
            if sku.startswith("CC-QJ"):
                jet_totals_cust["Quad Jet"] += qty
            elif sku.startswith("CC-PR"):
                jet_totals_cust["Pro Jet"] += qty
            elif sku.startswith("CC-MJ"):
                jet_totals_cust["Micro Jet MKII"] += qty
            elif sku.startswith("CC-CC2"):
                jet_totals_cust["Cryo Clamp"] += qty

        # Controllers
        elif sku.startswith(("CC-TB", "CC-SS", "CC-SM")):
            controller_list.append(fmt_line(so, qty, sku, line))
            if sku.startswith("CC-TB"):
                controller_totals_cust["The Button"] += qty
            elif sku.startswith("CC-SS"):
                controller_totals_cust["Shostarter"] += qty
            elif sku.startswith("CC-SM"):
                controller_totals_cust["Shomaster"] += qty

        # MagicFX
        elif sku.startswith("Magic") or sku.startswith("MFX-"):
            magic_list.append(fmt_line(so, qty, sku, line))

        # Hoses
        elif sku.startswith("CC-CH"):
            hose_list.append(fmt_line(so, qty, sku, line))

        # Fittings & Accessories
        elif sku.startswith(("CC-F-", "CC-AC", "CC-CT", "CC-WA")):
            fittings_accessories_list.append(fmt_line(so, qty, sku, line))
            if sku.startswith("CC-AC-LA2"):
                cust_LED_mk2_cnt += qty

        # Handhelds
        elif sku.startswith("CC-HCC") or sku.startswith("Handhe"):
            handheld_list.append(fmt_line(so, qty, sku, line))
            cust_handheld_mk2_cnt += qty

        # Shipping / misc NPT we skip
        elif sku.startswith(("Shipp", "Overn", "CC-NP")):
            pass

        # Misc
        else:
            misc_list.append(fmt_line(so, qty, sku, line))
            if sku == "CC-RC-2430":
                cust_RC_cnt += qty

        # Track distinct sales orders (if you need it later)
        if so not in sales_order_list:
            sales_order_list.append(so)

    # ---------------------------
    # Historical data integration
    # ---------------------------
    spending_dict, spending_total, cust_jet, cust_hh, cust_cntl, cust_acc = hist_cust_data(
        customer_name
    )

    # Normalize df_qb date
    df_qb["date"] = pd.to_datetime(df_qb["date"], errors="coerce")
    df_qb["date"] = df_qb["date"].dt.strftime("%Y-%m-%d")

    # Add historical handhelds
    for hh, tot in cust_hh.items():
        for sale in tot[1]:
            date_str = sale[1]
            qty_hh = sale[0]
            match = df_qb.loc[
                (df_qb["customer"] == customer_name) & (df_qb["date"] == date_str)
            ]
            if not match.empty:
                order_num = match["order_num"].iloc[0]
                handheld_list.append(f"| {order_num} | {date_str} | ( {int(qty_hh)}x ) {hh}")
            else:
                handheld_list.append(f"| {date_str} | ( {int(qty_hh)}x ) {hh}")

    # Add historical jets
    for jet, tot in cust_jet.items():
        jet_totals_cust[jet] += tot[0]
        for sale in tot[1]:
            date_str = sale[1]
            qty_jet = sale[0]
            match = df_qb.loc[
                (df_qb["customer"] == customer_name) & (df_qb["date"] == date_str)
            ]
            if not match.empty:
                order_num = match["order_num"].iloc[0]
                jet_list.append(f"| {order_num} | {date_str} | ( {int(qty_jet)}x ) {jet}")
            else:
                jet_list.append(f"| {date_str} | ( {int(qty_jet)}x ) {jet}")

    # Add historical controllers
    for cntl, tot in cust_cntl.items():
        controller_totals_cust[cntl] += tot[0]
        for sale in tot[1]:
            date_str = sale[1]
            qty_cntl = sale[0]
            match = df_qb.loc[
                (df_qb["customer"] == customer_name) & (df_qb["date"] == date_str)
            ]
            if not match.empty:
                order_num = match["order_num"].iloc[0]
                controller_list.append(
                    f"| {order_num} | {date_str} | ( {int(qty_cntl)}x ) {cntl}"
                )
            else:
                controller_list.append(
                    f"| {date_str} | ( {int(qty_cntl)}x ) {cntl}"
                )

    # Add historical accessories
    for acc, tot in cust_acc.items():
        for sale in tot[1]:
            date_str = sale[1]
            qty_acc = sale[0]
            match = df_qb.loc[
                (df_qb["customer"] == customer_name) & (df_qb["date"] == date_str)
            ]
            if not match.empty:
                order_num = match["order_num"].iloc[0]
                fittings_accessories_list.append(
                    f"| {order_num} | {date_str} | ( {int(qty_acc)}x ) {acc}"
                )
            else:
                fittings_accessories_list.append(
                    f"| {date_str} | ( {int(qty_acc)}x ) {acc}"
                )

    # Update counts with historical values
    cust_handheld_mk2_cnt += cust_hh["Handheld MKII"][0]
    cust_handheld_mk1_cnt = cust_hh["Handheld MKI"][0]

    cust_LED_mk2_cnt += cust_acc["LED Attachment II"][0]
    cust_LED_mk1_cnt = cust_acc["LED Attachment I"][0]

       # ---------------------------
    # Spending trends (all years, future-proof)
    # ---------------------------

    # spend_by_year_df came from df_cust (recent years in df)
    # spending_dict came from hist_cust_data (older years)
    combined_spend = dict(spending_dict)  # historical first
    for year, amt in spend_by_year_df.items():
        combined_spend[year] = combined_spend.get(year, 0) + float(amt)

    if not combined_spend:
        year_metrics = []
        total_spending_all = 0.0
    else:
        all_years = sorted(combined_spend.keys())
        max_years_to_show = 3          # last 3 years; change if you want more
        last_years = all_years[-max_years_to_show:]

        year_metrics = []
        for year in last_years:
            spend = float(combined_spend[year])
            prev_year = year - 1
            prev_spend = float(combined_spend.get(prev_year, 0))
            # If there is no previous year, treat as 0 -> 100% growth
            delta = percent_of_change(prev_spend, spend)
            year_metrics.append((year, spend, delta))

        total_spending_all = float(sum(combined_spend.values()))

    return {
        "year_metrics": year_metrics,
        "total_spending_all": total_spending_all,

        # everything else you already return:
        "jet_totals_cust": jet_totals_cust,
        "controller_totals_cust": controller_totals_cust,
        "cust_handheld_mk2_cnt": cust_handheld_mk2_cnt,
        "cust_handheld_mk1_cnt": cust_handheld_mk1_cnt,
        "cust_LED_mk2_cnt": cust_LED_mk2_cnt,
        "cust_LED_mk1_cnt": cust_LED_mk1_cnt,
        "cust_RC_cnt": cust_RC_cnt,
        "jet_list": jet_list,
        "controller_list": controller_list,
        "handheld_list": handheld_list,
        "hose_list": hose_list,
        "fittings_accessories_list": fittings_accessories_list,
        "misc_list": misc_list,
        "magic_list": magic_list,
    }