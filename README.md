![Dashboard Preview](dashboard-1.png)

# 🏡 Mortgage Affordability Dashboard
Interactively explore how home prices, interest rates, and lending factors shape monthly payments.

[**Launch app on Streamlit**](https://mortgage-dashboard-fqmjntdeeqzedgcpbpnsev.streamlit.app/) 
*No installs required - runs entirely in your browser*

---

## What It Does
This dashboard visualizes the relationship between **purchase price**, **interest rate**, and **monthly mortgage payment**, according for real-world costs like:
- Property taxes
- Homeowners & flood insurance 
- PMI & HOA fees

The interactive heatmap lets you quickly see how affordability shifts as these parameters change - ideal for homebuyers, analysts, or anyone curious about market sensitivity.

---

## How It Works
Under the hood:
- Built in Python + Streamlit (*see app.py for the Python script*)
- Uses Plotly for interactive heatmaps
- Dynamically recalculates payments using a standard P&I formula plus escrows & premiums

Change the sliders and watch the heatmap update to explore affordability scenarios in real time.

---

## Run this Dashboard Locall

Run the commands below from your terminal:

```bash
# 1. Clone this repo
git clone https://github.com/lcholmes91/mortgage-dashboard.git
cd mortgage-dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the app
streamlit run app.py
```
Then open the local URL Streamlit gives you.

---

## Why I Built This
I wanted an intuitive way to visualize how subtle shifts in rates or prices affect affordability — something more interactive than a spreadsheet and more visual than a calculator.

---

## Contributing
Pull requests & ideas are welcome!
If you have feedback, feel free to [open an issue](https://github.com/lcholmes91/mortgage-dashboard/issues).