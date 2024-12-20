import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

def clean_valid_names(global_names, names_to_remove=["M", "DOCTOR"]):
    """
    Cleans the valid names DataFrame by removing unwanted names and duplicates.
    """
    valid_names_df = global_names.clean_df.copy()
    print("Initial name dataset size:", valid_names_df.shape)
    
    valid_names_df = valid_names_df[~valid_names_df["Name"].isin(names_to_remove)]
    valid_names_df = valid_names_df.drop_duplicates(subset=["Name"])
    
    print("Cleaned name dataset size:", valid_names_df.shape)
    return valid_names_df


def process_genres(df, subset_cols=None):
    """
    Splits and explodes the Genres column for analysis.
    """
    if subset_cols:
        df = df.drop_duplicates(subset=subset_cols)
    return df.assign(Genres=df["Genres"].str.split(", ")).explode("Genres")


def get_top_10_genres(expanded_imdb_mov_char_data,):
    """
    Determines the top 10 movie genres based on unique movie occurrences.
    """
    unique_movies_genres = process_genres(expanded_imdb_mov_char_data, subset_cols=["Movie_name"])
    
    # Obtenir les 10 genres principaux
    top_10_genres = unique_movies_genres["Genres"].value_counts().head(10).index.tolist()
    print("Top 10 genres:", top_10_genres)
    return top_10_genres


def filter_data_by_top_genres(expanded_imdb_mov_char_data, top_10_genres):
    """
    Filters movie data to include only rows from the top 10 genres.
    """
    expanded_data_genres = process_genres(expanded_imdb_mov_char_data)
    return expanded_data_genres[expanded_data_genres["Genres"].isin(top_10_genres)]


def merge_and_analyze_names(filtered_data, valid_names_df):
    """
    Merges movie data with valid names and determines the top 10 names per genre.
    """
    merged_df = filtered_data.merge(
        valid_names_df, left_on="Character_name", right_on="Name", how="inner"
    )
    
    top_names_df = (
        merged_df.groupby("Genres")["Character_name"]
        .value_counts()
        .groupby(level=0)
        .nlargest(10)
        .reset_index(level=0, drop=True)
        .reset_index(name="Count")
    )
    return top_names_df


def visualize_top_names(top_names_df):
    """
    Creates a treemap to visualize the top 10 names per genre.
    """
    top_fig = px.treemap(
        top_names_df,
        path=["Genres", "Character_name"],
        values="Count",
        title="Top 10 most represented names by movie genres",
        color="Genres",
        template="plotly_white"
    )
    # fixed size for better visualization
    top_fig.update_traces(
        hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>"
    )
    top_fig.write_html("docs/_includes/top_10_names_by_genres.html")
    top_fig.show()




def load(filepath):
    """
    Load the dataset, clean it, and explode the Genres column.
    """
    # Load the data
    df = pd.read_csv(filepath)
    
    # Rename the column and drop unnecessary ones
    df = df.rename(columns={"Movie Name": "Movie_name"})
    df = df.drop(columns=['Influenced', 'Character Name', 'Wikipedia_movie_ID'])
    df = df[df['Genres'] != 'Action/Adventure']

    
    # Explode Genres
    df['Genres'] = df['Genres'].str.split(', ')
    exploded_df = df.explode('Genres')
    
    return exploded_df




#####  Based on proportion of influence (count) ######


def count_top_genres(df, top_n=10):
    """
   Determine the top N genres by count
    """
   # Count occurrences of each genre
    genre_counts = df['Genres'].value_counts()
    
    # Get the top N genres
    top_genres = genre_counts.head(top_n)
    
    # Convert to a DataFrame for output
    top_genres_df = top_genres.reset_index()
    top_genres_df.columns = ['Genres', 'Count']  # Rename columns for clarity
    
    return top_genres_df
        













# viauslization 
def plot_top_genres(genre_influence, metric):
    """
    Create a bar chart for the top N genres and save it as an HTML file.
    """
    fig = px.bar(
        genre_influence,
        x='Genres',
        y=metric,
        title='Top 10 Most Influential Movie Genres on Names',
        labels={'Mean Difference': 'Total Influence Score'},
        template='plotly_white'
    )

    fig.show()

def find_top_names_for_top_genres(df, top_genres, top_n_names=3):
    """
    Determine the top N normalized names for each of the top genres.

    Parameters:
        df (DataFrame): The dataset with 'Genres' and 'Normalized_name'.
        top_genres (DataFrame): The DataFrame containing top genres with their counts.
        top_n_names (int): Number of top names to retrieve per genre.

    Returns:
        DataFrame: Top N names for each genre.
    """
    # Filter the dataset to include only rows with the top genres
    filtered_df = df[df['Genres'].isin(top_genres['Genres'])]

    # Group by genre and name, and count occurrences
    name_counts = (
        filtered_df.groupby(['Genres', 'Normalized_name'])
        .size()
        .reset_index(name='Count')
    )

    # Find the top N names for each genre
    top_names = (
        name_counts.groupby('Genres')
        .apply(lambda x: x.nlargest(top_n_names, 'Count'))
        .reset_index(drop=True)
    )

    return top_names



