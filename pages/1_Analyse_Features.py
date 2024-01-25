import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

client_id = st.session_state.client_id
feature_names = st.session_state.feature_names

df_sample = pd.read_csv("Data/sample_data.csv")
df_global = pd.read_csv("Data/infos_glo.csv")

client_sample = df_sample[df_sample["SK_ID_CURR"] == client_id].copy()

st.write(f"Id du Client : {client_id}")

selected_features = st.multiselect("Choississez une à deux features :", feature_names)

if len(selected_features) >= 3:
    st.write("Trop de Features ont été sélectionnées")
elif len(selected_features) == 1:
    #Récupération des données
    client_value = client_sample[selected_features].values[0]
    average_value = df_global[selected_features].values[0]

    #Création du graphique avec plotly
    fig = go.Figure()

    # Ajouter les barres pour le client et la moyenne
    fig.add_trace(go.Bar(x=["Client"], 
                         y=[client_value[0]], 
                         name="Client"
                         )
                )

    fig.add_trace(go.Bar(x=["Global"], 
                         y=[average_value[0]], 
                         name="Global"
                         )
                )
    
    # Mise en page du graphique
    if (client_value[0] > 0) & (average_value[0] > 0):
        max_range = max([client_value[0], average_value[0]]) + 0.01
    elif (client_value[0] < 0) & (average_value[0] < 0): 
        max_range = min([client_value[0], average_value[0]]) - 0.01
    else:
        max_range=1

    fig.update_layout(
        barmode='group',  # Pour superposer les barres
        title=f'{selected_features[0]}',
        xaxis_title='Features',
        yaxis_title='Valeurs',
        yaxis=dict(range=[0, max_range])
    )

    # Afficher la figure dans Streamlit
    st.plotly_chart(fig)

else:
    