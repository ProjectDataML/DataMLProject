import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from sqlalchemy import create_engine
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import matplotlib.colors as colors
import numpy as np

# Charger les données depuis la base de données
def load_data():
    engine = create_engine('sqlite:///airbnb_data.db')
    query = "SELECT * FROM merged_data"
    return pd.read_sql_query(query, engine)

# Préparation des données pour le heatmap
def prepare_heatmap_data(df, by='neighbourhood_cleansed', column='room_type', values='price'):
    heatmap_data = df.groupby([by, column])[values].mean().unstack().fillna(0)
    return heatmap_data

# Fonction pour créer le heatmap
def create_heatmap(data):
    st.subheader("Heatmap des prix moyens par quartier et type de chambre")
    plt.figure(figsize=(12, 8))
    heatmap = sns.heatmap(data, cmap="YlGnBu")
    plt.title('Prix moyen par quartier et type de chambre')
    plt.xlabel('Type de chambre')
    plt.ylabel('Quartier')
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    st.pyplot()
    st.write("""
        Cette heatmap présente une cartographie détaillée des prix moyens selon les quartiers et les types de chambres sur Airbnb. Chaque intersection de quartier et de type de chambre est représentée par une couleur variant du vert clair au vert foncé, où les teintes plus sombres signalent des prix plus élevés. Cette visualisation permet de déceler les tendances de tarification dans différentes localités et selon la nature du logement. Les quartiers centraux et les sites touristiques, comme prévu, tendent à afficher des prix plus élevés. C'est le cas, par exemple, de "Mayfair" ou de certains quartiers parisiens. Le heatmap fournit un aperçu instantané de la stratégie de tarification et peut indiquer des zones de haute valeur pour les investisseurs immobiliers ou les hôtes cherchant à maximiser leurs revenus sur Airbnb. L'échelle de couleur utilisée est intuitive : plus la couleur est foncée, plus le prix moyen est élevé, ce qui permet même aux novices en données de saisir rapidement l'information clé.
        """)

# Fonction pour créer un treemap des villes avec les prix moyens des logements
def plot_city_treemap(df):
    st.subheader("Treemap des villes avec les prix moyens des logements")
    city_avg_price = df.groupby('city')['price'].mean().reset_index()
    fig = px.treemap(city_avg_price, path=['city'], values='price', title='Treemap des villes avec les prix moyens des logements')
    fig.data[0].hovertemplate = 'Ville: %{label}<br>Prix moyen: $%{value:.2f}'
    st.plotly_chart(fig, use_container_width=True)
    st.write("""
        Le treemap est une représentation proportionnelle où chaque ville est un bloc dont la taille et la couleur varient selon le prix moyen des logements. Les grandes sections sombres pour "Mayfair" et "Paris 16E" attirent immédiatement l'attention, suggérant non seulement des prix moyens élevés mais aussi probablement une concentration de logements haut de gamme ou une demande accrue. À l'inverse, des villes avec des blocs plus petits et plus clairs pourraient indiquer des marchés plus accessibles. Cette vue peut être extrêmement utile pour les voyageurs qui budgettent leur voyage, ainsi que pour les hôtes qui évaluent le positionnement de leur tarif par rapport aux autres villes. Le treemap est un excellent outil de comparaison rapide qui montre comment les prix varient significativement d'une ville à l'autre, et il met également en évidence la diversité des marchés immobiliers au sein du réseau Airbnb.
        """)

# Affichage du prix moyen par pays sous forme de bar chart
def plot_bar_chart(df):
    st.subheader("Prix moyens par pays")
    neighborhood_data = df.groupby('country')['price'].mean().sort_values()

    # Generate a color palette with distinct colors for each country
    colors = sns.color_palette('husl', len(neighborhood_data))

    # Plotting the bar chart with Seaborn for better styling
    plt.figure(figsize=(10, 6))
    sns.barplot(x=neighborhood_data.index, y=neighborhood_data.values, palette=colors)
    plt.xlabel('Pays')
    plt.ylabel('Prix moyen')
    plt.title('Prix moyens des locations Airbnb par pays')

    # Adding legend
    legend_labels = [f"{country}: {price:.2f} €" for country, price in
                     zip(neighborhood_data.index, neighborhood_data.values)]
    st.pyplot()
    st.write("""
    Le graphique montre les tarifs moyens des locations Airbnb dans quatre pays européens. Les Pays-Bas affichent les prix les plus élevés, suivis de près par le Royaume-Uni. La France se situe légèrement en dessous, tandis que l'Italie propose les prix les plus bas. Ces variations peuvent refléter la demande, la disponibilité des logements et les stratégies de tarification compétitives. Ces données sont cruciales pour les voyageurs dans la planification budgétaire et pour les hôtes dans l'ajustement de leur stratégie de tarification. Pour Airbnb, ces informations sont essentielles pour identifier les opportunités de marché et ajuster les stratégies de tarification.
    """)


