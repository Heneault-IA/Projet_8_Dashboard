import numpy as np
import pandas as pd
import streamlit as st
import mlflow

df_sample = pd.read_csv("Data/sample_data.csv")
infos = pd.read_csv("Data/infos_data.csv")

clients_id = df_sample["SK_ID_CURR"]

client_id = st.selectbox("Choississez un client", clients_id)

data = infos.loc[infos["SK_ID_CURR"] == client_id, ["AGE", "NAME_CONTRACT_TYPE", "CODE_GENDER", "AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY"]]
data.columns = ["Age", "Contract", "Gender", "Income", "Credit", "Annuity"]
data.index= [client_id]
numeric_columns = data.select_dtypes(include=['float64']).columns
data[numeric_columns] = data[numeric_columns].applymap(lambda x: f'{x:.1f}')

st.write("Client choisit :", client_id)
st.table(data)