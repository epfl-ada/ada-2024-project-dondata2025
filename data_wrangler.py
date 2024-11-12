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








# ********************************************************************************************************************

# Class for Names data

# ********************************************************************************************************************

# Class for Movie data from movie metadata
class MovieData(NamesData):

    def init(self, name, file_name, separator='\t', loaded=True):
        super().init(name, file_name, separator=separator, loaded=loaded)
        self.columns = ['Wikipedia_movie_ID', 'Freebase_movie_ID', 'Movie_name', 'Release_date', 'Revenue',
                        'Runtime', 'Languages', 'Countries', 'Genres']

    # Clean the raw data
    def clean_raw_data(self):
        self.clean_df = self.raw_df.copy()
        # Correct any misalignments in column names due to spaces
        self.clean_df.columns = [col.strip() for col in self.columns]

        # Rename columns
        #self.clean_df.columns = self.columns

        # Process the format of columns that are unreadable
        # Process 'Languages' column
        self.clean_df['Languages'] = self.clean_df['Languages'].apply(lambda data: self._parse_json_column(data, 'Languages'))
        # Process 'Countries' column
        self.clean_df['Countries'] = self.clean_df['Countries'].apply(lambda data: self._parse_json_column(data, 'Countries'))
        # Process 'Genres' column
        self.clean_df['Genres'] = self.clean_df['Genres'].apply(lambda data: self._parse_json_column(data, 'Genres'))

        # Checking the data types of the columns
        # Realase date to datetime
        self.clean_df['Release_date'] = pd.to_datetime(self.clean_df['Release_date'], errors='coerce',format='%Y-%m-%d')
        # Revenue to float
        self.clean_df['Revenue'] = pd.to_numeric(self.clean_df['Revenue'], errors='coerce')
        # Runtime to timedelta
        self.clean_df['Runtime'] = pd.to_timedelta(self.clean_df['Runtime'], errors='coerce')
        # Convert the columns to object type
        self.clean_df['Movie_name'] = self.clean_df['Movie_name'].astype('object')
        self.clean_df['Languages'] = self.clean_df['Languages'].astype('object')
        self.clean_df['Countries'] = self.clean_df['Countries'].astype('object')
        self.clean_df['Genres'] = self.clean_df['Genres'].astype('object')



        # Drop the 'Freebase_movie_ID' column because not useful
        self.clean_df.drop(columns=['Freebase_movie_ID'], inplace=True)



        
        # Check the cleaned data
        self.check_clean_data()







    def parse_json_column(self, data, column_name):
        if pd.notna(data):
            try:
                # Convert string representation of a dictionary to an actual dictionary
                data_dict = json.loads(data.replace("'", '"'))
            except Exception as e:
                return None  # Handle cases where conversion fails

            # Extract and process data based on the column type
            if column_name in ['Languages', 'Countries']:
                return ', '.join(
                    value.replace(" Language", "").replace(" Country", "") for value in data_dict.values())
            elif column_name == 'Genres':
                return ', '.join(genre.split(': ')[-1] if ': ' in genre else genre for genre in data_dict.values())
            else:
                return ', '.join(data_dict.values())
        return None

        # Check the cleaned data

    def check_clean_data(self):
        # Number of Columns should be 8
        assert self.clean_df.shape[1] == 8, f'{self.name} has {self.clean_df.shape[1]} columns, 8 are expected'
        # Expected column names
        expected_columns = ['Wikipedia_movie_ID', 'Movie_name', 'Release_date', 'Revenue', 'Runtime', 'Languages',
                            'Countries', 'Genres']
        assert all(col in self.clean_df.columns for col in
                   expected_columns), f'{self.name} does not have the right column names: {expected_columns}'

        # Missing values in the cleaned data
        missing_values = self.clean_df.isnull().sum().sum()
        missing_values += self.clean_df.isna().sum().sum()
        # for the string
        missing_values += self.clean_df.isin(['']).sum().sum()
        assert missing_values == 0, f'{self.name} has missing values!'

        # Check the type of the columns
        # Wikipedia_movie_ID : object
        assert self.clean_df['Wikipedia_movie_ID'].dtype == 'object', f'{self.name}: Wikipedia_movie_ID column is not of type object'
        # Movie_name : object
        assert self.clean_df['Movie_name'].dtype == 'object', f'{self.name}: Movie_name column is not of type object'
        # Release_date : datetime64[s]
        assert self.clean_df['Release_date'].dtype == 'datetime64[s]', f'{self.name}: Release_date column is not of type datetime64[s]'
        # Revenue : float64
        assert self.clean_df['Revenue'].dtype == 'float64', f'{self.name}: Revenue column is not of type float64'
        # Runtime : timedelta64[s]
        assert self.clean_df['Runtime'].dtype == 'timedelta64[s]', f'{self.name}: Runtime column is not of type timedelta64[s]'
        # Languages : object
        assert self.clean_df['Languages'].dtype == 'object', f'{self.name}: Languages column is not of type object'
        # Countries : object
        assert self.clean_df['Countries'].dtype == 'object', f'{self.name}: Countries column is not of type object'
        # Genres : object
        assert self.clean_df['Genres'].dtype == 'object', f'{self.name}: Genres column is not of type object'

        # Check for duplicates
        #duplicates = self.clean_df.duplicated().sum()
        #assert duplicates == 0, f'{self.name} has {duplicates} duplicates!'