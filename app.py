# Basic mortgage monthly payment app using streamlit
# To run locally, go to command line and run:
# 'streamlit run app.py' from the directory containing this file
# Must first run 'pip install streamlit'

# Dependencies - these must be in requirements.txt
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ----------------------------
# Page Config & Title
# ----------------------------
st.set_page_config(page_title="Mortgage Affordability Heatmap", layout="wide")
st.title("Monthly Payment Sensitivity")
st.write("Explore how monthly mortgage payments shift with changes in home price, interest rate, and other key factors.")


# ----------------------------
# Sidebar Controls
# ----------------------------
with st.sidebar:
    st.header("Inputs & Assumptions")
    st.caption("Adjust the sliders below to explore how changes in purchase price, interest rate, and other factors affect your monthly payment.")
    
    # Down Payment, Term, Tax Rate, Insurance, PMI, HOA, Flood
    # Each slider defines a range of possible values for that parameter,
    # the default value is used when the app is first loaded, & the label 
    # formatting displayed.
    down_payment = st.select_slider(
        "Down Payment ($)",
        options=list(range(0, 40_001, 1_000)),
        value=25_000,
        format_func=lambda x: f"${x:,.0f}"
    )
    term_years = st.select_slider(
        "Mortgage Term (Years)",
        options=list(range(10, 31, 5)),
        value=30, 
        format_func=lambda x: f"{x} Years"
    )
    effective_tax_rate = st.select_slider(
        "Effective Tax Rate (%)",
        options=list(np.round(np.arange(0.50, 1.51, 0.01), 2)),
        value=0.91,
        format_func=lambda x: f"{x:.2f}%"
    )
    annual_premium = st.select_slider(
        "Annual Homeowners Insurance ($)",
        options=list(range(2_000, 5_001, 20)),
        value=3120,
        format_func=lambda x: f"${x:,.0f}"
    )
    pmi_annual_rate = st.select_slider(
        "PMI Rate (%)",
        options=list(np.round(np.arange(0.30, 1.51, 0.01), 2)),
        value=0.50,
        format_func=lambda x: f"{x:.2f}%",
        help="Private Mortgage Insurance (PMI) rate applied if down payment is less than 20% of purchase price"
    )
    hoa_monthly = st.select_slider(
        "Monthly HOA Fees ($)",
        options=list(range(0, 501, 25)),
        value=0,
        format_func=lambda x: f"${x:,.0f}"
    )
    flood_annual_premium = st.select_slider(
        "Annual Flood Insurance ($)",
        options=list(range(300, 1_201, 25)),
        value=400,
        format_func=lambda x: f"${x:,.0f}"
    )

    # Purchase Prices & Interest Rates - min, max, step
    # These define the grid of purchase prices & interest rates to evaluate
    # in the heatmap.
    price_min = st.select_slider(
        "Purchase Price min", 
        options=list(range(230_000, 310_001, 1_000)),
        value=250_000,
        format_func=lambda x: f"${x:,.0f}"
    )
    price_max = st.select_slider(
        "Purchase Price max",
        options=list(range(230_000, 310_001, 1_000)),
        value=305_000,
        format_func=lambda x: f"${x:,.0f}"
    )
    price_step = st.select_slider(
        "Purchase Price step", 
        options=list(range(1_000, 25_001, 1_000)),
        value=5_000, 
        format_func=lambda x: f"${x:,.0f}",
        help="Step size for purchase price increments in the heatmap"
    )
    rate_min = st.select_slider(
        "Interest Rate min (%)", 
        options=np.round(np.arange(3, 8.1, 0.1), 3),
        value=4.0,
        format_func=lambda x: f"{x:.1f}%"
    )
    rate_max = st.select_slider(
        "Interest Rate max (%)",
        options=np.round(np.arange(3, 8.1, 0.1), 3),
        value=6.5,
        format_func=lambda x: f"{x:.1f}%"
    )
    rate_step = st.select_slider(
        "Interest Rate step (%)",
        options=[0.1, 0.25, 0.5, 1.0],
        value=0.25, 
        format_func=lambda x: f"{x:.2f}%",
        help="Step size for interest rate increments in the heatmap"
    )


