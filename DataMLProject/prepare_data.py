import pandas as pd
import os
from sqlalchemy import create_engine

def merge_and_insert_data(base_path='ml'):
    engine = create_engine('sqlite:///airbnb_data.db')
    final_df = pd.DataFrame()

    for city in os.listdir(base_path):
        city_path = os.path.join(base_path, city)
        if os.path.isdir(city_path):
            listings_path = os.path.join(city_path, 'listings.csv')
            reviews_path = os.path.join(city_path, 'reviews.csv')

            # Lire les fichiers CSV
            listings_df = pd.read_csv(listings_path)
            reviews_df = pd.read_csv(reviews_path)

            # Fusionner les DataFrames sur la colonne 'id'
            merged_df = pd.merge(listings_df, reviews_df, on='id')

            # Concaténer avec le DataFrame final
            final_df = pd.concat([final_df, merged_df], ignore_index=True)

    # Insérer le DataFrame final dans SQLite
    final_df.to_sql('merged_data', engine, if_exists='replace', index=False)

if __name__ == '__main__':
    merge_and_insert_data()
