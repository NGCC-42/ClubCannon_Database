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


# ----------------------------------------------------------
# HELPER FUNCTION TO CREATE DATAFRAME FROM EXCEL SPREADSHEET
# ----------------------------------------------------------

@st.cache_data
def create_dataframe(ss):

    df = pd.read_excel(ss,
                      dtype=object,
                      header=0, 
                      keep_default_na=False)
    return df


# -------------------------------------
# FUNCTION TO READ IN PARQUET FILE DATA
# -------------------------------------

@st.cache_data(ttl=7200)
def load_parquet_data():
    url = "https://www.dropbox.com/scl/fi/jmau29b93y6d5xs4ax8wh/SOD-12.23.25.parquet?rlkey=c4vh0k168qctgsldj0ebsvyld&dl=1"
    return pd.read_parquet(url)


# ---------------------------------------------------------------------
# HELPER FUNCTION TO READ IN WHOLESALE CUSTOMERS AND CREATE USABLE LIST
# ---------------------------------------------------------------------

@st.cache_data
def gen_ws_list(df_wholesale):
    wholesale_list = []
    for ws in df_wholesale.name:
        wholesale_list.append(ws)
    return wholesale_list


# --------------------------------------------------------------------
# RENAME DF COLUMNS FOR SIMPLICITY + PREPROCESS TO AVOID COMPLICATIONS
# --------------------------------------------------------------------

@st.cache_data
def preprocess_data(df, df_quotes, df_cogs, df_shipstat_23, df_shipstat_24, df_qb, df_hsd, df_hist):
    df_quotes.rename(columns={
        'Number': 'number',
        'Customer': 'customer',
        'CustomerContact': 'contact',
        'TotalInPrimaryCurrency': 'total',
        'CreatedUtc': 'date_created',
        'Status': 'status',
        'ClosedDate': 'closed_date'}, 
        inplace=True)
    
    
    quote_cust_list = df_quotes['customer'].unique().tolist()
    
    df.rename(columns={
        'Sales Order': 'sales_order',
        'Customer': 'customer',
        'Sales Person': 'channel',
        'Ordered Date': 'order_date',
        'Ordered Month': 'order_month',
        'Sales Order Status': 'status',
        'Line Item Name': 'item_sku',
        'Line Item': 'line_item',
        'Order Quantity': 'quantity',
        'Total Line Item $': 'total_line_item_spend',
        'Ordered Year': 'ordered_year'},
        inplace=True)
    
    df.order_date = pd.to_datetime(df.order_date).dt.date
    df['total_line_item_spend'] = df['total_line_item_spend'].astype('float32')
    #df['customer'] = df['customer'].str.title()
    #df_hist['customer'] = df_hist['customer'].str.title()
    df_hist = df_hist[~df_hist['customer'].str.contains('AMAZON SALES', na=False)]
    df_hist = df_hist[~df_hist['customer'].str.contains('AMAZON', na=False)]
    df_hist = df_hist[~df_hist['customer'].str.contains('Amazon', na=False)]
    
    df_qb['customer'] = df_qb['customer'].str.title()
    df_qb = df_qb[~df_qb['customer'].str.contains('Total', na=False)]
    df_qb = df_qb[~df_qb["order_num"].str.contains("F", na=False)]
    df_qb = df_qb[~df_qb["order_num"].str.contains("CF", na=False)]
    df_qb = df_qb[~df_qb["order_num"].str.contains("(I2G)", na=False)]
    df_qb = df_qb[~df_qb["order_num"].str.contains("ch_", na=False)]
    df_qb['customer'] = df_qb['customer'].ffill()
    df_qb.dropna(subset=['date'], inplace=True)
    df_qb.dropna(subset=['total'], inplace=True)
    df_qb.reset_index(drop=True, inplace=True)
    
    df_hsd.rename(columns={
        'Sales Order': 'sales_order',
        'Customer PO': 'po',
        'Customer': 'customer',
        'Item Name': 'item',
        'Item Description': 'description',
        'Quantity Ordered': 'quantity',
        'Value Shipped': 'value',
        'Shipped Date': 'date',
        'Shipped By': 'channel'},
         inplace=True)
    
    df_shipstat_24.rename(columns={
                        'Ship Date':'shipdate',
                        'Recipient':'customer',
                        'Order #':'order_number',
                        'Provider':'provider',
                        'Service':'service',
                        'Items':'items',
                        'Paid':'cust_cost',
                        'oz':'weight',
                        '+/-':'variance'},
                        inplace=True)
    
    df_shipstat_23.rename(columns={
                        'Ship Date':'shipdate',
                        'Recipient':'customer',
                        'Order #':'order_number',
                        'Provider':'provider',
                        'Service':'service',
                        'Items':'items',
                        'Paid':'cust_cost',
                        'oz':'weight',
                        '+/-':'variance'},
                        inplace=True)  
    
    df_cogs.rename(columns={
                        'Item Number/Revision':'item',
                        'Invoice Number':'invoice',
                        'Status':'status',
                        'Source':'sales_order',
                        'Customer':'customer',
                        'Invoice Issue Date':'issue_date',
                        'Invoice Paid Date':'paid_date',
                        'Invoice Quantity':'quantity',
                        'Material Value':'material_value',
                        'Labor Value': 'labor_value',
                        'Outside Processing Value': 'processing_value',
                        'Machine Value': 'machine_value',
                        'Total Cost': 'total_cost',
                        'Total Price': 'total_price',
                        'Unit Price': 'unit_price'},
                        inplace=True)  
    
    df_cogs['total_cost'] = df_cogs['total_cost'].astype('float32')
    df_cogs['total_price'] = df_cogs['total_price'].astype('float32')
    df_cogs['unit_price'] = df_cogs['unit_price'].astype('float32')

    return df, df_quotes, df_cogs, df_shipstat_23, df_shipstat_24, df_qb, df_hsd, df_hist


