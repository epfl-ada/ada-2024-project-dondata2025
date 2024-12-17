# Contains the complete process of the pipeline

# Imports
import os, sys
import pandas as pd
import numpy as np
import src.data.movies_char_data as movies_char_data
import src.utils.movies_utils as movies_utils
import src.utils.imdb_manipulation as imdb_manipulation
import src.utils.names_utils as names_utils
import src.data.names_data as names_data
import src.models.naming_prediction as naming_prediction
import tests.interval_test as interval_test


# Constants
## Data for movies (CMU and IMDB manipulation)

CLEANED_CMU_DATA_PATH = "data/clean/movies_char/"

CMU_CHARACTER_IN_PATH = "character.metadata.tsv"
CMU_CHARACTER_OUT_PATH = "CMU_characters.csv"
CMU_MOVIE_IN_PATH = "movie.metadata.tsv"
CMU_MOVIE_OUT_PATH = "CMU_movies.csv"
CMU_MOVIES_CHARS_OUT_PATH = CLEANED_CMU_DATA_PATH + "CMU_movies_chars.csv"

IMDB_DIR_PATH = "data/raw/imdb/"
CMU_IMDB_MERGED_OUT_PATH = "data/clean/CMU_IMDB_merged.csv"
BLOCKBUSTERS_OUT_PATH = "data/clean/blockbusters.csv"

TOP_PER_YEAR_DF_PATH = "data/clean/top_per_year.csv"

PLOT_SUMMARIES_PATH = "data/raw/plot_summaries.txt"
MAIN_CHARACTERS_PATH = "data/clean/main_chars_in_top_movies.csv" 

## Results
RESULTS_PATH_SARIMA = "data/clean/influenced_names_sarima.csv"
RESULTS_PATH_PROPHET = "data/clean/influenced_names_prophet.csv"
RESULTS_PATH_MEANS = "data/clean/influenced_names_means_diff.csv"

## Arguments
FIRST_YEAR = 1960
N_BIGGEST_RATING = 15


def print_step(message):
    """
    Function to print a step of the pipeline
    :param message: str the message to print
    """
    print("\n-------------------")
    print(f"{message}...")
    print("-------------------")


def write_all_names_data():
    """
    Function to get and write the names data of all countries
    :return: NamesData : The global names data, and the names data for each country
    """

    # Loading and cleaning the data from the different countries
    uk = names_data.UKNamesData("UK", "ukbabynames.csv")
    uk.clean_raw_data()
    uk.clean_df = uk.clean_df[uk.clean_df["Year"] >= FIRST_YEAR] # Exckude the input with years before FIRST_YEAR
    uk.write_clean_data()
    france = names_data.FranceNamesData("France", "france.csv", "https://www.insee.fr/fr/statistiques/8205621?sommaire=8205628#dictionnaire", ";")
    france.clean_raw_data()
    france.clean_df = france.clean_df[france.clean_df["Year"] >= FIRST_YEAR] # Exckude the input with years before FIRST_YEAR
    france.write_clean_data()
    us = names_data.USNamesData("US", "babyNamesUSYOB-full.csv")
    us.clean_raw_data()
    us.clean_df = us.clean_df[us.clean_df["Year"] >= FIRST_YEAR] # Exckude the input with years before FIRST_YEAR
    us.write_clean_data()
    norway = names_data.NovergianNamesData("Norway", "norway/norway_merged.csv")
    norway.clean_raw_data()
    norway.clean_df = norway.clean_df[norway.clean_df["Year"] >= FIRST_YEAR] # Exckude the input with years before FIRST_YEAR
    norway.write_clean_data()

    # Merge the data together
    global_names = names_utils.merge_names_data([uk, france, us, norway])
    global_names.sex_handling() # Handle the case where a name is in both sex -> only take the most common one
    global_names.write_clean_data()

    return global_names, uk, france, us, norway


