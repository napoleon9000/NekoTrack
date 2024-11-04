import streamlit as st
from backend.user_mgr import Manager
from utils import redemption_history_to_df

def app():

    st.subheader("Edit User")
    env = st.secrets['ENV']['ENV']
    mgr = Manager(env)
    if st.session_state['selected_user'] is not None:
        phone_number = st.session_state['selected_user']['phone_number']
        phone_number = st.text_input("Phone Number", value=phone_number)
    else:   
        phone_number = st.text_input("Enter Phone Number to Search")
    if phone_number:
        user = mgr.find_user(phone_number)
        if user:
            name = st.text_input("Name", value=user.name)
            credits = st.number_input("💳Credits", value=user.credits)
            tokens = st.number_input("💰Tokens", value=user.tokens)
            notes = st.text_area("Notes", value=user.notes)
            if st.button("Save"):
                mgr.edit_user(phone_number, name=name, credits=credits, tokens=tokens, notes=notes)
                st.success(f"User {phone_number} has been successfully updated!")
            st.markdown("---")

        else:
            st.error("User not found")

if __name__ == "__main__":
    app()
    st.write(st.session_state)