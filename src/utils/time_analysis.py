import pandas as pd
import plotly.express as px

def show_influence_by_eras():
    prophet = pd.read_csv("data/clean/influenced_names_prophet.csv")
    influenced_prophet = prophet[prophet["Influenced"] > 0]
    influenced_prophet["Era"] = pd.cut(influenced_prophet["Year"], bins=[1960, 1970, 1980, 1990, 2000, 2020], labels=["60s", "70s", "80s", "90s", "00s"])
    eras = influenced_prophet.groupby("Era").size().reset_index(name="Count")
    fig = px.bar(eras, x="Era", y="Count", title="Number of influenced names per Era")
    fig.update_layout(
            xaxis_title='Era',
            yaxis_title='Count',
            template="plotly_white",
            width=800
            )
    fig.show()

