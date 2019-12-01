import sys
import spotipy
import spotipy.util as util
import urllib.parse

# USAGE:  python plconvert.py SPOTIFY_USERNAME

def parse_args(*args):
    if len(args) <= 3:
        print("Usage: %s user_name playlist_name" % (args[0],))
        sys.exit(1)

    username = args[1]
    input_playlist = args[2]
    output_playlist = args[3]

    return username, input_playlist, output_playlist

def config_spotipy(username):
    scope = 'user-read-currently-playing'
    token = util.prompt_for_user_token(username, scope, client_id='48ee37470dea4578b9a1b6f7abd2fd53', client_secret='e08691c47f664e2bb785f554a1760182', redirect_uri='http://localhost/')
    if not token:
        print("Can't get token for " + username)
        sys.exit(1)

    return spotipy.Spotify(auth=token)

def run(sp, username, input_playlist, output_playlist):

    input_pl_id = get_playlist_id(sp, username, input_playlist)
    all_tracks = get_playlist_tracks(sp, username, input_pl_id)
    track_ids = lookup_track_ids(sp, all_tracks)

    output_pl_id = get_playlist_id(sp, username, output_playlist)

    sys.exit(0)

def get_playlist_id(sp, username, pl_name):
    playlists = sp.user_playlists(username)
    for playlist in playlists['items']:
        if playlist['owner']['id'] == username and playlist['name'] == pl_name:
            print(f"Found playlist {pl_name} with tracks={playlist['tracks']['total']}")
            return playlist['id']

    print(f"Playlist {pl_name} not found")
    sys.exit(1)

def get_playlist_albums(sp, username, input_pl_id):
    output_track_ids = []
    results = sp.user_playlist(username, input_pl_id, fields="tracks,next")
    input_tracks = results['tracks']
    for i, item in enumerate(input_tracks['items']):
        track = item['track']
        artist = track['artists'][0]['name']
        album = track['album']['name']
        song = track['name']
        query = f"artist:{artist} track:{song}"
        found_tracks = sp.search(q=query, type="track", limit=1)
        if found_tracks and len(found_tracks['tracks']['items']) > 0:
            id = found_tracks['tracks']['items'][0]['id']
            print(f"{artist}/{song}: {id}")
            output_track_ids.append(id)
        else:
            print(f"=== Can't match {artist}/{song}")
            #sp.user_playlist_add_tracks(user=user_config['username'], playlist_id=user_config['playlist_id'], tracks=all_track_ids)
    return output_track_ids

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

def lookup_track_ids(sp, input_tracks):
    output_track_ids = []
    for item in input_tracks:
        track = item['track']
        artist = track['artists'][0]['name']
        album = track['album']['name']
        song = track['name']
        query = f"artist:{artist} track:{song}"
        found_tracks = sp.search(q=query, type="track", limit=1)
        if found_tracks and len(found_tracks['tracks']['items']) > 0:
            id = found_tracks['tracks']['items'][0]['id']
            print(f"{artist}/{song}: {id}")
            output_track_ids.append(id)
        else:
            print(f"=== Can't match {artist}/{song}")

    return output_track_ids

def add_tracks_to_playlist(sp, output_track_ids, output_playlist_id):
    pass
    #sp.user_playlist_add_tracks(user=user_config['username'], playlist_id=user_config['playlist_id'], tracks=all_track_ids)

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
