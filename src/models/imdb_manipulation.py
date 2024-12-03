import pandas as pd

def get_movie_votes(datapath):
    """
    Function to get the votes of the movies
    :param datapath: str
    :return: DataFrame
    """
    # Reading title basics
    title_basics = pd.read_csv(f'{datapath}/title.basics.tsv', sep='\t', low_memory=False)
    # Keeping only movies
    title_basics = title_basics[title_basics['titleType'] == 'movie']
    print(f"There are {len(title_basics)} movies in the imdb dataset.")
    # Reading title ratings
    title_ratings = pd.read_csv(f'{datapath}/title.ratings.tsv', sep='\t', low_memory=False)
    # Merging the two dataframes on the tconst column
    title_basics_ratings = pd.merge(title_basics, title_ratings, on='tconst', how='inner')
    # Keeping only the columns we need
    title_basics_ratings = title_basics_ratings[['primaryTitle', 'originalTitle', 'numVotes', 'averageRating']] 
    # drop na values
    title_basics_ratings = title_basics_ratings.dropna()
    return title_basics_ratings

def merge_with_characters(imdb_df, characters_df):
    """
    Function to merge the imdb data with the characters data
    :param imdb_df: DataFrame
    :param characters_df: DataFrame
    :return: DataFrame
    """
    char_rating = characters_df.merge(
        imdb_df, 
        left_on='Movie_name', 
        right_on='primaryTitle', 
        how='left'
    )
    char_rating = char_rating.drop_duplicates()

    print(f"There are {char_rating.shape[0]} rows in the merged dataset")
    return char_rating