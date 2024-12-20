import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


#### Study of Norwegians total dataset


def norwegian_names_trend_per_decade():
    norwegian_df = pd.read_csv('data/clean/names/norway_merged.csv')


    # Create a new column for 10-year periods
    norwegian_df['Period'] = (norwegian_df['Year'] // 10) * 10  # Group by decades (e.g., 1960-1969 becomes 1960)

    # Aggregate by Period, Name, and Year
    aggregated_data = (
        norwegian_df.groupby(['Period', 'Name', 'Year'], as_index=False)['Count']
        .sum()  # Sum counts for the same name within the same period and year
    )

    #  Get top 10 names per period
    top_names_by_period = (
        aggregated_data.groupby(['Period', 'Name'], as_index=False)['Count']
        .sum()  # Sum total counts for the entire period
        .sort_values(['Period', 'Count'], ascending=[True, False])  # Sort within each period
        .groupby('Period', as_index=False)
        .head(10)  # Keep only the top 10 names per period
    )

    # Prepare the frames for each period
    frames = []
    for period in top_names_by_period['Period'].unique():
        # Get the top 10 names for the current period
        top_names = top_names_by_period[top_names_by_period['Period'] == period]['Name'].tolist()
        
        # Filter data for the top 10 names in this period
        filtered_data = aggregated_data[(aggregated_data['Period'] == period) & (aggregated_data['Name'].isin(top_names))]
        
        # Ensure all years in the period are covered for each name
        all_years = list(range(period, period + 10))
        filled_data = []
        for name in top_names:
            name_data = filtered_data[filtered_data['Name'] == name]
            # Fill missing years with 0 counts
            name_data = name_data.set_index('Year').reindex(all_years, fill_value=0).reset_index()
            name_data['Name'] = name  # Ensure the name column is preserved
            filled_data.append(name_data)
        
        # Combine all filled data into one DataFrame
        combined_data = pd.concat(filled_data)
        
        # Add line traces for the evolution of each name
        line_traces = []
        for name in top_names:
            name_data = combined_data[combined_data['Name'] == name]
            line_traces.append(go.Scatter(
                x=name_data['Year'],
                y=name_data['Count'],
                mode='lines',
                name=name,
                line=dict(width=2),
                showlegend=False,  # Hide legend for simplicity
            ))

        # Add text annotation for the top names below the plot
        text = f"Top 10 Names in {period}s: " + ", ".join(top_names)
        frame = go.Frame(
            data=line_traces,
            name=str(period),
            layout=go.Layout(
                annotations=[
                    dict(
                        text=text,
                        x=0.5,  # Center horizontally
                        y=-0.2,  # Position below the plot
                        xref="paper", yref="paper",
                        showarrow=False,
                        font=dict(size=14),
                        align="center",  # Align text to the center
                    )
                ]
            )
        )
        frames.append(frame)

    # Create the initial figure
    initial_period = min(top_names_by_period['Period'].unique())
    initial_top_names = top_names_by_period[top_names_by_period['Period'] == initial_period]['Name'].tolist()
    initial_filtered_data = aggregated_data[(aggregated_data['Period'] == initial_period) & (aggregated_data['Name'].isin(initial_top_names))]

    # Ensure all years are filled for the initial period
    all_years = list(range(initial_period, initial_period + 10))
    filled_initial_data = []
    for name in initial_top_names:
        name_data = initial_filtered_data[initial_filtered_data['Name'] == name]
        name_data = name_data.set_index('Year').reindex(all_years, fill_value=0).reset_index()
        name_data['Name'] = name
        filled_initial_data.append(name_data)

    combined_initial_data = pd.concat(filled_initial_data)

    initial_data = []
    for name in initial_top_names:
        name_data = combined_initial_data[combined_initial_data['Name'] == name]
        initial_data.append(go.Scatter(
            x=name_data['Year'],
            y=name_data['Count'],
            mode='lines',
            name=name,
            line=dict(width=2),
            showlegend=False,
        ))

    initial_text = f"Top 10 Norwegian Names in {initial_period}s:<br>" + ",<br>".join(initial_top_names)

    fig = go.Figure(
        data=initial_data,
        layout=go.Layout(
            annotations=[
                dict(
                    text=initial_text,
                    x=-0.3, y=0.95,
                    xref="paper", yref="paper",
                    showarrow=False,
                    font=dict(size=16),
                    align="center",
                )
            ],
            sliders=[dict(
                active=0,
                currentvalue={"prefix": "Period: "},
                pad={"t": 50},
                steps=[
                    dict(
                        method="animate",
                        args=[
                            [str(period)],  # Name of the frame
                            {"mode": "immediate", "frame": {"duration": 500, "redraw": True}}  # Animation settings
                        ],
                        label=f"{period}s",
                    )
                    for period in top_names_by_period['Period'].unique()
                ],
            )],
        ),
        frames=frames
    )

    fig.show()



def evolution_norwegian_names():
    norwegian_df = pd.read_csv('data/clean/names/norway_merged.csv')

    # Step 1: Add a 'Decade' column based on the 'Year' column
    norwegian_df['Decade'] = (norwegian_df['Year'] // 10) * 10

    # Step 2: Deduplicate names within each decade before processing
    norwegian_df_unique = norwegian_df.drop_duplicates(subset=['Decade', 'Name'])

    # Step 3: Group by decade and get the top 3 names for each decade
    top_names_by_decade = (
        norwegian_df_unique.groupby('Decade')
        .apply(lambda group: group.nlargest(3, 'Count')[['Decade', 'Name', 'Count']])  # Retain 'Decade' column
        .reset_index(drop=True)  # Flatten the index without dropping columns
        .groupby('Decade')['Name']
        .apply(list)
        .reset_index()
    )

    # Step 4: Merge the top names with the counts for each decade
    counts_by_decade = norwegian_df.groupby('Decade')['Count'].sum().reset_index()
    counts_with_top_names = counts_by_decade.merge(top_names_by_decade, on='Decade', how='left')

    # Step 5: Create the bar plot with Plotly
    fig = px.bar(
        counts_with_top_names,
        x='Decade',
        y='Count',
        text='Count',  # Display the count value on the bars
        labels={'Decade': 'Decade', 'Count': 'Total Norwegian Names'},
        title='Evolution of Norwegian Names Counts by Decade',
        color='Count',  # Optional: Color bars based on the count
        color_continuous_scale='Blues',
    )

    # Customize the hover template to replace "Label" with "Top 3 Names"
    fig.update_traces(
        hovertemplate="<b>Decade: %{x}</b><br>Total Norwegian Names: %{y}<br>Top 3 Names: %{customdata[0]}<extra></extra>",
        customdata=counts_with_top_names[['Name']]  # Pass top names for the tooltip
    )

    # Update layout for better visuals
    fig.update_layout(
        xaxis=dict(
            tickvals=counts_by_decade['Decade'],  # Ensure only decades appear
            title='Decade'
        ),
        yaxis_title='Total Counts of Norwegian Names',
        title_x=0.5,
        template='plotly_white'
    )

    # Show the figure
    fig.show()

   








#### Study of Norwegians influenced dataset










def norwegian_influenced_name_per_year():
    norwegian_prediction = pd.read_csv('data/clean/norway_prediction.csv')
    # keep only rows where influenced = 1
    norway_prediction_influenced = norwegian_prediction[norwegian_prediction['Influenced'] == 1]

    import plotly.express as px
    import plotly.graph_objects as go

    sort_significant = norway_prediction_influenced.sort_values(by='Year')
    sort_significant['Movie Name'] = sort_significant['Movie Name'].apply(lambda x: x.title())

    sort_significant['Label'] = sort_significant['Character Name'] + " from " + sort_significant['Movie Name']

    # 2. Prepare list of names for each year
    names_by_year = (
        sort_significant.groupby('Year')['Label']
        .apply(list)
        .to_dict()
    )

    # 3. Create a list of frames for each year
    frames = []
    for year, names in names_by_year.items():
        text = f"Influenced Norwegian Names in {year}:<br>" + ",<br>".join(names)
        frame = go.Frame(
            data=[],
            name=str(year),
            layout=go.Layout(
                annotations=[
                    dict(
                        text=text,
                        x=0.5, y=0.5,
                        xref="paper", yref="paper",
                        showarrow=False,
                        font=dict(size=16),
                        align="center",
                    )
                ]
            )
        )
        frames.append(frame)

    # 4. Create the initial figure
    initial_year = min(names_by_year.keys())
    initial_text = f"Influenced Norwegian Names in {initial_year}:<br>" + ",<br>".join(names_by_year[initial_year])

    fig = go.Figure(
        data=[],
        layout=go.Layout(
            annotations=[
                dict(
                    text=initial_text,
                    x=0.5, y=0.5,
                    xref="paper", yref="paper",
                    showarrow=False,
                    font=dict(size=16),
                    align="center",
                )
            ],
            sliders=[dict(
                active=0,
                currentvalue={"prefix": "Year: "},
                pad={"t": 50},
                steps=[
                    dict(
                        method="animate",
                        args=[
                            [str(year)],  # Name of the frame
                            {"mode": "immediate", "frame": {"duration": 0, "redraw": True}},
                        ],
                        label=str(year),
                    )
                    for year in names_by_year.keys()
                ],
            )],
        ),
        frames=frames
    )

    # 5. Show the figure
    fig.show()







def evolution_norwegian_influenced_names():
    norway_prediction = pd.read_csv('data/clean/norway_prediction.csv')
    norway_prediction_influenced = norway_prediction[norway_prediction['Influenced'] == 1]



    sort_significant = norway_prediction_influenced.sort_values(by='Year')
    sort_significant['Movie Name'] = sort_significant['Movie Name'].apply(lambda x: x.title())
    sort_significant['Label'] = sort_significant['Character Name'] + " from " + sort_significant['Movie Name']


    # Step 1: Add a 'Decade' column based on the 'Year' column
    sort_significant['Decade'] = (sort_significant['Year'] // 10) * 10

    # Group by decade and get the top 3 names for each decade
    top_names_by_decade = (
        sort_significant.groupby('Decade')
        .apply(lambda group: group.nlargest(3, 'Count')[['Decade', 'Label', 'Count']])  # Retain 'Decade' column
        .reset_index(drop=True)  # Flatten the index without dropping columns
        .groupby('Decade')['Label']
        .apply(list)
        .reset_index()
    )

    # Merge the top names with the counts for each decade
    counts_by_decade = sort_significant.groupby('Decade')['Count'].sum().reset_index()
    counts_with_top_names = counts_by_decade.merge(top_names_by_decade, on='Decade', how='left')

    # Create the bar plot with Plotly
    # Create the bar plot with Plotly
    fig = px.bar(
        counts_with_top_names,
        x='Decade',
        y='Count',
        text='Count',  # Display the count value on the bars
        labels={'Decade': 'Decade', 'Count': 'Total Influenced Names'},
        title='Evolution of Norwegian Influenced Names Counts by Decade',
        color='Count',  # Optional: Color bars based on the count
        color_continuous_scale='Blues',
    )

    # Customize the hover template to replace "Label" with "Top 3 Names"
    fig.update_traces(
        hovertemplate="<b>Decade: %{x}</b><br>Total Influenced Names: %{y}<br>Top 3 Names: %{customdata[0]}<extra></extra>",
        customdata=counts_with_top_names[['Label']]  # Pass top names for the tooltip
    )

    # Update layout for better visuals
    fig.update_layout(
        xaxis=dict(
            tickvals=counts_by_decade['Decade'],  # Ensure only decades appear
            title='Decade'
        ),
        yaxis_title='Total Counts of Norwegian Names Influenced',
        title_x=0.5,
        template='plotly_white'
    )

    # Show the figure
    fig.show()






