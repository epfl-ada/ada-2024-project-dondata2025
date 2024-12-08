# Some statistics come in two separate files depending on the sex of the babies. We need to merge them into a single file.
import pandas as pd
from unidecode import unidecode # To remove accents in the names -> utf-8 encoding


# Function to do the merging into one file, given the two files (male, female) and the output file paths
def merge_sex_norway(male, female, output, encoding='utf-8'):

    males = pd.read_csv(male, sep='\t', encoding=encoding)
    females = pd.read_csv(female, sep=';', encoding=encoding)

    # Add a column 'Sex' to each dataframe
    males['Sex'] = 'M'
    females['Sex'] = 'F'

    # Concatenate the two dataframes
    all_data = pd.concat([males, females])

    # Remove accents from the names
    all_data['first name'] = all_data['first name'].apply(lambda x: unidecode(x))

    # Save the result
    all_data.to_csv(output, index=False, encoding="utf-8")

    print(f"Data has been merged into {output}")

merge_sex_norway('data/raw/names/norway/boy norway.csv', 'data/raw/names/norway/girl norway.csv', 'data/raw/names/norway/norway_merged.csv', encoding="iso-8859-1")