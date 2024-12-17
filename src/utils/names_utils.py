# Description: This file contains some utils functions to work with the names class.

# General imports
import pandas as pd
import sys, os

# Main characters imports
import codecs, spacy
from collections import Counter

# Change the path if the file is launched directly (not imported)
if(__name__ == '__main__'):
    sys.path.append(os.path.abspath(os.path.join('../../'))) # root directory

from src.data.names_data import NamesData


# Merge a list of names classes together 
def merge_names_data(namesData : list) -> NamesData:
    
    name = ""
    df = pd.DataFrame()

    # Check that the inputs have been cleaned
    for names in namesData:
        names.check_clean_data()
        name += f"{names.name} & "
        # Merge the data
        df = pd.concat([df, names.clean_df])
    
    # New object
    name = name[:-3] # Remove the last ' & '
    merged = NamesData(name, name.replace(" & ", "_") + ".csv", loaded=False)
    merged.clean_df = df

    # Due to the merging, the data might be duplicated -> group by and sum the counts
    merged.clean_df = merged.clean_df.groupby(['Year', 'Name', 'Sex']).sum().reset_index()
    # sort data
    merged.clean_df = merged.clean_df.sort_values(by=['Year', 'Name', 'Sex'])

    merged.check_clean_data()
    return merged

def to_csv(self, filepath: str, index: bool = False):
    """
    Saves the clean_df DataFrame to a CSV file.
    :param filepath: The path to save the CSV file.
    :param index: Whether to include the index in the saved file.
    """
    self.clean_df.to_csv(filepath, index=index)


# Defining here some functions to extract the names from the plot summaries
def get_film_name_and_date(wiki_id, movies_chars_joined):
    """
    Retrieves the film name for a given Wikipedia ID from the movies_chars_joined DataFrame.

    Args:
        wiki_id (int): The Wikipedia ID of the movie.
        movies_chars_joined (pd.DataFrame): A DataFrame with columns 'Wikipedia_movie_ID' 
                                            and 'Movie_name'.

    Returns:
        str: The name of the movie if found, otherwise None.
        str: The release date of the movie if found, otherwise None.
        
    """
    filtered_data = movies_chars_joined[movies_chars_joined['Wikipedia_movie_ID'] == wiki_id]
    if not filtered_data.empty:
        date = filtered_data['Release_date'].iloc[0]
        # convert to a datetime object
        date = pd.to_datetime(date)
        return filtered_data['Movie_name'].iloc[0], date
    return None, None

# Function to map characters to their corresponding actors
def map_characters_to_actors(movies_chars_joined):
    # Strip spaces and convert to lowercase to avoid case and whitespace issues
    name = name.strip().lower()
    actor_name = 'Unknown Actor'
    
    # Iterate through all character names in mov_char_data to check for partial matches
    for char_name in movies_chars_joined['Character_name']:
        char_name_normalized = char_name.strip().lower()  # Normalize the character name
        
        # Check if the character name contains the input name as a substring
        if name in char_name_normalized:
            actor_name = movies_chars_joined[movies_chars_joined['Character_name'] == char_name]['Actor_name'].iloc[0]
            break  # Break once a match is found
    
    return actor_name

# Function to extract Names and filter 
def extract_names(text):
    """
    Extracts names from a given text using spaCy and returns a list of (name, frequency) tuples.

    Args:
        text (str): The text to extract names from.

    Returns:
        list: A list of (name, frequency) tuples sorted by frequency in descending order.
    """
    # Initialize a Counter to store name frequencies
    name_counts = Counter() 

    # Initialize the spacy model
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)

    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            name_counts[ent.text] += 1
            
    # Consolidate similar names
    consolidated_counts = Counter()
    names = sorted(name_counts.keys(), key=len, reverse=True)  # Sort by length to prioritize full names

    for name in names:
        if any(name in longer_name and name != longer_name for longer_name in consolidated_counts):
            # If name is a substring of a longer name, add its count to the longer name
            for longer_name in consolidated_counts:
                if name in longer_name:
                    consolidated_counts[longer_name] += name_counts[name]
                    break
        else:
            consolidated_counts[name] = name_counts[name]

    # Sort names by count in descending order
    sorted_counts = consolidated_counts.most_common()  # Returns a list of (name, count) tuples sorted by count
    
    return sorted_counts
    
