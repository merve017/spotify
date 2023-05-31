import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline
from sklearn.neighbors import NearestNeighbors


songslist = []

# Read the data from the CSV file
df_tracks = None
df_artists = None
global df_artists_tracks_orig
df_artists_tracks_orig = None
global df_artists_tracks
df_artists_tracks = None

def init_file():
    read_data()
    transform_data()
    build_recommendation_metric()
    build_recommendation_genre()

# read data as a def:
def read_data():
     global df_artists  
     df_artists = pd.read_csv('data/spotify_artists.csv', sep=',') 
     global df_tracks
     df_tracks = pd.read_csv('data/spotify_tracks.csv', sep=',')    
     

# do the transformation as a def:
def transform_data():
    df_tracks['artists_id'] = df_tracks['artists_id'].str.strip("[]").str.replace("'","")
    df_tracks.rename(columns={'id':'tracks_id'}, inplace=True)
    df_tracks.rename(columns={'name':'tracks_name'}, inplace=True)
    # Merge both dataframes
    global df_artists_tracks_orig
    global df_artists_tracks
    df_artists_tracks_orig = pd.merge(df_tracks, df_artists, left_on='artists_id', right_on='id', how='inner')
    df_artists_tracks = pd.merge(df_tracks, df_artists, left_on='artists_id', right_on='id', how='inner')
    df_artists_tracks['genres'] = df_artists_tracks['genres'].apply(lambda x: x if x else ["Unknown"])

# do the build recommendation metric as a def:
def build_recommendation_metric():
    global df_artists_tracks
    metric_pipeline = Pipeline(steps=[
        ('scaler', MinMaxScaler()),
        ('dbscan', DBSCAN(eps=0.3, min_samples=5))
    ])
    # Fit and transform the data
    metric_labels = metric_pipeline.fit_predict(df_artists_tracks[get_metric_features()])
    df_artists_tracks['metric_cluster'] = metric_labels

#get metric features as def
def get_metric_features():
    metric_features = ['acousticness', 'danceability', 'duration_ms', 'energy', 'instrumentalness', 'key', 'liveness', 
                    'loudness', 'mode', 'popularity', 'speechiness', 'tempo', 'time_signature', 'valence', 
                    'artist_popularity', 'followers']
    return metric_features

def build_recommendation_genre():
    global df_artists_tracks
    # Create binarized genres and put it to a DataFrame
    mlb = MultiLabelBinarizer()
    genres_binarized = mlb.fit_transform(df_artists_tracks['genres'])
    genres_df = pd.DataFrame(genres_binarized, columns=mlb.classes_)
    df_artists_tracks = pd.concat([df_artists_tracks.drop('genres', axis=1), genres_df], axis=1)
    # Define a pipeline for genre features
    n_clusters = 20  # Change no. of clusters here
    genre_pipeline = Pipeline(steps=[
        ('kmeans', KMeans(n_clusters=n_clusters))
    ])
    # Fit the data
    genre_labels = genre_pipeline.fit_predict(genres_df)
    df_artists_tracks['genre_cluster'] = genre_labels


def recommend_songs_knn(song_id, n_recommendations):
    df = df_artists_tracks
    additional_features = ['genre_cluster', 'metric_cluster']
    metric_features = get_metric_features()
    metric_features += additional_features
    # Get the genre_cluster and metric_cluster of the song
    song_clusters = df.loc[df['tracks_id'] == song_id, ['genre_cluster', 'metric_cluster']]
    genre_cluster = song_clusters['genre_cluster'].values[0]
    metric_cluster = song_clusters['metric_cluster'].values[0]

    # Get all songs within the same genre and metric clusters
    same_clusters = df[(df['genre_cluster'] == genre_cluster) & (df['metric_cluster'] == metric_cluster)]
    if len(same_clusters) >= n_recommendations:
        # If enough songs, compute KNN within the same genre and metric clusters
        song_features = same_clusters[same_clusters['tracks_id'] == song_id][metric_features]
        knn = NearestNeighbors(n_neighbors=n_recommendations)
        knn.fit(same_clusters[metric_features])
        distances, indices = knn.kneighbors(song_features)
    else:
        # Otherwise, get all songs within the same genre or metric cluster
        same_clusters = df[(df['genre_cluster'] == genre_cluster) | (df['metric_cluster'] == metric_cluster)]
        if len(same_clusters) >= n_recommendations:
            # If enough songs, compute KNN within the same genre or metric clusters
            song_features = same_clusters[same_clusters['tracks_id'] == song_id][metric_features]
            knn = NearestNeighbors(n_neighbors=n_recommendations)
            knn.fit(same_clusters[metric_features])
            distances, indices = knn.kneighbors(song_features)
        else:
            # If still not enough songs, compute KNN across all songs
            song_features = df[df['tracks_id'] == song_id][metric_features]
            knn = NearestNeighbors(n_neighbors=n_recommendations)
            knn.fit(df[metric_features])
            distances, indices = knn.kneighbors(song_features)

    # Print and return the recommendations
    song_list = []
    for i in range(len(distances.flatten())):
        if i == 0:
            print(f'Recommendations for {song_id}:\n')
        else:
            song_list.append(df.iloc[indices.flatten()[i]]['tracks_id'])
            print(f'{i}: {df.iloc[indices.flatten()[i]]["tracks_id"]}, with distance of {distances.flatten()[i]}')

    return song_list

def recommend_songs_knnOnly(song_id, n_recommendations):
    metric_features = get_metric_features()
    knn = NearestNeighbors(n_neighbors=n_recommendations)  # Change n_neighbors based on your needs
    knn.fit(df_artists_tracks[metric_features])
    df = df_artists_tracks
    song_features = df[df['tracks_id'] == song_id][metric_features]
    
    distances, indices = knn.kneighbors(song_features)
    
    song_list = []
    for i in range(len(distances.flatten())):
        if i == 0:
            print(f'Recommendations for {song_id}:\n')
        else:
            song_list.append(df.iloc[indices.flatten()[i]]['tracks_id'])
            print(f'{i}: {df.iloc[indices.flatten()[i]]["tracks_id"]}, with distance of {distances.flatten()[i]}')

    return song_list

# recommend songs mixed
def recommend_songs(song_id, n_recommendations):
    list = recommend_songs_knn(song_id, n_recommendations)
    return df_artists_tracks_orig[df_artists_tracks_orig['tracks_id'].isin(list)]

# recommend songs knn Only
def recommend_songsKnn(song_id, n_recommendations):
    list = recommend_songs_knnOnly(song_id, n_recommendations)
    return df_artists_tracks_orig[df_artists_tracks_orig['tracks_id'].isin(list)]

def matchingSongs(song_title_search):
    global df_artists_tracks_orig
    return df_artists_tracks_orig[df_artists_tracks_orig['tracks_name'].str.contains(song_title_search, case=False)]
