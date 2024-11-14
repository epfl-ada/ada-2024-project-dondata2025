
# What a beautiful name! Where does it come from?

## Abstract
*This is a ~150 word description of the project idea and goals. What's our motivation? What story do we want to tell*

Movies, and more generally TV contents, are known to be powerfull influencers. Jennifer Aniston's haircut, introduced in the TV show *Friends*, is considered to have become one of the most requested ever in history. 

Our project will then explore wether movies have influenced even the deepest part of who we are: our names.

In order to investigate this topic, we use a dataset with metadata from 81,741 movies, combined with one containing the names of more than 450,000 characters. Both were provided in our course. To connect those data with real life, we gathered name attribution datasets from various countries.
By integrating this information, we aim to identify correlations and patterns. We’ll explore how the most influential movies each year may have shaped naming trends and whether factors like genre or cultural context drive these changes.

## Research questions
*A list of research questions you would like to address during the project.*

- Can we find some names that have been ....
- Does the sexe of the newborn have any impact on that?
- Is it a global phenomenom or does it happen more in certain country?

## Additional datasets
*We will discuss here the list of additional datasets we would like to use in our project* 

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

*List the additional dataset(s) you want to use (if any), and some ideas on how you expect to get, manage, process, and enrich it/them. Show us that you’ve read the docs and some examples, and that you have a clear idea on what to expect. Discuss data size and format if relevant. It is your responsibility to check that what you propose is feasible*

## Methods
A remplir

## Proposed timeline

## Organization within the team
*A list of internal milestones up until project Milestone P3.*

## Questions for TAs
*Optional*
