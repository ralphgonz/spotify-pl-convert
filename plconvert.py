import sys
import spotipy
import spotipy.util as util
import urllib.parse

SCOPE = 'playlist-read-private playlist-modify-private playlist-modify-public'
OUTPUT_STEP_SIZE = 99

def run(sp, username, input_playlist, output_playlist):

    print("[get input playlist id]", flush=True)
    input_pl_id = get_playlist_id(sp, username, input_playlist)
    print("[get all tracks]", flush=True)
    all_tracks = get_playlist_tracks(sp, username, input_pl_id)
    print("[lookup tracks]", flush=True)
    track_ids = lookup_track_ids_by_artist(sp, all_tracks)

    print("[get output playlist id]", flush=True)
    output_pl_id = get_playlist_id(sp, username, output_playlist)
    print("[get existing tracks]", flush=True)
    existing_tracks = get_playlist_tracks(sp, username, output_pl_id)
    print("[filter existing tracks]", flush=True)
    filtered_track_ids = filter_existing_tracks(track_ids, existing_tracks)
    print("[add tracks]", flush=True)
    add_tracks_to_playlist(sp, username, output_pl_id, filtered_track_ids)
    print("[done]", flush=True)

    sys.exit(0)

def parse_args(*args):
    if len(args) != 4:
        print("Usage: %s spotify_user_name input_playlist_name output_playlist_name" % (args[0],))
        sys.exit(1)

    username = args[1]
    input_playlist = args[2]
    output_playlist = args[3]

    return username, input_playlist, output_playlist

def config_spotipy(username):
    print(f"Configure Spotipy for username={username}, scope={SCOPE}")
    token = util.prompt_for_user_token(username, SCOPE)
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
    results = sp.user_playlist_tracks(username, playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    print(f"found total {len(tracks)} tracks")
    return tracks

# Search songs on a per-artist basis to reduce number of API calls. Also lets not worry about matching album name.
def lookup_track_ids_by_artist(sp, input_tracks):
    artists = set()
    output_track_ids = []
    
    # Create song dictionary for matching
    song_dictionary = {}
    for item in input_tracks:
        track = item['track']
        artist = track['artists'][0]['name']
        song = track['name']
        key = create_song_key(artist, song)
        song_dictionary[key] = 1
        
    for item in input_tracks:
        track = item['track']
        artist = track['artists'][0]['name']
        if artist in artists:
            continue
        artists.add(artist)
        
        # Get all found tracks for artist
        query = f"artist:{artist}"
        found_tracks = sp.search(q=query, type="track", limit=50)
        if not found_tracks['tracks']['items']:
            print(f"=== Can't match {artist.encode('utf-8')}", flush=True)
            continue
        found_items = found_tracks['tracks']['items']
        while found_tracks['tracks']['next']:
            found_tracks = sp.next(found_tracks['tracks'])
            found_items.extend(found_tracks['tracks']['items'])
            
        # Match artist/song name
        for found_track in found_items:
            id = found_track['id']
            song = found_track['name']
            key = create_song_key(artist, song)
            if not key in song_dictionary:
                continue
            # print(f"{artist.encode('utf-8')}/{album.encode('utf-8')}/{song.encode('utf-8')}: {id}")
            output_track_ids.append(id)

    print(f"found total {len(output_track_ids)}/{len(input_tracks)} output tracks")
    return output_track_ids

def create_song_key(artist, song):
    return f"{artist.encode('utf-8')}|{song.encode('utf-8')}"
    
def filter_existing_tracks(output_track_ids, existing_tracks):
    # create dictionary of existing track ids
    existing_ids = {}
    for item in existing_tracks:
        track = item['track']
        existing_ids[track['id']] = 1
    
    filtered_track_ids = []
    for id in output_track_ids:
        if id in existing_ids:
            continue
        filtered_track_ids.append(id)
        
    print(f"found {len(output_track_ids) - len(filtered_track_ids)} existing tracks")
    return filtered_track_ids

def add_tracks_to_playlist(sp, username, output_playlist_id, output_track_ids):
    print(f"Adding {len(output_track_ids)} tracks to output playlist in groups of {OUTPUT_STEP_SIZE}")
    for i in range(0, len(output_track_ids), OUTPUT_STEP_SIZE):
        print(f"Range [{i}, {i+OUTPUT_STEP_SIZE})", flush=True)
        sp.user_playlist_add_tracks(user=username, 
                                    playlist_id=output_playlist_id, 
                                    tracks=output_track_ids[i:i+OUTPUT_STEP_SIZE])

###############

if __name__ == '__main__':
    print("[get inputs]", flush=True)
    username, input_playlist, output_playlist = parse_args(*sys.argv)
    print("[configure spotipy]", flush=True)
    sp = config_spotipy(username)
    run(sp, username, input_playlist, output_playlist)


#def show_currently_playing(sp):
#    track = sp._get('me/player/currently-playing')
#    currid = track['item']['album']['id']
#    print(f"current id={currid}")

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
