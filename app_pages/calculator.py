import streamlit as st
import pandas as pd

from calculator import profit_estimation, profit_estimation_with_total_payout

def app():
    st.title("Calculator")
    st.markdown("---")
    # profit estimation
    st.markdown("### Profit Estimation")
    
    # Input for data
    st.subheader("Enter transaction amounts")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        ones = st.number_input("Number of $1", min_value=0, step=1, key="ones")
    with col2:
        tens = st.number_input("Number of $10", min_value=0, step=1, key="tens")
    with col3:
        twenties = st.number_input("Number of $20", min_value=0, step=1, key="twenties")
    with col4:
        fifties = st.number_input("Number of $50", min_value=0, step=1, key="fifties")
    with col5:
        hundreds = st.number_input("Number of $100", min_value=0, step=1, key="hundreds")
    
    total_payout_toys = st.number_input("Total payout toys", min_value=0, step=1, key="total_payout_toys")

    # Generate data list
    data = ([1] * ones + [10] * tens + [20] * twenties + 
            [50] * fifties + [100] * hundreds)
    
    col1, col2 = st.columns(2)
    with col1:
        # Input for parameters (lower bound)
        st.subheader("Parameters (Lower Bound)")
        toys_payout_interval = st.number_input("Toys payout interval", value=3.0, step=0.1, key="toys_rate_low")
        toys_payout_rate_low = 1/toys_payout_interval
        avg_toys_cost_low = st.number_input("Average toys cost (Low):", value=2.5, step=0.1, key="toys_cost_low")
        fixed_cost_low = st.number_input("Fixed cost (Low):", value=400, step=10, key="fixed_cost_low")

    with col2:
        # Input for parameters (upper bound)
        st.subheader("Parameters (Upper Bound)")
        toys_payout_interval = st.number_input("Toys payout interval", value=8.0, step=0.1, key="toys_rate_high")
        toys_payout_rate_high = 1/toys_payout_interval
        avg_toys_cost_high = st.number_input("Average toys cost (High):", value=2.5, step=0.1, key="toys_cost_high")
        fixed_cost_high = st.number_input("Fixed cost (High):", value=400, step=10, key="fixed_cost_high")

    if st.button("Calculate Profit"):
        if data:
            # Calculate lower bound
            if total_payout_toys:
                profit_low, total_income_low, total_tokens_low, toys_payout_low = profit_estimation_with_total_payout(
                    data, total_payout_toys, avg_toys_cost_low, fixed_cost_low
                )
            else:
                profit_low, total_income_low, total_tokens_low, toys_payout_low = profit_estimation(
                    data, toys_payout_rate_low, avg_toys_cost_low, fixed_cost_low
                )
            
            # Calculate upper bound
            if total_payout_toys:
                profit_high, total_income_high, total_tokens_high, toys_payout_high = profit_estimation_with_total_payout(
                    data, total_payout_toys, avg_toys_cost_high, fixed_cost_high
                )
            else:
                profit_high, total_income_high, total_tokens_high, toys_payout_high = profit_estimation(
                    data, toys_payout_rate_high, avg_toys_cost_high, fixed_cost_high
                )
            
            st.subheader("Results")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Lower Bound")
                st.metric("Total Income", f"${total_income_low:.2f}")
                st.metric("Total Tokens", total_tokens_low)
                st.metric("Toys Payout", f"{toys_payout_low:.2f}")
                st.metric("Profit", f"${profit_low:.2f}")
            with col2:
                st.markdown("#### Upper Bound")
                st.metric("Total Income", f"${total_income_high:.2f}")
                st.metric("Total Tokens", total_tokens_high)
                st.metric("Toys Payout", f"{toys_payout_high:.2f}")
                st.metric("Profit", f"${profit_high:.2f}")
            
        else:
            st.error("Please enter at least one transaction amount.")

if __name__ == "__main__":
    app()