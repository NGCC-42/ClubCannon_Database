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


df, df_quotes, df_cogs, df_shipstat_23, df_shipstat_24, df_qb, df_hsd, df_hist, unique_customer_list, master_customer_list, wholesale_list = load_all_data()



@st.cache_data
def get_customer_spend_by_year(df: pd.DataFrame) -> dict[int, dict[str, float]]:
    """
    Returns a dict: {year: {customer: total_spend}} for all years present in df.
    Year is inferred from ordered_year (if numeric) or order_date.
    """
    df = df.copy()

    # Ensure datetime
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

    # Build a unified numeric year column
    ordered_year = pd.to_numeric(df.get("ordered_year", pd.Series(index=df.index)),
                                 errors="coerce")
    year_from_date = df["order_date"].dt.year

    # Prefer ordered_year when available, else fall back to date year
    df["year"] = ordered_year.fillna(year_from_date)

    # Drop rows with no valid year
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)

    spend_by_year: dict[int, dict[str, float]] = {}
    for year, sub in df.groupby("year"):
        spend_by_year[year] = (
            sub.groupby("customer")["total_line_item_spend"]
               .sum()
               .to_dict()
        )

    return spend_by_year