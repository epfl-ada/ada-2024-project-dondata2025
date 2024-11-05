import pandas as pd
import os
import json



DATA_FOLDER = 'data/raw/'

CHARACTER_METADATASET = DATA_FOLDER+"character.metadata.tsv"
MOVIE_METADATASET = DATA_FOLDER+"movie.metadata.tsv"
PLOT_SUMMARIES = DATA_FOLDER+"plot_summaries.txt"
NAME_CLUSTER = DATA_FOLDER+"name.clusters.txt"
TVTROPES = DATA_FOLDER+"tvtropes.clusters.txt"

# Load the data

# Character metadata
character = pd.read_csv(CHARACTER_METADATASET, delimiter='\t')
print("shape:", character.shape)
character.columns = ['Wikipedia_movie_ID', 'Freebase_movie_ID', 'Release_date','Character_name', 'Actor_DOB', 'Actor_gender', 'Actor_height', 'Actor_ethnicity', 'Actor_name', 'Actor_age', 'Freebase_character_map', ' Freebase character ID','Freebase actor ID '] 


movie_metadata = pd.read_csv(MOVIE_METADATASET, delimiter='\t')
print("shape:", movie_metadata.shape)
movie_metadata.columns = ['Wikipedia_movie_ID', 'Freebase_movie_ID', 'Movie_name', 'Release_date', 'Revenue', 'Runtime', 'Languages', 'Countries', 'Genres'] 

# printing size of both dataframes
print("movie_metadata size:", movie_metadata.shape)
print("character size:", character.shape)

# Merging the 2 dataset 
df = pd.merge(movie_metadata, character, on=['Wikipedia_movie_ID', 'Freebase_movie_ID', 'Release_date' ])
print("shape:", df.shape)


# Define a general function to parse JSON-like strings and extract data based on the column name
def extract_data_from_column(data, column_name):
    if pd.notna(data):
        # Check if the entry is already a dictionary
        if isinstance(data, dict):
            data_dict = data
        else:
            try:
                # Convert string representation of a dictionary to an actual dictionary
                data_dict = json.loads(data.replace("'", '"'))
            except Exception as e:
                return None  # Handle cases where conversion fails

        # Extract and process data based on the column type
        if column_name in ['Languages', 'Countries']:
            # Simplify by removing common suffix like "Language" or "Country" if needed
            return ', '.join(value.replace(" Language", "").replace(" Country", "") for value in data_dict.values())
        elif column_name == 'Genres':
            # For genres, extract the human-readable part after the colon if present
            return ', '.join(genre.split(': ')[-1] if ': ' in genre else genre for genre in data_dict.values())
        else:
            # Default behavior: join values with a comma
            return ', '.join(data_dict.values())
    return None


# Apply the function to different columns based on their type
for column in ['Languages', 'Countries', 'Genres']:
    df[column] = df[column].apply(lambda x: extract_data_from_column(x, column))


# Looking at my data types, I see that the Release_date column is an object. I will convert it to a datetime object.
df['Release_date'] = pd.to_datetime(df['Release_date'], errors='coerce')

# Actor_DOB is also an object. I will convert it to a datetime object.
df['Actor_DOB'] = pd.to_datetime(df['Actor_DOB'], errors='coerce')

# Save the processed DataFrame to a CSV file
output_file_path = 'processed_data.csv'  # You can specify a path and file name here
df.to_csv(output_file_path, index=False)  # index=False means do not write row index

print(f"Data saved to {output_file_path}")