import streamlit as st
import pickle
from pathlib import Path
import streamlit as st
import yaml
from yaml import SafeLoader
import csv
import streamlit as st
import pandas as pd
import numpy as np
import math as mt
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from itertools import chain
# from statsmodels.tsa.arima_model import ARIMA
from pmdarima.arima import auto_arima
import pickle
from pathlib import Path
# import streamlit_authenticator as stauth
import yaml
from yaml import SafeLoader


def import_data():
    data_product=st.file_uploader(label='importer les données de stock et de produit')
    if data_product:
        Product=pd.read_csv(data_product)
        Product['IdPro']=(Product['id'].astype(str)+Product['id decl'].astype(str)).astype('Int64')
        Product.drop_duplicates('IdPro',inplace=True)
        # ======save the data====
        Product.to_csv('product.csv',index=False)

    data=st.file_uploader(label='importer les données des ventes')
    if data: 
        sales=pd.read_csv(data)
        try:
            sales.drop('Unnamed: 0',axis=1,inplace=True)
        except:
            pass
        condition=sales['ID'].isna()
        clean_data=sales[~condition]
        dirty_data=sales[condition]
        dirty_data['Vente']=dirty_data['Vente'].str.replace('"',"|")
        with open('month_sales.csv','w',newline='') as fout:
            writer = csv.writer(fout)
            writer.writerow(dirty_data.columns)
            for d in dirty_data['Vente'].values:
                writer.writerow([d])
        second=pd.read_csv('month_sales.csv',sep=',',quotechar='|',encoding="ISO-8859-1")
        sales=pd.concat([clean_data,second])
        sales['ID_Produit']=sales['ID_Produit'].astype('Int64')
        sales['Déclinaison ID']=sales['Déclinaison ID'].astype('Int64')
        sales['IdPro']=(sales['ID_Produit'].astype(str)+sales['Déclinaison ID'].astype(str)).astype('Int64')
        sales['Date de validation']=pd.to_datetime(sales['Date de validation'],format='%Y/%m/%d')
        # ===== save the data
        sales.to_csv('./Input/sales.csv',index=False)
    return True 


