import streamlit as st

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


def app():
    col1, col2 = st.columns([3, 1])
    with col1:
        if env == 'dev':
            st.title(f"NekoTrack - {env}")
        else:
            st.title(f"NekoTrack")
    with col2:
        col3, col4 = st.columns([1, 1])
        with col3:  
            st.write(f'Welcome *{name}*')
        
    st.markdown("---")

