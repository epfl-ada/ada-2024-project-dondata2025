
# DonData : Beautiful name ! Where does it come from ?

## Abstract
*This is a ~150 word description of the project idea and goals. What's our motivation ? What story do we want to tell*

Movies, and more generally TV content are known to be a powerfull source of influence. Jennifer Aniston's haircut, introduced in the TV show *Friends*, is considered to have become one of the most requested ever in history. 

Our project aims to evaluate wether movies have influenced even the deepest part of who we are: our names.

In order to investigate this topic, we use a dataset containing [INSERT CORRECT VALUE] movies combined with one containing the names of the characters. To connect those data with real life, various datasets containing names attribution over time periods from different countries were found freely on the internet.

We will focus on the most popular movies per year and analyse the changes it might have caused to the naming of newborns and try to find if we can find some patterns or differences depending on various parameters from our datasets. 

## Research questions
*A list of research questions you would like to address during the project.*

- Can we find some names that have been ....
- Does the sexe of the newborn have any impact on that ?
- Is it a global phenomenom or does it happen more in certain country ?


## Quickstart

```bash
# clone project
git clone <project link>
cd <project repo>

# [OPTIONAL] create conda environment
conda create -n <env_name> python=3.11 or ...
conda activate <env_name>


# install requirements
pip install -r pip_requirements.txt
```



### How to use the library
Tell us how the code is arranged, any explanations goes here.



## Project Structure

The directory structure of new project looks like this:

```
├── data                        <- Project data files
│
├── src                         <- Source code
│   ├── data                            <- Data directory
│   ├── models                          <- Model directory
│   ├── utils                           <- Utility directory
│   ├── scripts                         <- Shell scripts
│
├── tests                       <- Tests of any kind
│
├── results.ipynb               <- a well-structured notebook showing the results
│
├── .gitignore                  <- List of files ignored by git
├── pip_requirements.txt        <- File for installing python dependencies
└── README.md
```

