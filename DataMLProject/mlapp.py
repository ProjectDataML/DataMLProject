import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Utiliser le cache de Streamlit pour charger les données
@st.cache(allow_output_mutation=True)
def load_data():
    engine = create_engine('sqlite:///airbnb_data.db')
    query = "SELECT * FROM merged_data"
    df = pd.read_sql_query(query, engine)
    df['price'] = df['price'].replace('[\$,]', '', regex=True).astype(float)
    return df

# Fonction pour obtenir des recommandations basées sur des filtres
def get_recommendations(df, filters):
    for feature, value in filters.items():
        if value is not None:  # si un filtre est défini, l'appliquer
            df = df[df[feature] == value]
    return df.nsmallest(5, 'price')  # exemple: les 5 logements les moins chers

def main():
    st.set_page_config(layout="wide")
    st.title("Système de recommandation Airbnb")

    # Chargement des données
    df = load_data()

    # Affichage d'un sous-ensemble des données pour éviter la surcharge
    if st.checkbox('Afficher les données brutes'):
        st.write('Données Airbnb :')
        st.dataframe(df.head(50))

    # Widgets pour les filtres
    city_options = df['city'].dropna().unique().tolist()  # Exclure les valeurs NaN/None
    city_options.sort()  # Trier les options
    city_filter = st.selectbox('Ville', ['All'] + city_options)
    property_type_filter = st.selectbox('Type de propriété', ['All'] + sorted(df['property_type'].unique().tolist()))
    price_min, price_max = st.slider('Prix par nuit', float(df['price'].min()), float(df['price'].max()), (50.0, 200.0))
    accommodates_filter = st.slider('Nombre de personnes', 1, int(df['accommodates'].max()), 2)

    # Mise à jour des filtres en fonction des widgets
    filters = {
        'city': None if city_filter == 'All' else city_filter,
        'property_type': None if property_type_filter == 'All' else property_type_filter,
        'accommodates': accommodates_filter,
    }

    # Bouton de recommandation
    if st.button('Recommander'):
        # Appliquer le filtre de prix séparément car il s'agit d'une plage de valeurs
        filtered_df = df[(df['price'] >= price_min) & (df['price'] <= price_max)]
        recommendations = get_recommendations(filtered_df, filters)
        st.write('Recommandations :')
        for i, row in recommendations.iterrows():
            st.image(row['picture_url'], width=300, caption=f"{row['name']} - {row['price']} par nuit")

if __name__ == "__main__":
    main()
