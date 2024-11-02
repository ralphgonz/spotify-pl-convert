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
    track_ids = lookup_track_ids_by_album(sp, all_tracks)

    print("[get output playlist id]", flush=True)
    output_pl_id = get_playlist_id(sp, username, output_playlist)
    print("[add tracks]", flush=True)
    add_tracks_to_playlist(sp, username, output_pl_id, track_ids)
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

# Search songs on a per-album basis to reduce number of API calls
def lookup_track_ids_by_album(sp, input_tracks):
    albums = set()
    output_track_ids = []
    song_dictionary = {}
    for item in input_tracks:
        track = item['track']
        artist = track['artists'][0]['name']
        album = track['album']['name']
        song = track['name']
        key = f"{artist}|{album}|{song}"
        song_dictionary[key] = 1
        
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
            print(f"=== Can't match {artist}/{album}", flush=True)
            continue
        for found_track in found_tracks['tracks']['items']:
            id = found_track['id']
            song = found_track['name']
            key = f"{artist}|{album}|{song}"
            if not key in song_dictionary:
                continue;
            # print(f"{artist.encode('utf-8')}/{album.encode('utf-8')}/{song.encode('utf-8')}: {id}")
            output_track_ids.append(id)

    print(f"found total {len(output_track_ids)} output tracks")
    return output_track_ids

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

# Sample "track" object:
# 
# 	"track": {
# 		"album": {
# 			"album_type": "None",
# 			"artists": [
# 			],
# 			"available_markets": [
# 			],
# 			"external_urls": {
# 			},
# 			"href": "None",
# 			"id": "None",
# 			"images": [
# 			],
# 			"name": "Chelsea Girl",
# 			"release_date": "None",
# 			"release_date_precision": "None",
# 			"type": "album",
# 			"uri": "None"
# 		},
# 		"artists": [
# 			{
# 				"external_urls": {
# 				},
# 				"href": "None",
# 				"id": "None",
# 				"name": "Nico",
# 				"type": "artist",
# 				"uri": "None"
# 			}
# 		],
# 		"available_markets": [
# 		],
# 		"disc_number": 0,
# 		"duration_ms": 248000,
# 		"explicit": "False",
# 		"external_ids": {
# 		},
# 		"external_urls": {
# 		},
# 		"href": "None",
# 		"id": "None",
# 		"is_local": "True",
# 		"name": "The Fairest Of The Seasons",
# 		"popularity": 0,
# 		"preview_url": "None",
# 		"track_number": 0,
# 		"type": "track",
# 		"uri": "spotify:local:Nico:Chelsea+Girl:The+Fairest+Of+The+Seasons:248"
# 	}