def read_all_names_data():
    """
    Function to read the names data of all countries from a saved file

    :return: NamesData : The global names data, and the names data for each country
    """

    uk = names_data.NamesData("UK", "ukbabynames.csv", loaded=False)
    uk.load_clean_data()
    france = names_data.NamesData("France", "france.csv", "https://www.insee.fr/fr/statistiques/8205621?sommaire=8205628#dictionnaire", ";", loaded=False)
    france.load_clean_data()
    us = names_data.NamesData("US", "babyNamesUSYOB-full.csv", loaded=False)
    us.load_clean_data()
    norway = names_data.NamesData("Norway", "norway_merged.csv", loaded=False)
    norway.load_clean_data()
    global_names = names_data.NamesData("UK & France & US & Norway", "UK_France_US_Norway.csv", loaded=False)
    global_names.load_clean_data()

    return global_names, uk, france, us, norway

def write_CMU_and_IMDB(debug=False):
    """
    Functions that does all the Movie and Character data pipeline, all intermediate data is saved in the data/clean folder
    (Writes to memory the intermediate and final dataframe). If debug is True, the data is limited to 100 rows

    """

    #1. get data from movies and characters (CMU)
    print_step("Getting data from CMU and cleaning it")
    chars = movies_char_data.CharacterData("CMU Characters", CMU_CHARACTER_IN_PATH, output_name=CMU_CHARACTER_OUT_PATH)
    chars.pipeline()
    movies = movies_char_data.MovieData("CMU Movies", CMU_MOVIE_IN_PATH, output_name=CMU_MOVIE_OUT_PATH)
    movies.pipeline()

    if debug:
        print("Debug mode: limiting CMU data to 100 rows")
        chars.clean_df = chars.clean_df.sample(n=100)
        movies.clean_df = movies.clean_df.sample(n=100)

    #2. Join them together
    print_step("Joining then writing the movies and characters data")
    movies_chars_joined = movies_utils.merge_movies_characters_data(movies, chars)
    # Save the data
    movies_chars_joined.to_csv(CMU_MOVIES_CHARS_OUT_PATH, index=False)

    #3. Augment the data with IMDB data
    #3.1 Get most famous movies from IMDB
    print_step("Getting and filtering data from IMDB...")
    blockbusters = imdb_manipulation.get_all_blockbusters(IMDB_DIR_PATH)
    # Save the data
    blockbusters.to_csv(BLOCKBUSTERS_OUT_PATH, index=False)
    if debug:
        print("Debug mode: limiting IMDB data to 100 rows")
        blockbusters = blockbusters.sample(n=100)
    #3.2 Merge the data with CMU
    print_step("Merging CMU and IMDB data...")
    merged_cmu_imdb = imdb_manipulation.merge_imdb_and_dataset(blockbusters, movies())
    #merged_cmu_imdb = merged_cmu_imdb[merged_cmu_imdb['is_blockbuster'] == True]
    # Save the data
    merged_cmu_imdb.to_csv(CMU_IMDB_MERGED_OUT_PATH, index=False)

    #4. Get the biggest rating per year
    print_step("Getting the biggest rating per year...")
    # remove every movie without a name, weightedAverageRating or ReleaseDate
    merged_cmu_imdb = merged_cmu_imdb.dropna(subset=['Movie_name', 'weightedAverageRating', 'Release_date'])
    # Get the biggest rating per year
    top_per_year_df = imdb_manipulation.biggest_rating_per_year(merged_cmu_imdb, N_BIGGEST_RATING, FIRST_YEAR, by_num_votes=True)
    # Save the data
    top_per_year_df.to_csv(TOP_PER_YEAR_DF_PATH, index=False)    

    # 5. Compute the main characters in the top movies
    print_step("Computing the main characters' name in the top movies...")
    main_chars = names_utils.main_name_per_movie(PLOT_SUMMARIES_PATH, top_per_year_df)
    main_chars.to_csv(MAIN_CHARACTERS_PATH, index=False)


    return main_chars, top_per_year_df, merged_cmu_imdb, movies_chars_joined, blockbusters, chars, movies
    
