# Description: This file contains some utils functions to work with the movie charachters class.

import pandas as pd
from pandas import DataFrame
import sys, os
from src.data.data_class import DataClass

# Change the path if the file is launched directly (not imported)
if(__name__ == '__main__'):
    sys.path.append(os.path.abspath(os.path.join('../../'))) # root directory

CLEANED_DATA_PATH = "data/cleaned/movies_char/"



# Merge two names classes together: Movies and Characters and returns a clean DF
def merge_movies_characters_data(moviesData: DataClass, charactersData: DataClass) -> DataFrame:
    moviesData.check_clean_data()
    charactersData.check_clean_data()

    df = pd.merge(moviesData.clean_df, charactersData.clean_df, on=['Wikipedia_movie_ID', 'Release_date'], how='inner')
    name = f"{moviesData.name} & {charactersData.name}"

    # We use this class to use its write method
    file_name = name.replace(" & ", "_")
    merged = DataClass(name, file_name, None, None, False, None, None, CLEANED_DATA_PATH, file_name)
    merged.clean_df = df

    # Check for duplicates and print them if any
    duplicates = merged.clean_df[merged.clean_df.duplicated()]
    if not duplicates.empty:
        print(f"Duplicates found: {len(duplicates)} duplicates ! removing them...")
    
    # Remove duplicates
    merged.clean_df = merged.clean_df.drop_duplicates()

    return merged()