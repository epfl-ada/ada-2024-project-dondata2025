import json
import pandas as pd
import os
from src.data.data_class import DataClass
from unidecode import unidecode

# All the cleaned dataframes will follow the same structure:
# 1. Year
# 2. Name : in upper case
# 3. Sex [F/M]
# 4. Count

# DATA FOLDER PATH (script is launched from the root folder)
RAW_DATA_PATH = 'data/raw/'
CLEAN_DATA_PATH = 'data/clean/movies_char/'

# Create the clean data directory if it does not exist
os.makedirs(CLEAN_DATA_PATH, exist_ok=True)

# Class for Character data from 
class CharacterData(DataClass):

    # Initialize the class and call the parent class constructor
    def __init__(self, name, file_name, loaded=True, output_name=None):

        self.regex = '^[A-Z-\s\']+$'
        separator='\t'
        columns = ['Wikipedia_movie_ID', 'Freebase_movie_ID', 'Release_date', 'Character_name', 'Actor_DOB', 'Actor_gender', 'Actor_height', 'Actor_ethnicity', 'Actor_name', 'Actor_age', 'Freebase_character_map', 'Freebase_character_ID', 'Freebase_actor_ID']
        super().__init__(name, file_name, None, separator, loaded, columns, RAW_DATA_PATH, CLEAN_DATA_PATH, output_name)

    # Load and clean the raw data
    def clean_raw_data(self):
        print(f"{self.name} : Cleaning the raw data")
        self.clean_df = self.raw_df.copy()
        # Correct any misalignments in column names due to spaces
        self.clean_df.columns = [col.strip() for col in self.columns]

        # Check the good type format for the columns
        # Convert DOB and Release date to datetime
        self.clean_df['Actor_DOB'] = pd.to_datetime(self.clean_df['Actor_DOB'], errors='coerce', format='%Y-%m-%d')
        self.clean_df['Release_date'] = pd.to_datetime(self.clean_df['Release_date'], errors='coerce', format='%Y-%m-%d')
        # Fill missing values with NaT
        self.clean_df['Actor_DOB'] = self.clean_df['Actor_DOB'].fillna(pd.NaT)
        self.clean_df['Release_date'] = self.clean_df['Release_date'].fillna(pd.NaT)

        # Convert Character_name and Actor_name to object type
        self.clean_df['Character_name'] = self.clean_df['Character_name'].astype('object')
        self.clean_df['Actor_name'] = self.clean_df['Actor_name'].astype('object')

        # We need to homogenize the name of the character and the actor
        # They need to comply to the following REGEX : '^[A-Z-\s\']+$' -> space and - are allowed and ' in case of names like O'Brien
        ### 1. Uppercase
        self.clean_df['Character_name'] = self.clean_df['Character_name'].str.upper()
        self.clean_df['Actor_name'] = self.clean_df['Actor_name'].str.upper()
        ### 2. Remove accents using unidecode
        self.clean_df['Character_name'] = self.clean_df['Character_name'].astype(str)
        self.clean_df['Actor_name'] = self.clean_df['Actor_name'].astype(str)
        self.clean_df['Character_name'] = self.clean_df['Character_name'].apply(lambda x: unidecode(x))
        self.clean_df['Actor_name'] = self.clean_df['Actor_name'].apply(lambda x: unidecode(x))
        ### 3. Remove special characters that doesn't comply to the regex (remove the row since the name will never match a real one)
        self.clean_df = self.clean_df[self.clean_df['Character_name'].str.match(self.regex)]
        self.clean_df = self.clean_df[self.clean_df['Actor_name'].str.match(self.regex)]

        # Convert Actor_age to integer type
        self.clean_df['Actor_age'] = pd.to_numeric(self.clean_df['Actor_age'], errors='coerce')
        #Convert Actor_height to float
        self.clean_df['Actor_height'] = pd.to_numeric(self.clean_df['Actor_height'], errors='coerce')
 
        # Drop Freebase_movie_ID, Freebase_actor_ID, Freebas_character_map, Freebase_character_ID columns because they are not useful
        self.clean_df.drop(columns=['Freebase_movie_ID', 'Freebase_actor_ID', 'Freebase_character_map','Freebase_character_ID', 'Actor_ethnicity'], inplace=True)

        # Check the cleaned data
        self.check_clean_data()

    def check_clean_data(self):    
         #Check the number of columns (9)
        assert self.clean_df.shape[1] == 8, f'{self.name} has {self.clean_df.shape[1]} columns, 9 are expected'
        #Expected columns are  ['Wikipedia_movie_ID', 'Release_date', 'Character_name', 'Actor_DOB', 'Actor_gender', 'Actor_height', 'Actor_name', 'Actor_age']]
        expected_columns = ['Wikipedia_movie_ID', 'Release_date', 'Character_name', 'Actor_DOB', 'Actor_gender', 'Actor_height', 'Actor_name', 'Actor_age']
        assert all(col in self.clean_df.columns for col in expected_columns), f'{self.name} does not have the right column names: {expected_columns}'
        
        ## Wikipedia_movie_ID : int64
        assert self.clean_df['Wikipedia_movie_ID'].dtype == 'int64', f'{self.name} : Wikipedia_movie_ID column is not of type int64'
        ## Release_date : datetime64
        assert pd.api.types.is_datetime64_any_dtype(self.clean_df['Release_date']), f'{self.name} : Release_date column is not of type datetime64'
        ## Character_name : object
        assert self.clean_df['Character_name'].dtype == 'object', f'{self.name} : Character_name column is not of type object'
        ## Actor_DOB : datetime64
        assert pd.api.types.is_datetime64_any_dtype(self.clean_df['Actor_DOB']), f'{self.name} : Actor_DOB column is not of type datetime64'
        ## Actor_gender : object
        assert self.clean_df['Actor_gender'].dtype == 'object', f'{self.name} : Actor_gender column is not of type object'
        ## Actor_height : float64
        assert self.clean_df['Actor_height'].dtype == 'float64', f'{self.name} : Actor_height column is not of type float64'
        ## Actor_name : object
        assert self.clean_df['Actor_name'].dtype == 'object', f'{self.name} : Actor_name column is not of type object'
        ## Actor_age : float64
        assert self.clean_df['Actor_age'].dtype == 'float64', f'{self.name} : Actor_age column is not of type float64'

        # Check that the names contain only letters
        ## allowed regex for name : '^[A-Z0-9-\s\']+$' -> space, numbers, and - are allowed and ' in case of names like O'Brien
        ## allowed regex for sexe (only M/F) : '^[MF]$'
        assert all(self.clean_df['Character_name'].str.match(self.regex)), f'{self.name} : Not all the Character_name are composed of uppercased letters'
        assert all(self.clean_df['Actor_name'].str.match(self.regex)), f'{self.name} : Not all the Actor_name are composed of uppercased letters'
        assert all(self.clean_df['Actor_gender'].str.match('^[MF]$')), f'{self.name} : The Actor_gender column contains values different from M/F'
    


