import streamlit as st
import csv
import pandas as pd
def creatpage():
    data_product=st.file_uploader(label='importer les données de stock et de produit')
    if data_product:
        Product=pd.read_csv(data_product)
        Product['IdPro']=(Product['id'].astype(str)+Product['id decl'].astype(str)).astype('Int64')
        Product.drop_duplicates('IdPro',inplace=True)
        # ======save the data====
        Product.to_csv('data/product.csv',index=False)

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
        with open('data/month_sales.csv','w',newline='') as fout:
            writer = csv.writer(fout)
            writer.writerow(dirty_data.columns)
            for d in dirty_data['Vente'].values:
                writer.writerow([d])
        second=pd.read_csv('./data/month_sales.csv',sep=',',quotechar='|',encoding="ISO-8859-1")
        sales=pd.concat([clean_data,second])
        sales['ID_Produit']=sales['ID_Produit'].astype('Int64')
        sales['Déclinaison ID']=sales['Déclinaison ID'].astype('Int64')
        sales['IdPro']=(sales['ID_Produit'].astype(str)+sales['Déclinaison ID'].astype(str)).astype('Int64')
        sales['Date de validation']=pd.to_datetime(sales['Date de validation'],format='%Y/%m/%d')
        # ===== save the data
        sales.to_csv('./Input/sales.csv',index=False)
    return True 