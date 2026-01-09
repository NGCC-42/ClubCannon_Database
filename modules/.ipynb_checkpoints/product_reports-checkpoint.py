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
#from data.load import load_all_data



from logic.analytics import (
    num_to_month, 
    month_to_num,    
    to_date_revenue,
    percent_of_change,
    get_monthly_sales_v2,
    calc_monthly_totals_v2,
    magic_sales_data
)

from ui.charts import (
    display_pie_chart_comp, 
    plot_bar_chart_product_seg, 
    format_for_chart_hh,
    plot_bar_chart_hh,
    format_for_chart_product_seg
)

from ui.components import (
    style_metric_cards
)

from logic.products import (
    extract_handheld_data,
    extract_hose_data,
    extract_acc_data,
    extract_control_data,
    extract_jet_data,
    collect_product_data,
    organize_hose_data,
    calc_prod_metrics,
    calc_time_context,
    to_date_product,
    convert_prod_select,
    convert_prod_select_profit,
    to_date_product_profit,
    months_x, 
    magic_sales, 
    prep_data_context
)



# INITIALIZE PRODUCT COUNT VARIABLES
pj_td24 = 0
mj_td24 = 0
qj_td24 = 0
cc_td24 = 0
tb_td24 = 0
ss_td24 = 0
sm_td24 = 0
td_8nc24 = 0
td_8tc24 = 0
td_15nc24 = 0
td_15tc24 = 0


# ------------------------------------------
# DISPLAY FUNTION FOR PRODUCT SALES BY MONTH
# ------------------------------------------

def display_month_data_prod(
    product,
    sales_dict1,
    sales_dict2=None,
    value_type: str = "Unit",
    months=None,
):

   # Display monthly product data as metric cards in a 3-column grid.

   # Parameters
   # ----------
   # product : str
   #     Product key to look up in the sales dictionaries.
   # sales_dict1 : dict
   #     Current period sales dict: {month: {product: [value, ...]}, ...}
   # sales_dict2 : dict or None
   #     Prior period sales dict with the same structure (optional).
   #     If provided, diff vs prior is shown in the description.
   # value_type : str
   #     Either "Unit" or "Currency" (case-insensitive).
   # months : list[str] or None
   #     List of month labels to display. If None, uses global months_x.


    if months is None:
        months = months_x

    # Normalize type
    value_type = value_type.lower()  # "unit" or "currency"

    # Create enough rows of 3 columns each for all months
    num_rows = (len(months) + 2) // 3  # ceiling division
    rows = [st.columns(3) for _ in range(num_rows)]

    for idx, month in enumerate(months):
        row_idx, col_idx = divmod(idx, 3)
        col = rows[row_idx][col_idx]

        # Safely get the current value
        current_val = (
            sales_dict1.get(month, {})
                       .get(product, [0])[0]
        )

        # Compute diff vs prior year if provided
        desc = ""
        if sales_dict2 is not None:
            prior_val = (
                sales_dict2.get(month, {})
                           .get(product, [0])[0]
            )
            diff = current_val - prior_val
            sign = "+" if diff > 0 else "-" if diff < 0 else ""
            diff_abs = abs(int(diff))

            if value_type == "currency":
                desc = f"{sign} ${diff_abs:,} vs. prior year"
            else:
                desc = f"{sign} {diff_abs:,} vs. prior year"

        # Format main content based on type
        if value_type == "currency":
            content = f"${int(current_val):,}"
        else:
            content = f"{int(current_val):,}"

        with col:
            ui.metric_card(
                title=month,
                content=content,
                description=desc,
            )


#product_ctx = prep_data_context()


# ------------------------------------------------
# DISPLAY FUNCTIONS FOR HOSES - REVENUE AND PROFIT
# ------------------------------------------------

def display_hose_data(hose_details1, hose_details2, hose_details3, hose_details4):
    
    """
    Display hose data for three years (currently 2026, 2025, 2024).

    Each `hose_detailsX` is expected to be a list of 8 items:
      - hose_detailsX[0..6]: dicts like {'5FT STD': [qty, rev], ...}
      - hose_detailsX[7]: a list/tuple [qty, rev] for '100FT STD'
    """

    #prodTot26 = product_ctx['prodTot26']
    #prodTot25 = product_ctx['prodTot25']
    #prodTot24 = product_ctx['prodTot24']
    #prodTot23 = product_ctx['prodTot23']
    
    # Pair year labels with their corresponding data
    year_data = [
        ("2026", hose_details1),
        ("2025", hose_details2),
        ("2024", hose_details3),
        ("2023", hose_details4)
    ]

    cols = st.columns(4)

    for col, (year_label, hose_details) in zip(cols, year_data):
        with col:
            st.subheader(year_label)

            # First 7 groups are dicts of hose-type -> [units, revenue]
            for group_idx, group in enumerate(hose_details[:7]):
                group_units = 0
                group_rev = 0

                with st.container(border=True):
                    for hose_name, vals in group.items():
                        units = vals[0]
                        rev = vals[1]

                        group_units += units
                        group_rev += rev

                        ui.metric_card(
                            title=hose_name,
                            content=f"{int(units)} units",
                            description=f"${rev:,.2f} in rev",
                        )

                    # Group totals
                    st.markdown(
                        f"**Totals: {int(group_units)} - (${int(group_rev):,})**"
                    )

            # The 8th item (index 7) is the 100FT STD summary: [units, rev]
            hundred_units, hundred_rev = hose_details[7]
            ui.metric_card(
                title="100FT STD",
                content=f"{int(hundred_units)} units",
                description=f"${hundred_rev:,.2f} in rev",
                key=f"{year_label}-100FT",
            )

    return None


def display_hose_data_profit(hose_details1, hose_details2, hose_details3, hose_details4, product_ctx, bom_cost_hose):
    
    """
    Display hose profit data for 2026, 2025, 2024 and 2023

    Each hose_detailsX is expected to be a list of 8 items:
      - hose_detailsX[0..6]: dicts like {'5FT STD': [qty, rev], ...}
      - hose_detailsX[7]: [qty, rev] for '100FT STD' (we ignore qty/rev here
        and compute profit based on prodTot* and bom_cost_hose).
    Relies on globals: prodTot26, prodTot25, prodTot24, prodTot23, bom_cost_hose, calc_prod_metrics.
    """

    prodTot26 = product_ctx['prodTot26']
    prodTot25 = product_ctx['prodTot25']
    prodTot24 = product_ctx['prodTot24']
    prodTot23 = product_ctx['prodTot23']

    
    # Pair each year with: (hose_details, current_prod_tot, prior_prod_tot or None)
    year_data = [
        ("2026", hose_details1, prodTot26["hose"], prodTot25["hose"]),
        ("2025", hose_details2, prodTot25["hose"], prodTot24["hose"]),
        ("2024", hose_details3, prodTot24["hose"], prodTot23["hose"]),
        ("2023", hose_details4, prodTot23["hose"], None)# no prior year passed
    ]

    cols = st.columns(4)

    for col, (year_label, hose_details, prod_tot_curr, prod_tot_prev) in zip(cols, year_data):
        with col:
            st.subheader(year_label)

            # First 7 groups: dicts of hose_name -> [units, revenue]
            for group in hose_details[:7]:
                group_profit = 0.0

                with st.container(border=True):
                    for hose_name, vals in group.items():
                        # Call calc_prod_metrics with or without prior-year totals
                        if prod_tot_prev is not None:
                            prod_profit, profit_per_unit, *rest = calc_prod_metrics(
                                prod_tot_curr,
                                hose_name,
                                bom_cost_hose,
                                prod_tot_prev,
                            )
                        else:
                            prod_profit, profit_per_unit, *rest = calc_prod_metrics(
                                prod_tot_curr,
                                hose_name,
                                bom_cost_hose,
                            )

                        group_profit += prod_profit

                        ui.metric_card(
                            title=hose_name,
                            content=f"Profit: ${prod_profit:,.2f}",
                            description=f"Profit per Unit: ${profit_per_unit:,.2f}",
                        )

                    st.markdown(f"**Group Total: ${group_profit:,.2f}**")

            # 100FT STD – compute profit via calc_prod_metrics as well
            if prod_tot_prev is not None:
                prod_profit100, profit_per_unit100, *rest = calc_prod_metrics(
                    prod_tot_curr,
                    "100FT STD",
                    bom_cost_hose,
                    prod_tot_prev,
                )
            else:
                prod_profit100, profit_per_unit100, *rest = calc_prod_metrics(
                    prod_tot_curr,
                    "100FT STD",
                    bom_cost_hose,
                )

            ui.metric_card(
                title="100FT STD",
                content=f"Profit: ${prod_profit100:,.2f}",
                description=f"Profit per Unit: ${profit_per_unit100:,.2f}",
                key=f"{year_label}-100FT-profit",
            )

    return None


# -----------------------------------------------------
# DISPLAY FUNCTION FOR ACCESSORIES - REVENUE AND PROFIT
# -----------------------------------------------------

def display_acc_data(product_ctx):

    prodTot26 = product_ctx['prodTot26']
    prodTot25 = product_ctx['prodTot25']
    prodTot24 = product_ctx['prodTot24']
    prodTot23 = product_ctx['prodTot23']
    

    cola, colb, colc, cold, cole, colf, colg, colh = st.columns([.1,.1,.2,.2,.2,.2,.1,.1])

    with colc:
        for item, value in prodTot26['acc'].items():
            if item == 'CC-RC-2430':
                ui.metric_card(title='{}'.format(item), content='{} (PJ: {}, LA: {}, QJ: {})'.format(int(value[0]), int(value[2]), int(value[3]), int(value[4])), description='${:,.2f} in Revenue'.format(value[1]))
            else:
                value[0] = int(value[0])
                ui.metric_card(title='{}'.format(item), content='{}'.format(value[0]), description='${:,.2f} in Revenue'.format(value[1])) 
    
    with cold:
        for item, value in prodTot25['acc'].items():
            if item == 'CC-RC-2430':
                ui.metric_card(title='{}'.format(item), content='{} (PJ: {}, LA: {}, QJ: {})'.format(int(value[0]), int(value[2]), int(value[3]), int(value[4])), description='${:,.2f} in Revenue'.format(value[1]))
            else:
                value[0] = int(value[0])
                ui.metric_card(title='{}'.format(item), content='{}'.format(value[0]), description='${:,.2f} in Revenue'.format(value[1])) 
    with cole:
        key = 'anvienial23'
        for item_last, value_last in prodTot24['acc'].items():
            if item_last == 'CC-RC-2430':
                ui.metric_card(title='{}'.format(item_last), content='{} (PJ: {}, LA: {}, QJ: {})'.format(int(value_last[0]), int(value_last[2]), int(value_last[3]), int(value_last[4])), description='${:,.2f} in Revenue'.format(value_last[1]), key=key)
            else:
                value_last[0] = int(value_last[0])
                ui.metric_card(title='{}'.format(item_last), content='{}'.format(value_last[0]), description='${:,.2f} in Revenue'.format(value_last[1]), key=key)
            key += '64sdg5as'
    with colf:
        key2 = 'a'
        for item_last2, value_last2 in prodTot23['acc'].items():
            if item_last2 == 'CC-RC-2430':
                ui.metric_card(title='{}'.format(item_last2), content='{} (PJ: {}, LA: {})'.format(int(value_last2[0]), int(value_last2[2]), int(value_last2[3])), description='${:,.2f} in Revenue'.format(value_last2[1]), key=key2)
            else:
                value_last2[0] = int(value_last2[0])
                ui.metric_card(title='{}'.format(item_last2), content='{}'.format(value_last2[0]), description='${:,.2f} in Revenue'.format(value_last2[1]), key=key2)
            key2 += 'niane7'


def display_acc_data_profit(product_ctx, bom_cost_acc):

    prodTot26 = product_ctx['prodTot26']
    prodTot25 = product_ctx['prodTot25']
    prodTot24 = product_ctx['prodTot24']
    prodTot23 = product_ctx['prodTot23']

    
    cola, colb, colc, cold, cole, colf, colg, colh = st.columns([.1,.1,.2,.2,.2,.2,.1,.1])

    with colc:
        for item, value in prodTot26['acc'].items():
            prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last = calc_prod_metrics(prodTot26['acc'], item, bom_cost_acc, prodTot25['acc']) 
            if item == 'CC-RC-2430':
                ui.metric_card(title='{}'.format(item), content='Total Profit: ${:,.2f}'.format(prod_profit), description='Profit per Unit: ${:,.2f}'.format(profit_per_unit), key=f"acc_profit_{value}_{2026}_{item}")
            else:
                value[0] = int(value[0])
                ui.metric_card(title='{}'.format(item), content='Total Profit: ${:,.2f}'.format(prod_profit), description='Profit per Unit: ${:,.2f}'.format(profit_per_unit), key=f"acc_profit_{value}_{2026}_{item}") 

    with cold:
        for item_last, value_last in prodTot25['acc'].items():
            prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last = calc_prod_metrics(prodTot25['acc'], item_last, bom_cost_acc, prodTot24['acc']) 
            if item == 'CC-RC-2430':
                ui.metric_card(title='{}'.format(item_last), content='Total Profit: ${:,.2f}'.format(prod_profit), description='Profit per Unit: ${:,.2f}'.format(profit_per_unit), key=f"acc_profit_{value_last}_{2025}_{item_last}")
            else:
                value_last[0] = int(value_last[0])
                ui.metric_card(title='{}'.format(item_last), content='Total Profit: ${:,.2f}'.format(prod_profit), description='Profit per Unit: ${:,.2f}'.format(profit_per_unit), key=f"acc_profit_{value_last}_{2025}_{item_last}") 

    with cole:
        for item_last2, value_last2 in prodTot24['acc'].items():
            prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last = calc_prod_metrics(prodTot24['acc'], item_last2, bom_cost_acc, prodTot23['acc'])
            if item_last == 'CC-RC-2430':
                ui.metric_card(title='{}'.format(item_last2), content='Total Profit: ${:,.2f}'.format(prod_profit), description='Profit per Unit: ${:,.2f}'.format(profit_per_unit), key=f"acc_profit_{value_last2}_{2024}_{item}")
            else:
                value_last2[0] = int(value_last2[0])
                ui.metric_card(title='{}'.format(item_last2), content='Total Profit: ${:,.2f}'.format(prod_profit), description='Profit per Unit: ${:,.2f}'.format(profit_per_unit), key=f"acc_profit_{value_last2}_{2024}_{item}")

    with colf:
        for item_last3, value_last3 in prodTot23['acc'].items():
            prod_profit, profit_per_unit, avg_price = calc_prod_metrics(prodTot23['acc'], item_last3, bom_cost_acc)
            if item_last2 == 'CC-RC-2430':
                ui.metric_card(title='{}'.format(item_last3), content='Total Profit: ${:,.2f}'.format(prod_profit), description='Profit per Unit: ${:,.2f}'.format(profit_per_unit), key=f"acc_profit_{value_last3}_{2023}_{item_last3}")
            else:
                value_last2[0] = int(value_last2[0])
                ui.metric_card(title='{}'.format(item_last3), content='Total Profit: ${:,.2f}'.format(prod_profit), description='Profit per Unit: ${:,.2f}'.format(profit_per_unit), key=f"acc_profit_{value_last3}_{2023}_{item_last3}")

        





# -----------------------------------
# RENDER FUNCTION FOR DISPLAY IN MAIN
# -----------------------------------

