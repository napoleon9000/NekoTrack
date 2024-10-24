import streamlit_authenticator as stauth

input_string = "nekoneko"

hashed_passwords = stauth.Hasher([input_string]).generate()[0]

print(hashed_passwords)