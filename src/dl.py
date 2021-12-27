import os
import argparse
from yt_helper import YT_Helper

def _prepare_playlist(playlisturl):
    playlists = playlisturl.split(',') if playlisturl is not None else []
    if len(playlists)==0:
        print('No playlists URLs provided.')
        exit(1)
    return playlists

def _prepare_multiprocessing(multiprocessing):
    try:
        multiprocessing = max(1,int(multiprocessing))
    except ValueError:
        print('Multiprocessing should be an integer > 1. Setting to 1.')
        multiprocessing = 1
    return multiprocessing

if __name__=='__main__':
    parser = argparse.ArgumentParser(
        usage='%(prog)s [-h] [-p PLAYLISTURL] [-d DESTINATION] [-mp PROCESS_COUNT]')
    parser.add_argument('-p', '--playlisturl',
                        help='Url(s) of the playlist to be downloaded, comma separated')
    parser.add_argument('-d', '--destination', help='Save directory path',
                        default=os.path.curdir+'video')
    parser.add_argument('-mp', '--multiprocessing',
                        help='Number of parallel processes for download', default=1)
    args = parser.parse_args()

    playlists = _prepare_playlist(args.playlisturl)

    multiprocessing = _prepare_multiprocessing(args.multiprocessing)

    for playlist in playlists:
        try:
            yt = YT_Helper(args.destination, playlist, multiprocessing)
            yt.prepare()
            yt.download()
        except KeyboardInterrupt:
            print('Intterupted by user')
            break
