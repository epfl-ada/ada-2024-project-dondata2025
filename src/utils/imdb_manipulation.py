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
    print(f"There are {len(title_basics)} movies in the IMDB basic dataset.")
    
    # Reading title ratings
    title_ratings = pd.read_csv(f'{datapath}/title.ratings.tsv', sep='\t', low_memory=False)
    print(f"There are {len(title_ratings)} movies in the IMDB ratings dataset.")

    # Merging the two dataframes on the tconst column (movie identifier)
    title_basics_ratings = pd.merge(title_basics, title_ratings, on='tconst', how='inner')

    # Keeping only the columns we need
    title_basics_ratings = title_basics_ratings[['primaryTitle', 'originalTitle', 'numVotes', 'averageRating', 'startYear']] 

    # drop na values
    title_basics_ratings = title_basics_ratings.dropna()
    print(f"There are {len(title_basics_ratings)} movies in the title-basic merged dataset before treating duplicates.")
    
    # Aggregation of ratings and basics so that there is no duplicates due to different countries origins of votes for movies
    aggregated_imdb = title_basics_ratings.groupby(['primaryTitle', 'startYear']).apply(lambda group: pd.Series({
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


def get_all_blockbusters(datapath, votes_threshold=300000, rating_threshold=7.5):
    """
    Function to get all the blockbusters from IMDB data
    :param datapath: str
    :return: DataFrame
    """

    imdb_df = get_movie_votes(datapath)
    # keeping only rows wher is_blockbuster is True
    imdb_df['is_blockbuster'] = imdb_df.apply(is_blockbuster, args=(votes_threshold, rating_threshold), axis=1)
    return imdb_df.sort_values(by='weightedAverageRating', ascending=False)

    

def merge_imdb_and_dataset(imdb_df, cmu_df):
    """
    Function to merge the IMDb data with the CMU dataset.
    :param imdb_df: DataFrame
    :param cmu_df: DataFrame
    :return: DataFrame
    """
    from rapidfuzz import process, fuzz

    # Threshold for similarity
    similarity_threshold = 90  # RapidFuzz scores are 0-100

    # Preprocess column names and values
    imdb_df = imdb_df.rename(columns={"primaryTitle": "Movie_name"})
    imdb_df["Movie_name"] = imdb_df["Movie_name"].str.lower()
    cmu_df["Movie_name"] = cmu_df["Movie_name"].str.lower()

    # Exact match merge
    merged_df = cmu_df.merge(imdb_df, on="Movie_name", how="outer", indicator=True)

    # Identify unmatched titles
    unmatched_cmu = merged_df[merged_df["_merge"] == "left_only"]["Movie_name"].dropna().to_list()
    unmatched_imdb = merged_df[merged_df["_merge"] == "right_only"]["Movie_name"].dropna().to_list()
    
    print("Similarity-based matching...")
    # Perform similarity-based matching
    matched_rows = []
    for cmu_title in unmatched_cmu:
        # Find the best match for each CMU title in the unmatched IMDb titles
        match, score, _ = process.extractOne(cmu_title, unmatched_imdb, scorer=fuzz.ratio)
        if score >= similarity_threshold:
            cmu_row = cmu_df[cmu_df["Movie_name"] == cmu_title]
            imdb_row = imdb_df[imdb_df["Movie_name"] == match]

            # Combine the rows
            combined_row = cmu_row.iloc[0].combine_first(imdb_row.iloc[0])
            matched_rows.append(combined_row)

    # Convert matched rows into a DataFrame
    matched_df = pd.DataFrame(matched_rows)

    # Append the matched rows to the exact merged DataFrame
    exact_matches = merged_df[merged_df["_merge"] == "both"].drop(columns="_merge")
    final_df = pd.concat([exact_matches, matched_df], ignore_index=True)

    # Ensure no duplicates
    final_df = final_df.drop_duplicates()

    # We took the startYear from the IMDB dataset, so if the cmu "Release_date" is missing, we replace it with the IMDB startYear (converted to a datetime object)
    final_df["Release_date"] = pd.to_datetime(final_df["Release_date"], errors="coerce")
    final_df["startYear"] = pd.to_datetime(final_df["startYear"], errors="coerce")
    final_df["Release_date"] = final_df["Release_date"].combine_first(final_df["startYear"])

    # Keep only the movie with year <= 2012
    final_df = final_df[final_df["Release_date"].dt.year <= 2012]

    # Drop the startYear column and duplicates based on the Wikipedia_movie_ID
    final_df = final_df.drop(columns="startYear")
    final_df = final_df.drop_duplicates(subset="Wikipedia_movie_ID")

    return final_df


def biggest_rating_per_year(cmu_imdb_merged_df, n, first_year, by_num_votes=False):
    """
    Function to get the biggest n rating per year
    :param cmu_imdb_merged_df: DataFrame
    :param n: int : The number of biggest rating to keep per year
    :param first_year: int : The first year to consider
    :return: DataFrame : Same dataframe, but with only the n biggest rating per year
    """

    # Make sure that every movie has a name
    cmu_imdb_merged_df = cmu_imdb_merged_df.dropna(subset=["Movie_name"])

    # Convert the Release_date column to datetime
    cmu_imdb_merged_df["Release_date"] = pd.to_datetime(cmu_imdb_merged_df["Release_date"])

    # Use the datetiem object to make a year column
    cmu_imdb_merged_df["year"] = cmu_imdb_merged_df["Release_date"].dt.year
    
    temp = cmu_imdb_merged_df[cmu_imdb_merged_df["year"] >= first_year].copy()

    # We want to be sure that a movie can only appear once in the list -> we group by the name and the year
    temp = temp.groupby(["Movie_name"]).first().reset_index() 

    # depending on "by_num_votes", we either sort by weightedAverageRating or totalVotes
    if by_num_votes:
        temp = temp.sort_values(by="totalVotes", ascending=False)
    else:
        temp = temp.sort_values(by="weightedAverageRating", ascending=False)

    temp = temp.groupby("year").head(n)
    #keep only the names of the movies
    temp = temp[["Movie_name", "year"]]

    #We now use this list to filter the original dataframe, we only keep the movies that are in the list
    cmu_imdb_merged_df = cmu_imdb_merged_df.merge(temp, on=["Movie_name", "year"], how="inner")

    # For better visualization, we sort the dataframe by year, name and rating
    return cmu_imdb_merged_df.sort_values(by=["year", "Movie_name", "weightedAverageRating"], ascending=[True, True, False])
