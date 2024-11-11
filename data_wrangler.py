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

# this script is used to load read raw data, clean it and save it to a new file
# inidividual functions can be used to just load the clean data

import pandas as pd

# All the cleaned dataframes will follow the same structure:
# 1. Year
# 2. Name : in upper case
# 3. Sex [F/M]
# 4. Count

# DATA FOLDER PATH (script is launched from the root folder)
RAW_DATA_PATH = 'data/raw/names/'
CLEAN_DATA_PATH = 'data/clean/names/'


# Class for all the data cleaners
class NamesData():

    def __init__(self, name, file_name, credits=None, separator=',', loaded=True):

        # name used to refer to the dataset when errors are raised
        self.name = name
        # file name of the raw data
        self.file_name = file_name
        # create empty dataframes
        self.raw_df = pd.DataFrame()
        self.clean_df = pd.DataFrame()
        # We can add a credits attribute to give credit to the source of the data
        self.credits = credits
        self.columns = ['Year', 'Name', 'Sex', 'Count']
        # separator used in the csv file
        self.separator = separator

        if (loaded):  # If loaded is true, there is a file corresponding to the data in the raw directory
            self.loaded = True
            self.fetch_raw_data()
        else:  # was created from in memory content, no file corresponding in the raw directory
            self.loaded = False

    # Function called when 'len' is called on the object
    def __len__(self):
        return self.clean_df.shape[0]

        # function executed when an instance of the class is called, we return the cleaned dataframe

    def __call__(self, *args, **kwds):
        return self.clean_df

    # Reads the raw data and stores it in the raw_df attribute
    def fetch_raw_data(self):

        if not self.loaded:
            print(f"{self.name} : This object does not come from a local file, cannot be loaded")
            return

        self.raw_df = pd.read_csv(f'{RAW_DATA_PATH}{self.file_name}', delimiter=self.separator)
        print(f"{self.name} : loaded {self.raw_df.shape[0]} rows !")

    # Writes the cleaned data to a csv file
    def write_clean_data(self):

        clean_name = self.file_name
        # hierarchy of the file is not repercuted in the clean folder
        if ("/" in clean_name):
            split = clean_name.split("/")
            clean_name = split[-1]
            print(
                f"{self.name} : File name has been changed to {clean_name} (we don't want directories in the clean folder)")

        self.clean_df.to_csv(f'{CLEAN_DATA_PATH}{clean_name}', index=False)

    # If the clean data is already saved, load it (will throw an error if the file is not found)
    def load_clean_data(self):
        self.clean_df = pd.read_csv(f'{CLEAN_DATA_PATH}{self.file_name}')

    # Execute all the cleaning steps
    def pipeline(self):
        if not self.loaded:
            print(f"{self.name} : This object does not come from a local file, cannot be loaded")
            return
        self.fetch_raw_data()
        self.clean_raw_data()
        self.write_clean_data()
        print(
            f"{self.name} : Data has been cleaned and saved to the clean data directory ! ({self.clean_df.shape[0]} rows)")

    # Checks if there are missing values in the raw data and that it conforms to the expected structure
    def check_clean_data(self):
        # Number of Columns if equal to 4
        assert self.clean_df.shape[1] == 4, f'{self.name} has {self.clean_df.shape[1]} columns, 4 are excepted'
        # Expected column names are ['Year', 'Name', 'Sex', 'Count']
        assert all(col in self.clean_df.columns for col in
                   self.columns), f'{self.name} has not the right column names : {self.columns}'

        # Missing values in the cleaned data
        missing_values = self.clean_df.isnull().sum().sum()
        missing_values += self.clean_df.isna().sum().sum()
        # for the string
        missing_values += self.clean_df.isin(['']).sum().sum()
        assert missing_values == 0, f'{self.name} has missing values!'

        # Check the tyoe of the columns
        ## Year column should be int64
        assert self.clean_df['Year'].dtype == 'int64', f'{self.name} : Year column is not of type int64'
        ## Name column : String -> object in pandas
        assert self.clean_df['Name'].dtype == 'object', f'{self.name} : Name column is not of type object (string)'
        ## Sex column : String -> object in pandas
        assert self.clean_df['Sex'].dtype == 'object', f'{self.name} : Sex column is not of type object (string)'
        ## Count column : int64
        assert self.clean_df['Count'].dtype == 'int64', f'{self.name} : Count column is not of type int64'

        # Check for duplicates -> same name, same sex, same year, but different count
        wo_year = self.clean_df.drop(columns=['Count'])
        duplicates = wo_year.duplicated().sum()
        assert duplicates == 0, f'{self.name} has {duplicates} duplicates !'

        # Check that the names contain only letters
        # allowed regex for name : '^[A-Z-\s\']+$' -> space and - are allowed and ' in case of names like O'Brien
        # allowed regex for sexe (only M/F) : '^[MF]$'
        assert all(self.clean_df['Name'].str.match(
            "^[A-Z-\s\']+$")), f'{self.name} : Not all the names are composed of uppercased letters'
        assert all(self.clean_df['Sex'].str.match(
            '^[MF]$')), f'{self.name} : The sex column contains values different from M/F'

    # Function that will be defined by children classes
    def clean_raw_data(self):
        raise NotImplementedError

