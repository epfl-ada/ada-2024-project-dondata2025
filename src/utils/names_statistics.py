# Description: This file contains the code to generate statistics about the names in the dataset.

import pandas as pd
import sys, os

# Change the path if the file is launched directly (not imported)
if(__name__ == '__main__'):
    sys.path.append(os.path.abspath(os.path.join('../../'))) # root directory

from src.data.names_data import NamesData


