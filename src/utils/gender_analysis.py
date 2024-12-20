import pandas as pd
import plotly.express as px
from src.models.trend_by_gender import *

def plot_gender_proportion(df):
    """
    Plot the proportion of male vs female names influenced.
    :param df: DataFrame with a 'Gender' column.
    :return: None. Displays a pie chart of the proportion of male and female names.
    """
    # Calculate the proportion of male vs female names influenced
    gender_counts = df['Gender'].value_counts()

    # Create a pie chart
    fig = px.pie(
        gender_counts,
        values=gender_counts.values,
        names=gender_counts.index,
        title='Proportion of Male vs Female Names Influenced'
    )

    # Set transparent background
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot background
        paper_bgcolor='rgba(0,0,0,0)'  # Transparent chart background
    )

    # Show the pie chart
    fig.show()

def plot_genre_gender_influence(df):
    """
    Plots the percentage distribution of influenced baby names

    Parameters:
    - df (DataFrame): The dataset containing influenced baby names and genres.

    Returns:
    - None: Displays the plot.
    """

    # Drop rows where 'Genres' is NaN
    df = df.dropna(subset=['Genres'])

    # If a movie can belong to multiple genres, split them
    df['Genres'] = df['Genres'].str.split(',')

    # Explode the genres so each genre has its own row
    df_exploded = df.explode('Genres')

    # Clean whitespace in genres
    df_exploded['Genres'] = df_exploded['Genres'].str.strip()

    # Group by 'Genres' and 'Gender' and sum the 'Count'
    genre_gender_trend = df_exploded.groupby(['Genres', 'Gender'])['Count'].sum().reset_index()

    # Calculate total influence per genre
    top_genres_total = genre_gender_trend.groupby('Genres')['Count'].sum().reset_index()

    # Sort genres by total influence in descending order and select top 10
    top_genres = top_genres_total.sort_values(by='Count', ascending=False).head(10)

    # Filter the original genre_gender_trend for top genres
    genre_gender_trend_top = genre_gender_trend[genre_gender_trend['Genres'].isin(top_genres['Genres'])]

    # Pivot the table to have genders as separate columns
    genre_pivot = genre_gender_trend_top.pivot(index='Genres', columns='Gender', values='Count').fillna(0)

    # Calculate total influenced names per genre
    genre_pivot['Total'] = genre_pivot.sum(axis=1)

    # Calculate percentage for each gender within genres
    genre_pivot['M_Percent'] = (genre_pivot['M'] / genre_pivot['Total']) * 100
    genre_pivot['F_Percent'] = (genre_pivot['F'] / genre_pivot['Total']) * 100

    # Reset index to turn 'Genres' back into a column
    genre_pivot = genre_pivot.reset_index()

    # Melt the pivot table to long format for easier plotting with seaborn
    genre_percentage_melted = genre_pivot.melt(id_vars='Genres', value_vars=['M_Percent', 'F_Percent'],
                                               var_name='Gender', value_name='Percentage')

    # Replace 'M_Percent'/'F_Percent' with 'M'/'F' for clarity in the plot
    genre_percentage_melted['Gender'] = genre_percentage_melted['Gender'].str.replace('_Percent', '')

    # Create a horizontal bar plot to display percentage distribution within each genre
    fig = px.bar(
        genre_percentage_melted,
        x='Percentage',
        y='Genres',
        color='Gender',
        color_discrete_map={'M': 'blue', 'F': 'pink'},
        title='Percentage of Influenced Baby Names by Gender Across Top Genres',
        labels={'Percentage': 'Percentage of Influenced Names', 'Genres': 'Genre', 'Gender': 'Gender'},
        orientation='h'  # Horizontal bars
    )

    fig.update_layout(
        xaxis=dict(range=[0, 100]),  # Since percentages range from 0 to 100
        barmode='stack',  # Stack the bars for gender comparison
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot background
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent chart background
    )

    fig.show()