#Class for the movie.metadata.tsv data
class MovieMetadataData(NamesData):

        # Clean the raw data
        def clean_raw_data(self):
            # 1. drop the the columns that we don't need
            self.clean_df = self.raw_df.drop(columns=['Freebase_movie_ID'])
            # Change the column names
            self.clean_df.columns = self.columns
            # Rewrite the names in upper case
            self.clean_df['Name'] = self.clean_df['Name'].str.upper()
            # Check the data
            self.check_clean_data()


# Class for the US data
class USNamesData(NamesData):

    # Clean the raw data
    def clean_raw_data(self):
        self.clean_df = self.raw_df.copy()
        # Change the column names
        self.clean_df.columns = self.columns
        # Rewrite the names in upper case
        self.clean_df['Name'] = self.clean_df['Name'].str.upper()
        # Check the data
        self.check_clean_data()  # Nothing more has to be done, this dataset is already clean and of good quality


# Class for the UK data
class UKNamesData(NamesData):

    # Clean the raw data
    def clean_raw_data(self):
        from unidecode import unidecode

        # 1. drop the the columns that we don't need
        self.clean_df = self.raw_df.drop(columns=['rank', 'nation'])
        # invert columns 1 and 2
        self.clean_df = self.clean_df[['year', 'name', 'sex', 'n']]
        # Change the column names
        self.clean_df.columns = self.columns
        # for a strange reason, the type of the numbers are set to float -> cast to int
        self.clean_df['Year'] = self.clean_df['Year'].astype(int)
        self.clean_df['Count'] = self.clean_df['Count'].astype(int)
        # Put the name in upper case
        self.clean_df['Name'] = self.clean_df['Name'].str.upper()
        # The dataset contained both values in uppercase and lowercase, but with different count -> group them
        self.clean_df = self.clean_df.groupby(['Year', 'Name', 'Sex']).sum().reset_index()
        # Replace accents on letters
        self.clean_df['Name'] = self.clean_df['Name'].apply(lambda x: unidecode(x))
        # 31 entries are not complying with the regex -> drop them
        self.clean_df = self.clean_df[self.clean_df['Name'].str.match('^[A-Z-\s\']+$')]
        # Dataset contains 1 missing values out of 565817 rows -> drop the row
        self.clean_df.dropna(inplace=True)
        # Check the data
        self.check_clean_data()