def render_products(product_ctx, wholesale_list, bom_cost_jet, bom_cost_control, bom_cost_hh, bom_cost_hose, bom_cost_acc, bom_cost_mfx):

    
    today, one_year_ago, two_years_ago, three_years_ago, four_years_ago = calc_time_context()

    
    # ---------------------------------------------
    # MAP OUT VARIABLES FOR CONTEXT HELPER FUNCTION
    # ---------------------------------------------
    
    #rev_by_year = product_ctx["rev_by_year"]
    
    td_26 = product_ctx["td_26"]; td_25 = product_ctx["td_25"]; td_24 = product_ctx["td_24"]; td_23 = product_ctx["td_23"]; td_22 = product_ctx["td_22"]
    td_26_tot = product_ctx["td_26_tot"]; td_25_tot = product_ctx["td_25_tot"];  td_24_tot = product_ctx["td_24_tot"]; td_23_tot = product_ctx["td_23_tot"]; td_22_tot = product_ctx["td_22_tot"]
    
    sales_dict_25 = product_ctx["sales_dict_25"]; sales_dict_24 = product_ctx["sales_dict_24"]; sales_dict_23 = product_ctx["sales_dict_23"]
    
    total_25 = product_ctx["total_25"]; web_25 = product_ctx["web_25"]; ful_25 = product_ctx["ful_25"]; avg_25 = product_ctx["avg_25"]; magic25 = product_ctx["magic25"]
    total_24 = product_ctx["total_24"]; web_24 = product_ctx["web_24"]; ful_24 = product_ctx["ful_24"]; avg_24 = product_ctx["avg_24"]; magic24 = product_ctx["magic24"]
    total_23 = product_ctx["total_23"]; web_23 = product_ctx["web_23"]; ful_23 = product_ctx["ful_23"]; avg_23 = product_ctx["avg_23"]; magic23 = product_ctx["magic23"]
    
    jet26 = product_ctx["jet26"]; control26 = product_ctx["control26"]; handheld26 = product_ctx["handheld26"]; hose26 = product_ctx["hose26"]; acc26 = product_ctx["acc26"]; hose_detail26 = product_ctx["hose_detail26"]; prodTot26 = product_ctx["prodTot26"]
    jet25 = product_ctx["jet25"]; control25 = product_ctx["control25"]; handheld25 = product_ctx["handheld25"]; hose25 = product_ctx["hose25"]; acc25 = product_ctx["acc25"]; hose_detail25 = product_ctx["hose_detail25"]; prodTot25 = product_ctx["prodTot25"]; profit_25 = product_ctx["profit_25"]
    jet24 = product_ctx["jet24"]; control24 = product_ctx["control24"]; handheld24 = product_ctx["handheld24"]; hose24 = product_ctx["hose24"]; acc24 = product_ctx["acc24"]; hose_detail24 = product_ctx["hose_detail24"]; prodTot24 = product_ctx["prodTot24"]; profit_24 = product_ctx["profit_24"]
    jet23 = product_ctx["jet23"]; control23 = product_ctx["control23"]; handheld23 = product_ctx["handheld23"]; hose23 = product_ctx["hose23"]; acc23 = product_ctx["acc23"]; hose_detail23 = product_ctx["hose_detail23"]; prodTot23 = product_ctx["prodTot23"]; profit_23 = product_ctx["profit_23"]
    
    mfx_rev = product_ctx["mfx_rev"]; mfx_costs = product_ctx["mfx_costs"]; mfx_profit = product_ctx["mfx_profit"]

    # HISTORICAL    
    hhmk1_cust = product_ctx["hhmk1_cust"]; hhmk1_annual = product_ctx["hhmk1_annual"]; hhmk2_cust = product_ctx["hhmk2_cust"]; hhmk2_annual = product_ctx["hhmk2_annual"]
    tc_cust = product_ctx["tc_cust"]; tc_annual = product_ctx["tc_annual"]; tcog_cust = product_ctx["tcog_cust"]; tcog_annual = product_ctx["tcog_annual"]
    bp_cust = product_ctx["bp_cust"]; bp_annual = product_ctx["bp_annual"]

    mfd_cust = product_ctx["mfd_cust"]; mfd_annual = product_ctx["mfd_annual"]
    ctc_20_cust = product_ctx["ctc_20_cust"]; ctc_20_annual = product_ctx["ctc_20_annual"]; ctc_50_cust = product_ctx["ctc_50_cust"]; ctc_50_annual = product_ctx["ctc_50_annual"]
    ledmk1_cust = product_ctx["ledmk1_cust"]; ledmk1_annual = product_ctx["ledmk1_annual"]; ledmk2_cust = product_ctx["ledmk2_cust"]; ledmk2_annual = product_ctx["ledmk2_annual"]
    pwrpack_cust = product_ctx["pwrpack_cust"]; pwrpack_annual = product_ctx["pwrpack_annual"]
    
    jet_og_cust = product_ctx["jet_og_cust"]; jet_og_annual = product_ctx["jet_og_annual"]; pj_cust = product_ctx["pj_cust"]; pj_annual = product_ctx["pj_annual"]; pwj_cust = product_ctx["pwj_cust"]; pwj_annual = product_ctx["pwj_annual"]
    mjmk1_cust = product_ctx["mjmk1_cust"]; mjmk1_annual = product_ctx["mjmk1_annual"]; mjmk2_cust = product_ctx["mjmk2_cust"]; mjmk2_annual = product_ctx["mjmk2_annual"]
    ccmk1_cust = product_ctx["ccmk1_cust"]; ccmk1_annual = product_ctx["ccmk1_annual"]; ccmk2_cust = product_ctx["ccmk2_cust"]; ccmk2_annual = product_ctx["ccmk2_annual"]; qj_cust = product_ctx["qj_cust"]; qj_annual = product_ctx["qj_annual"]

    dmx_cntl_cust = product_ctx["dmx_cntl_cust"]; dmx_cntl_annual = product_ctx["dmx_cntl_annual"]; lcd_cntl_cust = product_ctx["lcd_cntl_cust"]; lcd_cntl_annual = product_ctx["lcd_cntl_annual"]; tbmk1_cust = product_ctx["tbmk1_cust"]; tbmk1_annual = product_ctx["tbmk1_annual"]
    pwr_cntl_cust = product_ctx["pwr_cntl_cust"]; pwr_cntl_annual = product_ctx["pwr_cntl_annual"]
    tbmk2_cust = product_ctx["tbmk2_cust"]; tbmk2_annual = product_ctx["tbmk2_annual"]; sm_cust = product_ctx["sm_cust"]; sm_annual = product_ctx["sm_annual"]; ss_cust = product_ctx["ss_cust"]; ss_annual = product_ctx["ss_annual"]

    blwr_cust = product_ctx["blwr_cust"]; blwr_annual = product_ctx['blwr_annual']
    
    

    col1, col2, col3 = st.columns([.25, .5, .25], gap='medium')

    with col2:
        
        # NAVIGATION TABS
        prod_cat = ui.tabs(options=['Jets', 'Controllers', 'Handhelds', 'Hoses', 'Accessories', 'MagicFX'], default_value='Jets', key='Product Categories')
       

    if prod_cat == 'Jets':

        pj_td23, pj_td24, pj_td25 = to_date_product('CC-PROJ')
        mj_td23, mj_td24, mj_td25 = to_date_product('CC-MJMK')
        qj_td23, qj_td24, qj_td25 = to_date_product('CC-QJ')
        cc_td23, cc_td24, cc_td25 = to_date_product('CC-CC2')

        with col2:
            year = ui.tabs(options=[2026, 2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015, 2014, 'Historical'], default_value=2026, key='Jet Year Select')

        if year == 2026:
            
            total_jet_rev = prodTot26['jet']['Pro Jet'][1] + prodTot26['jet']['Quad Jet'][1] + prodTot26['jet']['Micro Jet'][1] + prodTot26['jet']['Cryo Clamp'][1]
            
            with col2:
                cola, colb, colc, cold = st.columns(4, gap='medium')
    
                cola.subheader('Pro Jet')
                cola.metric('{:.1f}% of Total Revenue'.format((prodTot26['jet']['Pro Jet'][1] / td_26_tot) * 100), '{}'.format(int(prodTot26['jet']['Pro Jet'][0])), int(prodTot26['jet']['Pro Jet'][0] - pj_td25))
    
                colb.subheader('Quad Jet')
                colb.metric('{:.1f}% of Total Revenue'.format((prodTot26['jet']['Quad Jet'][1] / td_26_tot) * 100), '{}'.format(int(prodTot26['jet']['Quad Jet'][0])), int(prodTot26['jet']['Quad Jet'][0] - qj_td25))
    
                colc.subheader('Micro Jet')
                colc.metric('{:.1f}% of Total Revenue'.format((prodTot26['jet']['Micro Jet'][1] / td_26_tot) * 100), '{}'.format(int(prodTot26['jet']['Micro Jet'][0])), int(prodTot26['jet']['Micro Jet'][0] - mj_td25))
    
                cold.subheader('Cryo Clamp')
                cold.metric('{:.1f}% of Total Revenue'.format((prodTot26['jet']['Cryo Clamp'][1] / td_26_tot) * 100), '{}'.format(int(prodTot26['jet']['Cryo Clamp'][0])), int(prodTot26['jet']['Cryo Clamp'][0] - cc_td25))

                prod_profit_PJ, profit_per_unit_PJ, prod_profit_last_PJ, avg_price_PJ, avg_price_last_PJ, wholesale_sales_PJ, wholesale_percentage_PJ, wholesale_delta_PJ = calc_prod_metrics(prodTot26['jet'], 'Pro Jet', bom_cost_jet, prodTot25['jet'])
                prod_profit_QJ, profit_per_unit_QJ, prod_profit_last_QJ, avg_price_QJ, avg_price_last_QJ, wholesale_sales_QJ, wholesale_percentage_QJ, wholesale_delta_QJ = calc_prod_metrics(prodTot26['jet'], 'Quad Jet', bom_cost_jet, prodTot25['jet'])
                prod_profit_MJ, profit_per_unit_MJ, prod_profit_last_MJ, avg_price_MJ, avg_price_last_MJ, wholesale_sales_MJ, wholesale_percentage_MJ, wholesale_delta_MJ = calc_prod_metrics(prodTot26['jet'], 'Micro Jet', bom_cost_jet, prodTot25['jet'])
                prod_profit_CC, profit_per_unit_CC, prod_profit_last_CC, avg_price_CC, avg_price_last_CC, wholesale_sales_CC, wholesale_percentage_CC, wholesale_delta_CC = calc_prod_metrics(prodTot26['jet'], 'Cryo Clamp', bom_cost_jet, prodTot25['jet'])
                
                tot_jet_rev26 = prodTot26['jet']['Pro Jet'][1] + prodTot26['jet']['Quad Jet'][1] + prodTot26['jet']['Micro Jet'][1] + prodTot26['jet']['Cryo Clamp'][1]
                tot_jet_prof26 = prod_profit_PJ + prod_profit_QJ + prod_profit_MJ + prod_profit_CC
                if tot_jet_rev26 == 0:
                    jet_prof_margin26 = 0
                else:
                    jet_prof_margin26 = (tot_jet_prof26 / tot_jet_rev26) * 100
                
                colx, coly, colz = st.columns(3)
    
                colx.metric('**Total Revenue**', '${:,}'.format(int(tot_jet_rev26)))
                coly.metric('**Profit Margin**', '{:,.2f}%'.format(jet_prof_margin26))
                colz.metric('**Total Profit**', '${:,}'.format(int(tot_jet_prof26)))
    
                style_metric_cards()

                st.divider()
                display_pie_chart_comp(prodTot26['jet'])
                st.divider()

                prod_select = ui.tabs(options=['Pro Jet', 'Quad Jet', 'Micro Jet', 'Cryo Clamp'], default_value='Pro Jet', key='Jets')
        
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
    
                prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last, wholesale_sales, wholesale_percentage, wholesale_delta = calc_prod_metrics(prodTot26['jet'], prod_select, bom_cost_jet, prodTot25['jet'])

                # Calculate prior year to-date revenue for selected product
                prior_td_revenue = convert_prod_select(prod_select, 2026)

                # Convert prod_select to the td variable for 2024
                prod_td25 = convert_prod_select_profit(prod_select)
    
                col5.metric('**Revenue**', '${:,.2f}'.format(prodTot26['jet'][prod_select][1]), percent_of_change(prior_td_revenue, prodTot26['jet'][prod_select][1]))
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), percent_of_change(to_date_product_profit(prod_td25, prior_td_revenue, bom_cost_jet[prod_select]), prod_profit))
                col6.metric('**Wholesale**', '{:.2f}%'.format(wholesale_percentage))
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), percent_of_change(avg_price_last, avg_price))        
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_jet[prod_select]), '')
                
                display_month_data_prod(prod_select, jet26, jet25)
        
        
        elif year == 2025:
            
            total_jet_rev = prodTot25['jet']['Pro Jet'][1] + prodTot25['jet']['Quad Jet'][1] + prodTot25['jet']['Micro Jet'][1] + prodTot25['jet']['Cryo Clamp'][1]
            
            with col2:
                cola, colb, colc, cold = st.columns(4, gap='medium')
    
                cola.subheader('Pro Jet')
                cola.metric('{:.1f}% of Total Revenue'.format((prodTot25['jet']['Pro Jet'][1] / td_25_tot) * 100), '{}'.format(int(prodTot25['jet']['Pro Jet'][0])), int(prodTot25['jet']['Pro Jet'][0] - prodTot24['jet']['Pro Jet'][0]))
    
                colb.subheader('Quad Jet')
                colb.metric('{:.1f}% of Total Revenue'.format((prodTot25['jet']['Quad Jet'][1] / td_25_tot) * 100), '{}'.format(int(prodTot25['jet']['Quad Jet'][0])), int(prodTot25['jet']['Quad Jet'][0] - prodTot24['jet']['Quad Jet'][0]))
    
                colc.subheader('Micro Jet')
                colc.metric('{:.1f}% of Total Revenue'.format((prodTot25['jet']['Micro Jet'][1] / td_25_tot) * 100), '{}'.format(int(prodTot25['jet']['Micro Jet'][0])), int(prodTot25['jet']['Micro Jet'][0] - prodTot24['jet']['Micro Jet'][0]))
    
                cold.subheader('Cryo Clamp')
                cold.metric('{:.1f}% of Total Revenue'.format((prodTot25['jet']['Cryo Clamp'][1] / td_25_tot) * 100), '{}'.format(int(prodTot25['jet']['Cryo Clamp'][0])), int(prodTot25['jet']['Cryo Clamp'][0] - prodTot24['jet']['Cryo Clamp'][0]))

                prod_profit_PJ, profit_per_unit_PJ, prod_profit_last_PJ, avg_price_PJ, avg_price_last_PJ, wholesale_sales_PJ, wholesale_percentage_PJ, wholesale_delta_PJ = calc_prod_metrics(prodTot25['jet'], 'Pro Jet', bom_cost_jet, prodTot24['jet'])
                prod_profit_QJ, profit_per_unit_QJ, prod_profit_last_QJ, avg_price_QJ, avg_price_last_QJ, wholesale_sales_QJ, wholesale_percentage_QJ, wholesale_delta_QJ = calc_prod_metrics(prodTot25['jet'], 'Quad Jet', bom_cost_jet, prodTot24['jet'])
                prod_profit_MJ, profit_per_unit_MJ, prod_profit_last_MJ, avg_price_MJ, avg_price_last_MJ, wholesale_sales_MJ, wholesale_percentage_MJ, wholesale_delta_MJ = calc_prod_metrics(prodTot25['jet'], 'Micro Jet', bom_cost_jet, prodTot24['jet'])
                prod_profit_CC, profit_per_unit_CC, prod_profit_last_CC, avg_price_CC, avg_price_last_CC, wholesale_sales_CC, wholesale_percentage_CC, wholesale_delta_CC = calc_prod_metrics(prodTot25['jet'], 'Cryo Clamp', bom_cost_jet, prodTot24['jet'])
                
                tot_jet_rev25 = prodTot25['jet']['Pro Jet'][1] + prodTot25['jet']['Quad Jet'][1] + prodTot25['jet']['Micro Jet'][1] + prodTot25['jet']['Cryo Clamp'][1]
                tot_jet_prof25 = prod_profit_PJ + prod_profit_QJ + prod_profit_MJ + prod_profit_CC
                if tot_jet_rev25 == 0:
                    jet_prof_margin25 = 0
                else:
                    jet_prof_margin25 = (tot_jet_prof25 / tot_jet_rev25) * 100
                
                colx, coly, colz = st.columns(3)
    
                colx.metric('**Total Revenue**', '${:,}'.format(int(tot_jet_rev25)))
                coly.metric('**Profit Margin**', '{:,.2f}%'.format(jet_prof_margin25))
                colz.metric('**Total Profit**', '${:,}'.format(int(tot_jet_prof25)))
    
                style_metric_cards()

                st.divider()
                display_pie_chart_comp(prodTot25['jet'])
                st.divider()

                prod_select = ui.tabs(options=['Pro Jet', 'Quad Jet', 'Micro Jet', 'Cryo Clamp'], default_value='Pro Jet', key='Jets')
        
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
    
                prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last, wholesale_sales, wholesale_percentage, wholesale_delta = calc_prod_metrics(prodTot25['jet'], prod_select, bom_cost_jet, prodTot24['jet'])

                # Calculate prior year to-date revenue for selected product
                prior_td_revenue = convert_prod_select(prod_select, 2025)

                # Convert prod_select to the td variable for 2024
                prod_td24 = convert_prod_select_profit(prod_select)
    
                col5.metric('**Revenue**', '${:,.2f}'.format(prodTot25['jet'][prod_select][1]), percent_of_change(prior_td_revenue, prodTot25['jet'][prod_select][1]))
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), percent_of_change(to_date_product_profit(prod_td24, prior_td_revenue, bom_cost_jet[prod_select]), prod_profit))
                col6.metric('**Wholesale**', '{:.2f}%'.format(wholesale_percentage))
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), percent_of_change(avg_price_last, avg_price))        
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_jet[prod_select]), '')
                
                display_month_data_prod(prod_select, jet25, jet24)

        
        elif year == 2024:
            
            total_jet_rev = prodTot24['jet']['Pro Jet'][1] + prodTot24['jet']['Quad Jet'][1] + prodTot24['jet']['Micro Jet'][1] + prodTot24['jet']['Cryo Clamp'][1]
            
            with col2:
                cola, colb, colc, cold = st.columns(4)
    
                cola.subheader('Pro Jet')
                cola.metric('{:.1f}% of Total Revenue'.format((prodTot24['jet']['Pro Jet'][1] / total_24) * 100), '{}'.format(int(prodTot24['jet']['Pro Jet'][0])), int(prodTot24['jet']['Pro Jet'][0] - prodTot23['jet']['Pro Jet'][0]))
    
                colb.subheader('Quad Jet')
                colb.metric('{:.1f}% of Total Revenue'.format((prodTot24['jet']['Quad Jet'][1] / total_24) * 100), '{}'.format(int(prodTot24['jet']['Quad Jet'][0])), int(prodTot24['jet']['Quad Jet'][0] - prodTot23['jet']['Quad Jet'][0]))
    
                colc.subheader('Micro Jet')
                colc.metric('{:.1f}% of Total Revenue'.format((prodTot24['jet']['Micro Jet'][1] / total_24) * 100), '{}'.format(int(prodTot24['jet']['Micro Jet'][0])), int(prodTot24['jet']['Micro Jet'][0] - prodTot23['jet']['Micro Jet'][0]))
    
                cold.subheader('Cryo Clamp')
                cold.metric('{:.1f}% of Total Revenue'.format((prodTot24['jet']['Cryo Clamp'][1] / total_24) * 100), '{}'.format(int(prodTot24['jet']['Cryo Clamp'][0])), int(prodTot24['jet']['Cryo Clamp'][0] - prodTot23['jet']['Cryo Clamp'][0]))

                prod_profit_PJ, profit_per_unit_PJ, prod_profit_last_PJ, avg_price_PJ, avg_price_last_PJ, wholesale_sales_PJ, wholesale_percentage_PJ, wholesale_delta_PJ = calc_prod_metrics(prodTot24['jet'], 'Pro Jet', bom_cost_jet, prodTot23['jet'])
                prod_profit_QJ, profit_per_unit_QJ, prod_profit_last_QJ, avg_price_QJ, avg_price_last_QJ, wholesale_sales_QJ, wholesale_percentage_QJ, wholesale_delta_QJ = calc_prod_metrics(prodTot24['jet'], 'Quad Jet', bom_cost_jet, prodTot23['jet'])
                prod_profit_MJ, profit_per_unit_MJ, prod_profit_last_MJ, avg_price_MJ, avg_price_last_MJ, wholesale_sales_MJ, wholesale_percentage_MJ, wholesale_delta_MJ = calc_prod_metrics(prodTot24['jet'], 'Micro Jet', bom_cost_jet, prodTot23['jet'])
                prod_profit_CC, profit_per_unit_CC, prod_profit_last_CC, avg_price_CC, avg_price_last_CC, wholesale_sales_CC, wholesale_percentage_CC, wholesale_delta_CC = calc_prod_metrics(prodTot24['jet'], 'Cryo Clamp', bom_cost_jet, prodTot23['jet'])
                
                tot_jet_rev24 = prodTot24['jet']['Pro Jet'][1] + prodTot24['jet']['Quad Jet'][1] + prodTot24['jet']['Micro Jet'][1] + prodTot24['jet']['Cryo Clamp'][1]
                tot_jet_prof24 = prod_profit_PJ + prod_profit_QJ + prod_profit_MJ + prod_profit_CC
                jet_prof_margin24 = (tot_jet_prof24 / tot_jet_rev24) * 100
                
                colx, coly, colz = st.columns(3)
    
                colx.metric('**Total Revenue**', '${:,}'.format(int(tot_jet_rev24)))
                coly.metric('**Profit Margin**', '{:,.2f}%'.format(jet_prof_margin24))
                colz.metric('**Total Profit**', '${:,}'.format(int(tot_jet_prof24)))
                
                style_metric_cards()

                st.divider()
                display_pie_chart_comp(prodTot24['jet'])
                st.divider()
                
                prod_select = ui.tabs(options=['Pro Jet', 'Quad Jet', 'Micro Jet', 'Cryo Clamp'], default_value='Pro Jet', key='Jets')
        
                prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last, wholesale_sales, wholesale_percentage, wholesale_delta = calc_prod_metrics(prodTot24['jet'], prod_select, bom_cost_jet, prodTot23['jet'])

                # Calculate prior year to-date revenue for selected product
                #prior_td_revenue = convert_prod_select(prod_select, 2024)
                
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
        
                col5.metric('**Revenue**', '${:,.2f}'.format(prodTot24['jet'][prod_select][1]), percent_of_change(prodTot23['jet'][prod_select][1], prodTot24['jet'][prod_select][1]))
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), percent_of_change(prod_profit_last, prod_profit))
                col6.metric('**Wholesale**', '{:.2f}%'.format(wholesale_percentage))
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), percent_of_change(avg_price_last, avg_price))        
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_jet[prod_select]), '')
            
                    
                display_month_data_prod(prod_select, jet24, jet23)
            
            
        elif year == 2023:
            
            total_jet_rev = prodTot23['jet']['Pro Jet'][1] + prodTot23['jet']['Quad Jet'][1] + prodTot23['jet']['Micro Jet'][1] + prodTot23['jet']['Cryo Clamp'][1]
            
            with col2:
                cola, colb, colc, cold = st.columns(4)
        
                cola.subheader('Pro Jet')
                cola.metric('{:.1f}% of Total Revenue'.format((prodTot23['jet']['Pro Jet'][1] / total_23) * 100), '{}'.format(int(prodTot23['jet']['Pro Jet'][0])), '')
    
                colb.subheader('Quad Jet')
                colb.metric('{:.1f}% of Total Revenue'.format((prodTot23['jet']['Quad Jet'][1] / total_23) * 100), '{}'.format(int(prodTot23['jet']['Quad Jet'][0])), '')
    
                colc.subheader('Micro Jet')
                colc.metric('{:.1f}% of Total Revenue'.format((prodTot23['jet']['Micro Jet'][1] / total_23) * 100), '{}'.format(int(prodTot23['jet']['Micro Jet'][0])), '')
    
                cold.subheader('Cryo Clamp')
                cold.metric('{:.1f}% of Total Revenue'.format((prodTot23['jet']['Cryo Clamp'][1] / total_23) * 100), '{}'.format(int(prodTot23['jet']['Cryo Clamp'][0])), '')
    
                prod_profit_PJ, profit_per_unit_PJ, prod_profit_last_PJ, avg_price_PJ, avg_price_last_PJ = calc_prod_metrics(prodTot23['jet'], 'Pro Jet', bom_cost_jet)
                prod_profit_QJ, profit_per_unit_QJ, prod_profit_last_QJ, avg_price_QJ, avg_price_last_QJ = calc_prod_metrics(prodTot23['jet'], 'Quad Jet', bom_cost_jet)
                prod_profit_MJ, profit_per_unit_MJ, prod_profit_last_MJ, avg_price_MJ, avg_price_last_MJ = calc_prod_metrics(prodTot23['jet'], 'Micro Jet', bom_cost_jet)
                prod_profit_CC, profit_per_unit_CC, prod_profit_last_CC, avg_price_CC, avg_price_last_CC = calc_prod_metrics(prodTot23['jet'], 'Cryo Clamp', bom_cost_jet)
                
                tot_jet_rev23 = prodTot23['jet']['Pro Jet'][1] + prodTot23['jet']['Quad Jet'][1] + prodTot23['jet']['Micro Jet'][1] + prodTot23['jet']['Cryo Clamp'][1]
                tot_jet_prof23 = prod_profit_PJ + prod_profit_QJ + prod_profit_MJ + prod_profit_CC
                jet_prof_margin23 = (tot_jet_prof23 / tot_jet_rev23) * 100
                
                colx, coly, colz = st.columns(3)
    
                colx.metric('**Total Revenue**', '${:,}'.format(int(tot_jet_rev23)))
                coly.metric('**Profit Margin**', '{:,.2f}%'.format(jet_prof_margin23))
                colz.metric('**Total Profit**', '${:,}'.format(int(tot_jet_prof23)))
         
                style_metric_cards()
                
                st.divider()
                display_pie_chart_comp(prodTot23['jet'])
                st.divider()
                
                prod_select = ui.tabs(options=['Pro Jet', 'Quad Jet', 'Micro Jet', 'Cryo Clamp'], default_value='Pro Jet', key='Jets')
        
        
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
                
                prod_profit, profit_per_unit, avg_price, wholesale_sales, wholesale_percentage = calc_prod_metrics(prodTot23['jet'], prod_select, bom_cost_jet)
    
    
                col5.metric('**Revenue**', '${:,.2f}'.format(prodTot23['jet'][prod_select][1]), '')
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), '')
                col6.metric('**Wholesale**', '{:.2f}%'.format(wholesale_percentage))
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), '')        
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_jet[prod_select]), '')
                
                display_month_data_prod(prod_select, jet23)  

        elif year == 2022:
            
            with col2:
                cola, colb, colc= st.columns(3)
        
                cola.subheader('Pro Jet')
                cola.metric('', '{}'.format(pj_annual['2022']), 'N/A')
    
                colb.subheader('Quad Jet')
                colb.metric('', '{}'.format(qj_annual['2022']), (qj_annual['2022'] - qj_annual['2021']))

                colc.subheader('Cryo Clamp MK1')
                colc.metric('', '{}'.format(ccmk1_annual['2022']), (ccmk1_annual['2022'] - ccmk1_annual['2021']))
    
                cola.subheader('Micro Jet MK1')
                cola.metric('', '{}'.format(mjmk1_annual['2022']), (mjmk1_annual['2022'] - mjmk1_annual['2021']))
                                        
                colb.subheader('Total Jets')
                colb.metric('', '{}'.format(mjmk1_annual['2022'] + mjmk2_annual['2022'] + ccmk1_annual['2022'] + pj_annual['2022'] + qj_annual['2022']), ((mjmk1_annual['2022'] + mjmk2_annual['2022'] + ccmk1_annual['2022'] + pj_annual['2022'] + qj_annual['2022']) - (mjmk1_annual['2021'] + mjmk2_annual['2021'] + ccmk1_annual['2021'] + jet_og_annual['2021'] + qj_annual['2021'] + pwj_annual['2021'])))
                
                colc.subheader('Micro Jet MK2')
                colc.metric('', '{}'.format(mjmk2_annual['2022']), (mjmk2_annual['2022'] - mjmk2_annual['2021']))

                style_metric_cards()

        elif year == 2021:
            
            with col2:
                cola, colb, colc = st.columns(3)
        
                cola.subheader('DMX Jet')
                cola.metric('', '{}'.format(jet_og_annual['2021']), (jet_og_annual['2021'] - jet_og_annual['2020']))
    
                colb.subheader('Quad Jet')
                colb.metric('', '{}'.format(qj_annual['2021']), (qj_annual['2021'] - qj_annual['2020']))

                colc.subheader('Cryo Clamp MK1')
                colc.metric('', '{}'.format(ccmk1_annual['2021']), (ccmk1_annual['2021'] - ccmk1_annual['2020']))
    
                cola.subheader('Micro Jet MK1')
                cola.metric('', '{}'.format(mjmk1_annual['2021']), (mjmk1_annual['2021'] - mjmk1_annual['2020']))

                colb.subheader('Power Jet')
                colb.metric('', '{}'.format(pwj_annual['2021']), (pwj_annual['2021'] - pwj_annual['2020']))
                                        
                colb.subheader('Total Jets')
                colb.metric('', '{}'.format(mjmk1_annual['2021'] + mjmk2_annual['2021'] + ccmk1_annual['2021'] + jet_og_annual['2021'] + qj_annual['2021'] + pwj_annual['2021']), (mjmk1_annual['2021'] + mjmk2_annual['2021'] + ccmk1_annual['2021'] + jet_og_annual['2021'] + qj_annual['2021'] + pwj_annual['2021'] - (mjmk1_annual['2020'] + ccmk1_annual['2020'] + jet_og_annual['2020'] +  pwj_annual['2020'])))
                
                colc.subheader('Micro Jet MK2')
                colc.metric('', '{}'.format(mjmk2_annual['2021']), (mjmk2_annual['2021'] - mjmk2_annual['2020']))

                style_metric_cards()

        elif year == 2020:
            
            with col2:
                cola, colb, colc = st.columns(3)
        
                cola.subheader('DMX Jet')
                cola.metric('', '{}'.format(jet_og_annual['2020']), (jet_og_annual['2020'] - jet_og_annual['2019']))
    
                colb.subheader('Micro Jet MK1')
                colb.metric('', '{}'.format(mjmk1_annual['2020']), (mjmk1_annual['2020'] - mjmk1_annual['2019']))

                colc.subheader('Power Jet')
                colc.metric('', '{}'.format(pwj_annual['2020']), (pwj_annual['2020'] - pwj_annual['2019']))

                colb.subheader('Cryo Clamp MK1')
                colb.metric('', '{}'.format(ccmk1_annual['2020']), (ccmk1_annual['2020'] - ccmk1_annual['2019']))

                colb.subheader('Total Jets')
                colb.metric('', '{}'.format(mjmk1_annual['2020'] + ccmk1_annual['2020'] + jet_og_annual['2020'] +  pwj_annual['2020']), ((mjmk1_annual['2020'] + ccmk1_annual['2020'] + jet_og_annual['2020'] +  pwj_annual['2020']) - (mjmk1_annual['2019'] + ccmk1_annual['2019'] + jet_og_annual['2019'] +  pwj_annual['2019'])))
                

                style_metric_cards()

        elif year == 2019:
            
            with col2:
                cola, colb, colc = st.columns(3)
        
                cola.subheader('DMX Jet')
                cola.metric('', '{}'.format(jet_og_annual['2019']), (jet_og_annual['2019'] - jet_og_annual['2018']))
    
                colb.subheader('Micro Jet MK1')
                colb.metric('', '{}'.format(mjmk1_annual['2019']), (mjmk1_annual['2019'] - mjmk1_annual['2018']))

                colc.subheader('Power Jet')
                colc.metric('', '{}'.format(pwj_annual['2019']), (pwj_annual['2019'] - pwj_annual['2018']))

                colb.subheader('Cryo Clamp MK1')
                colb.metric('', '{}'.format(ccmk1_annual['2019']), (ccmk1_annual['2019'] - ccmk1_annual['2018']))

                colb.subheader('Total Jets')
                colb.metric('', '{}'.format(mjmk1_annual['2019'] + ccmk1_annual['2019'] + jet_og_annual['2019'] +  pwj_annual['2019']), ((mjmk1_annual['2019'] + ccmk1_annual['2019'] + jet_og_annual['2019'] +  pwj_annual['2019']) - (mjmk1_annual['2018'] + ccmk1_annual['2018'] + jet_og_annual['2018'] +  pwj_annual['2018'])))
                
                style_metric_cards()

        elif year == 2018:
            
            with col2:
                cola, colb, colc = st.columns(3)
        
                cola.subheader('DMX Jet')
                cola.metric('', '{}'.format(jet_og_annual['2018']), (jet_og_annual['2018'] - jet_og_annual['2017']))

                colb.subheader('Power Jet')
                colb.metric('', '{}'.format(pwj_annual['2018']), (pwj_annual['2018'] - pwj_annual['2017']))

                colc.subheader('Cryo Clamp MK1')
                colc.metric('', '{}'.format(ccmk1_annual['2018']), (ccmk1_annual['2018'] - ccmk1_annual['2017']))

                colb.subheader('Total Jets')
                colb.metric('', '{}'.format(ccmk1_annual['2018'] + jet_og_annual['2018'] +  pwj_annual['2018']), ((ccmk1_annual['2018'] + jet_og_annual['2018'] +  pwj_annual['2018']) - (ccmk1_annual['2017'] + jet_og_annual['2017'] +  pwj_annual['2017'])))

                style_metric_cards()

        elif year == 2017:
            
            with col2:
                cola, colb, colc = st.columns(3)
        
                cola.subheader('DMX Jet')
                cola.metric('', '{}'.format(jet_og_annual['2017']), (jet_og_annual['2017'] - jet_og_annual['2016']))

                colb.subheader('Power Jet')
                colb.metric('', '{}'.format(pwj_annual['2017']), (pwj_annual['2017'] - pwj_annual['2016']))

                colc.subheader('**Total Jets**')
                colc.metric('', '{}'.format(jet_og_annual['2017'] + pwj_annual['2017']), ((jet_og_annual['2017'] +  pwj_annual['2017']) - (jet_og_annual['2016'] +  pwj_annual['2016'])))
            
                style_metric_cards()

        elif year == 2016:
            
            with col2:
                cola, colb, colc = st.columns(3)
        
                colb.subheader('DMX Jet')
                colb.metric('', '{}'.format(jet_og_annual['2016']), (jet_og_annual['2016'] - jet_og_annual['2015']))

                style_metric_cards()

        elif year == 2015:
            
            with col2:
                cola, colb, colc = st.columns(3)
        
                colb.subheader('DMX Jet')
                colb.metric('', '{}'.format(jet_og_annual['2015']), (jet_og_annual['2015'] - jet_og_annual['2014']))

                style_metric_cards()

        elif year == 2014:
            
            with col2:
                cola, colb, colc = st.columns(3)
        
                colb.subheader('DMX Jet')
                colb.metric('', '{}'.format(jet_og_annual['2014']), '')

                style_metric_cards()

        elif year == 'Historical':

            pj_tot_unit = prodTot25['jet']['Pro Jet'][0] + prodTot24['jet']['Pro Jet'][0] + prodTot23['jet']['Pro Jet'][0] + pj_annual['2022']
            pj_tot_rev = prodTot25['jet']['Pro Jet'][1] + prodTot24['jet']['Pro Jet'][1] + prodTot23['jet']['Pro Jet'][1] + (pj_annual['2022'] * 1174)

            qj_tot_unit = prodTot25['jet']['Quad Jet'][0] + prodTot24['jet']['Quad Jet'][0] + prodTot23['jet']['Quad Jet'][0] + qj_annual['2022']
            qj_tot_rev = prodTot25['jet']['Quad Jet'][1] + prodTot24['jet']['Quad Jet'][1] + prodTot23['jet']['Quad Jet'][1] + (qj_annual['2022'] * 1800)

            mj2_tot_unit = prodTot25['jet']['Micro Jet'][0] + prodTot24['jet']['Micro Jet'][0] + prodTot23['jet']['Micro Jet'][0] + mjmk2_annual['2022'] + mjmk2_annual['2021']
            mj2_tot_rev = prodTot25['jet']['Micro Jet'][1] + prodTot24['jet']['Micro Jet'][1] + prodTot23['jet']['Micro Jet'][1] + (mjmk2_annual['2022'] * 778) + (mjmk2_annual['2021'] * 778)

            mj1_tot_unit = mjmk1_annual['2022'] + mjmk1_annual['2021'] + mjmk1_annual['2020'] + mjmk1_annual['2019']
            mj1_tot_rev = (mjmk1_annual['2022'] * 778.63) + (mjmk1_annual['2021'] * 778.99) + (mjmk1_annual['2020'] * 778.52) + (mjmk1_annual['2019'] * 778)

            cc2_tot_unit = prodTot25['jet']['Cryo Clamp'][0] + prodTot24['jet']['Cryo Clamp'][0] + prodTot23['jet']['Cryo Clamp'][0]
            cc2_tot_rev = prodTot25['jet']['Cryo Clamp'][1] + prodTot24['jet']['Cryo Clamp'][1] + prodTot23['jet']['Cryo Clamp'][1] 

            cc1_tot_unit = ccmk1_annual['2022'] + ccmk1_annual['2021'] + ccmk1_annual['2020'] + ccmk1_annual['2019'] + ccmk1_annual['2018']
            cc1_tot_rev = (ccmk1_annual['2022'] * 387.91) + (ccmk1_annual['2021'] * 387.91) + (ccmk1_annual['2020'] * 387.91) + (ccmk1_annual['2019'] * 387.91) + (ccmk1_annual['2018'] * 387.91)

            dmx_jet_tot_unit = jet_og_annual['2021'] + jet_og_annual['2020'] + jet_og_annual['2019'] + jet_og_annual['2018'] + jet_og_annual['2017'] + jet_og_annual['2016'] + jet_og_annual['2015'] + jet_og_annual['2014']
            dmx_jet_tot_rev = (jet_og_annual['2021'] * 1098.54) + (jet_og_annual['2020'] * 1098.54) + (jet_og_annual['2019'] * 1098.54) + (jet_og_annual['2018'] * 1098.54) + (jet_og_annual['2017'] * 1098.54) + (jet_og_annual['2016'] * 1098.54) + (jet_og_annual['2015'] * 1098.54) + (jet_og_annual['2014'] * 1098.54)
            
            pwj_tot_unit = pwj_annual['2021'] + pwj_annual['2020'] + pwj_annual['2019'] + pwj_annual['2018'] + pwj_annual['2017'] 
            pwj_tot_rev = (pwj_annual['2021'] * 948.53) + (pwj_annual['2020'] * 948.53) + (pwj_annual['2019'] * 948.53) + (pwj_annual['2018'] * 948.53) + (pwj_annual['2017'] * 948.53)


            cola, colb, colc, cold, cole = st.columns(5)

            colb.subheader('Pro Jet')
            colb.metric('**${:,.2f}**'.format(pj_tot_rev), '{}'.format(int(pj_tot_unit)))
            colb.subheader('Cryo Clamp MKII')
            colb.metric('**${:,.2f}**'.format(cc2_tot_rev), '{}'.format(int(cc2_tot_unit)))
            colb.subheader('Cryo Clamp MKI')
            colb.metric('**${:,.2f}**'.format(cc1_tot_rev), '{}'.format(cc1_tot_unit))

            colc.subheader('Quad Jet')
            colc.metric('**${:,.2f}**'.format(qj_tot_rev), '{}'.format(int(qj_tot_unit)))
            colc.subheader('Power Jet')
            colc.metric('**${:,.2f}**'.format(pwj_tot_rev), '{}'.format(pwj_tot_unit))
            colc.subheader('Total Jets')
            colc.metric('**${:,.2f}**'.format(pwj_tot_rev + dmx_jet_tot_rev + cc1_tot_rev + cc2_tot_rev + mj1_tot_rev + mj2_tot_rev + qj_tot_rev + pj_tot_rev), '{}'.format(int(pwj_tot_unit + dmx_jet_tot_unit + cc1_tot_unit + cc2_tot_unit + mj1_tot_unit + mj2_tot_unit + qj_tot_unit + pj_tot_unit)))

            cold.subheader('DMX Jet')
            cold.metric('**${:,.2f}**'.format(dmx_jet_tot_rev), '{}'.format(dmx_jet_tot_unit))
            cold.subheader('Micro Jet MKII')
            cold.metric('**${:,.2f}**'.format(mj2_tot_rev), '{}'.format(int(mj2_tot_unit)))
            cold.subheader('Micro Jet MKI')
            cold.metric('**${:,.2f}**'.format(mj1_tot_rev), '{}'.format(mj1_tot_unit))

            style_metric_cards()

            jet_annual_dict = {'2025': 0, '2024': 0, '2023': 0, '2022': 0, '2021': 0, '2020': 0, '2019': 0, '2018': 0, '2017': 0, '2016': 0, '2015': 0, '2014': 0}
            jet_annual_dict_seg = {'2025': {'Pro Jet': prodTot25['jet']['Pro Jet'][0], 'Quad Jet': prodTot25['jet']['Quad Jet'][0], 'Micro Jet MKII': prodTot25['jet']['Micro Jet'][0], 'Cryo Clamp': prodTot25['jet']['Cryo Clamp'][0]}, '2024': {'Pro Jet': prodTot24['jet']['Pro Jet'][0], 'Quad Jet': prodTot24['jet']['Quad Jet'][0], 'Micro Jet MKII': prodTot24['jet']['Micro Jet'][0], 'Cryo Clamp': prodTot24['jet']['Cryo Clamp'][0]}, '2023': {'Pro Jet': prodTot23['jet']['Pro Jet'][0], 'Quad Jet': prodTot23['jet']['Quad Jet'][0], 'Micro Jet MKII': prodTot23['jet']['Micro Jet'][0], 'Cryo Clamp': prodTot23['jet']['Cryo Clamp'][0]}, '2022': {'Pro Jet': pj_annual['2022'], 'Quad Jet': qj_annual['2022'], 'Micro Jet MKII': mjmk2_annual['2022'], 'Micro Jet MKI': mjmk1_annual['2022'], 'Cryo Clamp MKI': ccmk1_annual['2022']}, '2021': {'Micro Jet MKII': mjmk2_annual['2021'], 'Micro Jet MKI': mjmk1_annual['2021'], 'Cryo Clamp MKI': ccmk1_annual['2021'], 'Quad Jet': qj_annual['2021'], 'DMX Jet': jet_og_annual['2021'], 'Power Jet': pwj_annual['2021']}, '2020': {'Micro Jet MKI': mjmk1_annual['2020'], 'Cryo Clamp MKI': ccmk1_annual['2020'], 'DMX Jet': jet_og_annual['2020'], 'Power Jet': pwj_annual['2020']}, '2019': {'Micro Jet MKI': mjmk1_annual['2019'], 'Cryo Clamp MKI': ccmk1_annual['2019'], 'DMX Jet': jet_og_annual['2019'], 'Power Jet': pwj_annual['2019']}, '2018': {'Cryo Clamp MKI': ccmk1_annual['2018'], 'DMX Jet': jet_og_annual['2018'], 'Power Jet': pwj_annual['2018']}, '2017': {'DMX Jet': jet_og_annual['2017'], 'Power Jet': pwj_annual['2017']}, '2016': {'DMX Jet': jet_og_annual['2016']}, '2015': {'DMX Jet': jet_og_annual['2015']}, '2014': {'DMX Jet': jet_og_annual['2014']}}
            jet_annual_dict['2025'] += prodTot25['jet']['Pro Jet'][0] + prodTot25['jet']['Quad Jet'][0] + prodTot25['jet']['Micro Jet'][0] + prodTot25['jet']['Cryo Clamp'][0] 
            jet_annual_dict['2024'] += prodTot24['jet']['Pro Jet'][0] + prodTot24['jet']['Quad Jet'][0] + prodTot24['jet']['Micro Jet'][0] + prodTot24['jet']['Cryo Clamp'][0]
            jet_annual_dict['2023'] += prodTot23['jet']['Pro Jet'][0] + prodTot23['jet']['Quad Jet'][0] + prodTot23['jet']['Micro Jet'][0] + prodTot23['jet']['Cryo Clamp'][0]

            jet_list = [pj_annual, pwj_annual, jet_og_annual, ccmk1_annual, mjmk1_annual, mjmk2_annual, qj_annual]
            year_list = ['2022', '2021', '2020', '2019', '2018', '2017', '2016', '2015', '2014']
            
            colx, coly, colz = st.columns([.2, .6, .2])
            with coly:
                plot_bar_chart_product_seg(format_for_chart_product_seg(jet_annual_dict_seg, 'Total Jet Sales'), 'Total Jet Sales')


            

    elif prod_cat == 'Controllers':

        tb_td23, tb_td24, tb_td25 = to_date_product('CC-TB-35')
        ss_td23, ss_td24, ss_td25 = to_date_product('CC-SS-35')
        sm_td23, sm_td24, sm_td25 = to_date_product('CC-SM')

        with col2:
            year = ui.tabs(options=[2026, 2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015, 'Historical'], default_value=2026, key='Control Year Select')

        if year == 2026:
            
            total_cntl_rev = prodTot26['control']['The Button'][1] + prodTot26['control']['Shostarter'][1] + prodTot26['control']['Shomaster'][1]
            
            with col2:
                cola, colb, colc = st.columns(3)
                
                cola.subheader('The Button')
                cola.metric('{:.1f}% of Total Revenue'.format((prodTot26['control']['The Button'][1] / td_26_tot) * 100), '{}'.format(int(prodTot26['control']['The Button'][0])), int(prodTot26['control']['The Button'][0] - tb_td25))
                colb.subheader('Shostarter')
                colb.metric('{:.1f}% of Total Revenue'.format((prodTot26['control']['Shostarter'][1] / td_26_tot) * 100), '{}'.format(int(prodTot26['control']['Shostarter'][0])), int(prodTot26['control']['Shostarter'][0] - ss_td25))
                colc.subheader('Shomaster')
                colc.metric('{:.1f}% of Total Revenue'.format((prodTot26['control']['Shomaster'][1] / td_26_tot) * 100), '{}'.format(int(prodTot26['control']['Shomaster'][0])), int(prodTot26['control']['Shomaster'][0] - sm_td25))
    
                prod_profit_TB, profit_per_unit_TB, prod_profit_last_TB, avg_price_TB, avg_price_last_TB, wholesale_sales_TB, wholesale_percentage_TB, wholesale_delta_TB = calc_prod_metrics(prodTot26['control'], 'The Button', bom_cost_control, prodTot25['control'])
                prod_profit_SS, profit_per_unit_SS, prod_profit_last_SS, avg_price_SS, avg_price_last_SS, wholesale_sales_SS, wholesale_percentage_SS, wholesale_delta_SS = calc_prod_metrics(prodTot26['control'], 'Shostarter', bom_cost_control, prodTot25['control'])
                prod_profit_SM, profit_per_unit_SM, prod_profit_last_SM, avg_price_SM, avg_price_last_SM, wholesale_sales_SM, wholesale_percentage_SM, wholesale_delta_SM = calc_prod_metrics(prodTot26['control'], 'Shomaster', bom_cost_control, prodTot25['control'])
    
                tot_cntl_rev26 = prodTot26['control']['The Button'][1] + prodTot26['control']['Shostarter'][1] + prodTot26['control']['Shomaster'][1]
                tot_cntl_prof26 = prod_profit_TB + prod_profit_SS + prod_profit_SM
                if tot_cntl_rev26 == 0:
                    cntl_prof_margin26 = 0
                else:
                    cntl_prof_margin26 = (tot_cntl_prof26 / tot_cntl_rev26) * 100
    
                cola.metric('**Total Revenue**', '${:,}'.format(int(tot_cntl_rev26)))
                colb.metric('**Profit Margin**', '{:,.2f}%'.format(cntl_prof_margin26))
                colc.metric('**Total Profit**', '${:,}'.format(int(tot_cntl_prof26)))
        
                st.divider()
                display_pie_chart_comp(prodTot26['control'])
                st.divider()
                
                prod_select = ui.tabs(options=['The Button', 'Shostarter', 'Shomaster'], default_value='The Button', key='Controllers')
        
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
    
                prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last, wholesale_sales, wholesale_percentage, wholesale_delta = calc_prod_metrics(prodTot26['control'], prod_select, bom_cost_control, prodTot25['control'])

                # Calculate prior year to-date revenue for selected product
                prior_td_revenue = convert_prod_select(prod_select, 2026)

                # Convert prod_select to the td variable for 2024
                prod_td25 = convert_prod_select_profit(prod_select)
                
                col5.metric('**Revenue**', '${:,.2f}'.format(prodTot26['control'][prod_select][1]), percent_of_change(prior_td_revenue, prodTot26['control'][prod_select][1]))
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), percent_of_change(to_date_product_profit(prod_td25, prior_td_revenue, bom_cost_control[prod_select]), prod_profit))
                col6.metric('**Wholesale**', '{:.2f}%'.format(wholesale_percentage))
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), percent_of_change(avg_price_last, avg_price))
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_control[prod_select]), '')
                
                style_metric_cards()
                
                display_month_data_prod(prod_select, control26, control25) 

        
        elif year == 2025:
            
            total_cntl_rev = prodTot25['control']['The Button'][1] + prodTot25['control']['Shostarter'][1] + prodTot25['control']['Shomaster'][1]
            
            with col2:
                cola, colb, colc = st.columns(3)
                
                cola.subheader('The Button')
                cola.metric('{:.1f}% of Total Revenue'.format((prodTot25['control']['The Button'][1] / td_25_tot) * 100), '{}'.format(int(prodTot25['control']['The Button'][0])), int(prodTot25['control']['The Button'][0] - prodTot24['control']['The Button'][0]))
                colb.subheader('Shostarter')
                colb.metric('{:.1f}% of Total Revenue'.format((prodTot25['control']['Shostarter'][1] / td_25_tot) * 100), '{}'.format(int(prodTot25['control']['Shostarter'][0])), int(prodTot25['control']['Shostarter'][0] - prodTot24['control']['Shostarter'][0]))
                colc.subheader('Shomaster')
                colc.metric('{:.1f}% of Total Revenue'.format((prodTot25['control']['Shomaster'][1] / td_25_tot) * 100), '{}'.format(int(prodTot25['control']['Shomaster'][0])), int(prodTot25['control']['Shomaster'][0] - prodTot24['control']['Shomaster'][0]))
    
                prod_profit_TB, profit_per_unit_TB, prod_profit_last_TB, avg_price_TB, avg_price_last_TB, wholesale_sales_TB, wholesale_percentage_TB, wholesale_delta_TB = calc_prod_metrics(prodTot25['control'], 'The Button', bom_cost_control, prodTot24['control'])
                prod_profit_SS, profit_per_unit_SS, prod_profit_last_SS, avg_price_SS, avg_price_last_SS, wholesale_sales_SS, wholesale_percentage_SS, wholesale_delta_SS = calc_prod_metrics(prodTot25['control'], 'Shostarter', bom_cost_control, prodTot24['control'])
                prod_profit_SM, profit_per_unit_SM, prod_profit_last_SM, avg_price_SM, avg_price_last_SM, wholesale_sales_SM, wholesale_percentage_SM, wholesale_delta_SM = calc_prod_metrics(prodTot25['control'], 'Shomaster', bom_cost_control, prodTot24['control'])
    
                tot_cntl_rev25 = prodTot25['control']['The Button'][1] + prodTot25['control']['Shostarter'][1] + prodTot25['control']['Shomaster'][1]
                tot_cntl_prof25 = prod_profit_TB + prod_profit_SS + prod_profit_SM
                if tot_cntl_rev25 == 0:
                    cntl_prof_margin25 = 0
                else:
                    cntl_prof_margin25 = (tot_cntl_prof25 / tot_cntl_rev25) * 100
    
                cola.metric('**Total Revenue**', '${:,}'.format(int(tot_cntl_rev25)))
                colb.metric('**Profit Margin**', '{:,.2f}%'.format(cntl_prof_margin25))
                colc.metric('**Total Profit**', '${:,}'.format(int(tot_cntl_prof25)))
        
                st.divider()
                display_pie_chart_comp(prodTot25['control'])
                st.divider()
                
                prod_select = ui.tabs(options=['The Button', 'Shostarter', 'Shomaster'], default_value='The Button', key='Controllers')
        
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
    
                prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last, wholesale_sales, wholesale_percentage, wholesale_delta = calc_prod_metrics(prodTot25['control'], prod_select, bom_cost_control, prodTot24['control'])

                # Calculate prior year to-date revenue for selected product
                prior_td_revenue = convert_prod_select(prod_select, 2025)

                # Convert prod_select to the td variable for 2024
                prod_td24 = convert_prod_select_profit(prod_select)
                
                col5.metric('**Revenue**', '${:,.2f}'.format(prodTot25['control'][prod_select][1]), percent_of_change(prior_td_revenue, prodTot25['control'][prod_select][1]))
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), percent_of_change(to_date_product_profit(prod_td24, prior_td_revenue, bom_cost_control[prod_select]), prod_profit))
                col6.metric('**Wholesale**', '{:.2f}%'.format(wholesale_percentage))
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), percent_of_change(avg_price_last, avg_price))
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_control[prod_select]), '')
                
                style_metric_cards()
                
                display_month_data_prod(prod_select, control25, control24) 
        
        elif year == 2024:

            total_cntl_rev = prodTot24['control']['The Button'][1] + prodTot24['control']['Shostarter'][1] + prodTot24['control']['Shomaster'][1]
            
            with col2:
                cola, colb, colc = st.columns(3)
                
                cola.subheader('The Button')
                cola.metric('{:.1f}% of Total Revenue'.format((prodTot24['control']['The Button'][1] / total_24) * 100), '{}'.format(int(prodTot24['control']['The Button'][0])), int(prodTot24['control']['The Button'][0] - prodTot23['control']['The Button'][0]))
                colb.subheader('Shostarter')
                colb.metric('{:.1f}% of Total Revenue'.format((prodTot24['control']['Shostarter'][1] / total_24) * 100), '{}'.format(int(prodTot24['control']['Shostarter'][0])), int(prodTot24['control']['Shostarter'][0] - prodTot23['control']['Shostarter'][0]))
                colc.subheader('Shomaster')
                colc.metric('{:.1f}% of Total Revenue'.format((prodTot24['control']['Shomaster'][1] / total_24) * 100), '{}'.format(int(prodTot24['control']['Shomaster'][0])), int(prodTot24['control']['Shomaster'][0] - prodTot23['control']['Shomaster'][0]))
    
                prod_profit_TB, profit_per_unit_TB, prod_profit_last_TB, avg_price_TB, avg_price_last_TB, wholesale_sales_TB, wholesale_percentage_TB, wholesale_delta_TB = calc_prod_metrics(prodTot24['control'], 'The Button', bom_cost_control, prodTot23['control'])
                prod_profit_SS, profit_per_unit_SS, prod_profit_last_SS, avg_price_SS, avg_price_last_SS, wholesale_sales_SS, wholesale_percentage_SS, wholesale_delta_SS = calc_prod_metrics(prodTot24['control'], 'Shostarter', bom_cost_control, prodTot23['control'])
                prod_profit_SM, profit_per_unit_SM, prod_profit_last_SM, avg_price_SM, avg_price_last_SM, wholesale_sales_SM, wholesale_percentage_SM, wholesale_delta_SM = calc_prod_metrics(prodTot24['control'], 'Shomaster', bom_cost_control, prodTot23['control'])
    
                tot_cntl_rev24 = prodTot24['control']['The Button'][1] + prodTot24['control']['Shostarter'][1] + prodTot24['control']['Shomaster'][1]
                tot_cntl_prof24 = prod_profit_TB + prod_profit_SS + prod_profit_SM
                cntl_prof_margin24 = (tot_cntl_prof24 / tot_cntl_rev24) * 100
    
                cola.metric('**Total Revenue**', '${:,}'.format(int(tot_cntl_rev24)))
                colb.metric('**Profit Margin**', '{:,.2f}%'.format(cntl_prof_margin24))
                colc.metric('**Total Profit**', '${:,}'.format(int(tot_cntl_prof24)))
                
                st.divider()
                display_pie_chart_comp(prodTot24['control'])
                st.divider()
                
                prod_select = ui.tabs(options=['The Button', 'Shostarter', 'Shomaster'], default_value='The Button', key='Controllers')
        
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
    
                prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last, wholesale_sales, wholesale_percentage, wholesale_delta = calc_prod_metrics(prodTot24['control'], prod_select, bom_cost_control, prodTot23['control'])

                # Calculate prior year to-date revenue for selected product
                #prior_td_revenue = convert_prod_select(prod_select, 2024)
    
                
                col5.metric('**Revenue**', '${:,.2f}'.format(prodTot24['control'][prod_select][1]), percent_of_change(prodTot23['control'][prod_select][1], prodTot24['control'][prod_select][1]))
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), percent_of_change(prod_profit_last, prod_profit))
                col6.metric('**Wholesale**', '{:.2f}%'.format(wholesale_percentage))
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), percent_of_change(avg_price_last, avg_price))
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_control[prod_select]), '')
    
                style_metric_cards()
                
                display_month_data_prod(prod_select, control24, control23)

        elif year == 2023:

            total_cntl_rev = prodTot23['control']['The Button'][1] + prodTot23['control']['Shostarter'][1] + prodTot23['control']['Shomaster'][1]
            
            with col2:
                cola, colb, colc = st.columns(3)
                
                cola.subheader('The Button')
                cola.metric('{:.1f}% of Total Revenue'.format((prodTot23['control']['The Button'][1] / total_23) * 100), '{}'.format(int(prodTot23['control']['The Button'][0])), '')
                colb.subheader('Shostarter')
                colb.metric('{:.1f}% of Total Revenue'.format((prodTot23['control']['Shostarter'][1] / total_23) * 100), '{}'.format(int(prodTot23['control']['Shostarter'][0])), '')
                colc.subheader('Shomaster')
                colc.metric('{:.1f}% of Total Revenue'.format((prodTot23['control']['Shomaster'][1] / total_23) * 100), '{}'.format(int(prodTot23['control']['Shomaster'][0])), '')
    
                prod_profit_TB, profit_per_unit_TB, prod_profit_last_TB, avg_price_TB, avg_price_last_TB = calc_prod_metrics(prodTot23['control'], 'The Button', bom_cost_control)
                prod_profit_SS, profit_per_unit_SS, prod_profit_last_SS, avg_price_SS, avg_price_last_SS = calc_prod_metrics(prodTot23['control'], 'Shostarter', bom_cost_control)
                prod_profit_SM, profit_per_unit_SM, prod_profit_last_SM, avg_price_SM, avg_price_last_SM = calc_prod_metrics(prodTot23['control'], 'Shomaster', bom_cost_control)
    
                tot_cntl_rev23 = prodTot23['control']['The Button'][1] + prodTot23['control']['Shostarter'][1] + prodTot23['control']['Shomaster'][1]
                tot_cntl_prof23 = prod_profit_TB + prod_profit_SS + prod_profit_SM
                cntl_prof_margin23 = (tot_cntl_prof23 / tot_cntl_rev23) * 100
    
                cola.metric('**Total Revenue**', '${:,}'.format(int(tot_cntl_rev23)))
                colb.metric('**Profit Margin**', '{:,.2f}%'.format(cntl_prof_margin23))
                colc.metric('**Total Profit**', '${:,}'.format(int(tot_cntl_prof23)))
        
                st.divider()
                display_pie_chart_comp(prodTot23['control'])
                st.divider()
                
                prod_select = ui.tabs(options=['The Button', 'Shostarter', 'Shomaster'], default_value='The Button', key='Controllers')
        
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
    
                prod_profit, profit_per_unit, avg_price, wholesale_sales, wholesale_percentage = calc_prod_metrics(prodTot23['control'], prod_select, bom_cost_control)
    
                col5.metric('**Revenue**', '${:,.2f}'.format(prodTot23['control'][prod_select][1]), '')
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), '')
                col6.metric('**Wholesale**', '{:.2f}%'.format(wholesale_percentage))
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), '')
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_control[prod_select]), '')
    
                style_metric_cards()
                
                display_month_data_prod(prod_select, control23)

        elif year == 2022:

            total_cntl = dmx_cntl_annual['2022'] + lcd_cntl_annual['2022'] + tbmk1_annual['2022'] + tbmk2_annual['2022'] + sm_annual['2022'] + pwr_cntl_annual['2022']
            
            with col2:
                cola, colb, colc = st.columns(3)
                
                cola.subheader('Shomaster')
                cola.metric('', '{}'.format(sm_annual['2022']), sm_annual['2022'] - sm_annual['2021'])
                cola.subheader('The Button MK1')
                cola.metric('', '{}'.format(tbmk1_annual['2022']), tbmk1_annual['2022'] - tbmk1_annual['2021'])
                colb.subheader('LCD Controller')
                colb.metric('', '{}'.format(lcd_cntl_annual['2022']), lcd_cntl_annual['2022'] - lcd_cntl_annual['2021'])
                colb.subheader('Total Controllers')
                colb.metric('', '{}'.format(total_cntl), total_cntl - (dmx_cntl_annual['2021'] + lcd_cntl_annual['2021'] + tbmk1_annual['2021'] + tbmk2_annual['2021'] + sm_annual['2021'] + pwr_cntl_annual['2021']))
                colc.subheader('DMX Controller')
                colc.metric('', '{}'.format(dmx_cntl_annual['2022']), dmx_cntl_annual['2022'] - dmx_cntl_annual['2021'])
                colc.subheader('The Button')
                colc.metric('', '{}'.format(tbmk2_annual['2022']), 'N/A')
    
                style_metric_cards()

        elif year == 2021:

            total_cntl = dmx_cntl_annual['2021'] + lcd_cntl_annual['2021'] + tbmk1_annual['2021'] + tbmk2_annual['2021'] + sm_annual['2021'] + pwr_cntl_annual['2021']
            
            with col2:
                cola, colb, colc = st.columns(3)
                
                cola.subheader('Shomaster')
                cola.metric('', '{}'.format(sm_annual['2021']), sm_annual['2021'] - sm_annual['2020'])
                cola.subheader('The Button MK1')
                cola.metric('', '{}'.format(tbmk1_annual['2021']), tbmk1_annual['2021'] - tbmk1_annual['2020'])
                colb.subheader('LCD Controller')
                colb.metric('', '{}'.format(lcd_cntl_annual['2021']), lcd_cntl_annual['2021'] - lcd_cntl_annual['2020'])
                colb.subheader('Total Controllers')
                colb.metric('', '{}'.format(total_cntl), total_cntl - (dmx_cntl_annual['2020'] + lcd_cntl_annual['2020'] + tbmk1_annual['2020'] + tbmk2_annual['2020'] + sm_annual['2020'] + pwr_cntl_annual['2020']))
                colc.subheader('DMX Controller')
                colc.metric('', '{}'.format(dmx_cntl_annual['2021']), dmx_cntl_annual['2021'] - dmx_cntl_annual['2020'])
                colc.subheader('Power Controller')
                colc.metric('', '{}'.format(pwr_cntl_annual['2021']), pwr_cntl_annual['2021'] - pwr_cntl_annual['2020'])
    
                style_metric_cards()

        elif year == 2020:

            total_cntl = dmx_cntl_annual['2020'] + lcd_cntl_annual['2020'] + tbmk1_annual['2020'] + tbmk2_annual['2020'] + sm_annual['2020'] + pwr_cntl_annual['2020']
            
            with col2:
                cola, colb, colc = st.columns(3)
                
                cola.subheader('LCD Controller')
                cola.metric('', '{}'.format(lcd_cntl_annual['2020']), lcd_cntl_annual['2020'] - lcd_cntl_annual['2019'])
                colb.subheader('DMX Controller')
                colb.metric('', '{}'.format(dmx_cntl_annual['2020']), dmx_cntl_annual['2020'] - dmx_cntl_annual['2019'])
                colb.subheader('Total Controllers')
                colb.metric('', '{}'.format(total_cntl), total_cntl - (dmx_cntl_annual['2019'] + lcd_cntl_annual['2019'] + tbmk1_annual['2019'] + tbmk2_annual['2019'] + sm_annual['2019'] + pwr_cntl_annual['2019']))
                colc.subheader('Power Controller')
                colc.metric('', '{}'.format(pwr_cntl_annual['2020']), pwr_cntl_annual['2020'] - pwr_cntl_annual['2019'])
    
                style_metric_cards()

        elif year == 2019:

            total_cntl = dmx_cntl_annual['2019'] + lcd_cntl_annual['2019'] + tbmk1_annual['2019'] + tbmk2_annual['2019'] + sm_annual['2019'] + pwr_cntl_annual['2019']
            
            with col2:
                cola, colb, colc = st.columns(3)

                cola.subheader('LCD Controller')
                cola.metric('', '{}'.format(lcd_cntl_annual['2019']), lcd_cntl_annual['2019'] - lcd_cntl_annual['2018'])
                colb.subheader('DMX Controller')
                colb.metric('', '{}'.format(dmx_cntl_annual['2019']), dmx_cntl_annual['2019'] - dmx_cntl_annual['2018'])
                colb.subheader('Total Controllers')
                colb.metric('', '{}'.format(total_cntl), total_cntl - (dmx_cntl_annual['2018'] + lcd_cntl_annual['2018'] + tbmk1_annual['2018'] + tbmk2_annual['2018'] + sm_annual['2018'] + pwr_cntl_annual['2018']))
                colc.subheader('Power Controller')
                colc.metric('', '{}'.format(pwr_cntl_annual['2019']), pwr_cntl_annual['2019'] - pwr_cntl_annual['2018'])
    
                style_metric_cards()

        elif year == 2018:

            total_cntl = dmx_cntl_annual['2018'] + lcd_cntl_annual['2018'] + tbmk1_annual['2018'] + tbmk2_annual['2018'] + sm_annual['2018'] + pwr_cntl_annual['2018']
            
            with col2:
                cola, colb, colc = st.columns(3)

                cola.subheader('LCD Controller')
                cola.metric('', '{}'.format(lcd_cntl_annual['2018']), lcd_cntl_annual['2018'] - lcd_cntl_annual['2017'])
                colb.subheader('DMX Controller')
                colb.metric('', '{}'.format(dmx_cntl_annual['2018']), dmx_cntl_annual['2018'] - dmx_cntl_annual['2017'])
                colb.subheader('Total Controllers')
                colb.metric('', '{}'.format(total_cntl), total_cntl - (dmx_cntl_annual['2017'] + lcd_cntl_annual['2017'] + tbmk1_annual['2017'] + tbmk2_annual['2017'] + sm_annual['2017'] + pwr_cntl_annual['2017']))
                colc.subheader('Power Controller')
                colc.metric('', '{}'.format(pwr_cntl_annual['2018']), pwr_cntl_annual['2018'] - pwr_cntl_annual['2017'])
    
                style_metric_cards()

        elif year == 2017:

            total_cntl = dmx_cntl_annual['2017'] + lcd_cntl_annual['2017'] + tbmk1_annual['2017'] + tbmk2_annual['2017'] + sm_annual['2017'] + pwr_cntl_annual['2017']
            
            with col2:
                cola, colb, colc = st.columns(3)
            
                cola.subheader('DMX Controller')
                cola.metric('', '{}'.format(dmx_cntl_annual['2017']), dmx_cntl_annual['2017'] - dmx_cntl_annual['2016'])
                colb.subheader('Power Controller')
                colb.metric('', '{}'.format(pwr_cntl_annual['2017']), pwr_cntl_annual['2017'] - pwr_cntl_annual['2016'])
                colc.subheader('Total Controllers')
                colc.metric('', '{}'.format(total_cntl), total_cntl - (dmx_cntl_annual['2016'] + lcd_cntl_annual['2016'] + tbmk1_annual['2016'] + tbmk2_annual['2016'] + sm_annual['2016'] + pwr_cntl_annual['2016']))

                style_metric_cards()

        elif year == 2016:

            with col2:
                cola, colb, colc = st.columns(3)

                colb.subheader('DMX Controller')
                colb.metric('', '{}'.format(dmx_cntl_annual['2016']), dmx_cntl_annual['2016'] - dmx_cntl_annual['2015'])
    
                style_metric_cards()
                
        elif year == 2015:

            with col2:
                cola, colb, colc = st.columns(3)

                colb.subheader('DMX Controller')
                colb.metric('', '{}'.format(dmx_cntl_annual['2015']), '')
    
                style_metric_cards()

        elif year == 'Historical':

            tb_tot_unit = prodTot25['control']['The Button'][0] + prodTot24['control']['The Button'][0] + prodTot23['control']['The Button'][0] + tbmk2_annual['2022']
            tb_tot_rev = prodTot25['control']['The Button'][1] + prodTot24['control']['The Button'][1] + prodTot23['control']['The Button'][1] + (tbmk2_annual['2022'] * 383)

            ss_tot_unit = prodTot25['control']['Shostarter'][0] + prodTot24['control']['Shostarter'][0] + prodTot23['control']['Shostarter'][0]
            ss_tot_rev = prodTot25['control']['Shostarter'][1] + prodTot24['control']['Shostarter'][1] + prodTot23['control']['Shostarter'][1] 

            sm_tot_unit = prodTot25['control']['Shomaster'][0] + prodTot24['control']['Shomaster'][0] + prodTot23['control']['Shomaster'][0] + sm_annual['2022'] + sm_annual['2021']
            sm_tot_rev = prodTot25['control']['Shomaster'][1] + prodTot24['control']['Shomaster'][1] + prodTot23['control']['Shomaster'][1] + (sm_annual['2022'] * 2880) + (sm_annual['2021'] * 2880)

            dmx_cntl_tot_unit = dmx_cntl_annual['2022'] + dmx_cntl_annual['2021'] + dmx_cntl_annual['2020'] + dmx_cntl_annual['2019'] + dmx_cntl_annual['2018'] + dmx_cntl_annual['2017'] + dmx_cntl_annual['2016'] + dmx_cntl_annual['2015']
            dmx_cntl_tot_rev = (dmx_cntl_annual['2022'] * 450) + (dmx_cntl_annual['2021'] * 450) + (dmx_cntl_annual['2020'] * 450) + (dmx_cntl_annual['2019'] * 450) + (dmx_cntl_annual['2018'] * 450) + (dmx_cntl_annual['2017'] * 450) + (dmx_cntl_annual['2016'] * 450) + (dmx_cntl_annual['2015'] * 450)

            lcd_tot_unit = lcd_cntl_annual['2022'] + lcd_cntl_annual['2021'] + lcd_cntl_annual['2020'] + lcd_cntl_annual['2019'] + lcd_cntl_annual['2018']
            lcd_tot_rev = (lcd_cntl_annual['2022'] * 450) + (lcd_cntl_annual['2021'] * 450) + (lcd_cntl_annual['2020'] * 450) + (lcd_cntl_annual['2019'] * 450) + (lcd_cntl_annual['2018'] * 450)

            pwr_cntl_tot_unit = pwr_cntl_annual['2021'] + pwr_cntl_annual['2020'] + pwr_cntl_annual['2019'] + pwr_cntl_annual['2018'] + pwr_cntl_annual['2017']
            pwr_cntl_tot_rev = (pwr_cntl_annual['2021'] * 260) + (pwr_cntl_annual['2020'] * 260) + (pwr_cntl_annual['2019'] * 260) + (pwr_cntl_annual['2018'] * 260) + (pwr_cntl_annual['2017'] * 260)
            
            tbmk1_tot_unit = tbmk1_annual['2022'] + tbmk1_annual['2021']
            tbmk1_tot_rev = (tbmk1_annual['2022'] * 360) + (tbmk1_annual['2021'] * 360) 


            cola, colb, colc, cold, cole = st.columns(5)

            colb.subheader('The Button')
            colb.metric('**${:,.2f}**'.format(tb_tot_rev), '{}'.format(int(tb_tot_unit)))
            colb.subheader('The Button MKI')
            colb.metric('**${:,.2f}**'.format(tbmk1_tot_rev), '{}'.format(tbmk1_tot_unit))
            colb.subheader('Power Controller')
            colb.metric('**${:,.2f}**'.format(pwr_cntl_tot_rev), '{}'.format(pwr_cntl_tot_unit))

            colc.subheader('Shostarter')
            colc.metric('**${:,.2f}**'.format(ss_tot_rev), '{}'.format(int(ss_tot_unit)))
            colc.subheader('LCD Controller')
            colc.metric('**${:,.2f}**'.format(lcd_tot_rev), '{}'.format(lcd_tot_unit))

            cold.subheader('Shomaster')
            cold.metric('**${:,.2f}**'.format(sm_tot_rev), '{}'.format(int(sm_tot_unit)))
            cold.subheader('DMX Controller')
            cold.metric('**${:,.2f}**'.format(dmx_cntl_tot_rev), '{}'.format(dmx_cntl_tot_unit))
            cold.subheader('Total Controllers')
            cold.metric('**${:,.2f}**'.format(tbmk1_tot_rev + pwr_cntl_tot_rev + lcd_tot_rev + dmx_cntl_tot_rev + sm_tot_rev + ss_tot_rev + tb_tot_rev), '{}'.format(int(tbmk1_tot_unit + pwr_cntl_tot_unit + lcd_tot_unit + dmx_cntl_tot_unit + sm_tot_unit + ss_tot_unit + tb_tot_unit)))

            style_metric_cards()

            cntl_annual_dict = {'2025': 0, '2024': 0, '2023': 0, '2022': 0, '2021': 0, '2020': 0, '2019': 0, '2018': 0, '2017': 0, '2016': 0, '2015': 0, '2014': 0}
            cntl_annual_dict_seg = {'2025': {'The Button': prodTot25['control']['The Button'][0], 'Shostarter': prodTot25['control']['Shostarter'][0], 'Shomaster': prodTot25['control']['Shomaster'][0]}, '2024': {'The Button': prodTot24['control']['The Button'][0], 'Shostarter': prodTot24['control']['Shostarter'][0], 'Shomaster': prodTot24['control']['Shomaster'][0]}, '2023': {'The Button': prodTot23['control']['The Button'][0], 'Shostarter': prodTot23['control']['Shostarter'][0], 'Shomaster': prodTot23['control']['Shomaster'][0]}, '2022': {'The Button': tbmk2_annual['2022'], 'The Button MKI': tbmk1_annual['2022'], 'Shomaster': sm_annual['2022'], 'LCD Controller': lcd_cntl_annual['2022'], 'DMX Controller': dmx_cntl_annual['2022']}, '2021': {'Power Controller': pwr_cntl_annual['2021'], 'The Button MKI': tbmk1_annual['2021'], 'Shomaster': sm_annual['2021'], 'LCD Controller': lcd_cntl_annual['2021'], 'DMX Controller': dmx_cntl_annual['2021']}, '2020': {'Power Controller': pwr_cntl_annual['2020'], 'LCD Controller': lcd_cntl_annual['2020'], 'DMX Controller': dmx_cntl_annual['2020']}, '2019': {'Power Controller': pwr_cntl_annual['2019'], 'LCD Controller': lcd_cntl_annual['2019'], 'DMX Controller': dmx_cntl_annual['2019']}, '2018': {'Power Controller': pwr_cntl_annual['2018'], 'LCD Controller': lcd_cntl_annual['2018'], 'DMX Controller': dmx_cntl_annual['2018']}, '2017': {'Power Controller': pwr_cntl_annual['2017'], 'DMX Controller': dmx_cntl_annual['2017']}, '2016': {'DMX Controller': dmx_cntl_annual['2016']}, '2015': {'DMX Controller': dmx_cntl_annual['2015']}}
            cntl_annual_dict['2025'] += prodTot25['control']['The Button'][0] + prodTot25['control']['Shostarter'][0] + prodTot25['control']['Shomaster'][0] 
            cntl_annual_dict['2024'] += prodTot24['control']['The Button'][0] + prodTot24['control']['Shostarter'][0] + prodTot24['control']['Shomaster'][0]
            cntl_annual_dict['2023'] += prodTot23['control']['The Button'][0] + prodTot23['control']['Shostarter'][0] + prodTot23['control']['Shomaster'][0]

            cntl_list = [tbmk1_annual, pwr_cntl_annual, lcd_cntl_annual, dmx_cntl_annual, tbmk2_annual, sm_annual]
            year_list = ['2022', '2021', '2020', '2019', '2018', '2017', '2016', '2015', '2014']
            
            colx, coly, colz = st.columns([.2, .6, .2])
            with coly:
                plot_bar_chart_product_seg(format_for_chart_product_seg(cntl_annual_dict_seg, 'Total Controller Sales'), 'Total Controller Sales')
            

    elif prod_cat == 'Handhelds':

        td_8nc23, td_8nc24, td_8nc25 = to_date_product('CC-HCCMKII-08-NC')
        td_8tc23, td_8tc24, td_8tc25 = to_date_product('CC-HCCMKII-08-TC')
        td_15nc23, td_15nc24, td_15nc25 = to_date_product('CC-HCCMKII-15-NC')
        td_15tc23, td_15tc24, td_15tc25 = to_date_product('CC-HCCMKII-15-TC')

        with col2:
            year = ui.tabs(options=[2026, 2025, 2024, 2023, 'Historical'], default_value=2026, key='Handheld Year Select')

        if year == 2026:

            total_hh_rev = prodTot26['handheld']['8FT - No Case'][1] + prodTot26['handheld']['8FT - Travel Case'][1] + prodTot26['handheld']['15FT - No Case'][1] + prodTot26['handheld']['15FT - Travel Case'][1]
            
            with col2:
                cola, colb, colc, cold = st.columns(4)
        
                cola.subheader('8FT NC')
                cola.metric('{:.1f}% of Total Revenue'.format((prodTot26['handheld']['8FT - No Case'][1] / td_26_tot) * 100), '{}'.format(int(prodTot26['handheld']['8FT - No Case'][0])), '{}'.format(int(prodTot26['handheld']['8FT - No Case'][0] - td_8nc25)))
                cola.metric('', '${:,}'.format(int(prodTot26['handheld']['8FT - No Case'][1])), percent_of_change(convert_prod_select('8FT - No Case', 2026), prodTot26['handheld']['8FT - No Case'][1]))
                colb.subheader('8FT TC')
                colb.metric('{:.1f}% of Total Revenue'.format((prodTot26['handheld']['8FT - Travel Case'][1] / td_26_tot) * 100), '{}'.format(int(prodTot26['handheld']['8FT - Travel Case'][0])),  '{}'.format(int(prodTot26['handheld']['8FT - Travel Case'][0] - td_8tc25)))
                colb.metric('', '${:,}'.format(int(prodTot26['handheld']['8FT - Travel Case'][1])), percent_of_change(convert_prod_select('8FT - Travel Case', 2026), prodTot26['handheld']['8FT - Travel Case'][1]))
                colc.subheader('15FT NC')
                colc.metric('{:.1f}% of Total Revenue'.format((prodTot26['handheld']['15FT - No Case'][1] / td_26_tot) * 100), '{}'.format(int(prodTot26['handheld']['15FT - No Case'][0])),  '{}'.format(int(prodTot26['handheld']['15FT - No Case'][0] - td_15nc25)))
                colc.metric('', '${:,}'.format(int(prodTot26['handheld']['15FT - No Case'][1])), percent_of_change(convert_prod_select('15FT - No Case', 2026), prodTot26['handheld']['15FT - No Case'][1]))
                cold.subheader('15FT TC')
                cold.metric('{:.1f}% of Total Revenue'.format((prodTot26['handheld']['15FT - Travel Case'][1] / td_26_tot) * 100), '{}'.format(int(prodTot26['handheld']['15FT - Travel Case'][0])),  '{}'.format(int(prodTot26['handheld']['15FT - Travel Case'][0] - td_15tc25)))
                cold.metric('', '${:,}'.format(int(prodTot26['handheld']['15FT - Travel Case'][1])), percent_of_change(convert_prod_select('15FT - Travel Case', 2026), prodTot26['handheld']['15FT - Travel Case'][1]))
    
    
                prod_profit_8NC, profit_per_unit_8NC, prod_profit_last_8NC, avg_price_8NC, avg_price_last_8NC = calc_prod_metrics(prodTot26['handheld'], '8FT - No Case', bom_cost_hh, prodTot25['handheld'])
                prod_profit_8TC, profit_per_unit_8TC, prod_profit_last_8TC, avg_price_8TC, avg_price_last_8TC = calc_prod_metrics(prodTot26['handheld'], '8FT - Travel Case', bom_cost_hh, prodTot25['handheld'])
                prod_profit_15NC, profit_per_unit_15NC, prod_profit_last_15NC, avg_price_15NC, avg_price_last_15NC = calc_prod_metrics(prodTot26['handheld'], '15FT - No Case', bom_cost_hh, prodTot25['handheld'])
                prod_profit_15TC, profit_per_unit_15TC, prod_profit_last_15TC, avg_price_15TC, avg_price_last_15TC = calc_prod_metrics(prodTot26['handheld'], '15FT - Travel Case', bom_cost_hh, prodTot25['handheld'])
                
                tot_hh_rev26 = prodTot26['handheld']['8FT - No Case'][1] + prodTot26['handheld']['8FT - Travel Case'][1] + prodTot26['handheld']['15FT - No Case'][1] + prodTot26['handheld']['15FT - Travel Case'][1]
                tot_hh_prof26 = prod_profit_8NC + prod_profit_8TC + prod_profit_15NC + prod_profit_15TC

                if tot_hh_rev26 == 0:
                    prof_margin26 = 0
                else:
                    prof_margin26 = (tot_hh_prof26 / tot_hh_rev26) * 100
                
                colx, coly, colz = st.columns(3)
    
                colx.metric('**Total Revenue**', '${:,}'.format(int(tot_hh_rev26)))
                coly.metric('**Profit Margin**', '{:,.2f}%'.format(prof_margin26))
                colz.metric('**Total Profit**', '${:,}'.format(int(tot_hh_prof26)))
            
                st.divider()
                display_pie_chart_comp(prodTot26['handheld'])
                st.divider()
        
                prod_select = ui.tabs(options=['8FT - No Case', '8FT - Travel Case', '15FT - No Case', '15FT - Travel Case'], default_value='8FT - No Case', key='Handhelds')
        
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
    
                prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last = calc_prod_metrics(prodTot26['handheld'], prod_select, bom_cost_hh, prodTot25['handheld'])

                # Calculate prior year to-date revenue for selected product
                prior_td_revenue = convert_prod_select(prod_select, 2026)

                # Convert prod_select to the td variable for 2024
                prod_td25 = convert_prod_select_profit(prod_select)
                
                
                col5.metric('**Revenue**', '${:,.2f}'.format(int(prodTot26['handheld'][prod_select][1])), percent_of_change(prior_td_revenue, prodTot26['handheld'][prod_select][1]))
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), percent_of_change(to_date_product_profit(prod_td25, prior_td_revenue, bom_cost_hh[prod_select]), prod_profit))
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), percent_of_change(avg_price_last, avg_price))
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_hh[prod_select]), '')        
    
                style_metric_cards()
                
                display_month_data_prod(prod_select, handheld26, handheld25)
        
            
        elif year == 2025:

            total_hh_rev = prodTot25['handheld']['8FT - No Case'][1] + prodTot25['handheld']['8FT - Travel Case'][1] + prodTot25['handheld']['15FT - No Case'][1] + prodTot25['handheld']['15FT - Travel Case'][1]
            
            with col2:
                cola, colb, colc, cold = st.columns(4)
        
                cola.subheader('8FT NC')
                cola.metric('{:.1f}% of Total Revenue'.format((prodTot25['handheld']['8FT - No Case'][1] / td_25_tot) * 100), '{}'.format(int(prodTot25['handheld']['8FT - No Case'][0])), '{}'.format(int(prodTot25['handheld']['8FT - No Case'][0] - prodTot24['handheld']['8FT - No Case'][0])))
                cola.metric('', '${:,}'.format(int(prodTot25['handheld']['8FT - No Case'][1])), percent_of_change(convert_prod_select('8FT - No Case', 2025), prodTot25['handheld']['8FT - No Case'][1]))
                colb.subheader('8FT TC')
                colb.metric('{:.1f}% of Total Revenue'.format((prodTot25['handheld']['8FT - Travel Case'][1] / td_25_tot) * 100), '{}'.format(int(prodTot25['handheld']['8FT - Travel Case'][0])),  '{}'.format(int(prodTot25['handheld']['8FT - Travel Case'][0] - prodTot24['handheld']['8FT - Travel Case'][0])))
                colb.metric('', '${:,}'.format(int(prodTot25['handheld']['8FT - Travel Case'][1])), percent_of_change(convert_prod_select('8FT - Travel Case', 2025), prodTot25['handheld']['8FT - Travel Case'][1]))
                colc.subheader('15FT NC')
                colc.metric('{:.1f}% of Total Revenue'.format((prodTot25['handheld']['15FT - No Case'][1] / td_25_tot) * 100), '{}'.format(int(prodTot25['handheld']['15FT - No Case'][0])),  '{}'.format(int(prodTot25['handheld']['15FT - No Case'][0] - prodTot24['handheld']['15FT - No Case'][0])))
                colc.metric('', '${:,}'.format(int(prodTot25['handheld']['15FT - No Case'][1])), percent_of_change(convert_prod_select('15FT - No Case', 2025), prodTot25['handheld']['15FT - No Case'][1]))
                cold.subheader('15FT TC')
                cold.metric('{:.1f}% of Total Revenue'.format((prodTot25['handheld']['15FT - Travel Case'][1] / td_25_tot) * 100), '{}'.format(int(prodTot25['handheld']['15FT - Travel Case'][0])),  '{}'.format(int(prodTot25['handheld']['15FT - Travel Case'][0] - prodTot24['handheld']['15FT - Travel Case'][0])))
                cold.metric('', '${:,}'.format(int(prodTot25['handheld']['15FT - Travel Case'][1])), percent_of_change(convert_prod_select('15FT - Travel Case', 2025), prodTot25['handheld']['15FT - Travel Case'][1]))
    
    
                prod_profit_8NC, profit_per_unit_8NC, prod_profit_last_8NC, avg_price_8NC, avg_price_last_8NC = calc_prod_metrics(prodTot25['handheld'], '8FT - No Case', bom_cost_hh, prodTot24['handheld'])
                prod_profit_8TC, profit_per_unit_8TC, prod_profit_last_8TC, avg_price_8TC, avg_price_last_8TC = calc_prod_metrics(prodTot25['handheld'], '8FT - Travel Case', bom_cost_hh, prodTot24['handheld'])
                prod_profit_15NC, profit_per_unit_15NC, prod_profit_last_15NC, avg_price_15NC, avg_price_last_15NC = calc_prod_metrics(prodTot25['handheld'], '15FT - No Case', bom_cost_hh, prodTot24['handheld'])
                prod_profit_15TC, profit_per_unit_15TC, prod_profit_last_15TC, avg_price_15TC, avg_price_last_15TC = calc_prod_metrics(prodTot25['handheld'], '15FT - Travel Case', bom_cost_hh, prodTot24['handheld'])
                
                tot_hh_rev25 = prodTot25['handheld']['8FT - No Case'][1] + prodTot25['handheld']['8FT - Travel Case'][1] + prodTot25['handheld']['15FT - No Case'][1] + prodTot25['handheld']['15FT - Travel Case'][1]
                tot_hh_prof25 = prod_profit_8NC + prod_profit_8TC + prod_profit_15NC + prod_profit_15TC
                prof_margin25 = (tot_hh_prof25 / tot_hh_rev25) * 100
                
                colx, coly, colz = st.columns(3)
    
                colx.metric('**Total Revenue**', '${:,}'.format(int(tot_hh_rev25)))
                coly.metric('**Profit Margin**', '{:,.2f}%'.format(prof_margin25))
                colz.metric('**Total Profit**', '${:,}'.format(int(tot_hh_prof25)))
            
                st.divider()
                display_pie_chart_comp(prodTot25['handheld'])
                st.divider()
        
                prod_select = ui.tabs(options=['8FT - No Case', '8FT - Travel Case', '15FT - No Case', '15FT - Travel Case'], default_value='8FT - No Case', key='Handhelds')
        
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
    
                prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last = calc_prod_metrics(prodTot25['handheld'], prod_select, bom_cost_hh, prodTot24['handheld'])

                # Calculate prior year to-date revenue for selected product
                prior_td_revenue = convert_prod_select(prod_select, 2025)

                # Convert prod_select to the td variable for 2024
                prod_td24 = convert_prod_select_profit(prod_select)
                
                
                col5.metric('**Revenue**', '${:,.2f}'.format(int(prodTot25['handheld'][prod_select][1])), percent_of_change(prior_td_revenue, prodTot25['handheld'][prod_select][1]))
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), percent_of_change(to_date_product_profit(prod_td24, prior_td_revenue, bom_cost_hh[prod_select]), prod_profit))
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), percent_of_change(avg_price_last, avg_price))
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_hh[prod_select]), '')        
    
                style_metric_cards()
                
                display_month_data_prod(prod_select, handheld25, handheld24)
        
        elif year == 2024:

            total_hh_rev = prodTot24['handheld']['8FT - No Case'][1] + prodTot24['handheld']['8FT - Travel Case'][1] + prodTot24['handheld']['15FT - No Case'][1] + prodTot24['handheld']['15FT - Travel Case'][1]
            
            with col2:
                
                cola, colb, colc, cold = st.columns(4)
        
                cola.subheader('8FT NC')
                cola.metric('{:.1f}% of Total Revenue'.format((prodTot24['handheld']['8FT - No Case'][1] / total_24) * 100), '{}'.format(int(prodTot24['handheld']['8FT - No Case'][0])), '{}'.format(int(prodTot24['handheld']['8FT - No Case'][0] - prodTot23['handheld']['8FT - No Case'][0])))
                cola.metric('', '${:,}'.format(int(prodTot24['handheld']['8FT - No Case'][1])), percent_of_change(prodTot23['handheld']['8FT - No Case'][1], prodTot24['handheld']['8FT - No Case'][1]))
                colb.subheader('8FT TC')
                colb.metric('{:.1f}% of Total Revenue'.format((prodTot24['handheld']['8FT - Travel Case'][1] / total_24) * 100), '{}'.format(int(prodTot24['handheld']['8FT - Travel Case'][0])),  '{}'.format(int(prodTot24['handheld']['8FT - Travel Case'][0] - prodTot23['handheld']['8FT - Travel Case'][0])))
                colb.metric('', '${:,}'.format(int(prodTot24['handheld']['8FT - Travel Case'][1])), percent_of_change(prodTot23['handheld']['8FT - Travel Case'][1], prodTot24['handheld']['8FT - Travel Case'][1]))
                colc.subheader('15FT NC')
                colc.metric('{:.1f}% of Total Revenue'.format((prodTot24['handheld']['15FT - No Case'][1] / total_24) * 100), '{}'.format(int(prodTot24['handheld']['15FT - No Case'][0])),  '{}'.format(int(prodTot24['handheld']['15FT - No Case'][0] - prodTot23['handheld']['15FT - No Case'][0])))
                colc.metric('', '${:,}'.format(int(prodTot24['handheld']['15FT - No Case'][1])), percent_of_change(prodTot23['handheld']['15FT - No Case'][1], prodTot24['handheld']['15FT - No Case'][1]))
                cold.subheader('15FT TC')
                cold.metric('{:.1f}% of Total Revenue'.format((prodTot24['handheld']['15FT - Travel Case'][1] / total_24) * 100), '{}'.format(int(prodTot24['handheld']['15FT - Travel Case'][0])),  '{}'.format(int(prodTot24['handheld']['15FT - Travel Case'][0] - prodTot23['handheld']['15FT - Travel Case'][0])))
                cold.metric('', '${:,}'.format(int(prodTot24['handheld']['15FT - Travel Case'][1])), percent_of_change(prodTot23['handheld']['15FT - Travel Case'][1], prodTot24['handheld']['15FT - Travel Case'][1]))
    
    
                prod_profit_8NC, profit_per_unit_8NC, prod_profit_last_8NC, avg_price_8NC, avg_price_last_8NC = calc_prod_metrics(prodTot24['handheld'], '8FT - No Case', bom_cost_hh, prodTot23['handheld'])
                prod_profit_8TC, profit_per_unit_8TC, prod_profit_last_8TC, avg_price_8TC, avg_price_last_8TC = calc_prod_metrics(prodTot24['handheld'], '8FT - Travel Case', bom_cost_hh, prodTot23['handheld'])
                prod_profit_15NC, profit_per_unit_15NC, prod_profit_last_15NC, avg_price_15NC, avg_price_last_15NC = calc_prod_metrics(prodTot24['handheld'], '15FT - No Case', bom_cost_hh, prodTot23['handheld'])
                prod_profit_15TC, profit_per_unit_15TC, prod_profit_last_15TC, avg_price_15TC, avg_price_last_15TC = calc_prod_metrics(prodTot24['handheld'], '15FT - Travel Case', bom_cost_hh, prodTot23['handheld'])
                
                tot_hh_rev24 = prodTot24['handheld']['8FT - No Case'][1] + prodTot24['handheld']['8FT - Travel Case'][1] + prodTot24['handheld']['15FT - No Case'][1] + prodTot24['handheld']['15FT - Travel Case'][1]
                tot_hh_prof24 = prod_profit_8NC + prod_profit_8TC + prod_profit_15NC + prod_profit_15TC
                prof_margin24 = (tot_hh_prof24 / tot_hh_rev24) * 100
                
                colx, coly, colz = st.columns(3)
    
                colx.metric('**Total Revenue**', '${:,}'.format(int(tot_hh_rev24)))
                coly.metric('**Profit Margin**', '{:,.2f}%'.format(prof_margin24))
                colz.metric('**Total Profit**', '${:,}'.format(int(tot_hh_prof24)))
            
                st.divider()
                display_pie_chart_comp(prodTot24['handheld'])
                st.divider()
        
                prod_select = ui.tabs(options=['8FT - No Case', '8FT - Travel Case', '15FT - No Case', '15FT - Travel Case'], default_value='8FT - No Case', key='Handhelds')
        
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
    
                prod_profit, profit_per_unit, prod_profit_last, avg_price, avg_price_last = calc_prod_metrics(prodTot24['handheld'], prod_select, bom_cost_hh, prodTot23['handheld'])

                # Calculate prior year to-date revenue for selected product
                #prior_td_revenue = convert_prod_select(prod_select, 2024)
                
                
                col5.metric('**Revenue**', '${:,.2f}'.format(int(prodTot24['handheld'][prod_select][1])), percent_of_change(prodTot23['handheld'][prod_select][1], prodTot24['handheld'][prod_select][1]))
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), percent_of_change(prod_profit_last, prod_profit))
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), percent_of_change(avg_price_last, avg_price))
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_hh[prod_select]), '')        
    
                style_metric_cards()
                
                display_month_data_prod(prod_select, handheld24, handheld23)
            
        elif year == 2023:

            total_hh_rev = prodTot23['handheld']['8FT - No Case'][1] + prodTot23['handheld']['8FT - Travel Case'][1] + prodTot23['handheld']['15FT - No Case'][1] + prodTot23['handheld']['15FT - Travel Case'][1]
            
            with col2:
                
                cola, colb, colc, cold = st.columns(4)
        
                cola.subheader('8FT NC')
                cola.metric('{:.1f}% of Total Revenue'.format((prodTot23['handheld']['8FT - No Case'][1] / total_23) * 100), '{}'.format(int(prodTot23['handheld']['8FT - No Case'][0]), ''))
                cola.metric('', '${:,}'.format(int(prodTot23['handheld']['8FT - No Case'][1])), '')
                colb.subheader('8FT TC')
                colb.metric('{:.1f}% of Total Revenue'.format((prodTot23['handheld']['8FT - Travel Case'][1] / total_23) * 100), '{}'.format(int(prodTot23['handheld']['8FT - Travel Case'][0]),  ''))
                colb.metric('', '${:,}'.format(int(prodTot23['handheld']['8FT - Travel Case'][1])), '')
                colc.subheader('15FT NC')
                colc.metric('{:.1f}% of Total Revenue'.format((prodTot23['handheld']['15FT - No Case'][1] / total_23) * 100), '{}'.format(int(prodTot23['handheld']['15FT - No Case'][0]),  ''))
                colc.metric('', '${:,}'.format(int(prodTot23['handheld']['15FT - No Case'][1])), '')
                cold.subheader('15FT TC')
                cold.metric('{:.1f}% of Total Revenue'.format((prodTot23['handheld']['15FT - Travel Case'][1] / total_23) * 100), '{}'.format(int(prodTot23['handheld']['15FT - Travel Case'][0]),  ''))
                cold.metric('', '${:,}'.format(int(prodTot23['handheld']['15FT - Travel Case'][1])), '')
    
    
                prod_profit_8NC, profit_per_unit_8NC, avg_price_8NC = calc_prod_metrics(prodTot23['handheld'], '8FT - No Case', bom_cost_hh)
                prod_profit_8TC, profit_per_unit_8TC, avg_price_8TC = calc_prod_metrics(prodTot23['handheld'], '8FT - Travel Case', bom_cost_hh)
                prod_profit_15NC, profit_per_unit_15NC, avg_price_15NC = calc_prod_metrics(prodTot23['handheld'], '15FT - No Case', bom_cost_hh)
                prod_profit_15TC, profit_per_unit_15TC, avg_price_15TC = calc_prod_metrics(prodTot23['handheld'], '15FT - Travel Case', bom_cost_hh)
                
                tot_hh_rev23 = prodTot23['handheld']['8FT - No Case'][1] + prodTot23['handheld']['8FT - Travel Case'][1] + prodTot23['handheld']['15FT - No Case'][1] + prodTot23['handheld']['15FT - Travel Case'][1]
                tot_hh_prof23 = prod_profit_8NC + prod_profit_8TC + prod_profit_15NC + prod_profit_15TC
                prof_margin23 = (tot_hh_prof23 / tot_hh_rev23) * 100
                
                colx, coly, colz = st.columns(3)
    
                colx.metric('**Total Revenue**', '${:,}'.format(int(tot_hh_rev23)))
                coly.metric('**Profit Margin**', '{:,.2f}%'.format(prof_margin23))
                colz.metric('**Total Profit**', '${:,}'.format(int(tot_hh_prof23)))   
    
                st.divider()
                display_pie_chart_comp(prodTot23['handheld'])
                st.divider()
        
                prod_select = ui.tabs(options=['8FT - No Case', '8FT - Travel Case', '15FT - No Case', '15FT - Travel Case'], default_value='8FT - No Case', key='Handhelds')
        
                ### DISPLAY PRODUCT DETAILS 
                col5, col6, col7 = st.columns(3)
        
                prod_profit = (prodTot23['handheld'][prod_select][1]) - (prodTot23['handheld'][prod_select][0] * bom_cost_hh[prod_select])
                avg_price = prodTot23['handheld'][prod_select][1] / prodTot23['handheld'][prod_select][0]
                profit_per_unit = avg_price - bom_cost_hh[prod_select]
                
                col5.metric('**Revenue**', '${:,.2f}'.format(prodTot23['handheld'][prod_select][1]), '')
                col5.metric('**Profit per Unit**', '${:,.2f}'.format(profit_per_unit), '')
                col6.metric('**Profit**', '${:,.2f}'.format(prod_profit), '')
                col7.metric('**Avg Price**', '${:,.2f}'.format(avg_price), '')
                col7.metric('**BOM Cost**', '${:,.2f}'.format(bom_cost_hh[prod_select]), '')        
                
                style_metric_cards()
                
                display_month_data_prod(prod_select, handheld23)

        elif year == 'Historical':

            mk1_tot = 0
            mk2_tot = prodTot25['handheld']['8FT - No Case'][0] + prodTot25['handheld']['8FT - Travel Case'][0] + prodTot25['handheld']['15FT - No Case'][0] + prodTot25['handheld']['15FT - Travel Case'][0] + prodTot24['handheld']['8FT - No Case'][0] + prodTot24['handheld']['8FT - Travel Case'][0] + prodTot24['handheld']['15FT - No Case'][0] + prodTot24['handheld']['15FT - Travel Case'][0] + prodTot23['handheld']['8FT - No Case'][0] + prodTot23['handheld']['8FT - Travel Case'][0] + prodTot23['handheld']['15FT - No Case'][0] + prodTot23['handheld']['15FT - Travel Case'][0]

            for key, val in hhmk1_annual.items():
                mk1_tot += val
            for key, val in hhmk2_annual.items():
                mk2_tot += val

            with col2:
                
                cola, colb, colc = st.columns(3)
        
                cola.metric('**2022**', '{}'.format(hhmk1_annual['2022'] + hhmk2_annual['2022']), (hhmk1_annual['2022'] + hhmk2_annual['2022']) - (hhmk1_annual['2021'] + hhmk2_annual['2021']))
                cola.metric('**2019**', '{}'.format(hhmk1_annual['2019'] + hhmk2_annual['2019']), (hhmk1_annual['2019'] + hhmk2_annual['2019']) - hhmk1_annual['2018'])
                cola.metric('**2016**', '{}'.format(hhmk1_annual['2016']), hhmk1_annual['2016'] - hhmk1_annual['2015'])
                cola.metric('**Total MKII**', '{}'.format(int(mk2_tot)), '')
     
                colb.metric('**2021**', '{}'.format(hhmk1_annual['2021'] + hhmk2_annual['2021']),  (hhmk1_annual['2021'] + hhmk2_annual['2021']) - (hhmk1_annual['2020'] + hhmk2_annual['2020']))
                colb.metric('**2018**', '{}'.format(hhmk1_annual['2018']), hhmk1_annual['2018'] - hhmk1_annual['2017'])
                colb.metric('**2015**', '{}'.format(hhmk1_annual['2015']), hhmk1_annual['2015'] - hhmk1_annual['2014'])
                colb.metric('**2013**', '{}'.format(hhmk1_annual['2013']), '')
                colb.metric('**Total Handhelds Sold**', '{}'.format(int(mk1_tot + mk2_tot)), '')
                
                colc.metric('**2020**', '{}'.format(hhmk1_annual['2020'] + hhmk2_annual['2020']),  (hhmk1_annual['2020'] + hhmk2_annual['2020']) - (hhmk1_annual['2019'] + hhmk2_annual['2019']))
                colc.metric('**2017**', '{}'.format(hhmk1_annual['2017']), hhmk1_annual['2017'] - hhmk1_annual['2016'])
                colc.metric('**2014**', '{}'.format(hhmk1_annual['2014']), hhmk1_annual['2014'] - hhmk1_annual['2013'])
                colc.metric('**Total MKI**', '{}'.format(mk1_tot), '')

                style_metric_cards()

                hh_dict = {}
                
                hh_dict['2025'] = prodTot25['handheld']['8FT - No Case'][0] + prodTot25['handheld']['8FT - Travel Case'][0] + prodTot25['handheld']['15FT - No Case'][0] + prodTot25['handheld']['15FT - Travel Case'][0]
                hh_dict['2024'] = prodTot24['handheld']['8FT - No Case'][0] + prodTot24['handheld']['8FT - Travel Case'][0] + prodTot24['handheld']['15FT - No Case'][0] + prodTot24['handheld']['15FT - Travel Case'][0]
                hh_dict['2023'] = prodTot23['handheld']['8FT - No Case'][0] + prodTot23['handheld']['8FT - Travel Case'][0] + prodTot23['handheld']['15FT - No Case'][0] + prodTot23['handheld']['15FT - Travel Case'][0]
                
                for year, sales in hhmk1_annual.items():
                    hh_dict[year] = sales

                for year, sales in hhmk2_annual.items():
                    hh_dict[year] += sales


                hh_dict = {key: hh_dict[key] for key in reversed(hh_dict)}

                plot_bar_chart_hh(format_for_chart_hh(hh_dict))

        
    elif prod_cat == 'Hoses':

        with col2:
            hose_scope = ui.tabs(options=['Overview', 'Profit'], default_value='Overview', key='Hose Metric Scope')

        if hose_scope == 'Overview':
            cola, colb, colc = st.columns([.2, .6, .2])
            with colb:
                display_hose_data(hose_detail26, hose_detail25, hose_detail24, hose_detail23)
                
        if hose_scope == 'Profit':
            
            cola, colb, colc = st.columns([.2, .6, .2])
            with colb:
                display_hose_data_profit(hose_detail26, hose_detail25, hose_detail24, hose_detail23, product_ctx, bom_cost_hose)
          
    elif prod_cat == 'Accessories':

        with col2:
            acc_scope = ui.tabs(options=['Overview', 'Profit'], default_value='Overview', key='Acc Metric Scope')

        cola, colb, colc, cold, cole, colf, colg, colh = st.columns([.1,.1,.2,.2,.2,.2,.1,.1])
        
        colc.subheader('2026')
        cold.subheader('2025')
        cole.subheader('2024')
        colf.subheader('2023')

        if acc_scope == 'Overview':

            display_acc_data(product_ctx)

        if acc_scope == 'Profit':

            display_acc_data_profit(product_ctx, bom_cost_acc)


    elif prod_cat == 'MagicFX':
        
        with col2:
            year = ui.tabs(options=[2026, 2025, 2024, 2023], default_value=2026, key='Products Year Select')

        cola, colx, coly, colz, colb = st.columns([.15, .23, .23, .23, .15], gap='medium')

        if year == 2026:

            idx = 0
            
            count, magic_dict = magic_sales('2026')

            group1 = [1, 4, 7, 10]
            group2 = [2, 5, 8, 11]
            group3 = [3, 6, 9, 12]
            
            for key, val in magic_dict.items():
                if val[0] >= 1 and key != 'MFX-ECO2JET-BKT':
                    if idx in group1:
                        colx.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))
                    elif idx in group2:
                        coly.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))    
                    else:
                        colz.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))

                    idx += 1

        if year == 2025:

            idx = 0
            
            count, magic_dict = magic_sales('2025')

            group1 = [1, 4, 7, 10]
            group2 = [2, 5, 8, 11]
            group3 = [3, 6, 9, 12]
            
            for key, val in magic_dict.items():
                if val[0] >= 1 and key != 'MFX-ECO2JET-BKT':
                    if idx in group1:
                        colx.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))
                    elif idx in group2:
                        coly.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))    
                    else:
                        colz.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))

                    idx += 1
            
        if year == 2024:

            idx = 0
            
            count, magic_dict = magic_sales('2024')

            
            for key, val in magic_dict.items():
                if val[0] >= 1:
                    if 0 <= idx <= 5:
                        colx.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))
                    elif 5 < idx <= 10:
                        coly.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))    
                    else:
                        colz.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))

                    idx += 1

        if year == 2023:

            idx = 0
            
            count, magic_dict = magic_sales('2023')
            for key, val in magic_dict.items():
                if val[0] >= 1:
                    if 0 <= idx <= 5:
                        colx.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))
                    elif 5 < idx <= 10:
                        coly.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))    
                    else:
                        colz.metric('**{}**'.format(key), '{}'.format(int(val[0])), '${:,.2f} in revenue'.format(val[1]))

                    idx += 1
            
        style_metric_cards()
