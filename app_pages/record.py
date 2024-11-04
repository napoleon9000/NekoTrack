import streamlit as st
import pandas as pd
from dataclasses import dataclass
import traceback
import logging
import pytz
from datetime import datetime
import time
from backend.toy_record_mgr import Manager, Record

logger = logging.getLogger(__name__)

def save_record(machine_id, manager: Manager):
    date = st.session_state[f"date"]
    date_str = date.strftime("%Y-%m-%d")
    coins_in_str = st.session_state[f"coins_in_str_{machine_id}"]
    toys_payout_str = st.session_state[f"toys_payout_str_{machine_id}"]
    coins_in = int(coins_in_str) if coins_in_str != "" else 0
    toys_payout = int(toys_payout_str) if toys_payout_str != "" else 0
    param_strong_strength = st.session_state[f"param_strong_strength_{machine_id}"]
    param_medium_strength = st.session_state[f"param_medium_strength_{machine_id}"]
    param_weak_strength = st.session_state[f"param_weak_strength_{machine_id}"]
    param_award_interval = st.session_state[f"param_award_interval_{machine_id}"]
    param_mode = st.session_state[f"param_mode_{machine_id}"]
    notes = st.session_state[f"notes_{machine_id}"]
    id = f"{date_str}#{machine_id}"
    if coins_in == 0 or toys_payout == 0:
        st.error("Coins in and toys payout cannot be 0! Please check your input and try again.")
    try:
        record = Record(
            id=id,
            date=date_str,
            machine_id=machine_id,
            coins_in=coins_in,
            toys_payout=toys_payout,
            param_strong_strength=param_strong_strength,
            param_medium_strength=param_medium_strength,
            param_weak_strength=param_weak_strength,
            param_award_interval=param_award_interval,
            param_mode=param_mode,
            notes=notes
        )
        manager.create_record(record)
        st.success("Record saved successfully!")
    except Exception as e:
        traceback_msg = traceback.format_exc()
        logger.error(f"Error saving record: {traceback_msg}")
        st.error(f"Error saving record: {e}")


def app():
    env = st.secrets['ENV']['ENV']
    manager = Manager(env)

    # today's date in central time
    today = datetime.now(pytz.timezone('US/Central'))
    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
    with st.form(key='income_record_form', border=False):
        with col1:
            st.title("Income Record")
        with col2:
            date = st.date_input("Date", key="date2", value=today)
        with col3:
            post_income = st.number_input("POS Income", key="post_income", value=0)
        with col4:
            auto_income = st.number_input("Auto Machine Income", key="auto_income", value=0)
        if st.form_submit_button("Save"):
            manager.create_income_record(date=date.strftime("%Y-%m-%d"), POS_machine=post_income, auto_machine=auto_income)
            st.success("Income record saved successfully!")
    
    st.markdown("---")

    col1, col2, _ = st.columns([2, 2, 4])
    with col1:
        st.title("Toys Record")
    with col2:
        date = st.date_input("Date", key="date", value=today)
    st.markdown("---")

    # show all machines and images
    machines = manager.get_all_machines()
    


    for machine in machines:
        machine_id = machine['id']
        with st.form(key='record_form_'+machine_id, border=False):
            cols = st.columns(5)
            with cols[0]:
                machine_image = manager.get_image_by_machine_id(machine_id)
                if machine_image is None:
                    machine_image = 'claw_machine.webp'
                name = machine['name']
                location = machine['location']
                st.image(machine_image, width=150)
                if name is not None and name != "":
                    st.markdown(f"**Name:** {name}")
                else:
                    st.markdown(f"**id:** {machine_id}")
                if location is not None and location != "":
                    st.markdown(f"**Location:** {location}")
                

            with cols[1]:
                coins_in_str = st.text_input("Coins In", key=f"coins_in_str_{machine_id}", value="")
                toys_payout_str = st.text_input("Toys Payout", key=f"toys_payout_str_{machine_id}", value="")
                coins_in = int(coins_in_str) if coins_in_str != "" else 0
                toys_payout = int(toys_payout_str) if toys_payout_str != "" else 0

            with cols[2]:
                param_strong_strength_value = machine.get('param_strong_strength', 0) if machine.get('param_strong_strength') is not None else 0    
                param_strong_strength = st.number_input("Strong Strength", key=f"param_strong_strength_{machine_id}", min_value=0.0, max_value=50.0, step=0.2, value=param_strong_strength_value)
                param_medium_strength_value = machine.get('param_medium_strength', 0) if machine.get('param_medium_strength') is not None else 0
                param_medium_strength = st.number_input("Medium Strength", key=f"param_medium_strength_{machine_id}", min_value=0.0, max_value=50.0, step=0.2, value=param_medium_strength_value)
                param_weak_strength_value = machine.get('param_weak_strength', 0) if machine.get('param_weak_strength') is not None else 0
                param_weak_strength = st.number_input("Weak Strength", key=f"param_weak_strength_{machine_id}", min_value=0.0, max_value=50.0, step=0.2, value=param_weak_strength_value)
            
            with cols[3]:
                param_award_interval = st.number_input("Award Interval", key=f"param_award_interval_{machine_id}", min_value=0, max_value=1000, value=machine.get('param_award_interval', 0))
                options = ["1", "2", "3"]
                param_mode_value = machine.get('param_mode', 0) if machine.get('param_mode') is not None else '1'
                param_mode_value = options.index(param_mode_value)
                param_mode = st.selectbox("Mode", options, key=f"param_mode_{machine_id}", index=param_mode_value)
            
            with cols[4]:
                notes = st.text_area("Notes", key=f"notes_{machine_id}")

            if st.form_submit_button("Save"):
                save_record(machine_id, manager)
        
        st.markdown("---")
    
    if st.button("Save All"):
        # collect all the data
        with st.spinner("Saving..."):
            for machine in machines:
                machine_id = machine['id']
                save_record(machine_id, manager)
                time.sleep(1)

        st.success("Record saved successfully!")
    

if __name__ == "__main__":
    app()