def  main_analysis():

    def clean_vente(row):
        temp_list=row.split('-')
        return '-'.join(temp_list[:3])

    @st.cache
    def get_data():
        # data preprocessing
        sales=pd.read_csv('sales.csv')
        sales['Date de validation']=pd.to_datetime(
                sales['Date de validation'].apply(clean_vente),
                format='%Y-%m-%d')
        sales.drop_duplicates(inplace=True)

        mycig=pd.read_csv('Product.csv')\
                        .drop_duplicates()

        
        filter_table=sales[["Point_de_vente","ID_Produit"]].merge(mycig[["Fournisseur","Catégorie","id","Marque"]],how='outer',left_on='ID_Produit',right_on='id')
        
        
        return mycig,sales,filter_table



    def multiselect(df,column):
        return st.sidebar.multiselect(column,options=df[column].dropna().unique())


    def timeSeries_manip(df):
        values=[]
        cols=[]
        for col in df:
            result=df[col]
            # changé to autoarima
            # model = sm.tsa.statespace.SARIMAX(result, order=(1, 1, 1)).fit()
            model=auto_arima(result, start_p=0, start_q=0)
            cols.append(col)
            values.append(
                    round(max(
                        0,
                        model.predict(start=len(result), end=len(result)+30).sum()
                        ))

                )
        return pd.DataFrame({'Catégorie':cols,'estimation':values})


    ##################################################################################################
    ##################################################################################################
    ############# read the data set from files ######################
    mycig,sales,filter_table=get_data()

    ############## Side bar  filters ##################

    fournisseur = multiselect(filter_table,'Fournisseur')
    if fournisseur:
        filter_table=filter_table[filter_table["Fournisseur"].isin(fournisseur)] 

    marque = multiselect(filter_table,"Marque")
    if marque:
        filter_table=filter_table[filter_table["Marque"].isin(marque)] 

    id_prod =multiselect(filter_table,"id")
    if id_prod:
        filter_table=filter_table[filter_table["id"].isin(id_prod)] 

    cat =multiselect(filter_table,"Catégorie")
    if cat:
        filter_table=filter_table[filter_table["Catégorie"].isin(cat)] 

    pdv =multiselect(filter_table,"Point_de_vente")
    if pdv:
        filter_table=filter_table[filter_table["Point_de_vente"].isin(pdv)] 


    begin_date = st.sidebar.date_input("Date 1",sales['Date de validation'].min())  
    end_date = st.sidebar.date_input("Date 2",sales['Date de validation'].max())    

    coissance = st.sidebar.number_input("Croissance in %") 
    temp_de_traittement = st.sidebar.number_input("Temps de traitement de commande", value=0)


    ######################  Main Bar  ######################################################

    st.title(":bar_chart: Mycif Analysis")
    st.markdown("---")

    # ============== show the pdv result in each stocks ===================
    # =======================================================================

    mycig=mycig[(mycig['Fournisseur'].isin(filter_table["Fournisseur"].unique()))
                & (mycig['Marque'].isin(filter_table["Marque"].unique()))
                & (mycig['Catégorie'].isin(filter_table["Catégorie"].unique()))
                & (mycig['id'].isin(filter_table["id"].unique()))
                ]
    sales=sales[
        (sales["Point_de_vente"].isin(filter_table["Point_de_vente"].unique())) &
        (sales["ID_Produit"].isin(filter_table["id"].unique())) 
    ]

    # =======================================================================
    col1,col2=st.columns((2,5))

    X=[];y=[]
    for el in filter_table["Point_de_vente"].dropna().unique():
                temp='Stock '+ str(el)
                try:
                    X.append(el)
                    y.append(mycig[temp].sum())
                except:
                    pass

    trace = go.Bar(x=X, y=y)
    layout = go.Layout(title='QUANTITE DE CHAQUE STOCK', xaxis=dict(title='Nom de Stock'), yaxis=dict(title='stoke'))
    fig = go.Figure(data=[trace], layout=layout)

    col1.markdown("<div style='margin:50% 0px;text-align:center'><h6>QUANTITE GLOBALE DES STOKE</h6><h1 style='font-size:50px'>{}</h1></div>".format(mycig['Stock'].sum()), unsafe_allow_html=True)
    col2.plotly_chart(fig)


    ###########################################################

    trace2 = go.Bar(x=mycig['Catégorie'], y=mycig['Stock'])
    layout2 = go.Layout(title='QUANTITE DE CHAQUE Produit', xaxis=dict(title='Nom de Stock'), yaxis=dict(title='stoke'))
    fig2 = go.Figure(data=[trace2], layout=layout2)
    st.plotly_chart(fig2)


    col1,col2=st.columns((2,3))

    df=sales.groupby(['Point_de_vente','Catégorie']).sum()['Quantité'].to_frame().reset_index().sort_values("Quantité",ascending=False)
    
    col1.text("les produits les vondus dans les store")
    col1.dataframe(df)

    timeSeries=sales.pivot_table(index='Date de validation',values='Quantité',aggfunc='sum',fill_value=0)
    timeSeries.columns=timeSeries.columns.str.strip()


    data=go.Scatter(x=timeSeries.index,y=timeSeries['Quantité'], mode='lines', name='Quantité')
    layout = go.Layout(title='Multiple Lines Plot')
    fig = go.Figure(data=data, layout=layout)
    col2.plotly_chart(fig)


    ####################################""
    st.markdown("<h4 style='font-size:20px;'>le nombre d\'élement vendus :</h4>",unsafe_allow_html=True)
    col1,col2=st.columns([4,2])
    col1.markdown("<h4 style='font-size:20px'>{} à </h4>".format(begin_date), unsafe_allow_html=True)
    col2.markdown("<h4 style='font-size:20px'>{} est</h4>".format(end_date), unsafe_allow_html=True)
    r=sales[(sales['Date de validation'].dt.date >= begin_date) & (sales['Date de validation'].dt.date <= end_date) ]
    st.markdown("<h1 style='font-size:50px;text-align:center'>{}</h1>".format(r['Quantité'].sum()), unsafe_allow_html=True)

    st.markdown("---")

    ################## time series plot  vent ########################
    col1,col2,col3=st.columns((1,1,3))

    button_1 = col1.button("Besoin Dans 30 jours", key="inline")
    button_2 = col2.button("Besoin Dans 60 jours", key="inline2")
    button_3 = col3.button("Besoin Dans 90 jours", key="inline3")

    if button_1:
        for stock in filter_table["Point_de_vente"].dropna().unique():
            time_data=sales[(sales["Point_de_vente"]==stock) ]
            timeSeries=time_data.pivot_table(index='Date de validation',columns='Catégorie',values='Quantité',aggfunc='sum',fill_value=0)
            prediction=timeSeries_manip(timeSeries)
            stock_charge=mycig.groupby('Catégorie',as_index=False).count()[['Catégorie','Stock {}'.format(stock),]]
            stock_charge['Stock {}'.format(stock)]=stock_charge['Stock {}'.format(stock)]
            result=prediction.merge(stock_charge,how='left',on="Catégorie")
            result['besoin']=(result['estimation']-result['Stock {}'.format(stock)]).apply(lambda x:max(x,0)).astype('Int32')
            besoin_day=result['estimation']/60
            result['stoke capacité']=(result['Stock {}'.format(stock)]//besoin_day)
            st.dataframe(result)
    ##############  ask saad ########################
    return True


st.set_page_config(page_title="Data analysis", page_icon=":bar_chart:", layout="wide")
page=st.sidebar.selectbox('selectioner la page: ',['main','import'])
st.sidebar.markdown('---')
if page=='main':
    main_analysis()
if page=='import':
    import_data()
    st.sidebar.markdown('Remarque: importer les corrects données pour chaque selection')
st.sidebar.markdown('---')