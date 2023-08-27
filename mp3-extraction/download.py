import os
import time
import yt_dlp
import logging
import librosa
import librosa.display
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor


def download_song(song_id, track, artist):
    output_dir = 'songs'
    os.makedirs(output_dir, exist_ok=True)

    if ('/' in track): track = track.replace('/', '_')
    if ('/' in artist): artist = artist.replace('/', '_')
    filename = f"{song_id}_{track.replace(' ', '_')}_{artist.replace(' ', '_')}"
    filepath = os.path.join(output_dir, filename)

    if os.path.exists(filepath + '.mp3'):
        print(f"Skipping {filename + '.mp3'} (already downloaded)")
        return

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': filepath,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        query = f"{track} {artist}"
        try:
            info_dict = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
            ydl.download([info_dict['webpage_url']])
            return
        except Exception as e:
            logging.error(f"[{song_id}] Download failed ({track}, {artist}): {e}")


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('download.log')
        ],
    )

    df = pd.read_csv('muse_v3.csv')
    song_list = [(id, row['track'], row['artist']) for id, row in df.iterrows()]

    with ThreadPoolExecutor(max_workers=1) as executor:
        futures = [executor.submit(download_song, *song) for song in song_list]

        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"Download failed: {e}")


if __name__ == '__main__':
    main()
