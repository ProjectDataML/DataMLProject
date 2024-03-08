import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

def load_data():
    engine = create_engine('sqlite:///airbnb_data.db')
    query = "SELECT * FROM merged_data"
    return pd.read_sql_query(query, engine)

def main():
    st.title("Visualisation des données Airbnb fusionnées")

    df = load_data()
    if st.checkbox("Afficher les données"):
        st.write(df)

if __name__ == "__main__":
    main()
