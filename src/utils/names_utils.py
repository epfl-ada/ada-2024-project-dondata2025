# Description: This file contains some utils functions to work with the names class.

import pandas as pd
import sys, os

# Change the path if the file is launched directly (not imported)
if(__name__ == '__main__'):
    sys.path.append(os.path.abspath(os.path.join('../../'))) # root directory

from src.data.names_data import NamesData


# Merge a list of names classes together 
def merge_names_data(namesData : list) -> NamesData:
    
    name = ""
    df = pd.DataFrame()

    # Check that the inputs have been cleaned
    for names in namesData:
        names.check_clean_data()
        name += f"{names.name} & "
        # Merge the data
        df = pd.concat([df, names.clean_df])
    
    # New object
    name = name[:-3] # Remove the last ' & '
    merged = NamesData(name, name.replace(" & ", "_") + ".csv", loaded=False)
    merged.clean_df = df

    # Due to the merging, the data might be duplicated -> group by and sum the counts
    merged.clean_df = merged.clean_df.groupby(['Year', 'Name', 'Sex']).sum().reset_index()
    # sort data
    merged.clean_df = merged.clean_df.sort_values(by=['Year', 'Name', 'Sex'])

    merged.check_clean_data()
    return merged

    
# Merge two names classes together: Movies and Characters
def merge_movies_characters_data(moviesData : NamesData, charactersData : NamesData) -> NamesData:
        
        moviesData.check_clean_data()
        charactersData.check_clean_data()
    
        # Merge the data
        df = pd.merge(moviesData.clean_df, charactersData.clean_df, on=['Wikipedia_movie_ID', 'Freebase_movie_ID', 'Release_date' ])
    
        # New object
        name = f"{moviesData.name} & {charactersData.name}"
        merged = NamesData(name, name.replace(" & ", "_") + ".csv", loaded=False)
        merged.clean_df = df
    
        # Due to the merging, the data might be duplicated -> group by and sum the counts
        merged.clean_df = merged.clean_df.groupby(['Wikipedia_movie_ID', 'Freebase_movie_ID', 'Release_date' ]).sum().reset_index()
        merged.check_clean_data()
        return merged



