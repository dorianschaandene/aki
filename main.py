import streamlit as st
import pandas as pd
import json
import numpy as np
from pytube import YouTube
from googleapiclient.discovery import build

# Fonction de chargement des données
@st.cache_data()
def load_data():
    with open('films2.json') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    # Effectuer les transformations nécessaires sur le DataFrame
    df['genre'] = df['genre'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
    df['genre'] = df['genre'].str.split(', ')
    df["ratingValue"].replace("", np.nan, inplace=True)
    df = df[df["ratingValue"].notna()]
    df["ratingValue"] = df["ratingValue"].astype(float)
    df["year"] = df["year"].str.extract('(\d{4})')
    df = df[df["year"].notna()]
    df["year"] = df["year"].astype(int)
    df["runtime"] = df["runtime"].str.extract('(\d+)').astype(float)
    return df

# Fonction de filtrage des films
def filter_films(df, genres_choisis, année_debut, année_fin, duree_choisie):
    if duree_choisie == "Films de moins d'une heure":
        duree_min, duree_max = 0, 60
    elif duree_choisie == "Films de moins d'une heure trente":
        duree_min, duree_max = 60, 90
    elif duree_choisie == "Films de moins de 2 h 00":
        duree_min, duree_max = 90, 120
    elif duree_choisie == "Films de moins de 2 h 30":
        duree_min, duree_max = 120, 150
    elif duree_choisie == "Films de 3 heures et plus":
        duree_min, duree_max = 180, float('inf')

    return df[
        (df['genre'].apply(lambda x: set(genres_choisis).issubset(set(x))))  # Vérifie si tous les genres sélectionnés sont présents dans les genres du film
        & (df['year'].between(année_debut, année_fin))  # Vérifie si l'année de sortie du film est dans la fourchette choisie
        & (df['runtime'] >= duree_min)  # Vérifie si la durée du film est supérieure ou égale à la durée minimale choisie
        & (df['runtime'] <= duree_max)  # Vérifie si la durée du film est inférieure ou égale à la durée maximale choisie
    ]

# Fonction de recherche de film
def search_film(df, query, année_debut, année_fin, duree_min, duree_max):
    filtered_df = df[
        (df['name'].str.lower() == query.lower())
        & (df['year'].between(année_debut, année_fin))
        & (df['runtime'] >= duree_min)
        & (df['runtime'] <= duree_max)
    ]
    return filtered_df

# Fonction de recherche de bande annonce sur YouTube
def search_trailer(query, year):
    api_key = 'AIzaSyDdghcFJshrHFoCIA7nVoPaVtM18xsk4rg'  # Remplacez par votre clé API YouTube Data v3
    youtube = build('youtube', 'v3', developerKey=api_key)

    search_query = f"{query} {year} trailer"
    request = youtube.search().list(
        part='snippet',
        q=search_query,
        maxResults=1
    )
    response = request.execute()

    if 'items' in response and len(response['items']) > 0:
        video_id = response['items'][0]['id']['videoId']
        return f"https://www.youtube.com/watch?v={video_id}"
    else:
        return None

def main():
    st.title("Qu'est-ce qu'on regarde ce soir?")

    # Chargement des données
    df = load_data()

    # Liste des genres
    genres = df['genre'].explode().unique().tolist()

    # Liste des fourchettes d'années
    années = list(range(int(df['year'].min()), int(df['year'].max()), 10))
    années = [f'{année}-{année + 9}' for année in années]

    # Liste des fourchettes de durée
    durees = [
        "Films de moins d'une heure",
        "Films de moins d'une heure trente",
        "Films de moins de 2 h 00",
        "Films de moins de 2 h 30",
        "Films de 3 heures et plus"
    ]

    return df, genres, années, durees


if __name__ == '__main__':
    main()
