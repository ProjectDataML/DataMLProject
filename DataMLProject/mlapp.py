import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report

# Utiliser le cache de Streamlit pour charger les données
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

    # Supprimer les colonnes non nécessaires ou redondantes
    columns_to_drop = ['id', 'listing_url', 'scrape_id', 'last_scraped', 'name',
                       'neighborhood_overview', 'picture_url', 'host_id', 'host_url', 'host_name',
                       'host_since', 'host_location', 'host_about', 'host_thumbnail_url',
                       'host_picture_url', 'calendar_last_scraped']
    df.drop(columns=columns_to_drop, inplace=True)

    # Gérer les valeurs manquantes
    # Remplacer les valeurs manquantes numériques par la médiane
    num_imputer = SimpleImputer(strategy='median')

    # Pour les colonnes catégorielles, remplacer les valeurs manquantes par le plus fréquent
    cat_imputer = SimpleImputer(strategy='most_frequent')

    # Sélection des caractéristiques numériques et catégorielles
    num_features = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    cat_features = df.select_dtypes(include=['object']).columns.tolist()

    # Retirer la cible s'il est dans les caractéristiques
    num_features.remove('number_of_reviews')

    # Prétraitement avec ColumnTransformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', num_imputer, num_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), cat_features)
        ])

    # Créer la cible pour la classification
    df['is_popular'] = (df['number_of_reviews'] > 50).astype(int)

    # Séparer les caractéristiques et la cible
    X = df.drop('is_popular', axis=1)
    y = df['is_popular']

    # Division du dataset en ensemble d'entraînement et de test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Création du pipeline de prétraitement et du modèle
    pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                               ('classifier', RandomForestClassifier(random_state=42))])

    # Entraînement du modèle
    pipeline.fit(X_train, y_train)

    # Le modèle est maintenant prêt et peut être utilisé pour faire des prédictions
    y_pred = pipeline.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy:.4f}")


    report = classification_report(y_test, y_pred)
    print("\nClassification Report:\n", report)

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
