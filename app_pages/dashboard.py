import streamlit as st
from backend.toy_record_mgr import Manager as ToyRecordManager
import logging
import pandas as pd

logger = logging.getLogger(__name__)



def app():
    st_secrets = dict(st.secrets)
    credentials = st.secrets["credentials"].to_dict()
    env = st_secrets['ENV']['ENV']

    if env != 'dev':
        authentication_status = st.session_state['authentication_status']
        if authentication_status:
            name = st.session_state['name']
            username = st.session_state['username']
        else:
            st.error("Please login to continue")
            st.stop()

    else:
        name = 'Dev'
        authentication_status = True
        username = 'nekoconnect'

    col1, col2 = st.columns([3, 1])
    with col1:
        if env == 'dev':
            st.title(f"NekoTrack - Dashboard - {env}")
        else:
            st.title(f"NekoTrack - Dashboard")
    with col2:
        col3, col4 = st.columns([1, 1])
        with col3:  
            st.write(f'Welcome *{name}*')

    toy_record_manager = ToyRecordManager(env)

    records = toy_record_manager.get_all_income_records()
    machines = toy_record_manager.get_all_machines_obj()
    all_analyze_results = []
    today_results = []
    last_3_days_results = []
    for machine in machines:
        analyze_result, all_time_payout_rate, last_3_days_payout_rate = toy_record_manager.calculate_machine_payout_rate(machine.id)
        all_analyze_results.append(analyze_result)
        today_payout_rate = analyze_result['daily_payout_rate'].iloc[-1]
        today_results.append((machine.name, today_payout_rate))
        last_3_days_results.append((machine.name, last_3_days_payout_rate))
    today_df = pd.DataFrame(today_results, columns=['machine', 'payout_rate']).sort_values(by='payout_rate', ascending=False)
    today_df['payout_rate'] = today_df['payout_rate'].round(decimals=2)
    last_3_days_df = pd.DataFrame(last_3_days_results, columns=['machine', 'payout_rate']).sort_values(by='payout_rate', ascending=False)
    last_3_days_payout_rate = analyze_result['daily_payout_rate'].iloc[-3:].mean()
    last_3_days_df['payout_rate'] = last_3_days_df['payout_rate'].round(decimals=2)

    _, df = toy_record_manager.plot_overall_analyze_result(all_analyze_results)
    today_payout_rate = df['daily_payout_rate'].iloc[-1]
    last_3_days_payout_rate = df['daily_payout_rate'].iloc[-3:].mean()


    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        with st.container(border=True):
            st.markdown("### Income Records")
            if records is not None:
                st.dataframe(records.astype({
                    'date':'datetime64[ns]',
                    'POS_machine': 'float64',
                    'auto_machine': 'float64',
                    'total': 'float64',
                }))
            else:
                st.info("No income records yet")
    
    with col2:
        # machines with highest payout rate and lowest payout rate
        with st.container(border=True):
            st.markdown(f"### Payout Rate - Today: {today_payout_rate:.2f}")
            st.markdown("#### Hardest 5")
            # First transpose, then convert types
            hardest_5 = today_df.head(5).reset_index(drop=True).T
            st.dataframe(hardest_5.astype({
                0: 'string',  # After transpose, column names become numeric indices
                1: 'string',
                2: 'string',
                3: 'string',
                4: 'string'
            }))
            
            st.markdown("#### Easiest 5")
            easiest_5 = today_df.tail(5).sort_values(by='payout_rate', ascending=True).reset_index(drop=True).T
            st.dataframe(easiest_5.astype({
                0: 'string',
                1: 'string',
                2: 'string',
                3: 'string',
                4: 'string'
            }))
    with col3:
        with st.container(border=True):
            st.markdown(f"### Payout Rate - Last 3 Days: {last_3_days_payout_rate:.2f}")
            st.markdown("#### Hardest 5")
            hardest_5 = last_3_days_df.head(5).reset_index(drop=True).T
            st.dataframe(hardest_5.astype({
                0: 'string',
                1: 'string',
                2: 'string',
                3: 'string',
                4: 'string'
            }))
            st.markdown("#### Easiest 5")
            easiest_5 = last_3_days_df.tail(5).sort_values(by='payout_rate', ascending=True).reset_index(drop=True).T
            st.dataframe(easiest_5.astype({
                0: 'string',
                1: 'string',
                2: 'string',
                3: 'string',
                4: 'string'
            }))
        
    st.markdown("---")

