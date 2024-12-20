import pandas as pd
import src.utils.pipelines as pip

def load_and_clean_influenced_names(file_path):
    """
    Load and clean the dataset of influenced names.
    :param file_path: The path to the CSV file containing the influenced names data.
    :return: A cleaned DataFrame containing the influenced names.
    """
    # Load the dataset
    prophet = pd.read_csv(file_path)

    # Filter for influenced names
    influenced_prophet = prophet[prophet["Influenced"] > 0]

    # Remove common identification mistakes such as "the", "a" or "Mr"
    influenced_prophet = influenced_prophet[~influenced_prophet["Character Name"].isin(["the", "a", "Mr"])]

    # Print the number of influenced names and the shape of the dataframe
    print("Number of influenced names with prophet: ", len(influenced_prophet))
    print(influenced_prophet.shape)

    # Drop unnecessary columns
    influenced_prophet.drop(columns=["Count", 'Mean Difference'], inplace=True)

    return influenced_prophet


def load_and_clean_character_data():
    """
    Load and clean the character names data, keeping only 'Name' and 'Sex' columns.
    :return: A cleaned DataFrame with 'Name' and 'Gender' columns.
    """
    # Load the data
    global_names, _, _, _, _ = pip.read_all_names_data()
    df_character = global_names()

    # Keep only 'Name' and 'Sex' columns
    df_character = df_character[['Name', 'Sex']]

    # Rename 'Sex' to 'Gender'
    df_character.rename(columns={'Sex': 'Gender'}, inplace=True)

    return df_character

def merge_influenced_and_character_data(influenced_prophet, df_character):
    """
    Merge the influenced names data with the character data based on 'Normalized_name' and 'Year'.
    :param influenced_prophet: DataFrame containing the influenced names data.
    :param df_character: DataFrame containing the character data with 'Name', 'Gender', and 'Year' columns.
    :return: A merged DataFrame with relevant columns.
    """
    # Perform a merge based on 'Normalized_name' == 'Name' and 'Year'
    merged_df = influenced_prophet.merge(
        df_character[['Name', 'Gender', 'Year', 'Count']],  # Select only the relevant columns
        how='left',  # Use a left join to keep all rows in influenced_prophet
        left_on=['Normalized_name', 'Year'],  # Match these columns from influenced_prophet
        right_on=['Name', 'Year']  # With these columns from df_character
    )

    # Drop the extra 'Name' column if needed (optional)
    merged_df.drop(columns='Name', inplace=True)

    return merged_df

def fill_missing_gender_and_clean(merged_df):
    """
    Fill missing values in 'Gender' column and clean data based on a reference dataset.
    :param merged_df: DataFrame containing the merged data with 'Gender' column having missing values.
    :return: A cleaned DataFrame with 'Gender' filled and specific rows dropped.
    """
    # Data to use for filling missing values
    data = {
        'Wikipedia ID': [323715, 920296, 11077335, 97758, 97646, 146947, 8695, 10645970, 23487440, 321496,
                         97758, 68245, 133648, 1210303, 950929, 697113, 3917873, 31557],
        'Movie Name': ['troy', 'somewhere in time', 'doctor zhivago', 'doctor zhivago', 'die hard', 'spider-man',
                       'dr. strangelove or: how i learned to stop worrying and love the bomb', 'rocky', 'alien',
                       'pirates of the caribbean: the curse of the black pearl', 'doctor zhivago', 'bonnie and clyde',
                       'scent of a woman', 'constantine', 'the haunting', 'big trouble in little china',
                       'chitty chitty bang bang', 'the good, the bad and the ugly'],
        'Year': [2004, 1980, 1965, 1965, 1988, 2002, 1964, 1981, 1979, 2003, 1965, 1967, 1992, 2005, 1963,
                 1986, 1968, 1966],
        'Character Name': ['Briseis', 'McKenna', 'Yuri', 'Yuri', 'Kristoff', 'Daily', 'Alexei', 'Shankar', 'Ash',
                           'Sparrow', 'Pasha', 'Moss', 'Ranger', 'Lucifer', 'Hill', 'Lo', 'Jemima', 'Blondie'],
        'Gender': ['F', 'F', 'M', 'M', 'M', 'F', 'M', 'M', 'M', 'M', 'M',
                   'M', 'M', 'M', 'M', 'M', 'F', 'F']
    }

    df_reference = pd.DataFrame(data)

    # Merge to bring in Gender information from df_reference
    merged_df = merged_df.merge(
        df_reference[['Wikipedia ID', 'Movie Name', 'Year', 'Character Name', 'Gender']],
        on=['Wikipedia ID', 'Movie Name', 'Year', 'Character Name'],
        how='left',
        suffixes=('', '_reference')
    )

    # Fill NaN values in 'Gender' using 'Gender_reference' from df_reference
    merged_df['Gender'] = merged_df['Gender'].fillna(merged_df['Gender_reference'])

    # Drop the temporary 'Gender_reference' column
    merged_df.drop(columns=['Gender_reference'], inplace=True)

    # Drop rows with 'Character Name' as 'Daily', 'Hill', or 'Lo'
    merged_df = merged_df[~merged_df['Character Name'].isin(['Daily', 'Hill', 'Lo'])]

    return merged_df
