import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import re
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import ast as ast



# Read the data from the CSV file
global df_artists_tracks
df_artists_tracks = None
global df_artists_tracks_orig
df_artists_tracks_orig = None

METRIC_FEATURES = ['acousticness', 'danceability', 'duration_ms', 'energy', 'instrumentalness', 'key', 'liveness', 
                   'loudness', 'mode', 'popularity', 'speechiness', 'tempo', 'time_signature', 'valence'
                   ,'artist_popularity', 'followers'
                   ]

#TODO: only relevant for jupyter notebook
def main2():
    global df_artists_tracks, df_artists_tracks_orig
    df_artists, df_tracks = read_data()
    df_artists_tracks, df_artists_tracks_orig = transform_data(df_artists, df_tracks)
    df_artists_tracks = drop_columns(df_artists_tracks)

def main():
    global df_artists_tracks, df_artists_tracks_orig
    df_artists, df_tracks = read_data()
    df_artists_tracks, df_artists_tracks_orig = transform_data(df_artists, df_tracks)
    df_artists_tracks = drop_columns(df_artists_tracks)
    df_artists_tracks = build_recommendation_genre(df_artists_tracks)
    df_artists_tracks = build_recommendation_metric(df_artists_tracks)
    
def read_data():
    df_artists = pd.read_csv('data/spotify_artists.csv', sep=',') 
    df_tracks = pd.read_csv('data/spotify_tracks.csv', sep=',')   
    return df_artists, df_tracks 
     
def transform_data(df_artists, df_tracks):
    df_tracks['artists_id'] = df_tracks['artists_id'].str.strip("[]").str.replace("'","")
    df_tracks.rename(columns={'id':'tracks_id', 'name':'tracks_name'}, inplace=True)
    df_artists['id'] = df_artists['id'].str.strip("[]").str.replace("'","")
    df_artists.rename(columns={'name':'artists_name'}, inplace=True)
    df_artists_tracks = pd.merge(df_tracks, df_artists, left_on='artists_id', right_on='id', how='inner')
    df_artists_tracks_orig = df_artists_tracks.copy()
    return df_artists_tracks, df_artists_tracks_orig

def drop_columns(df_artists_tracks):
    columns_to_keep = ['acousticness', 'danceability', 'duration_ms', 'energy', 'instrumentalness', 'key', 'liveness', 
                       'loudness', 'mode', 'popularity', 'speechiness', 'tempo', 'time_signature', 'valence',
                       'artist_popularity', 'followers', 
                       'genres', 'tracks_id', 'tracks_name', 'artists_id', 
                       'artists_name', 'album_id', 'uri', 'preview_url', 'country', 'lyrics']
    df_artists_tracks = df_artists_tracks[columns_to_keep]
    return df_artists_tracks

def build_recommendation_metric(df_artists_tracks):
    metric_pipeline = Pipeline(steps=[
        ('scaler', MinMaxScaler()),
        ('dbscan', DBSCAN(eps=0.5, min_samples=7))
    ])
    metric_features = METRIC_FEATURES #+ ['genre_cluster']
    # Fit and transform the data
    df_artists_tracks['metric_cluster'] = metric_pipeline.fit_predict(df_artists_tracks[metric_features])
    return df_artists_tracks
    