def read_CMU_IMDB():
    """
    Function to read the all the data stored in the write_CMU_and_IMDB function
    :return: List<DataFrame> : The DataFrame for the Top N movies per year, imdb and cmu merge, the movies and characters data, the blockbusters data, the characters data and the movies data 
    """

    top_n_per_year = pd.read_csv(TOP_PER_YEAR_DF_PATH)
    merged_cmu_imdb = pd.read_csv(CMU_IMDB_MERGED_OUT_PATH)
    movies_chars_joined = pd.read_csv(CMU_MOVIES_CHARS_OUT_PATH)
    blockbusters = pd.read_csv(BLOCKBUSTERS_OUT_PATH)
    chars = pd.read_csv(CLEANED_CMU_DATA_PATH + CMU_CHARACTER_OUT_PATH)
    movies = pd.read_csv(CLEANED_CMU_DATA_PATH + CMU_MOVIE_OUT_PATH)
    main_chars = pd.read_csv(MAIN_CHARACTERS_PATH)

    return main_chars, top_n_per_year, merged_cmu_imdb, movies_chars_joined, blockbusters, chars, movies


def is_name_influenced_sarima(name, names_data, year, progress, plot=False):
    """
    Function to check if a name is influenced by a movie
    :param name: str : The name we want to check
    :param names_data: NamesData : The names data of the country we want / or global
    :param year: int : The year of the movie
    :return: bool : True if the name is influenced, False otherwise
    """

    # Progress
    progress[0] += 1
    if(progress[0] % 100 == 0):
        print(f"Progress: {progress[0]}/{progress[1]}")


    # Some of the retreived characters names are not 
    pred = naming_prediction.predict_naming_ARIMA(names_data, name, year, 5, plot=plot)

    if(pred is not None):
        # We use our decision method to see if the name is influenced
        predicted_curve = pred["Predicted Count"]
        lower = pred["Lower CI"]
        upper = pred["Upper CI"]
        real_curve = pred["True Count"]

        # We check if the real curve is in the interval of the predicted curve
        test = interval_test.outside_interval(predicted_curve, upper, lower, real_curve, 0.82)
        if(test):
            print(f"{name} is influenced by a movie in {year}")
            return True
        else:
            return False
    else:
        return False

def compute_all_influence_sarima(namesData, mean_df):
    """
    Function to compute the influenced names by the movies using the sarima method

    :param main_characters: DataFrame : The names of the main character in the top movies
    :param namesData: NamesData : The names data of the country we want / or global
    :param mean_df: DataFrame : The DataFrame containing the mean difference of the names -> will allow to speed up the process
    """

    print_step("Using the mean difference results to speed up the SARIMA method...")
    # We keep only the names were the column Influence is not < 0 and not = inf (excluded cases and already marked as created)
    sarima_df = mean_df[mean_df["Influence"] > 0].copy()
    sarima_df = sarima_df[sarima_df["Influence"] != np.inf]
    # rename the column Influence to Mean Difference
    sarima_df = sarima_df.rename(columns={"Influence": "Mean Difference"})

    print(f"Using {len(sarima_df)} names to speed up the SARIMA method. (from {len(mean_df)} names)")

    progress = np.zeros((2,)) # we use this to print the progress of the computation, first value is the number of names computed, second is the total number of names to compute
    progress[1] = len(sarima_df)

    # We add a column "Influenced" to the DataFrame, and we fill it with the result of the function is_name_influenced (for each row)
    sarima_df["Influenced"] = sarima_df.apply(lambda x: 
                                                    is_name_influenced_sarima( x["Normalized_name"], namesData, x["Year"], progress), axis=1)

    # Write the data
    sarima_df.to_csv(RESULTS_PATH_SARIMA, index=False)

    print(f"Influenced names computed and saved in {RESULTS_PATH_SARIMA}")

    return sarima_df

def is_name_influenced_prophet(name, names_data, year, plot=False):
    """
    Function to check if a name is influenced by a movie using the prophet method
    :param name: str : The name we want to check
    :param names_data: NamesData : The names data of the country we want / or global
    :param year: int : The year of the movie
    :return: bool : True if the name is influenced, False otherwise
    """
    try:
        # Some of the retreived characters names are not 
        pred = naming_prediction.predict_naming_prophet(names_data, name, year, 10, plot=plot)

        # We use our decision method to see if the name is influenced
        predicted_curve = pred["Predicted Count"]
        lower = pred["yhat_lower"]
        upper = pred["yhat_upper"]
        real_curve = pred["True Count"]

        # We check if the real curve is in the interval of the predicted curve
        test = interval_test.outside_interval(predicted_curve, upper, lower, real_curve, 0.9)

        if(test):
            print(f"{name} is influenced by a movie in {year}")
            return 1
        else:
            return 0
    except ValueError as e:
        print(f"Error with {name} in {year} : {e}")
        return 0


