import pandas as pd
import matplotlib.pyplot as plt

def trend_eval_ranking(df_babies, df_movies):
    """
    Function to evaluate the trend of a name based on the ranking of a movie character
    :param names_data: NamesData object
    :param mov_char_data: MovieCharacterData object
    :return: DataFrame
    """
    # Creating a new column for the release year (without month and day) of the movie
    df_movies['Release_year'] = df_movies['Release_date'].dt.year
    # Ditching entries with nan revenue 
    df_movies = df_movies.dropna(subset=['Revenue'])
    # Taking only the first name of the character name
    df_movies.loc[:, 'Character_name'] = df_movies['Character_name'].str.split().str[0]
    # Putting every character name in upper case
    df_movies.loc[:, 'Character_name'] = df_movies['Character_name'].str.upper()

    # Taking only characters of the top 100 characters by revenue every year
    df_movies = (df_movies[df_movies["numVotes"] >= 100000]
        .groupby('Release_year')
        .apply(lambda x: x.nlargest(100, 'averageRating'))
        .reset_index(drop=True))

    merged_df = df_babies.merge(
        df_movies[['Character_name', 'Release_year', 'Movie_name']],
        left_on='Name', right_on='Character_name',
        how='inner'
    )


    # Function to analyze the trend of a character name
    def analyze_trend(group, window_before = 5, window_after = 5):
        movie_name = group['Movie_name'].iloc[0]
        release_year = group['Release_year'].iloc[0]
        pre_movie = group[(group['Year'] < release_year) & (group['Year'] >= release_year - window_before)]
        post_movie = group[(group['Year'] >= release_year) & (group['Year'] <= release_year + window_after)]
        pre_avg = pre_movie['Count'].mean()
        post_avg = post_movie['Count'].mean()
        trend_increase = post_avg - pre_avg
        return pd.Series({'pre_avg': pre_avg, 'post_avg': post_avg, 'trend_increase': trend_increase, 'movie_name': movie_name, 'release_year': release_year})



    # Apply the function to each character name
    groupedByName =  merged_df.groupby('Character_name')
    trend_df = groupedByName.apply(analyze_trend).reset_index()
    ranking = trend_df.sort_values('trend_increase', ascending=False)
    return ranking

def plot_trend(name, sex, ranking, df_babies):
    character_trend = df_babies[(df_babies['Name'] == name) & (df_babies["Sex"] == sex)]
    plt.plot(character_trend['Year'], character_trend['Count'], label='Baby Name Count')
    plt.title(f'Trend of Baby Name Count for "{name}" Over Time')
    plt.xlabel('Year')
    plt.ylabel('Count')

    movname = ranking[ranking['Character_name'] == name]['movie_name'].iloc[0]

    # add vertical lines for the release year of the movie influencing the trend
    plt.axvline(x=ranking[ranking['Character_name'] == name]['release_year'].iloc[0], color='r', linestyle='--', label=f'{movname} Release Year')

    plt.legend()
    plt.show()