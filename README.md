# Spotify Playlist Converter

Python program to read a 'local' playlist (such as one imported from iTunes) and convert
it to a playlist of Spotify song IDs. This can then be bulk-liked
by dragging to your Liked Songs list in the Spotify app.

### Prerequisites

1. Install Python spotipy package.

   ```pip install spotipy```

1. Create a spotify client id and redirect url at developer site: 

   https://developer.spotify.com

1. Set environment variables:

   ```
   export SPOTIPY_CLIENT_SECRET='YOUR-CLIENT-SECRET'
   export SPOTIPY_CLIENT_ID='YOUR-CLIENT-ID'
   export SPOTIPY_REDIRECT_URI='http://localhost/'
   ```

### Prepare Source and Destination Playlists

1. Enable sharing playlists in iTunes.

1. Import your iTunes playlist to a 'local' playlist with Spotify App.

1. Create an empty destination playlist in Spotify App.

### Convert Playlist

1. Run plconvert.py:

   ```
   python plconvert.py SPOTIFY-USER-NAME INPUT-PL-NAME OUTPUT-PL-NAME
   ```

1. In Spotify app, Select All of the destination playlist contents and drag to Liked Songs


