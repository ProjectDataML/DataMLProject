import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def load_data():
    engine = create_engine('sqlite:///airbnb_data.db')
    query = "SELECT * FROM merged_data"
    df = pd.read_sql_query(query, engine)
    df['price'] = df['price'].replace('[\$,]', '', regex=True).astype(int)
    df['original_price'] = df['price']  # Conserver les prix originaux dans une nouvelle colonne
    return df, engine

def perform_clustering(data, features_list, n_clusters=15):
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(data[features_list])
    kmeans = KMeans(n_clusters=n_clusters, random_state=0)
    clusters = kmeans.fit_predict(features_scaled)
    data['cluster'] = clusters
    return kmeans, scaler

def find_nearest_cluster(model, user_input, scaler, features_list):
    try:
        user_df = pd.DataFrame([user_input], columns=features_list)
        scaled_input = scaler.transform(user_df)
        cluster = model.predict(scaled_input)[0]
        return cluster
    except Exception as e:
        print(f"Error in find_nearest_cluster: {e}")
        return None

def save_rating(engine, listing_id, rating):
    with engine.connect() as conn:
        conn.execute(
            "INSERT INTO ratings (listing_id, rating) VALUES (?, ?) ON CONFLICT(listing_id) DO UPDATE SET rating = excluded.rating",
            (listing_id, rating))

def main():
    df, engine = load_data()
    st.title("Système de recommandation de logements")

    selected_country = st.selectbox('Dans quel pays cherchez-vous un logement ?', df['country'].dropna().unique(), key='country')
    selected_room_type = st.selectbox('Quel type de chambre cherchez-vous ?', df['room_type'].unique(), key='room_type')

    features_list = ['price', 'beds']
    filtered_df = df[(df['country'] == selected_country) & (df['room_type'] == selected_room_type)]
    kmeans, scaler = perform_clustering(filtered_df, features_list)

    user_inputs = {feature: st.number_input("Entrez votre valeur préférée pour " + feature, value=int(filtered_df[feature].mean())) for feature in features_list}

    if st.button("Trouver les meilleurs logements"):
        cluster = find_nearest_cluster(kmeans, list(user_inputs.values()), scaler, features_list)
        cluster_data = filtered_df[filtered_df['cluster'] == cluster]
        top_listings = cluster_data.nsmallest(10, 'original_price')

        st.subheader(f"Les 10 meilleurs logements dans le cluster {cluster + 1}")
        for index, row in top_listings.iterrows():
            with st.container():
                st.image(row['picture_url'], width=300)
                link = f"<a href='{row['listing_url']}' target='_blank'>{row['name']}</a> - ${row['original_price']} per night"
                st.markdown(link, unsafe_allow_html=True)
                rating = st.slider("Notez ce logement de 1 à 5 étoiles", 1, 5, value=3, step=1, key=f"rate_{row['id']}")
                if st.button("Enregistrer la note", key=f"save_{row['id']}"):
                    save_rating(engine, row['id'], rating)
                    st.success("Merci pour votre évaluation!")

if __name__ == "__main__":
    main()