# Affichage de la répartition des types de logements sous forme de diagramme circulaire
def plot_property_types_pie(df):
    st.subheader('Répartition des 6 grands types de logements')
    top_property_types = df['property_type'].value_counts().head(6)
    fig, ax = plt.subplots()
    ax.pie(top_property_types, labels=top_property_types.index, autopct='%1.1f%%')
    st.pyplot(fig)
    st.write("""
    Le diagramme circulaire concernant la "Répartition des 6 grands types de logements" révèle que la majorité des propriétés disponibles sont des "Entire rental unit", indiquant une forte préférence des utilisateurs d'Airbnb pour des logements entiers. Cela peut refléter le désir des voyageurs pour plus d'espace, de confort et de confidentialité. Les autres catégories, comme les "Entire lofts" et les "Private rooms in home", occupent des segments plus petits, ce qui implique que bien qu'il y ait une demande pour ces types de logements, elle est considérablement moindre comparée à celle pour des logements entiers. Cette information est utile pour les hôtes lors de la mise en marché de leur propriété et peut également indiquer où Airbnb pourrait étendre son offre pour satisfaire la demande.
    """)


# Affichage de la disponibilité moyenne des annonces au fil du temps sous forme de graphique linéaire
def plot_availability_over_time(df):
    st.subheader('Disponibilité moyenne des annonces au fil du temps')
    availability = df.groupby('last_scraped')['availability_365'].mean()
    plt.plot(availability.index, availability.values)
    plt.xlabel('Date')
    plt.ylabel('Disponibilité moyenne (sur 365 jours)')
    plt.title('Disponibilité moyenne des annonces au fil du temps')
    st.pyplot()
    st.write("""
    En ce qui concerne la "Disponibilité moyenne des annonces au fil du temps", nous voyons des fluctuations significatives tout au long de la période représentée. La chute nette de la disponibilité à mi-parcours suggère une période de forte occupation ou une restriction temporaire de l'offre. Le pic remarquable en décembre pourrait être attribué aux vacances de Noël, quand les propriétaires choisissent de mettre leurs biens sur le marché pour profiter de la demande saisonnière. Ces données sont essentielles pour les hôtes Airbnb qui peuvent vouloir ajuster leur disponibilité en prévision des variations saisonnières de la demande, et pour les voyageurs cherchant à comprendre les meilleures périodes pour trouver des options de logement disponibles.
    """)


# Affichage de la distribution des prix par type de logement sous forme de boîte à moustaches
def plot_price_distribution_by_room_type(df):
    st.subheader("Distribution des prix par type de logement")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(x='room_type', y='price', data=df, ax=ax)
    ax.set_title('Distribution des prix par type de logement')
    ax.set_xlabel('Type')
    ax.set_ylabel('Prix')
    ax.set_ylim(0, 500)
    st.pyplot(fig)
    st.write("""
        Les boxplots décrivent la distribution des prix par type de logement, révélant des différences substantielles dans les gammes de prix. Les appartements et maisons entiers présentent une grande variété de prix, tandis que les chambres partagées sont les moins chères mais aussi les moins variées en termes de prix. Cela indique que malgré la préférence pour des logements entiers, il existe un marché pour tous les types de logements, chacun attirant un segment différent de voyageurs.
        """)

# Affichage du prix moyen et de la note moyenne par Superhôte vs. Hôte
def plot_superhost_impact_on_price_and_ratings(df):
    st.subheader("Prix moyen et Note Moyenne: Superhôte vs. Hôte")
    fig, axs = plt.subplots(1, 2, figsize=(12, 5))
    sns.barplot(x='host_is_superhost', y='price', data=df, ax=axs[0])
    axs[0].set_title('Prix moyen : Superhôte vs. Hôte')
    axs[0].set_xlabel('Est Super Hôte')
    axs[0].set_ylabel('Prix Moyen')
    sns.barplot(x='host_is_superhost', y='review_scores_rating', data=df, ax=axs[1])
    axs[1].set_title('Note Moyenne: Superhôte vs. Hôte')
    axs[1].set_xlabel('Est Super Hôte')
    axs[1].set_ylabel('Note Moyenne')
    st.pyplot(fig)
    st.write("""
    Ce graphe montre que les Superhôtes ont tendance à avoir à la fois des prix et des notes moyennes plus élevés. Cela souligne l'association perçue entre la qualité de l'expérience client et le coût du logement. Les voyageurs semblent reconnaître et valoriser le statut de Superhôte, qui est attribué aux hôtes offrant un service exceptionnel, et sont disposés à payer plus pour cette assurance qualité. Cette distinction est cruciale pour les hôtes aspirant à devenir Superhôtes, car elle peut justifier des tarifs plus élevés et améliorer l'occupation.
    """)

