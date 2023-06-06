import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline
from sklearn.neighbors import NearestNeighbors


# Read the data from the CSV file
global df_artists_tracks
df_artists_tracks = None
global df_artists_tracks_orig
df_artists_tracks_orig = None

METRIC_FEATURES = ['acousticness', 'danceability', 'duration_ms', 'energy', 'instrumentalness', 'key', 'liveness', 
                   'loudness', 'mode', 'popularity', 'speechiness', 'tempo', 'time_signature', 'valence', 
                   'artist_popularity', 'followers']

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
    df_artists_tracks = build_recommendation_metric(df_artists_tracks)
    df_artists_tracks = build_recommendation_genre(df_artists_tracks)
    
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
                       'artist_popularity', 'followers', 'genres', 'tracks_id', 'tracks_name', 'artists_id', 
                       'artists_name', 'album_id', 'uri', 'preview_url', 'country', 'lyrics']
    df_artists_tracks = df_artists_tracks[columns_to_keep]
    return df_artists_tracks

def build_recommendation_metric(df_artists_tracks):
    metric_pipeline = Pipeline(steps=[
        ('scaler', MinMaxScaler()),
        ('dbscan', DBSCAN(eps=0.3, min_samples=5))
    ])
    # Fit and transform the data
    df_artists_tracks['metric_cluster'] = metric_pipeline.fit_predict(df_artists_tracks[METRIC_FEATURES])
    return df_artists_tracks

def build_recommendation_genre(df_artists_tracks, n_clusters=105):
    # Create binarized genres and put it to a DataFrame
    mlb = MultiLabelBinarizer()
    genres_binarized = mlb.fit_transform(df_artists_tracks['genres'])
    genres_df = pd.DataFrame(genres_binarized, columns=mlb.classes_)
    df_artists_tracks = pd.concat([df_artists_tracks.drop('genres', axis=1), genres_df], axis=1)
    # Define a pipeline for genre features
    genre_pipeline = Pipeline(steps=[
        ('kmeans', KMeans(n_clusters=n_clusters))
    ])
    # Fit the data
    genre_labels = genre_pipeline.fit_predict(genres_df)
    df_artists_tracks['genre_cluster'] = genre_labels
    return df_artists_tracks
    
def recommend_songs_knn(df, song_id, n_recommendations, priority_factor=5):
    additional_features = ['genre_cluster', 'metric_cluster']
    metric_features = METRIC_FEATURES + additional_features

    df_scaled = df.copy()
    df_scaled[additional_features] *= priority_factor

    # Fit the NearestNeighbors model
    knn = NearestNeighbors(n_neighbors=n_recommendations, metric='cosine')
    knn.fit(df_scaled[metric_features])
    
    song_features = df_scaled[df_scaled['tracks_id'] == song_id][metric_features]

    distances, indices = knn.kneighbors(song_features)

    song_list = [df.iloc[indices.flatten()[i]]['tracks_id'] 
    for i in range(1, len(distances.flatten()))
        if print(f'{i}: {df.iloc[indices.flatten()[i]]["tracks_id"]}, with distance of {distances.flatten()[i]}') is None]
    return df[df['tracks_id'].isin(song_list)]


def recommend_songs(song_id, df, n_recommendations):
    return recommend_songs_knn(df, song_id, n_recommendations)
    #print(df[df['tracks_id'].isin(list)]).value_counts()
    #return df[df['tracks_id'].isin(list)]

def search_songs_and_artists(search, df):
    tracks_match = df[df['tracks_name'].str.contains(search, case=False)]
    artists_match = df[df['artists_name'].str.contains(search, case=False)]
    return pd.concat([tracks_match, artists_match]).drop_duplicates()

def getGenres():
    global df_artists_tracks_orig
    return df_artists_tracks_orig['genres'].unique().tolist()

def getGenre_tracks(genre):
    global df_artists_tracks_orig
    return df_artists_tracks_orig[df_artists_tracks_orig['genres'].str.contains(genre)]['tracks_name'].sample(1)

def get_artists_tracks():
    global df_artists_tracks
    return df_artists_tracks    