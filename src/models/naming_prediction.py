import pmdarima as pm
import pandas as pd
from src.data.names_data import NamesData
import matplotlib.pyplot as plt
from prophet import Prophet


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
    data.check_clean_data()
    input_data = data().copy()

    # Filter for the specified name and aggregate counts if needed
    name_data = input_data[input_data['Name'] == name]
    name_data = name_data.groupby(['Year']).sum().reset_index()
    name_data = name_data.drop(columns=['Name'])

    # Split the dataset at the stop_year
    train_data = name_data[name_data['Year'] <= stop_year]
    true_data = name_data[name_data['Year'] >= stop_year]
    true_data = true_data[true_data['Year'] <= stop_year + nb_years]

    # Split into x and y as an array
    x_train = train_data['Year'].values
    y_train = train_data['Count'].values

    x_true = true_data['Year'].values
    y_true = true_data['Count'].values

    # Fit the model
    model = pm.auto_arima(y_train, seasonal=True, m=1)
    forecast = model.predict(n_periods=nb_years)

    # Plot if necessary
    if plot:
        y_train = pd.Series(y_train)
        y_forecast = pd.Series(forecast)
        x_train = pd.Series(x_train)
        # for the beauty of the plot, we add the last year of the train data to the forecast so that the line is connected
        x_forecast = pd.Series(range(stop_year, stop_year + 1 + nb_years))
        y_forecast = pd.concat([y_train[-1:], y_forecast])
        # Plot the test data in blue and label it
        # keep only 10 years before the stop year
        x_train = x_train[-10:]
        y_train = y_train[-10:]
        plt.plot(x_train, y_train, color='blue', label='Train data')
        # Plot the forecast data in orange
        plt.plot(x_forecast, y_forecast, color='orange', label='Forecast data')
        # Plot the real data in green
        plt.plot(x_true, y_true, color='green', label='True data')
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
    prediction = pd.DataFrame({'Year': range(stop_year + 1, stop_year + 1 + nb_years), 'Predicted Count': forecast, 'True Count': y_true})
    return prediction


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
    data.check_clean_data()
    input_data = data().copy()

    # Filter for the specified name and aggregate counts if needed
    name_data = input_data[input_data['Name'] == name]
    name_data = name_data.groupby(['Year']).sum().reset_index()
    name_data = name_data.drop(columns=['Name', 'Sex'])

    # Split the dataset at the stop_year
    train_data = name_data[name_data['Year'] <= stop_year].rename(columns={'Year': 'ds', 'Count': 'y'})
    true_data = name_data[name_data['Year'] >= stop_year] # the = is for visualisation -> connected points on the graph
    true_data = true_data[true_data['Year'] <= stop_year + nb_years]

    # Convert the Year column to datetime
    train_data['ds'] = pd.to_datetime(train_data['ds'], format='%Y')

    # Fit the model
    model = Prophet()
    model.fit(train_data)

    prediction = model.make_future_dataframe(periods=nb_years, freq='YE')
    forecast = model.predict(prediction)

    # get the incertitude interval and the prediction
    forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    forecast = forecast.rename(columns={'ds': 'Year', 'yhat': 'Predicted Count'})


    # Plot if necessary
    if(plot):
        
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
    forecast = forecast[forecast['Year'] >= pd.to_datetime(stop_year + 1, format='%Y')]
    return forecast

    