def find_top_names_with_movies(df, top_genres, top_n_names=3):
    """
    Determine the top N normalized names for each genre, with a list of movie names.

    Parameters:
        df (DataFrame): The dataset with 'Genres', 'Normalized_name', and 'Movie Name'.
        top_genres (DataFrame): The DataFrame containing top genres with their counts.
        top_n_names (int): Number of top names to retrieve per genre.

    Returns:
        DataFrame: Top N names for each genre with a list of associated movie names.
    """
    # Filter the dataset to include only rows with the top genres
    filtered_df = df[df['Genres'].isin(top_genres['Genres'])]

    # Group by genre and normalized name, aggregating movie names into a list
    grouped = (
        filtered_df.groupby(['Genres', 'Normalized_name', 'Movie_name'])
        .agg(
            Count=('Normalized_name', 'size'),
            Movie_Names=('Movie_name', lambda x: list(x.unique()))
        )
        .reset_index()
    )


    # Find the top N names for each genre
    top_names = (
        grouped.groupby('Genres')
        .apply(lambda x: x.nlargest(top_n_names, 'Count'))
        .reset_index(drop=True)
    )

    return top_names



def plot_treemap_with_movies(top_names_by_genre):
    """
    Plot a treemap of the top 3 influential names per genre with movie names displayed on hover.
    """
    # Ensure the movie names are in a single string for hover display
    top_names_by_genre['Movies'] = top_names_by_genre['Movie_Names'].apply(lambda x: ", ".join(x))

    # Create the treemap
    fig = px.treemap(
        top_names_by_genre,
        path=['Genres', 'Normalized_name'],
        values='Count',  # Use the count of names as the value
        title="Top 3 influenced names per most influent genre in occurence",
        template="plotly_white",
        color='Genres',
        custom_data=['Movies']  # Include aggregated movie names for hover
    )
    
    # Update hover template to display the movie list
    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>Movies: %{customdata[0]}<extra></extra>"
    )
    
    # Show and save the figure
    fig.show()
    fig.write_html("docs/_includes/treemap_top3_by_genre_by_count.html")



def proportion_of_influence(df, top_n=10):
    """
    Determine the proportion of influence for the top N genres
    """
    # Count occurrences of each genre
    genre_counts = df['Genres'].value_counts()
    
    # Get the top N genres
    top_genres = genre_counts.head(top_n)
    print(top_genres)

    # Calculate the total number of names
    total_names = len(df)
    print(total_names)

    # Calculate the proportion of influence for each genre in percentage
    top_genres_proportion = top_genres / total_names * 100
    
    # Convert to a DataFrame for output
    top_genres_proportion_df = top_genres_proportion.reset_index()
    top_genres_proportion_df.columns = ['Genres', 'Proportion (%)']  # Rename columns for clarity

    return top_genres_proportion_df





###### Based on mean influence for influenceed names ######






def get_top_genre_influence(df, top_n=10):
    """
    Group data by genres and calculate the total mean difference (influence score).
    Returns the top N influential genres.
    """
    df = df[df['Genres'] != 'Action/Adventure']

    genre_influence = (
        df.groupby('Genres')['Mean Difference']
        .sum()
        .reset_index()
        .sort_values(by='Mean Difference', ascending=False)
    )

    return genre_influence.head(top_n)

def plot_top_genres(genre_influence, metric):
    """
    Create a bar chart for the top N genres and save it as an HTML file.
    """
    fig, ax = plt.subplots()
    ax.bar(genre_influence['Genres'], genre_influence[metric], color='skyblue')
    ax.set_title('Top 10 Most Influential Movie Genres on Names')
    ax.set_xlabel('Genres')
    ax.set_ylabel('Total Influence Score')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

def get_top_names_by_genre(exploded):
    """
    For each of the top genres, find the top 3 names with the highest Mean Difference.
    """
    exploded = exploded[exploded['Genres'] != 'Action/Adventure']

    top_10_genres = (
        exploded.groupby('Genres')['Mean Difference']
        .sum()
        .reset_index()
        .sort_values(by='Mean Difference', ascending=False)
        .head(10)['Genres']
    )


    # Step 2: Filter the data to include only the top 10 genres
    filtered_df = exploded[exploded['Genres'].isin(top_10_genres)]

    # Step 3: For each genre, find the top 3 names with the biggest Mean Difference
    top_names_by_genre = (
        filtered_df.groupby('Genres', group_keys=False)
        .apply(lambda x: x.nlargest(3, 'Mean Difference'))
    )
    return top_names_by_genre


def plot_treemap(top_names_by_genre):
    """
    Plot a treemap of the top 3 influential names per genre and save it as an HTML file.
    """
    top_names_by_genre['Movie_name'] = top_names_by_genre['Movie_name'].str.title()
    # Create the treemap
    fig = px.treemap(
        top_names_by_genre,
        path=['Genres', 'Normalized_name'],
        values='Mean Difference',
        title="Top 3 Influential Names per Genre",
        template="plotly_white",
        color='Genres',
        custom_data=['Movie_name']  # Include movie names for hover
    )
    
    # Update hover template to display movie names
    fig.update_traces(
        hovertemplate= "<b>%{label}</b><br>%{customdata[0]}<extra></extra>"
    )
    
    # Show and save the figure
    fig.show()
    fig.write_html("docs/_includes/treemap_top3_by_genre.html")


