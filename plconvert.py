import sys
import spotipy
import spotipy.util as util

# USAGE:  python plconvert.py SPOTIFY_USERNAME


def run(sp):
    show_playlists(sp)
    #t = sp._get('me/player/currently-playing')
    #currid = t['item']['album']['id']
    #print(f"current id={currid}")

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


###############

if __name__ == '__main__':
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print("Usage: %s username" % (sys.argv[0],))
        sys.exit()

    scope = 'user-read-currently-playing'
    token = util.prompt_for_user_token(username, scope, client_id='48ee37470dea4578b9a1b6f7abd2fd53', client_secret='e08691c47f664e2bb785f554a1760182', redirect_uri='http://localhost/')
    if token:
        print(f"Got token {token}")
        sp = spotipy.Spotify(auth=token)
        run(sp)
    else:
        print("Can't get token for " + username)

