# Description: This file contains some utils functions to work with the movie charachters class.

import pandas as pd
import sys, os

# Change the path if the file is launched directly (not imported)
if(__name__ == '__main__'):
    sys.path.append(os.path.abspath(os.path.join('../../'))) # root directory

from src.data.names_data import NamesData


# Merge two names classes together: Movies and Characters
def merge_movies_characters_data(moviesData: NamesData, charactersData: NamesData) -> NamesData:
    moviesData.check_clean_data()
    charactersData.check_clean_data()

    df = pd.merge(moviesData.clean_df, charactersData.clean_df, on=['Wikipedia_movie_ID', 'Release_date'], how='inner')
    name = f"{moviesData.name} & {charactersData.name}"
    merged = NamesData(name, name.replace(" & ", "_") + ".csv", loaded=False)
    merged.clean_df = df

    # Print data types of columns
    print(merged.clean_df.dtypes)

    # Check for duplicates and print them if any
    duplicates = merged.clean_df[merged.clean_df.duplicated()]
    if not duplicates.empty:
        print("Duplicates found:")
        print(duplicates)

    # Remove duplicates
    merged.clean_df = merged.clean_df.drop_duplicates()

    return merged