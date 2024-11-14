
import pandas as pd
from src.data.data_class import DataClass

# All the cleaned dataframes will follow the same structure:
# 1. Year
# 2. Name : in upper case
# 3. Sex [F/M]
# 4. Count

# DATA FOLDER PATH (script is launched from the root folder)
RAW_DATA_PATH = 'data/raw/names/'
CLEAN_DATA_PATH = 'data/clean/names/'

# Class for all the data cleaners
class NamesData(DataClass):

    def __init__(self, name, file_name, credits=None, separator=',', loaded=True):

        columns = ['Year', 'Name', 'Sex', 'Count']
        # Call the parent class constructor
        super().__init__(name, file_name, credits, separator, loaded, columns, RAW_DATA_PATH, CLEAN_DATA_PATH)

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

        # Check that the year is positive, less than 2024 and bigger than 1750
        assert all(self.clean_df['Year'] > 1750), f'{self.name} : The year is lower than 1750'
        assert all(self.clean_df['Year'] < 2024), f'{self.name} : The year is bigger than 2024'

        # Check that the count is positive
        assert all(self.clean_df['Count'] >= 0), f'{self.name} : The count is negative'

        print(f"{self.name} : Data is clean and conforms to the expected structure !")

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
