import sys
import spotipy
import spotipy.util as util
import urllib.parse

# USAGE:  python plconvert.py SPOTIFY_USERNAME

def run(*args):
    if len(args) <= 3:
        print("Usage: %s user_name playlist_name" % (args[0],))
        sys.exit(1)

    username = args[1]
    input_playlist = args[2]
    output_playlist = args[3]
    scope = 'user-read-currently-playing'
    token = util.prompt_for_user_token(username, scope, client_id='48ee37470dea4578b9a1b6f7abd2fd53', client_secret='e08691c47f664e2bb785f554a1760182', redirect_uri='http://localhost/')
    if not token:
        print("Can't get token for " + username)
        sys.exit(1)

    sp = spotipy.Spotify(auth=token)
    input_pl_id = get_playlist_id(sp, username, input_playlist)
    output_pl_id = get_playlist_id(sp, username, output_playlist)
    track_ids = get_playlist_tracks(sp, username, input_pl_id)

    sys.exit(0)

def show_currently_playing(sp):
    track = sp._get('me/player/currently-playing')
    currid = track['item']['album']['id']
    print(f"current id={currid}")

def show_tracks(tracks):
    for i, item in enumerate(tracks['items']):
        track = item['track']
        print(f"  {i} {track['artists'][0]['name'].encode('utf-8')} {track['name'].encode('utf-8')}")

def show_playlists(sp):
    playlists = sp.user_playlists(username)
    for playlist in playlists['items']:
        if playlist['owner']['id'] == username:
            print
            print(playlist['name'])
            print(f"  total tracks {playlist['tracks']['total']}")
            results = sp.user_playlist(username, playlist['id'], fields="tracks,next")
            tracks = results['tracks']
            show_tracks(tracks)
            while tracks['next']:
                tracks = sp.next(tracks)
                show_tracks(tracks)

def get_playlist_id(sp, username, pl_name):
    playlists = sp.user_playlists(username)
    for playlist in playlists['items']:
        if playlist['owner']['id'] == username and playlist['name'] == pl_name:
            return playlist['id']

    print(f"Playlist {pl_name} not found")
    sys.exit(1)

def get_playlist_tracks(sp, username, input_pl_id):
    output_track_ids = []
    results = sp.user_playlist(username, input_pl_id, fields="tracks,next")
    input_tracks = results['tracks']
    for i, item in enumerate(input_tracks['items']):
        track = item['track']
        artist = track['artists'][0]['name']
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

###############

if __name__ == '__main__':
    run(*sys.argv)