def compute_all_influence_prophet(mean_df, namesData):
    """
    Function to compute the influenced names by the movies using the prophet method

    :param main_characters: DataFrame : The names of the main character in the top movies
    :param namesData: NamesData : The names data of the country we want / or global
    :param mean_df: DataFrame : The DataFrame containing the mean difference of the names -> will allow to speed up the process
    """

    print_step("Using the mean difference results to speed up the Prophet method...")
    # We keep only the names were the column Influence is not < 0 and not = inf (excluded cases and already marked as created)
    prophet_df = mean_df[mean_df["Influence"] > 0].copy()
    prophet_df = prophet_df[prophet_df["Influence"] != np.inf]
    # rename the column Influence to Mean Difference
    prophet_df = prophet_df.rename(columns={"Influence": "Mean Difference"})

    print(f"Using {len(prophet_df)} names to speed up the SARIMA method. (from {len(mean_df)} names)")

    # Now we want to apply the prophet method to the names, it is a fast process, no need to log the progress
    prophet_df["Influenced"] = prophet_df.apply(lambda x: is_name_influenced_prophet( x["Normalized_name"], namesData, x["Year"]), axis=1)

    # Write the data
    prophet_df.to_csv(RESULTS_PATH_PROPHET, index=False)

    print(f"Influenced names computed and saved in {RESULTS_PATH_PROPHET}")

    return prophet_df

def load_influenced_sarima():
    """
    Function to load the influenced names generate by Sarima
    :return: DataFrame : The DataFrame containing the influenced names
    """
    return pd.read_csv(RESULTS_PATH_SARIMA)


def compute_all_influence_mean(main_characters, namesData):
    """
    Function to compute the influenced names by the movies using the mean comparison method

    :param main_characters: DataFrame : The names of the main character in the top movies
    :param namesData: NamesData : The names data of the country we want / or global
    """

    print_step("Computing the influenced names using the mean difference...")

    namesData.check_clean_data()

    # This method is way faster than the SARIMA method, so instead of keeping only the first part of the characters name, we iterate over the names using the split method
    ## We split the names in main_characters so that each row has only a one word name (Princess Leia -> Princess, Leia)
    splitted_main_characters = main_characters.copy()
    splitted_main_characters["Full name"] = splitted_main_characters["Character Name"] # To keep the full name somewhere

    splitted_main_characters = splitted_main_characters.assign(
            **{"Character Name": splitted_main_characters["Character Name"].str.split(" ")}
        ).explode("Character Name").reset_index(drop=True)

    print(f"Splitting the names in {len(main_characters)} main characters to {len(splitted_main_characters)} names")

    intersection = names_utils.chars_and_names_intersection(splitted_main_characters, namesData)

    progress = np.zeros((2,)) # we use this to print the progress of the computation, first value is the number of names computed, second is the total number of names to compute
    progress[1] = len(intersection)
    
    # We add a column "Influence" to the DataFrame, and we fill it with the result of the function is_name_influenced (for each row) /!\ This is not a boolean but a difference of mean
    intersection["Influence"] = intersection.apply(lambda x: 
                                                    naming_prediction.difference_in_means( namesData, x["Normalized_name"], x["Year"], 5, progress), axis=1)

    intersection  = intersection.sort_values(by="Influence", ascending=False)

    # Write the data
    intersection.to_csv(RESULTS_PATH_MEANS, index=False)

    print(f"Influenced names computed and saved in {RESULTS_PATH_MEANS}")

    return intersection

def load_influenced_means():
    """
    Function to load the influenced names generate by the mean comparison method
    :return: DataFrame : The DataFrame containing the influenced names
    """
    return pd.read_csv(RESULTS_PATH_MEANS)
    
