# this script is used to load read raw data, clean it and save it to a new file
# inidividual functions can be used to just load the clean data

import pandas as pd
import sys

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

    def __init__(self, name, file_name, credits=None, separator=','):

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
        # load the raw data
        self.fetch_raw_data()

    # Reads the raw data and stores it in the raw_df attribute
    def fetch_raw_data(self):
        self.raw_df = pd.read_csv(f'{RAW_DATA_PATH}{self.file_name}', delimiter=self.separator)
        print(f"{self.name} : loaded {self.raw_df.shape[0]} rows !")

    # Writes the cleaned data to a csv file
    def write_clean_data(self):
        clean_name = self.file_name
         # hierarchy of the file is not repercuted in the clean folder
        if("/" in clean_name):
            split = clean_name.split("/")
            clean_name = split[-1]
            print(f"File name has been changed to {self.file_name} (we don't want directories in the clean folder)")
        
        self.clean_df.to_csv(f'{CLEAN_DATA_PATH}{clean_name}', index=False)

    # If the clean data is already saved, load it (will throw an error if the file is not found)
    def load_clean_data(self):
        self.clean_df = pd.read_csv(f'{CLEAN_DATA_PATH}{self.file_name}')
        
    # Execute all the cleaning steps
    def pipeline(self):
        self.fetch_raw_data()
        self.clean_raw_data()
        self.write_clean_data()
        print(f"Data has been cleaned and saved to the clean data directory !")

    # Checks if there are missing values in the raw data and that it conforms to the expected structure
    def check_clean_data(self):
        # Number of Columns if equal to 4
        assert self.clean_df.shape[1] == 4, f'{self.name} has {self.clean_df.shape[1]} columns, 4 are excepted'
        # Expected column names are ['Year', 'Name', 'Sex', 'Count']
        assert all(col in self.clean_df.columns for col in self.columns), f'{self.name} has not the right column names : {self.columns}'

        # Missing values in the cleaned data
        missing_values = self.clean_df.isnull().sum().sum()
        missing_values += self.clean_df.isna().sum().sum()
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

    # Function that will be defined by children classes
    def clean_raw_data(self):
        raise NotImplementedError
    

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
        self.check_clean_data() #Nothing more has to be done, this dataset is already clean and of good quality

# Class for the UK data
class UKNamesData(NamesData):

    # Clean the raw data
    def clean_raw_data(self):
        # 1. drop the the columns that we don't need
        self.clean_df = self.raw_df.drop(columns=['rank', 'nation'])
        # invert columns 1 and 2
        self.clean_df = self.clean_df[['year', 'name', 'sex', 'n']]
        # Change the column names
        self.clean_df.columns = self.columns
        # for a strange reason, the type of the numbers are set to float -> cast to int
        self.clean_df['Year'] = self.clean_df['Year'].astype(int)
        self.clean_df['Count'] = self.clean_df['Count'].astype(int)
        # Check the data
        # self.check_clean_data() -> this will fail due to some missing values in the data
        missing_values = self.clean_df.isnull().sum().sum()
        print(f"{self.name} : the raw dataset contains {missing_values} missing values out of {self.clean_df.shape[0]} rows, it will be dropped")
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
        self.clean_df['sexe'] = self.clean_df['sexe'].replace({1:'M', 2:'F'})

        self.clean_df = self.clean_df[['annais', 'preusuel', 'sexe', 'nombre']]
        self.clean_df.columns = self.columns

        # order by year
        self.clean_df = self.clean_df.sort_values(by='Year')
        self.clean_df.reset_index(drop=True, inplace=True)

        # set the column types
        self.clean_df['Year'] = self.clean_df['Year'].astype(int)
        self.clean_df['Name'] = self.clean_df['Name'].str.upper()
        self.clean_df['Count'] = self.clean_df['Count'].astype(int)
        self.clean_df['Sex'] = self.clean_df['Count'].astype(str)
        
        # Check the data
        self.check_clean_data()




    

        



