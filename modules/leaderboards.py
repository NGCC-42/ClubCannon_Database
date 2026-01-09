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
#from fpdf import FPDF
#import base64
from io import BytesIO

from data.load import load_all_data
from ui.components import style_metric_cards
from logic.analytics import percent_of_change
from logic.leaderboard_logic import get_customer_spend_by_year
from logic.customer_logic import compute_customer_details

# --------------------
# MAKE DATA ACCESSIBLE
# --------------------

df, df_quotes, df_cogs, df_shipstat_23, df_shipstat_24, df_qb, df_hsd, df_hist, unique_customer_list, master_customer_list, wholesale_list = load_all_data()


# ----------------------------------------------------
# SORTING FUNCTION FOR LEADERBOARDS - CURRENTLY UNUSED
# ----------------------------------------------------

def sort_top_20(dict, number):

    leaderboard_list = []
    
    for key, value in dict.items():
        if value >= 2000:
            leaderboard_list.append((key, value))

    sorted_leaderboard = sorted(leaderboard_list, key=lambda x: x[1], reverse=True)

    return sorted_leaderboard[:number]


# ---------------------------------------
# RENDER FUNCTION TO DISPLAY LEADERBOARDS
# ---------------------------------------

def render_leaderboards():
     # --- Header / controls ---
    colx, coly, colz = st.columns([0.15, 0.7, 0.15])
    coly.header("Customer Leaderboards")
    coly.subheader("")

    with coly:
        ranking_number = st.selectbox(
            "Choose Leaderboard Length",
            [5, 10, 15, 20, 25, 50],
        )

    # --- Compute spend by year (cached) ---
    spend_by_year = get_customer_spend_by_year(df)  # {year: {customer: spend}}

    if not spend_by_year:
        coly.info("No customer spend data available.")
        return

    all_years = sorted(spend_by_year.keys())          # e.g. [2019, 2020, 2021, 2022, 2023, 2024, 2025]
    # Pick the latest 3 years (or fewer if not available)
    max_years_to_show = 3
    years_to_show = all_years[-max_years_to_show:]    # newest at the end
    # We want newest on the LEFT visually, so reverse when building columns
    years_display = list(reversed(years_to_show))     # e.g. [2025, 2024, 2023]

    # --- Build columns dynamically based on how many years we have ---
    with coly:
        cols = st.columns(len(years_display))
        # First row: year headers
        for col, year in zip(cols, years_display):
            col.subheader(str(year))

        # --- For each year, compute top N and show metrics ---
        for col, year in zip(cols, years_display):
            cust_spend = spend_by_year[year]

            # Sort customers by spend, descending, and take top N
            top_items = sorted(
                cust_spend.items(),
                key=lambda x: x[1],
                reverse=True
            )[:ranking_number]

            # Previous year for % change (if it exists)
            prev_year = year - 1
            prev_spend_dict = spend_by_year.get(prev_year, {})

            rank = 1
            for customer, spend in top_items:
                prev_spend = prev_spend_dict.get(customer, 0)

                # For the earliest year in our display, you *can* show 0% or skip,
                # but percent_of_change(prev_spend, spend) handles prev_spend == 0.
                delta_text = percent_of_change(prev_spend, spend)

                col.metric(
                    label=f"**${spend:,.2f}**",
                    value=f"{rank}) {customer}",
                    delta=delta_text,
                )
                rank += 1

        style_metric_cards()


def build_customer_spend_leaderboard(df, df_qb, master_customer_list) -> pd.DataFrame:
    rows = []

    for cust in master_customer_list:
        data = compute_customer_details(df, df_qb, cust)
        if not data:
            continue

        total = float(data.get("total_spending_all", 0) or 0)

        # year_metrics: [(year, spend, delta), ...]
        year_metrics = data.get("year_metrics", []) or []
        year_spend = {int(y): float(s or 0) for (y, s, _delta) in year_metrics}

        # "Active years" = years with > 0 spend (recommended)
        active_years = sorted([y for y, s in year_spend.items() if s > 0])

        if active_years:
            first_year = min(active_years)
            last_year = max(active_years)
            years_active = len(active_years)
            avg_annual = total / years_active
        else:
            first_year = None
            last_year = None
            years_active = 0
            avg_annual = 0

        rows.append(
            {
                "Customer": cust,
                "Lifetime Spend": total,
                "Avg Annual Spend (active years)": avg_annual,
                "Active Years": years_active,
                "First Active Year": first_year,
                "Last Active Year": last_year,
            }
        )

    out = pd.DataFrame(rows)
    if out.empty:
        return out

    return out.sort_values("Lifetime Spend", ascending=False).reset_index(drop=True)


def render_customer_spend_leaderboard(df, df_qb, master_customer_list):
    st.subheader("Customers by Lifetime Spending")

    leaderboard_df = build_customer_spend_leaderboard(df, df_qb, master_customer_list)

    if leaderboard_df.empty:
        st.info("No customer spend data found.")
        return

    st.dataframe(leaderboard_df, use_container_width=True)

    # Excel export
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        leaderboard_df.to_excel(writer, index=False, sheet_name="Leaderboard")
    buffer.seek(0)

    st.download_button(
        "Download Excel",
        data=buffer,
        file_name="customer_lifetime_spend_leaderboard.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )



