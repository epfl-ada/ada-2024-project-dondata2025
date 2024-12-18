import pmdarima as pm
import pandas as pd
from src.data.names_data import NamesData
import matplotlib.pyplot as plt
from prophet import Prophet
from causalimpact import CausalImpact
import numpy as np
import seaborn as sns



def predict_naming_ARIMA(data: NamesData, name: str, stop_year: int, nb_years: int, plot=False) -> pd.DataFrame:
    """
    Predict the evolution of a name's count by year using a SARIMA model.
    :param data: the name dataset
    :param name: the name from which we predict the evolution
    :param stop_year: the year of the event, we will predict the evolution from stop_year + 1
    :param nb_years: the number of years we want to predict
    :param plot: if True, displays diagnostic plots
    :return: a dataframe with the predictions (starting from stop_year + 1)
    """
    input_data = data().copy()

    # Filter for the specified name and aggregate counts if needed
    name_data = input_data[input_data['Name'] == name]
    name_data = name_data.groupby(['Year']).sum().reset_index()
    name_data = name_data.drop(columns=['Name'])

    # Split the dataset at the stop_year
    train_data = name_data[name_data['Year'] <= stop_year]
    true_data = name_data[name_data['Year'] >= stop_year]
    true_data = true_data[true_data['Year'] <= stop_year + nb_years]

    # Check if there is data to train the model (since some odd names might not have enough data)
    # we want to have more than 10 years of data
    if len(train_data) < 5:
        return None

    # An issue is that the data might have some missing years, we need to fill them with 0! -> 1915, 1917, 1918, 1919, 1920 -> 1916 is missing and should be filled with 0
    # We will create a new dataframe with all the years from the first year to the stop year
    # Then we will merge the two dataframes and fill the missing values with 0
    all_years = pd.DataFrame({'Year': range(train_data['Year'].min(), stop_year + 1)})
    train_data = pd.merge(all_years, train_data, on='Year', how='left').fillna(0)
    
    # We do the same for the true data, it can also be completely empty -> we fill it from the stop year to the stop year + nb_years -> it should always have this shape
    all_years = pd.DataFrame({'Year': range(stop_year, stop_year + nb_years + 1)})
    true_data = pd.merge(all_years, true_data, on='Year', how='left').fillna(0)

    # Split into x and y as an array
    x_train = train_data['Year'].values
    y_train = train_data['Count'].values

    x_true = true_data['Year'].values
    y_true = true_data['Count'].values

    try:
        # Fit the model
        model = pm.auto_arima(y_train, seasonal=True, m=1)
        forecast, conf_int = model.predict(n_periods=nb_years, return_conf_int=True)
    except:
        print(f"An error occurred while predicting the evolution of the name count for {name} using SARIMA.")
        return None

    # Plot if necessary
    if plot:
        x_train = pd.Series(x_train, dtype=int)
        y_train = pd.Series(y_train)

        # for the beauty of the plot, we add the last year of the train data to the forecast so that the line is connected
        x_forecast = pd.Series(range(stop_year, stop_year + 1 + nb_years), dtype=int)
        y_forecast = pd.Series(forecast)
        y_forecast = pd.concat([y_train[-1:], y_forecast])

        # Confidence intervals
        lower_bound = pd.Series(conf_int[:, 0])  # Lower bound of CI
        upper_bound = pd.Series(conf_int[:, 1])  # Upper bound of CI
        # To make the graph look better and since the prediction starts at y+1, we add the last value of y_train
        lower_bound = pd.concat([y_train[-1:], lower_bound])
        upper_bound = pd.concat([y_train[-1:], upper_bound])

        # Plot the test data in blue and label it
        # keep only 30 years before the stop year
        x_train = x_train[-30:]
        y_train = y_train[-30:]
        plt.plot(x_train, y_train, color='blue', label='Train data')
        # Plot the forecast data in orange
        plt.plot(x_forecast, y_forecast, color='orange', label='Forecast data')
        # Plot the real data in green
        plt.plot(x_true, y_true, color='green', label='True data')

        # Plot confidence intervals as a shaded region
        x_conf = pd.Series(range(stop_year, stop_year + nb_years + 1), dtype=int)  # Forecast years
        plt.fill_between(x_conf, lower_bound, upper_bound, color='gray', alpha=0.2, label='Confidence Interval')

        # Horizontal line for the stop year
        plt.axvline(x=stop_year, color='red', linestyle='--', label='Stop year')

        # Plot styling
        plt.xlabel('Year')
        plt.ylabel('Count')
        plt.title('Prediction of the evolution of the name count for ' + name + " using SARIMA")
        plt.legend()
        plt.show()

    # Create the dataframe containg the prediction and the real data
    # drop the first element of the true data as it is the last element of the train data
    y_true = y_true[1:]

    prediction = pd.DataFrame({
    'Year': range(stop_year + 1, stop_year + 1 + nb_years),
    'Predicted Count': forecast,
    'Lower CI': conf_int[:, 0],
    'Upper CI': conf_int[:, 1],
    'True Count': y_true
    })
    return prediction

def difference_in_means(names_data: NamesData, name: str, stop_year: int, nb_year: int, progress : np.array):
    """
    Compute the difference in means between the period before and after the stop year.
    :param names_data: the name dataset
    :param name: the name from which we compute the difference in means
    :param stop_year: the year of the event
    :param nb_year: the number of years to consider before and after the event
    :param progress: an array to store the progress of the computation
    :return: the difference in means or np.inf if the name was invented by a movie
    """
    # Filter for the specified name and aggregate counts if needed
    name_data = names_data()[names_data()['Name'] == name]
    name_data = name_data.groupby(['Year']).sum().reset_index()

    progress[0] += 1
    # print the progress
    if progress[0] == progress[1]//4:
        print("25%")
    elif progress[0] == progress[1]//2:
        print("50%")
    elif progress[0] == 3*progress[1]//4:
        print("75%")
    elif progress[0] == progress[1]:
        print("100%")

    # Split the dataset at the stop_year
    pre_period = name_data[(name_data['Year'] >= stop_year - nb_year) & (name_data['Year'] < stop_year)]
    post_period = name_data[(name_data['Year'] >= stop_year) & (name_data['Year'] <= stop_year + nb_year)]

    # Compute the difference in means
    pre_mean = pre_period['Count'].mean()
    post_mean = post_period['Count'].mean()

    # If the pre_mean is 0, we check if the name was invented by a movie
    if pre_mean == 0 or np.isnan(pre_mean):
        two_years_after = name_data[(name_data['Year'] <= stop_year + 2) & (name_data['Year'] >= stop_year)]
        created = two_years_after['Count'].mean()

        if created >= 0:
            return np.inf
        elif np.isnan(created):
            return -np.inf
    if post_mean == 0 or np.isnan(post_mean):
        return -np.inf
        
    diff = post_mean - pre_mean
    return diff