def recommend_songs_knn(df, song_id, n_recommendations, priority_factor=5):
    print(song_id)
    additional_features = ['genre_cluster', 'metric_cluster']
    metric_features = METRIC_FEATURES + additional_features

    #drop 'genre_cluster' and 'metric_cluster' from the metric_features

    #metric_features = [feature for feature in metric_features if feature not in additional_features]


    # filter the dataframe on the genre_cluster of the song_id
    #df_scaled = df[df['genre_cluster'] == df[df['tracks_id'] == song_id]['genre_cluster'].values[0]].copy()
    df_scaled = df.copy()
    """df_scaled[additional_features] *= priority_factor

    pipeline = Pipeline([
        ('scaler', StandardScaler()),  # Normalize the data
        ('knn', NearestNeighbors(n_neighbors=n_recommendations, metric='cosine'))
    ])"""


        # Scale all metric features
    scaler = StandardScaler()
    df_scaled[metric_features] = scaler.fit_transform(df_scaled[metric_features])

    # Apply priority factors to genre_cluster and metric_cluster
    df_scaled['genre_cluster'] *= priority_factor
    df_scaled['metric_cluster'] *= priority_factor

    # Define the pipeline
    pipeline = Pipeline([
        ('knn', NearestNeighbors(n_neighbors=n_recommendations, metric='cosine'))
    ])

    pipeline.fit(df_scaled[metric_features])
    
    song_features = df_scaled[df_scaled['tracks_id'] == song_id][metric_features]
    #song_features_scaled = pipeline.named_steps['scaler'].transform(song_features)
    song_features_scaled = song_features
    #print(song_features)
    #song_row = df_scaled[df_scaled['tracks_id'] == song_id]

    distances, indices = pipeline.named_steps['knn'].kneighbors(song_features_scaled)

    song_list = [df_scaled.iloc[indices.flatten()[i]]['tracks_id'] 
        for i in range(1, len(distances.flatten()))
        if print(f'{i}: {df.iloc[indices.flatten()[i]]["tracks_id"]}, with distance of {distances.flatten()[i]}') is None]

    return df[df['tracks_id'].isin(song_list)]
        
    

def recommend_songs(song_id, df, n_recommendations):
    return recommend_songs_knn(df, song_id, n_recommendations)

def search_songs_and_artists(search, df):
    search = search.upper()
    #put artists name and tracks_name together and look for the search string
    #create new data frame df_new with the new column artists name and tracks name
    df_new = df.copy()
    df_new['artists_tracks_name'] = df_new['artists_name'] + ' ' + df_new['tracks_name']
    df_new['artists_tracks_name'] = df_new['artists_tracks_name'].str.upper()
    tracks_match = df_new[df_new['artists_tracks_name'].str.contains(search, case=False)]
    #tracks_match = df_new[df['tracks_name'].str.contains(search, case=False)]
    return tracks_match.drop_duplicates()

def getGenres(df):
    unique_genres = df['genres'].apply(ast.literal_eval).explode().unique()

    cleaned_genres = []
    for genre in unique_genres:
        if not genre:  # Check if genre is empty
            genre = 'Unknown'
        elif isinstance(genre, list):  # Check if genre is a list
            genre = ', '.join(genre)  # Convert list to string
        cleaned_genres.append(genre)
    
    # Remove duplicates
    cleaned_genres = list(set(cleaned_genres))
    return cleaned_genres

def getGenre_tracks(genre):
    global df_artists_tracks_orig
    return df_artists_tracks_orig[df_artists_tracks_orig['genres'].str.contains(genre)]['tracks_name'].sample(1)

def get_artists_tracks():
    global df_artists_tracks
    return df_artists_tracks    

def build_recommendation_genre(df_artists_tracks):
    stop_words=stopwords.words('english')
    lemmatizer = WordNetLemmatizer()
    def preprocess_text(text):
        text = re.sub(r'\[|\]|\'|,', '', text)    
        text = text.lower()
        text = text.replace('hip hop', 'hip-hop')
        text = text.replace('r&b', 'r-n-b')
        text = text.replace('death metal', 'death-metal')
        words = text.split()    
        words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]
        text = ' '.join(words)
        return text
    
    df_artists_tracks['genres_new'] = df_artists_tracks['genres'].apply(preprocess_text)
    df_artists_tracks_copy = df_artists_tracks[df_artists_tracks['genres_new']!=''].copy()

    vectorizer = TfidfVectorizer(stop_words=stopwords.words('english'))
    features = vectorizer.fit_transform(df_artists_tracks_copy['genres_new'])
    num_clusters = 105  
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init='auto')
    kmeans.fit(features)
    df_artists_tracks_copy['genre_cluster'] = kmeans.labels_
    df_artists_tracks.loc[df_artists_tracks_copy.index, 'genre_cluster'] = df_artists_tracks_copy['genre_cluster']
    df_artists_tracks['genre_cluster'] = df_artists_tracks['genre_cluster'].fillna(-1)
    return df_artists_tracks