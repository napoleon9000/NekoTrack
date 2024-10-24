import streamlit as st
from backend import Manager
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
            name = st.text_input("Name", value=user[0]['name'])
            credits = st.number_input("Credits", value=user[0]['credits'])
            notes = st.text_area("Notes", value=user[0]['notes'])
            if st.button("Save"):
                mgr.edit_user(phone_number, name=name, credits=credits, notes=notes)
                st.success(f"User {phone_number} has been successfully updated!")
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col2:
                st.markdown("##### Redemption History")
                st.dataframe(redemption_history_to_df(user[0]['redemption_history']))
            with col1:
                # add redeem rewards
                st.markdown("##### Redeem Rewards")
                item = st.text_input("Item Name")
                credits = st.number_input("Item Value", min_value=0, step=1)
                if st.button("Redeem"):
                    try:
                        mgr.record_redemption(phone_number, item, credits)
                        st.success(f"User {phone_number} has been successfully updated!")
                    except ValueError as e:
                        st.error(e)

        else:
            st.error("User not found")

if __name__ == "__main__":
    app()
    st.write(st.session_state)