import pandas as pd

# Class for all the data cleaners, it defines the structure we expect of the data and the methods to clean it
class DataClass():

    def __init__(self, name, file_name, credits, separator, loaded, columns, raw_path, clean_path, output_name=None):

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
        self.columns = columns
        # separator used in the csv file
        self.separator = separator

        # Paths to the raw and clean data
        self.raw_path = raw_path
        self.clean_path = clean_path
        
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

        self.raw_df = pd.read_csv(f'{self.raw_path}{self.file_name}', delimiter=self.separator)
        print(f"{self.name} : loaded {self.raw_df.shape[0]} rows !")

    # Writes the cleaned data to a csv file
    def write_clean_data(self):
        
        self.check_clean_data()

        # takes the file name if no output_name is given
        if self.output_name is None:
            self.output_name = self.file_name

        clean_name = self.output_name
         # hierarchy of the file is not repercuted in the clean folder
        if("/" in clean_name):
            split = clean_name.split("/")
            clean_name = split[-1]
            print(f"{self.name} : File name has been changed to {clean_name} (we don't want directories in the clean folder)")
        
        self.clean_df.to_csv(f'{self.clean_path}{clean_name}', index=False, encoding='utf-8')
        print(f"{self.name} : Clean data has been and saved to {self.clean_path}{clean_name}! ({self.clean_df.shape[0]} rows)")

    # If the clean data is already saved, load it (will throw an error if the file is not found)
    def load_clean_data(self):
        if self.output_name is None:
            self.output_name = self.file_name
        print(f"{self.name} : Loading clean data from {self.clean_path}{self.output_name}")

        # read the csv file and set the columns, but this is a big file!
        self.clean_df = pd.read_csv(f'{self.clean_path}{self.output_name}', low_memory=False, encoding='utf-8')

        # set the column with self.columns
        self.clean_df.columns = self.columns

    # Checks if there are missing values in the raw data and that it conforms to the expected structure
    def check_clean_data(self):
        raise NotImplementedError

    # Function that will be defined by children classes
    def clean_raw_data(self):
        raise NotImplementedError

    # Execute all the cleaning steps
    def pipeline(self):
        if not self.loaded:
            print(f"{self.name} : This object does not come from a local file, the pipeline cannot be executed")
            return
        self.fetch_raw_data()
        self.clean_raw_data()
        self.write_clean_data()