import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd


st.set_page_config(
    page_title="Dashboard Critères"
)

st.title("Dashboard Analyse des Critères")

# Bouton pour activer/désactiver le mode daltonien
colorblind_mode = st.checkbox("Activer le mode daltonien")

if colorblind_mode:
    color_client = "#1f78b4"
    color_global = "#ff7f00"
    color_classe_client = "#ff7f00"
    color_other_classe = "#984ea3"
else:
    color_client = "#7fb8da"
    color_global = "#0074cc"
    color_classe_client = "#0074cc"
    color_other_classe = "#001f3f"

client_id = st.session_state.client_id
classe = st.session_state.classe
feature_names = st.session_state.feature_names

if classe=="Accepté":
    target=0
    other=1
    other_classe="Refusé"
else:
    target=1
    other=0
    other_classe="Accpeté"

df_sample = pd.read_csv("Data/sample_data.csv")
df_global = pd.read_csv("Data/infos_glo.csv")
df_bivarie = pd.read_csv("Data/infos_glo_complete.csv")
df_classes = pd.read_csv("Data/infos_classes.csv")

client_sample = df_sample[df_sample["SK_ID_CURR"] == client_id].copy()

st.write(f"Id du Client : {client_id}, Acceptation : {classe}")

selected_features = st.multiselect("Choississez un à deux critères :", feature_names)

if len(selected_features) == 1:
    checkbox_classe = st.checkbox("Cliquez pour voir la séparation par classes")
    #Récupération des données
    if checkbox_classe:
        classe_client_value = df_classes.loc[df_classes["TARGET"]==target, selected_features].values[0]
        other_classe_value = df_classes.loc[df_classes["TARGET"]==other, selected_features].values[0]
    else:
        classe_client_value = df_global[selected_features].values[0]
        other_classe_value = [0]
        nom_classe = "Global"
    client_value = client_sample[selected_features].values[0]

    #Création du graphique avec plotly
    fig = go.Figure()

    # Ajouter les barres pour le client et la moyenne
    fig.add_trace(go.Bar(x=["Client"], 
                         y=[client_value[0]], 
                         name="Client",
                         marker_color=color_client
                         )
                )

    fig.add_trace(go.Bar(x=[nom_classe], 
                         y=[classe_client_value[0]], 
                         name=classe,
                         marker_color=color_classe_client
                         )
                )
    
    if checkbox_classe:
        fig.add_trace(go.Bar(x=[other_classe], 
                            y=[other_classe_value[0]], 
                            name=other_classe,
                            marker_color=color_other_classe
                            )
                    )
    
    if (client_value[0] < 0) & (classe_client_value[0] < 0) & (other_classe_value[0] <= 0): 
        max_range = min([client_value[0], classe_client_value[0], other_classe_value[0]]) - 0.01
    else:
        max_range = max([client_value[0], classe_client_value[0], other_classe_value[0]]) + 0.01

    fig.update_layout(
        barmode='group',  # Pour superposer les barres
        title=f'{selected_features[0]}',
        xaxis_title=f'Classe du client : {classe}',
        yaxis_title='Valeurs',
        yaxis=dict(range=[0, max_range])
    )

    # Afficher la figure dans Streamlit
    st.plotly_chart(fig)
    
    desc_unique_feature = st.checkbox("Afficher en Tableau")

    if desc_unique_feature:
        # Création du DataFrame
        df_client = pd.DataFrame(client_value).transpose()
        df_client.index=["Valeurs Client"]
        if checkbox_classe:
            df_classe = pd.DataFrame(classe_client_value).transpose()
            df_classe.index = [nom_classe]
            df_other = pd.DataFrame(other_classe_value).transpose()
            df_other.index = [other_classe]

            df_global = pd.concat([df_classe, df_other])
        else:

            df_global = pd.DataFrame(classe_client_value).transpose()
            df_global.index=["Valeurs Globales"]
        concat_features = pd.concat([df_client, df_global])
        concat_features.columns=[selected_features]

        st.write(f"{selected_features}")
        #Affichage du Tableau
        st.table(concat_features)

elif len(selected_features) == 2:
    checkbox_classe = st.checkbox("Cliquez pour voir la séparation par classes")
    #Récupération des données
    if checkbox_classe:
        classe_client_value = df_classes.loc[df_classes["TARGET"]==target, selected_features]
        other_classe_value = df_classes.loc[df_classes["TARGET"]==other, selected_features]
        # Rajouter deuxième classe
        nom_classe = classe
    else:
        global_values = df_classes[selected_features]
        nom_classe = "Global"
    #Récupération des données
    client_values = client_sample[selected_features]

    fig = go.Figure()

    if checkbox_classe:
        fig.add_trace(go.Scatter( 
                                x=classe_client_value[selected_features[0]], 
                                y=classe_client_value[selected_features[1]],
                                name=classe,
                                marker_color = color_classe_client,
                                text=classe))

        fig.add_trace(go.Scatter(
                                x=other_classe_value[selected_features[0]], 
                                y=other_classe_value[selected_features[1]],
                                name=other_classe,
                                marker_color = color_other_classe,
                                text=other_classe))

    else :
        # Ajouter les points pour global_values en bleu
        fig.add_trace(go.Scatter(
                                x=global_values[selected_features[0]], 
                                y=global_values[selected_features[1]],
                                name="Global",
                                marker_color = color_global))

    # Ajouter les points pour client_values en rouge
    fig.add_trace(go.Scatter(
                            x=client_values[selected_features[0]], 
                            y=client_values[selected_features[1]],
                            name="Client",
                            marker_symbol = 'x',
                            marker_size = 10,
                            marker_line_width = 2,
                            marker_color = color_client,
                            marker_line_color = color_client
                            ))    
    
    # Mise en page du graphique
    fig.update_traces(mode="markers")
    fig.update_layout(title=f'Analyse des critères choisis ({selected_features[0]} et {selected_features[1]})',
                      xaxis_title=f'{selected_features[0]}', 
                      yaxis_title=f'{selected_features[1]}',)

    # Afficher la figure dans Streamlit
    st.plotly_chart(fig)

    desc_features = st.checkbox("Afficher en Tableau")

    if desc_features:
        df_client = pd.DataFrame(client_values)
        df_client.index = ["Valeurs Client"]

        df_global = pd.DataFrame(global_values.mean()).transpose()
        df_global.index = ["Valeurs Globales"]

        df_concat = pd.concat([df_client, df_global])        

        st.write(f"Analyse des critères choisis ({selected_features[0]} et {selected_features[1]})")
        st.table(df_concat)

elif len(selected_features) >= 3:
    st.write("Trop de Features ont été sélectionnées")