def main_name_per_movie(plot_summaries_path, movies_chars_joined):
    # Load plot summaries
    with codecs.open(plot_summaries_path, encoding="utf8") as file:
        content = file.read()

    # Cut the content into lines
    df_data = cut_plots(content, movies_chars_joined)

    # Extract names for each row
    extracted_data = []
    for _, row in df_data.iterrows():
        plot_summary = row['Plot Summary']
        wikipedia_id = row['Wikipedia ID']
        movie_name = row['Movie Name']
        year = row['Year']

        # Use the extract_names function on the plot summary to get character names and their frequencies
        names = extract_names(plot_summary)

        # Append each name, its frequency, and associated metadata to the extracted data list
        for name, frequency in names:
            extracted_data.append({
                'Wikipedia ID': wikipedia_id,
                'Movie Name': movie_name,
                'Year': year,
                'Character Name': name,
                'Count': frequency
            })
    # Convert the extracted data to a DataFrame
    result_df = pd.DataFrame(extracted_data)

    # Filter out names with low frequency
    threshold = 2
    print(result_df.columns)
    filtered_names_df = result_df[result_df['Count'] >= threshold]

    # Map characters to actors
    #filtered_names_df['Actor'] = filtered_names_df['Wikipedia ID'].apply(map_characters_to_actors(movies_chars_joined))

    print(f"Done! Extracted {len(filtered_names_df)} names from plot summaries.")

    return filtered_names_df


def cut_plots(content, movies_chars_joined):
    """
    Extracts Wikipedia ID, movie names, and plot summaries from raw text content,
    filtering out plots that don't match any Wikipedia ID in the provided DataFrame.

    Args:
        content (str): The raw content of the text file, where each line is formatted 
                       as 'Wikipedia ID<tab>Plot Summary'.
        movies_chars_joined (pd.DataFrame): A DataFrame with columns 
                                            'Wikipedia_movie_ID' and 'Movie_name', 
                                            used to map IDs to movie names.

    Returns:
        pd.DataFrame: A DataFrame with columns: 'Wikipedia ID', 'Movie Name', 'Plot Summary'.
    """
    data = []
    columns = ['Wikipedia ID', 'Movie Name', 'Plot Summary', 'Year']

    # Split the content into lines
    plots = content.strip().split("\n")
    
    # Process each line
    for line in plots:
        # Split the line by tabs to separate Wikipedia ID and plot summary
        film_data = line.split("\t")
        if len(film_data) == 2:  # Ensure the line has both ID and summary
            try:
                wikipedia_id = int(film_data[0].strip())  # Convert Wikipedia ID to integer
                plot_summary = film_data[1].strip()

                # Get the film name for this ID
                film_name, date = get_film_name_and_date(wikipedia_id, movies_chars_joined)

                # Only add the entry if the film name exists
                if film_name is not None and date is not None:
                    # It's a date time object, we only want the year
                    year = date.year
                    data.append([wikipedia_id, film_name, plot_summary, year])
            except ValueError:
                # Skip lines with invalid Wikipedia ID formats
                continue

    return pd.DataFrame(data, columns=columns)


def normalize_names(column):
    """
    Function to normalize the names in a column to have a batter chance of matching with the names in the NamesData class
    :param names_data: Series : The column containing the names
    :return: Series : The column with the normalized names (copy)
    """
    from unidecode import unidecode

    out = column.copy()
    out = out.str.upper() # Upper case
    # remove accents
    out = out.apply(lambda x: unidecode(x))
    # remove special characters
    out = out.str.replace(r'[^A-Z\s]', '')
    # remove multiple spaces
    out = out.str.replace(r'\s+', ' ')
    # remove leading and trailing spaces
    out = out.str.strip()

    # characters names might be different from just the first name format and we don't really have a formal way of knowing which parts is the relevant one
    # "Captain Jack Sparrow" -> "Jack Sparrow" -> "Jack" (Couldn't find a way to do this in a general way) 
    # We will split the name on the spaces and take the first part, even though we might lose some information due to characters like "Princess Leia"
    out = out.str.split(' ').str[0]

    return out
    


def chars_and_names_intersection(main_chars, names_data):
    """
    Function to get the intersection between the main characters and the top movies per year
    :param main_chars: DataFrame : The DataFrame with the main characters
    :param names_data: NamesData : The class containing the names we want to have an intersection with
    :return: DataFrame : The DataFrame of the format of main_chars, but with only the intersection of the names
    """

    names_df = names_data() # We use only the Name column here
    # get the normalized names in the main_chars
    main_chars_names = normalize_names(main_chars['Character Name'])
    # add it as a temporary column in the df
    main_chars['Normalized_name'] = main_chars_names
    # get the intersection
    intersection = main_chars[main_chars['Normalized_name'].isin(names_df['Name'])]

    print(f"Fraction of the main characters in the names data : {len(intersection) / len(main_chars)}")

    # Now we have the issue that a name was given to both a women or a men -> w

    return intersection    
