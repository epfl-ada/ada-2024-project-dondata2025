import pandas as pd
import numpy as np
import plotly.express as px

def density_heatmap(df_rating):
    df_rating = df_rating.groupby("Movie_name",as_index=False).first()

    # Update the bin ranges to reduce sparsity
    log_bins = np.logspace(1, 7, num=15, base=10) # Creates 15 bins from 10^0 to 10^7
    # Remove the last 3 bins to reduce sparsity
    log_bins = log_bins[:-3]
    log_labels = [
        f"{int(log_bins[i]):,}-{int(log_bins[i+1]-1):,}" 
        for i in range(len(log_bins)-1)
    ]

    # Apply bins to the DataFrame
    df_rating["numVotes_bin"] = pd.cut(
        df_rating["totalVotes"], 
        bins=log_bins, 
        labels=log_labels
    )

    df_rating["averageRating_bin"] = pd.cut(df_rating["weightedAverageRating"], bins=[0,2,3,4,5, 6,7, 8, 9,10], labels=["0-2", "2-3", "3-4", "4-5", "5-6","6-7", "7-8","8-9","9-10"])

    heatmap_data = df_rating.groupby(["numVotes_bin", "averageRating_bin"]).size().reset_index(name="Movie Count")

    custom_scale = [
            [0.0, "white"],    # At 0% of the scale, the color is white
            [0.1, "lightblue"], # Transition starts from light blue
            [0.5, "blue"],     # Midway, the color becomes blue
            [1.0, "darkblue"]  # At 100% of the scale, the color is dark blue
        ]


    # Create a heatmap
    fig = px.density_heatmap(
        heatmap_data,
        x="averageRating_bin",
        y="numVotes_bin",
        z="Movie Count",
        title="Heatmap distribution of Movies by Number of Votes and Average Rating",
        labels={"numVotes_bin": "Number of Votes", "averageRating_bin": "Average Rating"},
        color_continuous_scale=custom_scale
    )

    # Max width
    fig.update_layout(width=800, height=600)

    fig.update_layout(xaxis_title="Average Rating", yaxis_title="Number of Votes", coloraxis_colorbar_title="Number of Movies")
    fig.write_html("docs/_includes/rating-votes.html")
    fig.show()