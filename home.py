# Standard library imports
import copy, logging, yaml
from yaml.loader import SafeLoader
from datetime import datetime

# Third-party imports
import pandas as pd
import streamlit as st
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
from streamlit_authenticator import Authenticate
from st_files_connection import FilesConnection

# Local application imports
from backend import Manager
from app_pages.edit_user import app as edit_user_page
from app_pages.add_new_user import app as add_new_user_page
from app_pages.calculator import app as calculator_page
from app_pages.machines import app as machines_page
from app_pages.record import app as record_page
from app_pages.record_analyze import app as record_analyze_page
from app_pages.edit_machine import app as edit_machine_page
from app_pages.leaderboard import app as leaderboard_page

logging.basicConfig(level=logging.INFO)

st.set_page_config(
    page_title="NekoConnect",
    layout="wide",
    )

st_secrets = dict(st.secrets)
credentials = st.secrets["credentials"].to_dict()
env = st_secrets['ENV']['ENV']

if env != 'dev':
    authenticator = Authenticate( 
        credentials,
        st_secrets['cookie']['name'],
        st_secrets['cookie']['key'],
        st_secrets['cookie']['expiry_days'],
        st_secrets['preauthorized']
    )

    name, authentication_status, username = authenticator.login(key='Login', location='main')
    st.session_state['authentication_status'] = authentication_status
    st.session_state['name'] = name
    st.session_state['username'] = username

else:
    name = 'Dev'
    authentication_status = True
    username = 'nekoconnect'

if authentication_status:
    
    mgr = Manager(env)

    # init session state
    if 'selected_user' not in st.session_state:
        st.session_state['selected_user'] = None
    if 'page' not in st.session_state:
        st.session_state['page'] = 'home'

    def switch_page(page):
        st.session_state['page'] = page

    st.sidebar.button("Home", on_click=switch_page, args=('home',), use_container_width=True)
    st.sidebar.button("Add New User", on_click=switch_page, args=('add_new_user',), use_container_width=True)
    st.sidebar.button("Edit User", on_click=switch_page, args=('edit_user',), use_container_width=True)
    st.sidebar.button("Calculator", on_click=switch_page, args=('calculator',), use_container_width=True)
    st.sidebar.button("Machines", on_click=switch_page, args=('machines',), use_container_width=True)
    st.sidebar.button("Add Record", on_click=switch_page, args=('record',), use_container_width=True)
    st.sidebar.button("Record Analyze", on_click=switch_page, args=('record_analyze',), use_container_width=True)
    st.sidebar.button("Leaderboard", on_click=switch_page, args=('leaderboard',), use_container_width=True)
    st.sidebar.button("Edit Machine", on_click=switch_page, args=('edit_machine',), use_container_width=True)


    def home_page():
        # Page functionality
            col1, col2 = st.columns([3, 1])
            with col1:
                if env == 'dev':
                    st.title(f"NekoConnect - {env}")
                else:
                    st.title(f"NekoConnect")
            with col2:
                col3, col4 = st.columns([1, 1])
                with col3:  
                    st.write(f'Welcome *{name}*')
                with col4:
                    if env != 'dev':    
                        authenticator.logout('Logout', 'main')
            st.markdown("---")
            st.markdown("### All Users")

            # find all users
            all_info = mgr.display_user_info()
            if all_info is None:
                st.info("No users found. Please add a new user.")
                return
            
            # search bar
            col1, col2 = st.columns([3, 1])
            with col1:
                search_phone = st.text_input("Enter phone number to search user")
            with col2:
                if st.button("Clear", use_container_width=True):
                    search_phone = ""
            if search_phone:
                all_info = all_info[all_info['phone_number'] == search_phone]
                all_info = all_info.reset_index(drop=True)
            
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 5])
            with col1:
                st.button('Refresh')
            with col2:
                db_json = mgr.download_all_data()
                st.download_button(
                    label="Download data",
                    data=db_json,
                    file_name=f"nekoconnect_users_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json",
                    mime="application/json",
                )

            def on_edit_click(index):
                st.session_state['selected_user'] = all_info.iloc[index]
                st.session_state['page'] = 'edit_user'


            def on_delete_click(index):
                # double check to confirm deletion
                phone_number = all_info.iloc[index]['phone_number']
                mgr.delete_user(phone_number)

            for index, row in all_info.iterrows():
                col1, col2, col3 = st.columns([5, 1, 1])
                with col1:
                    row = pd.DataFrame(row).T
                    st.dataframe(row, use_container_width=True)
                with col2:
                    st.button("Edit", key=f"edit_{index}", use_container_width=True, on_click=on_edit_click, args=(index,))
                with col3:
                    st.button("Delete", key=f"delete_{index}", use_container_width=True, on_click=on_delete_click, args=(index,))


    if st.session_state['page'] == 'home':
        home_page()

    elif st.session_state['page'] == 'edit_user':
        edit_user_page()

    elif st.session_state['page'] == 'add_new_user':
        add_new_user_page()

    elif st.session_state['page'] == 'calculator':
        calculator_page()

    elif st.session_state['page'] == 'machines':
        machines_page()

    elif st.session_state['page'] == 'record':
        record_page()

    elif st.session_state['page'] == 'record_analyze':
        record_analyze_page()

    elif st.session_state['page'] == 'edit_machine':
        edit_machine_page()

    elif st.session_state['page'] == 'leaderboard':
        leaderboard_page()

elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')