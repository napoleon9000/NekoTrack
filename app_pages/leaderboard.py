import streamlit as st
import pandas as pd
from dataclasses import dataclass
import numpy as np

from toy_record import Manager, Record
import matplotlib.pyplot as plt

def show_list(data, all_machines):
    sorted_idx = np.argsort(data)
    for idx in sorted_idx:
        machine = all_machines[idx]
        texts = f"**{machine.name}**: {data[idx]:.2f}"
        if machine.notes is not None and machine.notes != "":
            texts += f"  ({machine.notes})"
        st.markdown(texts)

def show_bar_chart(data, all_machines, title):
    sorted_idx = np.argsort(data)[::-1]
    labels = [all_machines[idx].name for idx in sorted_idx]
    values = [data[idx] for idx in sorted_idx]
    fig, ax = plt.subplots()
    ax.barh(labels, values)
    ax.set_xlabel('Payout Rate')
    ax.set_ylabel('Machine')
    ax.set_title(title)
    ax.grid(True)
    st.pyplot(fig)

    data_df = pd.DataFrame({'Machine': labels, 'Payout Rate': values}, index=range(len(labels)))
    return data_df



def app():
    st.title("Leaderboard")
    st.markdown("---")

    # show all machines and images
    env = st.secrets['ENV']['ENV']
    manager = Manager(env)
    all_results = manager.get_all_machines_payout_rate()
    all_machines = manager.get_all_machines_obj()

    last_day_payout_rate = [result['last_day_payout_rate'] for result in all_results]
    all_time_payout_rate = [result['all_time_payout_rate'] for result in all_results]
    last_3_days_payout_rate = [result['last_3_days_payout_rate'] for result in all_results]

    col1, col2 = st.columns(2)
    with col1:
        data_df = show_bar_chart(last_day_payout_rate, all_machines, "Last Day Payout Rate")
        with st.expander("Detail", expanded=False):
            st.write(data_df)

    with col2:
        data_df = show_bar_chart(last_3_days_payout_rate, all_machines, "Last 3 Days Payout Rate")
        with st.expander("Detail", expanded=False):
            st.write(data_df)

    with col1:
        data_df = show_bar_chart(all_time_payout_rate, all_machines, "All Time Payout Rate")
        with st.expander("Detail", expanded=False):
            st.write(data_df)



if __name__ == "__main__":
    app()