def predict_naming_prophet(data: NamesData, name: str, stop_year: int, nb_years: int, plot=False) -> pd.DataFrame:
    """
    Predict the evolution of a name's count by year using Facebook's Prophet model.
    :param data: the name dataset
    :param name: the name from which we predict the evolution
    :param stop_year: the year of the event, we will predict the evolution from stop_year + 1
    :param nb_years: the number of years we want to predict
    :param plot: if True, displays diagnostic plots
    :return: a dataframe with the predictions (starting from stop_year + 1)
    """

    # Supress the warnings
    import logging
    logging.getLogger('cmdstanpy').setLevel(logging.ERROR)

    input_data = data().copy()

    # Filter for the specified name and aggregate counts if needed
    name_data = input_data[input_data['Name'] == name]
    name_data = name_data.groupby(['Year']).sum().reset_index()
    name_data = name_data.drop(columns=['Name', 'Sex']) # no need for them

    
    # Fill missing values in the interval with 0
    full_years = range(name_data['Year'].min(), stop_year + nb_years + 1)
    name_data = name_data.set_index('Year').reindex(full_years)
    name_data = name_data.reset_index().rename(columns={'index': 'Year'})
    name_data["Count"] = name_data["Count"].fillna(0)
    # Set the type back to int
    name_data['Count'] = name_data['Count'].astype(int)

    # Split the dataset at the stop_year
    train_data = name_data[name_data['Year'] <= stop_year].rename(columns={'Year': 'ds', 'Count': 'y'})
    true_data = name_data[name_data['Year'] >= stop_year]  # the = is for visualisation -> connected points on the graph
    true_data = true_data[true_data['Year'] <= stop_year + nb_years]

    y_true = true_data['Count'].values

    # Convert the Year column to datetime
    train_data['ds'] = pd.to_datetime(train_data['ds'], format='%Y')

    # Fit the model
    model = Prophet(interval_width=0.95, changepoint_prior_scale=0.001) # 95% confidence interval
    model.fit(train_data)

    prediction = model.make_future_dataframe(periods=nb_years+1, freq='YE')
    forecast = model.predict(prediction)

    # get the incertitude interval and the prediction
    forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    forecast = forecast.rename(columns={'ds': 'Year', 'yhat': 'Predicted Count'})

    # Plot if necessary
    if (plot):
        # plot the previous data, keep only the past 30 years
        train_data = train_data[train_data['ds'] >= pd.to_datetime(stop_year - 30, format='%Y')]
        plt.plot(train_data['ds'], train_data['y'], color='blue', label='Previous data')

        # plot the forecast data with the incertitude interval, keep only the last 30 years
        forecast = forecast[forecast['Year'] >= pd.to_datetime(stop_year - 30, format='%Y')]
        plt.plot(forecast['Year'], forecast['Predicted Count'], color='orange', label='Forecast data')
        plt.fill_between(forecast['Year'], forecast['yhat_lower'], forecast['yhat_upper'], color='orange', alpha=0.2)

        # plot the true data
        true_data['Year'] = pd.to_datetime(true_data['Year'], format='%Y')
        plt.plot(true_data['Year'], true_data['Count'], color='green', label='True data')

        # plot the stop year
        plt.axvline(x=pd.to_datetime(stop_year, format='%Y'), color='red', linestyle='--', label='Stop year')

        # Plot styling
        plt.xlabel('Year')
        plt.ylabel('Count')
        plt.title('Prediction of the evolution of the name count for ' + name + " using Prophet")
        plt.legend()
        plt.show()

    # Keep only the last nb_years
    forecast['Year'] = forecast['Year'].dt.year
    forecast = forecast[forecast['Year'] >= (stop_year + 1)]

    y_true = y_true[1:]

    forecast['True Count'] = y_true

    return forecast


def compute_distance_abs(df_pred):
    """
    Computes the absolute difference between predicted and true counts.

    :param df_pred: DataFrame containing the columns 'Year', 'Predicted Count', and 'True Count'
    :return: DataFrame with an additional 'Distance' column representing the absolute difference
    """
    distance_pred = df_pred[['Year', 'Predicted Count', 'True Count']].copy()

    distance_pred['Distance'] = abs(distance_pred['Predicted Count'] - distance_pred['True Count'])
    return distance_pred



def compute_distance(df_pred):
    """
    Computes the distance between the true count and the predicted count for each year.
    If the predicted count is higher than the true count, -inf is returned. Otherwise, the absolute difference is returned.

    :param df_pred: DataFrame containing the columns 'Year', 'Predicted Count', and 'True Count'
    :return: DataFrame with an additional 'Distance' column representing the computed distance
    """
    distance_pred = df_pred[['Year', 'Predicted Count', 'True Count']].copy()

    distance_pred['Distance'] = np.where(distance_pred['Predicted Count'] > distance_pred['True Count'], -np.inf,
                                         abs(distance_pred['Predicted Count'] - distance_pred['True Count']))
    return distance_pred


def compute_area(distance_df):
    """
    Computes the area under the curve for the distance using the trapezoidal rule.

    :param distance_df: DataFrame containing the columns 'Year' and 'Distance'
    :return: float representing the computed area under the curve
    """
    # Use the trapezoidal rule to compute the area under the curve
    area = np.trapz(distance_df['Distance'], x=distance_df['Year'])
    return area


def plot_distance(distance_df, label1='Distance 1', distance_df2=None, label2='Distance 2'):
    """
    Plots the distance between true counts and model predictions for one or two DataFrames.

    :param distance_df: DataFrame containing the columns 'Year' and 'Distance'
    :param label1: Label for the first distance plot
    :param distance_df2: (optional) A second DataFrame containing the columns 'Year' and 'Distance'
    :param label2: Label for the second distance plot
    :return: None, displays a line plot of the distances
    """
    plt.figure(figsize=(16, 8))
    sns.lineplot(x='Year', y='Distance', data=distance_df, label=label1)
    if distance_df2 is not None:
        sns.lineplot(x='Year', y='Distance', data=distance_df2, label=label2)
    plt.title('Difference between true count and model predictions')
    plt.xlabel('Year')
    plt.ylabel('Count Difference')
    plt.legend()
    plt.show()
