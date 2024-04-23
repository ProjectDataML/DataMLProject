import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np

# Chargement des données
def load_data():
    engine = create_engine('sqlite:///airbnb_data.db')
    query = "SELECT * FROM merged_data"
    df = pd.read_sql_query(query, engine)
    df['price'] = df['price'].replace('[\$,]', '', regex=True).astype(float)
    return df

# Fonction pour le clustering
def perform_clustering(data, features_list, n_clusters=5):
    features = data[features_list]
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    kmeans = KMeans(n_clusters=n_clusters, random_state=0)
    clusters = kmeans.fit_predict(features_scaled)
    data['cluster'] = clusters
    return kmeans

# Trouver le cluster le plus proche
def find_nearest_cluster(model, user_input, scaler):
    scaled_input = scaler.transform([user_input])
    cluster = model.predict(scaled_input)[0]
    return cluster

def main():
    df = load_data()

    # Configuration de l'interface utilisateur pour la sélection des caractéristiques de clustering
    st.title("Système de recommandation de logements")
    n_clusters = st.sidebar.slider("Nombre de clusters", min_value=2, max_value=10, value=5)
    features_list = st.sidebar.multiselect("Sélectionnez les caractéristiques pour le clustering",
                                           options=['latitude', 'longitude', 'price', 'accommodates', 'beds'],
                                           default=['price', 'beds'])

    # Clustering des données
    scaler = StandardScaler()
    df[features_list] = scaler.fit_transform(df[features_list])
    kmeans = perform_clustering(df, features_list, n_clusters)

    # Formulaire de saisie des préférences de l'utilisateur
    st.header("Entrez vos préférences")
    user_inputs = []
    for feature in features_list:
        user_input = st.number_input(f"Saisissez votre valeur préférée pour {feature}", value=float(df[feature].mean()))
        user_inputs.append(user_input)

    if st.button("Trouver les meilleurs logements"):
        cluster = find_nearest_cluster(kmeans, user_inputs, scaler)
        cluster_data = df[df['cluster'] == cluster]
        top_listings = cluster_data.nlargest(10, 'price')

        st.subheader(f"Les 10 meilleurs logements dans le cluster {cluster + 1}")
        for index, row in top_listings.iterrows():
            st.image(row['picture_url'], width=300, caption=f"{row['name']} - ${row['price']} per night")

if __name__ == "__main__":
    main()
