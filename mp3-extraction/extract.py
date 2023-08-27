import os
import sys
import time
import librosa
import logging
import numpy as np
import pandas as pd
import sounddevice as sd
import concurrent.futures


def sample_pickles(n=10):
    muse = pd.read_csv('muse_v3.csv').assign(y=None, sr=None)
    pickle_files = [f for f in os.listdir('pickles') if f.endswith('.pkl')]

    for pickle in pickle_files:
        print(pickle)
        pickle_df = pd.read_pickle(os.path.join('pickles', pickle))
        pickle_sample = pickle_df.sample(min(len(pickle_df), n))

        for index, row in pickle_sample.iterrows():
            muse.iat[index, muse.columns.get_loc('y')] = row['y']
            muse.iat[index, muse.columns.get_loc('sr')] = row['sr']

    muse_sample = muse.dropna(subset=['y', 'sr'])
    muse_sample.to_pickle(f'samples/sample_{n * len(pickle_files)}.pkl')
    print(muse_sample)


def getSongPath(song_id, track, artist):
    HARD_DRIVE = '/Volumes/Nico Backup Drive'
    song_dir = os.path.join(HARD_DRIVE, 'songs')

    if ('/' in track): track = track.replace('/', '_')
    if ('/' in artist): artist = artist.replace('/', '_')
    filename = f"{song_id}_{track.replace(' ', '_')}_{artist.replace(' ', '_')}"
    filepath = os.path.join(song_dir, filename) + '.mp3'

    if os.path.exists(filepath):
        return filepath
    else:
        logging.error(f"[{song_id}] File not found: {filepath}")
        return None


def load_song(index, track, artist):
    path = getSongPath(index, track, artist)
    if path:
        y, sr = librosa.load(path)
        duration = librosa.get_duration(y=y, sr=sr)
        mid_quartiles = np.percentile(np.arange(duration), [25, 75])
        start_time = np.random.uniform(low=mid_quartiles[0], high=mid_quartiles[1]-30)
        y_30s = y[int(start_time*sr):int((start_time+30)*sr)]
        return index, y_30s, sr
    else:
        return index, None, None


def extract_features():
    chunk_size = 1000
    muse = pd.read_csv('muse_v3.csv')

    num_items_processed = 0
    for chunk_start in range(0, len(muse), chunk_size):
        chunk_end = min(chunk_start + chunk_size, len(muse))
        pickle_file = f'pickles/y_sr_{chunk_start}_{chunk_end-1}.pkl'
        if os.path.exists(pickle_file):
            logging.info(f"Skipping {pickle_file}")
            num_items_processed = chunk_end
            continue

        features = pd.DataFrame(columns=['y', 'sr'])
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(load_song, index, row['track'], row['artist']) for index, row in muse.iloc[chunk_start:chunk_end].iterrows()]

            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                index, y, sr = future.result()
                if y is not None:
                    features.loc[index] = [y, sr]
                    logging.info(f"[{index}] Extracted features: ({muse.at[index, 'track']}, {muse.at[index, 'artist']})")
                else:
                    logging.error(f"[{index}] Failed to extract features: ({muse.at[index, 'track']}, {muse.at[index, 'artist']})")

                num_items_processed += 1
                if num_items_processed % chunk_size == 0:
                    pickle_file = f'pickles/y_sr_{num_items_processed-chunk_size}_{num_items_processed-1}.pkl'
                    features.to_pickle(pickle_file)
                    logging.info(f"[{num_items_processed-1}] Saved features: {pickle_file}")

        if num_items_processed % chunk_size != 0:
            pickle_file = f'pickles/y_sr_{num_items_processed-(num_items_processed%chunk_size)}_{num_items_processed-1}.pkl'
            features.to_pickle(pickle_file)
            logging.info(f"[{num_items_processed-1}] Saved features: {pickle_file}")


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s %(message)s',
        handlers=[logging.FileHandler('extract.log')],
    )

    # while True:
    #     try:
    #         extract_features()
    #     except Exception as e:
    #         logging.error(f"Error: {e}")
    #         time.sleep(10)

    # sample_pickles()

    df = pd.read_pickle('samples/sample_890.pkl')
    sample = df.sample(100)
    for index, row in sample.iterrows():
        print('playing:', index, row['track'], row['artist'])
        sd.play(row['y'], row['sr'])
        sd.wait()
        time.sleep(1)


if __name__ == '__main__':
    main()