# ---------------------------------------------------------------------
# DEFINE A FUNCTION TO CORRECT NAME DISCRPANCIES IN SOD AND STANDARDIZE
# ---------------------------------------------------------------------

@st.cache_data
def fix_names(df):

    df.replace('Tim Doyle', 'Timothy Doyle', inplace=True)
    df.replace('ESTEFANIA URBAN', 'Estefania Urban', inplace=True)
    df.replace('estefania urban', 'Estefania Urban', inplace=True)
    df.replace('JR Torres', 'Jorge Torres', inplace=True)
    df.replace('Saul Dominguez', 'Coco Bongo', inplace=True)
    df.replace('Paul Souza', 'Pyro Spectaculars Industries, Inc.', inplace=True)
    df.replace('Pyro Spectaculars Industries, Inc. ', 'Pyro Spectaculars Industries, Inc.', inplace=True)
    df.replace('CHRISTOPHER BARTOSIK', 'Christopher Bartosik', inplace=True)
    df.replace('Jon Ballog', 'Blair Entertainment / Pearl AV', inplace=True)
    df.replace('Jack Bermo', 'Jack Bermeo', inplace=True)
    df.replace('Tonz of Fun', 'Eric Walker', inplace=True)
    df.replace('Travis S. Johnson', 'Travis Johnson', inplace=True)
    df.replace('Yang Gao', 'Nebula NY', inplace=True)
    df.replace('Adam Stipe', 'Special Event Services (SES)', inplace=True)
    df.replace('Michael Brammer', 'Special Event Services (SES)', inplace=True)
    df.replace('ffp effects inc c/o Third Encore', 'FFP FX', inplace=True)
    df.replace('Disney Worldwide Services, Inc', 'Disney Cruise Line', inplace=True)
    df.replace('Jeff Meuzelaar', 'Jeff Meuzelaar / Pinnacle Productions', inplace=True)
    df.replace('Ernesto Blanco', 'Ernesto Koncept Systems', inplace=True)
    df.replace('Justin Jenkins', 'Justin Jenkins / Creative Production & Design', inplace=True)
    df.replace('Creative Production & Design', 'Justin Jenkins / Creative Production & Design', inplace=True)
    df.replace('Andrew Pla / Rock The House', 'Steve Tanruther / Rock The House', inplace=True)
    df.replace('Ryan Konikoff / ROCK THE HOUSE', 'Steve Tanruther / Rock The House', inplace=True)
    df.replace('Cole M. Blessinger', 'Cole Blessinger', inplace=True)
    df.replace('Parti Line International, LLC', 'Flutter Fetti', inplace=True)
    df.replace('Flutter Feti', 'Flutter Fetti', inplace=True)
    df.replace('MICHAEL MELICE', 'Michael Melice', inplace=True)
    df.replace('Michael Brammer / Special Event Services', 'Special Event Services (SES)', inplace=True)
    df.replace('Dios Vazquez ', 'Dios Vazquez', inplace=True)
    df.replace('Brilliant Stages Ltd T/A TAIT', 'Brilliant Stages', inplace=True)
    df.replace('San Clemente High School Attn Matt Reid', 'Matthew Reid', inplace=True)
    df.replace('Anita Chandra / ESP Gaming', 'Anita Chandra', inplace=True)
    df.replace('randy hood', 'Randy Hood', inplace=True)
    df.replace('Randy Hood / Hood And Associates / talent', 'Randy Hood', inplace=True)
    df.replace('Steve VanderHeyden (Band Ayd Event Group)', 'Steve Vanderheyden / Band Ayd Event Group', inplace=True)
    df.replace('Steve VanderHeyden', 'Steve Vanderheyden / Band Ayd Event Group', inplace=True)
    df.replace('Kyle Kelly', 'Special FX Rentals', inplace=True)
    df.replace('MARIE COVELLI', 'Marie Covelli', inplace=True)
    df.replace('Frank Brown', 'Frank Brown / Night Nation Run', inplace=True)
    df.replace('Matt Spencer / SDCM', 'Matt Spencer', inplace=True)
    df.replace('Solotech U.S. Corporation', 'Solotech', inplace=True)
    df.replace('Michael Bedkowski', 'POSH DJs', inplace=True)
    df.replace('Kyle Jonas', 'POSH DJs', inplace=True)
    df.replace('Evan Ruga', 'POSH DJs', inplace=True)
    df.replace('Sean Devaney', 'POSH DJs', inplace=True)
    df.replace('Brian Uychich', 'POSH DJs', inplace=True)
    df.replace('Omar Sánchez Jiménez / Pyrofetti FX', 'Pyrofetti Efectos Especiales SA de CV', inplace=True)
    df.replace('Omar Sánchez Jiménez / Pyrofetti Fx', 'Pyrofetti Efectos Especiales SA de CV', inplace=True)
    df.replace('Omar Jimenez / Pyrofetti efectos especiales', 'Pyrofetti Efectos Especiales SA de CV', inplace=True)
    df.replace('Oscar Jimenez / Pyrofetti Fx', 'Pyrofetti Efectos Especiales SA de CV', inplace=True)
    df.replace('Gilbert / Pyrotec Sa', 'Pyrofetti Efectos Especiales SA de CV', inplace=True)
    df.replace('Gilbert / Pyrotec S.A.', 'Pyrofetti Efectos Especiales SA de CV', inplace=True)
    df.replace('Gilbert Salazar / Pyrotec S.A.', 'Pyrofetti Efectos Especiales SA de CV', inplace=True)
    df.replace('Image SFX (Gordo)', 'Image SFX', inplace=True)
    df.replace('Image SFX (Drake 6 Jets)', 'Image SFX', inplace=True)
    df.replace('Image SFX (Drake 18 Jets)', 'Image SFX', inplace=True)
    df.replace('Image SFX (Water Cannon Deposit)', 'Image SFX', inplace=True)
    df.replace('Image SFX (Water Cannon Deposit)', 'Image SFX', inplace=True)
    df.replace('Shadow Mountain Productions', 'Tanner Valerio', inplace=True)
    df.replace('Tanner Valerio / Shadow Mountain Productions', 'Tanner Valerio', inplace=True)
    df.replace('Tanner Valero', 'Tanner Valerio', inplace=True)
    df.replace('Tanner Valerio / Shadow Mountain Productions (GEAR TO RETURN)', 'Tanner Valerio', inplace=True)
    df.replace('Tanner Valerio / Shadow Mountain productions (GEAR TO RETURN)', 'Tanner Valerio', inplace=True)
    df.replace('Tanner Valerio / Shadow Mountain productions', 'Tanner Valerio', inplace=True)
    df.replace('Blast Pyrotechnics', 'Blaso Pyrotechnics', inplace=True)
    df.replace('Pyrotecnico ', 'Pyrotecnico', inplace=True)
    df.replace('PYROTECNICO ', 'PYROTECNICO', inplace=True)
    df.replace('Pyrotecnico', 'PYROTECNICO', inplace=True)
    df.replace('Pyrotek FX ', 'Pyrotek FX', inplace=True)
    df.replace('Pyrotek Fx ', 'Pyrotek Fx', inplace=True)
    df.replace('Pyro Spectacular Industries', 'Pyro Spectaculars Industries, Inc.', inplace=True)
    df.replace('SK PYRO SPECIAL EFFECTS', 'SK Pyro Special Effects', inplace=True)
    df.replace('Illuminated Integration / Nashville Live', 'Illuminated Integration', inplace=True)
    df.replace('edgar guerrero', 'Edgar Guerrero', inplace=True)
    df.replace('HEDGER SANCHEZ', 'Hedger Sanchez', inplace=True)
    df.replace('Gear Club Direct Pro - Luis Garcia', 'Gear Club Direct', inplace=True)
    df.replace('edgar Rojas', 'Edgar Rojas', inplace=True)
    df.replace('Grant ashling', 'Grant Ashling', inplace=True)
    df.replace('Sebastian Gomez', 'Sebastian Gómez', inplace=True)
    df.replace('Ravinder singh', 'Ravinder Singh', inplace=True)
    df.replace('Eric Swanson / Slightly Stoopid', 'Slightly Stoopid', inplace=True)
    df.replace('the bouffants / David Griffin', 'David Griffin', inplace=True)
    df.replace('Anthony Mendoza (Infusion Lounge)', 'Anthony Mendoza', inplace=True)
    df.replace('The Party Stage Company / Ryan Smith', 'Ryan Smith', inplace=True)
    df.replace('Rafael Urban (Re-ship charge)', 'Rafael Urban', inplace=True)
    df.replace('California Pro Sound And Light', 'California Pro Sound and Light', inplace=True)
    df.replace('Max Moussier / Sound Miami Nightclub', 'Max Moussier', inplace=True)
    df.replace('Tony Tannous (Sound Agents Australia)', 'Tony Tannous', inplace=True)
    df.replace('Carlos BURGOS', 'Carlos Burgos', inplace=True)
    df.replace('Jonathan / Visual Edge', 'Visual Edge', inplace=True)
    df.replace('Justin Jenkins / Creative Production & Design', 'Justin Jenkins', inplace=True)
    df.replace('David Belogolovsky (6 solenoids)', 'David Belogolovsky', inplace=True)
    df.replace('amar gill', 'Amar Gill', inplace=True)
    df.replace('ARIEL MARTINEZ', 'Ariel Martinez', inplace=True)
    df.replace('JOSE ANTONIO MAR HERNANDEZ', 'Jose Antonio Mar Hernandez', inplace=True)
    df.replace('Alma Delia Rivero Sánchez', 'Alma Delia Rivero Sanchez', inplace=True)
    df.replace('PROMEDSA', 'Promedsa', inplace=True)
    df.replace('JABARI JOHNSON', 'Jabari Johnson', inplace=True)
    df.replace('Paul Klassenn / Laird FX', 'Paul Klaassen / Laird FX', inplace=True)
    df.replace('Parag Enterprises / Divine FX', 'Divine FX', inplace=True)
    df.replace('Romin Zandi ', 'Romin Zandi', inplace=True)
    df.replace('Romin Zandi (Personal)', 'Romin Zandi', inplace=True)
    df.replace('cesar palomino', 'Cesar Palomino', inplace=True)
    df.replace('zcibeiro Medina', 'Zcibeiro Medina', inplace=True)
    df.replace('Gregory Lomangino', 'Greg Lomangino', inplace=True)
    df.replace('Rory McElroy ', 'Rory McElroy', inplace=True)
    df.replace('Ronald Michel ', 'Ronald Michel', inplace=True)
    df.replace('Roland Mendoza', 'Rolando Mendoza', inplace=True)
    df.replace('rolando mendoza', 'Rolando Mendoza', inplace=True)
    df.replace('Rochester Red Wings / Morrie', 'Morrie Silver', inplace=True)
    df.replace('ROBERT SIMPSON', 'Robert Simpson', inplace=True)
    df.replace('ER Productions (Device programmer)', 'ER Productions', inplace=True)
    df.replace('University of Wyoming / Shelley', 'University of Wyoming', inplace=True)
    df.replace('Mario moreno', 'Mario Moreno', inplace=True)
    df.replace('gregory morris', 'Gregory Morris', inplace=True)
    df.replace('preston M Murray', 'Preston M Murray', inplace=True)
    df.replace('Jorge Pulido Ayala / MIA Eventos', 'Jorge Ayala', inplace=True)
    df.replace('Jorge Pulido Ayala', 'Jorge Ayala', inplace=True)
    df.replace('Jorge Ayala / MIA Eventos', 'Jorge Ayala', inplace=True)
    df.replace('Garth Hoffmann ', 'Garth Hoffmann', inplace=True)
    df.replace('Ernesto Koncept Systems / Khalil', 'Ernesto Koncept Systems', inplace=True)
    df.replace('jose ramos', 'Jose Ramos', inplace=True)
    df.replace('RAMON', 'Ramon', inplace=True)
    df.replace('4WALL ENTERTAINMENT, INC. ', '4WALL ENTERTAINMENT, INC.', inplace=True)
    df.replace('alex allen', 'Alex Allen', inplace=True)
    df.replace('Advanced Entertainment Services ', 'Advanced Entertainment Services', inplace=True)
    df.replace('adrian zerla', 'Adrian Zerla', inplace=True)
    df.replace('Anthony LoBosco', 'Anthony Lobosco', inplace=True)
    df.replace('ANTHONY DAMPLO', 'Anthony Damplo', inplace=True)
    df.replace('matthew reid', 'Matthew Reid', inplace=True)
    df.replace('Matt Reid', 'Matthew Reid', inplace=True)
    df.replace('PROVIDE CO.,LTD.', 'Provide Co., LTD', inplace=True)
    df.replace('Gear Club Direct ', 'Gear Club Direct', inplace=True)
    df.replace('Cole bibler', 'Cole Bibler', inplace=True)
    df.replace('cole bibler', 'Cole Bibler', inplace=True)
    df.replace('juan gil', 'Juan Gil', inplace=True)
    df.replace('juan mora', 'Juan Mora', inplace=True)
    df.replace('LEGACY MARLEY', 'Legacy Marley', inplace=True)
    df.replace('Ben steele', 'Ben Steele', inplace=True)
    df.replace('Benjamin Steele', 'Ben Steele', inplace=True)
    df.replace('Marisol Padilla Padilla', 'Marisol Padilla', inplace=True)
    df.replace('Bes Entertainment / Matt Besemer', 'Matt Besemer', inplace=True)
    df.replace('John Wright / Valdosta State University', 'John Wright', inplace=True)
    df.replace('Valdosta University', 'John Wright', inplace=True)
    df.replace('Deep South Productions ', 'Deep South Productions', inplace=True)
    df.replace('Jon Ballog', 'Blair Entertainment / Pearl AV', inplace=True)
    df.replace('Jon ballog', 'Blair Entertainment / Pearl AV', inplace=True)
    df.replace('Marisol Padilla Padilla', 'Marisol Padilla', inplace=True)
    df.replace('Sean Weaver / David Hays / Boland FX', 'Sean Weaver', inplace=True)
    df.replace('Sean Weaver / Universal Studios Orlando', 'Sean Weaver', inplace=True)
    df.replace('DEYRON BELL', 'Deyron Bell', inplace=True)
    df.replace('Toucan Productions, Inc.', 'Toucan Productions', inplace=True)
    df.replace('Pro FX Inc', 'Pro FX', inplace=True)
    df.replace('SMG Events / Adam Lucero ', 'SMG Events', inplace=True)
    df.replace('SMG Events / Adam Lucero', 'SMG Events', inplace=True)
    df.replace('SMG Events/Adam Lucero ', 'SMG Events', inplace=True)
    df.replace('SMG Events/Adam Lucero', 'SMG Events', inplace=True)
    df.replace('MICHAEL GREENBERG', 'Michael Greenberg', inplace=True)
    df.replace('ADAM MORGAN', 'Adam Morgan', inplace=True)
    df.replace('Complete Production Resources ', 'Complete Production Resources', inplace=True)
    df.replace('Gregory Lomangino', 'Greg Lomangino', inplace=True)
    df.replace('James Kerns', 'James Mitchell Kerns', inplace=True)
    df.replace('Jeff Meuzelaar / Pinnacle Productions', 'Jeff Meuzelaar', inplace=True)
    df.replace('Justin Thomas / J&M Displays', 'Justin Thomas', inplace=True)
    df.replace('Ernie Valdez Jr.', 'Ernie Valdez', inplace=True)
    df.replace('warren monnich / Subtronics', 'Warren Monnich', inplace=True)
    df.replace('warren monnich', 'Warren Monnich', inplace=True)
    df.replace('Jeff Cornell', 'JDL FX', inplace=True)
    df.replace('ESI Production', 'ESI Productions', inplace=True)
    df.replace('ESI Productions ', 'ESI Productions', inplace=True)
    df.replace('John Wright / Valdosta State University', 'John Wright', inplace=True)
    df.replace('sean atkins ', 'Sean Atkins', inplace=True)
    df.replace('sean atkins', 'Sean Atkins', inplace=True)
    df.replace('sean atkins  ', 'Sean Atkins', inplace=True)
    
   
    return df


