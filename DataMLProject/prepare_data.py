import pandas as pd
import os
from sqlalchemy import create_engine

def clean_data(df):
    # Drop columns with more than 50% missing values
    threshold = len(df) * 0.5
    df = df.dropna(thresh=threshold, axis=1)

    # Drop rows with any remaining missing values
    df = df.dropna()

    # Removing duplicates
    df = df.drop_duplicates()

    # Convert 'host_since' to datetime
    df['host_since'] = pd.to_datetime(df['host_since'], errors='coerce')

    # Cleaning the 'price' column
    df['price'] = df['price'].str.replace(',', '').str.replace('$', '')
    df['price'] = pd.to_numeric(df['price'], errors='coerce')

    # Remove rows with non-numeric prices
    df = df.dropna(subset=['price'])

    # Split 'neighbourhood' into three new columns
    location_split = df['neighbourhood'].str.split(', ', expand=True)
    df['city'] = location_split[0]
    df['department'] = location_split[1]
    df['country'] = location_split[2]

    # Remove original 'neighbourhood' column
    df = df.drop('neighbourhood', axis=1)

    # Remove original 'amenities' column
    df = df.drop('amenities', axis=1)

    # Clean city names (remove case-sensitive duplicates)
    df['city'] = df['city'].replace(['París','France','Paris city', 'Île-de-France'], 'Paris')
    df['city'] = df['city'].replace(['Milano'], 'Milan')
    df['city'] = df['city'].replace(['Italy'], 'Lombardia')
    df['city'] = df['city'].replace(['UK','United Kingdom', 'England', 'Greater London', 'Central London'], 'London')
    df['city'] = df['city'].str.lower().str.strip().drop_duplicates().str.title()


    # Clean country names
    df['country'] = df['country'].replace({'FR': 'France'})
    df['country'] = df['country'].replace(['Central London', 'Greater London', 'London', 'England'], 'United Kingdom')
    df['country'] = df['country'].replace({'Lombardia': 'Italy'})

    # Convert date columns to datetime
    date_columns = ['last_scraped', 'calendar_last_scraped', 'first_review', 'last_review']
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%d-%m-%Y')

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
