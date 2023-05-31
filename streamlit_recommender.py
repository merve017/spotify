import streamlit as st
from recommender import recommend_songs, init_file, matchingSongs, recommend_songsKnn

st.title('Song Recommender')

init_file()

tab1, tab2, tab3= st.tabs(["Knn_only", "mixed", "test2"])


with tab1:
    song_id = st.text_input('Bitte geben Sie eine Song-ID ein:', '', key=7)
    num_recommendations = st.slider('Anzahl der gewünschten Empfehlungen', 1, 10, 5, key=6)

    if st.button('Suche Song-Empfehlungen', key=5):
        if song_id:
            try:
                recommendations = recommend_songsKnn(song_id, num_recommendations)
                st.write(recommendations)
            except Exception as e:
                st.write("Es gab einen Fehler bei der Song-Suche. Bitte versuchen Sie es erneut.")
                st.write(str(e))
        else:
            st.write('Bitte geben Sie eine Song-ID ein.')


with tab2:
    song_id = st.text_input('Bitte geben Sie eine Song-ID ein:', '', key=8)
    num_recommendations = st.slider('Anzahl der gewünschten Empfehlungen', 1, 10, 5, key=1)

    if st.button('Suche Song-Empfehlungen', key=3):
        if song_id:
            try:
                recommendations = recommend_songs(song_id, num_recommendations)
                st.write(recommendations)
            except Exception as e:
                st.write("Es gab einen Fehler bei der Song-Suche. Bitte versuchen Sie es erneut.")
                st.write(str(e))
        else:
            st.write('Bitte geben Sie eine Song-ID ein.')

with tab3:
    # Search bar for song title
    song_title_search = st.text_input('Bitte geben Sie einen Songtitel ein:', '')

    # If a song title is entered, display a list of matching songs
    if song_title_search:
        matching_songs = matchingSongs(song_title_search)
        if matching_songs.empty:
            st.write('Keine übereinstimmenden Songs gefunden.')
        else:
            song_selection = st.selectbox('Bitte wählen Sie einen Song aus:', matching_songs['tracks_name'])
            selected_song_id = matching_songs[matching_songs['tracks_name'] == song_selection]['tracks_id'].values[0]
            num_recommendations2 = st.slider('Anzahl der gewünschten Empfehlungen', 1, 10, 5, key=2)
            
            if st.button('Suche Song-Empfehlungen', key=4):
                try:
                    recommendations2 = recommend_songs(selected_song_id, num_recommendations2)
                    st.write(recommendations2)
                except Exception as e:
                    st.write("Es gab einen Fehler bei der Song-Suche. Bitte versuchen Sie es erneut.")
                    st.write(str(e))


