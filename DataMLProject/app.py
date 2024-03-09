import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from sqlalchemy import create_engine

# Charger les données depuis la base de données
def load_data():
    engine = create_engine('sqlite:///airbnb_data.db')
    query = "SELECT * FROM merged_data"
    return pd.read_sql_query(query, engine)

# Bar Chart Example
def plot_bar_chart(df):
    neighborhood_data = df.groupby('country')['price'].mean().sort_values()
    st.bar_chart(neighborhood_data)

# Fonction pour créer le diagramme circulaire des types de logements
def plot_property_types_pie(df):
    # Sélectionner les 6 grands types de logements
    top_property_types = df['property_type'].value_counts().head(6)
    fig, ax = plt.subplots()
    ax.pie(top_property_types, labels=top_property_types.index, autopct='%1.1f%%')
    ax.set_title('Répartition des 6 grands types de logements')
    st.pyplot(fig)

# Préparation des données pour le heatmap
def prepare_heatmap_data(df, by='neighbourhood_cleansed', column='room_type', values='price'):
    # Calculer le prix moyen par catégorie
    heatmap_data = df.groupby([by, column])[values].mean().unstack()
    return heatmap_data

# Création du heatmap
def create_heatmap(data):
    plt.figure(figsize=(12, 8))
    heatmap = sns.heatmap(data, cmap="YlGnBu")
    plt.title('Prix moyen par quartier et type de chambre')
    plt.xlabel('Type de chambre')
    plt.ylabel('Quartier')
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    st.pyplot()

# Fonction pour créer le graphique linéaire de disponibilité au fil du temps
def plot_availability_over_time(df):
    availability = df.groupby('last_scraped')['availability_365'].mean()
    plt.plot(availability.index, availability.values)
    plt.xlabel('Date')
    plt.ylabel('Disponibilité moyenne (sur 365 jours)')
    plt.title('Disponibilité moyenne des annonces au fil du temps')
    st.pyplot()

# Fonction pour créer un treemap des villes avec les prix moyens des logements
def plot_city_treemap(df):
    city_avg_price = df.groupby('city')['price'].mean().reset_index()
    fig = px.treemap(city_avg_price, path=['city'], values='price', title='Treemap des villes avec les prix moyens des logements')
    fig.data[0].hovertemplate = 'Ville: %{label}<br>Prix moyen: $%{value:.2f}'
    st.plotly_chart(fig)

# Initialisation du dashboard
def main():
    st.title("Tableau de bord des données Airbnb")
    st.set_option('deprecation.showPyplotGlobalUse', False)

    # Chargement et nettoyage des données
    df = load_data()

    # Affichage des données brutes
    st.subheader("Données Airbnb fusionnées")
    st.dataframe(df)

    # Statistiques descriptives
    st.write("Résumé Statistique")
    st.write(df.describe())

    # Statistiques interactives
    st.subheader("Analyse interactive des prix")
    max_price = st.slider("Sélectionnez le prix maximum", int(df['price'].min()), int(df['price'].max()), 100)
    df_price_filtered = df[df['price'] <= max_price]
    st.map(df_price_filtered[['latitude', 'longitude']])

    # Bar chart
    st.header("Prix moyens par pays")
    plot_bar_chart(df)

    # Afficher le diagramme circulaire des types de logements
    st.subheader('Répartition des 6 grands types de logements')
    plot_property_types_pie(df)

    # Création et affichage du heatmap
    st.subheader("Heatmap des prix moyens par quartier et type de chambre")
    heatmap_data = prepare_heatmap_data(df)
    create_heatmap(heatmap_data)

    # Afficher le graphique linéaire de disponibilité au fil du temps
    st.subheader('Disponibilité moyenne des annonces au fil du temps')
    plot_availability_over_time(df)

    # Afficher le treemap des villes
    st.subheader("Treemap des villes avec les prix moyens des logements")
    plot_city_treemap(df)

# Exécution de l'application
if __name__ == "__main__":
    main()
