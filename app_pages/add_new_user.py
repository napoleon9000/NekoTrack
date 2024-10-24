import streamlit as st
from backend import Manager

def app():
    env = st.secrets['ENV']['ENV']
    st.subheader("Add New User")
    mgr = Manager(env)
    phone_number = st.text_input("Phone Number")
    name = st.text_input("Name (Optional)")
    credits = st.number_input("Credits", min_value=0, value=0)
    notes = st.text_area("Notes", value="")
    if st.button("Save"):
        mgr.create_user(phone_number, name, credits, notes)
        st.success(f"User {phone_number} has been successfully created!")

if __name__ == "__main__":
    app()
