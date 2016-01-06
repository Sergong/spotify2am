#----------------------------------------------------------------------
#
# This script extracts all tracks from the Spotify Discover Weekly
# Playlist and outputs a spotify.csv file
#
#
import requests
import csv
import json
import base64
import os
import sys


def show_playlist_tracks(jsondata):
    for playlist in jsondata:
        print(playlist['name'])
        print('  total tracks', playlist['tracks']['total'])

    return len(jsondata)

#----------------------------------------------------------------------
#
#  You will need to create an App on the Spotify Developer site
#  https://developer.spotify.com/my-applications/#!/applications
#  in order to get a Client ID and a Client Secret
#
#

# Code to get an access token to be able to read my user playlists, using a callout to curl
# The string to encode is made up for ClientID:ClientSecret and needs to be Base64 encoded
client = str(base64.b64encode(b'[your ClientID]:[your Client Secret]'))
# Some String manipulation is needed to convert the binary encoding result into a string
encoded = client[2:len(client)-1]
# Constructing the Curl cmd line call to included the Base64 encoded Client and Secret and pipe it to a file
lcmd = 'curl -H "Authorization: Basic '+encoded+'" -d grant_type=client_credentials https://accounts.spotify.com/api/token > json.data'
# Execute the Curl command line
os.system(lcmd)

# Get the access token from the data returned by the curl call out
output = open('json.data', 'r' ).read()
access_token = json.loads(output)['access_token']


#----------------------------------------------------------------------
#
# set up additional data to be used in subsequent calls
#
userid = "" # <-- put your user ID here
name = "Discover Weekly"

# Now find the discover weekly playlist (note that you must ensure your personalized Discover Weekly playlist is publicly readable)
# First construct the url to find the playlist
pl_url = "https://api.spotify.com/v1/users/"+userid+"/playlists?limit=50"
# Using the requests module, call out to the Spotify Web API to get your playlists in json format
response  = requests.get(pl_url, headers={'Authorization': 'Bearer ' + access_token, 'Accept': 'application/json'})
# Now find the playlist called Discover Weekly (its usually in the first 50)
playlist = [playlist for playlist in response.json()['items'] if playlist['name'] == name] if response.ok else None
offset = 50
# If DW is not found, iterate through all playlists until we do... (no error handling here currently)
while len(playlist) == 0:
    pl_url = "https://api.spotify.com/v1/users/"+userid+"/playlists?limit=50&offset={}".format(offset)
    response  = requests.get(pl_url, headers={'Authorization': 'Bearer ' + access_token, 'Accept': 'application/json'})
    playlist = [playlist for playlist in response.json()['items'] if playlist['name'] == name] if response.ok else None
    offset += 50

# At this point we found our playlist, if its not there, the loop will be infinite...
# Now extract the URL for the tracks of the playlist
spoturl = playlist[0]['tracks']['href']

# Call out to the Spotify Web API to get the tracks in JSON format
r = requests.get(spoturl, headers={'Authorization': 'Bearer ' + access_token})
jsondata = r.json()

# Open our CSV file to dump the Artist, Song and Album values in
# Start with a header row
spotcsv = csv.writer(open('spotify.csv', 'w'), delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
spotcsv.writerow(['title', 'artist', 'album'])

for item in jsondata['items']:
  song = item['track']['name']
  album_name = item['track']['album']['name']
  for artist in item['track']['artists']:
    artist_name = artist['name']

  # Print the result to screen as well as writing the row in the CSV file
  print('Song: {}, artist: {}, album: {}'.format(song, artist_name, album_name))
  spotcsv.writerow([song, artist_name, album_name])
