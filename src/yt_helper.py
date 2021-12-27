from urllib import request
import re
import pytube
import multiprocessing as mp
import os
import random


class YT_Helper:
    PARTIAL_DOWNLOAD_PREFIX = "<ytdlpart>_"

    def __init__(self, destination, playlist_url, multiprocessing):
        self.destination = destination
        self.playlist_url = playlist_url
        self.playlist_id = self.playlist_url.replace(
            'https://www.youtube.com/playlist?list=', '')
        self.mp = multiprocessing
        self.video_urls = None

    def prepare(self):
        self._prepare_filesystem()
        video_elements = self._get_playlist_elements()
        self.video_urls = self._parse_palylist_elements(video_elements)

    def download(self):
        if self.video_urls is None:
            raise Exception("Run prepare before download.")
        print(f'Downloading {self.playlist_id}')
        if self.mp != 1:
            pool = mp.Pool(self.mp)
            random.shuffle(self.video_urls)
            _ = pool.map(self._download_file, enumerate(self.video_urls))
        else:
            for i, video_url in enumerate(self.video_urls):
                self._download_file((i, video_url))

    def _prepare_filesystem(self):
        if os.path.exists(self.destination):
            self.existing_files = [f for f in os.listdir(
                self.destination) if f.endswith('.mp4')]
        else:
            self.existing_files = []
            os.makedirs(self.destination)

    def _get_playlist_elements(self):
        page_elements = request.urlopen(self.playlist_url).readlines()
        page_elements = [el.decode() for el in page_elements]
        video_elements = [
            el for el in page_elements if '/watch?v=' in el and self.playlist_id in el]
        return video_elements

    def _parse_palylist_elements(self, video_elements):
        video_urls = []
        reg = r"(/watch\?v=[a-zA-Z0-9\-_]+\\u0026list=" + \
            self.playlist_id+r"\\u0026index=\d+)"
        for each in video_elements:
            for match in re.findall(reg, each):
                video_urls.append(match)
        print(f"{len(video_urls)} links found!")
        return ['https://www.youtube.com' + v for v in video_urls]

    def _download_file(self, data):
        counter, video_url = data
        try:
            yt = pytube.YouTube(video_url)
            yt.register_on_progress_callback(self._print_dot)

            vid = yt.streams.filter(subtype='mp4').first()
            fn = vid.default_filename

            if fn in self.existing_files:
                print('Skipping {}'.format(fn))
                return
            else:
                print(f'({counter+1}/{len(self.video_urls)}) Downloading {fn}')
                print()
                saved_path = vid.download(self.destination,
                                          filename_prefix=self.PARTIAL_DOWNLOAD_PREFIX,
                                          max_retries=5)
                os.rename(saved_path,
                          os.path.join(self.destination, fn))
                print('Done')
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except Exception as e:
            print(f"FAILED - {video_url}. {e}")

    def _print_dot(self, stream, chunk, bytes_remaining):
        print(f"{int(bytes_remaining/1024/1024):6d} Mb", end='\r')
