import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from src.models.trend_by_gender import *

def plot_gender_proportion():
    """
    Plot the proportion of male vs female names influenced using Matplotlib.
    :return: None. Displays a pie chart of the proportion of male and female names.
    """

    # Load cleaned dataframe
    df = pd.read_csv("data/clean/gender_name_influenced_prophet.csv")

    # Calculate the proportion of male vs female names influenced
    gender_counts = df['Gender'].value_counts()

    # Create the pie chart
    fig, ax = plt.subplots(figsize=(8, 6))

    # Colors for the pie chart
    colors = ['blue', 'pink']  # Assuming 'M' corresponds to blue and 'F' to pink

    # Plot the pie chart
    ax.pie(
        gender_counts.values,
        labels=gender_counts.index,
        autopct='%1.1f%%',  # Display percentage
        startangle=90,  # Start pie chart at 90 degrees
        colors=colors
    )

    # Add a title
    ax.set_title('Proportion of male vs female names influenced')

    # Set transparent background
    fig.patch.set_alpha(0)  # Transparent figure background
    ax.set_facecolor((1, 1, 1, 0))  # Transparent plot background

    # Show the plot
    plt.tight_layout()
    plt.show()

def plot_genre_gender_influence():
    """
    Plots the percentage distribution of influenced baby names by gender across genres using Matplotlib.
    :return: None. Displays the plot.
    """
    # Load cleaned dataframe
    df = pd.read_csv("data/clean/gender_name_influenced_prophet.csv")

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

    # Melt the pivot table to long format for easier plotting
    genre_percentage_melted = genre_pivot.melt(
        id_vars='Genres', value_vars=['M_Percent', 'F_Percent'],
        var_name='Gender', value_name='Percentage'
    )

    # Replace 'M_Percent'/'F_Percent' with 'M'/'F' for clarity in the plot
    genre_percentage_melted['Gender'] = genre_percentage_melted['Gender'].str.replace('_Percent', '')

    # Prepare data for plotting
    genres = genre_percentage_melted['Genres'].unique()[::-1]  # Reverse order for horizontal bars
    genders = ['M', 'F']
    colors = {'M': 'blue', 'F': 'pink'}

    # Pivot the data for stacking
    data_pivot = genre_percentage_melted.pivot(index='Genres', columns='Gender', values='Percentage').fillna(0)
    data_pivot = data_pivot.loc[genres]  # Ensure the genres are in the correct order

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 8))

    # Track bottom position for stacking
    bottom = np.zeros(len(data_pivot))

    # Plot each gender's bar
    for gender in genders:
        ax.barh(
            data_pivot.index,
            data_pivot[gender],
            color=colors[gender],
            label=gender,
            left=bottom
        )
        bottom += data_pivot[gender]

    # Add labels, title, and legend
    ax.set_xlabel('Percentage of influenced names')
    ax.set_ylabel('Genre')
    ax.set_title('Percentage of influenced baby names by gender across top genres')
    ax.set_xlim(0, 100)
    ax.legend(title='Gender')

    # Set a transparent background
    fig.patch.set_alpha(0)
    ax.set_facecolor((1, 1, 1, 0))  # Transparent plot area

    # Improve layout
    plt.tight_layout()

    # Show the plot
    plt.show()