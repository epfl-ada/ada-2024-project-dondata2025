import pandas as pd
import matplotlib.pyplot as plt

def show_influence_by_eras():
    prophet = pd.read_csv("data/clean/influenced_names_prophet.csv")
    influenced_prophet = prophet[prophet["Influenced"] > 0]
    influenced_prophet = influenced_prophet.copy()  # Create a deep copy to avoid warnings
    influenced_prophet.loc[:, "Era"] = pd.cut(
        influenced_prophet.loc[:, "Year"],
        bins=[1960, 1970, 1980, 1990, 2000, 2020],
        labels=["60s", "70s", "80s", "90s", "00s"]
    )
    eras = influenced_prophet.groupby("Era", observed=False).size().reset_index(name="Count")
    fig, ax = plt.subplots()
    ax.bar(eras['Era'], eras['Count'])
    ax.set_title('Number of influenced names per Era')
    ax.set_xlabel('Era')
    ax.set_ylabel('Count')
    fig.tight_layout()
    plt.show()

