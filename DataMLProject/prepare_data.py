import pandas as pd
import os
from sqlalchemy import create_engine

def clean_data(df):
    # Handling missing values
    # Drop columns with more than 50% missing values
    threshold = len(df) * 0.5
    df = df.dropna(thresh=threshold, axis=1)

    # Drop rows with any remaining missing values
    df = df.dropna()

    # Removing duplicates
    df = df.drop_duplicates()

    # Correcting data types
    # Convert necessary columns to appropriate data types
    df['host_since'] = pd.to_datetime(df['host_since'], errors='coerce')

    # Cleaning the 'price' column
    df['price'] = df['price'].str.replace(',', '').str.replace('$', '')
    df['price'] = pd.to_numeric(df['price'], errors='coerce')

    # Remove rows with non-numeric prices
    df = df.dropna(subset=['price'])

    # Split de la colonne 'neighbourhood' en trois nouvelles colonnes
    location_split = df['neighbourhood'].str.split(', ', expand=True)
    df['city'] = location_split[0]
    df['department'] = location_split[1]
    df['country'] = location_split[2]

    # Suppression de la colonne 'neighbourhood' originale
    df = df.drop('neighbourhood', axis=1)

    # Suppression de la colonne 'amenities' originale
    df = df.drop('amenities', axis=1)

    # Nettoyage des noms de ville (suppression des doublons avec différence de casse)
    df['city'] = df['city'].str.lower().str.strip()
    df['city'] = df['city'].drop_duplicates()
    df['city'] = df['city'].str.title()

    # Nettoyage des noms de pays
    df['country'] = df['country'].replace({'FR': 'France'})

    return df

def merge_and_insert_data(base_path='ml'):
    engine = create_engine('sqlite:///airbnb_data.db')
    final_df = pd.DataFrame()

    for city in os.listdir(base_path):
        city_path = os.path.join(base_path, city)
        if os.path.isdir(city_path):
            listings_path = os.path.join(city_path, 'listings.csv')
            reviews_path = os.path.join(city_path, 'reviews.csv')

            # Read the CSV files
            listings_df = pd.read_csv(listings_path, encoding='utf-8')
            reviews_df = pd.read_csv(reviews_path, encoding='utf-8')

            # Merge DataFrames on the 'id' column
            merged_df = pd.merge(listings_df, reviews_df, on='id', how='left')

            # Clean the merged data
            merged_df = clean_data(merged_df)

            # Concatenate with the final DataFrame
            final_df = pd.concat([final_df, merged_df], ignore_index=True)

    # Insert the final DataFrame into SQLite
    final_df.to_sql('merged_data', engine, if_exists='replace', index=False)

if __name__ == '__main__':
    merge_and_insert_data()
