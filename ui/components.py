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



# -------------------
# METIC CARD STYLING 
# -------------------
 
def style_metric_cards(
    background_color: str = "#000000",
    border_size_px: int = 1.5,
    border_color: str = "#EB1C25",
    border_radius_px: int = 5,
    border_left_color: str = "#EB1C25",
    box_shadow: bool = True,
) -> None:
    """
    Applies a custom style to st.metrics in the page

    Args:
        background_color (str, optional): Background color. Defaults to "#FFF".
        border_size_px (int, optional): Border size in pixels. Defaults to 1.
        border_color (str, optional): Border color. Defaults to "#CCC".
        border_radius_px (int, optional): Border radius in pixels. Defaults to 5.
        border_left_color (str, optional): Borfer left color. Defaults to "#9AD8E1".
        box_shadow (bool, optional): Whether a box shadow is applied. Defaults to True.
    """

    box_shadow_str = (
        "box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15) !important;"
        if box_shadow
        else "box-shadow: none !important;"
    )
    st.markdown(
        f"""
        <style>
            div[data-testid="stMetric"],
            div[data-testid="metric-container"] {{
                background-color: {background_color};
                border: {border_size_px}px solid {border_color};
                padding: 5% 1% 5% 5%;
                border-radius: {border_radius_px}px;
                border-left: 0.5rem solid {border_left_color} !important;
                {box_shadow_str}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# --------------------------------------------------
# CSS OVERRIDE FOR SELECTBOX TO FOLLOW PRIMARY COLOR
# --------------------------------------------------

def apply_selectbox_theme_fix():
    primary = st.get_option("theme.primaryColor") or "#FF4B4B"
    css = f"""
    <style>
    /* Selectbox + Multiselect outer border */
    div[data-baseweb="select"] > div {{
        border-color: {primary} !important;
    }}

    /* Focus ring */
    div[data-baseweb="select"] > div:focus-within {{
        border-color: {primary} !important;
        box-shadow: 0 0 0 0.15rem {primary}33 !important; /* 33 = ~20% alpha */
    }}

    /* Dropdown option hover + selected */
    div[role="listbox"] div[role="option"]:hover {{
        background-color: {primary}22 !important; /* ~13% */
    }}
    div[role="listbox"] div[role="option"][aria-selected="true"] {{
        background-color: {primary}33 !important; /* ~20% */
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)