import os
import pandas as pd

# iterate through all files in the pickles directory
for filename in os.listdir('pickles'):
   
    # check if the file is a pickle file
    if filename.endswith('.pkl'):
        
        # load the pickle file
        df = pd.read_pickle(os.path.join('pickles', filename))
        
        # check if the dataframe is sorted
        if not df.index.is_monotonic_increasing:
            # sort the dataframe by index
            df.sort_index(inplace=True)
            # save the sorted dataframe
            df.to_pickle(os.path.join('pickles', filename))
            # print the filename
            print(f'Sorted {filename}')
