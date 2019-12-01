import sys
import spotipy
import spotipy.util as util
import urllib.parse

# Create a spotify client id and set redirect url: https://developer.spotify.com
# Set environment variables:
# export SPOTIPY_CLIENT_SECRET='YOUR-CLIENT-SECRET'
# export SPOTIPY_CLIENT_ID='YOUR-CLIENT-ID'
# export SPOTIPY_REDIRECT_URI='http://localhost/'
# USAGE:  python plconvert.py SPOTIFY-USER-NAME INPUT-PL-NAME OUTPUT-PL-NAME

SCOPE = 'playlist-modify-public'
OUTPUT_STEP_SIZE = 99

def run(sp, username, input_playlist, output_playlist):

    input_pl_id = get_playlist_id(sp, username, input_playlist)
    all_tracks = get_playlist_tracks(sp, username, input_pl_id)
    track_ids = lookup_track_ids_by_album(sp, all_tracks)

    output_pl_id = get_playlist_id(sp, username, output_playlist)
    add_tracks_to_playlist(sp, username, output_pl_id, track_ids)

    sys.exit(0)

def parse_args(*args):
    if len(args) <= 3:
        print("Usage: %s spotify_user_name input_playlist_name output_playlist_name" % (args[0],))
        sys.exit(1)

    username = args[1]
    input_playlist = args[2]
    output_playlist = args[3]

    return username, input_playlist, output_playlist

def config_spotipy(username):
    print(f"Configure Spotipy for username={username}, scope={SCOPE}")
    scope = SCOPE
    token = util.prompt_for_user_token(username, scope)
    if not token:
        print("Can't get token for " + username)
        sys.exit(1)

    return spotipy.Spotify(auth=token)

def get_playlist_id(sp, username, pl_name):
    playlists = sp.user_playlists(username)
    for playlist in playlists['items']:
        if playlist['owner']['id'] == username and playlist['name'] == pl_name:
            print(f"Found playlist {pl_name} with tracks={playlist['tracks']['total']}")
            return playlist['id']

    print(f"Playlist {pl_name} not found")
    sys.exit(1)

def get_playlist_tracks(sp, username, playlist_id):
    results = sp.user_playlist(username, playlist_id, fields="tracks,next")
    tracks = results['tracks']
    all_tracks = list(tracks['items'])
    while 'next' in tracks:
        tracks = sp.next(tracks)
        if not tracks:
            break
        all_tracks.extend(tracks['items'])

    return all_tracks

def lookup_track_ids_by_album(sp, input_tracks):
    albums = set()
    output_track_ids = []
    for item in input_tracks:
        track = item['track']
        album = track['album']['name']
        if album in albums:
            continue
        albums.add(album)
        artist = track['artists'][0]['name']
        query = f"artist:{artist} album:{album}"
        found_tracks = sp.search(q=query, type="track", limit=20)
        if not found_tracks:
            print(f"=== Can't match {artist}/{album}")
            continue
        for found_track in found_tracks['tracks']['items']:
            id = found_track['id']
            song = found_track['name']
            print(f"{artist}/{album}/{song.encode('utf-8')}: {id}")
            output_track_ids.append(id)

    return output_track_ids

def add_tracks_to_playlist(sp, username, output_playlist_id, output_track_ids):
    print(f"Adding {len(output_track_ids)} tracks to output playlist in groups of {OUTPUT_STEP_SIZE}")
    for i in range(0, len(output_track_ids), OUTPUT_STEP_SIZE):
        print(f"Range [{i}, {i+OUTPUT_STEP_SIZE})")
        sp.user_playlist_add_tracks(user=username, 
                                    playlist_id=output_playlist_id, 
                                    tracks=output_track_ids[i:i+OUTPUT_STEP_SIZE])

###############

if __name__ == '__main__':
    username, input_playlist, output_playlist = parse_args(*sys.argv)
    sp = config_spotipy(username)
    run(sp, username, input_playlist, output_playlist)


#def show_currently_playing(sp):
#    track = sp._get('me/player/currently-playing')
#    currid = track['item']['album']['id']
#    print(f"current id={currid}")

#def show_tracks(tracks):
#    for i, item in enumerate(tracks['items']):
#        track = item['track']
#        print(f"  {i} {track['artists'][0]['name'].encode('utf-8')} {track['name'].encode('utf-8')}")

#def show_playlists(sp):
#    playlists = sp.user_playlists(username)
#    for playlist in playlists['items']:
#        if playlist['owner']['id'] == username:
#            print
#            results = sp.user_playlist(username, playlist['id'], fields="tracks,next")
#            tracks = results['tracks']
#            show_tracks(tracks)
#            while tracks['next']:
#                tracks = sp.next(tracks)
#                show_tracks(tracks)

#def lookup_track_ids(sp, input_tracks):
#    output_track_ids = []
#    for item in input_tracks:
#        track = item['track']
#        artist = track['artists'][0]['name']
#        song = track['name']
#        query = f"artist:{artist} track:{song}"
#        found_tracks = sp.search(q=query, type="track", limit=1)
#        if found_tracks and len(found_tracks['tracks']['items']) > 0:
#            id = found_tracks['tracks']['items'][0]['id']
#            print(f"{artist}/{song}: {id}")
#            output_track_ids.append(id)
#        else:
#            print(f"=== Can't match {artist}/{song}")
#    return output_track_ids

