# To access Spotipy
import spotipy
# To View the API response
import json

username = 'mavii17'
clientID = '1aa7507d6cc04b9da1a9985a2c92b4bc'
clientSecret = '46ccf650ac9046cca22fe9bcd375ad7e'
redirectURI = 'http://localhost:8888/callback'

# Create OAuth Object
oauth_object = spotipy.SpotifyOAuth(clientID,clientSecret,redirectURI)
# Create token
token_dict = oauth_object.get_access_token()
token = token_dict['access_token']
# Create Spotify Object
spotifyObject = spotipy.Spotify(auth=token)

user = spotifyObject.current_user()
# To print the response in readable format.
print(json.dumps(user,sort_keys=True, indent=4))

def get_user():
    return user

def getSpotipyObject():
    return spotifyObject

