import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#st.set_page_config(layout="wide")
st.title("📊 Demand Distribution & Rolling Demand Analyzer")

st.write("Upload a file containing day-to-day sales data.")

# ==============================
# FILE UPLOAD
# ==============================

uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:

    # Read file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("Data Preview")
    st.dataframe(df.head())

    # ==============================
    # COLUMN SELECTION
    # ==============================

    column = st.selectbox("Select Demand Column", df.columns)

    if "Date" not in df.columns:
        st.error("Your file must contain a 'Date' column.")
    else:

        df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
        df = df.sort_values("Date")

        demand_data = df[column].dropna()

        # ==============================
        # HISTOGRAM
        # ==============================

        st.subheader("📊 Demand Distribution")

        bins = st.slider("Select Number of Bins", 5, 50, 15)

        fig1, ax1 = plt.subplots(figsize=(8,4))
        ax1.hist(demand_data, bins=bins)
        ax1.set_xlabel("Demand")
        ax1.set_ylabel("No of Days")
        ax1.set_title("Demand Distribution Histogram")

        st.pyplot(fig1)

        # ==============================
        # DESCRIPTIVE STATISTICS
        # ==============================

        st.subheader("📈 Descriptive Statistics")

        mean = demand_data.mean()
        std_dev = demand_data.std()
        count = demand_data.count()
        min_val = demand_data.min()
        max_val = demand_data.max()
        q25 = demand_data.quantile(0.25)
        q50 = demand_data.quantile(0.50)
        q75 = demand_data.quantile(0.75)
        q90 = demand_data.quantile(0.90)
        q95 = demand_data.quantile(0.95)

        cv = std_dev / mean if mean != 0 else 0

        stats_df = pd.DataFrame({
            "Metric": [
                "Count",
                "Mean",
                "Standard Deviation",
                "Minimum",
                "25%",
                "50% (Median)",
                "75%",
                "90%",
                "95%",
                "Maximum",
                "Coefficient of Variation (CV)"
            ],
            "Value": [
                round(count, 2),
                round(mean, 2),
                round(std_dev, 2),
                round(min_val, 2),
                round(q25, 2),
                round(q50, 2),
                round(q75, 2),
                round(q90, 2),
                round(q95, 2),
                round(max_val, 2),
                round(cv, 3)
            ]
        })

        st.table(stats_df)

        st.markdown("""
        **CV Interpretation:**
        - CV < 0.5 → Stable demand  
        - 0.5 – 1 → Moderate variability  
        - > 1 → Highly uncertain demand  
        """)

        # ==============================
        # ROLLING N-DAY CUMULATIVE DEMAND
        # ==============================

        st.subheader("📊 Rolling N-Day Cumulative Demand")

        n_days = st.slider(
            "Select number of days (Rolling Window)",
            min_value=2,
            max_value=60,
            value=10
        )

        df["Rolling_Demand"] = df[column].rolling(window=n_days).sum()
        rolling_df = df.dropna(subset=["Rolling_Demand"])

        fig2, ax2 = plt.subplots()

        ax2.plot(
            rolling_df["Date"],
            rolling_df["Rolling_Demand"]
        )

        ax2.set_xlabel("Date")
        ax2.set_ylabel(f"{n_days}-Day Cumulative Demand")
        ax2.set_title(f"Rolling {n_days}-Day Demand")

        st.pyplot(fig2)

        # ==============================
        # OPTIONAL: ROLLING DISTRIBUTION
        # ==============================

        st.subheader("📊 Distribution of Rolling Demand")

        fig3, ax3 = plt.subplots()
        ax3.hist(rolling_df["Rolling_Demand"], bins=bins)
        ax3.set_xlabel(f"{n_days}-Day Demand")
        ax3.set_ylabel("Frequency")
        ax3.set_title(f"Distribution of {n_days}-Day Demand")

        st.pyplot(fig3)
