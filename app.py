import streamlit as st
from main import main, filter_films, search_film, search_trailer

def display_films(films):
    if films.empty:
        st.write("Désolé, nous n'avons pas trouvé de films qui correspondent à vos critères.")
    else:
        st.write(f"Nombre de films trouvés : {len(films)}")
        index = st.session_state.get('film_index', 0)
        if index >= len(films):
            st.write("Vous avez atteint la fin de la liste.")
        else:
            film = films.iloc[index]
            st.write(f"**{film['name']}** - Année : {film['year']}")
            st.image(film['poster_url'], width=300)
            st.write(f"Durée : {film['runtime']} minutes")
            trailer_url = search_trailer(film['name'], film['year'])
            if trailer_url:
                st.video(trailer_url)
            else:
                st.write("Bande annonce non disponible")
            st.write("---")

            if index < len(films) - 1:
                if st.button("Film suivant"):
                    st.session_state['film_index'] = index + 1
            else:
                st.write("Vous avez atteint la fin de la liste.")


def main_app():
    df, genres, années, durees = main()

    # Utilisateur choisit les genres
    genres_choisis = st.multiselect("Choisissez les genres de film que vous préférez (maximum 2 choix)", genres, max_selections=2)

    # Utilisateur choisit une fourchette d'années
    fourchette_choisie = st.selectbox("Choisissez une fourchette d'années de film que vous préférez:", années)
    année_debut, année_fin = map(int, fourchette_choisie.split('-'))

    # Utilisateur choisit une fourchette de durée
    duree_choisie = st.selectbox("Choisissez une fourchette de durée du film:", durees)

    # Filtrer le DataFrame pour obtenir les films qui correspondent aux critères de l'utilisateur
    films_filtrés = filter_films(df, genres_choisis, année_debut, année_fin, duree_choisie)

    # Moteur de recherche de film
    search_query = st.text_input("Rechercher un film par nom")
    if search_query:
        films_filtrés = search_film(df, search_query, année_debut, année_fin, films_filtrés['runtime'].min(), films_filtrés['runtime'].max())

    display_films(films_filtrés)

if __name__ == '__main__':
    main_app()
