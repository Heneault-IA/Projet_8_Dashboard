import streamlit as st
import plotly.graph_objects as go
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup


st.set_page_config(
    page_title="Dashboard Credit"
)

def make_prediction(file):
    # URL de l'API
    api_url = "https://home-credi-default-risk-2d75b983d33b.herokuapp.com"

    # Créer un objet FormData pour envoyer le fichier 
    files={'file': ("test.csv", file)}

    # Envoyer la requête à votre API Flask
    response = requests.post(f"{api_url}/predict", files=files)
    
    # Gérer la réponse JSON
    if response.status_code == 200:
        # Utilisez BeautifulSoup pour extraire les informations
        soup = BeautifulSoup(response.text, 'html.parser')

        # Sélectionnez toutes les lignes du tableau
        rows = soup.find_all('tr')
        
        # Initialisez des listes pour stocker les numéros et les états
        numeros = []
        ids = []
        probas = []
        etats = []

        # Parcourez les lignes (à partir de la deuxième ligne, car la première est l'en-tête)
        for row in rows[1:]:
            # Sélectionnez toutes les cellules de la ligne
            cells = row.find_all('td')
            
            # Récupérez les données des cellules
            numero = cells[0].get_text(strip=True)
            client_id = cells[1].get_text(strip=True)
            proba = cells[2].get_text(strip=True)
            etat = cells[3].get_text(strip=True)
            
            # Ajoutez les données aux listes
            numeros.append(numero)
            ids.append(client_id)
            probas.append(proba)
            etats.append(etat)

        return numeros, ids, probas, etats

    else:
        return {"error": f"Erreur de la requête : {response.status_code}"}

def make_gauge(probabilite, prediction):
    # Créer la jauge colorée
    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=probabilite,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"{prediction}"},
        gauge={
            'axis': {'range': [0, 1]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 0.25], 'color': "red"},
                {'range': [0.25, 0.47], 'color': "orange"},
                {'range': [0.47, 0.75], 'color': "yellow"},
                {'range': [0.75, 1], 'color': "green"},
            ]
        }
    ))

    return fig


def make_graph_feature_importance(features_client, features_global, feature_names, colorblind_mode=False):
    if colorblind_mode:
        color_client = "#1f78b4"
        color_global = "#ff7f00"
    else:
        color_client = "#1f78b4"
        color_global = "#4f9eff"
    
    fig = go.Figure()

    # Tracer les barres du premier tableau
    fig.add_trace(go.Bar(
        x=feature_names,
        y=features_client,
        name='Importance Client',
        marker_color=color_client
    ))

    # Tracer les barres du deuxième tableau
    fig.add_trace(go.Bar(
        x=feature_names,
        y=features_global,
        name='Importance Globale',
        marker_color=color_global
    ))

    # Mise en page du graphique
    fig.update_layout(
        barmode='group',  # Pour superposer les barres
        title='Importance des Principaux Critères de Prise de Décision',
        xaxis_title='Critères',
        yaxis_title='Valeurs',
        
    )

    return fig


def main():

    st.title("Dashboard de décision d'octroi du crédit")

    # Bouton pour activer/désactiver le mode daltonien
    colorblind_mode = st.checkbox("Activer le mode daltonien")

    df_samples = pd.read_csv("Data/sample_data.csv")

    clients_id = df_samples["SK_ID_CURR"]

    if 'client_id' not in st.session_state:
        st.session_state.client_id = None
    if 'classe' not in st.session_state:
        st.session_state.classe = None
    if 'feature_names' not in st.session_state:
        st.session_state.feaure_names = None

    client_id = st.selectbox("Choississez un client", clients_id)
    
    st.session_state.client_id = client_id

    st.write("Client choisit :", client_id)

    data = df_samples[df_samples["SK_ID_CURR"] == client_id]

    csv_data = data.to_csv(index=False)

    # Faire la prédiction en utilisant l'API
    nums, ids, probas, predictions = make_prediction(csv_data)

    proba = 100-float(probas[0])
    prediction = predictions[0]
    
    st.session_state.classe = prediction

    desc_gauge = st.checkbox("Activer la description textuelle de la gauge")

    if desc_gauge:
        description_gauge = f"Le crédit est {prediction}, car le score est de {proba} sur 47"
        st.markdown(description_gauge)
    else:
        fig = make_gauge((proba/100), prediction)

        # Afficher la jauge dans Streamlit
        st.plotly_chart(fig, use_container_width=True)


    if prediction== "Accepté":
        df_features_samples = pd.read_csv("Data/shap_samples_negative.csv")
    else:
        df_features_samples = pd.read_csv("Data/shap_samples_positive.csv")
    
    df_features = pd.read_csv("Data/shap_df.csv")

    features_client = df_features_samples[df_features_samples["SK_ID_CURR"] == client_id].copy()
    features_client.drop(columns=["SK_ID_CURR"], inplace=True)
    features_client = features_client.iloc[0]
    features_client.sort_values(ascending=False, inplace=True)

    features = features_client[:5]
    feature_names = list(features.index)

    st.session_state.feature_names = feature_names

    features_global = df_features.loc[0, feature_names]

    desc_importance = st.checkbox("Afficher un tableau")

    if desc_importance:

        # Création du DataFrame
        df_client = pd.DataFrame(features).transpose()
        df_client.index=["Valeurs Client"]
        df_global = pd.DataFrame(features_global).transpose()
        df_global.index=["Valeurs Globales"]
        concat_features = pd.concat([df_client, df_global])

        st.write("Importance des Principaux Critères de Prise de Décision")
        #Affichage du Tableau
        st.table(concat_features.transpose())

    else:

        # Création de la figure
        fig = make_graph_feature_importance(features, features_global, feature_names, colorblind_mode)

        # Afficher la figure dans Streamlit
        st.plotly_chart(fig)

if __name__ == "__main__":
    main()