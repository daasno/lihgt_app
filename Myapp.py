import streamlit as st
import pickle
from pathlib import Path
import streamlit as st
import yaml
from yaml import SafeLoader
import main
import import_data

if __name__ == '__main__':
    st.set_page_config(page_title="Data analysis", page_icon=":bar_chart:", layout="wide")
    page=st.sidebar.selectbox('selectioner la page: ',['main','import'])
    st.sidebar.markdown('---')
    if page=='main':
        main.creatpage()
    if page=='import':
        import_data.creatpage()
        st.sidebar.markdown('Remarque: importer les corrects données pour chaque selection')
    st.sidebar.markdown('---')