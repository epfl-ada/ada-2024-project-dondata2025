import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
import json

# --- Data Preparation ---
merged_df = pd.read_csv("data/clean/influenced_prophet_with_genres.csv")
merged_df['Genres'] = merged_df['Genres'].str.split(', ')
exploded_df = merged_df.explode('Genres')

top_25_genres = (
    exploded_df.groupby('Genres')['Mean Difference']
    .sum()
    .reset_index()
    .sort_values(by='Mean Difference', ascending=False)
    .head(25)['Genres']
)

filtered_df = exploded_df[exploded_df['Genres'].isin(top_25_genres)]

top_names_by_genre = (
    filtered_df.groupby(['Genres', 'Normalized_name'])['Mean Difference']
    .sum()
    .reset_index()
    .sort_values(['Genres', 'Mean Difference'], ascending=[True, False])
    .groupby('Genres')
    .head(3)
)

unique_genres = top_names_by_genre['Genres'].unique()

# Arrange 25 genres into 3 rows: 8, 9, 8
row1_genres = unique_genres[:8]
row2_genres = unique_genres[8:17]
row3_genres = unique_genres[17:25]

def make_hex_divs(genres):
    return [
        html.Div(
            html.Span(genre),  # wrap text in a span
            id={'type': 'genre-hex', 'index': genre},
            className='hex',
            n_clicks=0
        )
        for genre in genres
    ]

top_row_hex = make_hex_divs(row1_genres)
middle_row_hex = make_hex_divs(row2_genres)
bottom_row_hex = make_hex_divs(row3_genres)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    html.Div("Select a movie genre:", className='title'),
    html.Div([
        html.Div(top_row_hex, className='honeycomb-row', style={"transform": "translate(50px, 31px)"}),
        html.Div(middle_row_hex, className='honeycomb-row', style={"transform": "translateX(50px)"}),
        html.Div(bottom_row_hex, className='honeycomb-row', style={"transform": "translate(50px, -31px)"}),
    ], className='honeycomb-container'),
    html.Div([
        dcc.Graph(id='genre-bar-plot', style={'width': '100%', 'height': '80vh'})
    ], className='graph-container'),
    dcc.Store(id='selected-genre', data=unique_genres[0])
], className='main-container')


@app.callback(
    Output('genre-bar-plot', 'figure'),
    Input('selected-genre', 'data')
)
def update_figure(selected_genre):
    filtered_data = top_names_by_genre[top_names_by_genre['Genres'] == selected_genre]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=filtered_data['Normalized_name'],
        y=filtered_data['Mean Difference'],
        name=selected_genre,
        marker_color='rgb(102,153,255)'
    ))
    fig.update_layout(
        title=f"Top 3 prénoms influencés par le genre '{selected_genre}'",
        xaxis_title="Names",
        yaxis_title="Mean of influence",
        template="plotly_white"
    )
    return fig

@app.callback(
    Output('selected-genre', 'data'),
    [Input({'type': 'genre-hex', 'index': g}, 'n_clicks') for g in unique_genres],
    [State('selected-genre', 'data')]
)
def update_selected_genre(*args):
    ctx = dash.callback_context
    if not ctx.triggered:
        return unique_genres[0]
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        button_id_json = json.loads(button_id)
        return button_id_json['index']

@app.callback(
    [Output({'type': 'genre-hex', 'index': g}, 'className') for g in unique_genres],
    Input('selected-genre', 'data')
)
def update_hex_classes(selected_genre):
    return [
        'hex active' if genre == selected_genre else 'hex'
        for genre in unique_genres
    ]

if __name__ == '__main__':
    app.run_server(debug=True)