# --------------------------------------------------------------
# FUNCTION TO LOAD IN ALL DATA FOR PROCESSING IN VARIOUS MODULES
# --------------------------------------------------------------

@st.cache_data
def load_all_data():

    ### LOAD FILES
    
    #sod_ss = 'MASTER DATA 2.17.25.xlsx'
    sod_ss = 'SOD 7.1.25.xlsx'
    
    
    hist_ss = 'data/Files/CC Historical Sales 2.7.xlsx'
    
    hsd_ss = 'data/Files/HSD 11.8.24.xlsx'
    
    quote_ss = 'data/Files/Quote Report 1.28.25.xlsx'
    
    #sales_sum_csv = 'Total Summary-2022 - Present.csv'
    
    shipstat_ss_24 = 'data/Files/2024 SR 11.01.24.xlsx'
    shipstat_ss_23 = 'data/Files/2023 SR.xlsx'
    
    #prod_sales = 'Product Sales Data.xlsx'
    
    wholesale_cust = 'data/Files/wholesale_customers 4.3.25.xlsx'
    
    cogs_ss = 'data/Files/COGS 1.29.25a.xlsx'
    
    qb_ss = 'data/Files/QB Transactions.xlsx'

    df = load_parquet_data()
    
    df_hist = pd.read_excel(hist_ss, dtype=object, header=0)
    df_hist.fillna(0, inplace=True)
    
    df_quotes = create_dataframe(quote_ss)
    
    df_shipstat_24 = create_dataframe(shipstat_ss_24)
    
    df_shipstat_23 = create_dataframe(shipstat_ss_23)
    
    df_hsd = create_dataframe(hsd_ss)
    
    df_wholesale = create_dataframe(wholesale_cust)
    
    df_cogs = create_dataframe(cogs_ss)
    
    df_qb = pd.read_excel(qb_ss,
                          #dtype=object,
                          header=0,
                          keep_default_na=True)


    wholesale_list = gen_ws_list(df_wholesale)
    
    ### STRIP UNUSED COLUMN ###
    
    missing_cols = [col for col in ['Ordered Week', 'Customer Item Name'] if col not in df.columns]
    if missing_cols:
        print(f"Warning: The following columns are missing and cannot be dropped: {missing_cols}")
    else:
        df = df.drop(['Ordered Week', 'Customer Item Name'], axis=1)


    df, df_quotes, df_cogs, df_shipstat_23, df_shipstat_24, df_qb, df_hsd, df_hist = preprocess_data(df, df_quotes, df_cogs, df_shipstat_23, df_shipstat_24, df_qb, df_hsd, df_hist)

    df = fix_names(df)
    df_hist = fix_names(df_hist)
    df_qb = fix_names(df_qb)
    
    ### CREATE A LIST OF UNIQUE CUSTOMERS ###
    unique_customer_list = df.customer.unique().tolist()
    hist_customer_list = df_hist['customer'].unique()
    master_customer_list = list(set(unique_customer_list) | set(hist_customer_list))

    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

    return df, df_quotes, df_cogs, df_shipstat_23, df_shipstat_24, df_qb, df_hsd, df_hist, unique_customer_list, master_customer_list, wholesale_list
    
    
