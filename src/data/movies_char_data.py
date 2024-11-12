import json
import pandas as pd
import os

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

# Class for all the data cleaners
class DataClass():

    def __init__(self, name, file_name, credits=None, separator=',', loaded=True, output_name=None):

        # name used to refer to the dataset when errors are raised
        self.name = name
        # file name of the raw data
        self.file_name = file_name
        # output name of the cleaned data
        self.output_name = output_name
        # create empty dataframes
        self.raw_df = pd.DataFrame()
        self.clean_df = pd.DataFrame()
        # We can add a credits attribute to give credit to the source of the data
        self.credits = credits
        self.columns = ['Year', 'Name', 'Sex', 'Count']
        # separator used in the csv file
        self.separator = separator
        
        print("Checking if the data is loaded from a file or from memory")
        if(loaded): # If loaded is true, there is a file corresponding to the data in the raw directory
            self.loaded = True
            self.fetch_raw_data()
        else: # was created from in memory content, no file corresponding in the raw directory
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

        print(f"{self.name} : Loading the raw data in the attribute")
        print(f'{RAW_DATA_PATH}{self.file_name}')
        self.raw_df = pd.read_csv(f'{RAW_DATA_PATH}{self.file_name}', delimiter=self.separator)
        print(f"{self.name} : loaded {self.raw_df.shape[0]} rows !")

    # Writes the cleaned data to a csv file
    def write_clean_data(self):

        # takes the file name if no output_name is given
        if self.output_name is None:
            self.output_name = self.file_name

        clean_name = self.output_name
         # hierarchy of the file is not repercuted in the clean folder
        if("/" in clean_name):
            split = clean_name.split("/")
            clean_name = split[-1]
            print(f"{self.name} : File name has been changed to {clean_name} (we don't want directories in the clean folder)")
        
        self.clean_df.to_csv(f'{CLEAN_DATA_PATH}{clean_name}', index=False)
        print(f"{self.name} : Data has been cleaned and saved to {CLEAN_DATA_PATH}{clean_name}!")

    # If the clean data is already saved, load it (will throw an error if the file is not found)
    def load_clean_data(self):
        self.clean_df = pd.read_csv(f'{CLEAN_DATA_PATH}{self.file_name}')

    # Checks if there are missing values in the raw data and that it conforms to the expected structure
    def check_clean_data(self):
        # Number of Columns if equal to 4
        assert self.clean_df.shape[1] == 4, f'{self.name} has {self.clean_df.shape[1]} columns, 4 are excepted'
        # Expected column names are ['Year', 'Name', 'Sex', 'Count']
        assert all(col in self.clean_df.columns for col in self.columns), f'{self.name} has not the right column names : {self.columns}'

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
        assert all(self.clean_df['Name'].str.match("^[A-Z-\s\']+$")), f'{self.name} : Not all the names are composed of uppercased letters'
        assert all(self.clean_df['Sex'].str.match('^[MF]$')), f'{self.name} : The sex column contains values different from M/F'

    # Function that will be defined by children classes
    def clean_raw_data(self):
        raise NotImplementedError

    # Execute all the cleaning steps
    def pipeline(self):
        if not self.loaded:
            print(f"{self.name} : This object does not come from a local file, cannot be loaded")
            return
        self.fetch_raw_data()
        self.clean_raw_data()
        self.write_clean_data()

# Class for Character data from 
class CharacterData(DataClass):

    def __init__(self, name, file_name, separator='\t', loaded=True, output_name=None):
        super().__init__(name, file_name, separator=separator, loaded=loaded)
        self.columns = ['Wikipedia_movie_ID', 'Freebase_movie_ID', 'Release_date', 'Character_name', 'Actor_DOB', 'Actor_gender', 'Actor_height', 'Actor_ethnicity', 'Actor_name', 'Actor_age', 'Freebase_character_map', 'Freebase_character_ID', 'Freebase_actor_ID']

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
        # Convert Actor_age to integer type
        self.clean_df['Actor_age'] = pd.to_numeric(self.clean_df['Actor_age'], errors='coerce')
        #Convert Actor_height to float
        self.clean_df['Actor_height'] = pd.to_numeric(self.clean_df['Actor_height'], errors='coerce')
 
        # Drop Freebase_movie_ID, Freebase_actor_ID, Freebas_character_map, Freebase_character_ID columns because they are not useful
        self.clean_df.drop(columns=['Freebase_movie_ID', 'Freebase_actor_ID', 'Freebase_character_map','Freebase_character_ID'], inplace=True)

        # Check the cleaned data
        self.check_clean_data()

    def check_clean_data(self):    
         #Check the number of columns (9)
        assert self.clean_df.shape[1] == 9, f'{self.name} has {self.clean_df.shape[1]} columns, 9 are expected'
        #Expected columns are  ['Wikipedia_movie_ID', 'Release_date', 'Character_name', 'Actor_DOB', 'Actor_gender', 'Actor_height', 'Actor_ethnicity', 'Actor_name', 'Actor_age']]
        expected_columns = ['Wikipedia_movie_ID', 'Release_date', 'Character_name', 'Actor_DOB', 'Actor_gender', 'Actor_height', 'Actor_ethnicity', 'Actor_name', 'Actor_age']
        assert all(col in self.clean_df.columns for col in expected_columns), f'{self.name} does not have the right column names: {expected_columns}'
        # to delete : assert all(col in self.clean_df.columns for col in self.columns), f'{self.name} has not the right column names : {self.columns}'

        # Check for missing values
        #missing_values = self.clean_df.isnull().sum().sum()
        #missing_values += self.clean_df.isna().sum().sum()
        # for the string
        #missing_values += self.clean_df.isin(['']).sum().sum()
        #assert missing_values == 0, f'{self.name} has missing values!'

        # Check the type of the columns
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
        ## allowed regex for name : '^[A-Z-\s\']+$' -> space and - are allowed and ' in case of names like O'Brien
        assert all(self.clean_df['Actor_gender'].str.match('^[MF]$')), f'{self.name} : The Actor_gender column contains values different from M/F'

# Class for Movie data from movie metadata
class MovieData(DataClass):

    def __init__(self, name, file_name, separator='\t', loaded=True, output_name=None):
        super().__init__(name, file_name, separator=separator, loaded=loaded)
        self.columns = ['Wikipedia_movie_ID', 'Freebase_movie_ID', 'Movie_name', 'Release_date', 'Revenue',
                        'Runtime', 'Languages', 'Countries', 'Genres']
        
    def fetch_raw_data(self):

        if not self.loaded:
            print(f"{self.name} : This object does not come from a local file, cannot be loaded")
            return

        print(f"{self.name} : Loading the raw data in the attribute")
        print(f'{RAW_DATA_PATH}{self.file_name}')
        self.raw_df = pd.read_csv(f'{RAW_DATA_PATH}{self.file_name}', delimiter='\t', quotechar='"', escapechar='\\')
        print(f"{self.name} : loaded {self.raw_df.shape[0]} rows !")
    
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
        self.clean_df['Runtime'] = pd.to_timedelta(self.clean_df['Runtime'], errors='coerce')
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