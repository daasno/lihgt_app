import streamlit_authenticator as stauth

hashed_passwords = stauth.Hasher(['XXXXX']).generate()
print(hashed_passwords)