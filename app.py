# Basic mortgage monthly payment app using streamlit
# To run locally, go to command line and run:
# streamlit run ./app.py
# Must first run pip install streamlit

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
    annual_premium = st.select_slider("Annual Homeowners Insurance ($)",
        "Annual Homeowners Insurance ($)",
        options=list(range(2_000, 5_001, 20)),
        value=3120,
        format_func=lambda x: f"${x:,.0f}"
    )
    pmi_annual_rate = st.select_slider(
        "PMI Rate (%)",
        options=list(np.round(np.arange(0.30, 1.51, 0.01), 2)),
        value=0.50,
        format_func=lambda x: f"{x:.2f}%"
    )
    hoa_monthly = st.select_slider("Monthly HOA Fees ($)",
        options=list(range(0, 501, 25)),
        value=0,
        format_func=lambda x: f"${x:,.0f}"
    )
    flood_annual_premium = st.select_slider("Annual Flood Insurance ($)",
        options=list(range(300, 1_201, 25)),
        value=400,
        format_func=lambda x: f"${x:,.0f}"
    )

    # Purchase Prices - define min, max, step
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
        format_func=lambda x: f"${x:,.0f}"
    )

    # Interest Rates - define min, max, step
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
        format_func=lambda x: f"{x:.2f}%"
    )


# ----------------------------
# Monthly Payment Function
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
fig = px.imshow(
    df.pivot(index="interest_rate", 
             columns="purchase_price", 
             values="monthly_payment"),
    color_continuous_scale='RdYlGn_r',          # low=green, high=red
    aspect="auto",
    labels=dict(color="Monthly Payment ($)"),
    zmin=1_700,                                 # anchor to a fixed min/max for color scale
    zmax=2_025
)

# Format axes and colorbar
fig.update_layout(
    xaxis_title="Purchase Price",
    yaxis_title="Interest Rate",
    xaxis=dict(tickformat="$,.0f"),
    yaxis=dict(tickformat=".1%"),
    coloraxis_colorbar=dict(tickformat="$,.0f")
)

# Add annotations
fig.update_traces(texttemplate="$%{z:,.0f}", textfont_size=11)

# Show the figure in Streamlit
st.plotly_chart(fig, use_container_width=True)

# Show the underlying data
with st.expander("Show Values"):
    st.dataframe(df.pivot(index="interest_rate", columns="purchase_price", values="monthly_payment").round(2))