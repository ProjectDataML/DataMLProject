import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Charger les données depuis la base de données
def load_data():
    engine = create_engine('sqlite:///airbnb_data.db')
    query = "SELECT * FROM merged_data"
    return pd.read_sql_query(query, engine)

def main():
    st.set_page_config(layout="wide")
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.title("Recommendation")

    # Chargement des données
    df = load_data()

if __name__ == "__main__":
    main()

