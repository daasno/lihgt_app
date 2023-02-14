import streamlit as st
import pickle
from pathlib import Path
import streamlit_authenticator as stauth
import yaml
from yaml import SafeLoader
from views import main,import_data
# //////////////////////// user authentication 

st.set_page_config(page_title="Data analysis", page_icon=":bar_chart:", layout="wide")


with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')
elif authentication_status:
    page=st.sidebar.selectbox('selectioner la page: ',['main','import'])
    st.sidebar.markdown('---')
    if page=='main':
        main.creatpage()
    if page=='import':
        import_data.creatpage()
        st.sidebar.markdown('Remarque: importer les corrects données pour chaque selection')
    st.sidebar.markdown('---')
    authenticator.logout('Logout', 'sidebar')