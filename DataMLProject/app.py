import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from io import BytesIO


def load_data():
    engine = create_engine('sqlite:///airbnb_data.db')
    query = "SELECT * FROM merged_data"
    return pd.read_sql_query(query, engine)

# Fonction pour convertir le DataFrame en objet CSV
def convert_df_to_csv(df):
    csv_bytes = BytesIO()
    df.to_csv(csv_bytes, index=False)
    csv_bytes.seek(0)
    return csv_bytes

def main():
    st.title("Visualisation des données Airbnb fusionnées")

    df = load_data()

    st.write("Tableau")
    st.dataframe(df)

    st.write(df.size)

    st.write("Résumé Statistique")
    st.write(df.describe())

    # Filtre par ville
    city = st.sidebar.multiselect("Choisissez la ville:", options=df['city'].unique())

    # Filtre de données en fonction de la ville sélectionnée
    if city:
        df = df[df['city'].isin(city)]

    # Histogramme des prix
    st.subheader("Distribution des prix")
    fig, ax = plt.subplots()
    ax.hist(df['price'], bins=30, range=(0, 1000))
    st.pyplot(fig)

    # Visualisation de la disponibilité
    st.subheader("Disponibilité des logements")
    availability_counts = df['availability_365'].value_counts()
    st.bar_chart(availability_counts)

if __name__ == "__main__":
    main()