import streamlit as st
from recommender import recommend_songs, main, search_songs_and_artists, getGenres, getGenre_tracks, get_artists_tracks
import spotify_conn as sp
from streamlit_option_menu import option_menu
from streamlit_card import card
import spotipy as spotify
import pandas as pd
import ast as ast

#st.title('Spotify 2.0')

@st.cache
def load_data():
    main()
    return get_artists_tracks().copy()

df_artists_tracks = load_data()

def increment_counter(track_id):
   st.session_state.key = track_id

# Initialize a session state for your app
if 'page' not in st.session_state:
    st.session_state.page = 'Home'
    st.session_state['key'] = None
    st.session_state['searchText'] = ""
# Set up your sidebar
sidebar = st.sidebar
sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Spotify_logo_without_text.svg/168px-Spotify_logo_without_text.svg.png")
with sidebar:
    choose = option_menu("Spotify 2.0", ["Home", "Browse", "Dev"], #, "Contact",
                         icons=['house', 'search', 'code'], #, 'person lines fill',
                         menu_icon="app-indicator", default_index=0,
                         styles={
                            "container": {"padding": "5!important", "background-color": "#272831"},
                            "icon": {"color": "white", "font-size": "25px"}, 
                            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
                            "nav-link-selected": {"background-color": "#02ab21"},
                        }
    ) 
    #if st.session exists, then we can use it to store the key of the song that was clicked on

    if  ('key' in st.session_state) & (st.session_state.key!=None):
        st.write("Sie haben zuletzt gehört:")
        st.session_state.url = f'<iframe src="https://open.spotify.com/embed/track/{st.session_state.key}" width="300" height="380" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>'
        #st.write(st.session_state.key)
        st.markdown(st.session_state.url, unsafe_allow_html=True)

#logo = Image.open(r'C:\Users\13525\Desktop\Insights_Bees_logo.png')
if choose == "Home":
    st.session_state.page = 'Home'
elif choose==('Browse'):
    st.session_state.page = 'Browse'
elif choose==('Dev'):
    st.session_state.page = 'Dev'

# Then, display your pages
if st.session_state.page == 'Home':
    st.header   ("Discover!")
    st.subheader("Top 10 Popular Songs:")
    filtered_df = df_artists_tracks.sort_values(by=['popularity'], ascending=False)
    rows = filtered_df.shape[0] if filtered_df.shape[0]<10  else 10
    for i in range(0,rows,2):
        col1, col2 = st.columns([1,1])  # Adjust the ratio based on your needs
        with col1:
            track_id = filtered_df.iloc[i]['tracks_id']
            print(track_id)
            st.markdown(f'<iframe src="https://open.spotify.com/embed/track/{track_id}" width="300" height="100" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>', unsafe_allow_html=True)
        with col2:
            i+=1
            track_id = filtered_df.iloc[i]['tracks_id']
            print(track_id)
            st.markdown(f'<iframe src="https://open.spotify.com/embed/track/{track_id}" width="300" height="100" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>', unsafe_allow_html=True)

    

elif st.session_state.page == 'Browse':
    st.subheader("Search for songs and artists")
    search = st.text_input('Search for a song or artist:')
    #st.session_state.key = None
    #st.write(st.session_state.key)
    if search:
        #st.write('You searched for:', search) #TODO auskommentieren
        #st.write(st.session_state['searchText']) #TODO auskommentieren
        if(st.session_state['searchText']!=search):
            st.session_state.key = None
            st.session_state['searchText'] = search
        matching_songs =search_songs_and_artists(search, df_artists_tracks)
        if matching_songs.empty:
            st.write('No matching songs/artists found.')
        else:
            if st.session_state.key == None:
                st.session_state.recommendations = matching_songs
                st.write('Matching Songs/Artists:')
            else:
                st.write('Recommended songs:')
                st.session_state.recommendations = recommend_songs(st.session_state.key, df_artists_tracks, 11)
            for i in range(len(st.session_state.recommendations)-1):
                #create columns with the names of the artists and songs and a button to play the song
                row = st.session_state.recommendations.iloc[i]
                track_name = row['tracks_name']
                artist_name = row['artists_name']
                track_id = row['tracks_id']
                #col1, col2, col3, col4 = st.columns([1,1,1,1])  # Adjust the ratio based on your needs
                col1, col2= st.columns([2,1])  # Adjust the ratio based on your needs
                with col1:
                    st.markdown(f'<iframe src="https://open.spotify.com/embed/track/{track_id}" width="300" height="100" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>', unsafe_allow_html=True)
                    #st.markdown( "<style>audio::-webkit-media-controls-enclosure {background-color:#1db954;}</style>", unsafe_allow_html=True)
                    #st.audio(row['preview_url'], format="audio/mp3")  
                with col2:
                    st.button('Similar tracks', key = "button"+track_id, on_click=increment_counter, args=(track_id, ))
            st.dataframe(df_artists_tracks[df_artists_tracks['tracks_id']==st.session_state.key])
            st.dataframe(st.session_state.recommendations)    
    else:
        st.session_state.recommendations = df_artists_tracks.sample(10)
        for i in range(len(st.session_state.recommendations)-1):
            #create columns with the names of the artists and songs and a button to play the song
            row = st.session_state.recommendations.iloc[i]
            track_name = row['tracks_name']
            artist_name = row['artists_name']
            track_id = row['tracks_id']
            #col1, col2, col3, col4 = st.columns([1,1,1,1])  # Adjust the ratio based on your needs
            col1, col2= st.columns([2,1])  # Adjust the ratio based on your needs
            with col1:
            #    st.write(track_name)
            #with col2:
            #    st.write(artist_name)
            #with col3: 
                st.markdown(f'<iframe src="https://open.spotify.com/embed/track/{track_id}" width="300" height="100" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>', unsafe_allow_html=True)
                #st.markdown( "<style>audio::-webkit-media-controls-enclosure {background-color:#1db954;}</style>", unsafe_allow_html=True)
                #st.audio(row['preview_url'], format="audio/mp3")  
            with col2:
                st.button('Similar tracks', key = "button"+track_id, on_click=increment_counter, args=(track_id, ))
        st.dataframe(df_artists_tracks[df_artists_tracks['tracks_id']==st.session_state.key])
        st.dataframe(st.session_state.recommendations)    

