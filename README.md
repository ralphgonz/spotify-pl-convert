# Spotify Playlist Converter

Python program to read a 'local' playlist (such as one imported from iTunes) and convert
it to a playlist of Spotify song IDs. This can then be bulk-liked
by dragging to your Liked Songs list in the Spotify app.

### Prerequisites

Note that spotipy's authentication hack requires Python to open a browser so you can copy the redirect url. For Windows, try using git bash.

1. Install Python, pip, and spotipy package.

   ```pip install spotipy```

1. Create a spotify client id and redirect url (`http://localhost:8080`) at developer site: 

   https://developer.spotify.com

1. Set environment variables:

   ```
   export SPOTIPY_CLIENT_SECRET='YOUR-CLIENT-SECRET'
   export SPOTIPY_CLIENT_ID='YOUR-CLIENT-ID'
   export SPOTIPY_REDIRECT_URI='http://localhost:8080'
   ```

### Prepare Source and Destination Playlists

1. Enable 'Show Local Files' setting with Spotify App.

1. Add selected local folders sources. You may have to toggle some of the default sources to disable them.

1. Create a Spotify playlist from the selected Local Files.

1. Create an empty destination playlist in Spotify App.

### Convert Playlist

1. Run plconvert.py:

   ```
   python plconvert.py SPOTIFY-USER-NAME INPUT-PL-NAME OUTPUT-PL-NAME
   ```

1. Optional: In Spotify app, Select All of the destination playlist contents and drag to Liked Songs
