
# What a beautiful name! Where does it come from?

## Abstract

Movies, and more generally TV contents, are known to be powerful influencers. Jennifer Aniston's haircut, introduced in the TV show *Friends*, is considered to have become one of the most requested ever in history. 

Our project will then explore wether movies have influenced even the deepest part of who we are: our names.

To investigate this topic, we use a dataset with metadata from 81,741 movies, combined with one containing the names of more than 450,000 characters. Both were provided in our course. To connect those data with real life, we gathered name attribution datasets from various countries.
By integrating this information, we aim to identify correlations and patterns. We’ll explore how the most influential movies each year may have shaped naming trends and whether factors like genre or cultural context drive these changes.

## Research questions

- Can we find some names that have been impacted by the release of a blockbuster movie ?
- Does the sex of the newborn have any impact on that?
- Do those trends appear in specific countries ? Can this relate to the movie's country of origin or the actors' ethnicity ?
- Can we observe the same influence with actor names ?
- How does this influence last over time, i.e. is it a short or long-term effect over baby name trends ?

## Additional datasets

For our project, we integrated several name attribution datasets from various countries, including:

- Canada
- United States of America
- France
- New Zealand
- United Kingdom
- Norway
- Ireland
- Spain
- Argentina

You may wonder why our additional datasets predominantly come from developed countries. We initially considered a more diverse selection, aiming to include datasets from countries like China, Japan, Russia, and India. However, we faced an initial challenge: **the alphabet**. Many countries use scripts other than the Latin alphabet, which complicates the task of managing and processing names consistently. Translating traditional names or finding equivalent representations in the Latin script proved to be a daunting, error-prone task.
Therefore, we opted to limit our analysis to datasets that use the Latin alphabet. Even so, there remains a wide array of countries to choose from. 

Our second challenge was **data availability from national statistics offices**. While these agencies do their best, offices in developing countries often prioritize data on critical metrics such as birth mortality rates or education levels—an understandable priority that, unfortunately, restricts the availability of name attribution data.

We ultimately assembled nearly ten diverse datasets. Since the formats varied widely, we developed a script (names_data.py) to clean and standardize the datasets into a unified structure with these fields:

1. Year
2. Name (in uppercase)
3. Sex [F/M]
4. Count

This standardization process ensures consistent and efficient analysis across all datasets.

## Methods
The first method we use is designed to analyze the impact of popular movie character names on baby name trends, revealing shifts in naming patterns after blockbuster movies releases.

- Data Filtering: First we filter the dataset of movies to keep only those with high cultural impact, defined as the top 10 characters from biggest revenue-generating movies per year. Each year’s top movies are identified by grouping the dataset by Release_year and selecting the 10 characters coming from those movies with the highest revenue within each group.

- Character Selection: Once top movies are identified, the character dataset is filtered to include only characters appearing in these selected movies. This filtering creates a refined subset of character names with high public exposure, ready for trend analysis.

- Trend Computation: For each character name in the filtered dataset, we compute the change in baby name popularity around the movie’s release. We do this by calculating the average annual count of babies given the name in the five years before and five years after the release. The difference between these two averages is our trend evalutation.

However, we must take into account that the character name could be influenced by baby name trends and not the other way around. For example, the trend evaluation assessed that the 1953 movie "Peter Pan" was influential and increased the number of babies named "Michael". If we look at the graph, we can see that "Peter-Pan" came out during a "Michael" trend and was thus most likely not so influential on said trend.

![Michael graph](img/michael_graph.png)


## Proposed timeline 
Week 18-24nov 
- Models' improvement and refinement
- Add more visualization
- Look for additional baby names datasets to clean and add to the dataframe
- Do not go too deep into newer features to wait for Milestone feedback
Week 25nov-1dec
- Adjust from Milestone feedback, decide all choices for implementation
- Lighter Week for project to do and submit Homework 2

Week 2-8dec
- Start website UI/layout
- Implement P-value for better trust in results
- Start additional analysis bound to characteristics (popularity in certain countries/continents, ethnicity of influential characters, etc...)
- Start linking the data story from A to Z

Week 9-14dec 
- Finalize website visuals and data story showcase 
- Clean and comment the code
- Test the data story for edge cases/weird inputs
- Make sure the website makes it understandable and concise

Week 15-20dec
- Polish everything for the submission
- Finish any above task that is not done

## Task attribution
Jérémy and Emile : coding up the features 

Julien and Pauline : Designing the process and the algorithms

Corentin : handling the website/data story visualizations

Obviously bound to change according to necessities

## Questions for TAs
- Is it a reasonable assumption that blockbusters will have no missing datas (NaN values) and thus we don't have to worry about discarding data entries with missing values in important fields such as Revenue ?
- How can we elaborately determine how a movie is a blockbuster ? For now we only sort by Revenue but should we use a more refined metric ? Same question for iconic actors