elif st.session_state.page == 'Dev':

    tab1, tab2, tab3= st.tabs(["SUche", "Song-Empfehlung", "Test-tab"])

    with tab1:
        # Search bar for song title
        search = st.text_input('Bitte geben Sie einen Songtitel ein:', '')

        # If a song title is entered, display a list of matching songs
        if search:
            matching_songs = search_songs_and_artists(search, df_artists_tracks)
            if matching_songs.empty:
                st.write('Keine übereinstimmenden Songs gefunden.')
            else:
                song_selection = st.selectbox('Bitte wählen Sie einen Song aus:', matching_songs['tracks_name'] + " - " + matching_songs['artists_name'])
                selected_song_id = matching_songs[(matching_songs['tracks_name'] + " - " + matching_songs['artists_name']) == song_selection]['tracks_id'].values[0]
                num_recommendations2 = st.slider('Anzahl der gewünschten Empfehlungen', 1, 10, 5, key=2)
                
                if st.button('Suche Song-Empfehlungen', key=4):
                    try:
                        recommendations2 = recommend_songs(selected_song_id, df_artists_tracks, num_recommendations2)
                        st.write(recommendations2)
                    except Exception as e:
                        st.write("Es gab einen Fehler bei der Song-Suche. Bitte versuchen Sie es erneut.")
                        st.write(str(e))

    with tab2:
        song_id = st.text_input('Bitte geben Sie eine Song-ID ein:', '', key=8)
        num_recommendations = st.slider('Anzahl der gewünschten Empfehlungen', 1, 10, 5, key=1)
        if st.button('Suche Song-Empfehlungen', key=3):
            #if song_id is in df_artists_tracks tracks_id
            if df_artists_tracks[df_artists_tracks['tracks_id'] == song_id].empty:
                st.write('Song-ID nicht gefunden.') 
            else:
                st.markdown(f'<iframe src="https://open.spotify.com/embed/track/{song_id}" width="300" height="380" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>', unsafe_allow_html=True)
                try:
                    recommendations = recommend_songs(song_id, df_artists_tracks, num_recommendations)
                    st.write(recommendations)
                except Exception as e:
                    st.write("Es gab einen Fehler bei der Song-Suche. Bitte versuchen Sie es erneut.")
                    st.write(str(e))

    with tab3:
        st.write("Tab für weiter Tests")
        selected_genre = st.selectbox('Select a genre:', getGenres(df_artists_tracks))
        filtered_df = df_artists_tracks[df_artists_tracks['genres'].apply(lambda x: selected_genre in ast.literal_eval(x))]
        st.dataframe(filtered_df)
        #top5 = df_artists_tracks.head(100)
        #st.dataframe(top5)
        rows = filtered_df.shape[0] if filtered_df.shape[0]<10  else 10
        for i in range(0,rows,2):
            col1, col2 = st.columns([1,1])  # Adjust the ratio based on your needs
            with col1:
                track_id = filtered_df.iloc[i]['tracks_id']
                print(track_id)
                st.markdown(f'<iframe src="https://open.spotify.com/embed/track/{track_id}" width="300" height="100" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>', unsafe_allow_html=True)
            with col2:
                i+=1
                track_id = filtered_df.iloc[i]['tracks_id']
                print(track_id)
                st.markdown(f'<iframe src="https://open.spotify.com/embed/track/{track_id}" width="300" height="100" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>', unsafe_allow_html=True)


    

