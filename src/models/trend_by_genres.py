import pandas as pd
import plotly.express as px

# Utilitaire : Nettoyer un DataFrame de noms
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


# Utilitaire : Préparer les genres (split & explode)
def process_genres(df, subset_cols=None):
    """
    Splits and explodes the Genres column for analysis.
    """
    if subset_cols:
        df = df.drop_duplicates(subset=subset_cols)
    return df.assign(Genres=df["Genres"].str.split(", ")).explode("Genres")


# Étape 1 : Obtenir les 10 genres principaux
def get_top_10_genres(expanded_imdb_mov_char_data):
    """
    Determines the top 10 movie genres based on unique movie occurrences.
    """
    unique_movies_genres = process_genres(expanded_imdb_mov_char_data, subset_cols=["Movie_name"])
    
    # Obtenir les 10 genres principaux
    top_10_genres = unique_movies_genres["Genres"].value_counts().head(10).index.tolist()
    print("Top 10 genres:", top_10_genres)
    return top_10_genres


# Étape 2 : Filtrer les données par genres
def filter_data_by_top_genres(expanded_imdb_mov_char_data, top_10_genres):
    """
    Filters movie data to include only rows from the top 10 genres.
    """
    expanded_data_genres = process_genres(expanded_imdb_mov_char_data)
    return expanded_data_genres[expanded_data_genres["Genres"].isin(top_10_genres)]


# Étape 3 : Fusionner et analyser les prénoms
def merge_and_analyze_names(filtered_data, valid_names_df):
    """
    Merges movie data with valid names and determines the top 10 names per genre.
    """
    # Fusionner avec les prénoms valides
    merged_df = filtered_data.merge(
        valid_names_df, left_on="Character_name", right_on="Name", how="inner"
    )
    
    # Compter et regrouper les prénoms par genre
    top_names_df = (
        merged_df.groupby("Genres")["Character_name"]
        .value_counts()
        .groupby(level=0)
        .nlargest(10)
        .reset_index(level=0, drop=True)
        .reset_index(name="Count")
    )
    return top_names_df


# Étape 4 : Visualisation
def visualize_top_names(top_names_df):
    """
    Creates a treemap to visualize the top 10 names per genre.
    """
    fig = px.treemap(
        top_names_df,
        path=["Genres", "Character_name"],
        values="Count",
        title="Répartition des Top 10 Prénoms par Genre de Films",
        color="Genres",
        template="plotly_dark"
    )
    fig.show()