# Affichage de la tendance mensuelle des reviews
def plot_availability_trends(df):
    st.subheader("Tendance par mois")
    df['last_review'] = pd.to_datetime(df['last_review'])
    df['review_month'] = df['last_review'].dt.month
    monthly_reviews = df.groupby('review_month').size().reset_index(name='count')

    # Generate a color palette with distinct colors for each month
    colors = sns.color_palette('husl', len(monthly_reviews))

    # Plotting the bar chart with Seaborn for better styling
    plt.figure(figsize=(10, 6))
    sns.barplot(x='review_month', y='count', data=monthly_reviews, palette=colors)
    plt.title('Tendance par mois')
    plt.xlabel('Mois')
    plt.ylabel('Nombre de reviews (pour mesurer activité)')
    plt.xticks(range(1, 13), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    st.pyplot()
    st.write("""
        L'évolution mensuelle de la disponibilité des logements Airbnb offre un aperçu des fluctuations observées, attribuables à divers facteurs tels que les saisons touristiques, les événements locaux et les réglementations sur les locations à court terme. Par exemple, les pics de disponibilité en fin d'année correspondent probablement à la demande accrue pendant les vacances. À l'inverse, les creux peuvent résulter de périodes de faible activité touristique ou de décisions des propriétaires de ne pas louer leurs biens. Comprendre ces tendances est essentiel pour les hôtes et Airbnb, leur permettant d'ajuster leurs stratégies pour maximiser les revenus et équilibrer l'offre et la demande. Ce graphique offre également des indications précieuses pour la planification future, aidant les hôtes à optimiser leur occupation et Airbnb à identifier des opportunités de croissance.
        """)


# Affichage du Cluster Map des prix
def plot_price_map_clustered(df):
    st.subheader("Cluster Map des prix")
    europe_center_lat, europe_center_lon = 54.5260, 15.2551
    map = folium.Map(location=[europe_center_lat, europe_center_lon], zoom_start=4)
    marker_cluster = MarkerCluster().add_to(map)
    min_price = np.percentile(df['price'], 5)
    max_price = np.percentile(df['price'], 95)
    norm = colors.Normalize(vmin=min_price, vmax=max_price)
    colormap = colors.LinearSegmentedColormap.from_list("price_colormap", ["green", "red"])
    for _, row in df.iterrows():
        clipped_price = np.clip(row['price'], min_price, max_price)
        normalized_price = norm(clipped_price)
        color = colors.to_hex(colormap(normalized_price))
        folium.CircleMarker(location=[row['latitude'], row['longitude']], radius=5, color=color, fill=True, fill_color=color, fill_opacity=0.7).add_to(marker_cluster)
    st_folium(map, width='100%', height=600)
    st.write("""
        Enfin, la cluster map des prix présente une perspective géographique sur la tarification des logements Airbnb. Les clusters de couleur sur la carte indiquent des concentrations de prix similaires. Cette vue permet aux utilisateurs de déterminer rapidement où les logements sont généralement plus coûteux ou plus abordables. Par exemple, des clusters de prix élevés dans les capitales ou les destinations touristiques majeures ne sont pas surprenants. En revanche, des clusters de prix bas pourraient indiquer des marchés moins connus ou émergents. Pour les analystes de données et les décideurs chez Airbnb, cette carte peut être utilisée pour identifier des opportunités de croissance ou pour ajuster les stratégies de tarification en fonction des conditions du marché local.
        """)


# Initialisation du dashboard
def main():
    st.set_page_config(layout="wide")
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.title("Tableau de bord des données Airbnb")

    # Chargement des données
    df = load_data()

    # Affichage des sections
    st.header("Analyse des données Airbnb")

    # Organiser les sections en colonnes
    col1, col2 = st.columns([1, 1])

    # Section 1: Carte avec heatmap
    with col1:
        heatmap_data = prepare_heatmap_data(df)
        create_heatmap(heatmap_data)

    # Section 2: Treemap des villes avec les prix moyens des logements
    with col2:
        plot_city_treemap(df)

    # Section 3: Prix moyens par pays
    with col1:
        plot_bar_chart(df)

    # Section 4: Disponibilité moyenne des annonces au fil du temps
    with col2:
        plot_availability_over_time(df)

    # Section 5: Répartition des types de logements
    with col1:
        plot_property_types_pie(df)

    # Section 6: Distribution des prix par type de logement
    with col2:
        plot_price_distribution_by_room_type(df)

    # Section 7: Impact des Superhôtes sur le prix et les notes
    with col1:
        plot_superhost_impact_on_price_and_ratings(df)

    # Section 8: Tendance par mois
    with col2:
        plot_availability_trends(df)

    # Section 9: Cluster Map des prix
    plot_price_map_clustered(df)

if __name__ == "__main__":
    main()
