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
    print(f"There are {len(title_ratings)} movies in the title dataset.")

    # Merging the two dataframes on the tconst column
    title_basics_ratings = pd.merge(title_basics, title_ratings, on='tconst', how='inner')
    # Keeping only the columns we need
    title_basics_ratings = title_basics_ratings[['primaryTitle', 'originalTitle', 'numVotes', 'averageRating']] 
    # drop na values
    title_basics_ratings = title_basics_ratings.dropna()
    print(f"There are {len(title_basics_ratings)} movies in the title-basic merged dataset before treating duplicates.")
    
    # Aggregation of ratings and basics so that there is no duplicates due to different countries origins of votes for movies
    aggregated_imdb = title_basics_ratings.groupby('primaryTitle').apply(lambda group: pd.Series({
        'weightedAverageRating': round((group['numVotes'] * group['averageRating']).sum() / group['numVotes'].sum(), 2),
        'totalVotes': group['numVotes'].sum()})
        ).reset_index()


    # adding a column to weighted average rating and total votes
    #imdb_votes = title_basics_ratings.merge(aggregated_imdb, on='primaryTitle', how='left')


    return aggregated_imdb


def is_blockbuster(row, votes_threshold=1000000, rating_threshold=8.0):
    """
    Determines if a movie is a blockbuster based on total votes and weighted average rating.
    :param row: A row of the DataFrame
    :param votes_threshold: The minimum number of votes to qualify as a blockbuster
    :param rating_threshold: The minimum average rating to qualify as a blockbuster
    :return: Boolean (True if blockbuster, False otherwise)
    """
    return row['totalVotes'] > votes_threshold and row['weightedAverageRating'] >= rating_threshold


def merge_imdb_and_dataset(imdb_df, characters_df):
    """
    Function to merge the imdb data with the characters data
    :param imdb_df: DataFrame
    :param characters_df: DataFrame
    :return: DataFrame
    """
    print("Size of imdb dataset before merging: ", imdb_df.shape)
    print("Size of mov_char_data dataset before merging: ", characters_df.shape)
    char_rating = characters_df.merge(
        imdb_df, 
        left_on='Movie_name', 
        right_on='primaryTitle', 
        how='left'
    )
    char_rating = char_rating.drop_duplicates()

    print(f"There are {char_rating.shape[0]} rows in the merged dataset")
    return char_rating