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


# -------------------------------------------
# RENDER FUNCTION TO DISPLAY CUSTOMER DETAILS
# -------------------------------------------

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