# ----------------------------
# Monthly Payment Function - taken mostly from house_buying.ipynb
# ----------------------------
def monthly_payment(purchase_price: float, 
                    down_payment: float, 
                    note_rate: float, 
                    term_years: int, 
                    effective_tax_rate: float,
                    annual_premium: float, 
                    pmi_annual_rate: float, 
                    hoa_monthly: float, 
                    flood_annual_premium: float, 
                    verbose=False):
    """Calcuates the total estimated monthly payment for a house; does not include utilities and maintenance.

    Args:
        purchase_price (float): The total price of the house.
        down_payment (float): The down payment made on the house.
        note_rate (float): The annual interest rate on the mortgage.
        term_years (integer): The term of the mortgage in years.
        effective_tax_rate (float): The effective property tax rate.
        annual_premium (integer): The annual homeowners insurance premium.
        pmi_annual_rate (float): The annual mortgage insurance premium rate.
        hoa_monthly (integer): The monthly homeowners association fee.
        verbose (bool, optional): If True, prints detailed payment breakdown. Defaults to False.

    Returns:
        float: The total estimated monthly payment.
    """    

    # <1> Principal & Interest (P&I)
    L_base = purchase_price - down_payment
    i = note_rate / 12
    n = term_years * 12
    P_and_I = L_base * (i * (1 + i)**n) / ((1 + i)**n - 1)

    # <2> Escrows
    taxes_monthly = (purchase_price * effective_tax_rate) / 12  
    hoi_monthly = annual_premium / 12   
    pmi_monthly = ((L_base * pmi_annual_rate) / 12) if down_payment < 0.20 * purchase_price else 0.0
    flood_monthly = flood_annual_premium / 12  

    # Total
    return P_and_I + taxes_monthly + hoi_monthly + pmi_monthly + hoa_monthly + flood_monthly

# Build a grid of monthly payments
prices = np.arange(price_min, price_max + 1, price_step, dtype=int)
rates = np.round(np.arange(rate_min/100, rate_max/100 + 1e-12, rate_step/100, dtype=float), 4)

# Fill the monthly payment grid
data = []
for r in rates:
    for p in prices:
        payment = monthly_payment(purchase_price=p, down_payment=down_payment, note_rate=r, 
                                  term_years=term_years, effective_tax_rate=effective_tax_rate/100, 
                                  annual_premium=annual_premium, pmi_annual_rate=pmi_annual_rate/100,
                                  hoa_monthly=hoa_monthly, flood_annual_premium=flood_annual_premium, 
                                  verbose=False)
        data.append({'interest_rate': r, 
                     'purchase_price': p, 
                     'monthly_payment': payment})  
df = pd.DataFrame(data)


# ----------------------------
# Heatmap (Plotly)
# ----------------------------
fig = px.imshow(                                # imshow creates heatmaps as displayed matrices
    df.pivot(index="interest_rate",             # Create a pivot table of monthly payments with interest rates as rows
             columns="purchase_price",          # and purchase prices as columns
             values="monthly_payment"),
    color_continuous_scale='RdYlGn_r',          # low=green, high=red
    aspect="auto",                              # Auto aspect ratio
    origin='lower',                             # Put the lowest values at the bottom
    labels=dict(color="Monthly Payment"),
    zmin=1_700,                                 # Anchor to a fixed min/max for color scale
    zmax=2_025
)

# Format axes and colorbar
fig.update_layout(
    xaxis_title="Purchase Price",               # X-axis label
    yaxis_title="Interest Rate",                # Y-axis label
    xaxis=dict(tickformat="$,.0f"),             # Format x-axis tick labels as currency
    yaxis=dict(tickformat=".1%"),               # Format y-axis tick labels as percentages
    coloraxis_colorbar=dict(tickformat="$,.0f") # Format colorbar tick labels as currency
)

fig.update_traces(texttemplate="$%{z:,.0f}", textfont_size=11)  # Show formatted monthly payment values in each cell

# Show the heatmap figure in Streamlit
st.plotly_chart(fig, use_container_width=True)

# Show the underlying data
df_wide = df.pivot(index="interest_rate",       # Pivot to wide format for display; rows=interest rates
                   columns="purchase_price",    # Columns=purchase prices
                   values="monthly_payment")    # Values=monthly payments  

# The st.dataframe doesn't honor Styler.format_index/columns names, 
# so we set them as formatted strings here
df_wide.index = pd.Index([f"{x:.1%}" for x in df_wide.index], name='Interest Rate')         # Format interest rates as percentages
df_wide.columns = pd.Index([f"${x:,.0f}" for x in df_wide.columns], name='Purchase Price')  # Format purchase prices as currency

styled = (df_wide.style.format('${:,.2f}'))         # Format all values as currency with 2 decimal places

with st.expander("Show Values"):                    # Collapsible section to show underlying data
    st.dataframe(styled, use_container_width=True)  # Show the styled DataFrame; auto-stretch to container width