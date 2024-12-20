import pandas as pd
import plotly.express as px
from src.models.trend_by_genres import *


def show_top10_movie_genre_amplitude():
    exploded_df = load("data/clean/influenced_prophet_with_genres.csv")
    genre_influence = get_top_genre_influence(exploded_df, top_n=10)
    plot_top_genres(genre_influence, metric ='Mean Difference')



def show_influence_amplitude_by_movie_genre():
    exploded_df = load("data/clean/influenced_prophet_with_genres.csv")
    genre_influence = get_top_genre_influence(exploded_df, top_n=10)
    top_names_by_genre = get_top_names_by_genre(exploded_df)
    plot_treemap(top_names_by_genre)

def show_top_genre_by_count():
    names_influenced = load("data/clean/influenced_prophet_with_genres.csv")
    top_genres = count_top_genres(names_influenced, top_n=10)
    print("Top Genres:")
    top_genres.head()
    plot_top_genres(top_genres, metric = 'Count')

def show_top10_genre_occurence():
    names_influenced = load("data/clean/influenced_prophet_with_genres.csv")
    top_genres = count_top_genres(names_influenced, top_n=10)
    names_influenced.head()
    top_names_with_movies = find_top_names_with_movies(names_influenced, top_genres, top_n_names=3)
    plot_treemap_with_movies(top_names_with_movies)





    





  