# Class for Movie data from movie metadata
class MovieData(DataClass):

    # Initialize the class and call the parent class constructor
    def __init__(self, name, file_name, loaded=True, output_name=None):
        separator = '\t'
        columns = ['Wikipedia_movie_ID', 'Freebase_movie_ID', 'Movie_name', 'Release_date', 'Revenue','Runtime', 'Languages', 'Countries', 'Genres']
        super().__init__(name, file_name, None, separator, loaded, columns, RAW_DATA_PATH, CLEAN_DATA_PATH, output_name)
    
    # Clean the raw data
    def clean_raw_data(self):
        self.clean_df = self.raw_df.copy()

        # Change the column names
        self.clean_df.columns = self.columns

        # Correct any misalignments in column names due to spaces
        self.clean_df.columns = [col.strip() for col in self.clean_df.columns]

        # Ensure the 'Languages' column exists before processing
        if 'Languages' in self.clean_df.columns:
            self.clean_df['Languages'] = self.clean_df['Languages'].apply(
                lambda data: self.parse_json_column(data, 'Languages'))
        else:
            print("Warning: 'Languages' column not found in the data")

        # Ensure the 'Countries' column exists before processing
        if 'Countries' in self.clean_df.columns:
            self.clean_df['Countries'] = self.clean_df['Countries'].apply(
                lambda data: self.parse_json_column(data, 'Countries'))
        else:
            print("Warning: 'Countries' column not found in the data")

        # Ensure the 'Genres' column exists before processing
        if 'Genres' in self.clean_df.columns:
            self.clean_df['Genres'] = self.clean_df['Genres'].apply(
                lambda data: self.parse_json_column(data, 'Genres'))
        else:
            print("Warning: 'Genres' column not found in the data")

        # Checking the data types of the columns
        # Release date to datetime
        self.clean_df['Release_date'] = pd.to_datetime(self.clean_df['Release_date'], errors='coerce',
                                                       format='%Y-%m-%d')
        # Wikipedia_movie_ID to int64
        self.clean_df['Wikipedia_movie_ID'] = pd.to_numeric(self.clean_df['Wikipedia_movie_ID'], errors='coerce')

        # Revenue to float
        self.clean_df['Revenue'] = pd.to_numeric(self.clean_df['Revenue'], errors='coerce')
        # Runtime to timedelta
        self.clean_df['Runtime'] = pd.to_timedelta(self.clean_df['Runtime'], unit='m', errors='coerce')
        # Convert the columns to object type
        self.clean_df['Movie_name'] = self.clean_df['Movie_name'].astype('object')
        if 'Languages' in self.clean_df.columns:
            self.clean_df['Languages'] = self.clean_df['Languages'].astype('object')
        if 'Countries' in self.clean_df.columns:
            self.clean_df['Countries'] = self.clean_df['Countries'].astype('object')
        if 'Genres' in self.clean_df.columns:
            self.clean_df['Genres'] = self.clean_df['Genres'].astype('object')

        # Drop the 'Freebase_movie_ID' column because not useful
        self.clean_df.drop(columns=['Freebase_movie_ID'], inplace=True)

        # Check the cleaned data
        self.check_clean_data()

    def parse_json_column(self, data, column_name):
        '''
        Parse the JSON data in the column and return a string representation of the values
        param data: JSON data in the column
        param column_name: Name of the column
        return: String representation of the values
        
        '''
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
        #missing_values = self.clean_df.isnull().sum().sum()
        #missing_values += self.clean_df.isna().sum().sum()
        # for the string
        #missing_values += self.clean_df.isin(['']).sum().sum()
        #assert missing_values == 0, f'{self.name} has missing values!'

        # Check the type of the columns
        # Wikipedia_movie_ID : object
        assert self.clean_df['Wikipedia_movie_ID'].dtype == 'int64', f'{self.name}: Wikipedia_movie_ID column is not of type int64'
        # Movie_name : object
        assert self.clean_df['Movie_name'].dtype == 'object', f'{self.name}: Movie_name column is not of type object'
        # Release_date : datetime
        assert pd.api.types.is_datetime64_any_dtype(self.clean_df['Release_date']), f'{self.name}: Release_date column is not of type datetime'
        # Revenue : float64
        assert self.clean_df['Revenue'].dtype == 'float64', f'{self.name}: Revenue column is not of type float64'
        # Runtime : timedelta
        assert pd.api.types.is_timedelta64_dtype(self.clean_df['Runtime']), f'{self.name}: Runtime column is not of type timedelta'
        # Languages : object
        assert self.clean_df['Languages'].dtype == 'object', f'{self.name}: Languages column is not of type object'
        # Countries : object
        assert self.clean_df['Countries'].dtype == 'object', f'{self.name}: Countries column is not of type object'
        # Genres : object
        assert self.clean_df['Genres'].dtype == 'object', f'{self.name}: Genres column is not of type object'

        # Check for duplicates
        #duplicates = self.clean_df.duplicated().sum()
        #assert duplicates == 0, f'{self.name} has {duplicates} duplicates!'