import pandas as pd
import plotly.express as px

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
    top_fig.update_layout(width=1000, height=600)
    top_fig.update_traces(
        hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>"
    )
    top_fig.write_html("docs/_includes/top_10_names_by_genres.html")
    top_fig.show()





#####  Based on proportion of influence (count) ######
def count_top_genres(df, top_n=10):
    """
    Group data by genres and calculate the total mean difference (influence score).
    Returns the top N influential genres.
    """
    df = df[df['Genres'] != 'Action/Adventure']

    genre_influence = (
        df.groupby('Genres')[['Movie-name', Normalized_name]]
        .sum()
        .reset_index()
        .sort_values(by='', ascending=False)
    )

    return genre_influence.head(top_n)




###### Based on mean influence for influenceed names ######



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
    fig = px.bar(
        genre_influence,
        x='Genres',
        y=metric,
        title='Top 10 Most Influential Movie Genres on Names',
        labels={'Mean Difference': 'Total Influence Score'},
        template='plotly_white'
    )
    fig.show()

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



This treemap is a representation of the amplitude of the influence of movie genre:

{% include treemap_top3_by_genre.html %}


this other treemap shows the most influent genre and the top 3 names for each of them, in term  propotion.
{ %include treemap_top3_by_genre_by_count.html %}