# Class for the Spain data
class FranceNamesData(NamesData):

    # Clean the raw data
    def clean_raw_data(self):
        # Latin language use accents in the name, this function will help to remove them
        from unidecode import unidecode

        self.clean_df = self.raw_df.drop(columns=['dpt'])

        # the null value for the departement is XX, and the null value for the year is XXXX, we will remove these entries
        self.clean_df = self.clean_df[self.clean_df['annais'] != 'XXXX']

        # Remove the accents from the names (might take some time)
        self.clean_df['preusuel'] = self.clean_df['preusuel'].astype(str)
        self.clean_df['preusuel'] = self.clean_df['preusuel'].apply(lambda x: unidecode(x))
        # this might have created some duplicates -> we need to group them and sum the counts
        self.clean_df = self.clean_df.groupby(['annais', 'preusuel', 'sexe']).sum().reset_index()

        # the sex is 1 if it is a boy, 2 if it is a girl -> replace by M/F
        self.clean_df['sexe'] = self.clean_df['sexe'].replace(1, 'M')
        self.clean_df['sexe'] = self.clean_df['sexe'].replace(2, 'F')

        self.clean_df = self.clean_df[['annais', 'preusuel', 'sexe', 'nombre']]
        self.clean_df.columns = self.columns

        # order by year
        self.clean_df = self.clean_df.sort_values(by='Year')
        self.clean_df.reset_index(drop=True, inplace=True)

        # set the column types
        self.clean_df['Year'] = self.clean_df['Year'].astype(int)
        self.clean_df['Name'] = self.clean_df['Name'].str.upper()
        self.clean_df['Count'] = self.clean_df['Count'].astype(int)

        # There is only 1 name not matching the regex -> drop
        self.clean_df = self.clean_df[self.clean_df['Name'].str.match('^[A-Z-\s\']+$')]

        # Check the data
        self.check_clean_data()

    # Class for Movie data from movie metadata
    class MovieData(NamesData):

        def init(self, name, file_name, separator='\t', loaded=True):
            super().init(name, file_name, separator=separator, loaded=loaded)
            self.columns = ['Wikipedia_movie_ID', 'Freebase_movie_ID', 'Movie_name', 'Release_date', 'Revenue',
                            'Runtime', 'Languages', 'Countries', 'Genres']

        # Clean the raw data
        def clean_raw_data(self):
            self.clean_df = self.raw_df.copy()
            # Rename columns
            self.clean_df.columns = self.columns

            # Drop the 'Freebase_movie_ID' column
            self.clean_df.drop(columns=['Freebase_movie_ID'], inplace=True)

            # Process 'Languages' column
            self.clean_df['Languages'] = self.clean_df['Languages'].apply(lambda data: self._parse_json_column(data, 'Languages'))
            # Process 'Countries' column
            self.clean_df['Countries'] = self.clean_df['Countries'].apply(lambda data: self._parse_json_column(data, 'Countries'))
            # Process 'Genres' column
            self.clean_df['Genres'] = self.clean_df['Genres'].apply(lambda data: self._parse_json_column(data, 'Genres'))

            #Assign types to columns
            self.clean_df['Release_date'] = pd.to_datetime(self.clean_df['Release_date'], errors='coerce')
            self.clean_df['Revenue'] = pd.to_numeric(self.clean_df['Revenue'], errors='coerce')
            self.clean_df['Runtime'] = pd.to_timedelta(self.clean_df['Runtime'], errors='coerce')
            # Assigne type object to the columns
            self.clean_df['Movie_name'] = self.clean_df['Movie_name'].astype('object')
            self.clean_df['Languages'] = self.clean_df['Languages'].astype('object')
            self.clean_df['Countries'] = self.clean_df['Countries'].astype('object')
            self.clean_df['Genres'] = self.clean_df['Genres'].astype('object')

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
            # Number of Columns should be 7
            assert self.clean_df.shape[1] == 7, f'{self.name} has {self.clean_df.shape[1]} columns, 7 are expected'
            # Expected column names
            expected_columns = ['Wikipedia_movie_ID', 'Movie_name', 'Release_date', 'Revenue', 'Runtime', 'Languages',
                                'Countries']
            assert all(col in self.clean_df.columns for col in
                       expected_columns), f'{self.name} does not have the right column names: {expected_columns}'

            # Missing values in the cleaned data
            missing_values = self.clean_df.isnull().sum().sum()
            missing_values += self.clean_df.isna().sum().sum()
            missing_values += self.clean_df.isin(['']).sum().sum()
            assert missing_values == 0, f'{self.name} has missing values!'

            # Check the type of the columns
            assert self.clean_df[
                       'Wikipedia_movie_ID'].dtype == 'object', f'{self.name}: Wikipedia_movie_ID column is not of type object'
            assert self.clean_df[
                       'Movie_name'].dtype == 'object', f'{self.name}: Movie_name column is not of type object'
            assert self.clean_df[
                       'Release_date'].dtype == 'datetime64[s]', f'{self.name}: Release_date column is not of type datetime64[s]'
            assert self.clean_df['Revenue'].dtype == 'float64', f'{self.name}: Revenue column is not of type float64'
            assert self.clean_df[
                       'Runtime'].dtype == 'timedelta64[s]', f'{self.name}: Runtime column is not of type timedelta64[s]'
            assert self.clean_df['Languages'].dtype == 'object', f'{self.name}: Languages column is not of type object'
            assert self.clean_df['Countries'].dtype == 'object', f'{self.name}: Countries column is not of type object'

            # Check for duplicates
            duplicates = self.clean_df.duplicated().sum()
            assert duplicates == 0, f'{self.name} has {duplicates} duplicates!'